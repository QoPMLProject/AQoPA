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
from aqopa.simulator.error import EnvironmentDefinitionException,\
    RuntimeException

# gui imports
from aqopa.gui.models_lib_gui import LibraryFrame, EVT_MODEL_SELECTED
from aqopa.gui.modules_panel_gui import ModulesPanel, EVT_MODULES_CHANGED
from aqopa.gui.mmv_tab_panel_gui import MMVTabPanel

ModelParsedEvent, EVT_MODEL_PARSED = wx.lib.newevent.NewEvent()
ModelParseErrorEvent, EVT_MODEL_PARSE_ERROR = wx.lib.newevent.NewEvent()

# Modules communication events
ModuleSimulationRequestEvent, EVT_MODULE_SIMULATION_REQUEST = wx.lib.newevent.NewEvent() # Parameters: module
ModuleSimulationAllowedEvent, EVT_MODULE_SIMULATION_ALLOWED = wx.lib.newevent.NewEvent() # Parameters: interpreter
ModuleSimulationFinishedEvent, EVT_MODULE_SIMULATION_FINISHED = wx.lib.newevent.NewEvent()

"""
TODO : do the 'gui.py' code clean-up -> now its just the fast'n'dirty code [I mean, my edits]
"""
        
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

        self.allModules = []
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

    def SetAllModules(self, modules):
        """ """
        self.allModules = modules
        
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
            self.interpreter.parse(self.allModules)
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
                "Version %s finished successfully.\n\n" \
                % simulator.context.version.name
                    
        except RuntimeException, e:
            runResultValue = self.runResult.GetValue()
            resultMessage = runResultValue + \
                "Version %s finished with error: \nHost: %s \nInstruction: %s\nError: %s \n\n" \
                % (simulator.context.version.name,
                    unicode(simulator.context.get_current_host()),
                    unicode(simulator.context.get_current_instruction()),
                    e.args[0])
        except Exception, e:
            sys.stderr.write(traceback.format_exc())
            runResultValue = self.runResult.GetValue()
            resultMessage = runResultValue + \
                "Version %s finished with unknown error.\n\n" \
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
        self.Layout()
        
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
            resultPanel.Hide()
            
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
        for m in self.moduleResultPanel:
            self.moduleResultPanel[m].Hide()
        m = self.buttonsModule[btn]
        self.moduleResultPanel[m].Show()
        self.Layout()

