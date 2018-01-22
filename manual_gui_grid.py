"""
    Created by Ganesh Arvapalli on 1/22/18
    ganesh.arvapalli@pctest.com
"""

import Tkinter as tk
from tkFont import Font
from motor_driver import MotorDriver
from numpy import linspace, meshgrid
from matplotlib.mlab import griddata
import matplotlib.pyplot as plt


class ManualGridGUI(tk.Tk):
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

    def __init__(self, parent, x_dist=2.8, y_dist=2.8):
        tk.Tk.__init__(self, parent)
        self.parent = parent

        # Setting up motor-related variables
        self.motor = MotorDriver()
        self.x_dist, self.y_dist = x_dist, y_dist
        self.x_steps = int(self.x_dist / self.motor.step_unit)
        self.y_steps = int(self.y_dist / self.motor.step_unit)
        self.x_frac = self.x_dist / self.motor.step_unit - self.x_steps
        self.y_frac = self.y_dist / self.motor.step_unit - self.y_steps
        self.x_error, self.y_error = 0, 0
        self.x_loc, self.y_loc = 0, 0

        # Setting up plot related variables
        self.x_pts = []
        self.y_pts = []
        self.z_pts = []
        self.checked_pts = []
        self.setup()

    def update_variables(self):
        if float(self.x_entry.get()) < 0 or float(self.y_entry.get()) < 0:
            print 'Please enter a valid distance.'
            return
        self.x_dist = float(self.x_entry.get())
        self.y_dist = float(self.y_entry.get())
        self.x_steps = int(self.x_dist / self.motor.step_unit)
        self.y_steps = int(self.y_dist / self.motor.step_unit)
        self.x_frac = self.x_dist / self.motor.step_unit - self.x_steps
        self.y_frac = self.y_dist / self.motor.step_unit - self.y_steps
        print 'Distances changed: X =', self.x_dist, 'Y =', self.y_dist


    def setup(self):
        self.title('Please select a location on the grid')
        self.config(background='lightblue')
        my_font = Font(family='Nirmala UI', size=15)

        # Button control grid
        controlFrame = tk.Frame(background='lightblue', padx=10, pady=30)
        btnUp = tk.Button(controlFrame, text='Up', command=self.button_up, padx=10, pady=15, bg='cyan', font=my_font)
        btnDown = tk.Button(controlFrame, text='Down', command=self.button_down, padx=10, pady=15, bg='cyan',
                            font=my_font)
        btnLeft = tk.Button(controlFrame, text='Left', command=self.button_left, padx=15, pady=15, bg='cyan',
                            font=my_font)
        btnRight = tk.Button(controlFrame, text='Right', command=self.button_right, padx=15, pady=15, bg='cyan',
                             font=my_font)

        entry_center = tk.Label(controlFrame, text=':)')
        btnUp.grid(row=0, column=1, sticky='NSEW')
        btnDown.grid(row=2, column=1, sticky='NSEW')
        btnLeft.grid(row=1, column=0, sticky='NSEW')
        btnRight.grid(row=1, column=2, sticky='NSEW')
        entry_center.grid(row=1, column=1)

        controlFrame.grid_rowconfigure(3, weight=1)
        controlFrame.grid_columnconfigure(3, weight=1)
        controlFrame.grid(row=0, column=0, padx=10, pady=10)

        # Display the location of the robot relative to the start position
        self.loc = tk.Label(self, text='Current location:\n[%.3f, %.3f]' % (self.x_loc, self.y_loc), font=my_font,
                         bg='white')
        self.loc.grid(row=2, column=0, sticky='NSEW', padx=150, pady=10)

        # For changing the set distances mid-program
        modifyFrame = tk.Frame(bg='lightblue')
        self.x_entry = tk.Entry(modifyFrame, font=my_font)
        self.y_entry = tk.Entry(modifyFrame, font=my_font)
        self.x_entry.insert(0, str(self.x_dist))
        self.y_entry.insert(0, str(self.y_dist))
        self.x_entry.grid(row=1, column=0, sticky='NSEW', padx=5, pady=5)
        self.y_entry.grid(row=1, column=2, sticky='NSEW', padx=5, pady=5)

        x_entry_label = tk.Label(modifyFrame, text='X Distance', font=my_font, bg='cyan', padx=5, pady=5)
        y_entry_label = tk.Label(modifyFrame, text='Y Distance', font=my_font, bg='cyan', padx=5, pady=5)
        x_entry_label.grid(row=0, column=0, sticky='NSEW')
        y_entry_label.grid(row=0, column=2, sticky='NSEW')

        submitBtn = tk.Button(modifyFrame, text='Change settings', command=self.update_variables, padx=5, pady=5,
                              font=my_font)
        submitBtn.grid(row=2, column=1)
        modifyFrame.grid_rowconfigure(3, weight=1)
        modifyFrame.grid_columnconfigure(3, weight=1)
        modifyFrame.grid(row=0, column=1, padx=10, pady=10)

        data_frame = tk.Frame(bg='lightblue')
        value_label = tk.Label(data_frame, text='Enter value here: ', font=my_font, bg='white')
        self.value_entry = tk.Entry(data_frame, font=my_font)
        measure_here = tk.Button(data_frame, text='Add to graph', padx=10, pady=10, font=my_font, command=self.add_to_data)
        gridBtn = tk.Button(data_frame, text='Generate graph', padx=10, pady=10, font=my_font, command=self.plot)

        value_label.grid(row=0, column=0, padx=10, pady=10)
        self.value_entry.grid(row=0, column=1, padx=10, pady=10)
        measure_here.grid(row=0, column=2, padx=10, pady=10)
        gridBtn.grid(row=0, column=3, padx=10, pady=10)
        data_frame.grid_rowconfigure(1, weight=1)
        data_frame.grid_columnconfigure(4, weight=1)
        data_frame.grid(row=2, column=1)

        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # Keyboard controls
        self.bind('<Up>', self.key_up)
        self.bind('<Down>', self.key_down)
        self.bind('<Left>', self.key_left)
        self.bind('<Right>', self.key_right)

    def add_to_data(self):
        if self.value_entry.get() is None or self.value_entry.get() == '':
            print 'Please enter a valid value.'
            return
        # if self.x_loc not in self.x_pts or self.y_loc not in self.y_pts:
        # if self.y_pts[self.x_pts.index(self.x_loc)] == self.y_loc:        Better but what if x_pts not found?
        if (self.x_loc, self.y_loc) in self.checked_pts:
            print 'Already measured.'
            return
        self.checked_pts.append((self.x_loc, self.y_loc))
        self.x_pts.append(self.x_loc)
        self.y_pts.append(self.y_loc)
        self.z_pts.append(float(self.value_entry.get()))
        print '[', self.x_loc, ',', self.y_loc, ']: ', float(self.value_entry.get())
        print self.x_pts
        print self.y_pts
        print self.z_pts
        # else:
        #     print 'Point already has value. Updating to new value'
        #     self.z_pts.insert(self.x_pts.index(self.x_loc), float(self.value_entry.get()))

    def grid(self, resX=100, resY=100):
        xi = linspace(min(self.x_pts), max(self.x_pts), resX)
        yi = linspace(min(self.y_pts), max(self.y_pts), resY)
        Z = griddata(self.x_pts, [-1 * k for k in self.y_pts], self.z_pts, xi, yi, interp='linear')
        X, Y = meshgrid(xi, yi)
        return X, Y, Z

    def plot(self):
        if len(self.x_pts) < 4:
            print 'Not enough values. Collect more data.'
            return
        X, Y, Z = self.grid()
        fig, axes = plt.subplots(1, 1)
        axes.set_aspect('equal')
        # axes.hold(True)
        graph = axes.contourf(X, Y, Z)
        axes.scatter(self.x_pts, [-1 * k for k in self.y_pts], c=self.z_pts, s=60, cmap=graph.cmap)
        cbar = fig.colorbar(graph)
        cbar.set_label('Signal Level')
        axes.margins(0.05)
        plt.show(block=False)

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


def main():
    man = ManualGridGUI(None, float(2.8), float(2.8))
    man.title('Manual Control')
    man.mainloop()


if __name__ == '__main__': main()