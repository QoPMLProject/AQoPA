#!/usr/bin/env python

import wx
import sys
import time
import traceback

# AQoPA imports
from aqopa import app
from aqopa.model.parser import MetricsParserException,\
    ConfigurationParserException, ModelParserException
from aqopa.simulator.error import EnvironmentDefinitionException,\
    RuntimeException

"""
@file       run_panel_gui.py
@brief      GUI for the 'Run' tab on AQoPA's main window (panel)
@author     Damian Rusinek <damian.rusinek@gmail.com>
@date       created on 05-09-2013 by Damian Rusinek
@date       edited on 08-05-2014 by Katarzyna Mazur (visual improvements)
"""

# model parsing events
ModelParsedEvent, EVT_MODEL_PARSED = wx.lib.newevent.NewEvent()
ModelParseErrorEvent, EVT_MODEL_PARSE_ERROR = wx.lib.newevent.NewEvent()

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

        panelSizer = wx.BoxSizer(wx.HORIZONTAL)

        # create the top panel - it can be the parsing panel
        # (when parsing the model) or the run panel = when
        # running the simulation process (analysis)
        topPanel = wx.Panel(self, style=wx.ALIGN_CENTER)
        topPanel.SetSizer(panelSizer)

        # build panels
        self.parsingPanel = self._BuildParsingPanel(topPanel)
        self.runPanel = self._BuildRunPanel(topPanel)

        # align panels
        panelSizer.Add(self.parsingPanel, 1, wx.ALL | wx.EXPAND, 5)
        panelSizer.Add(self.runPanel, 1, wx.ALL | wx.EXPAND, 5)

        # hide the run panel (for now on) it will be visible
        # after parsing the model and clicking the 'run' button
        self.runPanel.Hide()

        # align panels
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(topPanel, 1, wx.ALL | wx.EXPAND, 5)

        # create the bottom panel - the one with the buttons
        bottomPanel = wx.Panel(self, style=wx.ALIGN_CENTER)

        # create buttons
        self.parseButton = wx.Button(bottomPanel, label="Parse")
        self.parseButton.SetToolTip(wx.ToolTip("Parse chosen model"))
        self.runButton = wx.Button(bottomPanel, label="Run")
        self.runButton.SetToolTip(wx.ToolTip("Start the simulation process"))
        self.runButton.Enable(False)
        #self.cleanButton = wx.Button(bottomPanel, label="Clean")

        # properly align the bottom panel, buttons on the right
        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        panelSizer.Add(self.parseButton, 0, wx.LEFT | wx.ALL, 5)
        panelSizer.Add(self.runButton, 0, wx.LEFT | wx.ALL, 5)
        #panelSizer.Add(self.cleanButton, 0, wx.LEFT | wx.ALL, 5)
        bottomPanel.SetSizer(panelSizer)
        sizer.Add(bottomPanel, 0, wx.ALIGN_RIGHT | wx.RIGHT, 5)

        self.SetSizer(sizer)

        ###############
        # EVENTS
        ###############

        self.parseButton.Bind(wx.EVT_BUTTON, self.OnParseClicked)
        self.runButton.Bind(wx.EVT_BUTTON, self.OnRunClicked)
        #self.cleanButton.Bind(wx.EVT_BUTTON, self.OnCleanClicked)

        self.Bind(EVT_MODEL_PARSED, self.OnModelParsed)

    def _BuildParsingPanel(self, parent):
        """
        @brief      creates the parsing panel
        @return     brand new parsing panel
        """

        # new panel, we will return it and set as the main panel
        # for AQoPA's main windows's Run tab
        panel = wx.Panel(parent)

        # create group boxes aka static boxes
        parsingInfoBox = wx.StaticBox(panel, label="Model parsing information")
        # create sizers = some kind of layout management
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        parsingInfoBoxSizer = wx.StaticBoxSizer(parsingInfoBox, wx.HORIZONTAL)
        # create text area for displaying parsing information
        self.parseResult = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)

        # do the final panel alignment
        parsingInfoBoxSizer.Add(self.parseResult, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(parsingInfoBoxSizer, 1, wx.EXPAND, 5)
        panel.SetSizer(sizer)

        return panel

    def _BuildRunPanel(self, parent):
        """
        @brief      creates the run panel
        @return     brand new run panel
        """

        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # create group boxes aka static boxes
        self.statusStaticBox = wx.StaticBox(panel, label="Status: ")
        timeStaticBox = wx.StaticBox(panel, label="Analysis Time")
        runInfoBox = wx.StaticBox(panel, label="Model run information")

        # create sizers = some kind of layout management
        self.statusStaticBoxSizer = wx.StaticBoxSizer(self.statusStaticBox, wx.VERTICAL)
        timeStaticBoxSizer = wx.StaticBoxSizer(timeStaticBox, wx.VERTICAL)
        runInfoBoxSizer = wx.StaticBoxSizer(runInfoBox, wx.VERTICAL)
        progressSizer = wx.BoxSizer(wx.HORIZONTAL)

        # create labels
        self.percentLabel = wx.StaticText(panel, label="0%")
        self.dotsLabel = wx.StaticText(panel, label=".")
        self.analysisTime = wx.StaticText(panel, label='---')

        # create text area
        self.runResult = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)

        # add content to sizers
        progressSizer.Add(self.dotsLabel, 0, wx.ALIGN_LEFT, 5)
        progressSizer.Add(self.percentLabel, 0, wx.ALIGN_LEFT, 5)
        self.statusStaticBoxSizer.Add(progressSizer, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        timeStaticBoxSizer.Add(self.analysisTime, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        runInfoBoxSizer.Add(self.runResult, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.statusStaticBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(timeStaticBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(runInfoBoxSizer, 1, wx.ALL | wx.EXPAND, 5)

        # do the final alignment
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
        if not self.selectedModules:
            dial = wx.MessageDialog(None, "You have to choose some modules!", 'Warning', wx.OK | wx.ICON_EXCLAMATION)
            dial.ShowModal()
        else :
            try:
                self.DisableModulesSelection(True)

                self.statusStaticBox.SetLabel("Status: running")
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
                self.statusStaticBox.SetLabel("Status: error")
                self.runButton.Enable(True)
                errorMessage = "Error on creating environment: %s\n" % e
                if len(e.errors) > 0:
                    errorMessage += "Errors:\n"
                    errorMessage += "\n".join(e.errors)
                self.runResult.SetValue(errorMessage)
                self.progressTimer.Stop()

            except Exception, e:
                self.statusStaticBox.SetLabel("Error")
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
        self.DisableModulesSelection(False)
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
            self.statusStaticBox.SetLabel("Status: finished")
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

    #def OnCleanClicked(self, event):
    #    self.parseResult.Clear()

    def DisableModulesSelection(self, value) :

        """
        @brief  disables/enables elements on 'Modules' tab (panel),
        thanks to such approach we can get rid of some errors, simply
        disable modules selection/configuration when the simulation
        is running, and re-enable it when simulation ends
        """

        # get run panel parent - that is, the wx Notebook
        notebook = self.GetParent()
        # get modules panel, it's the third page in our wx Notebook
        modulesTab = notebook.GetPage(3)

        # disable or enable gui elements (depends on 'value')
        if value :
            modulesTab.selectButton.Disable()
            modulesTab.configureButton.Disable()
            modulesTab.comboCheckBox.Disable()
            modulesTab.modulesConfComboBox.Disable()
        else :
            modulesTab.selectButton.Enable()
            modulesTab.configureButton.Enable()
            modulesTab.comboCheckBox.Enable()
            modulesTab.modulesConfComboBox.Enable()