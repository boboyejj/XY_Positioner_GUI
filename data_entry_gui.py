"""
    Created by Ganesh Arvapalli on 1/22/18
    ganesh.arvapalli@pctest.com
"""

import Tkinter as tk
import sys


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
        entry.focus()
        entry.grid(row=0,column=1, padx=10, pady=10)
        self.grid_rowconfigure(1)
        self.grid_columnconfigure(2)

        self.bind('<Return>', self.exit_gui)

    def callback(self, sv):
        try:
            self.value = float(sv.get())
        except ValueError:
            print 'Please type a valid number.'

    def getval(self):
        return self.value

    def exit_gui(self, event):
        self.destroy()


def main():
    man = DataEntryGUI(None)
    man.title('Data Entry')
    man.mainloop()
    print man.getval()

    man = DataEntryGUI(None)
    man.title('Data Entry')
    man.mainloop()
    print man.getval()

    man = DataEntryGUI(None)
    man.title('Data Entry')
    man.mainloop()
    print man.getval()

if __name__ == '__main__':
    main()
