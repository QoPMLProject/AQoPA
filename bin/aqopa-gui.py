'''
Created on 05-09-2013

@author: Damian Rusinek <damian.rusinek@gmail.com>
'''

import wx

TYPE_EVT_MODEL_CHANGED = wx.NewEventType()
EVT_MODEL_CHANGED = wx.PyEventBinder(TYPE_EVT_MODEL_CHANGED, 1)

class ModelChangedEvent(wx.PyCommandEvent):
    
    def __init__(self, evtType, id, modelText="", 
                 metricsText="", configurationText=""):
        """ """
        wx.PyCommandEvent.__init__(self, evtType, id)
        self.modelText = modelText
        self.metricsText = metricsText
        self.configurationText = configurationText
        
class ParserDataPanel(wx.Panel):
    """ 
    Panel containing text area for one of model parts: model, metrics, configuration.
    """
    
    def __init__(self, parent):
        """ """
        wx.Panel.__init__(self, parent=parent)
    
        self.dataTextArea = wx.TextCtrl(self, style=wx.TE_MULTILINE)
    
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.dataTextArea, 1, wx.EXPAND)
        
        self.SetSizer(sizer)
        
class ModelNotebook(wx.Notebook):
    """ """
    
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent)

        self.modelTab = ParserDataPanel(self)
        self.Bind(wx.EVT_TEXT, self.OnTextChange, self.modelTab.dataTextArea)
        self.AddPage(self.modelTab, "Model")
        
        self.metricsTab = ParserDataPanel(self)
        self.Bind(wx.EVT_TEXT, self.OnTextChange, self.metricsTab.dataTextArea)
        self.AddPage(self.metricsTab, "Metrics")
        
        self.configurationTab = ParserDataPanel(self)
        self.Bind(wx.EVT_TEXT, self.OnTextChange, self.configurationTab.dataTextArea)
        self.AddPage(self.configurationTab, "Configuration")
        
    def LoadModelFile(self, filePath):
        self.modelTab.dataTextArea.LoadFile(filePath)
        
    def LoadMetricsFile(self, filePath):
        self.metricsTab.dataTextArea.LoadFile(filePath)
        
    def LoadConfigurationFile(self, filePath):
        self.configurationTab.dataTextArea.LoadFile(filePath)
        
    def GetModelData(self):
        return self.modelTab.dataTextArea.GetValue().strip()
        
    def GetMetricsData(self):
        return self.metricsTab.dataTextArea.GetValue().strip()
        
    def GetConfigurationData(self):
        return self.configurationTab.dataTextArea.GetValue().strip()
        
    def OnTextChange(self, event):
        self.GetEventHandler().ProcessEvent(ModelChangedEvent(TYPE_EVT_MODEL_CHANGED, 1,
                                                              modelText=self.GetModelData(),
                                                              metricsText=self.GetMetricsData(),
                                                              configurationText=self.GetConfigurationData()))
        
class MainFrame(wx.Frame):
    """ """
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        ###########
        # MENUBAR 
        ###########        
        
        menuBar = wx.MenuBar()

        fileMenu = wx.Menu()
        item = fileMenu.Append(wx.ID_ABOUT, text="About AQoPA")
        self.Bind(wx.EVT_MENU, self.OnAbout, item)
        fileMenu.AppendSeparator()
        item = fileMenu.Append(-1, text="Load &Model")
        self.Bind(wx.EVT_MENU, self.OnLoadModel, item)
        item = fileMenu.Append(-1, text="Load M&etrics")
        item = fileMenu.Append(-1, text="Load &Configuration")
        fileMenu.AppendSeparator()
        self.parseModelItem = fileMenu.Append(-1, text="Parse Model")
        self.parseModelItem.Enable(False)
        fileMenu.AppendSeparator()
        item = fileMenu.Append(wx.ID_EXIT, text="&Quit")
        self.Bind(wx.EVT_MENU, self.OnQuit, item)
        menuBar.Append(fileMenu, "&File")
        
        modulesMenu = wx.Menu()
        item = modulesMenu.Append(-1, text="Choose")
        item = modulesMenu.Append(-1, text="Configure")
        item.Enable(False)
        menuBar.Append(modulesMenu, "&Modules")
        
        runMenu = wx.Menu()
        item = runMenu.Append(-1, text="Run")
        item.Enable(False)
        menuBar.Append(runMenu, "&Run")
        
        self.SetMenuBar(menuBar)
        
        ###########
        # SIZERS 
        ###########
        
        panel = wx.Panel(self)
        
        self.modelNotebook = ModelNotebook(panel)
        self.Bind(EVT_MODEL_CHANGED, self.OnModelChanged, self.modelNotebook)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.modelNotebook, 1, wx.ALL|wx.EXPAND, 5)
        panel.SetSizer(sizer)
        
        self.Layout()
        
    def OnQuit(self, event=None):
        """ Close app """
        self.Close()
        
    def OnAbout(self, event=None):
        """ Show about info """
        dlg = wx.MessageDialog(self, "Automated Quality of Protection Analysis tool of QoP-ML models\n\nProject Home: http://qopml.org", 
                               "About AQoPA", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnLoadModel(self, event):
        """ Load model file """
        ofdlg = wx.FileDialog(self, "Load file", "", "", "QoP-ML Files (*.qopml)|*.qopml", 
                              wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        ofdlg.ShowModal()
        self.modelNotebook.LoadModelFile(ofdlg.GetPath())
        ofdlg.Destroy()
        
    def OnModelChanged(self, event):
        """ """
        modelReady = event.modelText != ""
        modelReady = modelReady and ( event.metricsText != "" )
        modelReady = modelReady and ( event.configurationText != "" )
        
        self.parseModelItem.Enable(modelReady)
        
class AqopaApp(wx.App):
    
    def OnInit(self):
        frame = MainFrame(None, title="AQoPA")
        frame.Show(True)
        self.SetTopWindow(frame)
        return True


def main():
    app = AqopaApp(False)
    app.MainLoop()


if __name__ == "__main__":
    main()