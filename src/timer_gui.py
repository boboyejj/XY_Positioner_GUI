"""
    Created by Ganesh Arvapalli on 1/23/18
    ganesh.arvapalli@pctest.com
"""

import tkinter as tk
from tkinter import font as tkFont
import winsound


class TimerGUI(tk.Tk):
    def __init__(self, time):
        tk.Tk.__init__(self)
        self.title('Timer for ' + str(time) + ' seconds')
        self.config(bg='#73AB84')

        # Center on screen
        width, height = 300, 300
        screen_w, screen_h = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (screen_w / 2) - (width / 2)
        y = (screen_h / 2) - (height / 2)
        self.geometry('%dx%d+%d+%d' % (width, height, x, y))

        my_font = tkFont.Font(family='Nirmala UI', size=24)
        self.label = tk.Label(self, text="", width=10, pady=150, font=my_font, bg='#73AB84')
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
