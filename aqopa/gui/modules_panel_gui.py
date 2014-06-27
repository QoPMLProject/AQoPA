#!/usr/bin/env python

import wx
import wx.lib.newevent
from aqopa.gui.combo_check_box import ComboCheckBox
from aqopa.gui.general_purpose_frame_gui import GeneralFrame

"""
@file       modules_panel_gui.py
@brief      GUI for the 'Modules' tab on AQoPA's main window (panel)
@author     Damian Rusinek <damian.rusinek@gmail.com>
@date       created on 05-09-2013 by Damian Rusinek
@date       edited on 07-05-2014 by Katarzyna Mazur
"""

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
        self.selectButton = wx.Button(self, label="Select")
        # 'Configure' button = configure selected module, clicking the button should bring a new window where the configuration of the chosen module will be possible
        self.configureButton = wx.Button(self, label="Configure")
        self.configureButton.Disable()

        # create group boxes, aka static boxes
        modulesSelectionBox = wx.StaticBox(self, label="Select modules")
        modulesConfigurationBox = wx.StaticBox(self, label="Configure modules")
        mainBox = wx.StaticBox(self, label="Modules")

        # create sizers = some kind of layout management
        modulesSelectionBoxSizer = wx.StaticBoxSizer(modulesSelectionBox, wx.HORIZONTAL)
        modulesConfigurationBoxSizer = wx.StaticBoxSizer(modulesConfigurationBox, wx.HORIZONTAL)
        mainBoxSizer = wx.StaticBoxSizer(mainBox, wx.VERTICAL)

        # create labels, aka static texts
        selectModulesLabel = wx.StaticText(self, label="Choose modules for analysis and click the 'Select'\nbutton to add them to the configuration panel.")
        configureModulesLabel = wx.StaticText(self, label="Choose module from selected modules and\nconfigure them one by one.")

        # create combocheckbox, empty at first
        self.comboCheckBox = wx.combo.ComboCtrl(self)
        self.tcp = ComboCheckBox()
        self.comboCheckBox.SetPopupControl(self.tcp)
        self.comboCheckBox.SetText('...')

        # create ordinary combobox for module configuration
        self.modulesConfComboBox = wx.ComboBox(self, style=wx.TE_READONLY)

        # add tooltipz = make user's life easier
        modulesSelectionBox.SetToolTip(wx.ToolTip("Select modules for analysis"))
        modulesConfigurationBox.SetToolTip(wx.ToolTip("Configure chosen modules"))

        # align 'select modules' group box
        modulesSelectionBoxSizer.Add(selectModulesLabel, 1, wx.ALL | wx.EXPAND, 5)
        modulesSelectionBoxSizer.Add(self.comboCheckBox, 1, wx.ALL | wx.EXPAND, 5)
        modulesSelectionBoxSizer.Add(self.selectButton, 0, wx.ALL | wx.EXPAND, 5)

        # align 'configure modules' group box
        modulesConfigurationBoxSizer.Add(configureModulesLabel, 1, wx.ALL | wx.EXPAND, 5)
        modulesConfigurationBoxSizer.Add(self.modulesConfComboBox, 1, wx.ALL | wx.EXPAND, 5)
        modulesConfigurationBoxSizer.Add(self.configureButton, 0, wx.ALL | wx.EXPAND, 5)

        # do some bindings:
        self.selectButton.Bind(wx.EVT_BUTTON, self.OnSelectButtonClicked)
        self.configureButton.Bind(wx.EVT_BUTTON, self.OnConfigureButtonClicked)

        #self.tcp.checkBoxList.Bind(wx.EVT_CHECKLISTBOX, self.OnCheckBoxChange)

        # names of the modules to appeared in the config combobox
        self.modulesNames4Combo = []

        for m in self.allModules:
            gui = m.get_gui()
            self.modulesNames4Combo.append(gui.get_name())

        # fill combocheckbox with modules names
        self.tcp.SetChoices(self.modulesNames4Combo)

        for i in range(0,4) :
            mainSizer.Add(wx.StaticText(self), 0, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(modulesSelectionBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        for i in range(0,3) :
            mainSizer.Add(wx.StaticText(self), 0, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(modulesConfigurationBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        mainBoxSizer.Add(mainSizer, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(mainBoxSizer)

    def OnSelectButtonClicked(self, event):
        """
        @brief grabs selected modules from
        combocheckbox widget, puts them into
        conf combobox
        """

        # add selected modules to config-combo box - u can
        # configure only selected modules, one by one
        self.FillUpComboWithModules(self.tcp.GetSelectedItems())
        # check which module was selected, make a list out of the selected modules
        modules = []
        [modules.append(self.allModules[i]) for i in range(self.tcp.checkBoxList.GetCount()) if self.tcp.checkBoxList.IsChecked(i)]
        # perform event - modules were selected
        wx.PostEvent(self, ModulesChangedEvent(modules=modules, all_modules=self.allModules))

    def OnConfigureButtonClicked(self, event):
        """
        @brief configures chosen module [ideally, do it in
        a new window]
        """
        # print self.modulesConfComboBox.GetStringSelection()
        # get selected module from combo
        selectedModule = self.modulesConfComboBox.GetValue()

        for m in self.allModules :
            if m.get_gui().get_name() == selectedModule :
                # new window (frame, actually) where we open up a
                # panel received from module/name/gui.py[get_configuration_panel]
                confWindow = GeneralFrame(self, "Module Configuration", "Configuration", "config.png")
                panel = m.get_gui().get_configuration_panel(confWindow)
                confWindow.AddPanel(panel)
                confWindow.Show()
                break

    def FillUpComboWithModules(self, modules):
        """
        @brief adds selected modules to the combobox
        """
        # clear combo, do not remember prev choices
        self.modulesConfComboBox.Clear()
        # DO NOT select, selecting can mess up many things
        self.modulesConfComboBox.SetSelection(-1)
        self.modulesConfComboBox.SetValue("")
        # add all chosen modules to the combo
        self.modulesConfComboBox.AppendItems(modules)
        self.modulesConfComboBox.Refresh()
        # enable button if combo is not empty =
        # we can actually configure some modules
        if modules :
            self.configureButton.Enable()
        else:
            self.configureButton.Disable()