#!/usr/bin/env python

import wx
import os

# AQoPA gui imports
from aqopa.gui.modules_panel_gui import ModulesPanel, EVT_MODULES_CHANGED
from aqopa.gui.mmv_panel_gui import MMVPanel
from aqopa.gui.run_panel_gui import RunPanel, EVT_MODEL_PARSED
from aqopa.gui.results_panel_gui import ResultsPanel

"""
@file       main_notebook_gui.py
@brief      GUI for the main notebook, where we attach our AQoPA tabs
@author     Damian Rusinek
@date       created on 05-09-2013 by Damian Rusinek
@date       edited on 07-05-2014 by Katarzyna Mazur (visual improvements mainly)
"""

# modules communication events
ModuleSimulationRequestEvent, EVT_MODULE_SIMULATION_REQUEST = wx.lib.newevent.NewEvent() # Parameters: module
ModuleSimulationAllowedEvent, EVT_MODULE_SIMULATION_ALLOWED = wx.lib.newevent.NewEvent() # Parameters: interpreter
ModuleSimulationFinishedEvent, EVT_MODULE_SIMULATION_FINISHED = wx.lib.newevent.NewEvent()

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

        # list containing notebook images:
        # .ico seem to be more OS portable, although we use .png here
        # the (20, 20) is the size in pixels of the images
        il = wx.ImageList(20, 20)
        modelsTabImg = il.Add(wx.Bitmap(self.CreatePath4Resource('models_lib.png'), wx.BITMAP_TYPE_PNG))
        metricsTabImg = il.Add(wx.Bitmap(self.CreatePath4Resource('metrics.png'), wx.BITMAP_TYPE_PNG))
        versionsTabImg = il.Add(wx.Bitmap(self.CreatePath4Resource('versions.png'), wx.BITMAP_TYPE_PNG))
        runTabImg = il.Add(wx.Bitmap(self.CreatePath4Resource('run.png'), wx.BITMAP_TYPE_PNG))
        modulesTabImg = il.Add(wx.Bitmap(self.CreatePath4Resource('modules.png'), wx.BITMAP_TYPE_PNG))
        resultsTabImg = il.Add(wx.Bitmap(self.CreatePath4Resource('results.png'), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)

        ###########
        # TABS
        ###########

        self.modelTab = MMVPanel(self)
        self.modelTab.Layout()
        self.Bind(wx.EVT_TEXT, self.OnModelTextChange, self.modelTab.dataTextArea)
        self.AddPage(self.modelTab, "Model")
        self.SetPageImage(0, modelsTabImg)

        self.metricsTab = MMVPanel(self)
        self.metricsTab.Layout()
        self.Bind(wx.EVT_TEXT, self.OnModelTextChange, self.metricsTab.dataTextArea)
        self.AddPage(self.metricsTab, "Metrics")
        self.SetPageImage(1, metricsTabImg)

        self.versionsTab = MMVPanel(self)
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

    def CreatePath4Resource(self, resourceName):
        """
        @brief      creates and returns path to the
                    given file in the resource
                    ('assets') dir
        @return     path to the resource
        """
        tmp = os.path.split(os.path.dirname(__file__))
        return os.path.join(tmp[0], 'bin', 'assets', resourceName)

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