#!/usr/bin/env python

import wx
import os
from aqopa.gui.general_purpose_frame_gui import GeneralFrame

"""
@file       gui.py
@brief      gui file for the greenanalysis module
@author     Katarzyna Mazur
"""


class SingleVersionPanel(wx.Panel):
    def __init__(self, module, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.module = module
        self.versionSimulator = {}

        # ################
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
        # CO2 RESULTS BOX
        ##################################

        self.co2Box = wx.StaticBox(self, label="The Carbon Dioxide Emissions Analysis Results")
        self.co2Label = wx.StaticText(self, label="CO2 produced per   \none kWh [pounds]:")
        self.co2Input = wx.TextCtrl(self, size=(200, -1))
        co2Sizer = wx.BoxSizer(wx.HORIZONTAL)
        co2Sizer.Add(self.co2Label, 0, wx.ALL | wx.EXPAND, 5)
        co2Sizer.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
        co2Sizer.Add(self.co2Input, 1, wx.ALL | wx.EXPAND | wx.ALIGN_RIGHT, 5)
        hostsBox, hostsBoxSizer = self._BuildHostsBoxAndSizer()
        co2BoxSizer = wx.StaticBoxSizer(self.co2Box, wx.VERTICAL)
        co2BoxSizer.Add(co2Sizer, 0, wx.ALL | wx.EXPAND)
        co2BoxSizer.Add(wx.StaticText(self), 0, wx.ALL | wx.EXPAND, 5)
        co2BoxSizer.Add(hostsBoxSizer, 1, wx.ALL | wx.EXPAND)

        #################
        # BUTTONS LAY
        #################
        self.showCo2ResultsBtn = wx.Button(self, label="Show")
        self.showCo2ResultsBtn.Bind(wx.EVT_BUTTON, self.OnShowCo2ResultsBtnClicked)
        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
        buttonsSizer.Add(self.showCo2ResultsBtn, 0, wx.ALL | wx.EXPAND, 5)

        #################
        # MAIN LAY
        #################
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(versionBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(co2BoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(buttonsSizer, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)

        self.SetVersionsResultsVisibility(False)

    def OnShowCo2ResultsBtnClicked(self, event):
        co2Text = self.co2Input.GetValue().strip()
        try:
            co2 = float(co2Text)
        except ValueError:
            wx.MessageBox("'%s' is not valid CO2 amount. Please correct it." % co2Text,
                          'Error', wx.OK | wx.ICON_ERROR)
            return

        versionName = self.versionsList.GetValue()
        simulator = self.versionSimulator[versionName]
        selected_host = self._GetSelectedHost(simulator)
        all_emissions = self.module.calculate_all_emissions(simulator, simulator.context.hosts, co2)

        # get some financial info from module
        minemission, minhost = self.module.get_min_emission(simulator, simulator.context.hosts)
        maxemission, maxhost = self.module.get_max_emission(simulator, simulator.context.hosts)
        total_emission = self.module.get_total_emission(simulator, simulator.context.hosts)
        avg_emission = self.module.get_avg_emission(simulator, simulator.context.hosts)
        curr_emission = all_emissions[selected_host]

        # after all calculations, build the GUI
        title = "Carbon Dioxide Emissions Analysis for Host: "
        title += selected_host.original_name()

        co2Window = GeneralFrame(self, "Carbon Dioxide Emissions Analysis Results", title, "modules_results.png")
        co2Panel = wx.Panel(co2Window)

        # conversion constant used to convert pounds to kgs
        conv_constant = 0.45539237

        # ########################################################################
        # ACTUAL CARBON DIOXIDE EMISSIONS
        #########################################################################
        actualEmissionsBox = wx.StaticBox(co2Panel, label="Actual Carbon Dioxide Emissions of CPU")
        actualEmissionsBoxSizer = wx.StaticBoxSizer(actualEmissionsBox, wx.VERTICAL)
        #########################################################################
        # emission of the selected host
        #########################################################################
        infoLabel = "Emission for Host: "
        hostInfoLabel = wx.StaticText(co2Panel, label=infoLabel)
        co2Label ="%.15f" % curr_emission + " pounds" # + " / " + "%.15f" % float(curr_emission * conv_constant) + " kg"
        hostCO2Label = wx.StaticText(co2Panel, label=co2Label)
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(hostInfoLabel, 0, wx.ALL | wx.EXPAND, 5)
        sizer1.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
        sizer1.Add(hostCO2Label, 0, wx.ALL | wx.EXPAND, 5)
        #########################################################################
        # minimal emission of version (minimal emissions of every host in given version)
        #########################################################################
        infoLabel = "Minimal Version Emission (Host: " + minhost.original_name() + ")"
        hostInfoLabel = wx.StaticText(co2Panel, label=infoLabel)
        co2Label ="%.15f" % minemission + " pounds" # + " / " + "%.15f" % float(minemission * conv_constant) + " kg"
        hostCO2Label = wx.StaticText(co2Panel, label=co2Label)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(hostInfoLabel, 0, wx.ALL | wx.EXPAND, 5)
        sizer2.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
        sizer2.Add(hostCO2Label, 0, wx.ALL | wx.EXPAND, 5)
        #########################################################################
        # maximal emission of version (maximal emissions of every host in given version)
        #########################################################################
        infoLabel = "Maximal Version Emission (Host: " + maxhost.original_name() + ")"
        hostInfoLabel = wx.StaticText(co2Panel, label=infoLabel)
        co2Label ="%.15f" % maxemission + " pounds" # + " / " + "%.15f" % float(maxemission * conv_constant) + " kg"
        hostCO2Label = wx.StaticText(co2Panel, label=co2Label)
        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3.Add(hostInfoLabel, 0, wx.ALL | wx.EXPAND, 5)
        sizer3.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
        sizer3.Add(hostCO2Label, 0, wx.ALL | wx.EXPAND, 5)
        #########################################################################
        # average version emission
        #########################################################################
        infoLabel = "Average Version Emission: "
        hostInfoLabel = wx.StaticText(co2Panel, label=infoLabel)
        co2Label ="%.15f" % avg_emission + " pounds" # + " / " + "%.15f" % float(avg_emission * conv_constant) + " kg"
        hostCO2Label = wx.StaticText(co2Panel, label=co2Label)
        sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer4.Add(hostInfoLabel, 0, wx.ALL | wx.EXPAND, 5)
        sizer4.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
        sizer4.Add(hostCO2Label, 0, wx.ALL | wx.EXPAND, 5)
        #########################################################################
        # total version emission
        #########################################################################
        infoLabel = "Total Version Emission: "
        hostInfoLabel = wx.StaticText(co2Panel, label=infoLabel)
        co2Label ="%.15f" % total_emission + " pounds" # + " / " + "%.15f" % float(total_emission * conv_constant) + " kg"
        hostCO2Label = wx.StaticText(co2Panel, label=co2Label)
        sizer5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer5.Add(hostInfoLabel, 0, wx.ALL | wx.EXPAND, 5)
        sizer5.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
        sizer5.Add(hostCO2Label, 0, wx.ALL | wx.EXPAND, 5)

        actualEmissionsBoxSizer.Add(sizer1, 0, wx.ALL | wx.EXPAND, 5)
        actualEmissionsBoxSizer.Add(sizer2, 0, wx.ALL | wx.EXPAND, 5)
        actualEmissionsBoxSizer.Add(sizer3, 0, wx.ALL | wx.EXPAND, 5)
        actualEmissionsBoxSizer.Add(sizer4, 0, wx.ALL | wx.EXPAND, 5)
        actualEmissionsBoxSizer.Add(sizer5, 0, wx.ALL | wx.EXPAND, 5)

        #########################################################################
        # MAIN LAYOUT
        #########################################################################

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(actualEmissionsBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)

        co2Panel.SetSizer(mainSizer)
        co2Panel.Layout()
        co2Window.CentreOnScreen()
        co2Window.AddPanel(co2Panel)
        co2Window.SetWindowSize(600, 300)
        co2Window.Show()

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

    # ################
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
        widgets.append(self.co2Box)
        widgets.append(self.hostsBox)
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
        singleVersionImg = il.Add(wx.Bitmap(self.CreatePath4Resource('gogreen.png'), wx.BITMAP_TYPE_PNG))
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
        return "Carbon Dioxide Emissions Analysis"

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