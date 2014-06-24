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
        self.buttonsModule = {}

        self._BuildMainLayout()

    def _BuildMainLayout(self):

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.modulesChooserBox = wx.StaticBox(self, label="TEMP LABEL")
        self.modulesChooserBox.Hide()
        self.modulesChooserBoxSizer = wx.StaticBoxSizer(self.modulesChooserBox, wx.HORIZONTAL)

        self.modulesBox = wx.StaticBox(self, label="Modules", size=(100, 100))
        self.modulesBox.Hide()
        self.modulesBoxSizer = wx.StaticBoxSizer(self.modulesBox, wx.VERTICAL)

        self.resultsBox = wx.StaticBox(self, label="Results", size=(100, 100))
        self.resultsBox.Hide()
        self.resultsBoxSizer = wx.StaticBoxSizer(self.resultsBox, wx.VERTICAL)


        mainSizer.Add(self.modulesBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(self.resultsBoxSizer, 1, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(self.modulesChooserBoxSizer, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(mainSizer)
        self.Layout()

    def _BuildModulesLayout(self):
        """ """

        # create combocheckbox, empty at first
        self.comboCheckBox = wx.combo.ComboCtrl(self)
        self.tcp = ComboCheckBox()
        self.comboCheckBox.SetPopupControl(self.tcp)
        self.comboCheckBox.SetText('...')
        # create static text - simple information for the user whatz goin' on with GUI
        modulesInfo = wx.StaticText(self, label="Select module to see the analysis results.")

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


        # add text near the combocheckbox
        self.modulesChooserBoxSizer.Add(modulesInfo, 0, wx.ALL | wx.EXPAND, 5)

        # add some horizontal space - empty label its simple and effective
        self.modulesChooserBoxSizer.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)

        # add combocheck box to the panel that will show up after selecting
        # modules in the modules tab from the main window
        self.modulesChooserBoxSizer.Add(self.comboCheckBox, 0, wx.ALL | wx.EXPAND, 5)


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
            self.modulesChooserBox.Show()
        else:
            self.modulesBox.Hide()
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
        for m in self.moduleResultPanel:
            self.moduleResultPanel[m].Hide()
        m = self.buttonsModule[btn]
        self.moduleResultPanel[m].Show()
        self.Layout()