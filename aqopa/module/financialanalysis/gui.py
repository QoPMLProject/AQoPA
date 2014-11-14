#!/usr/bin/env python

import wx
import os
from wx.lib.masked import NumCtrl
from aqopa.gui.general_purpose_frame_gui import GeneralFrame

"""
@file       gui.py
@brief      gui file for the financialanalysis module
@author     Katarzyna Mazur
"""


class SingleVersionPanel(wx.Panel):
    def __init__(self, module, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.module = module
        self.versionSimulator = {}
        self.cost = []

        #################
        # VERSION BOX
        #################

        versionBox = wx.StaticBox(self, label="Version")
        versionsLabel = wx.StaticText(self, label="Choose Version To See\nAnalysis Results:")
        self.versionsList = wx.ComboBox(self, style=wx.TE_READONLY, size=(200, -1))
        self.versionsList.Bind(wx.EVT_COMBOBOX, self.OnVersionChanged)
        versionBoxSizer = wx.StaticBoxSizer(versionBox, wx.HORIZONTAL)
        versionBoxSizer.Add(versionsLabel, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        versionBoxSizer.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
        versionBoxSizer.Add(self.versionsList, 1, wx.ALL | wx.ALIGN_CENTER, 5)

        ##################################
        # FINANCIAL RESULTS BOX
        ##################################

        self.cashBox = wx.StaticBox(self, label="The Financial Analysis Results")
        self.cashLabel = wx.StaticText(self, label="Price of one kWh [$]:")
        self.cashInput = wx.TextCtrl(self, size=(200, -1))
        #self.cashInput = wx.lib.masked.NumCtrl(self, fractionWidth = 10, size=(200,-1))
        #self.cashInput.Bind(wx.EVT_CHAR, self.CashInputValidator)
        cashSizer = wx.BoxSizer(wx.HORIZONTAL)
        cashSizer.Add(self.cashLabel, 0, wx.ALL | wx.EXPAND, 5)
        cashSizer.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
        cashSizer.Add(self.cashInput, 1, wx.ALL | wx.EXPAND | wx.ALIGN_RIGHT, 5)
        hostsBox, hostsBoxSizer = self._BuildHostsBoxAndSizer()
        cashBoxSizer = wx.StaticBoxSizer(self.cashBox, wx.VERTICAL)
        cashBoxSizer.Add(cashSizer, 0, wx.ALL | wx.EXPAND)
        cashBoxSizer.Add(wx.StaticText(self), 0, wx.ALL | wx.EXPAND, 5)
        cashBoxSizer.Add(hostsBoxSizer, 1, wx.ALL | wx.EXPAND)

        #################
        # BUTTONS LAY
        #################
        self.showFinanceResultsBtn = wx.Button(self, label="Show")
        self.showFinanceResultsBtn.Bind(wx.EVT_BUTTON, self.OnShowFinanceResultsBtnClicked)
        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
        buttonsSizer.Add(self.showFinanceResultsBtn, 0, wx.ALL | wx.EXPAND, 5)

        #################
        # MAIN LAY
        #################
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(versionBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(cashBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(buttonsSizer, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)

        self.SetVersionsResultsVisibility(False)

    # def CashInputValidator(self, event):
    #     raw_value = self.cashInput.GetValue().strip()
    #     print raw_value
    #     if all(x in '0123456789.+-' for x in raw_value):
    #         self.value = round(float(raw_value), 2)
    #         self.cashInput.ChangeValue(str(self.value))
    #
    #     else:
    #         self.cashInput.ChangeValue("Number only")

    def OnShowFinanceResultsBtnClicked(self, event):
        cashText = self.cashInput.GetValue().strip()
        try:
            cash = float(cashText)
        except ValueError:
            wx.MessageBox("'%s' is not a valid price. Please correct it." % cashText,
                          'Error', wx.OK | wx.ICON_ERROR)
            return

        def convert_to_kWh(joules):
            return joules / 3600000.0

        def find_host_with_min_cost():
            pass

        def find_host_with_max_cost():
            pass

        def find_avg_cost():
            pass

        versionName = self.versionsList.GetValue()
        simulator = self.versionSimulator[versionName]

        cs = self.module.get_all_hosts_consumption(simulator)
        print str(cs[self._GetSelectedHost(simulator)]) + " joules " + str(convert_to_kWh(cs[self._GetSelectedHost(simulator)])) + " kwhs "

    def _GetSelectedHost(self, simulator):

        host = None

        # get selected host name from combo
        hostName = self.hostsList.GetValue()

        # find host with the selected name
        for h in simulator.context.hosts:
            if h.original_name() == hostName:
                host = h
                break

        return host

    def _PopulateComboWithHostsNames(self, simulator):
        hostsNames = []
        [hostsNames.append(h.original_name()) for h in simulator.context.hosts if h.original_name() not in hostsNames]
        self.hostsList.Clear()
        self.hostsList.AppendItems(hostsNames)

    #################
    # LAYOUT
    #################

    def _BuildHostsBoxAndSizer(self):
        """ """

        self.chooseHostLbl = wx.StaticText(self, label="Choose Host To See\nit's Total Cost:")
        self.hostsList = wx.ComboBox(self, style=wx.TE_READONLY, size=(200, -1))

        self.hostsBox = wx.StaticBox(self, label="Host(s)")
        self.hostsBoxSizer = wx.StaticBoxSizer(self.hostsBox, wx.HORIZONTAL)

        self.hostsBoxSizer.Add(self.chooseHostLbl, 0, wx.ALL | wx.EXPAND, 5)
        self.hostsBoxSizer.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
        self.hostsBoxSizer.Add(self.hostsList, 1, wx.ALL | wx.EXPAND | wx.ALIGN_RIGHT, 5)

        return self.hostsBox, self.hostsBoxSizer

    #################
    # REACTIONS
    #################

    def AddFinishedSimulation(self, simulator):
        """ """
        version = simulator.context.version
        self.versionsList.Append(version.name)
        self.versionSimulator[version.name] = simulator

    def OnVersionChanged(self, event):
        """ """
        versionName = self.versionsList.GetValue()
        simulator = self.versionSimulator[versionName]
        self._PopulateComboWithHostsNames(simulator)
        self.SetVersionsResultsVisibility(True)

    def RemoveAllSimulations(self):
        """ """
        self.versionsList.Clear()
        self.versionsList.SetValue("")
        self.versionSimulator = {}
        self.hostsList.Clear()
        self.hostsList.SetValue("")
        self.SetVersionsResultsVisibility(False)

    def SetVersionsResultsVisibility(self, visible):
        """ """
        widgets = []
        widgets.append(self.hostsList)
        widgets.append(self.hostsBox)
        widgets.append(self.cashBox)
        widgets.append(self.showFinanceResultsBtn)
        widgets.append(self.chooseHostLbl)

        for w in widgets:
            if visible:
                w.Show()
            else:
                w.Hide()

        self.Layout()


class MainResultsNotebook(wx.Notebook):
    def __init__(self, module, *args, **kwargs):
        wx.Notebook.__init__(self, *args, **kwargs)

        self.module = module

        il = wx.ImageList(24, 24)
        singleVersionImg = il.Add(wx.Bitmap(self.CreatePath4Resource('cash.png'), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)

        self.oneVersionTab = SingleVersionPanel(self.module, self)
        self.AddPage(self.oneVersionTab, "Single Version")
        self.SetPageImage(0, singleVersionImg)
        self.oneVersionTab.Layout()

    def OnParsedModel(self):
        """ """
        self.oneVersionTab.RemoveAllSimulations()

    def OnSimulationFinished(self, simulator):
        """ """
        self.oneVersionTab.AddFinishedSimulation(simulator)

    def OnAllSimulationsFinished(self, simulators):
        """ """
        pass

    def CreatePath4Resource(self, resourceName):
        """
        @brief      creates and returns path to the
                    given file in the resource
                    ('assets') dir
        @return     path to the resource
        """
        tmp = os.path.split(os.path.dirname(__file__))
        # find last / character in path
        idx = tmp[0].rfind('/')
        # get substring - path for resource
        path = tmp[0][0:idx]
        return os.path.join(path, 'bin', 'assets', resourceName)


class ModuleGui(wx.EvtHandler):
    def __init__(self, module):
        """ """
        wx.EvtHandler.__init__(self)
        self.module = module
        self.mainResultNotebook = None

    def get_gui(self):
        if not getattr(self, '__gui', None):
            setattr(self, '__gui', ModuleGui(self))
        return getattr(self, '__gui', None)

    def get_name(self):
        return "Financial Analysis"

    def install_gui(self, simulator):
        """ Install module for gui simulation """
        self._install(simulator)
        return simulator

    def get_configuration_panel(self, parent):
        """ Returns WX panel with configuration controls. """

        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        text = wx.StaticText(panel, label="Module does not need to be configured.")
        sizer.Add(text, 0, wx.ALL | wx.EXPAND, 5)
        text = wx.StaticText(panel, label="All result options will be available after results are calculated.")
        sizer.Add(text, 0, wx.ALL | wx.EXPAND, 5)
        panel.SetSizer(sizer)
        return panel

        # panel = wx.Panel(parent)
        # # create group boxes, aka static boxes
        # costConfBox = wx.StaticBox(panel, label="Cost Per One Kilowatt-Hour")
        # # create info label
        # moduleInfoLabel = wx.StaticText(panel, label="To obtain meaningful results, you need to select The Time Analysis and The Energy Analysis Modules as well. "
        #                                              "Also, remember to give the price of one kilowatt-hour in US dollars.")
        # cashInfoLabel = wx.StaticText(panel, label="Cost per kWh [$]")
        # # create sizers = some kind of layout management
        # sizer = wx.StaticBoxSizer(costConfBox, wx.VERTICAL)
        # inputCashSizer = wx.BoxSizer(wx.HORIZONTAL)
        # mainSizer = wx.BoxSizer(wx.VERTICAL)
        # # create line edit field
        # cashInputText = wx.TextCtrl(panel)
        # inputCashSizer.Add(cashInfoLabel, 0, wx.ALL | wx.EXPAND, 5)
        # inputCashSizer.Add(cashInputText, 1, wx.ALL | wx.EXPAND, 5)
        # # lay them all out
        # sizer.Add(moduleInfoLabel, 0, wx.ALL | wx.EXPAND, 5)
        # sizer.Add(wx.StaticText(panel), 1, wx.ALL | wx.EXPAND, 5)
        # sizer.Add(inputCashSizer, 1, wx.ALL | wx.EXPAND, 5)
        # mainSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)
        # panel.SetSizer(mainSizer)
        # return panel, cashInputText.GetValue()

    def get_results_panel(self, parent):
        """
        Create main result panel existing from the beginning
        which will be extended when versions' simulations are finished.
        """
        self.mainResultNotebook = MainResultsNotebook(self.module, parent)
        return self.mainResultNotebook

    def on_finished_simulation(self, simulator):
        """ """
        self.mainResultNotebook.OnSimulationFinished(simulator)

    def on_finished_all_simulations(self, simulators):
        """
        Called once for all simulations after all of them are finished.
        """
        self.mainResultNotebook.OnAllSimulationsFinished(simulators)

    def on_parsed_model(self):
        """ """
        self.mainResultNotebook.OnParsedModel()