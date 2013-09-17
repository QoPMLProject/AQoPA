'''
Created on 05-09-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''
import os
import sys
import time
import threading
import traceback
import wx
import wx.lib.newevent
import wx.lib.delayedresult

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

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
    
    def __init__(self, *args, **kwargs):
        """ """
        wx.Panel.__init__(self, *args, **kwargs)
    
        self.dataTextArea = wx.TextCtrl(self, style=wx.TE_MULTILINE)

        bPanel = wx.Panel(self)
        bSizer = wx.BoxSizer(wx.VERTICAL)
        bPanel.SetSizer(bSizer)

        self.loadButton = wx.Button(bPanel)
        self.saveButton = wx.Button(bPanel)
        
        bSizer.Add(self.loadButton, 0, wx.ALL, 5)
        bSizer.Add(self.saveButton, 0, wx.ALL, 5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(bPanel, 0, wx.ALL, 5)
        sizer.Add(self.dataTextArea, 1, wx.ALL | wx.EXPAND, 5)
        
        self.SetSizer(sizer)
        
        self.Layout()
        
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
        
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        statusStaticBox = wx.StaticBox(panel, label="Status")
        statusStaticBoxSizer = wx.StaticBoxSizer(statusStaticBox, wx.VERTICAL)

        self.statusLabel = wx.StaticText(panel, label="Running")
        self.percentLabel = wx.StaticText(panel, label="0%")
        self.dotsLabel = wx.StaticText(panel, label=".")
        
        statusStaticBoxSizer.Add(self.statusLabel, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        statusStaticBoxSizer.Add(self.percentLabel, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        statusStaticBoxSizer.Add(self.dotsLabel, 0, wx.ALL|wx.ALIGN_CENTER, 5)
        
        
        timeStaticBox = wx.StaticBox(panel, label="Analysis Time")
        timeStaticBoxSizer = wx.StaticBoxSizer(timeStaticBox, wx.VERTICAL)
        
        self.analysisTime = wx.StaticText(panel, label='---')
        
        timeStaticBoxSizer.Add(self.analysisTime, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        
        text = wx.StaticText(panel, label="Run Info")
        self.runResult = wx.TextCtrl(panel, 
                                     style=wx.TE_MULTILINE | wx.TE_READONLY)
    
        sizer.Add(statusStaticBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(timeStaticBoxSizer, 0, wx.ALL | wx.EXPAND, 5)    
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
            resultMessage = "VERSIONS SYNTAX ERROR\n"
            if len(e.syntax_errors):
                resultMessage += "\n".join(e.syntax_errors)
        
        if error:
            resultMessage += "\nModel may include syntax parsed by modules (eg. metrics, configuration). "+\
                             "Have you selected modules?"
            wx.PostEvent(self, ModelParseErrorEvent(error=resultMessage))
        if resultMessage != "":
            self.parseResult.SetValue(resultMessage)
            
        self.ShowPanel(self.parsingPanel)
            
    def OnModelParsed(self, event):
        """ """
        self.runButton.Enable(True)
            
    def OnRunClicked(self, event):
        """ """
        try:
            self.statusLabel.SetLabel("Running")
            self.analysisTime.SetLabel("---")
            self.percentLabel.SetLabel("0%")
            self.runResult.SetValue("")
            
            self.runButton.Enable(False)
            self.ShowPanel(self.runPanel)
            
            self.finishedSimulators = []
            self.jobs = {}
            
            self.startAnalysisTime = time.time()
            
            self.interpreter.prepare()
            self.progressTimer.Start(1000)
            i = 0
            for simulator in self.interpreter.simulators:
                wx.lib.delayedresult.startWorker(self.OnSimulationFinished, 
                                                 self.interpreter.run_simulation, 
                                                 wargs=(simulator,),
                                                 jobID = i)
                self.jobs[i] = simulator
                i += 1
                
            
        except EnvironmentDefinitionException, e:
            self.statusLabel.SetLabel("Error")
            self.runButton.Enable(True)
            errorMessage = "Error on creating environment: %s\n" % e
            if len(e.errors) > 0:
                errorMessage += "Errors:\n"
                errorMessage += "\n".join(e.errors)
            self.runResult.SetValue(errorMessage)
            self.progressTimer.Stop()
            
        except Exception, e:
            self.statusLabel.SetLabel("Error")
            self.runButton.Enable(True)
            sys.stderr.write(traceback.format_exc())
            errorMessage = "Unknown error\n"
            self.runResult.SetValue(errorMessage)
            self.progressTimer.Stop()
        
        self.ShowPanel(self.runPanel)
        
    def OnSimulationFinished(self, result):
        """ """
        jobID = result.getJobID()
        simulator = self.jobs[jobID]
        self.finishedSimulators.append(simulator)
        resultMessage = None
        try :
            
            simulator = result.get()
    
            self.PrintProgressbar(self.GetProgress())
            
            for m in self.selectedModules:
                gui = m.get_gui()
                gui.on_finished_simulation(simulator)
                
            runResultValue = self.runResult.GetValue()
            resultMessage = runResultValue + \
                "Version %s finished successfully.\n" \
                % simulator.context.version.name
                    
        except RuntimeError, e:
            pass
        except Exception, e:
            sys.stderr.write(traceback.format_exc())
            
            runResultValue = self.runResult.GetValue()
            resultMessage = runResultValue + \
                "Version %s finished with unknown error.\n" \
                % simulator.context.version.name
        
        if resultMessage:    
            self.runResult.SetValue(resultMessage)
        
        if len(self.finishedSimulators) == len(self.interpreter.simulators):
            self.OnAllSimulationsFinished()
            
                
    def OnAllSimulationsFinished(self):
        """ """
        self.progressTimer.Stop()
        self.PrintProgressbar(1)
        
        self.endAnalysisTime = time.time()
        timeDelta = self.endAnalysisTime - self.startAnalysisTime
        analysisTimeLabel = "%.4f s" % timeDelta 
        
        self.analysisTime.SetLabel(analysisTimeLabel)
        self.Layout()
        
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
            if len(dots) > 10:
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
        
    def ClearResults(self):
        """ """
        for m in self.selectedModules:
            gui = m.get_gui()
            gui.on_parsed_model()
                    
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
        self.modelTab.loadButton.SetLabel("Load Model")
        self.modelTab.saveButton.SetLabel("Save Model")
        self.modelTab.Layout()
        self.Bind(wx.EVT_TEXT, self.OnModelTextChange, self.modelTab.dataTextArea)
        self.AddPage(self.modelTab, "Model")
        
        self.metricsTab = ModelPartDataPanel(self)
        self.metricsTab.loadButton.SetLabel("Load Metrics")
        self.metricsTab.saveButton.SetLabel("Save Metrics")
        self.metricsTab.Layout()
        self.Bind(wx.EVT_TEXT, self.OnModelTextChange, self.metricsTab.dataTextArea)
        self.AddPage(self.metricsTab, "Metrics")
        
        self.configurationTab = ModelPartDataPanel(self)
        self.configurationTab.loadButton.SetLabel("Load Versions")
        self.configurationTab.saveButton.SetLabel("Save Versions")
        self.configurationTab.Layout()
        self.Bind(wx.EVT_TEXT, self.OnModelTextChange, self.configurationTab.dataTextArea)
        self.configurationTab.Layout()
        self.AddPage(self.configurationTab, "Versions")
        
        self.modulesTab = ModulesPanel(self, modules=self.availableModules)
        self.modulesTab.Bind(EVT_MODULES_CHANGED, self.OnModulesChange)
        self.modulesTab.Layout()
        self.AddPage(self.modulesTab, "Modules")
        
        self.runTab = RunPanel(self)
        self.runTab.Layout()
        self.runTab.Bind(EVT_MODEL_PARSED, self.OnModelParsed)
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
        
    def OnModelParsed(self, event):
        self.resultsTab.ClearResults()
        event.Skip()
        
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
        self.Bind(wx.EVT_MENU, self.OnLoadConfiguration, item)
        fileMenu.AppendSeparator()
        item = fileMenu.Append(wx.ID_EXIT, text="&Quit")
        self.Bind(wx.EVT_MENU, self.OnQuit, item)
        menuBar.Append(fileMenu, "&File")
        
        self.SetMenuBar(menuBar)
        
        ###################
        # SIZERS & EVENTS
        ###################
        
        self.mainNotebook = MainNotebook(self)
        
        self.Bind(wx.EVT_BUTTON, self.OnLoadModel, self.mainNotebook.modelTab.loadButton)
        self.Bind(wx.EVT_BUTTON, self.OnLoadMetrics, self.mainNotebook.metricsTab.loadButton)
        self.Bind(wx.EVT_BUTTON, self.OnLoadConfiguration, self.mainNotebook.configurationTab.loadButton)
        
        self.Bind(wx.EVT_BUTTON, self.OnSaveModel, self.mainNotebook.modelTab.saveButton)
        self.Bind(wx.EVT_BUTTON, self.OnSaveMetrics, self.mainNotebook.metricsTab.saveButton)
        self.Bind(wx.EVT_BUTTON, self.OnSaveConfiguration, self.mainNotebook.configurationTab.saveButton)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.mainNotebook, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)
        
        self.Layout()
        
    def OnQuit(self, event=None):
        """ Close app """
        self.Close()
        
    def OnAbout(self, event=None):
        """ Show about info """
        dlg = wx.MessageDialog(self, "Automated Quality of Protection Analysis tool of QoP-ML models.\n" +\
                                     "Version: %s\n\nProject Home: http://qopml.org" % aqopa.VERSION, 
                               "About AQoPA", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        
    def _LoadFile(self, loadFileDataFunction, pageNumber):
        """ Load file to text area """
        ofdlg = wx.FileDialog(self, "Load file", "", "", "QoP-ML Files (*.qopml)|*.qopml", 
                              wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        ofdlg.ShowModal()
        if ofdlg.GetPath():
            loadFileDataFunction(ofdlg.GetPath())
        ofdlg.Destroy()
        self.mainNotebook.SetSelection(pageNumber)
        
    def _SaveFile(self, getDataFunction, pageNumber):
        """ Load file to text area """
        ofdlg = wx.FileDialog(self, "Save file", "", "", "QoP-ML Files (*.qopml)|*.qopml", 
                              wx.FD_SAVE)
        ofdlg.ShowModal()
        if ofdlg.GetPath():
            f = open(ofdlg.GetPath(), "w")
            f.write(getDataFunction())
            f.close()
        ofdlg.Destroy()
        self.mainNotebook.SetSelection(pageNumber)
        
    def OnLoadModel(self, event):
        """ Load model file """
        self._LoadFile(self.mainNotebook.LoadModelFile, 0)
        
    def OnLoadMetrics(self, event):
        """ Load model file """
        self._LoadFile(self.mainNotebook.LoadMetricsFile, 1)
        
    def OnLoadConfiguration(self, event):
        """ Load model file """
        self._LoadFile(self.mainNotebook.LoadConfigurationFile, 2)
        
    def OnSaveModel(self, event):
        """ Load model file """
        self._SaveFile(self.mainNotebook.GetModelData, 0)
        
    def OnSaveMetrics(self, event):
        """ Load model file """
        self._SaveFile(self.mainNotebook.GetMetricsData, 1)
        
    def OnSaveConfiguration(self, event):
        """ Load model file """
        self._SaveFile(self.mainNotebook.GetConfigurationData, 2)
        
        
class AqopaApp(wx.App):
    
    def OnInit(self):
        self.mainFrame = MainFrame(None, title="AQoPA")
        self.mainFrame.Show(True)
        self.mainFrame.Maximize(True)
        self.SetTopWindow(self.mainFrame)
        
        self.mainFrame.Bind(wx.EVT_KEY_UP, self.OnKeyDown)
        
        return True
    
    def OnKeyDown(self, event):
        if event.KeyCode == 76:
            self.mainFrame.mainNotebook.configurationTab.dataTextArea.SetValue(""" versions {
  
  version scenario1_sim100 {


    set host Server(Server);

    run host KeysStore(*) {
      run Store1(*)
    }
    run host Server(*) {
      run Server1(get_db_key,decrypt_aes_256_sim_100,select_rows_100,get_rows)
    }
    run host Client(*){10}[ch1, ch2] {
      run Client1(*)
    }
  }
  
  version scenario1_sim200 {


    set host Server(Server1);

    run host KeysStore(*) {
      run Store1(*)
    }
    run host Server(*) {
      run Server1(get_db_key,decrypt_aes_256_sim_200,select_rows_200,get_rows)
    }
    run host Client(*){20}[ch1, ch2] {
      run Client1(*)
    }
  }
  
  
  
  version scenario2_sim100 {


    set host Server(Server);

    run host KeysStore(*) {
      run Store1(*)
    }
    run host Server(*) {
      run Server1(get_db_key,decrypt_aes_128_sim_100,select_rows_100,get_rows)
    }
    run host Client(*){10}[ch1, ch2] {
      run Client1(*)
    }
  }
  
  version scenario2_sim200 {


    set host Server(Server1);

    run host KeysStore(*) {
      run Store1(*)
    }
    run host Server(*) {
      run Server1(get_db_key,decrypt_aes_128_sim_200,select_rows_200,get_rows)
    }
    run host Client(*){20}[ch1, ch2] {
      run Client1(*)
    }
  }
} """)
            self.mainFrame.mainNotebook.modelTab.dataTextArea.SetValue(""" functions {
  fun nonce() (create nonce);

  fun s_enc(data, key); 
  fun s_dec(data, key); 
  fun sign(data, s_key); 
  fun a_enc(data, p_key);
  fun a_dec(data, s_key);
  fun pkey(skey);
  fun skey();
  fun hash(data);
  
  fun id_c() (identification of Client);
  fun crit() (searching criteria);
  
  fun database() (creates non-encrypted database);
  fun key_request() (creates key request);
  fun get_db_key(key) (retrieving key for database);
  fun select_rows(database, criteria);
} 

equations {
  eq s_dec(s_enc(data, key), key) = data;
  eq a_dec(a_enc(data, pkey(skey)), skey) = data;
  
  eq get_db_key(key) = key;
}

channels {
  channel ch1,ch2,ch3,ch4 (*);
}

hosts {

 host Client(rr)(ch1, ch2) {
 
   #ID_C = id_c();
   #CRIT = crit();
 
   process Client1(ch1, ch2) {
     M1 = (ID_C, CRIT);
     out(ch1: M1);
     in(ch2: M2);
   }
 
 }
 
 host Server(rr)(ch1, ch2, ch3, ch4) {
 
   #DB_KEY = nonce();
   #DB = s_enc(database(), DB_KEY);
   #SK_S = skey();
 
   process Server1(ch1, ch2, ch3, ch4) {
   
     while(true) {
    in(ch1: M1);
    
    CRIT = M1[1];
      
    subprocess get_db_key(ch3, ch4) {
      R = key_request();
      out (ch3: R);
      in (ch4: TMP_DB_KEY);
    }
      
    subprocess decrypt_aes_128_sim_100() {
      DB_PLAINTEXT = s_dec(DB, TMP_DB_KEY)[AES,128,CBC,300MB,100];
    }
    
    subprocess decrypt_aes_128_sim_200() {
      DB_PLAINTEXT = s_dec(DB, TMP_DB_KEY)[AES,128,CBC,300MB,200];
    }
      
    subprocess decrypt_aes_256_sim_100() {
      DB_PLAINTEXT = s_dec(DB, TMP_DB_KEY)[AES,256,CBC,300MB,100];
    }
    
    subprocess decrypt_aes_256_sim_200() {
      DB_PLAINTEXT = s_dec(DB, TMP_DB_KEY)[AES,256,CBC,300MB,200];
    }
    
    subprocess get_db() {
      DB_PLAINTEXT = s_dec(DB, TMP_DB_KEY);
    }
    
    subprocess select_rows_100() {
      ROWS = select_rows(DB_PLAINTEXT, CRIT)[100];
    }
    
    subprocess select_rows_200() {
      ROWS = select_rows(DB_PLAINTEXT, CRIT)[200];
    }
    
    subprocess get_rows() {
      M2 = ROWS;
    }
    
    subprocess get_rows_with_hash_and_signature_100() {
      H = hash(ROWS)[SHA1,1MB,100];
      SGN = sign(H, SK_S)[20B,RSA,2048,100];
      M2 = (ROWS,SGN);
    }
    
    subprocess get_rows_with_hash_and_signature_200() {
      H = hash(ROWS)[SHA1,1MB,200];
      SGN = sign(H, SK_S)[20B,RSA,2048,200];
      M2 = (ROWS,SGN);
    }
    
    out(ch2: M2);
     }
   }
 
 }
 
 host KeysStore(rr)(ch3, ch4) {
 
   #DB_KEY = nonce();
 
   process Store1(ch3, ch4) {
   
     while (true) {
       in (ch3: Request);
       KEY = get_db_key(DB_KEY);
       out(ch4: KEY);
     }
   }
 
 }

} """)
            self.mainFrame.mainNotebook.metricsTab.dataTextArea.SetValue(""" metrics {
  conf(Server) {
    CPU = 12 x Intel Core i7-3930K 3.20GHz;
    CryptoLibrary = openssl 1.0.1c;
    OS = Debian 7.1 64-bit;
  }
  
  conf(Server1) {
    CPU = 12 x Intel Core i7-3930K 3.20GHz;
    CryptoLibrary = openssl 1.0.1c;
    OS = Debian 7.1 64-bit;
  }

  data(Server) {
    primhead[function][input_size][algorithm][key_bitlength][simultaneous_operations][time:exact(ms)];
    primitive[sign][20B][RSA][2048][100][0.2839];
    primitive[sign][20B][RSA][2048][200][0.1577];
    #
    primhead[function][simultaneous_operations][time:exact(ms)];
    primitive[select_rows][100][2235.5903];
    primitive[select_rows][200][6487.1342];
    #
    primhead[function][algorithm][key_bitlength][mode][input_size][simultaneous_operations][time:exact(ms)];
    primitive[s_dec][AES][128][CBC][300MB][100][12132.5026];
    primitive[s_dec][AES][128][CBC][300MB][200][14126.168];
    primitive[s_dec][AES][256][CBC][300MB][100][12239.8706];
    primitive[s_dec][AES][256][CBC][300MB][200][14092.4126];
    #
    primhead[function][algorithm][input_size][simultaneous_operations][time:exact(ms)];
    primitive[hash][SHA1][1MB][100][0.1797];    
    primitive[hash][SHA1][1MB][200][0.0861];    
    
  }

  data(Server1) {
    primhead[function][input_size][algorithm][key_bitlength][simultaneous_operations][time:exact(ms)];
    primitive[sign][20B][RSA][2048][100][0.4839];
    primitive[sign][20B][RSA][2048][200][0.3577];
    #
    primhead[function][simultaneous_operations][time:exact(ms)];
    primitive[select_rows][100][2435.5903];
    primitive[select_rows][200][7487.1342];
    #
    primhead[function][algorithm][key_bitlength][mode][input_size][simultaneous_operations][time:exact(ms)];
    primitive[s_dec][AES][128][CBC][300MB][100][14132.5026];
    primitive[s_dec][AES][128][CBC][300MB][200][16126.168];
    primitive[s_dec][AES][256][CBC][300MB][100][14239.8706];
    primitive[s_dec][AES][256][CBC][300MB][200][16092.4126];
    #
    primhead[function][algorithm][input_size][simultaneous_operations][time:exact(ms)];
    primitive[hash][SHA1][1MB][100][0.2797];    
    primitive[hash][SHA1][1MB][200][0.0861];    
    
  }
}
 """)


def main():
    app = AqopaApp(False)
    app.MainLoop()


if __name__ == "__main__":
    main()
