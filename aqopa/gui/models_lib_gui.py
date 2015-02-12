#!/usr/bin/env python

import os
import wx
import wx.richtext
import wx.lib.newevent

"""
@file       models_lib_gui.py
@brief      GUI for the  models library window (in python's nomenclature it's a wx frame)
@author     Damian Rusinek
@date       created on 05-09-2013 by Damian Rusinek
@date       edited on 05-05-2014 by Katarzyna Mazur (visual improvements)
"""

ModelSelectedEvent, EVT_MODEL_SELECTED = wx.lib.newevent.NewEvent()

class LibraryTree(wx.TreeCtrl):
    """ """

    def __init__(self, *args, **kwargs):
        wx.TreeCtrl.__init__(self, *args, **kwargs)

        models_item = self.AddRoot(text="Models")
        models_dir = os.path.join(os.path.dirname(__file__),
                                  os.pardir,
                                  'library',
                                  'models')

        import xml.etree.ElementTree as ET

        for dir_root, dirs, files in os.walk(models_dir):
            if 'meta.xml' in files:
                item_key = os.path.basename(dir_root)

                tree = ET.parse(os.path.join(dir_root, 'meta.xml'))
                root = tree.getroot()

                name_child = root.find('name')
                if name_child is not None:
                    item = self.AppendItem(models_item, text=name_child.text)

                    author = root.find('author').text if root.find('author') is not None else ''
                    author_email = root.find('author_email').text if root.find('author_email') is not None else ''
                    description = root.find('description').text if root.find('description') is not None else ''

                    model_file = ''
                    metrics_file = ''
                    versions_file = ''
                    files = root.find('files')
                    if files is not None:
                        model_file = files.find('model').text if files.find('model') is not None else ''
                        metrics_file = files.find('metrics').text if files.find('metrics') is not None else ''
                        versions_file = files.find('versions').text if files.find('versions') is not None else ''

                    model_data = {
                        'root': dir_root,
                        'name': name_child.text,
                        'author': author,
                        'author_email': author_email,
                        'description': description,

                        'files': {
                            'model': model_file,
                            'metrics': metrics_file,
                            'versions': versions_file,
                        }
                    }
                    self.SetPyData(item, model_data)
        self.ExpandAll()

    def GetModelData(self, item):
        """ """
        if item in self.items_data:
            return self.items_data[item]
        return None


