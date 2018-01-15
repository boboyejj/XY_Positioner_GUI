import Tkinter as tk
import ttk
import numpy as np

class LocationSelectGUI(tk.Tk):
    def __init__(self, parent, grid):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.grid = grid
        self.setup()

    def setup(self):
        self.title('Please select a location on the grid')
        self.choiceVar = tk.IntVar()
        self.choiceVar = 0
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                btn = tk.Button(self, text=str(int(self.grid[i][j])),
                                command=lambda row=i, col=j: self.selected(row, col))
                btn.grid(row=i, column=j, sticky="nsew")

        self.grid_rowconfigure(len(self.grid), weight=1)
        self.grid_columnconfigure(len(self.grid[0]), weight=1)
        self.configure(background='grey')

    def selected(self, row, col):
        self.choiceVar = self.grid[row][col]
        self.quit()

    def get_gui_value(self):
        return self.choiceVar