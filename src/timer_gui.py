"""
    Created by Ganesh Arvapalli on 1/23/18
    ganesh.arvapalli@pctest.com
"""

import Tkinter as tk
import winsound


class TimerGUI(tk.Tk):
    def __init__(self, time):
        tk.Tk.__init__(self)
        self.label = tk.Label(self, text="", width=10)
        self.label.pack()
        self.remaining = 0
        self.countdown(time)

    def countdown(self, remaining = None):
        if remaining is not None:
            self.remaining = remaining

        if self.remaining <= 0:
            self.label.configure(text="time's up!")
            winsound.PlaySound('C:\Windows\Media\Ring01.wav', winsound.SND_FILENAME)
        else:
            self.label.configure(text="%d" % self.remaining)
            self.remaining = self.remaining - 1
            self.after(1000, self.countdown)


if __name__ == "__main__":
    app = TimerGUI(5)
    app.mainloop()