class ModelDescriptionPanel(wx.Panel):
    """
     @brief Creates panel for displaying information about the chosen model
    """

    def __init__(self, *args, **kwargs):
        """
         @brief Initializes and aligns gui elements, inits model's data
        """
        wx.Panel.__init__(self, *args, **kwargs)

        # class' data
        self.model_data = None

        # create dicts for opened files [only for
        # those from models library]
        self.filenames = {}

        # create text area (text edit, disabled, not editable) to show model's description
        __txtStyle = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_AUTO_URL
        self.modelsDescriptionText = wx.TextCtrl(self, style=__txtStyle)

        # create group boxes aka static boxes
        self.modelAboutBox = wx.StaticBox(self, label="About the model ...")
        self.modelsGeneralInfoBox = wx.StaticBox(self, label="General information")
        self.modelsDescriptionBox = wx.StaticBox(self, label="Description")
        self.modelsTreeBox = wx.StaticBox(self, label="Models library", style=wx.SUNKEN_BORDER)

        # create sizers = some kind of layout management
        modelAboutBoxSizer = wx.StaticBoxSizer(self.modelAboutBox, wx.VERTICAL)
        modelGeneralInfoBoxSizer = wx.StaticBoxSizer(self.modelsGeneralInfoBox, wx.VERTICAL)
        modelDescriptionBoxSizer = wx.StaticBoxSizer(self.modelsDescriptionBox, wx.VERTICAL)
        modelsTreeBoxSizer = wx.StaticBoxSizer(self.modelsTreeBox, wx.VERTICAL)

        # create buttons
        self.loadModelButton = wx.Button(self, label="Load model")
        self.loadModelButton.Hide()
        cancelButton = wx.Button(self, label="Close")

        # create static texts aka labels
        moduleNameLabel = wx.StaticText(self, label="Name: ")
        moduleAuthorsNameLabel = wx.StaticText(self, label="Author: ")
        moduleAuthorsEmailLabel = wx.StaticText(self, label="E-mail: ")

        # create font for static texts = same as default panel font, just bold
        defSysFont = self.GetFont()
        boldFont = wx.Font(pointSize=defSysFont.GetPointSize(),
                           family=defSysFont.GetFamily(),
                           style=defSysFont.GetStyle(),
                           weight=wx.FONTWEIGHT_BOLD)

        # create static texts will we displayed in bold
        moduleNameLabel.SetFont(boldFont)
        moduleAuthorsNameLabel.SetFont(boldFont)
        moduleAuthorsEmailLabel.SetFont(boldFont)

        # create editable static texts (labels) - will be modified
        self.moduleNameText = wx.StaticText(self)
        self.moduleAuthorsNameText = wx.StaticText(self)
        self.moduleAuthorsEmailText = wx.StaticText(self)

        # do some bindings -
        # loadModelButton loads the chosen model to the text area
        self.loadModelButton.Bind(wx.EVT_LEFT_UP, self.OnLoadModelClicked)
        # cancelButton simply closes the model's lib window (frame)
        cancelButton.Bind(wx.EVT_BUTTON, self.OnCancelClicked)

        # create'n'align models lib tree
        self.modelsTree = LibraryTree(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.modelsTree, 1, wx.ALL | wx.EXPAND)
        modelsTreeBoxSizer.Add(sizer, 1, wx.ALL | wx.EXPAND, 5)

        # add some vertical space to make gui more readable
        __verticalSpace = 25

        # align name label and name
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(moduleNameLabel, 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(wx.StaticText(self), 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.moduleNameText, 1, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        modelGeneralInfoBoxSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        # align author label and author
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(moduleAuthorsNameLabel, 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(wx.StaticText(self), 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.moduleAuthorsNameText, 1, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        modelGeneralInfoBoxSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        # align email label and email
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(moduleAuthorsEmailLabel, 0, wx.ALL | wx.LEFT, 5)
        sizer.Add(wx.StaticText(self), 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.moduleAuthorsEmailText, 1, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        modelGeneralInfoBoxSizer.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)

        # add group box 'general model info' at the top of the 'model's about' group box
        modelAboutBoxSizer.Add(modelGeneralInfoBoxSizer, 0, wx.ALL | wx.TOP | wx.EXPAND, 10)

        # add text area to the 'model's description' group box
        modelDescriptionBoxSizer.Add(self.modelsDescriptionText, 1, wx.EXPAND | wx.TOP | wx.ALL, 5)

        # add 'model's description' group box to the 'model's about' group box
        modelAboutBoxSizer.Add(modelDescriptionBoxSizer, 1, wx.ALL | wx.TOP | wx.EXPAND, 10)

        # align buttons
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.loadModelButton, 0, wx.LEFT | wx.ALL, 5)
        sizer.Add(cancelButton, 0, wx.LEFT | wx.ALL, 5)
        # add buttons to 'about the model' group box
        modelAboutBoxSizer.Add(sizer, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)

        # align all the gui elements together on the panel
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(modelsTreeBoxSizer, 1, wx.ALL | wx.EXPAND)  # or simply sizer.Add(modelsTreeBoxSizer, 0, wx.EXPAND)
        sizer.Add(modelAboutBoxSizer, 1, wx.EXPAND)

        # do the final alignment
        self.SetSizer(sizer)
        self.Layout()

    def OnCancelClicked(self, event):
        """
	     @brief     closes the frame (as well as the panel)
	    """
        frame = self.GetParent()
        frame.Close()

    def __CreateLibraryPath(self, filename):
        """
        @brief      creates a filepath displayed on GUI,
                    the filepath is the path of the
                    model/metric/version chosen from
                    AQoPA's model library
        """
        __mainPath = os.path.split(self.model_data['root'])[0]
        for i in range (0,4):
            __mainPath = os.path.split(__mainPath)[0]
        __mainPath += "/library/models/"
        __chosenModelPath = os.path.split(self.model_data['root'])[1]
        __mainPath += __chosenModelPath
        __mainPath += "/"
        __mainPath += filename
        return __mainPath

    def ShowModel(self, model_data):
        """ """
        self.model_data = model_data
        self.moduleNameText.SetLabel(model_data['name'])
        self.moduleAuthorsNameText.SetLabel(model_data['author'])
        self.moduleAuthorsEmailText.SetLabel(model_data['author_email'])
        self.modelsDescriptionText.SetValue(model_data['description'])
        self.filenames['model'] = self.__CreateLibraryPath(os.path.split(self.model_data['files']['model'])[1])
        self.filenames['metrics'] = self.__CreateLibraryPath(os.path.split(self.model_data['files']['metrics'])[1])
        self.filenames['versions'] = self.__CreateLibraryPath(os.path.split(self.model_data['files']['versions'])[1])
        self.modelsDescriptionText.Show()
        self.loadModelButton.Show()
        self.Layout()

    def OnLoadModelClicked(self, event=None):
        """ """
        f = open(os.path.join(self.model_data['root'], self.model_data['files']['model']))
        model_data = f.read()
        f.close()

        f = open(os.path.join(self.model_data['root'], self.model_data['files']['metrics']))
        metrics_data = f.read()
        f.close()

        f = open(os.path.join(self.model_data['root'], self.model_data['files']['versions']))
        versions_data = f.read()
        f.close()

        evt = ModelSelectedEvent(model_data=model_data,
                                 metrics_data=metrics_data,
                                 versions_data=versions_data,
                                 filenames=self.filenames)
        wx.PostEvent(self, evt)


class LibraryFrame(wx.Frame):
    """ """

    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        ###################
        # SIZERS & EVENTS
        ###################

        self.modelDescriptionPanel = ModelDescriptionPanel(self)
        self.modelsTree = self.modelDescriptionPanel.modelsTree
        self.modelDescriptionPanel.Bind(EVT_MODEL_SELECTED, self.OnLoadModelSelected)

        # fill panel with linear gradient to make it look fancy = NOT NOW!
        #self.modelDescriptionPanel.Bind(wx.EVT_PAINT, self.OnPaintPrettyPanel)

        self.modelsTree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnModelSelected)
        self.modelsTree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnModelDoubleClicked)

        # set window's icon
        self.SetIcon(wx.Icon(self.CreatePath4Resource('models_lib.ico'), wx.BITMAP_TYPE_ICO))

        # set minimum windows' size - you can make it bigger, but not smaller!
        self.SetMinSize(wx.Size(800, 450))
        # do the final alignment
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.modelDescriptionPanel, 4, wx.EXPAND)
        self.SetSizer(sizer)
        # center model's lib window on a screen
        self.CentreOnParent()
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

    def GetFilenames(self):
        return self.modelDescriptionPanel.filenames

    def OnPaintPrettyPanel(self, event):
        # establish the painting canvas
        dc = wx.PaintDC(self.modelDescriptionPanel)
        x = 0
        y = 0
        w, h = self.GetSize()
        dc.GradientFillLinear((x, y, w, h), '#606060', '#E0E0E0', nDirection=wx.NORTH)

    def OnModelSelected(self, event=None):
        """ """
        itemID = event.GetItem()
        if not itemID.IsOk():
            itemID = self.tree.GetSelection()
        model_data = self.modelsTree.GetPyData(itemID)
        if model_data:
            self.modelDescriptionPanel.ShowModel(model_data)

    def OnModelDoubleClicked(self, event=None):
        """ """
        itemID = event.GetItem()
        if not itemID.IsOk():
            itemID = self.tree.GetSelection()
        model_info = self.modelsTree.GetPyData(itemID)
        if model_info:
            f = open(os.path.join(model_info['root'], model_info['files']['model']))
            model_data = f.read()
            f.close()

            f = open(os.path.join(model_info['root'], model_info['files']['metrics']))
            metrics_data = f.read()
            f.close()

            f = open(os.path.join(model_info['root'], model_info['files']['versions']))
            versions_data = f.read()
            f.close()

            evt = ModelSelectedEvent(model_data=model_data,
                                     metrics_data=metrics_data,
                                     versions_data=versions_data,
                                     filenames=self.GetFilenames())
            wx.PostEvent(self, evt)
            self.Close()

    def OnLoadModelSelected(self, event=None):
        """ """
        wx.PostEvent(self, event)
        self.Close()
