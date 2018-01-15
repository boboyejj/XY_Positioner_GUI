import Tkinter as tk
import ttk

class PostScanGUI(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent

        self.choiceVar = tk.StringVar()
        self.choices = ('Correct Previous Value', 'Zoom Scan', 'Exit')
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
        w = tk.Tk()
        w.withdraw()
        self.quit()

    def get_gui_value(self):
        return self.choiceVar
