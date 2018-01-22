"""
    Created by Ganesh Arvapalli on 1/22/18
    ganesh.arvapalli@pctest.com
"""

import Tkinter as tk


class DataEntryGUI(tk.Tk):

    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.value = 0
        self.setup()

    def setup(self):
        label = tk.Label(self, text='Please enter the desired value for this point.', padx=10, pady=10)
        label.grid(row=0, column=0)
        entry = tk.Entry(self)
        entry.grid(row=0,column=1, padx=10, pady=10)
        self.grid_rowconfigure(1)
        self.grid_columnconfigure(2)


def main():
    man = DataEntryGUI(None)
    man.title('Data Entry')
    man.mainloop()


if __name__ == '__main__': main()
