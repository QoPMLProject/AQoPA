#!/usr/bin/env python

import wx
from aqopa.gui.combo_check_box import ComboCheckBox

"""
@file       main_notebook_gui.py
@brief      GUI for the main notebook, where we attach our AQoPA tabs
@author     Damian Rusinek
@date       created on 05-09-2013 by Damian Rusinek
@date       edited on 09-05-2014 by Katarzyna Mazur (visual improvements mainly)
"""

class ResultsPanel(wx.Panel):
    """ """
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.selectedModules = []
        self.moduleResultPanel = {}
        #self.buttonsModule = {}

        self._BuildMainLayout()

    def _BuildMainLayout(self):

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.modulesChooserBox = wx.StaticBox(self, label="Modules")
        self.modulesChooserBox.Hide()
        self.modulesChooserBoxSizer = wx.StaticBoxSizer(self.modulesChooserBox, wx.HORIZONTAL)

        #self.modulesBox = wx.StaticBox(self, label="Modules", size=(100, 100))
        #self.modulesBox.Hide()
        #self.modulesBoxSizer = wx.StaticBoxSizer(self.modulesBox, wx.VERTICAL)

        self.resultsBox = wx.StaticBox(self, label="Results")
        self.resultsBox.Hide()
        self.resultsBoxSizer = wx.StaticBoxSizer(self.resultsBox, wx.VERTICAL)

        #mainSizer.Add(self.modulesBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(self.modulesChooserBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.AddSpacer(25)
        mainSizer.Add(self.resultsBoxSizer, 1, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(mainSizer)
        self.Layout()

    def _BuildModulesLayout(self):
        """ """

        # create combobox, empty at first
        self.modulesChooserComboBox = wx.ComboBox(self)
        # bind selection event - if user selects the module,
        # AQoPA will show up some results panels
        self.modulesChooserComboBox.Bind(wx.EVT_COMBOBOX, self.OnModuleSelected)
        # create static text - simple information for the user whatz goin' on with GUI
        modulesInfo = wx.StaticText(self, label="Select module to see the analysis results.")

        # names of the modules to appeared in the config combobox
        self.modulesNames4Combo = []

        for m in self.selectedModules:
            if m in self.moduleResultPanel:
                continue

            gui = m.get_gui()

            # collect the names of all the selected modules
            self.modulesNames4Combo.append(m.get_gui().get_name())

            #btn = wx.Button(self, label=gui.get_name())
            #btn.Bind(wx.EVT_BUTTON, self.OnModuleButtonClicked)
            #self.modulesBoxSizer.Add(btn, 0, wx.ALL | wx.EXPAND)
            #self.buttonsModule[btn] = m

            resultPanel = gui.get_results_panel(self)
            self.resultsBoxSizer.Add(resultPanel, 1, wx.ALL | wx.EXPAND, 5)
            self.moduleResultPanel[m] = resultPanel

            self.Layout()
            resultPanel.Hide()

        # set modules as items of the combobox
        # clear combo, do not remember prev choices
        self.modulesChooserComboBox.Clear()
        # DO NOT select, selecting can mess up many things
        self.modulesChooserComboBox.SetSelection(-1)
        self.modulesChooserComboBox.SetValue("")
        # add all chosen modules to the combo
        self.modulesChooserComboBox.AppendItems(self.modulesNames4Combo)
        self.modulesChooserComboBox.Refresh()

        # add text near the combocheckbox
        self.modulesChooserBoxSizer.Add(modulesInfo, 0, wx.ALL | wx.EXPAND, 5)

        # add some horizontal space - empty label its simple and effective
        self.modulesChooserBoxSizer.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)

        # add combocheck box to the panel that will show up after selecting
        # modules in the modules tab from the main window
        self.modulesChooserBoxSizer.Add(self.modulesChooserComboBox, 1, wx.ALL | wx.EXPAND, 5)

        # get unselected modules, make a list out of them
        uncheckedModules = []
        [uncheckedModules.append(m) for m in self.moduleResultPanel if m not in self.selectedModules]

        buttonsToRemove = []
        for m in uncheckedModules:
            self.moduleResultPanel[m].Destroy()
            del self.moduleResultPanel[m]

            #for btn in self.buttonsModule:
           #     if self.buttonsModule[btn] == m:
           #         buttonsToRemove.append(btn)

            for i in self.modulesNames4Combo :
                if i == m.get_gui().get_name() :
                    print "REMOVE ME PLEASE ;__;"

        #for btn in buttonsToRemove:
        #    btn.Destroy()
        #    del self.buttonsModule[btn]

        self.Layout()

    def SetSelectedModules(self, modules):
        """ """
        self.selectedModules = modules

        if len(self.selectedModules) > 0:
            #self.modulesBox.Show()
            self.resultsBox.Show()
            self.modulesChooserBox.Show()
        else:
            #self.modulesBox.Hide()
            self.resultsBox.Hide()
            self.modulesChooserBox.Hide()

        self._BuildModulesLayout()

    def ClearResults(self):
        """ """
        for m in self.selectedModules:
            gui = m.get_gui()
            gui.on_parsed_model()

    def OnModuleButtonClicked(self, event):
        """ """
        btn = event.EventObject
        #for m in self.moduleResultPanel:
        #    self.moduleResultPanel[m].Hide()
        #m = self.buttonsModule[btn]
        #self.moduleResultPanel[m].Show()
        #self.Layout()

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
        # on combo - thats the module we're looking for - grab it
        for m in self.selectedModules :
            if m.get_gui().get_name() == selectedModule :
                currentModule = m
                break
        # show the above-found module
        self.moduleResultPanel[currentModule].Show()
        self.Layout()