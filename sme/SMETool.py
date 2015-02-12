#!/usr/bin/env python
  
import sys
import wx
import wx.grid
import Utility
import Structs
import os

"""
@brief          Security Mechanisms Evaluation Tool
@file           SMETool.py
@author
@date
@date           edited on 01-07-2014 by Katarzyna Mazur (visual improvements mainly)
"""

#MODEL LIBRARY
class ModelLibraryDialog(wx.Dialog):

    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)

        # create txt ctrls
        self.modelDescTxtCtrl = wx.TextCtrl(self, wx.ID_ANY, "")
        self.modelDescTxtCtrl.SetEditable(False)
        self.modelDescTxtCtrl.AppendText("Model Description:")

        self.tree_ctrl_1 = wx.TreeCtrl(self, 2, style=wx.TR_HAS_BUTTONS | wx.TR_DEFAULT_STYLE | wx.SUNKEN_BORDER)

        self.loadModelBtn = wx.Button(self, 1, ("Load model"))
        self.Bind(wx.EVT_BUTTON, self.onClickLoadModel, id=1)
        root = self.tree_ctrl_1.AddRoot("Models:")
        self.tree_ctrl_1.AppendItem(root, "TLS cryptographic protocol")
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.onClickModelTreeNode, id=2)
        self.currentlySelected = ""

        self.__set_properties()
        self.__do_layout()

    def onClickLoadModel(self, e):
        if(self.currentlySelected=="TLS cryptographic protocol"):
            smetool.OnLoadAll(None)
            self.Close()

    def onClickModelTreeNode(self, e):
        self.currentlySelected = self.tree_ctrl_1.GetItemText(e.GetItem())
        if(self.currentlySelected=="TLS cryptographic protocol"):
            self.modelDescTxtCtrl.Clear()
            self.modelDescTxtCtrl.AppendText("TLS cryptographic protocol description")

    def __set_properties(self):
        self.SetTitle(("Model's Library"))
        self.SetClientSize(wx.Size(600, 400))

    def __do_layout(self):

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        groupBoxAll = wx.StaticBox(self, label="Model's Library")
        groupBoxAllSizer = wx.StaticBoxSizer(groupBoxAll, wx.HORIZONTAL)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.tree_ctrl_1, 1, wx.EXPAND, 5)

        descBox = wx.StaticBox(self, label="Model's Description")
        descBoxSizer = wx.StaticBoxSizer(descBox, wx.HORIZONTAL)
        descBoxSizer.Add(self.modelDescTxtCtrl, 1, wx.EXPAND, 5)

        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.EXPAND, 5)
        buttonsSizer.Add(self.loadModelBtn, 0, wx.EXPAND, 5)

        groupBoxAllSizer.Add(sizer1, 1, wx.ALL | wx.EXPAND, 5)
        groupBoxAllSizer.Add(descBoxSizer, 1, wx.ALL | wx.EXPAND, 5)

        mainSizer.Add(groupBoxAllSizer, 1, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(buttonsSizer, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(mainSizer)
        self.CentreOnParent()
        self.Layout()

################################################################## CATEGORY CLASSES ##################################################################
class AddCategoryDialog(wx.Dialog):

    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)

        # create labels
        self.label1 = wx.StaticText(self, wx.ID_ANY, ("Name:"))
        self.label_2 = wx.StaticText(self, wx.ID_ANY, ("Description:"))

        # create txt ctrls
        self.catTxtCtrl = wx.TextCtrl(self, wx.ID_ANY, "", size=(200,-1))
        self.catDescTxtCtrl = wx.TextCtrl(self, wx.ID_ANY, "", size=(200,-1))

        # create buttons
        self.addBtn = wx.Button(self, label="Add")
        self.cancelBtn = wx.Button(self, label="Cancel")

        # do some buttons-bindings
        self.addBtn.Bind(wx.EVT_BUTTON, self.onClickAdd)
        self.cancelBtn.Bind(wx.EVT_BUTTON, self.onClickCancel)

        self.__set_properties()
        self.__do_layout()

    def onClickAdd(self, e):
        flag = True
        category = Structs.Category(self.catTxtCtrl.GetValue(),self.catDescTxtCtrl.GetValue())
        for cat_item in Structs.categoryList:
            if(category.name==cat_item.name):
                flag = False
        if(flag):
            Structs.categoryList.append(category)
        else:
            SMETool.ShowMessage(smetool, "Duplicate!")
            return
        SMETool.populatelctrl1(smetool, Structs.categoryList)
        self.Close()

    def onClickCancel(self, e):
        self.Close()

    def __set_properties(self):
        self.SetTitle(("Add a Category"))
        self.SetSize((365, 216))

    def __do_layout(self):

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        groupBox = wx.StaticBox(self, label="Add the Category")
        groupBoxSizer = wx.StaticBoxSizer(groupBox, wx.VERTICAL)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.label1, 0, wx.ALIGN_LEFT, 5)
        sizer1.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer1.Add(self.catTxtCtrl, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.label_2, 0, wx.ALIGN_LEFT, 5)
        sizer2.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer2.Add(self.catDescTxtCtrl, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        buttonsSizer.Add(self.addBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)
        buttonsSizer.Add(self.cancelBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)

        groupBoxSizer.Add(sizer1, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer2, 0, wx.EXPAND | wx.ALL, 5)

        mainSizer.Add(groupBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
        mainSizer.Add(buttonsSizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(mainSizer)
        self.CentreOnParent()
        self.Layout()

class EditCategoryDialog(wx.Dialog):

    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.index = smetool.categoriesListView.GetFocusedItem()

        # create labels
        self.label1 = wx.StaticText(self, wx.ID_ANY, ("Name:"))
        self.label_2 = wx.StaticText(self, wx.ID_ANY, ("Description:"))

        #create text ctrls
        self.catNameTxtCtrl = wx.TextCtrl(self, wx.ID_ANY, Structs.categoryList[self.index].name, size=(200,-1))
        self.catDescTxtCtrl = wx.TextCtrl(self, wx.ID_ANY, Structs.categoryList[self.index].description, size=(200,-1))

        # create buttons
        self.applyBtn = wx.Button(self, label="Apply")
        self.cancelBtn = wx.Button(self, label="Cancel")

        # do some buttons bindings
        self.applyBtn.Bind(wx.EVT_BUTTON, self.onClickApply)
        self.cancelBtn.Bind(wx.EVT_BUTTON, self.onClickCancel)

        self.__set_properties()
        self.__do_layout()

    def onClickApply(self, e):
        flag = True
        category = Structs.Category(self.catNameTxtCtrl.GetValue(),self.catDescTxtCtrl.GetValue())
        for cat_item in Structs.categoryList:
            if(category.name==cat_item.name):
                flag = False
        if(flag or Structs.categoryList[self.index].name==category.name):
            i=-1
            for fact in Structs.factList:
                i=i+1
                if(Structs.categoryList[self.index].name==fact.category):
                    Structs.factList[i].category = category.name
                    SMETool.onFactChange(smetool, Structs.factList[i].name+'('+Structs.categoryList[self.index].name+')', Structs.factList[i].name+'('+fact.category+')')
                    SMETool.populatelctrl2(smetool, Structs.factList)
            del Structs.categoryList[self.index]
            Structs.categoryList.append(category)
        else:
            SMETool.ShowMessage(smetool, "Duplicate!")
        SMETool.populatelctrl1(smetool, Structs.categoryList)
        self.Close()

    def onClickCancel(self, e):
        self.Close()

    def __set_properties(self):
        self.SetTitle(("Edit the Category"))
        self.SetSize((365, 216))

    def __do_layout(self):

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        groupBox = wx.StaticBox(self, label="Edit the Category")
        groupBoxSizer = wx.StaticBoxSizer(groupBox, wx.VERTICAL)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.label1, 0, wx.ALIGN_LEFT, 5)
        sizer1.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer1.Add(self.catNameTxtCtrl, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.label_2, 0, wx.ALIGN_LEFT, 5)
        sizer2.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer2.Add(self.catDescTxtCtrl, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        buttonsSizer.Add(self.applyBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)
        buttonsSizer.Add(self.cancelBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)

        groupBoxSizer.Add(sizer1, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer2, 0, wx.EXPAND | wx.ALL, 5)

        mainSizer.Add(groupBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
        mainSizer.Add(buttonsSizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(mainSizer)
        self.CentreOnParent()
        self.Layout()
################################################################## CATEGORY CLASSES ##################################################################

################################################################## FACT CLASSES ##################################################################
class AddFactDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)

        # create labels
        self.label1 = wx.StaticText(self, wx.ID_ANY, ("Name:"))
        self.label_2 = wx.StaticText(self, wx.ID_ANY, ("Category:"))
        self.label_3 = wx.StaticText(self, wx.ID_ANY, ("Description:"))
        self.label_4 = wx.StaticText(self, wx.ID_ANY, ("Value:"))

        # create txt ctrls
        self.factNameTxtCtrl = wx.TextCtrl(self, wx.ID_ANY, "", size=(200,-1))
        self.factNameTxtCtrl.Disable()
        self.factDescTxtCtrl = wx.TextCtrl(self, wx.ID_ANY, "", size=(200,-1))
        self.factValTxtCtrl = wx.TextCtrl(self, wx.ID_ANY, "", size=(200,-1))

        # create combo
        self.factCatComboBox = wx.ComboBox(self, wx.ID_ANY, choices=self.catlist(), style=wx.CB_DROPDOWN|wx.TE_READONLY, size=(200,-1))

        # create buttons
        self.addBtn = wx.Button(self, label="Add")
        self.cancelBtn = wx.Button(self, label="Cancel")

        # do some buttons-bindings
        self.addBtn.Bind(wx.EVT_BUTTON, self.onClickAdd)
        self.cancelBtn.Bind(wx.EVT_BUTTON, self.onClickCancel)

        self.__set_properties()
        self.__do_layout()

    def onClickAdd(self, e):
        flag = True
        if(self.factCatComboBox.GetValue()==''):
            SMETool.ShowMessage(smetool, "Category can't be empty!")
            return
        f = 1
        fact_name = 'f%d' % (f,)
        if Structs.factList:
            while(flag):
                for item in Structs.factList:
                    if(item.category==self.factCatComboBox.GetValue()):
                        if(fact_name==item.name):
                            f=f+1
                            fact_name = 'f%d' % (f,)
                            flag = True
                            break
                        else:
                            flag = False
                    else:
                        flag = False
        flag = True
        fact = Structs.Fact(fact_name,self.factCatComboBox.GetValue(),self.factDescTxtCtrl.GetValue(),self.factValTxtCtrl.GetValue())
        for fact_item in Structs.factList:
            if(fact.name+fact.category==fact_item.name+fact_item.category):
                flag = False
        if(flag):
            Structs.factList.append(fact)
        else:
            SMETool.ShowMessage(smetool, "Duplicate!")
            return
        SMETool.populatelctrl2(smetool, Structs.factList)
        self.Close()

    def onClickCancel(self, e):
        self.Close()

    def catlist(self):
        somelist = []
        [somelist.append(category.name) for category in Structs.categoryList]
        return somelist

    def __set_properties(self):
        self.SetTitle(("Add a Fact"))
        self.SetSize((365, 316))

    def __do_layout(self):

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        groupBox = wx.StaticBox(self, label="Add a Fact")
        groupBoxSizer = wx.StaticBoxSizer(groupBox, wx.VERTICAL)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.label1, 0, wx.ALIGN_LEFT, 5)
        sizer1.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer1.Add(self.factNameTxtCtrl, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.label_2, 0, wx.ALIGN_LEFT, 5)
        sizer2.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer2.Add(self.factCatComboBox, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3.Add(self.label_3, 0, wx.ALIGN_LEFT, 5)
        sizer3.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer3.Add(self.factDescTxtCtrl, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer4.Add(self.label_4, 0, wx.ALIGN_LEFT, 5)
        sizer4.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer4.Add(self.factValTxtCtrl, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        buttonsSizer.Add(self.addBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)
        buttonsSizer.Add(self.cancelBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)

        groupBoxSizer.Add(sizer1, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer2, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer3, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer4, 0, wx.EXPAND | wx.ALL, 5)

        mainSizer.Add(groupBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
        mainSizer.Add(buttonsSizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(mainSizer)
        self.CentreOnParent()
        self.Layout()

class EditFactDialog(wx.Dialog):

    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.index = smetool.factsListView.GetFocusedItem()

        # create labels
        self.label1 = wx.StaticText(self, wx.ID_ANY, ("Name:"))
        self.label_2 = wx.StaticText(self, wx.ID_ANY, ("Category:"))
        self.label_3 = wx.StaticText(self, wx.ID_ANY, ("Description:"))
        self.label_4 = wx.StaticText(self, wx.ID_ANY, ("Value:"))

        # create text ctrls
        self.factNameTxtCtrl = wx.TextCtrl(self, wx.ID_ANY, Structs.factList[self.index].name, size=(200,-1))
        self.factDescTxtCtrl = wx.TextCtrl(self, wx.ID_ANY, Structs.factList[self.index].description, size=(200,-1))
        self.factValTxtCtrl = wx.TextCtrl(self, wx.ID_ANY, Structs.factList[self.index].value, size=(200,-1))

        # create combo
        self.factCatComboBox = wx.ComboBox(self, wx.ID_ANY, choices=self.catlist(), style=wx.CB_DROPDOWN|wx.TE_READONLY, size=(200,-1))
        self.factCatComboBox.SetValue(Structs.factList[self.index].category)

        # create buttons
        self.applyBtn = wx.Button(self, label="Apply")
        self.cancelBtn = wx.Button(self, label="Cancel")

        # do some buttons-bindings
        self.applyBtn.Bind(wx.EVT_BUTTON, self.onClickApply)
        self.cancelBtn.Bind(wx.EVT_BUTTON, self.onClickCancel)

        self.__set_properties()
        self.__do_layout()

    def onClickApply(self, e):
        flag = True
        fact = Structs.Fact(self.factNameTxtCtrl.GetValue(),self.factCatComboBox.GetValue(),self.factDescTxtCtrl.GetValue(),self.factValTxtCtrl.GetValue())
        for fact_item in Structs.factList:
            if(fact.name+fact.category==Structs.factList[self.index].name+Structs.factList[self.index].category):
                break
            else:
                if(fact.name+fact.category==fact_item.name+fact_item.category):
                    flag = False
                    break
        if(flag):
                SMETool.onFactChange(smetool, Structs.factList[self.index].name+'('+Structs.factList[self.index].category+')', fact.name+'('+fact.category+')')
                del Structs.factList[self.index]
                Structs.factList.append(fact)
        else:
            SMETool.ShowMessage(smetool, "Duplicate!")
        SMETool.populatelctrl2(smetool, Structs.factList)
        self.Close()

    def onClickCancel(self, e):
        self.Close()

    def catlist(self):
        somelist = []
        [somelist.append(category.name) for category in Structs.categoryList]
        return somelist

    def __set_properties(self):
        self.SetTitle(("Edit the Fact"))
        self.SetSize((365, 316))

    def __do_layout(self):

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        groupBox = wx.StaticBox(self, label="Edit the Fact")
        groupBoxSizer = wx.StaticBoxSizer(groupBox, wx.VERTICAL)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.label1, 0, wx.ALIGN_LEFT, 5)
        sizer1.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer1.Add(self.factNameTxtCtrl, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.label_2, 0, wx.ALIGN_LEFT, 5)
        sizer2.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer2.Add(self.factCatComboBox, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3.Add(self.label_3, 0, wx.ALIGN_LEFT, 5)
        sizer3.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer3.Add(self.factDescTxtCtrl, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer4.Add(self.label_4, 0, wx.ALIGN_LEFT, 5)
        sizer4.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer4.Add(self.factValTxtCtrl, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        buttonsSizer.Add(self.applyBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)
        buttonsSizer.Add(self.cancelBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)

        groupBoxSizer.Add(sizer1, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer2, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer3, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer4, 0, wx.EXPAND | wx.ALL, 5)

        mainSizer.Add(groupBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
        mainSizer.Add(buttonsSizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(mainSizer)
        self.CentreOnParent()
        self.Layout()

class ViewFactsDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)

        # create list box
        self.list_box_1 = wx.ListBox(self, wx.ID_ANY, choices=self.populateFactView())

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetSize((574, 826))
        self.list_box_1.SetMinSize((550, 788))

    def __do_layout(self):

        groupBox = wx.StaticBox(self, label="All Available Facts")
        groupBoxSizer = wx.StaticBoxSizer(groupBox, wx.VERTICAL)

        groupBoxSizer.Add(self.list_box_1, 1, wx.EXPAND, 5)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(groupBoxSizer, 1, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(mainSizer)
        self.CentreOnParent()
        self.Layout()

    def populateFactView(self):
        somelist = []
        somelist.append("")
        for category in Structs.categoryList:
            somelist.append("Category name: "+category.name+" ("+category.description+")")
            for fact in Structs.factList:
                if(fact.category==category.name):
                    somelist.append(fact.name+"("+fact.category+") = "+fact.value)
            somelist.append("")
        return somelist

################################################################## FACT CLASSES ##################################################################

################################################################## SECURITY ATTRIBUTE CLASSES ##################################################################
class AddSADialog(wx.Dialog):

    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)

        #create labels
        self.label1 = wx.StaticText(self, wx.ID_ANY, ("Name:"))
        self.label_2 = wx.StaticText(self, wx.ID_ANY, ("Description:"))

        # create text ctrls
        self.SAName = wx.TextCtrl(self, wx.ID_ANY, "", size=(200, -1))
        self.SADesc = wx.TextCtrl(self, wx.ID_ANY, "", size=(200, -1))

        #create buttons
        self.addBtn = wx.Button(self, label="Add")
        self.cancelBtn = wx.Button(self, label="Cancel")

        # do some buttons-bindings
        self.addBtn.Bind(wx.EVT_BUTTON, self.onClickAdd)
        self.cancelBtn.Bind(wx.EVT_BUTTON, self.onClickCancel)

        self.__set_properties()
        self.__do_layout()

    def onClickAdd(self, e):
        flag = True
        sa = Structs.SecurityAttribute(self.SAName.GetValue(),self.SADesc.GetValue())
        for sa_item in Structs.saList:
            if(sa.name==sa_item.name):
                flag = False
        if(flag):
            Structs.saList.append(sa)
        else:
            SMETool.ShowMessage(smetool, "Duplicate!")
            return
        SMETool.populatelctrl3(smetool, Structs.saList)
        self.Close()

    def onClickCancel(self, e):
        self.Close()

    def __set_properties(self):
        self.SetTitle(("Add a Security Attribute"))
        self.SetSize((365, 216))

    def __do_layout(self):

        groupBox = wx.StaticBox(self, label="Add a Security Attribute")
        groupBoxSizer = wx.StaticBoxSizer(groupBox, wx.VERTICAL)

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.label1, 0, wx.ALIGN_LEFT, 5)
        sizer1.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer1.Add(self.SAName, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.label_2, 0, wx.ALIGN_LEFT, 5)
        sizer2.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer2.Add(self.SADesc, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        buttonsSizer.Add(self.addBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)
        buttonsSizer.Add(self.cancelBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)

        groupBoxSizer.Add(sizer1, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer2, 0, wx.EXPAND | wx.ALL, 5)

        mainSizer.Add(groupBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
        mainSizer.Add(buttonsSizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(mainSizer)
        self.CentreOnParent()
        self.Layout()

class EditSADialog(wx.Dialog):

    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.index = smetool.SAListView.GetFocusedItem()

        # create labels
        self.label1 = wx.StaticText(self, wx.ID_ANY, ("Name:"))
        self.label_2 = wx.StaticText(self, wx.ID_ANY, ("Description:"))

        #create txt ctrls
        self.SANameTxtCtrl = wx.TextCtrl(self, wx.ID_ANY, Structs.saList[self.index].name, size=(200,-1))
        self.SADescTxtCtrl = wx.TextCtrl(self, wx.ID_ANY, Structs.saList[self.index].description, size=(200,-1))

        # create buttons
        self.applyBtn = wx.Button(self, label="Apply")
        self.cancelBtn = wx.Button(self, label="Cancel")

        # do some buttons-bindings
        self.applyBtn.Bind(wx.EVT_BUTTON, self.onClickApply)
        self.cancelBtn.Bind(wx.EVT_BUTTON, self.onClickCancel)

        self.__set_properties()
        self.__do_layout()

    def onClickApply(self, e):
        flag = True
        sa = Structs.SecurityAttribute(self.SANameTxtCtrl.GetValue(),self.SADescTxtCtrl.GetValue())
        for sa_item in Structs.saList:
            if(sa.name==Structs.saList[self.index].name):
                break
            else:
                if(sa.name==sa_item.name):
                    flag = False
                    break
        if(flag):
            indexi = 0
            for item in Structs.foList:
                if(item.security_attribute==Structs.saList[smetool.SAListView.GetFocusedItem()].name):
                    Structs.foList[indexi].security_attribute=sa.name
                    SMETool.populatelctrl6(smetool, Structs.foList)
            indexi=indexi+1
            indexi = 0
            for item in Structs.erList:
                if(item.security_attribute==Structs.saList[smetool.SAListView.GetFocusedItem()].name):
                    Structs.erList[indexi].security_attribute=sa.name
                    SMETool.populatelctrl10(smetool, Structs.erList)
                    indexi=indexi+1
            del Structs.saList[self.index]
            Structs.saList.append(sa)
        else:
            SMETool.ShowMessage(smetool, "Duplicate!")
        SMETool.populatelctrl3(smetool, Structs.saList)
        self.Close()

    def onClickCancel(self, e):
        self.Close()

    def __set_properties(self):
        self.SetTitle(("Edit the Security Attribute"))
        self.SetSize((365, 216))

    def __do_layout(self):

        groupBox = wx.StaticBox(self, label="Edit the Security Attribute")
        groupBoxSizer = wx.StaticBoxSizer(groupBox, wx.VERTICAL)

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.label1, 0, wx.ALIGN_LEFT, 5)
        sizer1.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer1.Add(self.SANameTxtCtrl, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.label_2, 0, wx.ALIGN_LEFT, 5)
        sizer2.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer2.Add(self.SADescTxtCtrl, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        buttonsSizer.Add(self.applyBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)
        buttonsSizer.Add(self.cancelBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)

        groupBoxSizer.Add(sizer1, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer2, 0, wx.EXPAND | wx.ALL, 5)

        mainSizer.Add(groupBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
        mainSizer.Add(buttonsSizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(mainSizer)
        self.CentreOnParent()
        self.Layout()
################################################################## SECURITY ATTRIBUTE CLASSES ##################################################################

################################################################## RULE CLASSES ##################################################################
class AddRuleDialog(wx.Dialog):
    
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)

        self.list_box_1 = wx.ListBox(self, wx.ID_ANY, choices=[])
        
        # create labels
        self.label_1 = wx.StaticText(self, wx.ID_ANY, ("Choose fact category:"))
        self.label_2 = wx.StaticText(self, wx.ID_ANY, ("Choose fact:"))
        
        # create buttons
        self.AND_Btn = wx.Button(self, label="AND")
        self.OR_Btn = wx.Button(self, label="OR")
        self.NEG_Btn = wx.Button(self, label="NEG")
        self.IMPLY_Btn = wx.Button(self, label="IMPLY")
        self.addRuleBtn = wx.Button(self, label="Add")
        self.undoRuleBtn = wx.Button(self, label="Undo")
        self.completeRuleBtn = wx.Button(self, label="Complete")

        # do some buttons-bindings
        self.AND_Btn.Bind(wx.EVT_BUTTON, self.onClickAND)
        self.OR_Btn.Bind(wx.EVT_BUTTON, self.onClickOR)
        self.NEG_Btn.Bind(wx.EVT_BUTTON, self.onClickNEG)
        self.IMPLY_Btn.Bind(wx.EVT_BUTTON, self.onClickIMPLY)
        self.addRuleBtn.Bind(wx.EVT_BUTTON, self.onClickAdd)
        self.undoRuleBtn.Bind(wx.EVT_BUTTON, self.onClickUndo)
        self.completeRuleBtn.Bind(wx.EVT_BUTTON, self.onClickComplete)

        # create combo boxes
        self.factCatComboBox = wx.ComboBox(self, 10, choices=self.catlist(), style=wx.CB_DROPDOWN|wx.TE_READONLY, size=(200, -1))
        self.combo_box_2 = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN|wx.TE_READONLY, size=(200, -1))
        self.combo_box_2.Disable()

        # do some combo-bindings
        self.Bind(wx.EVT_COMBOBOX, self.OnSelect1, id=10)

        self.__set_properties()
        self.__do_layout()

    def catlist(self):
        somelist = []
        [somelist.append(category.name) for category in Structs.categoryList]
        return somelist

    def factlist(self, cat):
        somelist = []
        [somelist.append(fact.value) for fact in Structs.factList if(fact.category==cat)]
        return somelist

    def OnSelect1(self, e):
        self.combo_box_2.Enable()
        self.combo_box_2.SetItems(self.factlist(self.factCatComboBox.GetValue()))

    def onClickAND(self, e):
        self.list_box_1.Append(Structs.AND)

    def onClickOR(self, e):
        self.list_box_1.Append(Structs.OR)

    def onClickNEG(self, e):
        self.list_box_1.Append(Structs.NEG)

    def onClickIMPLY(self, e):
        self.list_box_1.Append(Structs.IMPLY)

    def onClickAdd(self, e):
        if self.list_box_1.GetItems():
            if(self.list_box_1.GetItems()[-1] == Structs.NEG):
                self.list_box_1.Delete(len(self.list_box_1.GetItems())-1)
                self.list_box_1.Append(Structs.NEG+self.combo_box_2.GetValue()+"("+self.factCatComboBox.GetValue()+")")
            else:
                self.list_box_1.Append(self.combo_box_2.GetValue()+"("+self.factCatComboBox.GetValue()+")")
        else:
            self.list_box_1.Append(self.combo_box_2.GetValue()+"("+self.factCatComboBox.GetValue()+")")

    def onClickUndo(self, e):
        index = self.list_box_1.GetCount()
        self.list_box_1.Delete(index-1)

    def onClickComplete(self, e):
        Structs.ruleList.append(Structs.Rule(self.list_box_1.GetItems()))
        SMETool.populatelctrl4(smetool, Structs.ruleList)
        self.Close()

    def __set_properties(self):
        self.SetTitle(("Create a Rule"))
        self.SetSize((708, 500))
        self.list_box_1.SetMinSize((574, 300))

    def __do_layout(self):

        groupBox = wx.StaticBox(self, label="Create a Rule")
        groupBoxSizer = wx.StaticBoxSizer(groupBox, wx.VERTICAL)

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.label_1, 0, wx.ALIGN_LEFT, 5)
        sizer1.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer1.Add(self.factCatComboBox, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.label_2, 0, wx.ALIGN_LEFT, 5)
        sizer2.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer2.Add(self.combo_box_2, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer3.Add(self.AND_Btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer3.Add(self.OR_Btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer3.Add(self.NEG_Btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer3.Add(self.IMPLY_Btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer3.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)

        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        buttonsSizer.Add(self.addRuleBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)
        buttonsSizer.Add(self.undoRuleBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)
        buttonsSizer.Add(self.completeRuleBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)

        groupBoxSizer.Add(self.list_box_1, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer1, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer2, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer3, 0, wx.EXPAND | wx.ALL, 5)

        mainSizer.Add(groupBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
        mainSizer.Add(buttonsSizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(mainSizer)
        self.CentreOnParent()
        self.Layout()

class EditRuleDialog(wx.Dialog):

    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)

        self.list_box_1 = wx.ListBox(self, wx.ID_ANY, choices=self.fillListBox())
        self.label_1 = wx.StaticText(self, wx.ID_ANY, ("Choose Fact Category:"))
        self.label_2 = wx.StaticText(self, wx.ID_ANY, ("Choose Fact:"))

        self.factCatComboBox = wx.ComboBox(self, 10, choices=self.catlist(), style=wx.CB_DROPDOWN|wx.TE_READONLY, size=(200, -1))
        self.Bind(wx.EVT_COMBOBOX, self.OnSelect1, id=10)
        self.combo_box_2 = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN|wx.TE_READONLY, size=(200, -1))
        self.combo_box_2.Disable()

        # create buttons
        self.IMPLY_Btn = wx.Button(self, label="IMPLY")
        self.AND_Btn = wx.Button(self, label="AND")
        self.OR_Btn = wx.Button(self, label="OR")
        self.NEG_Btn = wx.Button(self, label="NEG")
        self.addRuleBtn = wx.Button(self, label="Add")
        self.undoRuleBtn = wx.Button(self, label="Undo")
        self.completeRuleBtn = wx.Button(self, label="Complete")

        # do some buttons-bindings
        self.AND_Btn.Bind(wx.EVT_BUTTON, self.onClickAND)
        self.OR_Btn.Bind(wx.EVT_BUTTON, self.onClickOR)
        self.NEG_Btn.Bind(wx.EVT_BUTTON, self.onClickNEG)
        self.IMPLY_Btn.Bind(wx.EVT_BUTTON, self.onClickIMPLY)
        self.addRuleBtn.Bind(wx.EVT_BUTTON, self.onClickAdd)
        self.undoRuleBtn.Bind(wx.EVT_BUTTON, self.onClickUndo)
        self.completeRuleBtn.Bind(wx.EVT_BUTTON, self.onClickComplete)

        self.__set_properties()
        self.__do_layout()

    def fillListBox(self):
        somelist = []
        for ele in Structs.ruleList[smetool.ruleListView.GetFocusedItem()].elements:
            somelist.append(ele)
        return somelist

    def catlist(self):
        somelist = []
        for category in Structs.categoryList:
            somelist.append(category.name)
        return somelist

    def factlist(self, cat):
        somelist = []
        for fact in Structs.factList:
            if(fact.category==cat):
                somelist.append(fact.value)
        return somelist

    def OnSelect1(self, e):
        self.combo_box_2.Enable()
        self.combo_box_2.SetItems(self.factlist(self.factCatComboBox.GetValue()))

    def onClickAND(self, e):
        self.list_box_1.Append(Structs.AND)

    def onClickOR(self, e):
        self.list_box_1.Append(Structs.OR)

    def onClickNEG(self, e):
        self.list_box_1.Append(Structs.NEG)

    def onClickIMPLY(self, e):
        self.list_box_1.Append(Structs.IMPLY)

    def onClickAdd(self, e):
        self.list_box_1.Append(self.combo_box_2.GetValue()+"("+self.factCatComboBox.GetValue()+")")

    def onClickUndo(self, e):
        index = self.list_box_1.GetCount()
        self.list_box_1.Delete(index-1)

    def onClickComplete(self, e):
        del Structs.ruleList[smetool.ruleListView.GetFocusedItem()]
        Structs.ruleList.append(Structs.Rule(self.list_box_1.GetItems()))
        SMETool.populatelctrl4(smetool, Structs.ruleList)
        self.Close()

    def __set_properties(self):
        self.SetTitle(("Edit the Rule"))
        self.SetSize((708, 500))
        self.list_box_1.SetMinSize((574, 300))

    def __do_layout(self):

        groupBox = wx.StaticBox(self, label="Edit the Rule")
        groupBoxSizer = wx.StaticBoxSizer(groupBox, wx.VERTICAL)

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.label_1, 0, wx.ALIGN_LEFT, 5)
        sizer1.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer1.Add(self.factCatComboBox, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.label_2, 0, wx.ALIGN_LEFT, 5)
        sizer2.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer2.Add(self.combo_box_2, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer3.Add(self.AND_Btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer3.Add(self.OR_Btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer3.Add(self.NEG_Btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer3.Add(self.IMPLY_Btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer3.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)

        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        buttonsSizer.Add(self.addRuleBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)
        buttonsSizer.Add(self.undoRuleBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)
        buttonsSizer.Add(self.completeRuleBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)

        groupBoxSizer.Add(self.list_box_1, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer1, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer2, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer3, 0, wx.EXPAND | wx.ALL, 5)

        mainSizer.Add(groupBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
        mainSizer.Add(buttonsSizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(mainSizer)
        self.CentreOnParent()
        self.Layout()

################################################################## RULE CLASSES ##################################################################

#FACTS ORDER
class AddFODialog(wx.Dialog):

    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)

        self.list_box_1 = wx.ListBox(self, wx.ID_ANY, choices=[])
        self.label_1 = wx.StaticText(self, wx.ID_ANY, ("Choose Fact Category:"))
        self.label_2 = wx.StaticText(self, wx.ID_ANY, ("Choose Fact:"))
        self.label_3 = wx.StaticText(self, wx.ID_ANY, ("Choose Security Attribute:"))

        self.factCatComboBox = wx.ComboBox(self, 10, choices=self.catlist(), style=wx.CB_DROPDOWN|wx.TE_READONLY, size=(200, -1))
        self.Bind(wx.EVT_COMBOBOX, self.OnSelect1, id=10)
        self.combo_box_2 = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN, size=(200, -1))
        self.combo_box_2.Disable()
        self.combo_box_3 = wx.ComboBox(self, wx.ID_ANY, choices=self.securitylist(), style=wx.CB_DROPDOWN|wx.TE_READONLY, size=(200, -1))

        # create buttons
        self.addFactsOrderBtn = wx.Button(self, label="Add")
        self.undoFactsOrderBtn = wx.Button(self, label="Undo")
        self.completeFactsOrderBtn = wx.Button(self,label="Complete")
        self.AND_Btn = wx.Button(self, label="LESSER")
        self.OR_Btn = wx.Button(self, label="GREATER")
        self.NEG_Btn = wx.Button(self, label="EQUALS")

        # do some buttons-bindings
        self.addFactsOrderBtn.Bind(wx.EVT_BUTTON, self.onClickAdd)
        self.undoFactsOrderBtn.Bind(wx.EVT_BUTTON, self.onClickUndo)
        self.completeFactsOrderBtn.Bind(wx.EVT_BUTTON, self.onClickComplete)
        self.AND_Btn.Bind(wx.EVT_BUTTON, self.onClickLESSER)
        self.OR_Btn.Bind(wx.EVT_BUTTON, self.onClickGREATER)
        self.NEG_Btn.Bind(wx.EVT_BUTTON, self.onClickEQUALS)

        self.__set_properties()
        self.__do_layout()

    def catlist(self):
        somelist = []
        for category in Structs.categoryList:
            somelist.append(category.name)
        return somelist

    def factlist(self, cat):
        somelist = []
        for fact in Structs.factList:
            if(fact.category==cat):
                somelist.append(fact.value)
        return somelist

    def securitylist(self):
        somelist = []
        for security in Structs.saList:
            somelist.append(security.name)
        return somelist

    def OnSelect1(self, e):
        self.combo_box_2.Enable()
        self.combo_box_2.SetItems(self.factlist(self.factCatComboBox.GetValue()))

    def onClickLESSER(self, e):
        self.list_box_1.Append(Structs.LESSER)

    def onClickGREATER(self, e):
        self.list_box_1.Append(Structs.GREATER)

    def onClickEQUALS(self, e):
        self.list_box_1.Append(Structs.EQUALS)

    def onClickAdd(self, e):
        self.list_box_1.Append(self.combo_box_2.GetValue()+"("+self.factCatComboBox.GetValue()+")")

    def onClickUndo(self, e):
        index = self.list_box_1.GetCount()
        self.list_box_1.Delete(index-1)

    def onClickComplete(self, e):
        Structs.foList.append(Structs.FactsOrder(self.list_box_1.GetItems(),self.combo_box_3.GetValue()))
        SMETool.populatelctrl6(smetool, Structs.foList)
        self.Close()

    def __set_properties(self):
        self.SetTitle(("Create a Facts Order"))
        self.SetSize((708, 550))
        self.list_box_1.SetMinSize((574, 300))

    def __do_layout(self):

        groupBox = wx.StaticBox(self, label="Create a Facts Order")
        groupBoxSizer = wx.StaticBoxSizer(groupBox, wx.VERTICAL)

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.label_1, 0, wx.ALIGN_LEFT, 5)
        sizer1.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer1.Add(self.factCatComboBox, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.label_2, 0, wx.ALIGN_LEFT, 5)
        sizer2.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer2.Add(self.combo_box_2, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3.Add(self.label_3, 0, wx.ALIGN_LEFT, 5)
        sizer3.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer3.Add(self.combo_box_3, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer4.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer4.Add(self.AND_Btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer4.Add(self.OR_Btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer4.Add(self.NEG_Btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer4.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)

        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        buttonsSizer.Add(self.addFactsOrderBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)
        buttonsSizer.Add(self.undoFactsOrderBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)
        buttonsSizer.Add(self.completeFactsOrderBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)

        groupBoxSizer.Add(self.list_box_1, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer1, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer2, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer3, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer4, 0, wx.EXPAND | wx.ALL, 5)

        mainSizer.Add(groupBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
        mainSizer.Add(buttonsSizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(mainSizer)
        self.CentreOnParent()
        self.Layout()

class EditFODialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.list_box_1 = wx.ListBox(self, wx.ID_ANY, choices=self.fillListBox())
        self.label_1 = wx.StaticText(self, wx.ID_ANY, ("Choose Fact Category:"))
        self.label_2 = wx.StaticText(self, wx.ID_ANY, ("Choose Fact:"))
        self.label_3 = wx.StaticText(self, wx.ID_ANY, ("Choose Security Attribute:"))

        self.factCatComboBox = wx.ComboBox(self, 10, choices=self.catlist(), style=wx.CB_DROPDOWN|wx.TE_READONLY, size=(200, -1))
        self.Bind(wx.EVT_COMBOBOX, self.OnSelect1, id=10)
        self.combo_box_2 = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN|wx.TE_READONLY, size=(200, -1))
        self.combo_box_2.Disable()
        self.combo_box_3 = wx.ComboBox(self, wx.ID_ANY, choices=self.securitylist(), style=wx.CB_DROPDOWN|wx.TE_READONLY, size=(200, -1))
        self.combo_box_3.SetValue(Structs.foList[smetool.factsOrderListView.GetFocusedItem()].security_attribute)

        # create buttons
        self.addFactsOrderBtn = wx.Button(self, label="Add")
        self.undoFactsOrderBtn = wx.Button(self, label="Undo")
        self.completeFactsOrderBtn = wx.Button(self,label="Complete")
        self.AND_Btn = wx.Button(self, label="LESSER")
        self.OR_Btn = wx.Button(self, label="GREATER")
        self.NEG_Btn = wx.Button(self, label="EQUALS")

        # do some buttons-bindings
        self.addFactsOrderBtn.Bind(wx.EVT_BUTTON, self.onClickAdd)
        self.undoFactsOrderBtn.Bind(wx.EVT_BUTTON, self.onClickUndo)
        self.completeFactsOrderBtn.Bind(wx.EVT_BUTTON, self.onClickComplete)
        self.AND_Btn.Bind(wx.EVT_BUTTON, self.onClickLESSER)
        self.OR_Btn.Bind(wx.EVT_BUTTON, self.onClickGREATER)
        self.NEG_Btn.Bind(wx.EVT_BUTTON, self.onClickEQUALS)

        self.__set_properties()
        self.__do_layout()

    def fillListBox(self):
        somelist = []
        for ele in Structs.foList[smetool.factsOrderListView.GetFocusedItem()].elements:
            somelist.append(ele)
        return somelist

    def catlist(self):
        somelist = []
        for category in Structs.categoryList:
            somelist.append(category.name)
        return somelist

    def factlist(self, cat):
        somelist = []
        for fact in Structs.factList:
            if(fact.category==cat):
                somelist.append(fact.value)
        return somelist

    def securitylist(self):
        somelist = []
        for security in Structs.saList:
            somelist.append(security.name)
        return somelist

    def OnSelect1(self, e):
        self.combo_box_2.Enable()
        self.combo_box_2.SetItems(self.factlist(self.factCatComboBox.GetValue()))

    def onClickLESSER(self, e):
        self.list_box_1.Append(Structs.LESSER)

    def onClickGREATER(self, e):
        self.list_box_1.Append(Structs.GREATER)

    def onClickEQUALS(self, e):
        self.list_box_1.Append(Structs.EQUALS)

    def onClickAdd(self, e):
        self.list_box_1.Append(self.combo_box_2.GetValue()+"("+self.factCatComboBox.GetValue()+")")

    def onClickUndo(self, e):
        index = self.list_box_1.GetCount()
        self.list_box_1.Delete(index-1)

    def onClickComplete(self, e):
        del Structs.foList[smetool.factsOrderListView.GetFocusedItem()]
        Structs.foList.append(Structs.FactsOrder(self.list_box_1.GetItems(),self.combo_box_3.GetValue()))
        SMETool.populatelctrl6(smetool, Structs.foList)
        self.Close()

    def __set_properties(self):
        self.SetTitle(("Edit the Facts Order"))
        self.SetSize((708, 550))
        self.list_box_1.SetMinSize((574, 300))

    def __do_layout(self):

        groupBox = wx.StaticBox(self, label="Create a Facts Order")
        groupBoxSizer = wx.StaticBoxSizer(groupBox, wx.VERTICAL)

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.label_1, 0, wx.ALIGN_LEFT, 5)
        sizer1.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer1.Add(self.factCatComboBox, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.label_2, 0, wx.ALIGN_LEFT, 5)
        sizer2.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer2.Add(self.combo_box_2, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3.Add(self.label_3, 0, wx.ALIGN_LEFT, 5)
        sizer3.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer3.Add(self.combo_box_3, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer4.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer4.Add(self.AND_Btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer4.Add(self.OR_Btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer4.Add(self.NEG_Btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer4.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)

        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        buttonsSizer.Add(self.addFactsOrderBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)
        buttonsSizer.Add(self.undoFactsOrderBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)
        buttonsSizer.Add(self.completeFactsOrderBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)

        groupBoxSizer.Add(self.list_box_1, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer1, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer2, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer3, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer4, 0, wx.EXPAND | wx.ALL, 5)

        mainSizer.Add(groupBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
        mainSizer.Add(buttonsSizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(mainSizer)
        self.CentreOnParent()
        self.Layout()

#EVALUATION RULES
class AddERDialog(wx.Dialog):

    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)

        self.list_box_1 = wx.ListBox(self, wx.ID_ANY, choices=[])

        # create labels
        self.label_1 = wx.StaticText(self, wx.ID_ANY, ("Choose Fact Category:"))
        self.label_2 = wx.StaticText(self, wx.ID_ANY, ("Choose Fact:"))
        self.label_3 = wx.StaticText(self, wx.ID_ANY, ("Choose Security Attribute:"))
        self.label_4 = wx.StaticText(self, wx.ID_ANY, ("Enter Influence Value:"))

        # create buttons
        self.AND_Btn = wx.Button(self, label="AND")
        self.OR_Btn = wx.Button(self, label="OR")
        self.NEG_Btn = wx.Button(self, label="IMPLY")
        self.addBtn = wx.Button(self, label="Add")
        self.undoBtn = wx.Button(self, label="Undo")
        self.completeBtn = wx.Button(self, label="Complete")

        # do some buttons-bindings
        self.AND_Btn.Bind(wx.EVT_BUTTON, self.onClickAND)
        self.OR_Btn.Bind(wx.EVT_BUTTON, self.onClickOR)
        self.NEG_Btn.Bind(wx.EVT_BUTTON, self.onClickIMPLY)
        self.addBtn.Bind(wx.EVT_BUTTON, self.onClickAdd)
        self.undoBtn.Bind(wx.EVT_BUTTON, self.onClickUndo)
        self.completeBtn.Bind(wx.EVT_BUTTON, self.onClickComplete)

        # create combos
        self.factCatComboBox = wx.ComboBox(self, 10, choices=self.catlist(), style=wx.CB_DROPDOWN|wx.TE_READONLY, size=(200,-1))
        self.combo_box_2 = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN|wx.TE_READONLY, size=(200,-1))
        self.combo_box_2.Disable()
        self.combo_box_3 = wx.ComboBox(self, wx.ID_ANY, choices=self.securitylist(), style=wx.CB_DROPDOWN|wx.TE_READONLY, size=(200,-1))

        # do some combo bindings
        self.Bind(wx.EVT_COMBOBOX, self.OnSelect1, id=10)

        # create txt ctrls
        self.textctrl_1 = wx.TextCtrl(self, wx.ID_ANY, size=(200,-1))

        self.__set_properties()
        self.__do_layout()

    def catlist(self):
        somelist = []
        for category in Structs.categoryList:
            somelist.append(category.name)
        return somelist

    def factlist(self, cat):
        somelist = []
        for fact in Structs.factList:
            if(fact.category==cat):
                somelist.append(fact.value)
        return somelist

    def securitylist(self):
        somelist = []
        for security in Structs.saList:
            somelist.append(security.name)
        return somelist

    def OnSelect1(self, e):
        self.combo_box_2.Enable()
        self.combo_box_2.SetItems(self.factlist(self.factCatComboBox.GetValue()))

    def onClickAND(self, e):
        self.list_box_1.Append(Structs.AND)

    def onClickOR(self, e):
        self.list_box_1.Append(Structs.OR)

    def onClickIMPLY(self, e):
        self.list_box_1.Append(Structs.IMPLY)

    def onClickAdd(self, e):
        self.list_box_1.Append(self.combo_box_2.GetValue()+"("+self.factCatComboBox.GetValue()+")")

    def onClickUndo(self, e):
        index = self.list_box_1.GetCount()
        self.list_box_1.Delete(index-1)

    def onClickComplete(self, e):
        if self.textctrl_1.GetValue()=='':
            influence_value=0
        else:
            influence_value=self.textctrl_1.GetValue()
        Structs.erList.append(Structs.EvaluationRule(self.list_box_1.GetItems(),influence_value,self.combo_box_3.GetValue()))
        SMETool.populatelctrl10(smetool, Structs.erList)
        self.Close()

    def __set_properties(self):
        self.SetTitle(("Create an Evaluation Rule"))
        self.SetSize((708, 570))
        self.list_box_1.SetMinSize((574, 300))

    def __do_layout(self):

        groupBox = wx.StaticBox(self, label="Create an Evaluation Rule")
        groupBoxSizer = wx.StaticBoxSizer(groupBox, wx.VERTICAL)

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.label_1, 0, wx.ALIGN_LEFT, 5)
        sizer1.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer1.Add(self.factCatComboBox, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.label_2, 0, wx.ALIGN_LEFT, 5)
        sizer2.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer2.Add(self.combo_box_2, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3.Add(self.label_3, 0, wx.ALIGN_LEFT, 5)
        sizer3.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer3.Add(self.combo_box_3, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer4.Add(self.label_4, 0, wx.ALIGN_LEFT, 5)
        sizer4.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer4.Add(self.textctrl_1, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer5.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer5.Add(self.AND_Btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer5.Add(self.OR_Btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer5.Add(self.NEG_Btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer5.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)

        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        buttonsSizer.Add(self.addBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)
        buttonsSizer.Add(self.undoBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)
        buttonsSizer.Add(self.completeBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)

        groupBoxSizer.Add(self.list_box_1, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer1, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer2, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer3, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer4, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer5, 0, wx.EXPAND | wx.ALL, 5)

        mainSizer.Add(groupBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
        mainSizer.Add(buttonsSizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(mainSizer)
        self.CentreOnParent()
        self.Layout()

class EditERDialog(wx.Dialog):

    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)

        self.list_box_1 = wx.ListBox(self, wx.ID_ANY, choices=self.fillListBox())
        self.label_1 = wx.StaticText(self, wx.ID_ANY, ("Choose Fact Category:"))
        self.label_2 = wx.StaticText(self, wx.ID_ANY, ("Choose Fact:"))
        self.label_3 = wx.StaticText(self, wx.ID_ANY, ("Choose Security Attribute:"))
        self.label_4 = wx.StaticText(self, wx.ID_ANY, ("Enter Influence Value:"))
        self.AND_Btn = wx.Button(self, 1, ("AND"))
        self.Bind(wx.EVT_BUTTON, self.onClickAND, id=1)
        self.OR_Btn = wx.Button(self, 2, ("OR"))
        self.Bind(wx.EVT_BUTTON, self.onClickOR, id=2)
        self.NEG_Btn = wx.Button(self, 3, ("IMPLY"))
        self.Bind(wx.EVT_BUTTON, self.onClickIMPLY, id=3)
        self.factCatComboBox = wx.ComboBox(self, 10, choices=self.catlist(), style=wx.CB_DROPDOWN|wx.TE_READONLY, size=(200,-1))
        self.Bind(wx.EVT_COMBOBOX, self.OnSelect1, id=10)
        self.combo_box_2 = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN|wx.TE_READONLY, size=(200,-1))
        self.combo_box_2.Disable()
        self.combo_box_3 = wx.ComboBox(self, wx.ID_ANY, choices=self.securitylist(), style=wx.CB_DROPDOWN|wx.TE_READONLY, size=(200,-1))
        self.combo_box_3.SetValue(Structs.erList[smetool.evaluationRulesListView.GetFocusedItem()].security_attribute)
        self.textctrl_1 = wx.TextCtrl(self, wx.ID_ANY, size=(200,-1))
        self.textctrl_1.SetValue(Structs.erList[smetool.evaluationRulesListView.GetFocusedItem()].influence)

        self.addERBtn = wx.Button(self, 7, ("Add"))
        self.Bind(wx.EVT_BUTTON, self.onClickAdd, id=7)
        self.undoERBtn = wx.Button(self, 8, ("Undo"))
        self.Bind(wx.EVT_BUTTON, self.onClickUndo, id=8)
        self.completeERBtn = wx.Button(self, 9, ("Complete"))
        self.Bind(wx.EVT_BUTTON, self.onClickComplete, id=9)

        self.__set_properties()
        self.__do_layout()

    def fillListBox(self):
        somelist = []
        for ele in Structs.erList[smetool.evaluationRulesListView.GetFocusedItem()].elements:
            somelist.append(ele)
        return somelist

    def catlist(self):
        somelist = []
        for category in Structs.categoryList:
            somelist.append(category.name)
        return somelist

    def factlist(self, cat):
        somelist = []
        for fact in Structs.factList:
            if(fact.category==cat):
                somelist.append(fact.value)
        return somelist

    def securitylist(self):
        somelist = []
        for security in Structs.saList:
            somelist.append(security.name)
        return somelist

    def OnSelect1(self, e):
        self.combo_box_2.Enable()
        self.combo_box_2.SetItems(self.factlist(self.factCatComboBox.GetValue()))

    def onClickAND(self, e):
        self.list_box_1.Append(Structs.AND)

    def onClickOR(self, e):
        self.list_box_1.Append(Structs.OR)

    def onClickIMPLY(self, e):
        self.list_box_1.Append(Structs.IMPLY)

    def onClickAdd(self, e):
        self.list_box_1.Append(self.combo_box_2.GetValue()+"("+self.factCatComboBox.GetValue()+")")

    def onClickUndo(self, e):
        index = self.list_box_1.GetCount()
        self.list_box_1.Delete(index-1)

    def onClickComplete(self, e):
        if self.textctrl_1.GetValue()=='':
            influence_value=0
        else:
            influence_value=self.textctrl_1.GetValue()
        del Structs.erList[smetool.evaluationRulesListView.GetFocusedItem()]
        Structs.erList.append(Structs.EvaluationRule(self.list_box_1.GetItems(),influence_value,self.combo_box_3.GetValue()))
        SMETool.populatelctrl10(smetool, Structs.erList)
        self.Close()

    def __set_properties(self):
        self.SetTitle(("Edit the Evaluation Rule"))
        self.SetSize((708, 570))
        self.list_box_1.SetMinSize((574, 300))

    def __do_layout(self):

        groupBox = wx.StaticBox(self, label="Edit the Evaluation Rule")
        groupBoxSizer = wx.StaticBoxSizer(groupBox, wx.VERTICAL)

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.label_1, 0, wx.ALIGN_LEFT, 5)
        sizer1.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer1.Add(self.factCatComboBox, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.label_2, 0, wx.ALIGN_LEFT, 5)
        sizer2.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer2.Add(self.combo_box_2, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3.Add(self.label_3, 0, wx.ALIGN_LEFT, 5)
        sizer3.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer3.Add(self.combo_box_3, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer4.Add(self.label_4, 0, wx.ALIGN_LEFT, 5)
        sizer4.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer4.Add(self.textctrl_1, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer5.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer5.Add(self.AND_Btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer5.Add(self.OR_Btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer5.Add(self.NEG_Btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer5.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)

        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        buttonsSizer.Add(self.addERBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)
        buttonsSizer.Add(self.undoERBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)
        buttonsSizer.Add(self.completeERBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)

        groupBoxSizer.Add(self.list_box_1, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer1, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer2, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer3, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer4, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer5, 0, wx.EXPAND | wx.ALL, 5)

        mainSizer.Add(groupBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
        mainSizer.Add(buttonsSizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(mainSizer)
        self.CentreOnParent()
        self.Layout()

#CASE
class AddCaseDialog(wx.Dialog):

    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)

        self.list_box_1 = wx.ListBox(self, wx.ID_ANY, choices=[])
        self.label_1 = wx.StaticText(self, wx.ID_ANY, ("Choose Fact Category:"))
        self.label_2 = wx.StaticText(self, wx.ID_ANY, ("Choose Fact:"))
        self.label_4 = wx.StaticText(self, wx.ID_ANY, ("Enter Description:"))
        self.factCatComboBox = wx.ComboBox(self, 10, choices=self.catlist(), style=wx.CB_DROPDOWN|wx.TE_READONLY, size=(200,-1))
        self.Bind(wx.EVT_COMBOBOX, self.OnSelect1, id=10)
        self.combo_box_2 = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN|wx.TE_READONLY, size=(200,-1))
        self.combo_box_2.Disable()
        self.textctrl_1 = wx.TextCtrl(self, wx.ID_ANY, size=(200,-1))

        # create buttons
        self.addCaseBtn = wx.Button(self, label="Add")
        self.undoCaseBtn = wx.Button(self, label="Undo")
        self.completeCaseBtn = wx.Button(self, label="Complete")

        # do some buttons-bindings
        self.addCaseBtn.Bind(wx.EVT_BUTTON, self.onClickAdd)
        self.undoCaseBtn.Bind(wx.EVT_BUTTON, self.onClickUndo)
        self.completeCaseBtn.Bind(wx.EVT_BUTTON, self.onClickComplete)

        self.__set_properties()
        self.__do_layout()

    def catlist(self):
        somelist = []
        for category in Structs.categoryList:
            somelist.append(category.name)
        return somelist

    def factlist(self, cat):
        somelist = []
        for fact in Structs.factList:
            if(fact.category==cat):
                somelist.append(fact.value)
        return somelist

    def OnSelect1(self, e):
        self.combo_box_2.Enable()
        self.combo_box_2.SetItems(self.factlist(self.factCatComboBox.GetValue()))


    def onClickAdd(self, e):
        self.list_box_1.Append(self.combo_box_2.GetValue()+"("+self.factCatComboBox.GetValue()+")")

    def onClickUndo(self, e):
        index = self.list_box_1.GetCount()
        self.list_box_1.Delete(index-1)

    def onClickComplete(self, e):
        Structs.caseList.append(Structs.Case(self.createCasename(),self.list_box_1.GetItems(),self.textctrl_1.GetValue()))
        SMETool.populatelctrl11(smetool, Structs.caseList)
        self.Close()

    def createCasename(self):
        previ = 1
        newi = previ
        while(True):
            newi = previ
            for case in Structs.caseList:
                if(case.casename=="Case "+str(previ)):
                    previ=previ+1
            if(previ==newi):
                break
        casename = "Case "+str(newi)
        return casename

    def __set_properties(self):
        self.SetTitle(("Create a Case"))
        self.SetSize((708, 490))
        self.list_box_1.SetMinSize((574, 300))

    def __do_layout(self):

        groupBox = wx.StaticBox(self, label="Create a Case")
        groupBoxSizer = wx.StaticBoxSizer(groupBox, wx.VERTICAL)

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.label_1, 0, wx.ALIGN_LEFT, 5)
        sizer1.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer1.Add(self.factCatComboBox, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.label_2, 0, wx.ALIGN_LEFT, 5)
        sizer2.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer2.Add(self.combo_box_2, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3.Add(self.label_4, 0, wx.ALIGN_LEFT, 5)
        sizer3.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer3.Add(self.textctrl_1, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        buttonsSizer.Add(self.addCaseBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)
        buttonsSizer.Add(self.undoCaseBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)
        buttonsSizer.Add(self.completeCaseBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)

        groupBoxSizer.Add(self.list_box_1, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer1, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer2, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer3, 0, wx.EXPAND | wx.ALL, 5)

        mainSizer.Add(groupBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
        mainSizer.Add(buttonsSizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(mainSizer)
        self.CentreOnParent()
        self.Layout()

class EditCaseDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.list_box_1 = wx.ListBox(self, wx.ID_ANY, choices=self.fillListBox())
        self.label_1 = wx.StaticText(self, wx.ID_ANY, ("Choose Fact Category:"))
        self.label_2 = wx.StaticText(self, wx.ID_ANY, ("Choose Fact:"))
        self.label_4 = wx.StaticText(self, wx.ID_ANY, ("Enter Description:"))
        self.factCatComboBox = wx.ComboBox(self, 10, choices=self.catlist(), style=wx.CB_DROPDOWN|wx.TE_READONLY, size=(200,-1))
        self.Bind(wx.EVT_COMBOBOX, self.OnSelect1, id=10)
        self.combo_box_2 = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN|wx.TE_READONLY, size=(200,-1))
        self.combo_box_2.Disable()
        self.textctrl_1 = wx.TextCtrl(self, wx.ID_ANY, size=(200,-1))
        self.textctrl_1.SetValue(Structs.caseList[smetool.casesListView.GetFocusedItem()].description)
        self.addCaseBtn = wx.Button(self, 7, ("Add"))
        self.Bind(wx.EVT_BUTTON, self.onClickAdd, id=7)
        self.undoCaseBtn = wx.Button(self, 8, ("Undo"))
        self.Bind(wx.EVT_BUTTON, self.onClickUndo, id=8)
        self.completeCaseBtn = wx.Button(self, 9, ("Complete"))
        self.Bind(wx.EVT_BUTTON, self.onClickComplete, id=9)

        self.__set_properties()
        self.__do_layout()

    def fillListBox(self):
        somelist = []
        for fact in Structs.caseList[smetool.casesListView.GetFocusedItem()].facts:
            somelist.append(fact)
        return somelist

    def catlist(self):
        somelist = []
        for category in Structs.categoryList:
            somelist.append(category.name)
        return somelist

    def factlist(self, cat):
        somelist = []
        for fact in Structs.factList:
            if(fact.category==cat):
                somelist.append(fact.value)
        return somelist

    def OnSelect1(self, e):
        self.combo_box_2.Enable()
        self.combo_box_2.SetItems(self.factlist(self.factCatComboBox.GetValue()))


    def onClickAdd(self, e):
        self.list_box_1.Append(self.combo_box_2.GetValue()+"("+self.factCatComboBox.GetValue()+")")

    def onClickUndo(self, e):
        index = self.list_box_1.GetCount()
        self.list_box_1.Delete(index-1)

    def onClickComplete(self, e):
        casename = Structs.caseList[smetool.casesListView.GetFocusedItem()].casename
        del Structs.caseList[smetool.casesListView.GetFocusedItem()]
        Structs.caseList.append(Structs.Case(casename,self.list_box_1.GetItems(),self.textctrl_1.GetValue()))
        SMETool.populatelctrl11(smetool, Structs.caseList)
        self.Close()

    def __set_properties(self):
        self.SetTitle(("Edit the Case"))
        self.SetSize((708, 490))
        self.list_box_1.SetMinSize((574, 300))

    def __do_layout(self):

        groupBox = wx.StaticBox(self, label="Edit the Case")
        groupBoxSizer = wx.StaticBoxSizer(groupBox, wx.VERTICAL)

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(self.label_1, 0, wx.ALIGN_LEFT, 5)
        sizer1.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer1.Add(self.factCatComboBox, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.label_2, 0, wx.ALIGN_LEFT, 5)
        sizer2.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer2.Add(self.combo_box_2, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3.Add(self.label_4, 0, wx.ALIGN_LEFT, 5)
        sizer3.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        sizer3.Add(self.textctrl_1, 0, wx.EXPAND | wx.ALIGN_RIGHT, 5)

        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.ALIGN_CENTER, 5)
        buttonsSizer.Add(self.addCaseBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)
        buttonsSizer.Add(self.undoCaseBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)
        buttonsSizer.Add(self.completeCaseBtn, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM, 5)

        groupBoxSizer.Add(self.list_box_1, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer1, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer2, 0, wx.EXPAND | wx.ALL, 5)
        groupBoxSizer.Add(sizer3, 0, wx.EXPAND | wx.ALL, 5)

        mainSizer.Add(groupBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
        mainSizer.Add(buttonsSizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(mainSizer)
        self.CentreOnParent()
        self.Layout()

class EvaluateCaseDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.list_box_1 = wx.ListBox(self, wx.ID_ANY, choices=[])
        self.list_box_1.Enable(False)
        self.closeBtn = wx.Button(self, 9, ("Close"))
        self.detailsBtn = wx.Button(self, 10, ("Details"))
        self.grid_1 = wx.grid.Grid(self, wx.ID_ANY, size=(1, 1))
        self.Bind(wx.EVT_BUTTON, self.onClickClose, id=9)
        self.Bind(wx.EVT_BUTTON, self.onClickDetails, id=10)
        self.resultList = []
        self.factsetList = []

        self.__set_properties()
        self.__do_layout()

        self.evaluate()

    #Evaluation related
    def getleftside(self, somelist):
        leftside = []
        for item in somelist:
            if item==Structs.IMPLY:
                break
            else:
                leftside.append(item)
        return leftside

    def getrightside(self, somelist):
        flag = False
        rightside = []
        for item in somelist:
            if flag:
                rightside.append(item)
            if item==Structs.IMPLY:
                flag = True
        return rightside

    def analyse(self, startevalset):
        previousevalset = []
        additevalset = []
        currevalset = []
        for fact in startevalset:
            for rule in Structs.ruleList:
                if fact in rule.elements:
                    if fact in self.getleftside(rule.elements):
                        for item in self.getrightside(rule.elements):
                            if item!=Structs.IMPLY and item!=Structs.AND and item!=Structs.OR and item!=Structs.NEG and item not in additevalset:
                                additevalset.append(item)
        currevalset.extend(additevalset)
        while additevalset:
            additevalset = []
            for fact in currevalset:
                for rule in Structs.ruleList:
                    if fact in rule.elements:
                        if fact in self.getleftside(rule.elements):
                            for item in self.getrightside(rule.elements):
                                if item!=Structs.IMPLY and item!=Structs.AND and item!=Structs.OR and item!=Structs.NEG and item not in additevalset:
                                    additevalset.append(item)
            for element in additevalset:
                if element not in currevalset:
                    currevalset.append(element)
            if set(previousevalset)==set(additevalset):
                break
            previousevalset = additevalset
        for fact in currevalset:
            if fact in startevalset:
                currevalset.remove(fact)
        currevalset.extend(startevalset)
        del startevalset[0:len(startevalset)]
        del previousevalset[0:len(previousevalset)]
        del additevalset[0:len(additevalset)]
        return currevalset

    def createsecattdict(self):
        secattdict = {}
        for secatt in Structs.saList:
            secattdict.update({secatt.name:0})
        return secattdict

    def skipconflrules(self, currevalset):
        evalrules = []
        for rule in Structs.erList:
            evalrules.append(rule)
        currevalrules = evalrules
        skippedcomprules = []
        tempfactelements = []
        compositerules = []
        for evalrule in evalrules:
            if len(evalrule.elements)>2:
                tempfactelements = []
                for element in evalrule.elements:
                    if(element!=Structs.AND and element!=Structs.OR and element!=Structs.IMPLY):
                        tempfactelements.append(element)
                for fact in tempfactelements:
                    if fact not in currevalset:
                        if evalrule not in skippedcomprules:
                            skippedcomprules.append(evalrule)
        for evalrule in evalrules:
            for skipped in skippedcomprules:
                if(evalrule==skipped):
                    currevalrules.remove(skipped)
        evalrule = currevalrules
        for evalrule in evalrules:
            if len(evalrule.elements)>2:
                if evalrule not in compositerules:
                    compositerules.append(evalrule)
        for evalrulecomp in compositerules:
            for evalrule in evalrules:
                for element in evalrulecomp.elements:
                    if(element!=Structs.AND and element!=Structs.OR and element!=Structs.IMPLY):
                        if element in evalrule.elements and len(evalrule.elements)<=2 and evalrule.security_attribute==evalrulecomp.security_attribute:
                            if evalrule in currevalrules:
                                currevalrules.remove(evalrule)
        del skippedcomprules[0:len(skippedcomprules)]
        del tempfactelements[0:len(tempfactelements)]
        del compositerules[0:len(compositerules)]
        return currevalrules


    def evaluate(self):
        startset = []
        additionalfacts = []
        deletedfacts = []
        for item in Structs.caseList[smetool.casesListView.GetFocusedItem()].facts:
            startset.append(item)
        for fact in startset:
            if fact.startswith(Structs.NEG):
                continue
            for evalrule in Structs.erList:
                if fact in self.getleftside(evalrule.elements):
                    declared = True
            if not declared:
                for order in Structs.foList:
                    if fact in order.elements:
                        for element in order.elements:
                            if element!=Structs.GREATER and element!=Structs.LESSER and element!=Structs.EQUALS and element!=Structs.GREATER+Structs.EQUALS and element!=Structs.LESSER+Structs.EQUALS and element!=fact:
                                if element not in additionalfacts:
                                    additionalfacts.append(element)
                                if element not in deletedfacts:
                                    deletedfacts.append(fact)
                                break
            declared = False
        for fact in additionalfacts:
            startset.append(fact)
        for fact in deletedfacts:
            if fact in startset:
                startset.remove(fact)
        currevalset = self.analyse(startset)
        secattdict = self.createsecattdict()
        currevalrules = self.skipconflrules(currevalset)
        rulestoskip = []
        declared = False

        for fact in currevalset:
            if fact.startswith(Structs.NEG):
                continue
            for evalrule in currevalrules:
                if fact in self.getleftside(evalrule.elements):
                    for secatt in secattdict:
                        if secatt==evalrule.security_attribute:
                            if evalrule not in rulestoskip:
                                secattdict[secatt] = secattdict[secatt] + int(evalrule.influence)
                            if len(evalrule.elements)>2 :
                                if evalrule not in rulestoskip:
                                    rulestoskip.append(evalrule)
        for fact in currevalset:
            if fact in Structs.caseList[smetool.casesListView.GetFocusedItem()].facts:
                currevalset.remove(fact)
        self.resultList.append(Structs.caseList[smetool.casesListView.GetFocusedItem()].casename+":")
        self.resultList.append("")
        self.grid_1.SetRowLabelValue(0, Structs.caseList[smetool.casesListView.GetFocusedItem()].casename)
        iter = 0
        for key, value in secattdict.items():
            self.resultList.append(key+" - "+str(value))
            self.grid_1.SetColLabelValue(iter, key)
            self.grid_1.SetCellValue(0, iter, str(value))
            iter = iter+1
        self.resultList.append("")
        self.factsetList.append("Set of facts for "+Structs.caseList[smetool.casesListView.GetFocusedItem()].casename+":")
        self.factsetList.append("")
        for fact in currevalset:
            self.factsetList.append(fact)
        del currevalset[0:len(currevalset)]
        del currevalrules[0:len(currevalrules)]
        del rulestoskip[0:len(rulestoskip)]
        del additionalfacts[0:len(additionalfacts)]
        del deletedfacts[0:len(deletedfacts)]

    #End evaluation related
    def onClickClose(self, e):
        self.Close()

    def onClickDetails(self, e):
        self.list_box_1.Enable(True)
        self.list_box_1.Clear()
        self.list_box_1.AppendItems(self.resultList)
        self.list_box_1.AppendItems(self.factsetList)

    def __set_properties(self):
        self.SetTitle(("Case QoP Evaluation"))
        self.SetSize((800, 473))
        self.grid_1.CreateGrid(1, len(Structs.saList))
        for col in range(len(Structs.saList)):
            self.grid_1.SetColSize(col, 100)
        self.grid_1.SetMinSize((700, 300))
        self.grid_1.EnableEditing(False)
        self.list_box_1.SetMinSize((550, 100))

    def __do_layout(self):

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
        buttonsSizer.Add(self.detailsBtn, 0, wx.ALL | wx.EXPAND, 5)
        buttonsSizer.Add(self.closeBtn, 0, wx.ALL | wx.EXPAND, 5)

        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(self.grid_1, 1, wx.EXPAND, 5)

        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.list_box_1, 1, wx.EXPAND, 5)

        mainSizer.Add(sizer_1, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(sizer_2, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(buttonsSizer, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(mainSizer)
        self.CentreOnParent()
        self.Layout()

class EvaluateAllCasesDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.list_box_1 = wx.ListBox(self, wx.ID_ANY, choices=[])
        self.list_box_1.Enable(False)
        self.closeBtn = wx.Button(self, 9, ("Close"))
        self.detailsBtn = wx.Button(self, 10, ("Details"))
        self.grid_1 = wx.grid.Grid(self, wx.ID_ANY, size=(1, 1))
        self.Bind(wx.EVT_BUTTON, self.onClickClose, id=9)
        self.Bind(wx.EVT_BUTTON, self.onClickDetails, id=10)
        self.resultList = []
        self.factsetList = []
        self.minsecattdict = self.createminsecattdict()
        self.maxsecattdict = self.createsecattdict()
        self.treshsecattdict = self.createsecattdict()

        self.__set_properties()
        self.__do_layout()

        self.evaluateall()

    #Evaluation related
    def getleftside(self, somelist):
        leftside = []
        for item in somelist:
            if item==Structs.IMPLY:
                break
            else:
                leftside.append(item)
        return leftside

    def getrightside(self, somelist):
        flag = False
        rightside = []
        for item in somelist:
            if flag:
                rightside.append(item)
            if item==Structs.IMPLY:
                flag = True
        return rightside

    def analyse(self, startevalset):
        previousevalset = []
        additevalset = []
        currevalset = []
        for fact in startevalset:
            for rule in Structs.ruleList:
                if fact in rule.elements:
                    if fact in self.getleftside(rule.elements):
                        for item in self.getrightside(rule.elements):
                            if item!=Structs.IMPLY and item!=Structs.AND and item!=Structs.OR and item!=Structs.NEG and item not in additevalset:
                                additevalset.append(item)
        currevalset.extend(additevalset)
        while additevalset:
            additevalset = []
            for fact in currevalset:
                for rule in Structs.ruleList:
                    if fact in rule.elements:
                        if fact in self.getleftside(rule.elements):
                            for item in self.getrightside(rule.elements):
                                if item!=Structs.IMPLY and item!=Structs.AND and item!=Structs.OR and item!=Structs.NEG and item not in additevalset:
                                    additevalset.append(item)
            for element in additevalset:
                if element not in currevalset:
                    currevalset.append(element)
            if set(previousevalset)==set(additevalset):
                break
            previousevalset = additevalset
        for fact in currevalset:
            if fact in startevalset:
                currevalset.remove(fact)
        currevalset.extend(startevalset)
        del startevalset[0:len(startevalset)]
        del previousevalset[0:len(previousevalset)]
        del additevalset[0:len(additevalset)]
        return currevalset

    def createsecattdict(self):
        secattdict = {}
        for secatt in Structs.saList:
            secattdict.update({secatt.name:0})
        return secattdict

    def createminsecattdict(self):
        secattdict = {}
        for secatt in Structs.saList:
            secattdict.update({secatt.name:100})
        return secattdict

    def skipconflrules(self, currevalset):
        evalrules = []
        for rule in Structs.erList:
            evalrules.append(rule)
        currevalrules = evalrules
        skippedcomprules = []
        tempfactelements = []
        compositerules = []
        for evalrule in evalrules:
            if len(evalrule.elements)>2:
                tempfactelements = []
                for element in evalrule.elements:
                    if(element!=Structs.AND and element!=Structs.OR and element!=Structs.IMPLY):
                        tempfactelements.append(element)
                for fact in tempfactelements:
                    if fact not in currevalset:
                        if evalrule not in skippedcomprules:
                            skippedcomprules.append(evalrule)
        for evalrule in evalrules:
            for skipped in skippedcomprules:
                if(evalrule==skipped):
                    currevalrules.remove(skipped)
        evalrule = currevalrules
        for evalrule in evalrules:
            if len(evalrule.elements)>2:
                if evalrule not in compositerules:
                    compositerules.append(evalrule)
        for evalrulecomp in compositerules:
            for evalrule in evalrules:
                for element in evalrulecomp.elements:
                    if(element!=Structs.AND and element!=Structs.OR and element!=Structs.IMPLY):
                        if element in evalrule.elements and len(evalrule.elements)<=2 and evalrule.security_attribute==evalrulecomp.security_attribute:
                            if evalrule in currevalrules:
                                currevalrules.remove(evalrule)
        del skippedcomprules[0:len(skippedcomprules)]
        del tempfactelements[0:len(tempfactelements)]
        del compositerules[0:len(compositerules)]
        return currevalrules

    def evaluate(self, iterator):
        startset = []
        additionalfacts = []
        deletedfacts = []
        for item in Structs.caseList[iterator].facts:
            startset.append(item)
        for fact in startset:
            if fact.startswith(Structs.NEG):
                continue
            for evalrule in Structs.erList:
                if fact in self.getleftside(evalrule.elements):
                    declared = True
            if not declared:
                for order in Structs.foList:
                    if fact in order.elements:
                        for element in order.elements:
                            if element!=Structs.GREATER and element!=Structs.LESSER and element!=Structs.EQUALS and element!=Structs.GREATER+Structs.EQUALS and element!=Structs.LESSER+Structs.EQUALS and element!=fact:
                                if element not in additionalfacts:
                                    additionalfacts.append(element)
                                if element not in deletedfacts:
                                    deletedfacts.append(fact)
                                break
            declared = False
        for fact in additionalfacts:
            startset.append(fact)
        for fact in deletedfacts:
            if fact in startset:
                startset.remove(fact)
        currevalset = self.analyse(startset)
        secattdict = self.createsecattdict()
        currevalrules = self.skipconflrules(currevalset)
        rulestoskip = []
        declared = False

        for fact in currevalset:
            if fact.startswith(Structs.NEG):
                continue
            for evalrule in currevalrules:
                if fact in self.getleftside(evalrule.elements):
                    for secatt in secattdict:
                        if secatt==evalrule.security_attribute:
                            if evalrule not in rulestoskip:
                                secattdict[secatt] = secattdict[secatt] + int(evalrule.influence)
                            if len(evalrule.elements)>2 :
                                if evalrule not in rulestoskip:
                                    rulestoskip.append(evalrule)
        for fact in currevalset:
            if fact in Structs.caseList[iterator].facts:
                currevalset.remove(fact)
        self.resultList.append(Structs.caseList[iterator].casename+":")
        self.resultList.append("")
        self.grid_1.SetRowLabelValue(iterator, Structs.caseList[iterator].casename)
        iter = 0
        for key, value in secattdict.items():
            self.resultList.append(key+" - "+str(value))
            self.grid_1.SetColLabelValue(iter, key)
            self.grid_1.SetCellValue(iterator, iter, str(value))
            iter = iter+1
            if self.minsecattdict[key]>=value and value!=0:
                self.minsecattdict[key] = value
            if self.maxsecattdict[key]<=value:
                self.maxsecattdict[key] = value
        self.resultList.append("")
        self.factsetList.append("Set of facts for "+Structs.caseList[iterator].casename+":")
        self.factsetList.append("")
        for fact in currevalset:
            self.factsetList.append(fact)
        self.factsetList.append("")
        del currevalset[0:len(currevalset)]
        del currevalrules[0:len(currevalrules)]
        del rulestoskip[0:len(rulestoskip)]
        del additionalfacts[0:len(additionalfacts)]
        del deletedfacts[0:len(deletedfacts)]

    def evaluateall(self):
        val = ""
        ci = 0
        for case in Structs.caseList:
            self.evaluate(ci)
            ci=ci+1
        #self.list_box_1.AppendItems(self.resultList)
        #self.list_box_1.AppendItems(self.factsetList)

        for key, value in self.treshsecattdict.items():
            self.treshsecattdict[key] = float(self.maxsecattdict[key]-self.minsecattdict[key])/5
        for row in range(len(Structs.caseList)):
            #print "\nCASE:"+str(row+1)+"\n"
            for col in range(len(Structs.saList)):
                newmin = self.minsecattdict[self.grid_1.GetColLabelValue(col)]
                #print "starting newmin:" +str(newmin) +" sec_att: "+self.grid_1.GetColLabelValue(col)
                #print "value:" + str(self.grid_1.GetCellValue(row, col))
                for i in range(6):
                    if float(self.grid_1.GetCellValue(row, col))==0:
                        val = "no"
                        break
                    elif float(self.grid_1.GetCellValue(row, col))>newmin and i<5 or i==0:
                        newmin = newmin + self.treshsecattdict[self.grid_1.GetColLabelValue(col)]
                        #print "Newmin: "+str(newmin)
                    else:
                        if i==1:
                            val = "very low"
                        if i==2:
                            val = "low"
                        if i==3:
                            val = "medium"
                        if i==4:
                            val = "high"
                        if i==5:
                            val = "very high"
                        break
                #print "Cell: "+str(float(self.grid_1.GetCellValue(row, col)))
                #print "i "+str(i)
                self.grid_1.SetCellValue(row, col, self.grid_1.GetCellValue(row, col)+" ("+val+")")
                #print self.grid_1.GetCellValue(row, col)
        #print self.treshsecattdict
        #print self.minsecattdict
        #print self.maxsecattdict
        self.grid_1.SetReadOnly(len(Structs.caseList), len(Structs.saList), True)

    #End evaluation related
    def onClickClose(self, e):
        self.Close()

    def onClickDetails(self, e):
        self.list_box_1.Enable(True)
        self.list_box_1.Clear()
        self.list_box_1.AppendItems(self.resultList)
        self.list_box_1.AppendItems(self.factsetList)

    def __set_properties(self):
        self.SetTitle(("All Cases QoP Evaluation"))
        self.SetSize((800, 473))
        self.grid_1.CreateGrid(len(Structs.caseList), len(Structs.saList))
        for col in range(len(Structs.saList)):
            self.grid_1.SetColSize(col, 100)
        self.grid_1.SetMinSize((700, 300))
        self.grid_1.EnableEditing(False)
        self.list_box_1.SetMinSize((550, 100))

    def __do_layout(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.ALL | wx.EXPAND, 5)
        buttonsSizer.Add(self.detailsBtn, 0, wx.ALL | wx.EXPAND, 5)
        buttonsSizer.Add(self.closeBtn, 0, wx.ALL | wx.EXPAND, 5)

        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(self.grid_1, 1, wx.EXPAND, 5)

        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.list_box_1, 1, wx.EXPAND, 5)

        mainSizer.Add(sizer_1, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(sizer_2, 0, wx.ALL | wx.EXPAND, 5)
        mainSizer.Add(buttonsSizer, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(mainSizer)
        self.CentreOnParent()
        self.Layout()

#MAINFRAME
class SMETool(wx.Frame):
    def __init__(self, *args, **kwds):
        #kwds["style"] = wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.MAXIMIZE | wx.MAXIMIZE_BOX | wx.SYSTEM_MENU | wx.RESIZE_BORDER | wx.CLIP_CHILDREN
        wx.Frame.__init__(self, *args, **kwds)

    #MENUBAR

        self.sme_menubar = wx.MenuBar()

        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu2 = wx.Menu()

        # about menu item
        itemAbout = wx.MenuItem(wxglade_tmp_menu, wx.NewId(), u"&About SMETool\tCTRL+I", "", wx.ITEM_NORMAL)
        self.Bind(wx.EVT_MENU, self.OnAboutBox, itemAbout)
        itemAbout.SetBitmap(wx.Bitmap(self.CreatePath4Icons('about.png')))
        wxglade_tmp_menu.AppendItem(itemAbout)

        # separator
        wxglade_tmp_menu.AppendSeparator()

        # save all menu item
        saveAllItem = wx.MenuItem(wxglade_tmp_menu, wx.NewId(), u"&Save All\tCTRL+S", "", wx.ITEM_NORMAL)
        saveAllItem.Enable(False)
        self.Bind(wx.EVT_MENU, self.OnSaveAll, saveAllItem)
        wxglade_tmp_menu.AppendItem(saveAllItem)

        # separator
        wxglade_tmp_menu.AppendSeparator()

        # exit item
        exitItem = wx.MenuItem(wxglade_tmp_menu, wx.NewId(), u"&Quit\tCTRL+Q", "", wx.ITEM_NORMAL)
        exitItem.SetBitmap(wx.Bitmap(self.CreatePath4Icons('exit.png')))
        self.Bind(wx.EVT_MENU, self.OnExit, exitItem)
        wxglade_tmp_menu.AppendItem(exitItem)

        item = wx.MenuItem(wxglade_tmp_menu2,9999, u"&Browse Models\tCTRL+M", "", wx.ITEM_NORMAL)
        item.SetBitmap(wx.Bitmap(self.CreatePath4Icons('lib.png')))
        self.Bind(wx.EVT_MENU, self.OnModelLibrary, id=9999)
        item.Enable(True)
        wxglade_tmp_menu2.AppendItem(item)

        self.sme_menubar.Append(wxglade_tmp_menu, ("Menu"))
        self.sme_menubar.Append(wxglade_tmp_menu2, ("Library"))
        self.SetMenuBar(self.sme_menubar)
        self.losma = wx.Bitmap(self.CreatePath4Icons('logo_SMETool_small.png'), wx.BITMAP_TYPE_PNG)

        self.SetIcon(wx.Icon(self.CreatePath4Icons('appicon.png'), wx.BITMAP_TYPE_PNG))

        self.notebook_1 = wx.Notebook(self, wx.ID_ANY, style=0)

        # pretty, tiny icons for the notebook tabz - SME needs to look good 2!
        il = wx.ImageList(20, 20)
        self.categoriesTabImg = il.Add(wx.Bitmap(self.CreatePath4Icons('categories.png'), wx.BITMAP_TYPE_PNG))
        self.factsTabImg = il.Add(wx.Bitmap(self.CreatePath4Icons('facts.png'), wx.BITMAP_TYPE_PNG))
        self.secAttrTabImg = il.Add(wx.Bitmap(self.CreatePath4Icons('sec_attr.png'), wx.BITMAP_TYPE_PNG))
        self.rulesTabImg = il.Add(wx.Bitmap(self.CreatePath4Icons('rules.png'), wx.BITMAP_TYPE_PNG))
        self.factsOrderTabImg = il.Add(wx.Bitmap(self.CreatePath4Icons('facts_order.png'), wx.BITMAP_TYPE_PNG))
        self.evaluationRulesTabImg = il.Add(wx.Bitmap(self.CreatePath4Icons('ev_rules.png'), wx.BITMAP_TYPE_PNG))
        self.casesTabImg = il.Add(wx.Bitmap(self.CreatePath4Icons('cases.png'), wx.BITMAP_TYPE_PNG))
        self.notebook_1.AssignImageList(il)

    # -------------------------- TAB1 --------------------------

        # main panel for the first tab
        self.categoriesPanel = wx.Panel(self.notebook_1, wx.ID_ANY)
        # smetool logo
        self.logoSmall1 = wx.StaticBitmap(self.categoriesPanel, -1, self.losma)

        # create buttons, give them actual, meaningful names
        self.loadCategoriesBtn = wx.Button(self.categoriesPanel, label="Load")
        self.saveCategoriesBtn = wx.Button(self.categoriesPanel, label="Save")
        self.addCategoriesBtn = wx.Button(self.categoriesPanel, label="Add")
        self.deleteCategoriesBtn = wx.Button(self.categoriesPanel, label="Delete")
        self.editCategoriesBtn = wx.Button(self.categoriesPanel, label="Edit")

        # do some buttons-bindings
        self.loadCategoriesBtn.Bind(wx.EVT_BUTTON, self.onClickLoadCategories)
        self.saveCategoriesBtn.Bind(wx.EVT_BUTTON, self.onClickSaveCategories)
        self.addCategoriesBtn.Bind(wx.EVT_BUTTON, self.onClickAddCategory)
        self.deleteCategoriesBtn.Bind(wx.EVT_BUTTON, self.onClickDeleteCategory)
        self.editCategoriesBtn.Bind(wx.EVT_BUTTON, self.onClickEditCategory)

        # create list view
        self.categoriesListView = wx.ListView(self.categoriesPanel, wx.ID_ANY, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.categoriesListView.InsertColumn(0, 'Category')
        self.categoriesListView.SetColumnWidth(0, 200)
        self.categoriesListView.InsertColumn(1, 'Description')
        self.categoriesListView.SetColumnWidth(1, 500)
        self.populatelctrl1(Structs.categoryList)

    # -------------------------- TAB2 --------------------------

        #main panel for the second tab
        self.factsPanel = wx.Panel(self.notebook_1, wx.ID_ANY)
        # smetool logo
        self.logoSmall2 = wx.StaticBitmap(self.factsPanel, -1, self.losma)

        # create buttons, give them actual, meaningful names
        self.loadFactsBtn = wx.Button(self.factsPanel, label="Load")
        self.saveFactsBtn = wx.Button(self.factsPanel, label="Save")
        self.addFactsBtn = wx.Button(self.factsPanel, label="Add")
        self.deleteFactBtn = wx.Button(self.factsPanel, label="Delete")
        self.editFactBtn = wx.Button(self.factsPanel, label="Edit")
        self.viewFactsBtn = wx.Button(self.factsPanel, label="View")

        # do some buttons-bindings
        self.loadFactsBtn.Bind(wx.EVT_BUTTON, self.onClickLoadFacts)
        self.saveFactsBtn.Bind(wx.EVT_BUTTON, self.onClickSaveFacts)
        self.addFactsBtn.Bind(wx.EVT_BUTTON, self.onClickAddFact)
        self.deleteFactBtn.Bind(wx.EVT_BUTTON, self.onClickDeleteFact)
        self.editFactBtn.Bind(wx.EVT_BUTTON, self.onClickEditFact)
        self.viewFactsBtn.Bind(wx.EVT_BUTTON, self.onClickViewFact)

        # create list view
        self.factsListView = wx.ListView(self.factsPanel, wx.ID_ANY, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.factsListView.InsertColumn(0, 'Name')
        self.factsListView.SetColumnWidth(0, 100)
        self.factsListView.InsertColumn(1, 'Category')
        self.factsListView.SetColumnWidth(1, 200)
        self.factsListView.InsertColumn(2, 'Description')
        self.factsListView.SetColumnWidth(2, 200)
        self.factsListView.InsertColumn(3, 'Value')
        self.factsListView.SetColumnWidth(3, 200)
        self.populatelctrl2(Structs.factList)

    # -------------------------- TAB3 --------------------------

        #main panel for the third tab
        self.SAPanel = wx.Panel(self.notebook_1, wx.ID_ANY)
        # smetool logo
        self.logoSmall3 = wx.StaticBitmap(self.SAPanel, -1, self.losma)
        
        # create buttons, give them actual, meaningful names
        self.loadSABtn = wx.Button(self.SAPanel, label="Load")
        self.saveSABtn = wx.Button(self.SAPanel, label="Save")
        self.addSABtn = wx.Button(self.SAPanel, label="Add")
        self.deleteSABtn = wx.Button(self.SAPanel, label="Delete")
        self.editSABtn = wx.Button(self.SAPanel, label="Edit")

        # do some buttons-bindings
        self.loadSABtn.Bind(wx.EVT_BUTTON, self.onClickLoadSA)
        self.saveSABtn.Bind(wx.EVT_BUTTON, self.onClickSaveSA)
        self.addSABtn.Bind(wx.EVT_BUTTON, self.onClickAddSA)
        self.deleteSABtn.Bind(wx.EVT_BUTTON, self.onClickDeleteSA)
        self.editSABtn.Bind(wx.EVT_BUTTON, self.onClickEditSA)

        # create list view
        self.SAListView = wx.ListView(self.SAPanel, wx.ID_ANY, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.SAListView.InsertColumn(0, 'Security Attribute')
        self.SAListView.SetColumnWidth(0, 200)
        self.SAListView.InsertColumn(1, 'Description')
        self.SAListView.SetColumnWidth(1, 500)
        self.populatelctrl3(Structs.saList)

    # -------------------------- TAB4 --------------------------

        # main panel for the fourth tab
        self.rulePanel = wx.Panel(self.notebook_1, wx.ID_ANY)
        # smetool logo
        self.logoSmall4 = wx.StaticBitmap(self.rulePanel, -1, self.losma)

        # create buttons, give them actual, meaningful names
        self.loadRuleBtn = wx.Button(self.rulePanel, label="Load")
        self.saveRuleBtn = wx.Button(self.rulePanel, label="Save")
        self.addRuleBtn = wx.Button(self.rulePanel, label="Add")
        self.deleteRuleBtn = wx.Button(self.rulePanel, label="Delete")
        self.editRuleBtn = wx.Button(self.rulePanel, label="Edit")

        # do some buttons-bindings
        self.loadRuleBtn.Bind(wx.EVT_BUTTON, self.onClickLoadRules)
        self.saveRuleBtn.Bind(wx.EVT_BUTTON, self.onClickSaveRules)
        self.addRuleBtn.Bind(wx.EVT_BUTTON, self.onClickAddRule)
        self.deleteRuleBtn.Bind(wx.EVT_BUTTON, self.onClickDeleteRule)
        self.editRuleBtn.Bind(wx.EVT_BUTTON, self.onClickEditRule)

        # create list view
        self.ruleListView = wx.ListView(self.rulePanel, wx.ID_ANY, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.ruleListView.InsertColumn(0, 'Rule')
        self.ruleListView.SetColumnWidth(0, 1000)
        self.populatelctrl4(Structs.ruleList)

    # -------------------------- TAB5 --------------------------

        #main panel for the fifth tab
        self.factsOrderPanel = wx.Panel(self.notebook_1, wx.ID_ANY)
        # smetool logo
        self.logoSmall5 = wx.StaticBitmap(self.factsOrderPanel, -1, self.losma)

        # create buttons, give them actual, meaningful names
        self.loadFactsOrderBtn = wx.Button(self.factsOrderPanel, label="Load")
        self.saveFactsOrderBtn = wx.Button(self.factsOrderPanel, label="Save")
        self.addFactsOrderBtn = wx.Button(self.factsOrderPanel, label="Add")
        self.deleteFactsOrderBtn = wx.Button(self.factsOrderPanel, label="Delete")
        self.editFactsOrderBtn = wx.Button(self.factsOrderPanel, label="Edit")

        # do some buttons-bindings
        self.loadFactsOrderBtn.Bind(wx.EVT_BUTTON, self.onClickLoadFOs)
        self.saveFactsOrderBtn.Bind(wx.EVT_BUTTON, self.onClickSaveFOs)
        self.addFactsOrderBtn.Bind(wx.EVT_BUTTON, self.onClickAddFO)
        self.deleteFactsOrderBtn.Bind(wx.EVT_BUTTON, self.onClickDeleteFO)
        self.editFactsOrderBtn.Bind(wx.EVT_BUTTON, self.onClickEditFO)

        # create list view
        self.factsOrderListView = wx.ListView(self.factsOrderPanel, wx.ID_ANY, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.factsOrderListView.InsertColumn(0, 'Facts Order')
        self.factsOrderListView.SetColumnWidth(0, 500)
        self.factsOrderListView.InsertColumn(1, 'Security Attribute')
        self.factsOrderListView.SetColumnWidth(1, 500)
        self.populatelctrl6(Structs.foList)

    # -------------------------- TAB6 --------------------------

        #main panel for the sixth tab
        self.evaluationRulesPanel = wx.Panel(self.notebook_1, wx.ID_ANY)
        # smetool logo
        self.logoSmall6 = wx.StaticBitmap(self.evaluationRulesPanel, -1, self.losma)

        # create buttons, give them actual, meaningful names
        self.loadEvaluationRulesBtn = wx.Button(self.evaluationRulesPanel, label="Load")
        self.saveEvaluationRulesBtn = wx.Button(self.evaluationRulesPanel, label="Save")
        self.addEvaluationRulesBtn = wx.Button(self.evaluationRulesPanel, label="Add")
        self.deleteEvaluationRuleBtn = wx.Button(self.evaluationRulesPanel, label="Delete")
        self.editEvaluationRuleBtn = wx.Button(self.evaluationRulesPanel, label="Edit")

        # do some buttons-bindings
        self.loadEvaluationRulesBtn.Bind(wx.EVT_BUTTON, self.onClickLoadERs)
        self.saveEvaluationRulesBtn.Bind(wx.EVT_BUTTON, self.onClickSaveERs)
        self.addEvaluationRulesBtn.Bind(wx.EVT_BUTTON, self.onClickAddER)
        self.deleteEvaluationRuleBtn.Bind(wx.EVT_BUTTON, self.onClickDeleteER)
        self.editEvaluationRuleBtn.Bind(wx.EVT_BUTTON, self.onClickEditER)

        # create list view
        self.evaluationRulesListView = wx.ListView(self.evaluationRulesPanel, wx.ID_ANY, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.evaluationRulesListView.InsertColumn(0, 'Evaluation rule')
        self.evaluationRulesListView.SetColumnWidth(0, 300)
        self.evaluationRulesListView.InsertColumn(1, 'Influence Value')
        self.evaluationRulesListView.SetColumnWidth(1, 100)
        self.evaluationRulesListView.InsertColumn(2, 'Security Attribute')
        self.evaluationRulesListView.SetColumnWidth(2, 500)
        self.populatelctrl10(Structs.erList)

    # -------------------------- TAB7 --------------------------

        #main panel for the seventh tab
        self.casesPanel = wx.Panel(self.notebook_1, wx.ID_ANY)
        # smetool logo
        self.logoSmall7 = wx.StaticBitmap(self.casesPanel, -1, self.losma)

        # create buttons, give them actual, meaningful names
        self.loadCasesBtn = wx.Button(self.casesPanel, label="Load")
        self.saveCasesBtn = wx.Button(self.casesPanel, label="Save")
        self.addCasesBtn = wx.Button(self.casesPanel, label="Add")
        self.deleteCasesBtn = wx.Button(self.casesPanel, label="Delete")
        self.editCasesBtn = wx.Button(self.casesPanel, label="Edit")
        self.evaluateCasesBtn = wx.Button(self.casesPanel, label="Evaluate")
        self.evaluateAllCasesBtn = wx.Button(self.casesPanel, label="Evaluate All")

        # do some buttons-bindings
        self.loadCasesBtn.Bind(wx.EVT_BUTTON, self.onClickLoadCases)
        self.saveCasesBtn.Bind(wx.EVT_BUTTON, self.onClickSaveCases)
        self.addCasesBtn.Bind(wx.EVT_BUTTON, self.onClickAddCase)
        self.deleteCasesBtn.Bind(wx.EVT_BUTTON, self.onClickDeleteCase)
        self.editCasesBtn.Bind(wx.EVT_BUTTON, self.onClickEditCase)
        self.evaluateCasesBtn.Bind(wx.EVT_BUTTON, self.onClickEvaluateCase)
        self.evaluateAllCasesBtn.Bind(wx.EVT_BUTTON, self.onClickEvaluateAllCases)

        # create list view
        self.casesListView = wx.ListView(self.casesPanel, wx.ID_ANY, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.casesListView.InsertColumn(0, 'Case Number')
        self.casesListView.SetColumnWidth(0, 200)
        self.casesListView.InsertColumn(1, 'Facts')
        self.casesListView.SetColumnWidth(1, 500)
        self.casesListView.InsertColumn(2, 'Description')
        self.casesListView.SetColumnWidth(2, 500)
        self.populatelctrl11(Structs.caseList)

        self.__set_properties()
        self.__do_layout()

    def CreatePath4Icons(self, resourceName):
        return os.path.dirname(os.path.abspath(__file__))+"/img/"+resourceName

    def ShowMessage(self, message):
        wx.MessageBox(message, 'Dialog', wx.OK | wx.ICON_INFORMATION)

    def OnAboutBox(self, e):
        info = wx.AboutDialogInfo()
        info.SetIcon(wx.Icon(self.CreatePath4Icons("logo_SMETool_small.png"), wx.BITMAP_TYPE_PNG))
        info.SetName("Security Mechanisms Evaluation Tool")
        info.SetVersion('(v 0.9.3)')
        info.SetDescription("Michail Mokkas, mokkas@pjwstk.edu.pl")
        info.SetCopyright('(C) 2014')
        wx.AboutBox(info)

    def OnModelLibrary(self, e):
        dia = ModelLibraryDialog(self, -1, 'Model Library')
        dia.ShowModal()
        dia.Destroy()

    def OnLoadAll(self, e):
        dir = os.path.dirname(os.path.abspath(__file__))
        Utility.loadCategories(dir+"/files/categoryList.pickle")
        Utility.loadFacts(dir+"/files/factList.pickle")
        Utility.loadSA(dir+"/files/saList.pickle")
        Utility.loadRules(dir+"/files/ruleList.pickle")
        Utility.loadFOs(dir+"/files/foList.pickle")
        Utility.loadERs(dir+"/files/erList.pickle")
        Utility.loadCases(dir+"/files/caseList.pickle")
        self.populatelctrl1(Structs.categoryList)
        self.populatelctrl2(Structs.factList)
        self.populatelctrl3(Structs.saList)
        self.populatelctrl4(Structs.ruleList)
        self.populatelctrl6(Structs.foList)
        self.populatelctrl10(Structs.erList)
        self.populatelctrl11(Structs.caseList)

    def OnSaveAll(self, e):

        saveFileDialog = wx.FileDialog(self, "Choose A File To Save Model To:", "", "",
                                       "SME Tool Files (*.sme)|*.sme",
                                       wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        saveFileDialog.ShowModal()
        Utility.saveCategories(saveFileDialog.GetPath()+"_category.sme")
        Utility.saveFacts(saveFileDialog.GetPath()+"_fact.sme")
        Utility.saveSA(saveFileDialog.GetPath()+"_sa.sme")
        Utility.saveRules(saveFileDialog.GetPath()+"_rule.sme")
        Utility.saveFOs(saveFileDialog.GetPath()+"_fo.sme")
        Utility.saveERs(saveFileDialog.GetPath()+"_er.sme")
        Utility.saveCases(saveFileDialog.GetPath()+"_case.sme")
        saveFileDialog.Destroy()

        #Utility.saveCategories()
        #Utility.saveFacts()
        #Utility.saveSA()
        #Utility.saveRules()
        #Utility.saveFOs()
        #Utility.saveERs()
        #Utility.saveCases()
        self.populatelctrl1(Structs.categoryList)
        self.populatelctrl2(Structs.factList)
        self.populatelctrl3(Structs.saList)
        self.populatelctrl4(Structs.ruleList)
        self.populatelctrl6(Structs.foList)
        self.populatelctrl10(Structs.erList)
        self.populatelctrl11(Structs.caseList)

    def OnExit(self, e):
        self.Close()

#Category
    def onClickLoadCategories(self, e):
        dlg = wx.FileDialog(self, "Choose a file to load categories from:")
        dlg.ShowModal()
        dlg.Destroy()
        Utility.loadCategories(dlg.GetPath())
        self.populatelctrl1(Structs.categoryList)

    def onClickSaveCategories(self, e):
        dlg = wx.FileDialog(self, "Choose a file to save categories to:")
        dlg.ShowModal()
        dlg.Destroy()
        Utility.saveCategories(dlg.GetPath())


    def onClickAddCategory(self, e):
        dia = AddCategoryDialog(self, -1, 'Add a category')
        dia.ShowModal()
        dia.Destroy()

    def onClickDeleteCategory(self, e):
        index = 0
        for item in Structs.factList:
            if(item.category==Structs.categoryList[self.categoriesListView.GetFocusedItem()].name):
                self.onFactDelete(item.name+'('+item.category+')')
                del Structs.factList[index]
                self.populatelctrl2(Structs.factList)
            index=index+1
        del Structs.categoryList[self.categoriesListView.GetFocusedItem()]
        self.populatelctrl1(Structs.categoryList)

    def onClickEditCategory(self, e):
        dia = EditCategoryDialog(self, -1, 'Edit the Category')
        dia.ShowModal()
        dia.Destroy()

    def populatelctrl1(self, thelist):
        self.categoriesListView.DeleteAllItems()
        for item in thelist:
            self.categoriesListView.Append((item.name,item.description))

#Fact
    def onClickLoadFacts(self, e):
        dlg = wx.FileDialog(self, "Choose a file to load facts from:")
        dlg.ShowModal()
        dlg.Destroy()
        Utility.loadFacts(dlg.GetPath())
        self.populatelctrl2(Structs.factList)

    def onClickSaveFacts(self, e):
        dlg = wx.FileDialog(self, "Choose a file to save facts to:")
        dlg.ShowModal()
        dlg.Destroy()
        Utility.saveFacts(dlg.GetPath())

    def onClickAddFact(self, e):
        dia = AddFactDialog(self, -1, 'Add a fact')
        dia.ShowModal()
        dia.Destroy()

    def onClickDeleteFact(self, e):
        self.onFactDelete(Structs.factList[self.factsListView.GetFocusedItem()].name+'('+Structs.factList[self.factsListView.GetFocusedItem()].category+')')
        del Structs.factList[self.factsListView.GetFocusedItem()]
        self.populatelctrl2(Structs.factList)

    def onClickEditFact(self, e):
        dia = EditFactDialog(self, -1, 'Edit the Fact')
        dia.ShowModal()
        dia.Destroy()

    def onClickViewFact(self, e):
        dia = ViewFactsDialog(self, -1, 'View Facts')
        dia.ShowModal()
        dia.Destroy()

    def populatelctrl2(self, thelist):
        self.factsListView.DeleteAllItems()
        for item in thelist:
            self.factsListView.Append((item.name,item.category,item.description,item.value))

    def onFactDelete(self, catfact):
        index = 0
        for item in Structs.ruleList:
            for element in Structs.ruleList[index].elements:
                if(element==catfact):
                    del Structs.ruleList[index]
                    self.populatelctrl4(Structs.ruleList)
            index=index+1
        index = 0
        for item in Structs.foList:
            for element in Structs.foList[index].elements:
                if(element==catfact):
                    del Structs.foList[index]
                    self.populatelctrl6(Structs.foList)
            index=index+1
        index = 0
        for item in Structs.erList:
            for element in Structs.erList[index].elements:
                if(element==catfact):
                    del Structs.erList[index]
                    self.populatelctrl10(Structs.erList)
            index=index+1
        index = 0
        for item in Structs.caseList:
            for fact in Structs.caseList[index].facts:
                if(fact==catfact):
                    del Structs.caseList[index]
                    self.populatelctrl11(Structs.caseList)
            index=index+1

    def onFactChange(self, oldcatfact, newcatfact):
        index = 0
        index2 = 0
        for item in Structs.ruleList:
            for element in Structs.ruleList[index].elements:
                if(element==oldcatfact):
                    Structs.ruleList[index].elements[index2] = newcatfact
                    self.populatelctrl4(Structs.ruleList)
                index2=index2+1
            index=index+1
        index = 0
        index2 = 0
        for item in Structs.foList:
            for element in Structs.foList[index].elements:
                if(element==oldcatfact):
                    Structs.foList[index].elements[index2] = newcatfact
                    self.populatelctrl6(Structs.foList)
                index2=index2+1
            index=index+1
        index = 0
        index2 = 0
        for item in Structs.erList:
            for element in Structs.erList[index].elements:
                if(element==oldcatfact):
                    Structs.erList[index].elements[index2] = newcatfact
                    self.populatelctrl10(Structs.erList)
                index2=index2+1
            index=index+1
        index = 0
        index2 = 0
        for item in Structs.caseList:
            for fact in Structs.caseList[index].facts:
                if(fact==oldcatfact):
                    Structs.caseList[index].facts[index2] = newcatfact
                    self.populatelctrl11(Structs.caseList)
                index2=index2+1
            index=index+1

#Security attribute
    def onClickLoadSA(self, e):
        dlg = wx.FileDialog(self, "Choose a file to load the security attributes from:")
        dlg.ShowModal()
        dlg.Destroy()
        Utility.loadSA(dlg.GetPath())
        self.populatelctrl3(Structs.saList)

    def onClickSaveSA(self, e):
        dlg = wx.FileDialog(self, "Choose a file to save the security attributes to:")
        dlg.ShowModal()
        dlg.Destroy()
        Utility.saveSA(dlg.GetPath())

    def onClickAddSA(self, e):
        dia = AddSADialog(self, -1, 'Add a security attribute')
        dia.ShowModal()
        dia.Destroy()

    def onClickDeleteSA(self, e):
        index = 0
        for item in Structs.foList:
            if(item.security_attribute==Structs.saList[self.SAListView.GetFocusedItem()].name):
               del Structs.foList[index]
               self.populatelctrl6(Structs.foList)
            index=index+1
        index = 0
        for item in Structs.erList:
            if(item.security_attribute==Structs.saList[self.SAListView.GetFocusedItem()].name):
               del Structs.erList[index]
               self.populatelctrl10(Structs.erList)
            index=index+1
        del Structs.saList[self.SAListView.GetFocusedItem()]
        self.populatelctrl3(Structs.saList)

    def onClickEditSA(self, e):
        dia = EditSADialog(self, -1, 'Edit the security attribute')
        dia.ShowModal()
        dia.Destroy()

    def populatelctrl3(self, thelist):
        self.SAListView.DeleteAllItems()
        for item in thelist:
            self.SAListView.Append((item.name,item.description))

#Rule
    def onClickLoadRules(self, e):
        dlg = wx.FileDialog(self, "Choose a file to load the rules from:")
        dlg.ShowModal()
        dlg.Destroy()
        Utility.loadRules(dlg.GetPath())
        self.populatelctrl4(Structs.ruleList)

    def onClickSaveRules(self, e):
        dlg = wx.FileDialog(self, "Choose a file to save the rules to:")
        dlg.ShowModal()
        dlg.Destroy()
        Utility.saveRules(dlg.GetPath())

    def onClickAddRule(self, e):
        dia = AddRuleDialog(self, -1, 'Add a Rule')
        dia.ShowModal()
        dia.Destroy()

    def onClickDeleteRule(self, e):
        del Structs.ruleList[self.ruleListView.GetFocusedItem()]
        self.populatelctrl4(Structs.ruleList)

    def onClickEditRule(self, e):
        dia = EditRuleDialog(self, -1, 'Edit the Rule')
        dia.ShowModal()
        dia.Destroy()

    def populatelctrl4(self, thelist):
        self.ruleListView.DeleteAllItems()
        for item in thelist:
            ele = ''
            for element in item.elements:
                ele = ele + element
            self.ruleListView.Append((ele,)) # (ele,) != (ele) != (ele,"")

#Facts order
    def onClickLoadFOs(self, e):
        dlg = wx.FileDialog(self, "Choose a file to load facts order from:")
        dlg.ShowModal()
        dlg.Destroy()
        Utility.loadFOs(dlg.GetPath())
        self.populatelctrl6(Structs.foList)

    def onClickSaveFOs(self, e):
        dlg = wx.FileDialog(self, "Choose a file to save facts order to:")
        dlg.ShowModal()
        dlg.Destroy()
        Utility.saveFOs(dlg.GetPath())

    def onClickAddFO(self, e):
        dia = AddFODialog(self, -1, 'Add the Facts Order')
        dia.ShowModal()
        dia.Destroy()

    def onClickDeleteFO(self, e):
        del Structs.foList[self.factsOrderListView.GetFocusedItem()]
        self.populatelctrl6(Structs.foList)

    def onClickEditFO(self, e):
        dia = EditFODialog(self, -1, 'Edit the Facts Order')
        dia.ShowModal()
        dia.Destroy()

    def populatelctrl6(self, thelist):
        ele = ''
        self.factsOrderListView.DeleteAllItems()
        for item in thelist:
            for element in item.elements:
                ele = ele + element
            self.factsOrderListView.Append((ele,item.security_attribute))
            ele = ''

#Evaluation rules
    def onClickLoadERs(self, e):
        dlg = wx.FileDialog(self, "Choose a File to Load Evaluation Rules from:")
        dlg.ShowModal()
        dlg.Destroy()
        Utility.loadERs(dlg.GetPath())
        self.populatelctrl10(Structs.erList)

    def onClickSaveERs(self, e):
        dlg = wx.FileDialog(self, "Choose a File to Save Evaluation Rules from:")
        dlg.ShowModal()
        dlg.Destroy()
        Utility.saveERs(dlg.GetPath())

    def onClickAddER(self, e):
        dia = AddERDialog(self, -1, 'Add an Evaluation Rule')
        dia.ShowModal()
        dia.Destroy()

    def onClickDeleteER(self, e):
        del Structs.erList[self.evaluationRulesListView.GetFocusedItem()]
        self.populatelctrl10(Structs.erList)

    def onClickEditER(self, e):
        dia = EditERDialog(self, -1, 'Edit the Evaluation Rules')
        dia.ShowModal()
        dia.Destroy()

    def populatelctrl10(self, thelist):
        ele = ''
        self.evaluationRulesListView.DeleteAllItems()
        for item in thelist:
            for element in item.elements:
                ele = ele + element
            self.evaluationRulesListView.Append((ele, item.influence, item.security_attribute))
            ele = ''

#Case
    def onClickLoadCases(self, e):
        dlg = wx.FileDialog(self, "Choose a File to Load Cases from:")
        dlg.ShowModal()
        dlg.Destroy()
        Utility.loadCases(dlg.GetPath())
        self.populatelctrl11(Structs.caseList)

    def onClickSaveCases(self, e):
        dlg = wx.FileDialog(self, "Choose a File to Save Cases to:")
        dlg.ShowModal()
        dlg.Destroy()
        Utility.saveCases(dlg.GetPath())

    def onClickAddCase(self, e):
        dia = AddCaseDialog(self, -1, 'Add a Case')
        dia.ShowModal()
        dia.Destroy()

    def onClickDeleteCase(self, e):
        del Structs.caseList[self.casesListView.GetFocusedItem()]
        self.populatelctrl11(Structs.caseList)

    def onClickEditCase(self, e):
        dia = EditCaseDialog(self, -1, 'Edit the Case')
        dia.ShowModal()
        dia.Destroy()

    def onClickEvaluateCase(self, e):
        dia = EvaluateCaseDialog(self, -1, 'Case QoP Evaluation')
        dia.ShowModal()
        dia.Destroy()

    def onClickEvaluateAllCases(self, e):
        dia = EvaluateAllCasesDialog(self, -1, 'All Cases QoP Eavaluation')
        dia.ShowModal()
        dia.Destroy()

    def populatelctrl11(self, thelist):
        ele = ''
        self.casesListView.DeleteAllItems()
        for item in thelist:
            for element in item.facts:
                ele = ele + ' ' + element
            self.casesListView.Append((item.casename, ele, item.description))
            ele = ''


    def __set_properties(self):
        self.SetTitle(("Security Mechanisms Evaluation Tool"))

    def __do_layout(self):

        # -------------------------- TAB1 --------------------------

        # create horizontal sizer for all the buttons
        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(self.logoSmall1, 0, wx.ALIGN_CENTER, 5)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.EXPAND, 5)
        buttonsSizer.Add(self.loadCategoriesBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.saveCategoriesBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.addCategoriesBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.deleteCategoriesBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.editCategoriesBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # do the final alignment
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.categoriesListView, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(buttonsSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.categoriesPanel.SetSizer(sizer)

        # -------------------------- TAB2 --------------------------

        # create horizontal sizer for all the buttons
        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(self.logoSmall2, 0, wx.ALIGN_CENTER, 5)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.EXPAND, 5)
        buttonsSizer.Add(self.loadFactsBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.saveFactsBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.addFactsBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.deleteFactBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.editFactBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.viewFactsBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # do the final alignment
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.factsListView, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(buttonsSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.factsPanel.SetSizer(sizer)

        # -------------------------- TAB3 --------------------------

        # create horizontal sizer for all the buttons
        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(self.logoSmall3, 0, wx.ALIGN_CENTER, 5)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.EXPAND, 5)
        buttonsSizer.Add(self.loadSABtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.saveSABtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.addSABtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.deleteSABtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.editSABtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # do the final alignment
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.SAListView, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(buttonsSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SAPanel.SetSizer(sizer)

        # -------------------------- TAB4 --------------------------

        # create horizontal sizer for all the buttons
        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(self.logoSmall4, 0, wx.ALIGN_CENTER, 5)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.EXPAND, 5)
        buttonsSizer.Add(self.loadRuleBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.saveRuleBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.addRuleBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.deleteRuleBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.editRuleBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # do the final alignment
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.ruleListView, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(buttonsSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.rulePanel.SetSizer(sizer)

        # -------------------------- TAB5 --------------------------

        # create horizontal sizer for all the buttons
        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(self.logoSmall5, 0, wx.ALIGN_CENTER, 5)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.EXPAND, 5)
        buttonsSizer.Add(self.loadFactsOrderBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.saveFactsOrderBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.addFactsOrderBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.deleteFactsOrderBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.editFactsOrderBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # do the final alignment
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.factsOrderListView, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(buttonsSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.factsOrderPanel.SetSizer(sizer)

        # -------------------------- TAB6 --------------------------

        # create horizontal sizer for all the buttons
        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(self.logoSmall6, 0, wx.ALIGN_CENTER, 5)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.EXPAND, 5)
        buttonsSizer.Add(self.loadEvaluationRulesBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.saveEvaluationRulesBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.addEvaluationRulesBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.deleteEvaluationRuleBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.editEvaluationRuleBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # do the final alignment
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.evaluationRulesListView, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(buttonsSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.evaluationRulesPanel.SetSizer(sizer)

        # -------------------------- TAB7 --------------------------

        # create horizontal sizer for all the buttons
        buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsSizer.Add(self.logoSmall7, 0, wx.ALIGN_CENTER, 5)
        buttonsSizer.Add(wx.StaticText(self), 1, wx.EXPAND, 5)
        buttonsSizer.Add(self.loadCasesBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.saveCasesBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.addCasesBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.deleteCasesBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.editCasesBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.evaluateCasesBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        buttonsSizer.Add(self.evaluateAllCasesBtn, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # do the final alignment
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.casesListView, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(buttonsSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.casesPanel.SetSizer(sizer)

        #ALLTABS
        self.notebook_1.AddPage(self.categoriesPanel, ("Categories"))
        self.notebook_1.SetPageImage(0, self.categoriesTabImg)
        self.notebook_1.AddPage(self.factsPanel, ("Facts"))
        self.notebook_1.SetPageImage(1, self.factsTabImg)
        self.notebook_1.AddPage(self.SAPanel, ("Security Attributes"))
        self.notebook_1.SetPageImage(2, self.secAttrTabImg)
        self.notebook_1.AddPage(self.rulePanel, ("Rules"))
        self.notebook_1.SetPageImage(3, self.rulesTabImg)
        self.notebook_1.AddPage(self.factsOrderPanel, ("Facts Order"))
        self.notebook_1.SetPageImage(4, self.factsOrderTabImg)
        self.notebook_1.AddPage(self.evaluationRulesPanel, ("Evaluation Rules"))
        self.notebook_1.SetPageImage(5, self.evaluationRulesTabImg)
        self.notebook_1.AddPage(self.casesPanel, ("Cases"))
        self.notebook_1.SetPageImage(6, self.casesTabImg)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.notebook_1, 1, wx.EXPAND, 0, 5)
        self.SetSizer(sizer)
        self.Layout()

if __name__ == "__main__":

    app = wx.App()
    smetool = SMETool(None, wx.ID_ANY, "")
    smetool.SetClientSize(wx.Size(850,550))
    smetool.CenterOnScreen()
    smetool.Show()
    app.SetTopWindow(smetool)
    app.MainLoop()
