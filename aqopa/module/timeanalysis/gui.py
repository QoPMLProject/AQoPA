'''
Created on 06-09-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

import wx

class MainResultsFrame(wx.Frame):
    """ 
    Frame presenting results for one simulation.  
    Simulator may be retrived from module, 
    because each module has its own simulator.
    """
    
    def __init__(self, module, simulator, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.module     = module
        self.simulator  = simulator
        
        #################
        # TOTAL TIME BOX
        #################
        
        totalTimeBox = wx.StaticBox(self, label="Total time")
        label = wx.StaticText(self, label="%.2f ms" % self.get_total_time())
        
        totalTimeBoxSizer = wx.StaticBoxSizer(totalTimeBox, wx.VERTICAL)
        totalTimeBoxSizer.Add(label, 1, wx.ALL | wx.ALIGN_CENTER, 5)
        
        #################
        # ONE TIME BOX
        #################
        
        statisticsBox = wx.StaticBox(self, label="Statistics")
        operationBoxSizer = self._BuildOperationsBox()
        
        statisticsBoxSizer = wx.StaticBoxSizer(statisticsBox, wx.HORIZONTAL)
        statisticsBoxSizer.Add(operationBoxSizer, 1, wx.ALL)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(totalTimeBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(statisticsBoxSizer, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)
        sizer.Fit(self)
        
    #################
    # LAYOUT
    #################
    
    def _BuildCHoosHostsBox(self):
        """ """
        chooseHostsBox = wx.StaticBox(self, label="Host(s)")
        chooseHostsBoxSizer = wx.StaticBoxSizer(chooseHostsBox, wx.VERTICAL)
        
        for h in self.simulator.context.hosts:
            pass
    
    def _BuildOperationsBox(self):
        """ """
        operationBox = wx.StaticBox(self, label="Operation")
        
        self.oneTimeRB = wx.RadioButton(self, label="One host's time")
        self.avgTimeRB = wx.RadioButton(self, label="Average hosts' time")
        self.minTimeRB = wx.RadioButton(self, label="Minimal hosts' time")
        self.maxTimeRB = wx.RadioButton(self, label="Maximal hosts' time")
        
        operationBoxSizer = wx.StaticBoxSizer(operationBox, wx.VERTICAL)
        operationBoxSizer.Add(self.oneTimeRB, 0, wx.ALL)
        operationBoxSizer.Add(self.avgTimeRB, 0, wx.ALL)
        operationBoxSizer.Add(self.minTimeRB, 0, wx.ALL)
        operationBoxSizer.Add(self.maxTimeRB, 0, wx.ALL)
        
        return operationBoxSizer
    
    #################
    # STATISTICS
    #################
        
    def get_total_time(self):
        """ Return total time of simulated version. """
        totalTime = 0
        hosts = self.simulator.context.hosts
        for h in hosts:
            t = self.module.get_current_time(self.simulator, h)
            if t > totalTime:
                totalTime = t
        return totalTime 
        
class AllSimulationsResultsFrame(wx.Frame):
    """ """
    
    def __init__(self, simulators, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        
        self.simulators = simulators

class ModuleGui(object):
    """
    Class used by GUI version of AQoPA.
    """
    
    def __init__(self, module):
        """ """
        self.module = module
        
    def get_name(self):
        return "Time analysis"
    
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
    
    def get_finished_simulation_frame(self, simulator):
        """ 
        Create frame presenting results for one simulation (version).
        """
        context = simulator.context
        return MainResultsFrame(self.module, simulator, None, 
                                title = "Time Analysis Results - Version: %s" 
                                % context.version.name)
        
    def get_finished_all_simulations_frame(self, simulators):
        """ 
        Create frame presenting results for all simulations (versions).
        Called once for all simulations after all of them are finished.
        """
        return AllSimulationsResultsFrame(simulators, None, 
                                          title = "Time Analysis - Results") 
        

        
        
        
        
