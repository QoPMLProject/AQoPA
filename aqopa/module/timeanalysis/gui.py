'''
Created on 06-09-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

import wx
from aqopa.simulator.state import Hook

class MainResultsFrame(wx.Frame):
    """ """
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        
        

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
    
    def get_finished_thread_frame(self, thread):
        """ """
        context = thread.simulator.context
        return MainResultsFrame(None, title = "Time Analysis Results - Version: %s" 
                                % context.version.name)
    
        

        
        
        
        
