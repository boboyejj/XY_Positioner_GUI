import wx


class PostScanGUI(wx.Frame):

    def __init__(self, parent, title):
        wx.Panel.__init__(self, parent, title=title)
        self.parent = parent

        # UI Elements
        self.option_rbox = wx.RadioBox(self,
                                       label="Options",
                                       choices=['Zoom Scan', 'Correct Previous Value', 'Save Data', 'Exit'],
                                       style=wx.RA_SPECIFY_COLS,
                                       majorDimension=1)
        self.select_btn = wx.Button(self, wx.ID_ANY, "Select")
        self.Bind(wx.EVT_BUTTON, self.get_selection, self.select_btn)

        # Sizers/Layout, Static Lines, & Static Boxes
        self.mainv_sizer = wx.BoxSizer(wx.VERTICAL)

        self.mainv_sizer.Add(self.option_rbox, proportion=1, border=5, flag=wx.EXPAND | wx.ALL)
        self.mainv_sizer.Add(self.select_btn, proportion=0, border=5, flag=wx.EXPAND | wx.RIGHT | wx.TOP | wx.BOTTOM)
        self.SetSizer(self.mainv_sizer)
        self.SetAutoLayout(True)
        self.mainv_sizer.Fit(self)
        self.Show(True)

    def get_selection(self, e):
        return self.option_rbox.GetStringSelection()


if __name__ == '__main__':
    post_scan_gui = wx.App()
    panel = PostScanGUI(None)
    post_scan_gui.MainLoop()