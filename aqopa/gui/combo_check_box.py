#!/usr/bin/env python

import wx
import wx.combo

"""
@file       combo_check_box.py
@brief      mixed combo-check-box widget, needed for modules configuration
            and versions choosing [and probably some more GUI stuff]
@author     Katarzyna Mazur
@date       created on 12-05-2014 by Katarzyna Mazur
"""

class ComboCheckBox(wx.combo.ComboPopup):

    def Init(self):
        """
        @brief overrides Init method from the ComboPopup base class
        """

        # possible choices (checkboxes) displayed in combobox, empty at first
        self.choicesList = []

    def OnComboKeyEvent(self, event):
        """
        @brief receives key events from the parent ComboCtrl
        """
        wx.ComboPopup.OnComboKeyEvent(self, event)

    def Create(self, parent):
        """
        @brief creates the popup child control, returns true for success
        """

        # create checkbox list - use default wxpython's widget
        self.checkBoxList = wx.CheckListBox(parent)
        # react on checking / unchecking checkboxes in the checkbox list
        self.checkBoxList.Bind(wx.EVT_LISTBOX, self.OnListBoxClicked)
        return True

    def ClearChoices(self):
        del self.choicesList[:]

    def SetChoices(self, choices):
        """
        @brief initializes combobox with checkboxes values
        """

        # clear current content from combobox
        self.checkBoxList.Clear()
        # add all the elements from the list to the combo -
        self.checkBoxList.AppendItems(choices)

    def CheckIfAnythingIsSelected(self):
        """
        @brief checks if anything is selected on combobox,
        if at least one item is selected, returns True,
        otherwise False
        """
        for i in range(self.checkBoxList.GetCount()) :
            if self.checkBoxList.IsChecked(i) :
                return True
        return False

    def GetSelectedItemsCount(self):
        """
        @brief counts selected items (checkboxes) in
        our combobox, returns the number of the
        checked checkboxes
        """
        count = 0
        for i in range(self.checkBoxList.GetCount()) :
            if self.checkBoxList.IsChecked(i) :
                count += 1
        return count

    def GetControl(self):
        """
        @brief returns the widget that is to be used for the popup
        """
        return self.checkBoxList

    def OnListBoxClicked(self, evt):
        """
        @brief returns selected items in checkbox list
        """
        return [str(self.checkBoxList.GetString(i)) for i in range(self.checkBoxList.GetCount()) if
                        self.checkBoxList.IsChecked(i)]

    def GetSelectedItems(self):
        """
        @brief returns selected items in checkbox list
        """
        return [str(self.checkBoxList.GetString(i)) for i in range(self.checkBoxList.GetCount()) if
                        self.checkBoxList.IsChecked(i)]

    def OnPopup(self):
        """
        @brief called immediately after the popup is shown
        """
        wx.combo.ComboPopup.OnPopup(self)

    def GetAdjustedSize(self, minWidth, prefHeight, maxHeight):
        """
        @brief returns final size of popup - set prefHeight to 100
        in order to drop-down the popup and add vertical scrollbar
        if needed
        """
        return wx.combo.ComboPopup.GetAdjustedSize(self, minWidth, 100, maxHeight)

"""
@brief  Simple testing (example usage), should be removed or commented
"""

"""
# fast'n'dirty code for testing purposes ONLY!
class TestMePanel(wx.Panel):
    def __init__(self, parent, log):
        self.log = log
        wx.Panel.__init__(self, parent, -1)
        fgs = wx.FlexGridSizer(cols=3, hgap=10, vgap=10)

        # this is how we should use this combo check box widget
        # EXAMPLE USAGE
        cc = wx.combo.ComboCtrl(self)
        self.tcp = ComboCheckBox()
        cc.SetPopupControl(self.tcp)
        self.tcp.SetChoices(['Time Analysis', 'Energy consumption'])
        # second 'Set' removes previous - that's perfectly what we want
        self.tcp.SetChoices(['Time Analysis', 'Energy consumption', 'Reputation'])
        cc.SetText('...')

        # other, non important stuff
        fgs.Add(cc, 1, wx.EXPAND | wx.ALL, 20)
        butt = wx.Button(self, -0, "Check Selected")
        fgs.Add(butt, 1, wx.EXPAND | wx.ALL, 20)
        butt.Bind(wx.EVT_BUTTON, self.OnButtonClicked)
        box = wx.BoxSizer()
        box.Add(fgs, 1, wx.EXPAND | wx.ALL, 20)
        self.CentreOnParent()
        self.SetSizer(box)

    def OnButtonClicked(self, event=None):
        print self.tcp.GetSelectedItems()


class MainFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent)
        panel = TestMePanel(self, None)


if __name__ == "__main__":
    app = wx.App(0)
    frame = MainFrame(None)
    frame.CenterOnScreen()
    frame.Show()
    app.MainLoop()
"""