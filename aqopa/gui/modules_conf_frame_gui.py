#!/usr/bin/env python

import wx
import os

"""
@file       modules_conf_frame_gui.py
@brief      GUI (frame = window) for modules configuration
@author     Katarzyna Mazur
@date       created on 19-06-2014 by Katarzyna Mazur
"""

class ConfigFrame(wx.Frame):
    """
    @brief frame (simply: window) for configuring chosen modules
    """

    def __init__(self, parent):
        wx.Frame.__init__(self, parent)

        self.SetIcon(wx.Icon(self.CreatePath4Resource('config.png'), wx.BITMAP_TYPE_PNG))
        self.SetTitle("Module Configuration")

        # create static box aka group box
        self.groupBox = wx.StaticBox(self, label="Configuration")
        self.groupBoxSizer = wx.StaticBoxSizer(self.groupBox, wx.VERTICAL)

        # create buttons - simple 'OK' and 'Cancel' will be enough
        self.OKButton = wx.Button(self, label="OK")
        self.cancelButton = wx.Button(self, label="Cancel")

        # do some bindings - for now on OK, as well as the cancel button
        # will simply close the module configuration window
        self.OKButton.Bind(wx.EVT_BUTTON, self.OnOKButtonClicked)
        self.cancelButton.Bind(wx.EVT_BUTTON, self.OnCancelButtonClicked)

        # align buttons
        bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
        bottomSizer.Add(wx.StaticText(self), 1, wx.EXPAND, 5)
        bottomSizer.Add(self.OKButton, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        bottomSizer.Add(self.cancelButton, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.groupBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add(bottomSizer, 0, wx.EXPAND, 5)
        self.SetSizer(self.sizer)
        self.CentreOnParent()
        self.Layout()

    def AddPanel(self, panel) :

        self.groupBoxSizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.sizer.Layout()
        self.CentreOnParent()

    def OnOKButtonClicked(self, event) :
        self.Close()

    def OnCancelButtonClicked(self, event) :
        self.Close()

    def CreatePath4Resource(self, resourceName):
        """
        @brief      creates and returns path to the
                    given file in the resource
                    ('assets') dir
        @return     path to the resource
        """
        tmp = os.path.split(os.path.dirname(__file__))
        return os.path.join(tmp[0], 'bin', 'assets', resourceName)