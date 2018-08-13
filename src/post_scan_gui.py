import wx

class PostScanGUI(wx.Frame):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent

        # UI Elements
        self.option_rbox = wx.RadioBox(self,
                                       label="Options",
                                       choices=['Zoom Scan', 'Correct Previous Value', 'Save Data', 'Exit'],
                                       style=wx.RA_SPECIFY_COLS,
                                       majorDimension=1)
        self.select_btn = wx.Button(self, wx.ID_ANY, "Select")
        self.Bind(wx.EVT_BUTTON, self.return_selection, self.select_btn)
        # Sizers/Layout, Static Lines, & Static Boxes
        #self.radio_sizer = wx.StaticBoxSizer(wx.Vertical, self, "Options")
        self.mainh_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.mainh_sizer.Add(self.option_rbox, proportion=1, border=5, flag=wx.EXPAND | wx.ALL)
        self.mainh_sizer.Add()
        self.SetSizer(self.mainh_sizer)
        self.SetAutoLayout(True)
        self.mainh_sizer.Fit(self)
        self.Show(True)



if __name__ == '__main__':
    post_scan_gui = wx.App()
    panel = PostScanGUI(None)
    post_scan_gui.MainLoop()