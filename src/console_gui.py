"""
Console GUI

This is the GUI module for displaying a terminal console for the NS Testing program. This GUI is intended to be run
in conjunction with the 'xy_positioner_gui.py' only.

This module contains the following classes:
    - TextRedirecter(object): redirects stdout and stderr to the terminal console.
    - ConsoleGUI(wx.Frame): terminal console that displays all stdout and stderr from the main NS testing program.

Authors:
Chang Hwan 'Oliver' Choi, Biomedical/Software Engineering Intern (Aug. 2018) - changhwan.choi@pctest.com
"""

import wx


class TextRedirecter(object):
    def __init__(self, aWxTextCtrl):
        self.out = aWxTextCtrl

    def write(self, string):
        self.out.AppendText(string)


class ConsoleGUI(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800, 700), style=wx.CAPTION)

        # UI Elements
        self.console_text = wx.StaticText(self, label="Console Output")
        self.console_text.SetFont(wx.Font(9, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.console_tctrl = wx.TextCtrl(self, size=(600, 400), style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Sizers
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)

        # Layout
        self.mainsizer.Add(self.console_text, proportion=0, border=5, flag=wx.ALL)
        self.mainsizer.Add(self.console_tctrl, proportion=1, border=5,
                           flag=wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND)

        self.SetSizer(self.mainsizer)
        self.SetAutoLayout(True)
        self.mainsizer.Fit(self)


if __name__ == '__main__':
    consolegui = wx.App()
    fr = ConsoleGUI(None, "Console")
    consolegui.MainLoop()
