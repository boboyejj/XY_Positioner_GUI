"""
    Created by Ganesh Arvapalli on 1/16/18
    ganesh.arvapalli@pctest.com
"""

import Tkinter as tk
from tkFont import Font
from motor_driver import MotorDriver


class ManualGUI(tk.Tk):
    """Tkinter GUI that allows user to move motors manually set distances.

    Attributes:
        motor = MotorDriver that takes care of all motor movement
        x_dist = specified distance by which motor must travel in x direction
        y_dist = specified distance by which motor must travel in y direction
        x_steps = whole number of steps required to move set distance (x_dist)
        y_steps = whole number of steps required to move set distance (y_dist)
        x_frac = decimal left after rounding to whole number of steps for travelling x_dist
        y_frac = decimal left after rounding to whole number of steps for travelling y_dist
        x_error = accumulated error from leaving out x_frac
        y_error = accumulated error from leaving out y_frac
    """

    def __init__(self, parent, x_dist_=2.8, y_dist_=2.8):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.motor = MotorDriver()
        self.x_dist = x_dist_
        self.y_dist = y_dist_
        self.x_steps = int(self.x_dist / self.motor.step_unit)
        self.y_steps = int(self.y_dist / self.motor.step_unit)
        self.x_frac = self.x_dist / self.motor.step_unit - self.x_steps
        self.y_frac = self.y_dist / self.motor.step_unit - self.y_steps
        self.x_error, self.y_error = 0, 0
        self.x_loc, self.y_loc = 0, 0
        self.setup()

    def setup(self):
        self.title('Please select a location on the grid')
        self.config(background='lightblue')
        my_font = Font(family='Sans Serif', size=15)

        controlFrame = tk.Frame(background='lightblue', padx=10, pady=30)
        btnUp = tk.Button(controlFrame, text='Up', command=self.selectedUp, padx=15, pady=20, bg='blue', font=my_font)
        btnDown = tk.Button(controlFrame, text='Down', command=self.selectedDown, padx=15, pady=20, bg='blue', font=my_font)
        btnLeft = tk.Button(controlFrame, text='Left', command=self.selectedLeft, padx=20, pady=20, bg='blue', font=my_font)
        btnRight = tk.Button(controlFrame, text='Right', command=self.selectedRight, padx=20, pady=20, bg='blue', font=my_font)
        btnUp.grid(row=0, column=1, sticky="nsew")
        btnDown.grid(row=2, column=1, sticky="nsew")
        btnLeft.grid(row=1, column=0, sticky="nsew")
        btnRight.grid(row=1, column=2, sticky="nsew")

        controlFrame.grid_rowconfigure(3, weight=1)
        controlFrame.grid_columnconfigure(3, weight=1)
        controlFrame.grid(row=0, column=0)

        self.loc = tk.Label(self, text='Current location:\n[%.3f, %.3f]' % (self.x_loc, self.y_loc), font=my_font, padx=20, pady=20)
        self.loc.grid(row=1, column=0, sticky='sew')
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def selectedUp(self):
        self.y_loc -= self.y_dist
        self.y_error -= self.y_frac
        self.motor.reverse_motor_two(self.y_steps + int(self.y_error))
        self.y_error -= int(self.y_error)
        self.loc.config(text='Current location:\n[%.3f, %.3f]' % (self.x_loc, self.y_loc))

    def selectedDown(self):
        self.y_loc += self.y_dist
        self.y_error += self.y_frac
        self.motor.forward_motor_two(self.y_steps + int(self.y_error))
        self.y_error -= int(self.y_error)
        self.loc.config(text='Current location:\n[%.3f, %.3f]' % (self.x_loc, self.y_loc))

    def selectedLeft(self):
        self.x_loc -= self.x_dist
        self.x_error -= self.x_frac
        self.motor.reverse_motor_one(self.x_steps + int(self.x_error))
        self.x_error -= int(self.x_error)
        self.loc.config(text='Current location:\n[%.3f, %.3f]' % (self.x_loc, self.y_loc))

    def selectedRight(self):
        self.x_loc += self.y_dist
        self.x_error += self.x_frac
        self.motor.forward_motor_one(self.x_steps + int(self.x_error))
        self.x_error -= int(self.x_error)
        self.loc.config(text='Current location:\n[%.3f, %.3f]' % (self.x_loc, self.y_loc))