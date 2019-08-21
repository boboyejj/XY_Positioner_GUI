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
import keyboard
import time


class TextRedirector(object):
    """
    Class for redirecting the print function output to the ConsoleGUI TextCtrl widget.
    """
    def __init__(self, aWxTextCtrl):
        """
        :param aWxTextCtrl: reference to the TextCtrl widget in the ConsoleGUI.
        """
        self.out = aWxTextCtrl

    def write(self, string):
        """
        Writes the console output to the ConsoleGUI TextCtrl widget.
        :param string: String to be written on the TextCtrl widget.
        :return: Nothing.
        """
        self.out.AppendText(string)


class ConsoleGUI(wx.Frame):
    """
    Custom Terminal Console GUI. Helps users keep track of the NS scan's progress.
    """
    def __init__(self, parent, title):
        """
        :param parent: Parent frame invoking the ConsoleGUI.
        :param title: Title for the GUI window.
        """
        wx.Frame.__init__(self, parent, title=title, size=(800, 700))
        #self.SetWindowStyle(wx.CAPTION | wx.CLOSE_BOX | wx.STAY_ON_TOP)

        # UI Elements
        self.console_text = wx.StaticText(self, label="Console Output")
        self.console_text.SetFont(wx.Font(9, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.console_tctrl = wx.TextCtrl(self, size=(600, 400), style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Menu Bar
        pause_id = 120
        menubar = wx.MenuBar()
        helpmenu = wx.Menu()
        pause_item = wx.MenuItem(helpmenu, pause_id, text="Pause", kind=wx.ITEM_NORMAL)
        helpmenu.Append(pause_item)
        menubar.Append(helpmenu, 'Help')
        self.Bind(wx.EVT_MENU, self.pauseProg, id=pause_id)
        self.SetMenuBar(menubar)

        # Shortcut
        self.accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('p'), pause_id)])
        self.SetAcceleratorTable(self.accel_tbl)

        # Sizers
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)

        # Layout
        self.mainsizer.Add(self.console_text, proportion=0, border=5, flag=wx.ALL)
        self.mainsizer.Add(self.console_tctrl, proportion=1, border=5,
                           flag=wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND)

        self.SetSizer(self.mainsizer)
        self.SetAutoLayout(True)
        self.mainsizer.Fit(self)

    def pauseProg(self,e):
        """
        pause the program
        """
        print("press Enter to continue")

        while True:
            key = keyboard.read_key()

            if key == "enter":
                print("Program is resumed")
                # exit(0)
                break

            time.sleep(0.5)

if __name__ == '__main__':
    consolegui = wx.App()
    fr = ConsoleGUI(None, "Console")
    consolegui.MainLoop()
