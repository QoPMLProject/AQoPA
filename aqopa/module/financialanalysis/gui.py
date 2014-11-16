#!/usr/bin/env python

import wx
import os
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

    def OnShowFinanceResultsBtnClicked(self, event):
        cashText = self.cashInput.GetValue().strip()
        try:
            price = float(cashText)
        except ValueError:
            wx.MessageBox("'%s' is not a valid price. Please correct it." % cashText,
                          'Error', wx.OK | wx.ICON_ERROR)
            return

        def convert_to_joules(milijoules) :
            return milijoules / 1000.0

        def convert_to_kWh(joules):
            return joules / 3600000.0

        def calculate_cost(consumed_joules, cost_per_kWh):
            kWhs = convert_to_kWh(consumed_joules)
            cost = kWhs * cost_per_kWh
            return cost

        def calculate_cost_for_host(simulator, host, cost_per_kWh) :
            all_consumptions = self.module.get_all_hosts_consumption(simulator)
            joules = convert_to_joules(all_consumptions[host])
            cost_for_host = calculate_cost(joules, cost_per_kWh)
            return cost_for_host

        def calculate_all_costs(simulator, cost_per_kWh):
            hosts = simulator.context.hosts
            all_costs = {}
            for host in hosts :
                all_costs[host] = calculate_cost_for_host(simulator, host, cost_per_kWh)
            return all_costs

        def get_min_cost(all_costs):
            hosts = simulator.context.hosts
            host = hosts[0]
            min_cost = all_costs[hosts[0]]
            for h in hosts :
                if all_costs[h] < min_cost :
                    min_cost = all_costs[h]
                    host = h
            return host, min_cost

        def get_max_cost(all_costs):
            hosts = simulator.context.hosts
            host = hosts[0]
            max_cost = all_costs[hosts[0]]
            for h in hosts :
                if all_costs[h] > max_cost :
                    max_cost = all_costs[h]
                    host = h
            return host, max_cost

        def get_avg_cost(all_costs):
            hosts = simulator.context.hosts
            sum = 0.0
            i = 0
            for h in hosts :
                sum += all_costs[h]
                i += 1
            return sum / i

        def get_total_cost(all_costs):
            hosts = simulator.context.hosts
            sum = 0.0
            for h in hosts :
                sum += all_costs[h]
            return sum

        versionName = self.versionsList.GetValue()
        simulator = self.versionSimulator[versionName]
        selected_host = self._GetSelectedHost(simulator)
        all_costs = calculate_all_costs(simulator, price)

        minhost, mincost = get_min_cost(all_costs)
        maxhost, maxcost = get_max_cost(all_costs)
        curr_cost = all_costs[selected_host]
        total_cost = get_total_cost(all_costs)
        avg_cost = get_avg_cost(all_costs)

        # populate module with calculated costs
        for host in simulator.context.hosts :
            self.module.add_cost(simulator, host, all_costs[host])

        # some kind of debugging
        print "min cost: " + str(mincost) + " from host: " + minhost.name
        print "max cost: " + str(maxcost) + " from host: " + maxhost.name
        print "cost: " + str(curr_cost) + " from host " + selected_host.name
        print "avg cost: " + str(avg_cost)
        print "total cost: " + str(total_cost)

        print "from module (min): " + str(self.module.get_min_cost(simulator))
        print "from module (max): " + str(self.module.get_max_cost(simulator))

        # after all calculations, build the GUI
        title = "Financial Analysis for Host: "
        title += selected_host.original_name()

        cashWindow = GeneralFrame(self, "Financial Analysis Results", title, "modules_results.png")
        cashPanel = wx.Panel(cashWindow)

        #########################################################################
        # ACTUAL COSTS
        #########################################################################
        actualCostsBox = wx.StaticBox(cashPanel, label="Actual Costs of CPU Power Consumption")
        actualCostsBoxSizer = wx.StaticBoxSizer(actualCostsBox, wx.VERTICAL)
        #########################################################################
        # cost of the selected host
        #########################################################################
        infoLabel = "Cost for Host: "
        hostInfoLabel = wx.StaticText(cashPanel, label=infoLabel)
        costLabel = str(all_costs[selected_host]) + " $"
        hostCostLabel = wx.StaticText(cashPanel, label=costLabel)
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(hostInfoLabel, 0, wx.ALL | wx.EXPAND, 5)
        sizer1.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
        sizer1.Add(hostCostLabel, 0, wx.ALL | wx.EXPAND, 5)
        #########################################################################
        # minimal cost of version (minimal cost of every host in given version)
        #########################################################################
        infoLabel = "Minimal Version Cost (Host: " + minhost.original_name() + ")"
        hostInfoLabel = wx.StaticText(cashPanel, label=infoLabel)
        costLabel = str(mincost) + " $"
        hostCostLabel = wx.StaticText(cashPanel, label=costLabel)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(hostInfoLabel, 0, wx.ALL | wx.EXPAND, 5)
        sizer2.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
        sizer2.Add(hostCostLabel, 0, wx.ALL | wx.EXPAND, 5)
        #########################################################################
        # maximal cost of version (maximal cost of every host in given version)
        #########################################################################
        infoLabel = "Maximal Version Cost (Host: " + maxhost.original_name() + ")"
        hostInfoLabel = wx.StaticText(cashPanel, label=infoLabel)
        costLabel = str(maxcost) + " $"
        hostCostLabel = wx.StaticText(cashPanel, label=costLabel)
        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3.Add(hostInfoLabel, 0, wx.ALL | wx.EXPAND, 5)
        sizer3.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
        sizer3.Add(hostCostLabel, 0, wx.ALL | wx.EXPAND, 5)
        #########################################################################
        # average version cost
        #########################################################################
        infoLabel = "Average Version Cost: "
        hostInfoLabel = wx.StaticText(cashPanel, label=infoLabel)
        costLabel = str(avg_cost) + " $"
        hostCostLabel = wx.StaticText(cashPanel, label=costLabel)
        sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer4.Add(hostInfoLabel, 0, wx.ALL | wx.EXPAND, 5)
        sizer4.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
        sizer4.Add(hostCostLabel, 0, wx.ALL | wx.EXPAND, 5)
        #########################################################################
        # total version cost
        #########################################################################
        infoLabel = "Total Version Cost: "
        hostInfoLabel = wx.StaticText(cashPanel, label=infoLabel)
        costLabel = str(total_cost) + " $"
        hostCostLabel = wx.StaticText(cashPanel, label=costLabel)
        sizer5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer5.Add(hostInfoLabel, 0, wx.ALL | wx.EXPAND, 5)
        sizer5.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
        sizer5.Add(hostCostLabel, 0, wx.ALL | wx.EXPAND, 5)

        actualCostsBoxSizer.Add(sizer1, 0, wx.ALL | wx.EXPAND, 5)
        actualCostsBoxSizer.Add(sizer2, 0, wx.ALL | wx.EXPAND, 5)
        actualCostsBoxSizer.Add(sizer3, 0, wx.ALL | wx.EXPAND, 5)
        actualCostsBoxSizer.Add(sizer4, 0, wx.ALL | wx.EXPAND, 5)
        actualCostsBoxSizer.Add(sizer5, 0, wx.ALL | wx.EXPAND, 5)

        #########################################################################
        # ESTIMATED COSTS
        #########################################################################
        estimatedCostsBox = wx.StaticBox(cashPanel, label="Estimated Costs of CPU Power Consumption (7/24/365)")
        estimatedCostsBoxSizer = wx.StaticBoxSizer(estimatedCostsBox, wx.VERTICAL)

        #########################################################################
        # MAIN LAYOUT
        #########################################################################

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(actualCostsBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(estimatedCostsBoxSizer, 0, wx.ALL | wx.EXPAND, 5)

        cashPanel.SetSizer(mainSizer)
        cashPanel.Layout()
        cashWindow.CentreOnScreen()
        cashWindow.AddPanel(cashPanel)
        cashWindow.SetWindowSize(600, 350)
        cashWindow.Show()

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
        widgets.append(self.cashLabel)
        widgets.append(self.cashBox)
        widgets.append(self.cashInput)
        widgets.append(self.hostsList)
        widgets.append(self.hostsBox)
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