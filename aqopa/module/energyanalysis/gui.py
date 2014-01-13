'''
Created on 06-09-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

import os
import re
import wx
import wx.animate
import wx.lib.scrolledpanel as scrolled
import wx.lib.delayedresult

from aqopa.model import name_indexes
from aqopa.bin import gui as aqopa_gui
from aqopa.simulator.error import RuntimeException

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

        self.hostChoosePanels       = []  # Panels used to choose hosts for energy consumptions results
        self.checkBoxInformations   = []  # Tuples with host name, and index ranges widget
        self.hostCheckBoxes         = []  # List of checkboxes with hosts names used for hosts' selection

        self.consumptionResultsPanel       = None

        #################
        # VERSION BOX
        #################
        
        versionBox = wx.StaticBox(self, label="Version")
        self.versionsList = wx.ComboBox(self, style=wx.TE_READONLY)
        self.versionsList.Bind(wx.EVT_COMBOBOX, self.OnVersionChanged)
        
        versionBoxSizer = wx.StaticBoxSizer(versionBox, wx.VERTICAL)
        versionBoxSizer.Add(self.versionsList, 1, wx.ALL | wx.ALIGN_CENTER, 5)

        ##################################
        # ENERGY CONSUMPTION BOX
        ##################################
        
        self.consumptionsBox = wx.StaticBox(self, label="Energy consumption results")

        self.voltageLabel = wx.StaticText(self, label="Enther the Voltage value:")
        self.voltageInput = wx.TextCtrl(self)
        
        voltageHBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        voltageHBoxSizer.Add(self.voltageLabel, 0, wx.ALL | wx.EXPAND, 10)
        voltageHBoxSizer.Add(self.voltageInput, 0, wx.ALL | wx.EXPAND, 10)
        
        operationBox, operationBoxSizer = self._BuildOperationsBoxAndSizer()
        hostsBox, hostsBoxSizer = self._BuildHostsBoxAndSizer()

        consumptionsBoxSizer = wx.StaticBoxSizer(self.consumptionsBox, wx.VERTICAL)
        consumptionsHBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        consumptionsHBoxSizer.Add(operationBoxSizer, 0, wx.ALL | wx.EXPAND)
        consumptionsHBoxSizer.Add(hostsBoxSizer, 1, wx.ALL | wx.EXPAND)
        
        self.showConsumptionBtn = wx.Button(self, label="Show energy conspumption")
        self.showConsumptionBtn.Bind(wx.EVT_BUTTON, self.OnShowConsumptionButtonClicked)
        
        self.consumptionsResultBox = wx.StaticBox(self, label="Results")
        self.consumptionsResultBoxSizer = wx.StaticBoxSizer(self.consumptionsResultBox, wx.VERTICAL)
        
        consumptionsBoxSizer.Add(voltageHBoxSizer, 0, wx.ALL | wx.EXPAND)
        consumptionsBoxSizer.Add(consumptionsHBoxSizer, 0, wx.ALL | wx.EXPAND)
        consumptionsBoxSizer.Add(self.showConsumptionBtn, 0, wx.ALL | wx.EXPAND)
        consumptionsBoxSizer.Add(self.consumptionsResultBoxSizer, 1, wx.ALL | wx.EXPAND)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(versionBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(consumptionsBoxSizer, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)
        
        self.SetVersionsResultsVisibility(False)
        
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
        
        self._BuildHostsChoosePanel(simulator)
        self.SetVersionsResultsVisibility(True)
        
    def OnShowConsumptionButtonClicked(self, event):
        """ """
        versionName = self.versionsList.GetValue()
        simulator = self.versionSimulator[versionName]
        hosts = self._GetSelectedHosts(simulator)
        
        if len(hosts) == 0:
            wx.MessageBox("Please select hosts.", 'Error', wx.OK | wx.ICON_ERROR)
            return
        
        voltageText = self.voltageInput.GetValue().strip()
        try:
            voltage = float(voltageText)
        except ValueError:
            wx.MessageBox("Voltage '%s' is incorrect float number. Please correct it." % voltageText, 
                          'Error', wx.OK | wx.ICON_ERROR)
            return
        
        if self.oneECRB.GetValue():
            self.ShowHostsConsumption(simulator, hosts, voltage)
        elif self.avgECRB.GetValue():
            self.ShowAverageHostsConsumption(simulator, hosts, voltage)
        elif self.minECRB.GetValue():
            self.ShowMinimalHostsConsumption(simulator, hosts, voltage)
        elif self.maxECRB.GetValue():
            self.ShowMaximalHostsConsumption(simulator, hosts, voltage)
            
    def RemoveAllSimulations(self):
        """ """
        self.versionsList.Clear()
        self.versionsList.SetValue("")
        self.versionSimulator = {}

        self.hostChoosePanels = []
        self.checkBoxInformations = {}
        self.hostCheckBoxes = []
        self.hostsBoxSizer.Clear(True)

        self.SetVersionsResultsVisibility(False)

    #################
    # LAYOUT
    #################
    
    def _BuildOperationsBoxAndSizer(self):
        """ """
        self.operationBox = wx.StaticBox(self, label="Operation")
        
        self.oneECRB = wx.RadioButton(self, label="Energy consumption of one host")
        self.avgECRB = wx.RadioButton(self, label="Average hosts' energy consumption")
        self.minECRB = wx.RadioButton(self, label="Minimal hosts' energy consumption")
        self.maxECRB = wx.RadioButton(self, label="Maximal hosts' energy consumption")
        
        operationBoxSizer = wx.StaticBoxSizer(self.operationBox, wx.VERTICAL)
        operationBoxSizer.Add(self.oneECRB, 0, wx.ALL)
        operationBoxSizer.Add(self.avgECRB, 0, wx.ALL)
        operationBoxSizer.Add(self.minECRB, 0, wx.ALL)
        operationBoxSizer.Add(self.maxECRB, 0, wx.ALL)
        
        return self.operationBox, operationBoxSizer
    
    def _BuildHostsBoxAndSizer(self):
        """ """
        self.hostsBox = wx.StaticBox(self, label="Host(s)")
        self.hostsBoxSizer = wx.StaticBoxSizer(self.hostsBox, wx.VERTICAL)
        return self.hostsBox, self.hostsBoxSizer
    
    def _BuildHostsChoosePanel(self, simulator):
        """ """
        for p in self.hostChoosePanels:
            p.Destroy()
        self.hostChoosePanels = []
        self.checkBoxInformations = {}
        self.hostCheckBoxes = []
        
        self.hostsBoxSizer.Layout()
        
        hosts = simulator.context.hosts
        hostsIndexes = {} 
        for h in hosts:
            name = h.original_name()
            indexes = name_indexes(h.name)
            index = indexes[0]
            
            if name not in hostsIndexes or index > hostsIndexes[name]:
                hostsIndexes[name] = index
                
        for hostName in hostsIndexes:
            
            panel = wx.Panel(self)
            panelSizer = wx.BoxSizer(wx.HORIZONTAL)
            
            ch = wx.CheckBox(panel, label=hostName, size=(120, 20))
            textCtrl = wx.TextCtrl(panel)
            textCtrl.SetValue("0")
            
            rangeLabel = "Available range: 0"
            if hostsIndexes[hostName] > 0:
                rangeLabel += " - %d" % hostsIndexes[hostName] 
            maxLbl = wx.StaticText(panel, label=rangeLabel)
            
            panelSizer.Add(ch, 0, wx.ALL | wx.ALIGN_CENTER)
            panelSizer.Add(textCtrl, 0, wx.ALL | wx.ALIGN_CENTER)
            panelSizer.Add(maxLbl, 0, wx.ALL | wx.ALIGN_CENTER)
            panel.SetSizer(panelSizer)
            self.hostsBoxSizer.Add(panel, 1, wx.ALL)
            
            self.checkBoxInformations[ch] = (hostName, textCtrl)
            self.hostChoosePanels.append(panel)
            self.hostCheckBoxes.append(ch)
            
        self.hostsBoxSizer.Layout()
        self.Layout()

    def SetVersionsResultsVisibility(self, visible):
        """ """
        widgets = []
        widgets.append(self.consumptionsBox)
        widgets.append(self.operationBox)
        widgets.append(self.oneECRB)
        widgets.append(self.avgECRB)
        widgets.append(self.minECRB)
        widgets.append(self.maxECRB)
        widgets.append(self.hostsBox)
        widgets.append(self.showConsumptionBtn)
        widgets.append(self.consumptionsResultBox)
        widgets.append(self.voltageLabel)
        widgets.append(self.voltageInput)
        
        for w in widgets:
            if visible:
                w.Show()
            else:
                w.Hide()
                
        self.Layout()
    
    #################
    # STATISTICS
    #################
        
    def _GetSelectedHosts(self, simulator):
        """ Returns list of hosts selected by user """
        
        def ValidateHostsRange(indexesRange):
            """ """
            return re.match(r'\d(-\d)?(,\d(-\d)?)*', indexesRange)
        
        def GetIndexesFromRange(indexesRange):
            """ Extracts numbers list of hosts from range text """
            indexes = []
            ranges = indexesRange.split(',')
            for r in ranges:
                parts = r.split('-')
                if len(parts) == 1:
                    indexes.append(int(parts[0]))
                else:
                    for i in range(int(parts[0]), int(parts[1])+1):
                        indexes.append(i)
            return indexes
        
        hosts = []
        for ch in self.hostCheckBoxes:
            if not ch.IsChecked():
                continue
            hostName, hostRangeTextCtrl = self.checkBoxInformations[ch]
            indexesRange = hostRangeTextCtrl.GetValue()
            if not ValidateHostsRange(indexesRange):
                wx.MessageBox("Range '%s' for host '%s' is invalid. Valid example: 0,12,20-25,30." 
                              % (indexesRange, hostName), 'Error', wx.OK | wx.ICON_ERROR)
                break
            else:
                indexes = GetIndexesFromRange(indexesRange)
                for h in simulator.context.hosts:
                    hostIndexes = name_indexes(h.name)
                    if h.original_name() == hostName and hostIndexes[0] in indexes:
                        hosts.append(h)
        return hosts
        
    
    def ShowHostsConsumption(self, simulator, hosts, voltage):
        """ """
        if self.consumptionResultsPanel:
            self.consumptionResultsPanel.Destroy()
            self.consumptionResultsPanel = None
            
        self.consumptionResultsPanel = scrolled.ScrolledPanel(self)
        self.consumptionsResultBoxSizer.Add(self.consumptionResultsPanel, 1, wx.ALL | wx.EXPAND, 5)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        consumptions = self.module.get_hosts_consumptions(simulator, hosts, voltage)
        
        for h in hosts:
            lblText = "%s: %.2f mJ" % (h.name, consumptions[h])
            error = h.get_finish_error()
            if error is not None:
                lblText += " (Not Finished - %s)" % error
            lbl = wx.StaticText(self.consumptionResultsPanel, label=lblText)
            sizer.Add(lbl)
        
        self.consumptionResultsPanel.SetSizer(sizer)
        self.consumptionResultsPanel.SetupScrolling(scroll_x=False)
        self.Layout()
    
    def ShowAverageHostsConsumption(self, simulator, hosts, voltage):
        """ """
        def GetVal(consumptions, hosts):
            sum = 0.0
            n = len(hosts)
            for h in hosts:
                sum += consumptions[h]
            return sum / float(n)
        
        if self.consumptionResultsPanel:
            self.consumptionResultsPanel.Destroy()
            
        self.consumptionResultsPanel = scrolled.ScrolledPanel(self)
        self.consumptionsResultBoxSizer.Add(self.consumptionResultsPanel, 1, wx.ALL | wx.EXPAND, 5)
    
        val = GetVal(self.module.get_hosts_consumptions(simulator, hosts, voltage), hosts)
        lblText = "Average: %.2f mJ" % val
        lbl = wx.StaticText(self.consumptionResultsPanel, label=lblText)        
    
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(lbl)
        
        self.consumptionResultsPanel.SetSizer(sizer)
        self.Layout()
        
    def ShowMinimalHostsConsumption(self, simulator, hosts, voltage):
        """ """
        def GetVal(consumptions, hosts):
            val = None 
            for h in hosts:
                v = consumptions[h]
                if val is None or v < val:
                    val = v
            return val
        
        if self.consumptionResultsPanel:
            self.consumptionResultsPanel.Destroy()
            
        self.consumptionResultsPanel = scrolled.ScrolledPanel(self)
        self.consumptionsResultBoxSizer.Add(self.consumptionResultsPanel, 1, wx.ALL | wx.EXPAND, 5)
    
        val = GetVal(self.module.get_hosts_consumptions(simulator, hosts, voltage), hosts)
        lblText = "Minimum: %.2f mJ" % val
        lbl = wx.StaticText(self.consumptionResultsPanel, label=lblText)        
    
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(lbl)
        
        self.consumptionResultsPanel.SetSizer(sizer)
        self.Layout()
    
    def ShowMaximalHostsConsumption(self, simulator, hosts, voltage):
        """ """
        def GetVal(consumptions, hosts):
            val = 0.0 
            for h in hosts:
                v = consumptions[h]
                if v > val:
                    val = v
            return val
        
        if self.consumptionResultsPanel:
            self.consumptionResultsPanel.Destroy()
            
        self.consumptionResultsPanel = scrolled.ScrolledPanel(self)
        self.consumptionsResultBoxSizer.Add(self.consumptionResultsPanel, 1, wx.ALL | wx.EXPAND, 5)
    
        val = GetVal(self.module.get_hosts_consumptions(simulator, hosts, voltage), hosts)
        lblText = "Maximum: %.2f mJ" % val
        lbl = wx.StaticText(self.consumptionResultsPanel, label=lblText)     
    
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(lbl)
        
        self.consumptionResultsPanel.SetSizer(sizer)
        self.Layout()
        
        
class MainResultsNotebook(wx.Notebook):
    """ """
    def __init__(self, module, *args, **kwargs):
        wx.Notebook.__init__(self, *args, **kwargs)
        
        self.module = module
        
        self.oneVersionTab = SingleVersionPanel(self.module, self)
        self.AddPage(self.oneVersionTab, "Single Version")
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
        
class ModuleGui(wx.EvtHandler):
    """
    Class used by GUI version of AQoPA.
    """
    
    def __init__(self, module):
        """ """
        wx.EvtHandler.__init__(self)
        
        self.module = module
        self.mainResultNotebook = None
        
    def get_name(self):
        return "Energy Analysis"
    
    def get_configuration_panel(self, parent):
        """ Returns WX panel with configuration controls. """
        
        panel = wx.Panel(parent)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        text = wx.StaticText(panel, label="Module does not need to be configured.") 
        sizer.Add(text, 0, wx.ALL | wx.EXPAND, 5)
        text = wx.StaticText(panel, label="All result options will be available after results are calculated.") 
        sizer.Add(text, 0, wx.ALL | wx.EXPAND, 5)
        text = wx.StaticText(panel, label="Module requires Time Analysis module.") 
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
        
        

        
        
        
        