class MainNotebook(wx.Notebook):
    """ """

    def __init__(self, parent):
        wx.Notebook.__init__(self, parent)

        ###########
        # MODULES
        ###########

        self.availableModules = []

        from aqopa.module import timeanalysis
        timeanalysis_module = timeanalysis.Module()
        timeanalysis_module.get_gui().Bind(EVT_MODULE_SIMULATION_REQUEST,
                                           self.OnModuleSimulationRequest)
        timeanalysis_module.get_gui().Bind(EVT_MODULE_SIMULATION_FINISHED,
                                           self.OnModuleSimulationFinished)
        self.availableModules.append(timeanalysis_module)

        from aqopa.module import energyanalysis
        m = energyanalysis.Module(timeanalysis_module)
        self.availableModules.append(m)

        from aqopa.module import reputation
        self.availableModules.append(reputation.Module())

        #list containing notebook images:
        # .ico seem to be more OS portable
        il = wx.ImageList(16, 16) #the (16, 16) is the size in pixels of the images
        modelsTabImg = il.Add(wx.Bitmap(os.path.join(os.path.dirname(__file__),
                                     'assets',
                                     'models_lib.png'), wx.BITMAP_TYPE_PNG))
        metricsTabImg = il.Add(wx.Bitmap(os.path.join(os.path.dirname(__file__),
                                     'assets',
                                     'metrics.png'), wx.BITMAP_TYPE_PNG))
        versionsTabImg = il.Add(wx.Bitmap(os.path.join(os.path.dirname(__file__),
                                     'assets',
                                     'versions.png'), wx.BITMAP_TYPE_PNG))
        runTabImg = il.Add(wx.Bitmap(os.path.join(os.path.dirname(__file__),
                                     'assets',
                                     'run.png'), wx.BITMAP_TYPE_PNG))

        modulesTabImg = il.Add(wx.Bitmap(os.path.join(os.path.dirname(__file__),
                                     'assets',
                                     'modules.png'), wx.BITMAP_TYPE_PNG))

        resultsTabImg = il.Add(wx.Bitmap(os.path.join(os.path.dirname(__file__),
                                     'assets',
                                     'results.png'), wx.BITMAP_TYPE_PNG))

        self.AssignImageList(il)


        ###########
        # TABS
        ###########

        self.modelTab = MMVTabPanel(self)

        self.modelTab.Layout()
        self.Bind(wx.EVT_TEXT, self.OnModelTextChange, self.modelTab.dataTextArea)
        self.AddPage(self.modelTab, "Model")
        self.SetPageImage(0, modelsTabImg)

        self.metricsTab = MMVTabPanel(self)
        self.metricsTab.Layout()
        self.Bind(wx.EVT_TEXT, self.OnModelTextChange, self.metricsTab.dataTextArea)
        self.AddPage(self.metricsTab, "Metrics")
        self.SetPageImage(1, metricsTabImg)

        self.versionsTab = MMVTabPanel(self)
        self.versionsTab.Layout()
        self.Bind(wx.EVT_TEXT, self.OnModelTextChange, self.versionsTab.dataTextArea)
        self.versionsTab.Layout()
        self.AddPage(self.versionsTab, "Versions")
        self.SetPageImage(2, versionsTabImg)

        self.modulesTab = ModulesPanel(self, modules=self.availableModules)
        self.modulesTab.Bind(EVT_MODULES_CHANGED, self.OnModulesChange)
        self.modulesTab.Layout()
        self.AddPage(self.modulesTab, "Modules")
        self.SetPageImage(3, modulesTabImg)

        self.runTab = RunPanel(self)
        self.runTab.SetAllModules(self.availableModules)
        self.runTab.Layout()
        self.runTab.Bind(EVT_MODEL_PARSED, self.OnModelParsed)
        self.AddPage(self.runTab, "Run")
        self.SetPageImage(4, runTabImg)

        self.resultsTab = ResultsPanel(self)
        self.resultsTab.Layout()
        self.AddPage(self.resultsTab, "Results")
        self.SetPageImage(5, resultsTabImg)

    def LoadModelFile(self, filePath):
        self.modelTab.dataTextArea.LoadFile(filePath)

    def LoadMetricsFile(self, filePath):
        self.metricsTab.dataTextArea.LoadFile(filePath)

    def LoadVersionsFile(self, filePath):
        self.versionsTab.dataTextArea.LoadFile(filePath)

    def SetModelData(self, data):
        self.modelTab.dataTextArea.SetValue(data)

    def SetMetricsData(self, data):
        self.metricsTab.dataTextArea.SetValue(data)

    def SetVersionsData(self, data):
        self.versionsTab.dataTextArea.SetValue(data)

    def GetModelData(self):
        return self.modelTab.dataTextArea.GetValue().strip()

    def GetMetricsData(self):
        return self.metricsTab.dataTextArea.GetValue().strip()

    def GetVersionsData(self):
        return self.versionsTab.dataTextArea.GetValue().strip()

    def OnModelTextChange(self, event):
        self.runTab.SetModel(self.GetModelData(),
                             self.GetMetricsData(),
                             self.GetVersionsData())
        event.Skip()

    def OnModulesChange(self, event):
        self.runTab.SetSelectedModules(event.modules)
        self.resultsTab.SetSelectedModules(event.modules)

    def OnModelParsed(self, event):
        self.resultsTab.ClearResults()
        event.Skip()

    def OnModuleSimulationRequest(self, event):
        """ """
        gui = event.module.get_gui()
        self.runTab.runButton.Enable(False)
        self.runTab.parseButton.Enable(False)

        wx.PostEvent(gui, ModuleSimulationAllowedEvent(interpreter=self.runTab.interpreter))

    def OnModuleSimulationFinished(self, event):
        """ """
        self.runTab.parseButton.Enable(True)

