#!/usr/bin/env python

"""
@file       part_data_panel_gui.py
@brief      panel for model, metrics and versions tabs on AQoPA's main window
@author     Damian Rusinek
@author     Katarzyna Mazur (visual improvements)
@date       created on 05-09-2013 by Damian Rusinek
@date       edited on 06-05-2014 by Katarzyna Mazur
"""

import wx
import wx.richtext

class ModelPartDataPanel(wx.Panel):
    """
    @brief panel containing text area (and buttons 2) for one of model parts:
           model, metrics, configuration, used for creating tabs on AQoPA's
           main window
    """

    def __init__(self, *args, **kwargs):
        """ """
        wx.Panel.__init__(self, *args, **kwargs)

        # group box text = empty on start
        self.openedFileName = ""

         # group boxes aka static boxes
        self.tabBox = wx.StaticBox(self, label=self.openedFileName)

        # sizers = some kind of layout management
        self.tabBoxSizer = wx.StaticBoxSizer(self.tabBox, wx.HORIZONTAL)

        """bPanel = wx.Panel(self)
        bSizer = wx.BoxSizer(wx.VERTICAL)
        bPanel.SetSizer(bSizer)

        self.loadButton = wx.Button(bPanel)
        self.saveButton = wx.Button(bPanel)

        self.attachButtons(self.loadButton, self.saveButton)

        bSizer.Add(self.loadButton, 0, wx.ALL, 5)
        bSizer.Add(self.saveButton, 0, wx.ALL, 5)

        rightPanel = wx.Panel(self)
        rightPanelSizer = wx.BoxSizer(wx.VERTICAL)
        rightPanel.SetSizer(rightPanelSizer)

        self.dataTextArea = wx.richtext.RichTextCtrl(rightPanel, style=wx.TE_MULTILINE | wx.TE_NO_VSCROLL)
        self.dataTextArea.Bind(wx.EVT_KEY_UP, self.printCursorInfo)
        self.dataTextArea.Bind(wx.EVT_LEFT_UP, self.printCursorInfo)

        self.cursorInfoLabel = wx.StaticText(rightPanel, label="")

        rightPanelSizer.Add(self.dataTextArea, 1, wx.EXPAND)
        rightPanelSizer.Add(self.cursorInfoLabel, 0, wx.ALIGN_RIGHT)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(bPanel, 0, wx.ALL, 5)
        sizer.Add(rightPanel, 1, wx.ALL | wx.EXPAND, 5)

        # fill panel with linear gradient to make it look fancy
        self.Bind(wx.EVT_PAINT, self.OnPaintPrettyPanel)

        self.SetSizer(sizer)

        self.Layout()"""

    def OnPaintPrettyPanel(self, event):
        # establish the painting canvas
        dc = wx.PaintDC(self)
        x = 0
        y = 0
        w, h = self.GetSize()
        dc.GradientFillLinear((x, y, w, h), '#606060', '#E0E0E0', nDirection=wx.NORTH)

    def attachButtons(self, loadButton, saveButton):
        """ """
        loadButton.Bind(wx.EVT_BUTTON, self.onLoad)
        saveButton.Bind(wx.EVT_BUTTON, self.onSave)

    def onLoad(self, event):
        """ Load file to text area """
        ofdlg = wx.FileDialog(self, "Load file", "", "", "QoP-ML Files (*.qopml)|*.qopml",
                              wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        ofdlg.ShowModal()
        if ofdlg.GetPath():
            wildcard, types = wx.richtext.RichTextBuffer.GetExtWildcard(save=False)
            fileType = types[ofdlg.GetFilterIndex()]
            self.dataTextArea.LoadFile(ofdlg.GetPath(), fileType)
        ofdlg.Destroy()

    def onSave(self, event):
        """ Save text area value to file """
        ofdlg = wx.FileDialog(self, "Save file", "", "", "QoP-ML Files (*.qopml)|*.qopml",
                              wx.FD_SAVE)
        ofdlg.ShowModal()
        if ofdlg.GetPath():
            f = open(ofdlg.GetPath(), "w")
            f.write(self.dataTextArea.GetValue())
            f.close()
        ofdlg.Destroy()

    def printCursorInfo(self, event):
        """ """
        pos = self.dataTextArea.GetInsertionPoint()
        xy = self.dataTextArea.PositionToXY(pos)
        self.cursorInfoLabel.SetLabel("Line: %d, %d"
                                      % (xy[1]+1, xy[0]+1))
        self.Layout()
        event.Skip()