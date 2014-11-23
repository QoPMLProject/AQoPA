#!/usr/bin/env python

import wx
import os
from aqopa.gui.general_purpose_frame_gui import GeneralFrame
from sme.SMETool import SMETool

"""
@file       __init__.py
@brief      gui file for the qopanalysis module
@author     Katarzyna Mazur
"""

class SingleVersionPanel(wx.Panel):
    """
    Frame presenting results for one simulation.
    Simulator may be retrived from module,
    because each module has its own simulator.
    """

    def __init__(self, module, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.module = module
        self.versionSimulator = {}
        self.all_facts = []
        self.occured_facts = []

        #################
        # VERSION BOX
        #################

        versionBox = wx.StaticBox(self, label="Version")
        versionsLabel = wx.StaticText(self, label="Choose Version To See\nAnalysis Results:")
        self.versionsList = wx.ComboBox(self, style=wx.TE_READONLY)
        self.versionsList.Bind(wx.EVT_COMBOBOX, self.OnVersionChanged)
        versionBoxSizer = wx.StaticBoxSizer(versionBox, wx.HORIZONTAL)
        versionBoxSizer.Add(versionsLabel, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        versionBoxSizer.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
        versionBoxSizer.Add(self.versionsList, 1, wx.ALL | wx.ALIGN_CENTER, 5)

        ##################################
        # QoP PARAMETERS BOX
        ##################################
        self.qopParamsBox = wx.StaticBox(self, label="The QoP Analysis Results")
        hostsBox, hostsBoxSizer = self._BuildHostsBoxAndSizer()
        qopParamsBoxSizer = wx.StaticBoxSizer(self.qopParamsBox, wx.VERTICAL)
        qopParamsBoxSizer.Add(hostsBoxSizer, 1, wx.ALL | wx.EXPAND, 5)

        #################
        # BUTTONS LAY
        #################
        self.showQoPBtn = wx.Button(self, label="Show")
        self.showQoPBtn.Bind(wx.EVT_BUTTON, self.OnShowQoPBtnClicked)
        #self.launchSMEBtn = wx.Button(self, label="Evaluate")
        #self.launchSMEBtn.Bind(wx.EVT_BUTTON, self.OnLaunchSMEClicked)
        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
        buttonsSizer.Add(self.showQoPBtn, 0, wx.ALL | wx.EXPAND, 5)
        #buttonsSizer.Add(self.launchSMEBtn, 0, wx.ALL | wx.EXPAND, 5)

        #################
        # MAIN LAY
        #################
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(versionBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(qopParamsBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(buttonsSizer, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)

        self.SetVersionsResultsVisibility(False)

    def OnShowQoPBtnClicked(self, event):
        hostName = self.hostsList.GetValue()
        if hostName != "" :
            versionName = self.versionsList.GetValue()
            simulator = self.versionSimulator[versionName]
            host = self._GetSelectedHost(simulator)
            self.ShowQoPParameters(simulator, host)

    def OnLaunchSMEClicked(self, event):
        smetool = SMETool(None)
        smetool.SetClientSize(wx.Size(800,450))
        smetool.CentreOnScreen()
        smetool.Show()

    def _GetSelectedHost(self, simulator):

        host = None

        # get selected module name from combo
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

        self.chooseHostLbl = wx.StaticText(self, label="Choose Host To See\nit's QoP Parameters:")
        self.hostsList = wx.ComboBox(self, style=wx.TE_READONLY)

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
        widgets.append(self.showQoPBtn)
        #widgets.append(self.launchSMEBtn)
        widgets.append(self.qopParamsBox)
        widgets.append(self.chooseHostLbl)

        for w in widgets:
            if visible:
                w.Show()
            else:
                w.Hide()

        self.Layout()

    def ShowQoPParameters(self, simulator, host) :

        title = "QoP Parameters for host: "
        title += host.original_name()

        qopsWindow = GeneralFrame(self, "QoP Analysis Results", title, "modules_results.png")
        qopParamsPanel = wx.Panel(qopsWindow)

        # get all & occured facts
        versionName = self.versionsList.GetValue()
        simulator = self.versionSimulator[versionName]
        # simply copy lists
        self.occured_facts = self._GetoOccuredFacts(simulator)[:]
        self.all_facts = self._GetAllFacts(simulator)[:]

        ##################################
        # ALL FACTS LAYOUT
        ##################################
        all_factsListBox = wx.ListBox(qopParamsPanel, choices=self.all_facts)
        all_factsBox = wx.StaticBox(qopParamsPanel, label="All Facts")
        allFactsBoxSizer = wx.StaticBoxSizer(all_factsBox, wx.VERTICAL)
        allFactsBoxSizer.Add(all_factsListBox, 1, wx.ALL | wx.EXPAND, 5)

        ##################################
        # OCCURED FACTS LAYOUT
        ##################################
        occured_factsListBox = wx.ListBox(qopParamsPanel, choices=self.occured_facts)
        occured_factsBox = wx.StaticBox(qopParamsPanel, label="Occured Facts")
        occuredFactsBoxSizer = wx.StaticBoxSizer(occured_factsBox, wx.VERTICAL)
        occuredFactsBoxSizer.Add(occured_factsListBox, 1, wx.ALL | wx.EXPAND, 5)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(allFactsBoxSizer, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(occuredFactsBoxSizer, 1, wx.ALL | wx.EXPAND, 5)

        qopParamsPanel.SetSizer(sizer)
        qopParamsPanel.Layout()

        qopsWindow.CentreOnScreen()
        qopsWindow.AddPanel(qopParamsPanel)
        qopsWindow.SetWindowSize(600, 300)
        qopsWindow.Show()

        # some kind of debugging
        #print "Occured facts from GUI: "+str(self._GetoOccuredFacts(simulator))
        #print "All facts from GUI: "+str(self._GetAllFacts(simulator))

    def _GetAllFacts(self, simulator):
        return self.module.get_all_facts()

    def _GetoOccuredFacts(self, simulator):
        host = None
        # get all hosts assigned to this simulator
        allHosts = self.module.occured_facts[simulator]
        # get the name of the host selected on hosts combo box
        hostName = self.hostsList.GetValue()
        # from all hosts get the selected one - its the host
        # with the same same selected on combobox
        for h in allHosts :
            if h.original_name() == hostName :
                host = h
                break
        # get all facts for the particular simulator and host
        return self.module.get_occured_facts(simulator, host)

class MainResultsNotebook(wx.Notebook):
    """ """
    def __init__(self, module, *args, **kwargs):
        wx.Notebook.__init__(self, *args, **kwargs)

        self.module = module

        il = wx.ImageList(24, 24)
        singleVersionImg = il.Add(wx.Bitmap(self.CreatePath4Resource('qop.png'), wx.BITMAP_TYPE_PNG))
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
        return "QoP Analysis"

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