class MainFrame(wx.Frame):
    """ """
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        ###########
        # MENUBAR
        ###########

        # create menubar
        menuBar = wx.MenuBar()

        #create main menu, lets call it 'file' menu
        fileMenu = wx.Menu()
        # create menu item = about AQoPA
        item = wx.MenuItem(fileMenu, wx.NewId(), u"&About AQoPA\tCTRL+I")
        item.SetBitmap(wx.Bitmap(self.CreatePath4Resource('about.png')))
        fileMenu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnAbout, item)
        fileMenu.AppendSeparator()
        # create menu item = quit AQoPa
        item = wx.MenuItem(fileMenu, wx.NewId(), u"&Quit\tCTRL+Q")
        item.SetBitmap(wx.Bitmap(self.CreatePath4Resource('exit.png')))
        fileMenu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnQuit, item)
        # add 'file' menu to the menubar
        menuBar.Append(fileMenu, "&Menu")

        # create library menu, here u can find modules library
        libraryMenu = wx.Menu()
        # create models menu item
        item = wx.MenuItem(libraryMenu, wx.NewId(), u"&Browse models\tCTRL+M")
        item.SetBitmap(wx.Bitmap(self.CreatePath4Resource('models_lib.png')))
        libraryMenu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnBrowseModels, item)

        # create metric menu item
        item = wx.MenuItem(libraryMenu, wx.NewId(), u"&Browse metrics\tCTRL+F")
        item.SetBitmap(wx.Bitmap(self.CreatePath4Resource('metrics.png')))
        libraryMenu.AppendItem(item)

        # add 'library' menu to the menubar
        menuBar.Append(libraryMenu, "&Library")

        self.SetMenuBar(menuBar)

        ###################
        # SIZERS & EVENTS
        ###################

        self.mainNotebook = MainNotebook(self)

        logoPanel = wx.Panel(self)
        pic = wx.StaticBitmap(logoPanel)
        pic.SetBitmap(wx.Bitmap(self.CreatePath4Resource('logo.png')))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticText(self), 1, wx.EXPAND, 5)
        sizer.Add(logoPanel, 0, wx.RIGHT| wx.ALL|wx.EXPAND, 5)
        s2 = wx.BoxSizer(wx.VERTICAL)
        s2.Add(sizer, 0, wx.LEFT| wx.ALL|wx.EXPAND, 5)
        s2.Add(self.mainNotebook, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(s2)

        self.SetIcon(wx.Icon(self.CreatePath4Resource('app_logo.png'), wx.BITMAP_TYPE_PNG))
        self.SetMinSize(wx.Size(900, 700))
        self.CenterOnScreen()
        self.Layout()

    def CreatePath4Resource(self, resourceName):
        """
        @brief      creates and returns path to the
                    given file in the resource
                    ('assets') dir
        @return     path to the resource
        """
        return os.path.join(os.path.dirname(__file__),
                                     'assets',
                                     resourceName)

    def OnQuit(self, event=None):
        """
        @brief  closes the application
        """
        self.Close()

    def OnBrowseModels(self, event=None):
        """
        @brief  shows the library frame (models library window)
        """
        libraryFrame = LibraryFrame(self, title="Models Library")
        libraryFrame.Show(True)
        libraryFrame.CentreOnParent()
        #libraryFrame.Maximize(True)
        libraryFrame.Bind(EVT_MODEL_SELECTED, self.OnLibraryModelSelected)

    def OnLibraryModelSelected(self, event):
        """ """
        self.mainNotebook.SetModelData(event.model_data)
        self.mainNotebook.SetMetricsData(event.metrics_data)
        self.mainNotebook.SetVersionsData(event.versions_data)
        # set filenames on GUI
        self.mainNotebook.modelTab.SetFilenameOnGUI(event.filenames['model'])
        self.mainNotebook.metricsTab.SetFilenameOnGUI(event.filenames['metrics'])
        self.mainNotebook.versionsTab.SetFilenameOnGUI(event.filenames['versions'])

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

        logo_filepath = self.CreatePath4Resource('logo.png')

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
        self.mainFrame.CenterOnScreen()
       # self.mainFrame.Maximize(True)
        self.SetTopWindow(self.mainFrame)

        return True
    

