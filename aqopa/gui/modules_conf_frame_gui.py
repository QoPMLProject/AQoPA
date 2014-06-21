#!/usr/bin/env python

import wx

"""
@file       modules_conf_frame_gui.py
@brief      GUI (frame = window) for modules configuration
@author     Katarzyna Mazur
@date       created on 14-09-2013 by Katarzyna Mazur
"""

class ConfigFrame(wx.Frame):
    """
    @brief frame (simply: window) for configuring chosen modules
    """

    def __init__(self, parent):
        wx.Frame.__init__(self, parent)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        self.Layout()

    def AddPanel(self, panel) :
        self.sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.sizer.Layout()
        self.CentreOnParent()