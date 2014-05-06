#!/usr/bin/env python

"""
@file       models_lib_gui.py
@brief      GUI for models library window (in python's nomenclature it's a wx frame)
@author     Damian Rusinek
@author     Katarzyna Mazur (visual improvements)
@date       created on 05-09-2013 by Damian Rusinek
@date       edited on 05-05-2014 by Katarzyna Mazur
"""

import os
import wx
import wx.richtext
import wx.lib.newevent

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
                        'root':         dir_root,
                        'name':         name_child.text,
                        'author':       author,
                        'author_email': author_email,
                        'description':  description,

                        'files': {
                            'model':    model_file,
                            'metrics':  metrics_file,
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
     @brief Create panel for displaying information about the chosen model
    """

    def __init__(self, *args, **kwargs):
        """
         @brief Initialize and align gui elements, init model's data
        """
        wx.Panel.__init__(self, *args, **kwargs)

        # class' data
        self.model_data = None

        # text area (text edit, disabled, not editable) to show model's description
        __txtStyle = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_AUTO_URL
        self.modelsDescriptionText = wx.TextCtrl(self, style = __txtStyle)

        # group boxes aka static boxes
        self.modelAboutBox = wx.StaticBox(self, label="About the model ...")
        self.modelsGeneralInfoBox = wx.StaticBox(self, label="General information")
        self.modelsDescriptionBox = wx.StaticBox(self, label="Description")
        self.modelsTreeBox = wx.StaticBox(self, label="Models library")

        # sizers = some kind of layout management
        modelAboutBoxSizer = wx.StaticBoxSizer(self.modelAboutBox, wx.VERTICAL)
        modelGeneralInfoBoxSizer = wx.StaticBoxSizer(self.modelsGeneralInfoBox, wx.VERTICAL)
        modelDescriptionBoxSizer = wx.StaticBoxSizer(self.modelsDescriptionBox, wx.VERTICAL)
        modelsTreeBoxSizer = wx.StaticBoxSizer(self.modelsTreeBox, wx.VERTICAL)

        # create buttons
        self.loadModelButton = wx.Button(self, label="Load model")
        self.loadModelButton.Hide()
        cancelButton = wx.Button(self, label="Close")

        # static texts aka labels
        moduleNameLabel = wx.StaticText(self, label="Name:   ")
        moduleAuthorsNameLabel = wx.StaticText(self, label="Author: ")
        moduleAuthorsEmailLabel = wx.StaticText(self, label="E-mail:  ")

        # font for static texts = same as default panel font, just bold
        defSysFont = self.GetFont()
        boldFont = wx.Font(pointSize=defSysFont.GetPointSize(),
                           family=defSysFont.GetFamily(),
                           style=defSysFont.GetStyle(),
                           weight=wx.FONTWEIGHT_BOLD)

        # static texts will we displayed in bold
        moduleNameLabel.SetFont(boldFont)
        moduleAuthorsNameLabel.SetFont(boldFont)
        moduleAuthorsEmailLabel.SetFont(boldFont)

        # editable static texts (labels) - will be modified
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
        sizer.Add(moduleNameLabel, 0, wx.ALL | wx.TOP, 5)
        sizer.AddSpacer(__verticalSpace)
        sizer.Add(self.moduleNameText, 0, wx.ALL | wx.TOP, 5)
        modelGeneralInfoBoxSizer.Add(sizer, 0, wx.LEFT)

        # align author label and author
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(moduleAuthorsNameLabel, 0, wx.ALL | wx.TOP, 5)
        sizer.AddSpacer(__verticalSpace)
        sizer.Add(self.moduleAuthorsNameText, 0, wx.ALL | wx.TOP, 5)
        modelGeneralInfoBoxSizer.Add(sizer, 0, wx.LEFT)

        # align email label and email
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(moduleAuthorsEmailLabel, 0, wx.ALL | wx.TOP, 5)
        sizer.AddSpacer(__verticalSpace)
        sizer.Add(self.moduleAuthorsEmailText, 0, wx.ALL | wx.TOP, 5)
        modelGeneralInfoBoxSizer.Add(sizer, 0, wx.LEFT)

        # add group box 'general model info' at the top of the 'model's about' group box
        modelAboutBoxSizer.Add(modelGeneralInfoBoxSizer, 0, wx.ALL | wx.TOP | wx.EXPAND, 10)

        # add text area to the 'model's description' group box
        modelDescriptionBoxSizer.Add(self.modelsDescriptionText, 1, wx.EXPAND | wx.TOP | wx.ALL, 5)

        # add 'model's description' group box to the 'model's about' group box
        modelAboutBoxSizer.Add(modelDescriptionBoxSizer, 1, wx.ALL | wx.TOP | wx.EXPAND, 10)

        # align buttons
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.loadModelButton, 0, wx.LEFT | wx.BOTTOM, 5)
        sizer.Add(cancelButton, 0, wx.LEFT | wx.BOTTOM, 5)
        # add buttons to 'about the model' group box
        modelAboutBoxSizer.Add(sizer, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)

        # align all the gui elements together on the panel
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(modelsTreeBoxSizer, 1, wx.ALL | wx.EXPAND) # or simply sizer.Add(modelsTreeBoxSizer, 0, wx.EXPAND)
        sizer.Add(modelAboutBoxSizer, 1, wx.EXPAND)

        self.SetSizer(sizer)
        self.Layout()

    def OnCancelClicked(self, event) :
        """
	     @brief closes the frame (as well as the panel)
	    """
        frame = self.GetParent()
        frame.Close()

    def ShowModel(self, model_data):
        """ """
        self.model_data = model_data
        self.moduleNameText.SetLabel(model_data['name'])
        self.moduleAuthorsNameText.SetLabel(model_data['author'])
        self.moduleAuthorsEmailText.SetLabel(model_data['author_email'])
        self.modelsDescriptionText.SetValue(model_data['description'])
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
                                 versions_data=versions_data)
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

        # fill panel with linear gradient to make it look fancy
        self.modelDescriptionPanel.Bind(wx.EVT_PAINT, self.OnPaintPrettyPanel)

        self.modelsTree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnModelSelected)
        self.modelsTree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnModelDoubleClicked)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.modelDescriptionPanel, 4, wx.EXPAND)
        self.SetSizer(sizer)

        # set minimum windows' size - you can make it bigger, but not smaller!
        self.SetMinSize(wx.Size(1000, 500))
        # center model's lib window on a screen
        self.Centre()
        self.Layout()

    def OnPaintPrettyPanel(self, event):
        # establish the painting canvas
        dc = wx.PaintDC(self.modelDescriptionPanel)
        x = 0
        y = 0
        w, h = self.GetSize()
        dc.GradientFillLinear((x, y, w, h), '#606060', '#E0E0E0',  nDirection=wx.NORTH)

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
                                     versions_data=versions_data)
            wx.PostEvent(self, evt)
            self.Close()

    def OnLoadModelSelected(self, event=None):
        """ """
        wx.PostEvent(self, event)
        self.Close()
