"""
Location Selection GUI

This is the GUI module for selecting a coordinate post area scan for correcting a previous measurement.
This GUI is intended to be run in conjunction with the 'xy_positioner_gui.py' only. The GUI is currently only used
for the post-scan function 'Correct Previous Value'.

This module contains a single class:
    - LocationSelectionGUI(wx.Dialog): provides a grid of buttons to allow user to select area scan coordinate.

Authors:
Chang Hwan 'Oliver' Choi, Biomedical/Software Engineering Intern (Aug. 2018) - changhwan.choi@pctest.com
"""

import numpy as np
import wx


class LocationSelectGUI(wx.Dialog):
    """
    Location Selection GUI. Allows the user to select a position in the area scan grid for the 'Correct Previous
    Value' function.
    """
    def __init__(self, parent, title, grid):
        """
        :param parent: Parent frame invoking the LocationSelectGUI.
        :param title: Title for the GUI window.
        :param grid: Numpy array of the traversal grid for the general area scan.
        """
        wx.Dialog.__init__(self, parent, title=title)
        self.parent = parent
        self.grid = grid

        numrows = self.grid.shape[0]
        numcols = self.grid.shape[1]

        # Bindings
        self.Bind(wx.EVT_CLOSE, self.OnQuit)

        # Sizers
        self.coord_sizer = wx.GridSizer(rows=numrows, cols=numcols, hgap=0, vgap=0)
        for val in np.nditer(self.grid):
            btn = wx.Button(self, val, str(val), size=(50, 50))
            self.Bind(wx.EVT_BUTTON, lambda e, x=btn.Id: self.selected(x), btn)
            self.coord_sizer.Add(btn, proportion=1)
            self.coord_sizer.Layout()

        self.SetSizer(self.coord_sizer)
        self.SetAutoLayout(True)
        self.coord_sizer.Fit(self)
        self.Show(True)

    def selected(self, value):
        """
        Runs the parent Frame's 'run_currection()' function using the clicked button's number as the argument.
        Destroys the GUI on button click.

        :param value: Button value/position selected on the grid.
        :return: Nothing.
        """
        self.parent.run_correction(value)
        self.Destroy()

    def OnQuit(self, e):
        """
        Exit script - when the GUI closes, wx calls the MainFrame's 'run_post_scan()' function.
        Destroys the GUI button.

        :param e:
        :return:
        """
        wx.CallAfter(self.parent.run_post_scan)
        self.Destroy()


if __name__ == '__main__':
    # Generate Zig-zag grid
    rows = 4
    columns = 6
    g = []
    for i in range(rows):
        row = list(range(i * columns + 1, (i + 1) * columns + 1))
        if i % 2 != 0:
            row = list(reversed(row))
        g += row
    print(g)
    g = np.array(g).reshape(rows, columns)
    # Start GUI
    loc_gui = wx.App()
    fr = LocationSelectGUI(None, title='Location Selection', grid=g)
    loc_gui.MainLoop()
