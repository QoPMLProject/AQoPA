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

ModelChangedEvent, EVT_MODEL_CHANGED = wx.lib.newevent.NewEvent()
ModelParsedEvent, EVT_MODEL_PARSED = wx.lib.newevent.NewEvent()
ModelParseErrorEvent, EVT_MODEL_PARSE_ERROR = wx.lib.newevent.NewEvent()
ModulesChangedEvent, EVT_MODULES_CHANGED = wx.lib.newevent.NewEvent()

class ParserDataPanel(wx.Panel):
    """ 
    Panel containing text area for one of model parts: model, metrics, configuration.
    """
    
    def __init__(self, parent):
        """ """
        wx.Panel.__init__(self, parent=parent)
    
        self.dataTextArea = wx.TextCtrl(self, style=wx.TE_MULTILINE)
    
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.dataTextArea, 1, wx.EXPAND)
        
        self.SetSizer(sizer)
        
class ModelNotebook(wx.Notebook):
    """ """
    
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent)

        self.modelTab = ParserDataPanel(self)
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
        self.Bind(wx.EVT_TEXT, self.OnTextChange, self.modelTab.dataTextArea)
        self.AddPage(self.modelTab, "Model")
        
        self.metricsTab = ParserDataPanel(self)
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
        self.Bind(wx.EVT_TEXT, self.OnTextChange, self.metricsTab.dataTextArea)
        self.AddPage(self.metricsTab, "Metrics")
        
        self.configurationTab = ParserDataPanel(self)
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
    
    run host Client2(*) {
      run Client2(*)
    }
    
  }
  
} """)
        self.Bind(wx.EVT_TEXT, self.OnTextChange, self.configurationTab.dataTextArea)
        self.AddPage(self.configurationTab, "Configuration")
        
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
        
    def OnTextChange(self, event):
        wx.PostEvent(self, ModelChangedEvent(modelText=self.GetModelData(),
                                            metricsText=self.GetMetricsData(),
                                            configurationText=self.GetConfigurationData()))
        
class ParsePanel(wx.Panel):
    """ """
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
    
        self.parseResult = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        
        panel = wx.Panel(self,-1)
        wx.StaticText(panel, label="Parsing details")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.parseResult, 1, wx.ALL|wx.EXPAND, 5)
        
        self.SetSizer(sizer)
        
class RunPanel(wx.Panel):
    """ """
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
    
        self.runResult = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        panel = wx.Panel(self,-1, style=wx.ALIGN_CENTER)
        self.statusLabel = wx.StaticText(panel, label="Running")
        self.sizer.Add(panel, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        
        panel = wx.Panel(self,-1)
        self.percentLabel = wx.StaticText(panel, label="0%")
        self.sizer.Add(panel, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        
        panel = wx.Panel(self,-1)
        self.dotsLabel = wx.StaticText(panel, label=".")
        self.sizer.Add(panel, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        
        panel = wx.Panel(self,-1)
        wx.StaticText(panel, label="Run info")
        self.sizer.Add(panel, 0, wx.ALL|wx.EXPAND, 5)

        self.sizer.Add(self.runResult, 1, wx.ALL|wx.EXPAND, 5)
        
        self.SetSizer(self.sizer)
        
class ModulesChoosePanel(wx.Panel):
    """ """
    
    def __init__(self, *args, **kwargs):
        self.allModules = kwargs['modules']
        del kwargs['modules']
        
        wx.Panel.__init__(self, *args, **kwargs)
        
        panel = wx.Panel(self)
        wx.StaticText(panel, label="Choose modules")
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 0, wx.ALL|wx.EXPAND, 5)
        
        self.checkBoxesMap = {}
        
        for m in self.allModules:
            gui = m.get_gui()
            ch = wx.CheckBox(self, label=gui.get_name())
            ch.Bind(wx.EVT_CHECKBOX, self.OnCheckBoxChange)
            self.checkBoxesMap[m] = ch
            sizer.Add(ch, 0, wx.ALL|wx.EXPAND, 5)
        
        self.SetSizer(sizer)
        
    def OnCheckBoxChange(self, event):
        
        modules = []
        for m in self.allModules:
            ch = self.checkBoxesMap[m]
            if ch.IsChecked():
                modules.append(m)
        
        wx.PostEvent(self, ModulesChangedEvent(modules = modules))
        
class ModulesConfigurationNotebook(wx.Notebook):
    """ """
    
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent)
        
        
class ModulesConfigurationPanel(wx.Panel):
    """ """
    
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.configurationNotebook = ModulesConfigurationNotebook(self)        
        self.modules = []
        self.modulesWithExistingGui = []
        
        panel = wx.Panel(self)
        wx.StaticText(panel, label="Modules configuration")
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(panel, 0, wx.ALL|wx.EXPAND, 5)
        self.sizer.Add(self.configurationNotebook, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(self.sizer)

    def _BuildLayout(self):
        
        for m in self.modules:
            if m in self.modulesWithExistingGui:
                continue
            gui = m.get_gui()
            self.configurationNotebook.AddPage(gui.get_configuration_panel(self.configurationNotebook), 
                                               gui.get_name())
            self.modulesWithExistingGui.append(m)
            
        self.sizer.Layout()
            
        
    def SetModules(self, modules):
        """ """
        self.modules = modules
        self._BuildLayout()
        
        
class ModelPanel(wx.Panel):
    """ """
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        
        self.modelNotebook = ModelNotebook(self)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.modelNotebook, 3, wx.ALL|wx.EXPAND, 5)

        self.SetSizer(sizer)
        
class MainFrame(wx.Frame):
    """ """
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        ###############
        # SIMULATION
        ###############    

        self.interpreter        = None
        self.finishedSimulators = []
        
        self.progressTimer      = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnProgressTimerTick, self.progressTimer)

        ###########
        # MENUBAR 
        ###########        
        
        menuBar = wx.MenuBar()

        fileMenu = wx.Menu()
        item = fileMenu.Append(wx.ID_ABOUT, text="About AQoPA")
        self.Bind(wx.EVT_MENU, self.OnAbout, item)
        fileMenu.AppendSeparator()
        item = fileMenu.Append(-1, text="&Show Model")
        self.Bind(wx.EVT_MENU, self.OnShowModel, item)
        fileMenu.AppendSeparator()
        item = fileMenu.Append(-1, text="Load &Model")
        self.Bind(wx.EVT_MENU, self.OnLoadModel, item)
        item = fileMenu.Append(-1, text="Load M&etrics")
        self.Bind(wx.EVT_MENU, self.OnLoadMetrics, item)
        item = fileMenu.Append(-1, text="Load &Configuration")
        self.Bind(wx.EVT_MENU, self.OnLoadConfiguration, item)
        fileMenu.AppendSeparator()
        item = fileMenu.Append(wx.ID_EXIT, text="&Quit")
        self.Bind(wx.EVT_MENU, self.OnQuit, item)
        menuBar.Append(fileMenu, "&File")
        
        modulesMenu = wx.Menu()
        item = modulesMenu.Append(-1, text="Choose")
        self.Bind(wx.EVT_MENU, self.OnShowChooseModules, item)
        self.configureModulesItem = modulesMenu.Append(-1, text="Configure")
        self.Bind(wx.EVT_MENU, self.OnShowConfigureModules, self.configureModulesItem)
        self.configureModulesItem.Enable(False)
        menuBar.Append(modulesMenu, "&Modules")
        
        runMenu = wx.Menu()
        self.parseModelItem = runMenu.Append(-1, text="&Parse Model")
        self.parseModelItem.Enable(False)
        self.Bind(wx.EVT_MENU, self.OnParseClicked, self.parseModelItem)
        self.runlItem = runMenu.Append(-1, text="Run")
        self.Bind(wx.EVT_MENU, self.OnRunClicked, self.runlItem)
        self.runlItem.Enable(False)
        menuBar.Append(runMenu, "&Run")
        
        self.SetMenuBar(menuBar)
        
        ###########
        # MODULES 
        ###########
        
        self.availableModules = [ timeanalysis.Module() ]
        self.selectedModules = []
        
        ###################
        # SIZERS & EVENTS
        ###################
        
        self.Bind(EVT_MODEL_PARSED, self.OnModelParsed)
        
        self.modelPanel = ModelPanel(self)
        self.modelPanel.modelNotebook.Bind(EVT_MODEL_CHANGED, self.OnModelChanged)
        
        self.parsePanel = ParsePanel(self)
        self.runPanel = RunPanel(self)
        
        self.modulesChoosePanel = ModulesChoosePanel(self, modules=self.availableModules)
        self.modulesChoosePanel.Bind(EVT_MODULES_CHANGED, self.OnModulesChanged)
        
        self.modulesConfigurationPanel = ModulesConfigurationPanel(self)

        self.ShowPanel(self.modelPanel)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.modelPanel, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.parsePanel, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.modulesChoosePanel, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.modulesConfigurationPanel, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.runPanel, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)
        
        self.Layout()
        
    def ShowPanel(self, panel):
        """ Shows selected panel and hides other panels. """
        self.parsePanel.Hide()
        self.modelPanel.Hide()
        self.modulesChoosePanel.Hide()
        self.modulesConfigurationPanel.Hide()
        self.runPanel.Hide()
        panel.Show()
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
        
    def OnShowModel(self, event):
        """ Show model panel """
        self.ShowPanel(self.modelPanel)
        
    def OnShowChooseModules(self, event):
        """ Show model panel """
        self.ShowPanel(self.modulesChoosePanel)
        
    def OnShowConfigureModules(self, event):
        """ Show modules configuration panel """
        self.ShowPanel(self.modulesConfigurationPanel)
        
    def _LoadFile(self, loadFileDataFunction, pageNumber):
        """ Load file to text area """
        ofdlg = wx.FileDialog(self, "Load file", "", "", "QoP-ML Files (*.qopml)|*.qopml", 
                              wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        ofdlg.ShowModal()
        loadFileDataFunction(ofdlg.GetPath())
        ofdlg.Destroy()
        self.modelPanel.modelNotebook.SetSelection(pageNumber)
        self.ShowPanel(self.modelPanel)
        
    def OnLoadModel(self, event):
        """ Load model file """
        self._LoadFile(self.modelPanel.modelNotebook.LoadModelFile, 0)
        
    def OnLoadMetrics(self, event):
        """ Load model file """
        self._LoadFile(self.modelPanel.modelNotebook.LoadMetricsFile, 1)
        
    def OnLoadConfiguration(self, event):
        """ Load model file """
        self._LoadFile(self.modelPanel.modelNotebook.LoadConfigurationFile, 2)
        
    def OnModelChanged(self, event):
        """ """
        modelReady = event.modelText != ""
        modelReady = modelReady and ( event.metricsText != "" )
        modelReady = modelReady and ( event.configurationText != "" )
        self.parseModelItem.Enable(modelReady)
        event.Skip()
        
    def OnModulesChanged(self, event):
        """ """
        modules = event.modules
        self.configureModulesItem.Enable(len(modules) > 0)
        self.selectedModules = modules
        self.modulesConfigurationPanel.SetModules(modules)
        event.Skip()
        
    def OnParseClicked(self, event):
        
        mN = self.modelPanel.modelNotebook
        self.interpreter = aqopa.app.GuiInterpreter(
                                     model_as_text=mN.GetModelData(), 
                                     metrics_as_text=mN.GetMetricsData(), 
                                     config_as_text=mN.GetConfigurationData())
        
        for m in self.selectedModules:
            self.interpreter.register_qopml_module(m)
        
        try:
            resultMessage = ""
            error = False
            self.interpreter.parse()
            resultMessage = "SUCCESFULLY PARSED\n\n Now you can run simulation."
            wx.PostEvent(self, ModelParsedEvent())
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
            self.parsePanel.parseResult.SetValue(resultMessage)
            
        self.ShowPanel(self.parsePanel)
        
    def OnRunClicked(self, event):
        """ """
        try:
            self.runlItem.Enable(False)
            self.finishedSimulators = []
            
            self.interpreter.prepare()
            
            self.progressTimer.Start(1000)
            
            for simulator in self.interpreter.simulators:
                wx.lib.delayedresult.startWorker(self.OnSimulationFinished, self.interpreter.run_simulation, wargs=(simulator,))
            
        except EnvironmentDefinitionException, e:
            self.runlItem.Enable(True)
            errorMessage = "Error on creating environment: %s\n" % e
            if len(e.errors) > 0:
                errorMessage += "Errors:\n"
                errorMessage += "\n".join(e.errors)
                
            self.runPanel.runResult.SetValue(errorMessage)
            
            self.progressTimer.Stop()
        
        self.ShowPanel(self.runPanel)
        
    def OnModelParsed(self, event):
        """ """
        self.runlItem.Enable(True)
        
    def OnSimulationFinished(self, result):
        """ """
        simulator = result.get()
        self.finishedSimulators.append(simulator)

        self.PrintProgressbar(self.GetProgress())
        
        for m in self.selectedModules:
            gui = m.get_gui()
            
            frame = gui.get_finished_simulation_frame(simulator)
            if frame:
                frame.Show(True)
                
        if len(self.finishedSimulators) == len(self.interpreter.simulators):
            self.OnAllSimulationsFinished()
                
    def OnAllSimulationsFinished(self):
        """ """
        for m in self.selectedModules:
            gui = m.get_gui()
            
            frame = gui.get_finished_all_simulations_frame(self.interpreter.simulators)
            if frame:
                frame.Show(True)
            
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
        self.runPanel.percentLabel.SetLabel(percentage)
        self.runPanel.sizer.Layout()
        
        if progress == 1:
            self.runPanel.statusLabel.SetLabel('Finished')
            self.runPanel.sizer.Layout()
            self.runPanel.dotsLabel.SetLabel('')
            self.runPanel.sizer.Layout()
        else:
            dots = self.runPanel.dotsLabel.GetLabel()
            if len(dots) > 0:
                dots = "."
            else:
                dots += ".."
            self.runPanel.dotsLabel.SetLabel(dots)
            self.runPanel.sizer.Layout()
        
        
class AqopaApp(wx.App):
    
    def OnInit(self):
        self.main_frame = MainFrame(None, title="AQoPA")
        self.main_frame.Show(True)
        self.SetTopWindow(self.main_frame)
        return True


def main():
    app = AqopaApp(False)
    app.MainLoop()


if __name__ == "__main__":
    main()