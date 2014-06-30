#!/usr/bin/env python

import wx
import os

# AQoPA imports
import aqopa

# AQoPA gui imports
from aqopa.gui.models_lib_gui import LibraryFrame, EVT_MODEL_SELECTED
from aqopa.gui.main_notebook_gui import MainNotebook

"""
@file       main_frame_gui.py
@brief      GUI for the main frame (the one with the tabs on it)
@author     Damian Rusinek <damian.rusinek@gmail.com>
@date       created on 05-09-2013 by Damian Rusinek
@date       edited on 07-05-2014 by Katarzyna Mazur (visual improvements)
"""

class MainFrame(wx.Frame):
    """ """
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        ###########
        # MENUBAR
        ###########

        # create menubar
        menuBar = wx.MenuBar()

        #create main menu, lets call it 'file' menu
        fileMenu = wx.Menu()
        # create menu item = about AQoPA
        item = wx.MenuItem(fileMenu, wx.NewId(), u"&About AQoPA\tCTRL+I")
        item.SetBitmap(wx.Bitmap(self.CreatePath4Resource('about.png')))
        fileMenu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnAbout, item)
        fileMenu.AppendSeparator()
        # create menu item = quit AQoPa
        item = wx.MenuItem(fileMenu, wx.NewId(), u"&Quit\tCTRL+Q")
        item.SetBitmap(wx.Bitmap(self.CreatePath4Resource('exit.png')))
        fileMenu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnQuit, item)
        # add 'file' menu to the menubar
        menuBar.Append(fileMenu, "&Menu")

        # create library menu, here u can find modules library
        libraryMenu = wx.Menu()
        # create models menu item
        item = wx.MenuItem(libraryMenu, wx.NewId(), u"&Browse models\tCTRL+M")
        item.SetBitmap(wx.Bitmap(self.CreatePath4Resource('models_lib.png')))
        libraryMenu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnBrowseModels, item)

        # create metric menu item
        item = wx.MenuItem(libraryMenu, wx.NewId(), u"&Browse metrics\tCTRL+F")
        item.SetBitmap(wx.Bitmap(self.CreatePath4Resource('metrics.png')))
        libraryMenu.AppendItem(item)

        # add 'library' menu to the menubar
        menuBar.Append(libraryMenu, "&Library")

        self.SetMenuBar(menuBar)

        ###################
        # SIZERS & EVENTS
        ###################

        self.mainNotebook = MainNotebook(self)

        logoPanel = wx.Panel(self)
        pic = wx.StaticBitmap(logoPanel)
        pic.SetBitmap(wx.Bitmap(self.CreatePath4Resource('logo.png')))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticText(self), 1, wx.EXPAND, 5)
        sizer.Add(logoPanel, 0, wx.RIGHT| wx.ALL|wx.EXPAND, 5)
        s2 = wx.BoxSizer(wx.VERTICAL)
        s2.Add(sizer, 0, wx.LEFT| wx.ALL|wx.EXPAND, 5)
        s2.Add(self.mainNotebook, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(s2)

        self.SetIcon(wx.Icon(self.CreatePath4Resource('app_logo.png'), wx.BITMAP_TYPE_PNG))
        self.SetMinSize(wx.Size(900, 700))
        self.CenterOnScreen()
        self.Layout()

    def CreatePath4Resource(self, resourceName):
        """
        @brief      creates and returns path to the
                    given file in the resource
                    ('assets') dir
        @return     path to the resource
        """
        tmp = os.path.split(os.path.dirname(__file__))
        return os.path.join(tmp[0], 'bin', 'assets', resourceName)

    def OnQuit(self, event=None):
        """
        @brief  closes the application
        """
        self.Close()

    def OnBrowseModels(self, event=None):
        """
        @brief  shows the library frame (models library window)
        """
        libraryFrame = LibraryFrame(self, title="Models Library")
        libraryFrame.Show(True)
        libraryFrame.CentreOnParent()
        #libraryFrame.Maximize(True)
        libraryFrame.Bind(EVT_MODEL_SELECTED, self.OnLibraryModelSelected)

    def OnLibraryModelSelected(self, event):
        """ """
        self.mainNotebook.SetModelData(event.model_data)
        self.mainNotebook.SetMetricsData(event.metrics_data)
        self.mainNotebook.SetVersionsData(event.versions_data)
        # set filenames on GUI
        self.mainNotebook.modelTab.SetFilenameOnGUI(event.filenames['model'])
        self.mainNotebook.metricsTab.SetFilenameOnGUI(event.filenames['metrics'])
        self.mainNotebook.versionsTab.SetFilenameOnGUI(event.filenames['versions'])

    def OnAbout(self, event=None):
        """ Show about info """

        description = """AQoPA stands for Automated Quality of Protection Analysis Tool
        for QoPML models."""

        licence = """AQoPA is free software; you can redistribute
it and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the License,
or (at your option) any later version.

AQoPA is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE."""

        logo_filepath = self.CreatePath4Resource('logo.png')

        info = wx.AboutDialogInfo()
        info.SetIcon(wx.Icon(logo_filepath, wx.BITMAP_TYPE_PNG))
        info.SetName('AQoPA')
        info.SetVersion(aqopa.VERSION)
        info.SetDescription(description)
        info.SetCopyright('(C) 2013 QoPML Project')
        info.SetWebSite('http://www.qopml.org')
        info.SetLicence(licence)
        info.AddDeveloper('Damian Rusinek')
        info.AddDocWriter('Damian Rusinek')
        info.AddArtist('QoPML Project')
        info.AddTranslator('Damian Rusinek')

        wx.AboutBox(info)