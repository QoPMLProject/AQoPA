'''
Created on 05-09-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

import sys
import time
import threading
import wx
import wx.lib.newevent
import wx.lib.delayedresult

import aqopa
import aqopa.app
from aqopa.model.parser import MetricsParserException,\
    ConfigurationParserException, ModelParserException
from aqopa.module import timeanalysis
from aqopa.simulator.error import EnvironmentDefinitionException

ModelParsedEvent, EVT_MODEL_PARSED = wx.lib.newevent.NewEvent()
ModelParseErrorEvent, EVT_MODEL_PARSE_ERROR = wx.lib.newevent.NewEvent()
ModulesChangedEvent, EVT_MODULES_CHANGED = wx.lib.newevent.NewEvent()

class ModelPartDataPanel(wx.Panel):
    """ 
    Panel containing text area for one of model parts: 
    model, metrics, configuration.
    """
    
    def __init__(self, parent):
        """ """
        wx.Panel.__init__(self, parent=parent)
    
        self.dataTextArea = wx.TextCtrl(self, style=wx.TE_MULTILINE)
    
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.dataTextArea, 1, wx.EXPAND)
        
        self.SetSizer(sizer)
        
        
class ModulesPanel(wx.Panel):
    """ 
    Panel used for selecting modules and configuring them.
    """
    
    def __init__(self, *args, **kwargs):
        self.allModules = kwargs['modules']
        del kwargs['modules']
        
        wx.Panel.__init__(self, *args, **kwargs)
        
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        modulesBox = wx.StaticBox(self, label="Modules", size=(100, 100))
        modulesBoxSizer = wx.StaticBoxSizer(modulesBox, wx.VERTICAL)
        
        self.configurationBox = wx.StaticBox(self, label="Configuration", size=(100, 100))
        configurationBoxSizer = wx.StaticBoxSizer(self.configurationBox, wx.VERTICAL)
        
        self.checkBoxesMap = {}
        self.buttonsPanelMap = {}
        self.buttonsModuleGui = {}
        self.modulesPanels = []
        
        emptyPanel = wx.Panel(self, size=(200,20))
        sizer = wx.BoxSizer(wx.VERTICAL)
        text = wx.StaticText(emptyPanel, label="Click 'Configure' button to configure selected module.") 
        sizer.Add(text, 0, wx.ALL | wx.EXPAND, 5)
        emptyPanel.SetSizer(sizer)
        configurationBoxSizer.Add(emptyPanel, 1, wx.ALL | wx.EXPAND, 5)
        self.modulesPanels.append(emptyPanel)

        for m in self.allModules:
            gui = m.get_gui()
            
            modulePanel = wx.Panel(self)
            modulePanelSizer = wx.BoxSizer(wx.HORIZONTAL)
            
            ch = wx.CheckBox(modulePanel, label=gui.get_name())
            ch.Bind(wx.EVT_CHECKBOX, self.OnCheckBoxChange)
            self.checkBoxesMap[m] = ch
            
            btn = wx.Button(modulePanel, label="Configure")
            btn.Bind(wx.EVT_BUTTON, self.OnConfigureButtonClicked)
            
            modulePanelSizer.Add(ch, 0, wx.ALL)
            modulePanelSizer.Add(btn, 0, wx.ALL)
            modulePanel.SetSizer(modulePanelSizer)
            
            modulesBoxSizer.Add(modulePanel, 0, wx.ALL | wx.EXPAND, 5)
            
            moduleConfigurationPanel = gui.get_configuration_panel(self)
            configurationBoxSizer.Add(moduleConfigurationPanel, 1, wx.ALL | wx.EXPAND, 5)
            moduleConfigurationPanel.Hide()

            self.modulesPanels.append(moduleConfigurationPanel)
            self.buttonsPanelMap[btn] = moduleConfigurationPanel
            self.buttonsModuleGui[btn] = gui
            
        mainSizer.Add(modulesBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(configurationBoxSizer, 1, wx.ALL | wx.EXPAND, 5)
        
        self.SetSizer(mainSizer)
        
    def ShowModuleConfigurationPanel(self, panel):
        """ """
        for p in self.modulesPanels:
            p.Hide()
        panel.Show()
        self.Layout()
        
    def OnCheckBoxChange(self, event):
        """ """
        modules = []
        for m in self.allModules:
            ch = self.checkBoxesMap[m]
            if ch.IsChecked():
                modules.append(m)
        
        wx.PostEvent(self, ModulesChangedEvent(modules = modules))

    def OnConfigureButtonClicked(self, event):
        """ """
        btn = event.EventObject
        moduleGui = self.buttonsModuleGui[btn]
        
        self.configurationBox.SetLabel("%s - Configuration" % moduleGui.get_name())
        self.ShowModuleConfigurationPanel(self.buttonsPanelMap[btn])
        
class RunPanel(wx.Panel):
    """ """
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
    
        ###############
        # SIMULATION
        ###############    

        self.qopml_model              = ""
        self.qopml_metrics            = ""
        self.qopml_configuration      = ""

        self.selectedModules    = []

        self.interpreter        = None
        self.finishedSimulators = []
        
        self.progressTimer      = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnProgressTimerTick, self.progressTimer)
        
        ###############
        # LAYOUT
        ###############
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        leftPanel = wx.Panel(self, style=wx.ALIGN_CENTER)
        self.parseButton = wx.Button(leftPanel, label="Parse")
        self.runButton = wx.Button(leftPanel, label="Run")
        self.runButton.Enable(False)
        panelSizer = wx.BoxSizer(wx.VERTICAL)
        panelSizer.Add(self.parseButton, 0)
        panelSizer.Add(self.runButton, 0)
        leftPanel.SetSizer(panelSizer)
        
        sizer.Add(leftPanel, 0, wx.ALL | wx.EXPAND, 5)
        
        rightPanel = wx.Panel(self)
        self.parsingPanel = self._BuildParsingPanel(rightPanel)
        self.runPanel = self._BuildRunPanel(rightPanel)
        panelSizer = wx.BoxSizer(wx.VERTICAL)
        panelSizer.Add(self.parsingPanel, 1, wx.ALL | wx.EXPAND, 5)
        panelSizer.Add(self.runPanel, 1, wx.ALL | wx.EXPAND, 5)
        self.runPanel.Hide()
        rightPanel.SetSizer(panelSizer)

        sizer.Add(rightPanel, 1, wx.ALL | wx.EXPAND, 5)
        
        self.SetSizer(sizer)
        
        ###############
        # EVENTS
        ###############
        
        self.parseButton.Bind(wx.EVT_BUTTON, self.OnParseClicked)
        self.runButton.Bind(wx.EVT_BUTTON, self.OnRunClicked)
        
        self.Bind(EVT_MODEL_PARSED, self.OnModelParsed)
        
    def _BuildParsingPanel(self, parent):
        """ """
        panel = wx.Panel(parent, style=wx.ALIGN_CENTER)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        text = wx.StaticText(panel, label="Parsing Info")
        self.parseResult = wx.TextCtrl(panel, 
                                     style=wx.TE_MULTILINE | wx.TE_READONLY)
        
        sizer.Add(text, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.parseResult, 1, wx.ALL|wx.EXPAND, 5)
    
        panel.SetSizer(sizer)
        return panel
    
    def _BuildRunPanel(self, parent):
        """ """
        panel = wx.Panel(parent, style=wx.ALIGN_CENTER)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.statusLabel = wx.StaticText(panel, label="Running")
        self.percentLabel = wx.StaticText(panel, label="0%")
        self.dotsLabel = wx.StaticText(panel, label=".")
        text = wx.StaticText(panel, label="Run Info")
        self.runResult = wx.TextCtrl(panel, 
                                     style=wx.TE_MULTILINE | wx.TE_READONLY)
        
        sizer.Add(self.statusLabel, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        sizer.Add(self.percentLabel, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        sizer.Add(self.dotsLabel, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        sizer.Add(text, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.runResult, 1, wx.ALL|wx.EXPAND, 5)
    
        panel.SetSizer(sizer)
        return panel
    
    def ShowPanel(self, panel):
        self.parsingPanel.Hide()
        self.runPanel.Hide()
        panel.Show()
        self.Layout()
        
    def SetModel(self, model, metrics, configuration):
        """ """
        self.qopml_model              = model
        self.qopml_metrics            = metrics
        self.qopml_configuration      = configuration
        
    def SetSelectedModules(self, modules):
        """ """
        self.selectedModules = modules
        
    def OnParseClicked(self, event):
        """ """
        self.interpreter = aqopa.app.GuiInterpreter(
                                     model_as_text=self.qopml_model, 
                                     metrics_as_text=self.qopml_metrics,
                                     config_as_text=self.qopml_configuration)
        
        for m in self.selectedModules:
            self.interpreter.register_qopml_module(m)
        
        try:
            resultMessage = ""
            error = False
            self.interpreter.parse()
            resultMessage = "SUCCESFULLY PARSED\n\n Now you can run simulation."
            wx.PostEvent(self, ModelParsedEvent())
        except EnvironmentDefinitionException, e:
            error = True
            resultMessage = "ENVIRONMENT ERROR\n"
            resultMessage += "%s\n" % unicode(e)
        except ModelParserException, e:
            error = True
            resultMessage = "MODEL SYNTAX ERROR\n"
            if len(e.syntax_errors):
                resultMessage += "\n".join(e.syntax_errors)
        except MetricsParserException, e:
            error = True
            resultMessage = "METRICS SYNTAX ERROR\n"
            if len(e.syntax_errors):
                resultMessage += "\n".join(e.syntax_errors)
        except ConfigurationParserException, e:
            error = True
            resultMessage = "CONFIGURATION SYNTAX ERROR\n"
            if len(e.syntax_errors):
                resultMessage += "\n".join(e.syntax_errors)
        
        if error:
            resultMessage += "\nModel may include syntax parsed by modules (eg. metrics, configuration). "+\
                             "Have you selected modules?"
            wx.PostEvent(self, ModelParseErrorEvent(error=resultMessage))
        if resultMessage != "":
            self.parseResult.SetValue(resultMessage)
            
    def OnModelParsed(self, event):
        """ """
        self.runButton.Enable(True)
            
    def OnRunClicked(self, event):
        """ """
        try:
            self.runButton.Enable(False)
            self.ShowPanel(self.runPanel)
            
            self.finishedSimulators = []
            
            self.interpreter.prepare()
            self.progressTimer.Start(1000)
            for simulator in self.interpreter.simulators:
                wx.lib.delayedresult.startWorker(self.OnSimulationFinished, 
                                                 self.interpreter.run_simulation, 
                                                 wargs=(simulator,))
            
        except EnvironmentDefinitionException, e:
            self.runButton.Enable(True)
            
            errorMessage = "Error on creating environment: %s\n" % e
            if len(e.errors) > 0:
                errorMessage += "Errors:\n"
                errorMessage += "\n".join(e.errors)
                
            self.runResult.SetValue(errorMessage)
            
            self.progressTimer.Stop()
        
        self.ShowPanel(self.runPanel)
        
    def OnSimulationFinished(self, result):
        """ """
        simulator = result.get()
        self.finishedSimulators.append(simulator)

        self.PrintProgressbar(self.GetProgress())
        
        for m in self.selectedModules:
            gui = m.get_gui()
            gui.on_finished_simulation(simulator)
                
        if len(self.finishedSimulators) == len(self.interpreter.simulators):
            self.OnAllSimulationsFinished()
                
    def OnAllSimulationsFinished(self):
        """ """
        for m in self.selectedModules:
            gui = m.get_gui()
            gui.on_finished_all_simulations(self.interpreter.simulators)
            
    ################
    # PROGRESS BAR 
    ################
        
    def OnProgressTimerTick(self, event):
        """ """
        progress = self.GetProgress()
        if progress == 1:
            self.progressTimer.Stop()
        self.PrintProgressbar(progress)
        
    def GetProgress(self):
        all = 0.0
        sum = 0.0
        for simulator in self.interpreter.simulators:
            all += 1
            sum += simulator.context.get_progress()
        progress = 0
        if all > 0:
            progress = sum / all
        return progress
        
    def PrintProgressbar(self, progress):
        """
        Prints the formatted progressbar showing the progress of simulation. 
        """
        percentage = str(int(round(progress*100))) + '%'
        self.percentLabel.SetLabel(percentage)
        self.runPanel.Layout()
        
        if progress == 1:
            self.statusLabel.SetLabel('Finished')
            self.runPanel.Layout()
            self.dotsLabel.SetLabel('')
            self.runPanel.Layout()
        else:
            dots = self.dotsLabel.GetLabel()
            if len(dots) > 0:
                dots = "."
            else:
                dots += ".."
            self.dotsLabel.SetLabel(dots)
            self.runPanel.Layout()

        
class ResultsPanel(wx.Panel):
    """ """
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        
        self.selectedModules = []
        self.moduleResultPanel = {}
        self.buttonsModule = {}
        
        self._BuildMainLayout()
        
    def _BuildMainLayout(self):
        
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.modulesBox = wx.StaticBox(self, label="Modules", size=(100, 100))
        self.modulesBox.Hide()
        self.modulesBoxSizer = wx.StaticBoxSizer(self.modulesBox, wx.VERTICAL)
        
        self.resultsBox = wx.StaticBox(self, label="Results", size=(100, 100))
        self.resultsBox.Hide()
        self.resultsBoxSizer = wx.StaticBoxSizer(self.resultsBox, wx.VERTICAL)
        
        mainSizer.Add(self.modulesBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(self.resultsBoxSizer, 1, wx.ALL | wx.EXPAND, 5)
        
        self.SetSizer(mainSizer)
        self.modulesBoxSizer.Layout()
        self.resultsBoxSizer.Layout()
        mainSizer.Layout()
        
    def _BuildModulesLayout(self):
        """ """
        
        for m in self.selectedModules:
            if m in self.moduleResultPanel:
                continue
            
            gui = m.get_gui()
            
            btn = wx.Button(self, label=gui.get_name())
            btn.Bind(wx.EVT_BUTTON, self.OnModuleButtonClicked)
            self.modulesBoxSizer.Add(btn, 0, wx.ALL | wx.EXPAND)
            self.buttonsModule[btn] = m
            
            resultPanel = gui.get_results_panel(self)
            self.resultsBoxSizer.Add(resultPanel, 1, wx.ALL | wx.EXPAND)
            self.moduleResultPanel[m] = resultPanel
            
            self.Layout()
#            resultPanel.Hide()
            
        uncheckedModules = []
        for m in self.moduleResultPanel:
            if m not in self.selectedModules:
                uncheckedModules.append(m)

        buttonsToRemove = []
        for m in uncheckedModules:
            self.moduleResultPanel[m].Destroy()
            del self.moduleResultPanel[m]
            
            for btn in self.buttonsModule:
                if self.buttonsModule[btn] == m:
                    buttonsToRemove.append(btn)
                    
        for btn in buttonsToRemove:
            btn.Destroy()
            del self.buttonsModule[btn]
            
        self.Layout()
        
    def SetSelectedModules(self, modules):
        """ """
        self.selectedModules = modules
        
        if len(self.selectedModules) > 0:
            self.modulesBox.Show()
            self.resultsBox.Show()
        else:
            self.modulesBox.Hide()
            self.resultsBox.Hide()
        
        self._BuildModulesLayout()
        
    def OnModuleButtonClicked(self, event):
        """ """
        btn = event.EventObject
        
class MainNotebook(wx.Notebook):
    """ """
    
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent)
        
        ###########
        # MODULES 
        ###########
        
        self.availableModules = [ timeanalysis.Module() ]

        ###########
        # TABS
        ###########

        self.modelTab = ModelPartDataPanel(self)
        self.modelTab.Layout()
        self.modelTab.dataTextArea.SetValue(""" functions {
  fun ms_10();
  fun ms_1000();
} 

equations {
  eq ms_10() = true;
}

channels {
  channel ch1,ch2,ch3,ch4 (0);
}

hosts {

 host Client1(rr)(*) {
   process Client1(ch1, ch2) {
     M1 = ms_10();
     out(ch1: M1);
   }
 }
 
 host Client2(rr)(*) {
   process Client2(ch1, ch2) {
     M1 = ms_10();
     M1 = ms_10();
     out(ch1: M1);
     ms_1000();
     ms_1000();
     ms_1000();
     ms_1000();
     out(ch1: M1);
   }
 }
 
 host Server(rr)(*) {
   process Server1(ch1, ch2) {
     ms_1000();
     ms_1000();
     ms_1000();
     ms_1000();
     in(ch1: M1);
   }
 
 }
 
} """)
        self.Bind(wx.EVT_TEXT, self.OnModelTextChange, self.modelTab.dataTextArea)
        self.AddPage(self.modelTab, "Model")
        
        self.metricsTab = ModelPartDataPanel(self)
        self.metricsTab.Layout()
        self.metricsTab.dataTextArea.SetValue(""" metrics {
  conf(Server) {
    a=b;
  }
  conf(Mobile) {
    a=b;
  }
  
  data(Client) {
    primhead[function][time:exact(ms)];
    primitive[ms_10][10];
    primitive[ms_1000][1000];
  }
} """)
        self.Bind(wx.EVT_TEXT, self.OnModelTextChange, self.metricsTab.dataTextArea)
        self.AddPage(self.metricsTab, "Metrics")
        
        self.configurationTab = ModelPartDataPanel(self)
        self.configurationTab.Layout()
        self.configurationTab.dataTextArea.SetValue(""" versions {
  
  version v1 {
    
    set host Client1(Client);
    set host Client2(Client);
    set host Server(Client);
    
    run host Server(*) {
      run Server1(*)
    }
    
    run host Client2(*) {
      run Client2(*)
    }
    
  }
  
  version v12 {
    
    set host Client1(Client);
    set host Client2(Client);
    set host Server(Client);
    
    run host Server(*) {
      run Server1(*)
    }
    
    run host Client2(*){5} {
      run Client2(*)
    }
    
  }
  
} """)
        self.Bind(wx.EVT_TEXT, self.OnModelTextChange, self.configurationTab.dataTextArea)
        self.configurationTab.Layout()
        self.AddPage(self.configurationTab, "Versions")
        
        self.modulesTab = ModulesPanel(self, modules=self.availableModules)
        self.modulesTab.Bind(EVT_MODULES_CHANGED, self.OnModulesChange)
        self.modulesTab.Layout()
        self.AddPage(self.modulesTab, "Modules")
        
        self.runTab = RunPanel(self)
        self.runTab.Layout()
        self.AddPage(self.runTab, "Run")
        
        self.resultsTab = ResultsPanel(self)
        self.resultsTab.Layout()
        self.AddPage(self.resultsTab, "Results")
        
        
    def LoadModelFile(self, filePath):
        self.modelTab.dataTextArea.LoadFile(filePath)
        
    def LoadMetricsFile(self, filePath):
        self.metricsTab.dataTextArea.LoadFile(filePath)
        
    def LoadConfigurationFile(self, filePath):
        self.configurationTab.dataTextArea.LoadFile(filePath)
        
    def GetModelData(self):
        return self.modelTab.dataTextArea.GetValue().strip()
        
    def GetMetricsData(self):
        return self.metricsTab.dataTextArea.GetValue().strip()
        
    def GetConfigurationData(self):
        return self.configurationTab.dataTextArea.GetValue().strip()
        
    def OnModelTextChange(self, event):
        self.runTab.SetModel(self.GetModelData(), 
                             self.GetMetricsData(),
                             self.GetConfigurationData())
        
    def OnModulesChange(self, event):
        self.runTab.SetSelectedModules(event.modules)
        self.resultsTab.SetSelectedModules(event.modules)
        
class MainFrame(wx.Frame):
    """ """
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        ###########
        # MENUBAR 
        ###########        
        
        menuBar = wx.MenuBar()

        fileMenu = wx.Menu()
        item = fileMenu.Append(wx.ID_ABOUT, text="About AQoPA")
        self.Bind(wx.EVT_MENU, self.OnAbout, item)
        fileMenu.AppendSeparator()
        item = fileMenu.Append(-1, text="Load &Model")
        self.Bind(wx.EVT_MENU, self.OnLoadModel, item)
        item = fileMenu.Append(-1, text="Load M&etrics")
        self.Bind(wx.EVT_MENU, self.OnLoadMetrics, item)
        item = fileMenu.Append(-1, text="Load &Versions")
        self.Bind(wx.EVT_MENU, self.OnLoadVersions, item)
        fileMenu.AppendSeparator()
        item = fileMenu.Append(wx.ID_EXIT, text="&Quit")
        self.Bind(wx.EVT_MENU, self.OnQuit, item)
        menuBar.Append(fileMenu, "&File")
        
        self.SetMenuBar(menuBar)
        
        ###################
        # SIZERS & EVENTS
        ###################
        
        self.mainNotebook = MainNotebook(self)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.mainNotebook, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)
        
        self.Layout()
        
    def OnQuit(self, event=None):
        """ Close app """
        self.Close()
        
    def OnAbout(self, event=None):
        """ Show about info """
        dlg = wx.MessageDialog(self, "Automated Quality of Protection Analysis tool of QoP-ML models\n\nProject Home: http://qopml.org", 
                               "About AQoPA", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        
    def _LoadFile(self, loadFileDataFunction, pageNumber):
        """ Load file to text area """
        ofdlg = wx.FileDialog(self, "Load file", "", "", "QoP-ML Files (*.qopml)|*.qopml", 
                              wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        ofdlg.ShowModal()
        loadFileDataFunction(ofdlg.GetPath())
        ofdlg.Destroy()
        self.mainNotebook.SetSelection(pageNumber)
        
    def OnLoadModel(self, event):
        """ Load model file """
        self._LoadFile(self.mainNotebook.LoadModelFile, 0)
        
    def OnLoadMetrics(self, event):
        """ Load model file """
        self._LoadFile(self.mainNotebook.LoadMetricsFile, 1)
        
    def OnLoadVersions(self, event):
        """ Load model file """
        self._LoadFile(self.mainNotebook.LoadConfigurationFile, 2)
        
        
class AqopaApp(wx.App):
    
    def OnInit(self):
        self.main_frame = MainFrame(None, title="AQoPA")
        self.main_frame.Show(True)
        self.main_frame.Maximize(True)
        self.SetTopWindow(self.main_frame)
        return True


def main():
    app = AqopaApp(False)
    app.MainLoop()


if __name__ == "__main__":
    main()