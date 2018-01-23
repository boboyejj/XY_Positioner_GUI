"""
    Created by Ganesh Arvapalli on 1/16/18
    ganesh.arvapalli@pctest.com
"""

import Tkinter as tk
from tkFont import Font
from motor_driver import MotorDriver
from NARDA_control import NARDAcontroller
from PIL import ImageTk, Image


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

    def __init__(self, parent, x_dist_=2.8, y_dist_=2.8, dwell=2, scan=False, mode='E'):
        tk.Tk.__init__(self, parent)
        self.parent = parent

        # Setting up motor/NARDA related variables
        self.motor = MotorDriver()
        self.scan = scan
        if self.scan:
            self.narda = NARDAcontroller(type=mode, dwell=dwell)
        self.x_dist, self.y_dist, self.dwell = x_dist_, y_dist_, int(dwell)
        self.x_steps = int(self.x_dist / self.motor.step_unit)
        self.y_steps = int(self.y_dist / self.motor.step_unit)
        self.x_frac = self.x_dist / self.motor.step_unit - self.x_steps
        self.y_frac = self.y_dist / self.motor.step_unit - self.y_steps
        self.x_error, self.y_error = 0, 0
        self.x_loc, self.y_loc = 0, 0
        self.setup()

    def update_variables(self):
        if float(self.x_entry.get()) < 0 or float(self.y_entry.get()) < 0 or int(self.dwell_entry.get()) < 0:
            print 'Please enter a valid distance.'
            return
        self.x_dist = float(self.x_entry.get())
        self.y_dist = float(self.y_entry.get())
        self.dwell = int(self.dwell_entry.get())
        self.x_steps = int(self.x_dist / self.motor.step_unit)
        self.y_steps = int(self.y_dist / self.motor.step_unit)
        self.x_frac = self.x_dist / self.motor.step_unit - self.x_steps
        self.y_frac = self.y_dist / self.motor.step_unit - self.y_steps
        print 'Distances changed: X =', self.x_dist, 'Y =', self.y_dist
        print 'New dwell time:', self.dwell
        if self.scan:
            self.narda.set_dwell(self.dwell)

    def setup(self):
        self.title('Please select a location on the grid')
        self.config(background='lightblue')
        my_font = Font(family='Nirmala UI', size=15)

        # Button control grid
        controlFrame = tk.Frame(background='lightblue', padx=10, pady=30)
        btnUp = tk.Button(controlFrame, text='Up', command=self.button_up, padx=15, pady=20, bg='cyan', font=my_font)
        btnDown = tk.Button(controlFrame, text='Down', command=self.button_down, padx=15, pady=20, bg='cyan',
                            font=my_font)
        btnLeft = tk.Button(controlFrame, text='Left', command=self.button_left, padx=20, pady=20, bg='cyan',
                            font=my_font)
        btnRight = tk.Button(controlFrame, text='Right', command=self.button_right, padx=20, pady=20, bg='cyan',
                             font=my_font)

        img = Image.open('images/EHP-200A-500x500.gif').rotate(180)
        img.thumbnail((50, 50), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(img)
        btn_center = tk.Button(controlFrame, image=photo, command=self.measure)
        btn_center.image = photo
        btnUp.grid(row=0, column=1, sticky='NSEW')
        btnDown.grid(row=2, column=1, sticky='NSEW')
        btnLeft.grid(row=1, column=0, sticky='NSEW')
        btnRight.grid(row=1, column=2, sticky='NSEW')
        btn_center.grid(row=1, column=1)

        controlFrame.grid_rowconfigure(3, weight=1)
        controlFrame.grid_columnconfigure(3, weight=1)
        controlFrame.grid(row=0, column=0, padx=10, pady=10)

        # Display the location of the robot relative to the start position
        self.loc = tk.Label(self, text='Current location:\n[%.3f, %.3f]' % (self.x_loc, self.y_loc), font=my_font,
                            padx=20, pady=20, bg='white')
        self.loc.grid(row=1, column=0, sticky='NSEW', padx=150, pady=10)

        # For changing the set distances mid-program
        modifyFrame = tk.Frame(bg='lightblue')
        self.x_entry = tk.Entry(modifyFrame, font=my_font)
        self.y_entry = tk.Entry(modifyFrame, font=my_font)
        self.dwell_entry = tk.Entry(modifyFrame, font=my_font)
        self.x_entry.insert(0, str(self.x_dist))
        self.y_entry.insert(0, str(self.y_dist))
        self.dwell_entry.insert(0, str(self.dwell))
        self.x_entry.grid(row=1, column=0, sticky='NSEW', padx=10, pady=10)
        self.y_entry.grid(row=1, column=1, sticky='NSEW', padx=10, pady=10)
        self.dwell_entry.grid(row=1, column=2, stick='NSEW', padx=10, pady=10)

        x_entry_label = tk.Label(modifyFrame, text='X Distance', font=my_font, bg='cyan', padx=10, pady=10)
        y_entry_label = tk.Label(modifyFrame, text='Y Distance', font=my_font, bg='cyan', padx=10, pady=10)
        dwell_entry_label = tk.Label(modifyFrame, text='Dwell Time (in s)', font=my_font, bg='cyan', padx=10, pady=10)
        x_entry_label.grid(row=0, column=0, sticky='NSEW')
        y_entry_label.grid(row=0, column=1, sticky='NSEW')
        dwell_entry_label.grid(row=0, column=2, sticky='NSEW')

        submitBtn = tk.Button(modifyFrame, text='Change settings', command=self.update_variables, padx=10, pady=10,
                              font=my_font)
        submitBtn.grid(row=2, column=1)
        modifyFrame.grid_rowconfigure(3, weight=1)
        modifyFrame.grid_columnconfigure(3, weight=1)
        modifyFrame.grid(row=2, column=0, padx=10, pady=10)

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Keyboard controls
        self.bind('<Up>', self.key_up)
        self.bind('<Down>', self.key_down)
        self.bind('<Left>', self.key_left)
        self.bind('<Right>', self.key_right)

    def measure(self):
        if self.scan:
            self.narda.reset()
            self.narda.read_data()
            print self.narda.get_wide_band(), self.narda.get_highest_peak()
        else:
            print 'Measurement disabled. Please open NARDA software.'

    def button_up(self):
        self.y_loc -= self.y_dist
        self.y_error -= self.y_frac
        self.motor.reverse_motor_two(self.y_steps + int(self.y_error))
        self.y_error -= int(self.y_error)
        self.loc.config(text='Current location:\n[%.3f, %.3f]' % (self.x_loc, self.y_loc))

    def button_down(self):
        self.y_loc += self.y_dist
        self.y_error += self.y_frac
        self.motor.forward_motor_two(self.y_steps + int(self.y_error))
        self.y_error -= int(self.y_error)
        self.loc.config(text='Current location:\n[%.3f, %.3f]' % (self.x_loc, self.y_loc))

    def button_left(self):
        self.x_loc -= self.x_dist
        self.x_error -= self.x_frac
        self.motor.reverse_motor_one(self.x_steps + int(self.x_error))
        self.x_error -= int(self.x_error)
        self.loc.config(text='Current location:\n[%.3f, %.3f]' % (self.x_loc, self.y_loc))

    def button_right(self):
        self.x_loc += self.x_dist
        self.x_error += self.x_frac
        self.motor.forward_motor_one(self.x_steps + int(self.x_error))
        self.x_error -= int(self.x_error)
        self.loc.config(text='Current location:\n[%.3f, %.3f]' % (self.x_loc, self.y_loc))

    def key_up(self, event):
        self.y_loc -= self.y_dist
        self.y_error -= self.y_frac
        self.motor.reverse_motor_two(self.y_steps + int(self.y_error))
        self.y_error -= int(self.y_error)
        self.loc.config(text='Current location:\n[%.3f, %.3f]' % (self.x_loc, self.y_loc))

    def key_down(self, event):
        self.y_loc += self.y_dist
        self.y_error += self.y_frac
        self.motor.forward_motor_two(self.y_steps + int(self.y_error))
        self.y_error -= int(self.y_error)
        self.loc.config(text='Current location:\n[%.3f, %.3f]' % (self.x_loc, self.y_loc))

    def key_left(self, event):
        self.x_loc -= self.x_dist
        self.x_error -= self.x_frac
        self.motor.reverse_motor_one(self.x_steps + int(self.x_error))
        self.x_error -= int(self.x_error)
        self.loc.config(text='Current location:\n[%.3f, %.3f]' % (self.x_loc, self.y_loc))

    def key_right(self, event):
        self.x_loc += self.x_dist
        self.x_error += self.x_frac
        self.motor.forward_motor_one(self.x_steps + int(self.x_error))
        self.x_error -= int(self.x_error)
        self.loc.config(text='Current location:\n[%.3f, %.3f]' % (self.x_loc, self.y_loc))
