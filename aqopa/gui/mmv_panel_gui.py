#!/usr/bin/env python

import wx
import wx.richtext

"""
@file       mmv_panel_gui.py
@brief      GUI for the 'Model', 'Metrics' and 'Versions' tabs on AQoPA's main window (panel)
@author     Damian Rusinek <damian.rusinek@gmail.com>
@date       created on 05-09-2013 by Damian Rusinek
@date       edited on 06-05-2014 by Katarzyna Mazur (visual improvements mainly)
"""

class MMVPanel(wx.Panel):
    """
    @brief      panel containing text area (and buttons 2) for one of model parts:
                model, metrics, configuration, used for creating tabs on AQoPA's
                main window
    """

    def __init__(self, *args, **kwargs):
        """
         @brief         Initializes and aligns all the gui elements for
                        tabs: model, metrics and versions
        """
        wx.Panel.__init__(self, *args, **kwargs)

        # create group boxes aka static boxes
        self.tabBox = wx.StaticBox(self, label="File: ")

        # create sizers = some kind of layout management
        self.tabBoxSizer = wx.StaticBoxSizer(self.tabBox, wx.HORIZONTAL)

        # create text area; here we display model, metric or version content
        self.dataTextArea = wx.richtext.RichTextCtrl(self, style=wx.TE_MULTILINE | wx.TE_NO_VSCROLL)

        # create buttons - simple 'Load' and 'Save' will be enough
        self.loadButton = wx.Button(self, label="Load")
        self.saveButton = wx.Button(self, label="Save")
        # or add the 3rd button maybe? clears the
        # content of model/metric/version if clicked
        self.cleanButton = wx.Button(self, label="Clear")

        # create label 4 displaying information about the cursor
        # position in the opened file
        self.cursorInfoLabel = wx.StaticText(self)

        # create checkbox - make model/metric/version editable / not editable
        self.editable = wx.CheckBox(self, -1, label="Editable")

        # do some bindings -
        # show cursor position below the text area
        self.dataTextArea.Bind(wx.EVT_KEY_UP, self.printCursorInfo)
        self.dataTextArea.Bind(wx.EVT_LEFT_UP, self.printCursorInfo)
        # bind buttons to appropriate actions
        self.loadButton.Bind(wx.EVT_BUTTON, self.OnLoadClicked)
        self.saveButton.Bind(wx.EVT_BUTTON, self.OnSaveClicked)
        self.cleanButton.Bind(wx.EVT_BUTTON, self.OnCleanClicked)
        # bind checkbox state with the appropriate action - simply
        # allow / do not allow to edit opened model/metric/version
        self.editable.Bind(wx.EVT_CHECKBOX, self.OnCheckBoxClicked)

        # at first, we are not allowed to edit
        self.editable.SetValue(False)
        # pretend that we clicked the check box, so it's event gets called
        wx.PostEvent(self.editable, wx.CommandEvent(wx.wxEVT_COMMAND_CHECKBOX_CLICKED))

        # align buttons and the checkbox
        bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
        bottomSizer.Add(self.editable, 0, wx.EXPAND | wx.ALL, 5)
        # create empty static box (label) in order to make a horizontal
        # gap between the checkbox and the buttons
        bottomSizer.Add(wx.StaticText(self), 1, wx.EXPAND, 5)
        bottomSizer.Add(self.loadButton, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        bottomSizer.Add(self.saveButton, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        bottomSizer.Add(self.cleanButton, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # add some 'useful' tooltips
        self.loadButton.SetToolTip(wx.ToolTip("Load from HDD"))
        self.saveButton.SetToolTip(wx.ToolTip("Save to HDD"))
        self.cleanButton.SetToolTip(wx.ToolTip("Clear all"))

        # add text area to the fancy group box with a filename above the displayed file content
        self.tabBoxSizer.Add(self.dataTextArea, 1, wx.EXPAND | wx.ALL, 5)

        # do the final alignment
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tabBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.cursorInfoLabel, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(bottomSizer, 0, wx.EXPAND, 5)
        self.SetSizer(sizer)
        self.Layout()

    def OnLoadClicked(self, event):
        """ Load file to text area """
        ofdlg = wx.FileDialog(self, "Load file", "", "", "QoP-ML Files (*.qopml)|*.qopml",
                              wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        ofdlg.ShowModal()
        if ofdlg.GetPath():
            wildcard, types = wx.richtext.RichTextBuffer.GetExtWildcard(save=False)
            fileType = types[ofdlg.GetFilterIndex()]
            self.dataTextArea.LoadFile(ofdlg.GetPath(), fileType)
        self.SetFilenameOnGUI(ofdlg.GetPath())
        ofdlg.Destroy()

    def OnSaveClicked(self, event):
        """ Save text area value to file """
        ofdlg = wx.FileDialog(self, "Save file", "", "", "QoP-ML Files (*.qopml)|*.qopml",
                              wx.FD_SAVE)
        ofdlg.ShowModal()
        if ofdlg.GetPath() :
            # add *.qopml extension if not given
            validated = self.ValidateFilename(ofdlg.GetPath())
            f = open(validated, "w")
            f.write(self.dataTextArea.GetValue())
            f.close()
            # save on gui name of the saved file (with *.qopml) extension
            self.SetFilenameOnGUI(validated)
        ofdlg.Destroy()

    def OnCleanClicked(self, event):
        self.dataTextArea.SetValue("")

    def printCursorInfo(self, event):
        """ """
        pos = self.dataTextArea.GetInsertionPoint()
        xy = self.dataTextArea.PositionToXY(pos)
        self.cursorInfoLabel.SetLabel("Line: %d, %d"
                                      % (xy[1]+1, xy[0]+1))
        self.Layout()
        event.Skip()

    def OnPaintPrettyPanel(self, event):
        # establish the painting canvas
        dc = wx.PaintDC(self)
        x = 0
        y = 0
        w, h = self.GetSize()
        dc.GradientFillLinear((x, y, w, h), '#606060', '#E0E0E0', nDirection=wx.NORTH)

    def SetFilenameOnGUI(self, filename):
        """
        @brief      sets the title of the group box
                    to the opened/saved filename
        """
        self.tabBox.SetLabel("File: "+filename)

    def ValidateFilename(self, filename):
        """
        @brief      adds *.qopml extension to the file which
                    we want 2 save (but only if not given)
        @return     returns the validated filename
        """
        if filename.endswith(".qopml") :
            return filename
        else :
            filename += ".qopml"
            return filename

    def OnCheckBoxClicked(self, event):
        """
        @brief      checks if the checkbox is checked :D
                    if so, you can edit opened model/metric/version
                    if not, model/metric/version is not editable,
                    nah, just a fancy feature
        """
        if event.IsChecked() :
            self.dataTextArea.SetEditable(True)
        else :
            self.dataTextArea.SetEditable(False)