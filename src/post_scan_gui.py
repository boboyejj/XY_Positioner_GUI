"""
    Created by Ganesh Arvapalli on 1/15/18
    ganesh.arvapalli@pctest.com
"""

import tkinter as tk
from tkinter import ttk


class PostScanGUI(tk.Tk):
    """Tkinter GUI that allows user to select post scan options.

    Attributes:
        choiceVar = Option that is selected by the user
        combobox = Tkinter widget allowing for selection of different options
    """

    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.setup()

    def setup(self):
        self.choiceVar = tk.StringVar()
        self.choices = ('Correct Previous Value', 'Zoom Scan', 'Save Data', 'Exit')
        self.choiceVar.set(self.choices[0])

        label = tk.Label(self, text='What would you like to do next?')
        self.combobox = ttk.Combobox(self, textvariable=self.choiceVar, values=self.choices)
        btn = tk.Button(self, text='Select')
        btn.bind('<Button-1>', self.selected)
        btn.config(height=2, width=5)

        label.pack(side=tk.LEFT, pady=60, padx=5)
        self.combobox.pack(side=tk.RIGHT, pady=60, padx=5)
        btn.pack(side=tk.BOTTOM, pady=10)

    def selected(self, event):
        self.choiceVar = self.combobox.get()
        #w = tk.Tk()
        #w.withdraw()
        # self.destroy()
        try:
            self.eval('::ttk::CancelRepeat')
            self.destroy()
            self.quit()
        except:
            print("")

    def get_gui_value(self):
        if self.choiceVar is tk.StringVar:
            print("BLABLABLA")
            return 'Exit'
        else:
            return self.choiceVar


def main():
    post_gui = PostScanGUI(None)
    post_gui.title('Post Scan Options')
    post_gui.mainloop()

    print(post_gui.get_gui_value())


if __name__ == '__main__':
    main()
