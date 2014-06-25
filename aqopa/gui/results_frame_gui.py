#!/usr/bin/env python

import wx
import os

"""
@file       results_frame_gui.py
@brief      GUI (frame = window) for results presentation
@author     Katarzyna Mazur
@date       created on 25-06-2014 by Katarzyna Mazur
"""

class ResultsFrame(wx.Frame):
    """
    @brief frame (simply: window) for results presentation
    """

    def __init__(self, parent):
        wx.Frame.__init__(self, parent)

        self.SetIcon(wx.Icon(self.CreatePath4Resource('modules_results.png'), wx.BITMAP_TYPE_PNG))
        self.SetTitle("Analysis results")

        # create static box aka group box
        self.groupBox = wx.StaticBox(self, label="Results")
        self.groupBoxSizer = wx.StaticBoxSizer(self.groupBox, wx.VERTICAL)

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