#!/usr/bin/env python
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
import wx.richtext
import wx.lib.newevent
import wx.lib.delayedresult

import aqopa
from aqopa import app
from aqopa.model.parser import MetricsParserException,\
    ConfigurationParserException, ModelParserException
from aqopa.module import timeanalysis
from aqopa.simulator.error import EnvironmentDefinitionException,\
    RuntimeException

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

        bPanel = wx.Panel(self)
        bSizer = wx.BoxSizer(wx.VERTICAL)
        bPanel.SetSizer(bSizer)

        self.loadButton = wx.Button(bPanel)
        self.saveButton = wx.Button(bPanel)
        
        self.attachButtons(self.loadButton, self.saveButton)
        
        bSizer.Add(self.loadButton, 0, wx.ALL, 5)
        bSizer.Add(self.saveButton, 0, wx.ALL, 5)

        rightPanel = wx.Panel(self)
        rightPanelSizer = wx.BoxSizer(wx.VERTICAL)
        rightPanel.SetSizer(rightPanelSizer)

        self.dataTextArea = wx.richtext.RichTextCtrl(rightPanel, style=wx.TE_MULTILINE | wx.TE_NO_VSCROLL)
        self.dataTextArea.Bind(wx.EVT_KEY_UP, self.printCursorInfo)
        self.dataTextArea.Bind(wx.EVT_LEFT_UP, self.printCursorInfo)
        
        self.cursorInfoLabel = wx.StaticText(rightPanel, label="")
        
        rightPanelSizer.Add(self.dataTextArea, 1, wx.EXPAND)
        rightPanelSizer.Add(self.cursorInfoLabel, 0, wx.ALIGN_RIGHT)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(bPanel, 0, wx.ALL, 5)
        sizer.Add(rightPanel, 1, wx.ALL | wx.EXPAND, 5)
        
        self.SetSizer(sizer)
        
        self.Layout()
        
    def attachButtons(self, loadButton, saveButton):
        """ """
        loadButton.Bind(wx.EVT_BUTTON, self.onLoad)
        saveButton.Bind(wx.EVT_BUTTON, self.onSave)
        
    def onLoad(self, event):
        """ Load file to text area """
        ofdlg = wx.FileDialog(self, "Load file", "", "", "QoP-ML Files (*.qopml)|*.qopml", 
                              wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        ofdlg.ShowModal()
        if ofdlg.GetPath():
            wildcard, types = wx.richtext.RichTextBuffer.GetExtWildcard(save=False)
            fileType = types[ofdlg.GetFilterIndex()]
            self.dataTextArea.LoadFile(ofdlg.GetPath(), fileType)  # self.rtc is the RichTExtCtrl object
        ofdlg.Destroy()
        
    def onSave(self, event):
        """ Save text area value to file """
        ofdlg = wx.FileDialog(self, "Save file", "", "", "QoP-ML Files (*.qopml)|*.qopml", 
                              wx.FD_SAVE)
        ofdlg.ShowModal()
        if ofdlg.GetPath():
            f = open(ofdlg.GetPath(), "w")
            f.write(self.dataTextArea.GetValue())
            f.close()
        ofdlg.Destroy()
        
    def printCursorInfo(self, event):
        """ """
        pos = self.dataTextArea.GetInsertionPoint()
        xy = self.dataTextArea.PositionToXY(pos)
        self.cursorInfoLabel.SetLabel("Line: %d, %d" 
                                      % (xy[1]+1, xy[0]+1))
        self.Layout()
        event.Skip()
        
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
        self.interpreter = app.GuiInterpreter(
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
            self.simulatorIndex = 0
            
            self.startAnalysisTime = time.time()
            
            self.interpreter.prepare()
            self.progressTimer.Start(1000)

            simulator = self.interpreter.simulators[self.simulatorIndex]
            wx.lib.delayedresult.startWorker(self.OnSimulationFinished, 
                                             self.interpreter.run_simulation, 
                                             wargs=(simulator,),
                                             jobID = self.simulatorIndex)
                
            
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
        simulator = self.interpreter.simulators[self.simulatorIndex]
        self.simulatorIndex += 1
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
                    
        except RuntimeException, e:
            runResultValue = self.runResult.GetValue()
            resultMessage = runResultValue + \
                "Version %s finished with error: %s.\n" \
                % (simulator.context.version.name, e.args[0])
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
        else:
            simulator = self.interpreter.simulators[self.simulatorIndex]
            wx.lib.delayedresult.startWorker(self.OnSimulationFinished, 
                                             self.interpreter.run_simulation, 
                                             wargs=(simulator,),
                                             jobID = self.simulatorIndex)
                
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
        event.Skip()
        
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
        item = fileMenu.Append(wx.ID_EXIT, text="&Quit")
        self.Bind(wx.EVT_MENU, self.OnQuit, item)
        menuBar.Append(fileMenu, "&File")
        
        self.SetMenuBar(menuBar)
        
        ###################
        # SIZERS & EVENTS
        ###################
        
        self.mainNotebook = MainNotebook(self)
        
        logo_filepath = os.path.join(os.path.dirname(__file__), 
                                     'assets', 
                                     'logo.png')
        logoPanel = wx.Panel(self)
        pic = wx.StaticBitmap(logoPanel)
        pic.SetBitmap(wx.Bitmap(logo_filepath))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(logoPanel, 0, wx.CENTER, 5)
        sizer.Add(self.mainNotebook, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)
        
        self.Layout()
        
    def OnQuit(self, event=None):
        """ Close app """
        self.Close()
        
    def OnAbout(self, event=None):
        """ Show about info """
        
        description = """AQoPA stands for Automated Quality of Protection Analysis Tool 
        for QoPML models."""

        licence = """AQoPA is free software; you can redistribute 
it and/or modify it under the terms of the GNU General Public License as 
published by the Free Software Foundation; either version 2 of the License, 
or (at your option) any later version.

AQoPA is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE."""
        
        logo_filepath = os.path.join(os.path.dirname(__file__), 
                                     'assets', 
                                     'logo.png')
        
        info = wx.AboutDialogInfo()
        info.SetIcon(wx.Icon(logo_filepath, wx.BITMAP_TYPE_PNG))
        info.SetName('AQoPA')
        info.SetVersion(aqopa.VERSION)
        info.SetDescription(description)
        info.SetCopyright('(C) 2013 QoPML Project')
        info.SetWebSite('http://www.qopml.org')
        info.SetLicence(licence)
        info.AddDeveloper('Damian Rusinek')
        info.AddDocWriter('Damian Rusinek')
        info.AddArtist('QoPML Project')
        info.AddTranslator('Damian Rusinek')
        
        wx.AboutBox(info)
        
        
class AqopaApp(wx.App):
    
    def OnInit(self):
        self.mainFrame = MainFrame(None, 
                                   title="Automated Quality of Protection Analysis Tool")
        self.mainFrame.Show(True)
        self.mainFrame.Maximize(True)
        self.SetTopWindow(self.mainFrame)
        
        return True
    
