#!/usr/bin/env python

import wx
import os

"""
@file       general_purpose_frame_gui.py
@brief      GUI (frame = window) for modules configuration, results presentation, etc...
@author     Katarzyna Mazur
@date       created on 19-06-2014 by Katarzyna Mazur
"""

class GeneralFrame(wx.Frame):
    """
    @brief frame (simply: window) for configuring chosen modules
    """

    def __init__(self, parent, windowTitle, boxTitle, icon):
        wx.Frame.__init__(self, parent)

        self.SetIcon(wx.Icon(self.CreatePath4Resource(icon), wx.BITMAP_TYPE_PNG))
        self.SetTitle(windowTitle)

        # create static box aka group box
        self.groupBox = wx.StaticBox(self, label=boxTitle)
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
        self.CentreOnScreen()
        self.Layout()

    def AddPanel(self, panel) :
        self.panel = panel
        self.groupBoxSizer.Add(self.panel, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(self.sizer)
        self.sizer.Layout()

    def DoFit(self):
        self.sizer.Fit(self)
        self.CentreOnScreen()
        self.Layout()

    def SetWindowSize(self, width, height):
        self.SetClientSize(wx.Size(width, height))
        self.CentreOnScreen()
        self.Layout()

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