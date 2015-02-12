#!/usr/bin/env python

import wx

"""
@file       main_notebook_gui.py
@brief      GUI for the main notebook, where we attach our AQoPA tabs
@author     Damian Rusinek <damian.rusinek@gmail.com>
@date       created on 05-09-2013 by Damian Rusinek
@date       edited on 09-05-2014 by Katarzyna Mazur (visual improvements mainly)
"""

class ResultsPanel(wx.Panel):
    """ """
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.selectedModules = []
        self.moduleResultPanel = {}

        self._BuildMainLayout()

    def _BuildMainLayout(self):

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.modulesChooserBox = wx.StaticBox(self, label="Modules")
        self.modulesChooserBox.Hide()
        self.modulesChooserBoxSizer = wx.StaticBoxSizer(self.modulesChooserBox, wx.HORIZONTAL)

        # create combobox, empty at first
        self.modulesChooserComboBox = wx.ComboBox(self, style=wx.TE_READONLY)
        # clear combo, do not remember prev choices
        self.modulesChooserComboBox.Clear()
        # DO NOT select, selecting can mess up many things
        self.modulesChooserComboBox.SetSelection(-1)
        self.modulesChooserComboBox.SetValue("")
        self.modulesChooserComboBox.Hide()
        # bind selection event - if user selects the module,
        # AQoPA will show up some results panels
        self.modulesChooserComboBox.Bind(wx.EVT_COMBOBOX, self.OnModuleSelected)

        # create static text - simple information for the user whatz goin' on with GUI
        self.modulesInfo = wx.StaticText(self, label="Select module to see the analysis results.")
        self.modulesInfo.Hide()

        # add text near the combocheckbox
        self.modulesChooserBoxSizer.Add(self.modulesInfo, 0, wx.ALL | wx.EXPAND, 5)
        # add some horizontal space - empty label its simple and effective
        self.modulesChooserBoxSizer.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
        # add combocheck box to the panel that will show up after selecting
        # modules in the modules tab from the main window
        self.modulesChooserBoxSizer.Add(self.modulesChooserComboBox, 1, wx.ALL | wx.EXPAND, 5)

        self.resultsBox = wx.StaticBox(self, label="Results")
        self.resultsBox.Hide()
        self.resultsBoxSizer = wx.StaticBoxSizer(self.resultsBox, wx.VERTICAL)

        mainSizer.Add(self.modulesChooserBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        # add an empty static text - sth like a vertical spacer
        for i in range(0, 2) :
            mainSizer.Add(wx.StaticText(self), 0, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(self.resultsBoxSizer, 1, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(mainSizer)
        self.Layout()

    def _BuildModulesLayout(self):
        """
        @brief builds a main layout
        """

        for m in self.selectedModules:
            if m in self.moduleResultPanel:
                continue

            gui = m.get_gui()

            resultPanel = gui.get_results_panel(self)
            self.resultsBoxSizer.Add(resultPanel, 1, wx.ALL | wx.EXPAND, 5)
            self.moduleResultPanel[m] = resultPanel

            self.Layout()
            resultPanel.Hide()

        # get unselected modules, make a list out of them
        uncheckedModules = []
        [uncheckedModules.append(m) for m in self.moduleResultPanel if m not in self.selectedModules]

        # delete unchecked panels [modules actually]
        for m in uncheckedModules:
            self.moduleResultPanel[m].Destroy()
            del self.moduleResultPanel[m]

        self.Layout()

    def SetSelectedModules(self, modules):
        """ """
        self.selectedModules = modules

        if len(self.selectedModules) > 0:
            self.resultsBox.Show()
            self.modulesChooserBox.Show()
            # DO NOT select, selecting can mess up many things
            # instead, clear combo and its selection
            self.modulesChooserComboBox.Clear()
            self.modulesChooserComboBox.SetSelection(-1)
            self.modulesChooserComboBox.SetValue("...")
            # add selected modules to the combobox
            for m in self.selectedModules:
                self.modulesChooserComboBox.Append(m.get_gui().get_name())
            # refresh combo and show it
            self.modulesChooserComboBox.Refresh()
            self.modulesChooserComboBox.Show()
            self.modulesInfo.Show()
        else:
            self.resultsBox.Hide()
            # clear'n' hide combobox if we do not need
            # to see analysis results (0 modules were selected)
            self.modulesChooserComboBox.Clear()
            self.modulesChooserComboBox.Hide()
            self.modulesChooserBox.Hide()
            self.modulesInfo.Hide()

        self._BuildModulesLayout()

    def ClearResults(self):
        """ """
        for m in self.selectedModules:
            gui = m.get_gui()
            gui.on_parsed_model()

    def OnModuleSelected(self, event):
        """
        @brief  when user selects the module in combobox,
        appropriate result panel shows up, yay!
        """

        # get current selection
        selectedModule = self.modulesChooserComboBox.GetValue()
        # hide all panels
        for m in self.moduleResultPanel:
            self.moduleResultPanel[m].Hide()
        # get the module object from the selected modules list,
        # simply find it by name - if its the same as the selected
        # on combo - that's the module we're looking for - grab it
        for m in self.selectedModules :
            if m.get_gui().get_name() == selectedModule :
                currentModule = m
                break
        # show the above-found module
        self.moduleResultPanel[currentModule].Show()
        self.Layout()