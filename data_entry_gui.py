"""
    Created by Ganesh Arvapalli on 1/22/18
    ganesh.arvapalli@pctest.com
"""

import Tkinter as tk


class DataEntryGUI(tk.Tk):

    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.value = 0.0
        self.setup()

    def setup(self):
        label = tk.Label(self, text='Please enter the desired value: ')
        label.grid(row=0, column=0, padx=10, pady=10)
        sv = tk.StringVar()
        sv.trace("w", lambda name, index, mode, sv=sv: self.callback(sv))
        entry = tk.Entry(self, textvariable=sv)
        entry.grid(row=0,column=1, padx=10, pady=10)
        self.grid_rowconfigure(1)
        self.grid_columnconfigure(2)

    def callback(self, sv):
        self.value = float(sv.get())

    def getval(self):
        return self.value


def main():
    man = DataEntryGUI(None)
    man.title('Data Entry')
    man.mainloop()
    print man.getval()


if __name__ == '__main__':
    main()
