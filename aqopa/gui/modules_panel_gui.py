#!/usr/bin/env python

"""
@file       modules_panel_gui.py
@brief      GUI for the 'Modules' tab on AQoPA's main window (panel)
@author     Damian Rusinek
@date       created on 05-09-2013 by Damian Rusinek
@date       edited on 07-05-2014 by Katarzyna Mazur (visual improvements mainly)
"""

import wx
import wx.lib.newevent

ModulesChangedEvent, EVT_MODULES_CHANGED = wx.lib.newevent.NewEvent()

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
        self.ModulesPanels = []

        emptyPanel = wx.Panel(self, size=(200,20))
        sizer = wx.BoxSizer(wx.VERTICAL)
        text = wx.StaticText(emptyPanel, label="Click 'Configure' button to configure selected module.")
        sizer.Add(text, 0, wx.ALL | wx.EXPAND, 5)
        emptyPanel.SetSizer(sizer)
        configurationBoxSizer.Add(emptyPanel, 1, wx.ALL | wx.EXPAND, 5)
        self.ModulesPanels.append(emptyPanel)

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

            self.ModulesPanels.append(moduleConfigurationPanel)
            self.buttonsPanelMap[btn] = moduleConfigurationPanel
            self.buttonsModuleGui[btn] = gui

        mainSizer.Add(modulesBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(configurationBoxSizer, 1, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(mainSizer)

    def ShowModuleConfigurationPanel(self, panel):
        """ """
        for p in self.ModulesPanels:
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

        wx.PostEvent(self, ModulesChangedEvent(modules=modules, all_modules=self.allModules))

    def OnConfigureButtonClicked(self, event):
        """ """
        btn = event.EventObject
        moduleGui = self.buttonsModuleGui[btn]

        self.configurationBox.SetLabel("%s - Configuration" % moduleGui.get_name())
        self.ShowModuleConfigurationPanel(self.buttonsPanelMap[btn])