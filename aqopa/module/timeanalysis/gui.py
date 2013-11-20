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

        self.hostChoosePanels       = []  # Panels used to choose hosts for times results
        self.checkBoxInformations   = []  # Tuples with host name, and index ranges widget
        self.hostCheckBoxes         = []  # List of checkboxes with hosts names used for hosts' selection

        self.timeResultsPanel       = None

        #################
        # VERSION BOX
        #################
        
        versionBox = wx.StaticBox(self, label="Version")
        self.versionsList = wx.ComboBox(self, style=wx.TE_READONLY)
        self.versionsList.Bind(wx.EVT_COMBOBOX, self.OnVersionChanged)
        
        versionBoxSizer = wx.StaticBoxSizer(versionBox, wx.VERTICAL)
        versionBoxSizer.Add(self.versionsList, 1, wx.ALL | wx.ALIGN_CENTER, 5)

        #################
        # TOTAL TIME BOX
        #################
        
        self.totalTimeBox = wx.StaticBox(self, label="Total time")
        self.totalTimeLabel = wx.StaticText(self, label="---")
        
        totalTimeBoxSizer = wx.StaticBoxSizer(self.totalTimeBox, wx.VERTICAL)
        totalTimeBoxSizer.Add(self.totalTimeLabel, 1, wx.ALL | wx.ALIGN_CENTER, 5)
        
        #################
        # TIMES BOX
        #################
        
        self.timesBox = wx.StaticBox(self, label="Times")

        operationBox, operationBoxSizer = self._BuildOperationsBoxAndSizer()
        hostsBox, hostsBoxSizer = self._BuildHostsBoxAndSizer()

        timesBoxSizer = wx.StaticBoxSizer(self.timesBox, wx.VERTICAL)
        
        timesHBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        timesHBoxSizer.Add(operationBoxSizer, 0, wx.ALL | wx.EXPAND)
        timesHBoxSizer.Add(hostsBoxSizer, 1, wx.ALL | wx.EXPAND)
        
        self.showTimeBtn = wx.Button(self, label="Show time")
        self.showTimeBtn.Bind(wx.EVT_BUTTON, self.OnShowTimeButtonClicked)
        
        self.timesResultBox = wx.StaticBox(self, label="Results")
        self.timesResultBoxSizer = wx.StaticBoxSizer(self.timesResultBox, wx.VERTICAL)
        
        timesBoxSizer.Add(timesHBoxSizer, 0, wx.ALL | wx.EXPAND)
        timesBoxSizer.Add(self.showTimeBtn, 0, wx.ALL | wx.EXPAND)
        timesBoxSizer.Add(self.timesResultBoxSizer, 1, wx.ALL | wx.EXPAND)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(versionBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(totalTimeBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(timesBoxSizer, 1, wx.ALL | wx.EXPAND, 5)
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
        
        totalTime = self.GetTotalTime(simulator)
        self.totalTimeLabel.SetLabel("%.2f ms" % totalTime)
        
        self._BuildHostsChoosePanel(simulator)
        
        self.SetVersionsResultsVisibility(True)
        
    def OnShowTimeButtonClicked(self, event):
        """ """
        versionName = self.versionsList.GetValue()
        simulator = self.versionSimulator[versionName]
        hosts = self._GetSelectedHosts(simulator)
        if self.oneTimeRB.GetValue():
            self.ShowHostsTimes(simulator, hosts)
        elif self.avgTimeRB.GetValue():
            self.ShowAverageHostsTime(simulator, hosts)
        elif self.minTimeRB.GetValue():
            self.ShowMinimalHostsTime(simulator, hosts)
        elif self.maxTimeRB.GetValue():
            self.ShowMaximalHostsTime(simulator, hosts)
            
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
        
        self.oneTimeRB = wx.RadioButton(self, label="Total host's time")
        self.avgTimeRB = wx.RadioButton(self, label="Average hosts' time")
        self.minTimeRB = wx.RadioButton(self, label="Minimal hosts' time")
        self.maxTimeRB = wx.RadioButton(self, label="Maximal hosts' time")
        
        operationBoxSizer = wx.StaticBoxSizer(self.operationBox, wx.VERTICAL)
        operationBoxSizer.Add(self.oneTimeRB, 0, wx.ALL)
        operationBoxSizer.Add(self.avgTimeRB, 0, wx.ALL)
        operationBoxSizer.Add(self.minTimeRB, 0, wx.ALL)
        operationBoxSizer.Add(self.maxTimeRB, 0, wx.ALL)
        
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
        widgets.append(self.timesBox)
        widgets.append(self.totalTimeBox)
        widgets.append(self.totalTimeLabel)
        widgets.append(self.operationBox)
        widgets.append(self.oneTimeRB)
        widgets.append(self.avgTimeRB)
        widgets.append(self.minTimeRB)
        widgets.append(self.maxTimeRB)
        widgets.append(self.hostsBox)
        widgets.append(self.showTimeBtn)
        widgets.append(self.timesResultBox)
        
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
        
    def GetTotalTime(self, simulator):
        """ Return total time of simulated version. """
        totalTime = 0
        hosts = simulator.context.hosts
        for h in hosts:
            t = self.module.get_current_time(simulator, h)
            if t > totalTime:
                totalTime = t
        return totalTime 
    
    def ShowHostsTimes(self, simulator, hosts):
        """ """
        if self.timeResultsPanel:
            self.timeResultsPanel.Destroy()
            self.timeResultsPanel = None
            
        self.timeResultsPanel = scrolled.ScrolledPanel(self)
        self.timesResultBoxSizer.Add(self.timeResultsPanel, 1, wx.ALL | wx.EXPAND, 5)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        if len(hosts) == 0:
            lbl = wx.StaticText(self.timeResultsPanel, label="No hosts selected")
            sizer.Add(lbl)     
        else:
            for h in hosts:
                
                lblText = "%s: %.2f ms" % (h.name,self.module.get_current_time(simulator, h))
                
                error = h.get_finish_error()
                if error is not None:
                    lblText += " (Not Finished - %s)" % error
                
                lbl = wx.StaticText(self.timeResultsPanel, label=lblText)
                sizer.Add(lbl)
        
        self.timeResultsPanel.SetSizer(sizer)
        self.timeResultsPanel.SetupScrolling(scroll_x=False)
        self.Layout()
    
    def ShowAverageHostsTime(self, simulator, hosts):
        """ """
        def GetVal(simulator, hosts):
            sum = 0.0
            n = len(hosts)
            for h in hosts:
                sum += self.module.get_current_time(simulator, h)
            return sum / float(n)
        
        if self.timeResultsPanel:
            self.timeResultsPanel.Destroy()
            
        self.timeResultsPanel = scrolled.ScrolledPanel(self)
        self.timesResultBoxSizer.Add(self.timeResultsPanel, 1, wx.ALL | wx.EXPAND, 5)
    
        lblText = ""
        if len(hosts) == 0:
            lblText = "---"
        else:
            avg = GetVal(simulator, hosts)
            lblText = "Average: %.2f ms" % avg
        lbl = wx.StaticText(self.timeResultsPanel, label=lblText)        
    
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(lbl)
        
        self.timeResultsPanel.SetSizer(sizer)
        self.Layout()
        
    def ShowMinimalHostsTime(self, simulator, hosts):
        """ """
        def GetVal(simulator, hosts):
            val = None 
            for h in hosts:
                t = self.module.get_current_time(simulator, h)
                if val is None or t < val:
                    val = t
            return val
        
        if self.timeResultsPanel:
            self.timeResultsPanel.Destroy()
            
        self.timeResultsPanel = scrolled.ScrolledPanel(self)
        self.timesResultBoxSizer.Add(self.timeResultsPanel, 1, wx.ALL | wx.EXPAND, 5)
    
        lblText = ""
        if len(hosts) == 0:
            lblText = "---"
        else:
            val = GetVal(simulator, hosts)
            lblText = "Minimum: %.2f ms" % val
        lbl = wx.StaticText(self.timeResultsPanel, label=lblText)        
    
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(lbl)
        
        self.timeResultsPanel.SetSizer(sizer)
        self.Layout()
    
    def ShowMaximalHostsTime(self, simulator, hosts):
        """ """
        def GetVal(simulator, hosts):
            val = 0.0 
            for h in hosts:
                t = self.module.get_current_time(simulator, h)
                if t > val:
                    val = t
            return val
        
        if self.timeResultsPanel:
            self.timeResultsPanel.Destroy()
            
        self.timeResultsPanel = scrolled.ScrolledPanel(self)
        self.timesResultBoxSizer.Add(self.timeResultsPanel, 1, wx.ALL | wx.EXPAND, 5)
    
        lblText = ""
        if len(hosts) == 0:
            lblText = "---"
        else:
            val = GetVal(simulator, hosts)
            lblText = "Maximum: %.2f ms" % val
        lbl = wx.StaticText(self.timeResultsPanel, label=lblText)     
    
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(lbl)
        
        self.timeResultsPanel.SetSizer(sizer)
        self.Layout()
        
#TIME_TYPE_MAX   = 1
#TIME_TYPE_AVG   = 2
#TIME_TYPE_TOTAL = 3
#        
#class VersionsChartsPanel(wx.Panel):
#    
#    def __init__(self, module, *args, **kwargs):
#        wx.Panel.__init__(self, *args, **kwargs)
#
#        self.module = module
#
#        self.simulators = []
#        self.chartPanel = None
#        
#        sizer = wx.BoxSizer(wx.VERTICAL)
#        
#        self.chartTypeBox = wx.StaticBox(self, label="Chart Type")
#        self.chartTypeBoxSizer = wx.StaticBoxSizer(self.chartTypeBox, wx.HORIZONTAL)
#        
#        self.totalTimeOnRepetitionBtn = wx.Button(self, label="T_Total / N")
#        self.avgTimeOnRepetitionBtn = wx.Button(self, label="T_AVG / N")
#        self.totalTimeOnVersionsBtn = wx.Button(self, label="T_Total / Version")
#        self.totalTimeOnMetricsBtn = wx.Button(self, label="T_Total / M")
#        self.avgTimeOnMetricsBtn = wx.Button(self, label="T_AVG / M")
#        
#        self.totalTimeOnRepetitionBtn.Bind(wx.EVT_BUTTON, self.OnTimeTotalOnRepetitionBtnClicked)
#        self.avgTimeOnRepetitionBtn.Bind(wx.EVT_BUTTON, self.OnTimeAvgOnRepetitionBtnClicked)
#        self.totalTimeOnVersionsBtn.Bind(wx.EVT_BUTTON, self.OnTimeTotalOnVersionsBtnClicked)
#        self.totalTimeOnMetricsBtn.Bind(wx.EVT_BUTTON, self.OnTimeTotalOnMetricsBtnClicked)
#        self.avgTimeOnMetricsBtn.Bind(wx.EVT_BUTTON, self.OnTimeAvgOnMetricsBtnClicked)
#        
#        self.chartTypeBoxSizer.Add(self.totalTimeOnRepetitionBtn, 1, wx.ALL | wx.ALIGN_CENTER, 5)
#        self.chartTypeBoxSizer.Add(self.avgTimeOnRepetitionBtn, 1, wx.ALL | wx.ALIGN_CENTER, 5)
#        self.chartTypeBoxSizer.Add(self.totalTimeOnVersionsBtn, 1, wx.ALL | wx.ALIGN_CENTER, 5)
#        self.chartTypeBoxSizer.Add(self.totalTimeOnMetricsBtn, 1, wx.ALL | wx.ALIGN_CENTER, 5)
#        self.chartTypeBoxSizer.Add(self.avgTimeOnMetricsBtn, 1, wx.ALL | wx.ALIGN_CENTER, 5)
#        
#        sizer.Add(self.chartTypeBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
#        
#        
#        self.chartConfigBox = wx.StaticBox(self, label="Chart Configuration")
#        self.chartConfigBoxSizer = wx.StaticBoxSizer(self.chartConfigBox, wx.VERTICAL)
#        
#        sizer.Add(self.chartConfigBoxSizer, 1, wx.ALL | wx.EXPAND, 5)
#        
#        self.SetSizer(sizer)
#        
#    def _GetHostsRepetitions(self):
#        hostsRepetitions = {}
#        
#        for s in self.simulators:
#            for rh in s.context.version.run_hosts:
#                if rh.host_name not in hostsRepetitions:
#                    hostsRepetitions[rh.host_name] = 1
#                if rh.repetitions > hostsRepetitions[rh.host_name]:
#                    hostsRepetitions[rh.host_name] = rh.repetitions
#        
#        return hostsRepetitions
#    
#    def _GetHosts(self, simulators, hostName):
#        simulatorsHosts = {}
#        for s in simulators:
#            simulatorsHosts[s] = []
#            for h in s.context.hosts:
#                if h.original_name() == hostName:
#                    simulatorsHosts[s].append(h)
#        return simulatorsHosts
#    
#    def _MetricExistsIn(self, metric, metrics):
#        """ """
#        for m in metrics:
#            if self._AreMetricsEqual(m, metric):
#                return True
#        return False
#    
#    def _AreMetricsEqual(self, leftMetric, rightMetric):
#        """ """
#        if len(leftMetric) != len(rightMetric):
#            return False
#        
#        for leftMetricsSet in leftMetric:
#            found = False
#            for rightMetricsSet in rightMetric:
#                if leftMetricsSet.host_name == rightMetricsSet.host_name:
#                    found= True
#                    if leftMetricsSet.configuration_name != rightMetricsSet.configuration_name:
#                        return False
#            if not found:
#                return False
#        return True
#    
#    def _GetMetric(self, simulator):
#        """ """
#        return simulator.context.version.metrics_sets
#    
#    def _GetMetrics(self):
#        """ """
#        metrics = []
#        for s in self.simulators:
#            metric = self._GetMetric(s)
#            if not self._MetricExistsIn(metric, metrics):
#                metrics.append(metric)
#        return metrics
#        
#    #################
#    # REACTIONS
#    #################
#    
#    def OnTimeTotalOnRepetitionBtnClicked(self, event):
#        self.chartConfigBox.SetLabel("T_Total/N Chart Configuration")
#        self.BuildTimesByRepetitionsChartPanel(TIME_TYPE_MAX)
#    
#    def OnTimeAvgOnRepetitionBtnClicked(self, event):
#        self.chartConfigBox.SetLabel("TAvg/N Chart Configuration")
#        self.BuildTimesByRepetitionsChartPanel(TIME_TYPE_AVG)
#    
#    def OnTimeTotalOnVersionsBtnClicked(self, event):
#        self.chartConfigBox.SetLabel("TTotal/Version Chart Configuration")
#        self.BuildTimesByVersionsChartPanel(TIME_TYPE_TOTAL)
#    
#    def OnTimeTotalOnMetricsBtnClicked(self, event):
#        self.chartConfigBox.SetLabel("T_Total/M Chart Configuration")
#        self.BuildTimesByMetricsChartPanel(TIME_TYPE_MAX)
#    
#    def OnTimeAvgOnMetricsBtnClicked(self, event):
#        self.chartConfigBox.SetLabel("TAvg/M Chart Configuration")
#        self.BuildTimesByMetricsChartPanel(TIME_TYPE_AVG)
#        
#    def OnShowChartTTotalVarRepButtonClicked(self, event):
#        """ """
#        if len(self.curves) == 0:
#            wx.MessageBox("No curves defined. You must add at least one curve.", 
#                          'Error', wx.OK | wx.ICON_ERROR)
#        else:
#            self.CalculateAndShowChartByRepFrame(TIME_TYPE_MAX)
#    
#    def OnShowChartTAvgVarRepButtonClicked(self, event):
#        """ """
#        if len(self.curves) == 0:
#            wx.MessageBox("No curves defined. You must add at least one curve.", 
#                          'Error', wx.OK | wx.ICON_ERROR)
#        else:
#            self.CalculateAndShowChartByRepFrame(TIME_TYPE_AVG)
#        
#    def OnShowChartTTotalVarMetricsButtonClicked(self, event):
#        """ """
#        if len(self.curves) == 0:
#            wx.MessageBox("No curves defined. You must add at least one curve.", 
#                          'Error', wx.OK | wx.ICON_ERROR)
#        else:
#            self.CalculateAndShowChartByMetricsFrame(TIME_TYPE_MAX)
#    
#    def OnShowChartTAvgVarMetricsButtonClicked(self, event):
#        """ """
#        if len(self.curves) == 0:
#            wx.MessageBox("No curves defined. You must add at least one curve.", 
#                          'Error', wx.OK | wx.ICON_ERROR)
#        else:
#            self.CalculateAndShowChartByMetricsFrame(TIME_TYPE_AVG)
#        
#    def OnShowChartTTotalVarVersionButtonClicked(self, event):
#        """ """
#        if len(self.simulators) == 0:
#            wx.MessageBox("There are no finished simulations yet. Please wait and try again.", 
#                          'Error', wx.OK | wx.ICON_ERROR)
#        else:
#            self.CalculateAndShowChartByVersions()
#        
#    def OnAddCurveButtonClicked(self, event):
#        """ """
#        lblParts = []
#        curveSimulators = []
#        for ch in self.checkboxSimulator:
#            if ch.IsChecked():
#                curveSimulators.append(self.checkboxSimulator[ch])
#                lblParts.append(self.checkboxSimulator[ch].context.version.name)
#        
#        if len(curveSimulators) == 0:
#            return
#        
#        self.curves.append(curveSimulators)
#        
#        curveLabel = "%d. Versions: %s" % (len(self.curves), ', '.join(lblParts))
#        text = wx.StaticText(self.curvesListPanel, label=curveLabel)
#        self.curvesListPanelSizer.Add(text)
#        
#        self.Layout()
#    
#    #################
#    # LAYOUT
#    #################
#    
#    def BuildCurvesPanel(self, parent, parentSizer, onShowChartClicked):
#        """ """
#        rightBox = wx.StaticBox(parent, label="Define curves")
#        rightBoxSizer = wx.StaticBoxSizer(rightBox, wx.HORIZONTAL)
#        parentSizer.Add(rightBoxSizer, 4, wx.ALL, 5)
#        
#        addCurveBox = wx.StaticBox(parent, label="Add curve")
#        addCurveBoxSizer = wx.StaticBoxSizer(addCurveBox, wx.VERTICAL)
#        rightBoxSizer.Add(addCurveBoxSizer, 0, wx.ALL, 5)
#        
#        self.checkboxSimulator = {} 
#        
#        for s in self.simulators:
#            version = s.context.version
#            ch = wx.CheckBox(parent, label=version.name)
#            addCurveBoxSizer.Add(ch)
#            self.checkboxSimulator[ch] = s
#            
#        addCurveButton = wx.Button(parent, label="Add curve")
#        addCurveBoxSizer.Add(addCurveButton, 0, wx.ALIGN_CENTER)
#        addCurveButton.Bind(wx.EVT_BUTTON, self.OnAddCurveButtonClicked)
#        
#        curvesBox = wx.StaticBox(parent, label="Curves")
#        curvesBoxSizer = wx.StaticBoxSizer(curvesBox, wx.VERTICAL)
#        rightBoxSizer.Add(curvesBoxSizer, 1, wx.ALL, 5)
#        
#        self.curvesListPanel = wx.Panel(parent)
#        self.curvesListPanelSizer = wx.BoxSizer(wx.VERTICAL)
#        self.curvesListPanel.SetSizer(self.curvesListPanelSizer)
#        curvesBoxSizer.Add(self.curvesListPanel, 1, wx.ALL | wx.EXPAND, 5)
#        
#        showChartBtn = wx.Button(parent, label="Show Chart")
#        showChartBtn.Bind(wx.EVT_BUTTON, onShowChartClicked)
#        curvesBoxSizer.Add(showChartBtn, 0, wx.ALIGN_CENTER)
#    
#    def BuildTimesByRepetitionsChartPanel(self, timeType):
#        """ """
#        if self.chartPanel:
#            self.chartPanel.Destroy()
#            self.chartPanel = None
#            
#        self.chartPanel = wx.Panel(self)
#        chartPanelSizer = wx.BoxSizer(wx.HORIZONTAL)
#        self.chartPanel.SetSizer(chartPanelSizer)
#        
#        leftBox = wx.StaticBox(self.chartPanel, label="Choose host")
#        leftBoxSizer = wx.StaticBoxSizer(leftBox, wx.VERTICAL)
#        chartPanelSizer.Add(leftBoxSizer, 1, wx.ALL, 5)
#        
#        self.hostRadios = []
#        
#        hostsRepetitions = self._GetHostsRepetitions()
#        for hostName in hostsRepetitions:
#            radioBtn = wx.RadioButton(self.chartPanel, label=hostName)
#            leftBoxSizer.Add(radioBtn)
#            self.hostRadios.append(radioBtn)
#        
#        onShowChartBtnClicked = None
#        if timeType == TIME_TYPE_MAX:
#            onShowChartBtnClicked = self.OnShowChartTTotalVarRepButtonClicked
#        elif timeType == TIME_TYPE_AVG:
#            onShowChartBtnClicked = self.OnShowChartTAvgVarRepButtonClicked
#        
#        self.BuildCurvesPanel(self.chartPanel, chartPanelSizer, onShowChartBtnClicked)
#        
#        self.chartConfigBoxSizer.Add(self.chartPanel, 1, wx.ALL | wx.EXPAND, 5)
#        self.Layout()
#        
#        self.curves = []
#    
#    def BuildTimesByVersionsChartPanel(self, timeType):
#        """ """
#        if self.chartPanel:
#            self.chartPanel.Destroy()
#            self.chartPanel = None
#            
#        self.chartPanel = wx.Panel(self)
#        chartPanelSizer = wx.BoxSizer(wx.HORIZONTAL)
#        self.chartPanel.SetSizer(chartPanelSizer)
#        
#        self.BuildCurvesPanel(self.chartPanel, chartPanelSizer, self.OnShowChartTTotalVarVersionButtonClicked)
#        
#        self.chartConfigBoxSizer.Add(self.chartPanel, 1, wx.ALL | wx.EXPAND, 5)
#        self.Layout()
#        
#        self.curves = []
#    
#    def BuildTimesByMetricsChartPanel(self, timeType):
#        """ """
#        if self.chartPanel:
#            self.chartPanel.Destroy()
#            self.chartPanel = None
#            
#        self.chartPanel = wx.Panel(self)
#        chartPanelSizer = wx.BoxSizer(wx.HORIZONTAL)
#        self.chartPanel.SetSizer(chartPanelSizer)
#        
#        leftBox = wx.StaticBox(self.chartPanel, label="Metrics")
#        leftBoxSizer = wx.StaticBoxSizer(leftBox, wx.VERTICAL)
#        chartPanelSizer.Add(leftBoxSizer, 0, wx.ALL, 5)
#        
#        self.metrics = self._GetMetrics()
#        
#        i = 0
#        for metric in self.metrics:
#            i += 1
#            metricPanel = wx.Panel(self.chartPanel)
#            metricPanelSizer = wx.BoxSizer(wx.HORIZONTAL)
#            metricPanel.SetSizer(metricPanelSizer)
#            
#            leftBoxSizer.Add(metricPanel)
#            
#            metricNumber = "%d ." % i
#            lbl = wx.StaticText(metricPanel, label=metricNumber)
#            metricPanelSizer.Add(lbl)
#            
#            metricsConfigPanel = wx.Panel(metricPanel)
#            metricsConfigPanelSizer = wx.BoxSizer(wx.VERTICAL)
#            metricsConfigPanel.SetSizer(metricsConfigPanelSizer)
#            
#            metricPanelSizer.Add(metricsConfigPanel)
#            
#            for mSet in metric:
#                lbl = wx.StaticText(metricsConfigPanel, label="Host: %s -> Config: %s" % (mSet.host_name, mSet.configuration_name))
#                metricsConfigPanelSizer.Add(lbl)
#        
#        onShowChartBtnClicked = None
#        if timeType == TIME_TYPE_MAX:
#            onShowChartBtnClicked = self.OnShowChartTTotalVarMetricsButtonClicked
#        elif timeType == TIME_TYPE_AVG:
#            onShowChartBtnClicked = self.OnShowChartTAvgVarMetricsButtonClicked
#        
#        self.BuildCurvesPanel(self.chartPanel, chartPanelSizer, onShowChartBtnClicked)
#        
#        self.chartConfigBoxSizer.Add(self.chartPanel, 1, wx.ALL | wx.EXPAND, 5)
#        self.Layout()
#        
#        self.curves = []
#        
#    def CalculateAndShowChartByRepFrame(self, timeType):
#        """ """
#        
#        def TTotal(module, simulator, hosts):
#            val = 0.0 
#            for h in hosts:
#                t = module.get_current_time(simulator, h)
#                if t > val:
#                    val = t
#            return val
#        
#        def TAvg(module, simulator, hosts):
#            s = 0.0 
#            for h in hosts:
#                s += module.get_current_time(simulator, h)
#            l = len(hosts)
#            if l == 0:
#                return  0
#            return s / float(l)
#        
#        hostName = None
#        for radio in self.hostRadios:
#            if radio.GetValue():
#                hostName = radio.GetLabel()
#                break
#        if not hostName:
#            return
#        
#        curvesData = []
#        
#        chartFun = lambda x : x
#        chartTitle  = ""
#        xLabel      = ""
#        yLabel      = ""
#        
#        if timeType == TIME_TYPE_MAX:
#            chartFun    = TTotal
#            chartTitle  = "Chart: Total Time / Repetitions"
#            xLabel      = "Repetitions"
#            yLabel      = "T_Total"
#        else:
#            chartFun    = TAvg
#            chartTitle  = "Chart: TimeAvg / Repetitions"
#            xLabel      = "Repetitions"
#            yLabel      = "TAvg"
#        
#        i = 0
#        for curveSimulators in self.curves:
#            
#            i += 1
#            label = "%d." % i
#            
#            values = []
#            hostsBySimulator = self._GetHosts(curveSimulators, hostName)
#            for s in hostsBySimulator:
#                values.append((len(hostsBySimulator[s]), chartFun(self.module, s, hostsBySimulator[s])))
#
#            values.sort(key=lambda t: t[0])                
#            curveData = (label, values)
#            curvesData.append(curveData)
#            
#        self.ShowChartFrame(chartTitle, xLabel, yLabel, curvesData)
#        
#    def CalculateAndShowChartByMetricsFrame(self, timeType):
#        """ """
#        
#        def TTotal(values):
#            val = 0.0 
#            for t in values:
#                if t > val:
#                    val = t
#            return val
#        
#        def TAvg(values):
#            s = 0.0 
#            for v in values:
#                s += v
#            l = len(values)
#            if l == 0:
#                return  0
#            return s / float(l)
#        
#        def buildLegend(parent):
#            
#            mainBox = wx.StaticBox(parent, label="Metrics")
#            mainBoxSizer = wx.StaticBoxSizer(mainBox,wx.VERTICAL)
#            
#            i = 0
#            for metric in self.metrics:
#                i += 1
#                metricPanel = wx.Panel(parent)
#                metricPanelSizer = wx.BoxSizer(wx.HORIZONTAL)
#                metricPanel.SetSizer(metricPanelSizer)
#                
#                mainBoxSizer.Add(metricPanel)
#                
#                metricNumber = "%d ." % i
#                lbl = wx.StaticText(metricPanel, label=metricNumber)
#                metricPanelSizer.Add(lbl)
#                
#                metricsConfigPanel = wx.Panel(metricPanel)
#                metricsConfigPanelSizer = wx.BoxSizer(wx.VERTICAL)
#                metricsConfigPanel.SetSizer(metricsConfigPanelSizer)
#                
#                metricPanelSizer.Add(metricsConfigPanel)
#
#                for mSet in metric:
#                    lbl = wx.StaticText(metricsConfigPanel, label="Host: %s -> Config: %s" % (mSet.host_name, mSet.configuration_name))
#                    metricsConfigPanelSizer.Add(lbl)
#        
#            return mainBoxSizer
#        
#        curvesData = []
#        
#        chartFun = lambda x : x
#        chartTitle  = ""
#        xLabel      = ""
#        yLabel      = ""
#        
#        if timeType == TIME_TYPE_MAX:
#            chartFun    = TTotal
#            chartTitle  = "Chart: Total Time / Metric"
#            xLabel      = "Metric"
#            yLabel      = "T_Total"
#        else:
#            chartFun    = TAvg
#            chartTitle  = "Chart: TimeAvg / Metric"
#            xLabel      = "Metric"
#            yLabel      = "TAvg"
#        
#        c = 0
#        for curveSimulators in self.curves:
#            c += 1
#
#            values = []
#            i = 0
#            for m in self.metrics:
#                i += 1
#                time_values = []
#                
#                for s in curveSimulators:
#                    currentMetric = self._GetMetric(s)
#                    if self._AreMetricsEqual(m, currentMetric):
#                        time_values.extend([ self.module.get_current_time(s, h) 
#                                            for h in s.context.hosts])
#                
#                values.append((i, chartFun(time_values)))
#            
#            values.sort(key=lambda t: t[0])                
#            curveData = ("%d." % c, values)
#            curvesData.append(curveData)
#            
#        self.ShowChartFrame(chartTitle, xLabel, yLabel, curvesData, 
#                            buildLegendPanelFun=buildLegend)
#        
#    def CalculateAndShowChartByVersions(self):
#        """ """
#        def chartFun(module, simulator, hosts):
#            val = 0.0 
#            for h in hosts:
#                t = module.get_current_time(simulator, h)
#                if t > val:
#                    val = t
#            return val
#        
#        chartTitle  = "TTotal / Version"
#        xLabel      = "Version"
#        yLabel      = "TTotal"
#        curvesData  = []
#
#        c = 0
#        for curveSimulators in self.curves:
#            c += 1
#
#            values = []
#            i = 0
#            for s in curveSimulators:
#                i += 1
#                values.append((i, chartFun(self.module, s, s.context.hosts)))
#                
#            values.sort(key=lambda t: t[0]) 
#
#            curveData = ("%d." % c, values)
#            curvesData.append(curveData)
#            
#        self.ShowChartFrame(chartTitle, xLabel, yLabel, curvesData)
#        
#    def AddFinishedSimulation(self, simulator):
#        """ """
#        self.simulators.append(simulator)
#
#        self.chartTypeBox.Show()
#        self.totalTimeOnRepetitionBtn.Show()
#        self.totalTimeOnMetricsBtn.Show()
#        self.totalTimeOnVersionsBtn.Show()
#        self.avgTimeOnRepetitionBtn.Show()
#        self.avgTimeOnMetricsBtn.Show()
#
#        self.chartConfigBox.Show()
#        self.chartConfigBox.SetLabel("Chart Configuration")
#        self.Layout()
#
#    def RemoveAllSimulations(self):
#        """ """
#        self.simulators = []
#        self.chartTypeBox.Hide()
#        self.totalTimeOnRepetitionBtn.Hide()
#        self.totalTimeOnMetricsBtn.Hide()
#        self.totalTimeOnVersionsBtn.Hide()
#        self.avgTimeOnRepetitionBtn.Hide()
#        self.avgTimeOnMetricsBtn.Hide()
#
#        self.chartConfigBox.Hide()
#        self.chartConfigBoxSizer.Clear(True)
#        self.Layout()
#        
#    def ShowChartFrame(self, chartTitle, xTitle, yTitle, curvesData, 
#                       buildLegendPanelFun = None):
#        """ Shows frame with gnuplot chart """
#        
#        from wx.lib.plot import PlotCanvas, PolyMarker, PolyLine, PlotGraphics
#        import random 
#        
#        def drawPlot(chartTitle, xTitle, yTitle, curvesData):
#            """ """
#            plots = []
#            
#            for curveData in curvesData:
#                cr = random.randint(0, 255)
#                cg = random.randint(0, 255)
#                cb = random.randint(0, 255)
#                markers = PolyMarker(curveData[1], legend=curveData[0], 
#                                     colour=wx.Color(cr,cg,cb), size=2)
#                line = PolyLine(curveData[1], legend=curveData[0], 
#                                colour=wx.Color(cr,cg,cb), width=1)
#                plots.append(markers)
#                plots.append(line)
#            
#            return PlotGraphics(plots, chartTitle, 
#                                xTitle, yTitle)
#        
#        frame = wx.Frame(None, title=chartTitle)
#        panel = wx.Panel(frame)
#        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
#        panel.SetSizer(panelSizer)
#        
#        frameSizer = wx.BoxSizer(wx.VERTICAL)
#        frameSizer.Add(panel, 1, wx.ALL | wx.EXPAND, 5)
#        frame.SetSizer(frameSizer)
#        
#        canvas = PlotCanvas(panel)
#        canvas.Draw(drawPlot(chartTitle, xTitle, yTitle, curvesData))
#        
#        if buildLegendPanelFun:
#            legendPanel = buildLegendPanelFun(panel)
#            panelSizer.Add(legendPanel, 0, wx.ALL, 5)
#        panelSizer.Add(canvas, 1, wx.EXPAND)
#        
#        panelSizer.Layout()
#        
#        frame.Maximize(True)
#        frame.Show()
    
TIME_TYPE_TOTAL = 1
TIME_TYPE_AVG   = 2
    
class DistributedSystemOptimizationPanel(wx.ScrolledWindow):
    
    def __init__(self, module, *args, **kwargs):
        wx.ScrolledWindow.__init__(self, *args, **kwargs)

        self.module = module
        self.checkBoxes = []
        self.checkBoxToSimulator = {}
        
        # OPTIMIZATION CONFIGURATION
        
        descText = wx.StaticText(self, label="Distributed System Optimization can " + \
        "automatically answer the question what is the difference in performance " + \
        "between created scenarios. The difference is represented by number of " + \
        "simultaneous clients that are used in the protocol. Optimization algorithm " + \
        "tries to find the numbers of simultaneous clients for each version " + \
        "such that the execution time of protocols will be the same (with tolerance)."
        , style=wx.TE_MULTILINE | wx.TE_READONLY)
        
        configurationBox = wx.StaticBox(self, label="Optimization configuration")
        configurationBoxSizer = wx.StaticBoxSizer(configurationBox, wx.VERTICAL)
        
        hostSizer = wx.BoxSizer(wx.HORIZONTAL)
        hostText = wx.StaticText(self, label="Host:", size=(200, -1))
        self.hostCombo = wx.ComboBox(self, style=wx.TE_READONLY, size=(200, -1))
        hostSizer.Add(hostText, 1)
        hostSizer.Add(self.hostCombo, 1)
        
        versionsSizer = wx.BoxSizer(wx.HORIZONTAL)
        versionsText = wx.StaticText(self, label="Versions:", size=(200, -1))
        self.versionsSelectSizer = wx.BoxSizer(wx.VERTICAL)  
        versionsSizer.Add(versionsText, 1)  
        versionsSizer.Add(self.versionsSelectSizer, 1)
        
        typeSizer = wx.BoxSizer(wx.HORIZONTAL)
        timeTypeText = wx.StaticText(self, label="Time type:", size=(200, -1))
        timeTypeSelectSizer = wx.BoxSizer(wx.VERTICAL)
        self.avgRadioBtn = wx.RadioButton(self, label="Average")
        self.avgRadioBtn.SetValue(True)
        self.totalRadioBtn = wx.RadioButton(self, label="Total")
        timeTypeSelectSizer.Add(self.avgRadioBtn)
        timeTypeSelectSizer.Add(self.totalRadioBtn)
        typeSizer.Add(timeTypeText, 1)
        typeSizer.Add(timeTypeSelectSizer, 1)
        
        self.startButton = wx.Button(self, label="Start optimization")
        self.startButton.Bind(wx.EVT_BUTTON, self.OnStartClick)
        
        configurationBoxSizer.Add(hostSizer, 0, wx.ALIGN_CENTER|wx.ALL, 10)
        configurationBoxSizer.Add(versionsSizer, 0, wx.ALIGN_CENTER|wx.ALL, 10)
        configurationBoxSizer.Add(typeSizer, 0, wx.ALIGN_CENTER|wx.ALL, 10)
        configurationBoxSizer.Add(self.startButton, 0, wx.ALIGN_CENTER|wx.ALL, 10)
        
        # OPTIMIZATION PROCESS
        self.module.get_gui().Bind(aqopa_gui.EVT_MODULE_SIMULATION_ALLOWED, self.OnSimulationAllowed)
        
        self.interpreter = None # Interpreter used to run simulators
        
        self.maxTime = 0 # Maximum execution time (avg or total)
        self.timeType = None # The type of time calculation (avg or total)
        self.hostName = None # Name of host used to calculate avg time
        self.maxSimulator = None # The simulator with maximum execution time
        self.maxRepetition = 0 # The number of simulatenous clients in scenario with maximum execution time 
        
        self.newSimulator = None
        self.previousRepetition = 0
        self.previousTime = 0
        self.currentRepetition = 0
        self.currentTime = 0
        self.tolerance = 0.05
        
        self.progressTimer      = wx.Timer(self)
        self.dots = 0
        self.Bind(wx.EVT_TIMER, self.OnProgressTimerTick, self.progressTimer)
        
        self.processBox = wx.StaticBox(self, label="Optimization process")
        processBoxSizer = wx.StaticBoxSizer(self.processBox, wx.VERTICAL)
        
        self.statusText = wx.StaticText(self, label="Not started")
        self.dotsText = wx.StaticText(self, label="")
        self.dotsText.Hide()
        self.repetitionText = wx.StaticText(self, label="")
        self.repetitionText.Hide()
        
        self.maximumBox = wx.StaticBox(self, label="Maximum time version")
        maximumBoxSizer = wx.StaticBoxSizer(self.maximumBox, wx.VERTICAL)
        
        hs = wx.BoxSizer(wx.HORIZONTAL)
        self.versionsLabel = wx.StaticText(self, label="Version:")
        hs.Add(self.versionsLabel, 0)
        self.maximumVersionText = wx.StaticText(self, label="")
        hs.Add(self.maximumVersionText, 0, wx.ALIGN_RIGHT)
        maximumBoxSizer.Add(hs, 0)
        
        hs = wx.BoxSizer(wx.HORIZONTAL)
        self.timeLabel = wx.StaticText(self, label="Time:")
        hs.Add(self.timeLabel, 0)
        self.maximumTimeText = wx.StaticText(self, label="")
        hs.Add(self.maximumTimeText, 0, wx.ALIGN_RIGHT)
        maximumBoxSizer.Add(hs, 0)
        
        hs = wx.BoxSizer(wx.HORIZONTAL)
        self.hostsNumberLabel = wx.StaticText(self, label="Hosts number:")
        hs.Add(self.hostsNumberLabel, 0)
        self.maximumRepetitionText = wx.StaticText(self, label="")
        hs.Add(self.maximumRepetitionText, 0, wx.ALIGN_RIGHT)
        maximumBoxSizer.Add(hs, 0)
        
        self.resultsBox = wx.StaticBox(self, label="Optimization results")
        self.resultsBoxSizer = wx.StaticBoxSizer(self.resultsBox, wx.VERTICAL)
        
        processBoxSizer.Add(self.statusText, 0, wx.ALIGN_CENTER|wx.ALL, 10)
        processBoxSizer.Add(self.dotsText, 0, wx.ALIGN_CENTER|wx.ALL, 10)
        processBoxSizer.Add(self.repetitionText, 0, wx.ALIGN_CENTER|wx.ALL, 10)
        processBoxSizer.Add(maximumBoxSizer, 0, wx.EXPAND|wx.ALL, 10)
        processBoxSizer.Add(self.resultsBoxSizer, 0, wx.EXPAND|wx.ALL, 10)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(descText, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(configurationBoxSizer, 0, wx.EXPAND|wx.ALL, 10)
        sizer.Add(processBoxSizer, 0, wx.EXPAND|wx.ALL, 10)
        
        self.SetSizer(sizer)
        self.SetScrollRate(0, 10)
        
    def _OptimizationStep(self):
        """
        Implements one step of optimization.
        """
        nextRepetition = self._GenerateNewRepetitionNumber(self.maxTime, self.previousTime, 
                                    self.currentTime, self.previousRepetition, self.currentRepetition)
        if nextRepetition is None:
            self.currentTime = None
            self.currentRepetition = None
            self._FinishSimulatorOptimization()
            return

        if nextRepetition == self.currentRepetition:
            self._FinishSimulatorOptimization()
            return

        self.previousRepetition = self.currentRepetition
        self.currentRepetition = nextRepetition
        
        simulator = self.optimizedSimulators[self.optimizedSimulatorIndex]
        newVersion = simulator.context.version.clone()
        changed = False 
        for rh in newVersion.run_hosts:
            if rh.host_name == self.hostName:
                rh.repetitions = nextRepetition
                changed = True
                break
        if not changed:
            self.currentTime = None
            self._FinishSimulatorOptimization()
            return
         
        self.repetitionText.SetLabel("Repetition: %d" % nextRepetition)
        self.newSimulator = self.interpreter.builder.build_simulator(self.interpreter.store, newVersion)
        self.interpreter.install_modules(self.newSimulator)
        wx.lib.delayedresult.startWorker(self._FinishStep, 
                                         self.interpreter.run_simulation, 
                                         wargs=(self.newSimulator,))
        
    def _FinishStep(self, result):
        """
        Handles the result of one optimization step (simulation of new repetition number). 
        """
        
        try :
            result.get()
            
            self.previousTime = self.currentTime
            self.currentTime = self._GetTime(self.newSimulator, self.timeType, self.hostName)
            
            if (self.currentTime == self.previousTime) and (self.currentRepetition == self.previousRepetition):
                self._FinishSimulatorOptimization()
                return
            
            if (self.currentTime <= self.previousTime) and (self.currentRepetition >= self.previousRepetition):
                self.currentTime = None
                self.currentRepetition = None
                self._FinishSimulatorOptimization()
                return
            
            relError = abs(self.maxTime - self.currentTime)/self.maxTime
            if relError <= self.tolerance:
                self._FinishSimulatorOptimization()
                return
                
            self._OptimizationStep()
                    
        except RuntimeException, e:
            self.currentTime = None
            self._FinishSimulatorOptimization()
        except Exception, e:
            import traceback
            print traceback.format_exc()
            self.currentTime = None
            self._FinishSimulatorOptimization()
        
                
    def _FinishSimulatorOptimization(self):
        """
        Actions taken when optimization of one simulator is finished.
        """
        timeText = "Failed"
        repetitionText = ""
        if self.currentTime is not None:
            timeText = "%.2f ms" % self.currentTime
            repetitionText = "%d" % self.currentRepetition
            
        simulator = self.optimizedSimulators[self.optimizedSimulatorIndex]
        hS = wx.BoxSizer(wx.HORIZONTAL)
        hS.Add(wx.StaticText(self, label=simulator.context.version.name, size=(200, -1)), 0)
        hS.Add(wx.StaticText(self, label=timeText, size=(200, -1)), 0)
        hS.Add(wx.StaticText(self, label=repetitionText, size=(200, -1)), 0)
        self.resultsBoxSizer.Add(hS)
        self.Layout()
        
        self.optimizedSimulatorIndex += 1
        self._OptimizeNextSimulator()
        
    def _OptimizeNextSimulator(self):
        """ 
        Function find the number of simultaneous clients 
        for the next simulator from class field ```optimizedSimulators```.
        The next simulator is at index ```optimizedSimulatorIndex``` field.
        When no more simulators are left the optimization process is finished.
        """
        
        if self.optimizedSimulatorIndex >= len(self.optimizedSimulators):
            self.progressTimer.Stop()
            self.statusText.SetLabel("Finished")
            self.dotsText.SetLabel("")
            self.dotsText.Hide()
            self.repetitionText.SetLabel("")
            self.repetitionText.Hide()
            self.Layout()
            self.progressTimer.Stop()
            self.startButton.Enable(True)
            wx.PostEvent(self.module.get_gui(), aqopa_gui.ModuleSimulationFinishedEvent())
            return
            
        simulator = self.optimizedSimulators[self.optimizedSimulatorIndex]
        
        self.previousRepetition = 0
        self.previousTime = 0
        self.currentRepetition = self._GetHostRepetition(simulator, self.hostName)
        self.currentTime = self._GetTime(simulator, self.timeType, self.hostName)
        
        self.statusText.SetLabel("Working on %s" % simulator.context.version.name)
        self.repetitionText.SetLabel("")
        self._OptimizationStep()
        
    def _GetTime(self, simulator, timeType, hostName):
        """ 
        Returns the execution time of simulator.
        Parameter ``timeType`` selects the way of calculating time.
        It may be total execution time or average execution time of 
        host ``hostName``.
        """  
        times = self.module.current_times[simulator]
        if timeType == TIME_TYPE_TOTAL:
            return max([times[i] for i in times ])
        else: # TIME_TYPE_AVG
            nb_hosts = 0
            sum_times = 0.0
            for h in times:
                if h.original_name() == hostName:
                    nb_hosts += 1
                    sum_times += times[h]
            if nb_hosts > 0:
                return sum_times / nb_hosts
        return 0
    
    def _GetHostRepetition(self, simulator, hostName):
        """
        Returns number of repeated hosts ``hostName``.
        """
        version = simulator.context.version
        nb = 0
        for rh in version.run_hosts:
            if rh.host_name == hostName:
                nb += rh.repetitions
        return nb
    
    def _GetMaximumTimeSimulator(self, simulators, timeType, hostName):
        """ 
        Returns triple (simulator, time) with the maximum execution 
        time depending on the tipe of time selected
        """
        simulator = None
        time = 0.0
        for s in simulators:
            t = self._GetTime(s, timeType, hostName)
            if t >= time:
                simulator = s
                time = t
        return (simulator, time)
    
    def _GenerateNewRepetitionNumber(self, maxTime, previousTime, currentTime, 
                                     previousRepetition, currentRepetition):
        """
        Return the next number of simultaneous hosts closer to the final result.
        """
        if previousTime == currentTime:
            if currentRepetition == 0:
                return None
            a = currentTime / currentRepetition
            if a == 0:
                return None
            return int(maxTime / a)
        else:
            if currentRepetition == previousRepetition:
                return None
            a = (currentTime - previousTime) / (currentRepetition - previousRepetition)
            b = currentTime - currentRepetition * a
            return int((maxTime - b) / a)
        
    def RemoveAllSimulations(self):
        """ """
        self.checkBoxes = []
        self.checkBoxToSimulator = {}
        self.optimizedSimulators = []
        self.optimizedSimulatorIndex = 0

        self.startButton.Enable(False)
        self.hostCombo.Clear()
        self.hostCombo.SetValue("")
        self.versionsSelectSizer.Clear(True)

        self.processBox.Hide()
        self.statusText.Hide()
        self.dotsText.Hide()
        self.repetitionText.Hide()

        self.maximumBox.Hide()
        self.versionsLabel.Hide()
        self.timeLabel.Hide()
        self.hostsNumberLabel.Hide()
        self.maximumRepetitionText.Hide()
        self.maximumRepetitionText.SetLabel("")
        self.maximumTimeText.Hide()
        self.maximumTimeText.SetLabel("")
        self.maximumVersionText.Hide()
        self.maximumVersionText.SetLabel("")

        self.resultsBox.Hide()
        self.resultsBoxSizer.Clear(True)

        self.Layout()

    def AddFinishedSimulation(self, simulator):
        """ """
        version = simulator.context.version
        ch = wx.CheckBox(self, label=version.name)
        self.checkBoxes.append(ch)
        self.checkBoxToSimulator[ch] = simulator
        self.versionsSelectSizer.Add(ch)
        self.Layout()
    
    def OnAllSimulationsFinished(self, simulators):
        """ """
        items = []
        for s in simulators:
            version = s.context.version
            for rh in version.run_hosts:
                if rh.host_name not in items:
                    items.append(rh.host_name)

        self.hostCombo.Clear()
        self.hostCombo.AppendItems(items)
        self.hostCombo.Select(0)

        self.startButton.Enable(True)
        self.Layout()
    
    def OnStartClick(self, event=None):
        """ """
        self.processBox.Show()
        self.statusText.Show()
        self.dotsText.Show()
        self.repetitionText.Show()

        self.maximumBox.Show()
        self.versionsLabel.Show()
        self.timeLabel.Show()
        self.hostsNumberLabel.Show()
        self.maximumRepetitionText.Show()
        self.maximumTimeText.Show()
        self.maximumVersionText.Show()

        self.resultsBox.Show()

        simulators = []
        for ch in self.checkBoxes:
            if ch.IsChecked():
                simulators.append(self.checkBoxToSimulator[ch])
                
        if len(simulators) < 2:
            wx.MessageBox('Please select at least 2 versions.', 'Error', 
                          wx.OK | wx.ICON_ERROR)
            return
        
        self.timeType = TIME_TYPE_TOTAL
        if self.avgRadioBtn.GetValue():
            self.timeType = TIME_TYPE_AVG
        self.hostName = self.hostCombo.GetValue() 
        self.maxSimulator, self.maxTime = self._GetMaximumTimeSimulator(simulators, self.timeType, self.hostName)
        self.maxRepetition = self._GetHostRepetition(self.maxSimulator, self.hostName)
        
        self.maximumVersionText.SetLabel("%s" % self.maxSimulator.context.version.name)
        self.maximumTimeText.SetLabel("%.5f ms" % self.maxTime)
        self.maximumRepetitionText.SetLabel("%d" % self.maxRepetition)
        
        if self.maxTime == 0:
            wx.MessageBox('Maximum time is equal to 0. Cannot optimize.', 'Error', 
                          wx.OK | wx.ICON_ERROR)
            return
        
        self.startButton.Enable(False)
        self.statusText.SetLabel("Waiting for simulator")
        
        self.resultsBoxSizer.Clear(True)
        hS = wx.BoxSizer(wx.HORIZONTAL)
        hS.Add(wx.StaticText(self, label="Version", size=(200, -1)), 0)
        hS.Add(wx.StaticText(self, label="Time", size=(200, -1)), 0)
        hS.Add(wx.StaticText(self, label="Hosts", size=(200, -1)), 0)
        self.resultsBoxSizer.Add(hS)
        
        self.Layout()
        
        simulators.remove(self.maxSimulator)
        self.progressTimer.Start(500)
        self.optimizedSimulators = simulators
        self.optimizedSimulatorIndex = 0
        
        wx.PostEvent(self.module.get_gui(), aqopa_gui.ModuleSimulationRequestEvent(module=self.module))
          
    def OnSimulationAllowed(self, event):
        """ """
        self.interpreter = event.interpreter
        self._OptimizeNextSimulator()
            
    ################
    # PROGRESS BAR 
    ################
        
    def OnProgressTimerTick(self, event):
        """ """
        self.dots  = (self.dots + 1) % 10
        self.dotsText.SetLabel("." * self.dots)
        self.Layout()
        
class MainResultsNotebook(wx.Notebook):
    """ """
    def __init__(self, module, *args, **kwargs):
        wx.Notebook.__init__(self, *args, **kwargs)
        
        self.module = module
        
        self.oneVersionTab = SingleVersionPanel(self.module, self)
        self.AddPage(self.oneVersionTab, "Single Version")
        self.oneVersionTab.Layout()
        
#        self.compareTab = VersionsChartsPanel(self.module, self)
#        self.AddPage(self.compareTab, "Versions' Charts")
#        self.compareTab.Layout()
        
        self.distributedOptimizationTab = DistributedSystemOptimizationPanel(self.module, self)
        self.AddPage(self.distributedOptimizationTab, "Distributed System Optimization")
        self.distributedOptimizationTab.Layout()
        
    def OnParsedModel(self):
        """ """
        self.oneVersionTab.RemoveAllSimulations()
#        self.compareTab.RemoveAllSimulations()
        self.distributedOptimizationTab.RemoveAllSimulations()
        
    def OnSimulationFinished(self, simulator):
        """ """
        self.oneVersionTab.AddFinishedSimulation(simulator)
#        self.compareTab.AddFinishedSimulation(simulator)
        self.distributedOptimizationTab.AddFinishedSimulation(simulator)
        
    def OnAllSimulationsFinished(self, simulators):
        """ """
        self.distributedOptimizationTab.OnAllSimulationsFinished(simulators)
        
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
        return "Time Analysis"
    
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
        
        

        
        
        
        
