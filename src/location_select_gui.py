import wx
import numpy as np

class LocationSelectGUI(wx.Frame):
    def __init__(self, parent, title, grid):
        wx.Frame.__init__(self, parent, title=title)
        self.parent = parent
        self.grid = grid
        self.choice = None

        numrows = self.grid.shape[0]
        numcols = self.grid.shape[1]

        # Sizers
        self.coord_sizer = wx.GridSizer(rows=numrows, cols=numcols, hgap=0, vgap=0)
        for val in np.nditer(self.grid):
            btn = wx.Button(self, val, str(val))
            self.Bind(wx.EVT_BUTTON, lambda e, x=btn.Id: self.selected(x), btn)
            self.coord_sizer.Add(btn, proportion=1)
            self.coord_sizer.Layout()
            print("Button:", val)

        self.SetSizer(self.coord_sizer)
        self.SetAutoLayout(True)
        self.coord_sizer.Fit(self)
        self.Show(True)

    def selected(self, valid):
        self.choice = valid
        print(valid)
        #print(self.choice)

    def get_location(self):
        return self.choice



if __name__ == '__main__':
    rows = 4
    columns = 6
    g = []
    for i in range(rows):
        row = list(range(i * columns + 1, (i + 1) * columns + 1))
        if i % 2 != 0:
            row = list(reversed(row))
        g += row
        #g[i] = row
    print(g)
    g = np.array(g).reshape(rows, columns)
    loc_gui = wx.App()
    fr = LocationSelectGUI(None, title='Location Selection', grid=g)
    loc_gui.MainLoop()
