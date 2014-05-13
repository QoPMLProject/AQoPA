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
from aqopa.gui.combo_check_box import ComboCheckBox

ModulesChangedEvent, EVT_MODULES_CHANGED = wx.lib.newevent.NewEvent()

class ModulesPanel(wx.Panel):
    """
    Panel used for selecting modules and configuring them.
    """

    def __init__(self, *args, **kwargs):
        self.allModules = kwargs['modules']
        del kwargs['modules']

        wx.Panel.__init__(self, *args, **kwargs)

        # our main sizer
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # 'Select' button = select chosen modules
        selectButton = wx.Button(self, label="Select")

        # create group boxes, aka static boxes
        modulesSelectionBox = wx.StaticBox(self, label="Select modules")
        modulesConfigurationBox = wx.StaticBox(self, label="Configure modules")
        modulesBox = wx.StaticBox(self, label="Modules")

        # create sizers = some kind of layout management
        modulesSelectionBoxSizer = wx.StaticBoxSizer(modulesSelectionBox, wx.HORIZONTAL)
        modulesConfigurationBoxSier = wx.StaticBoxSizer(modulesConfigurationBox, wx.HORIZONTAL)
        modulesBoxSizer = wx.StaticBoxSizer(modulesBox, wx.VERTICAL)

        # create labels, aka static texts
        selectModulesLabel = wx.StaticText(self, label="Choose modules for analysis and click the 'Select'\nbutton to add them to the configuration panel.")

        # create combocheckbox, empty at first [need 2 change this]
        self.comboCheckBox = wx.combo.ComboCtrl(self)
        self.tcp = ComboCheckBox()
        self.comboCheckBox.SetPopupControl(self.tcp)

        # add tooltipz = make user's life easier
        modulesSelectionBox.SetToolTip(wx.ToolTip("Select modules for analysis"))
        modulesConfigurationBox.SetToolTip(wx.ToolTip("Configure chosen modules"))

        # align 'select modules' group box
        modulesSelectionBoxSizer.Add(selectModulesLabel, 1, wx.ALL | wx.EXPAND, 5)
        modulesSelectionBoxSizer.Add(self.comboCheckBox, 1, wx.ALL | wx.EXPAND, 5)
        modulesSelectionBoxSizer.Add(selectButton, 0, wx.ALL | wx.EXPAND, 5)

        # do some bindings:
        selectButton.Bind(wx.EVT_BUTTON, self.OnSelectButtonClicked)

        self.configurationBox = wx.StaticBox(self, label="Configuration")
        configurationBoxSizer = wx.StaticBoxSizer(self.configurationBox, wx.HORIZONTAL)

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

            # ordnung muss sein
            modulePanelSizer.Add(ch, 0, wx.ALL)
            modulePanelSizer.Add(wx.StaticText(self), 1, wx.EXPAND, 5)
            modulePanelSizer.Add(btn, 0, wx.ALL)
            modulePanel.SetSizer(modulePanelSizer)

            modulesBoxSizer.Add(modulePanel, 0, wx.ALL | wx.EXPAND, 5)

            moduleConfigurationPanel = gui.get_configuration_panel(self)
            configurationBoxSizer.Add(moduleConfigurationPanel, 1, wx.ALL | wx.EXPAND, 5)
            moduleConfigurationPanel.Hide()

            self.ModulesPanels.append(moduleConfigurationPanel)
            self.buttonsPanelMap[btn] = moduleConfigurationPanel
            self.buttonsModuleGui[btn] = gui

        mainSizer.Add(modulesSelectionBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(modulesConfigurationBox, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(modulesBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(configurationBoxSizer, 1, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(mainSizer)

    def OnSelectButtonClicked(self, event):
        """
        @brief grabs selected modules from
        combocheckbox widget
        """
        pass

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