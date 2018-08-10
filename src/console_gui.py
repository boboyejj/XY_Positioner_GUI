import wx

class ConsoleGUI(wx.Frame):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800, 700))

        # UI Elements
        self.console_text = wx.StaticText(self, label="Console Output")
        self.console_text.SetFont(wx.Font(9, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.console_tctrl = wx.TextCtrl(self, size=(600, 400))

        # Sizers
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)

        # Layout
        self.mainsizer.Add(self.console_text, proportion=0, border=5, flag=wx.ALL)
        self.mainsizer.Add(self.console_tctrl, proportion=1, border=5, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND)

        self.SetSizer(self.mainsizer)
        self.SetAutoLayout(True)
        self.mainsizer.Fit(self)

if __name__ == '__main__':
    consolegui = wx.App()
    fr = ConsoleGUI(None, "Console")
    consolegui.MainLoop()