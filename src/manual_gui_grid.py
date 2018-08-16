"""
    Created by Ganesh Arvapalli on 1/22/18
    ganesh.arvapalli@pctest.com
"""

import tkinter as tk
from tkinter import font
from src.motor_driver import MotorDriver
from numpy import linspace, meshgrid
from matplotlib.mlab import griddata
import matplotlib.pyplot as plt
import os


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

        # Center on screen
        width, height = 1050, 550
        screen_w, screen_h = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (screen_w / 2) - (width / 2)
        y = (screen_h / 2) - (height / 2)
        self.geometry('%dx%d+%d+%d' % (width, height, x, y))

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
            print("Please enter a valid distance.")
            return
        self.x_dist = float(self.x_entry.get())
        self.y_dist = float(self.y_entry.get())
        self.x_steps = int(self.x_dist / self.motor.step_unit)
        self.y_steps = int(self.y_dist / self.motor.step_unit)
        self.x_frac = self.x_dist / self.motor.step_unit - self.x_steps
        self.y_frac = self.y_dist / self.motor.step_unit - self.y_steps
        print("Distances changed: X =", self.x_dist, "Y =", self.y_dist)

    def setup(self):
        self.title('Please select a location on the grid')
        self.config(background='#1C3E52')
        my_font = font.Font(family='Nirmala UI', size=12)

        # Button control grid
        control_frame = tk.Frame(background='#1C3E52', padx=5, pady=5)
        btn_up = tk.Button(control_frame, text='Away \nmotor2 (Up)', command=self.button_up, padx=10, pady=15,
                           bg='#A3A3A3', font=my_font)
        btn_down = tk.Button(control_frame, text='Toward \nmotor2 (Down)', command=self.button_down, padx=10, pady=15,
                             bg='#A3A3A3', font=my_font)
        btn_left = tk.Button(control_frame, text='Away \nmotor1 (Left)', command=self.button_left, padx=15, pady=15,
                             bg='#A3A3A3', font=my_font)
        btn_right = tk.Button(control_frame, text='Toward \nmotor1 (Right)', command=self.button_right, padx=15,
                              pady=15, bg='#A3A3A3', font=my_font)

        entry_center = tk.Label(control_frame, text=':)')
        btn_up.grid(row=0, column=1, sticky='NSEW')
        btn_down.grid(row=2, column=1, sticky='NSEW')
        btn_left.grid(row=1, column=0, sticky='NSEW')
        btn_right.grid(row=1, column=2, sticky='NSEW')
        entry_center.grid(row=1, column=1)

        control_frame.grid_rowconfigure(3, weight=1)
        control_frame.grid_columnconfigure(3, weight=1)
        control_frame.grid(row=0, column=0, padx=30, pady=20)

        # Display the location of the robot relative to the start position
        self.loc = tk.Label(self, text='Current location:\n[%.3f, %.3f]' % (self.x_loc, self.y_loc), font=my_font,
                            bg='#CFCFCF')
        self.loc.grid(row=2, column=0, sticky='NSEW', padx=50, pady=50)

        # For changing the set distances mid-program
        modify_frame = tk.Frame(bg='#1C3E52')
        self.x_entry = tk.Entry(modify_frame, font=my_font)
        self.y_entry = tk.Entry(modify_frame, font=my_font)
        self.x_entry.insert(0, str(self.x_dist))
        self.y_entry.insert(0, str(self.y_dist))
        self.x_entry.grid(row=1, column=0, sticky='NSEW', padx=5, pady=15)
        self.y_entry.grid(row=3, column=0, sticky='NSEW', padx=5, pady=15)

        x_entry_label = tk.Label(modify_frame, text='X Distance', font=my_font, bg='#A3A3A3', padx=5, pady=5)
        y_entry_label = tk.Label(modify_frame, text='Y Distance', font=my_font, bg='#A3A3A3', padx=5, pady=5)
        x_entry_label.grid(row=0, column=0, sticky='NSEW')
        y_entry_label.grid(row=2, column=0, sticky='NSEW')

        submit_btn = tk.Button(modify_frame, text='Change settings', command=self.update_variables, padx=5, pady=5,
                               font=my_font)
        submit_btn.grid(row=4, column=0)
        modify_frame.grid_rowconfigure(5, weight=1)
        modify_frame.grid_columnconfigure(2, weight=1)
        modify_frame.grid(row=0, column=1)

        data_frame = tk.Frame(bg='#1C3E52')
        btn_frame = tk.Frame(bg='#1C3E52')
        value_label = tk.Label(data_frame, text='Enter value here: ', font=my_font, bg='#CFCFCF')
        self.value_entry = tk.Entry(data_frame, font=my_font)
        measure_here = tk.Button(data_frame, text='Add to graph', padx=10, font=my_font, command=self.add_to_data)

        value_label.grid(row=0, column=0, padx=10)
        self.value_entry.grid(row=0, column=1, padx=10)
        measure_here.grid(row=0, column=2, padx=10)
        data_frame.grid_rowconfigure(1, weight=1)
        data_frame.grid_columnconfigure(3, weight=1)
        data_frame.grid(row=2, column=1, padx=30, pady=10)

        grid_btn = tk.Button(btn_frame, text='Generate graph', padx=10, pady=5, font=my_font, command=self.plot)
        save_btn = tk.Button(btn_frame, text='Save data', padx=10, pady=5, font=my_font, command=self.save_data)

        grid_btn.grid(row=1, column=0, padx=10, pady=5)
        save_btn.grid(row=1, column=1, padx=10, pady=5)
        btn_frame.grid_rowconfigure(1, weight=1)
        btn_frame.grid_columnconfigure(2, weight=1)
        btn_frame.grid(row=3, column=1, padx=10, pady=5)

        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # Keyboard controls
        self.bind('<Up>', self.key_up)
        self.bind('<Down>', self.key_down)
        self.bind('<Left>', self.key_left)
        self.bind('<Right>', self.key_right)
        # self.bind('<Control-S>', self.save_data)

    def add_to_data(self):
        if self.value_entry.get() is None or self.value_entry.get() == '':
            print("Please enter a valid value.")
            return
        # if self.x_loc not in self.x_pts or self.y_loc not in self.y_pts:
        # if self.y_pts[self.x_pts.index(self.x_loc)] == self.y_loc:        Better but what if x_pts not found?
        # Currently does not support remeasuring points
        if (self.x_loc, self.y_loc) in self.checked_pts:
            print("Already measured.")
            return
        self.checked_pts.append((self.x_loc, self.y_loc))
        self.x_pts.append(self.x_loc)
        self.y_pts.append(-1 * self.y_loc)
        self.z_pts.append(float(self.value_entry.get()))
        print("[", self.x_loc, ",", self.y_loc, "]: ", float(self.value_entry.get()))
        # print self.x_pts
        # print self.y_pts
        # print self.z_pts
        # else:
        #     print 'Point already has value. Updating to new value'
        #     self.z_pts.insert(self.x_pts.index(self.x_loc), float(self.value_entry.get()))

    def grid(self, resX=100, resY=100):
        xi = linspace(min(self.x_pts), max(self.x_pts), resX)
        yi = linspace(min(self.y_pts), max(self.y_pts), resY)
        Z = griddata(self.x_pts, [k for k in self.y_pts], self.z_pts, xi, yi, interp='linear')
        # Z = griddata(self.x_pts, [k for k in self.y_pts], self.z_pts, xi, yi, interp='linear')
        X, Y = meshgrid(xi, yi, indexing='xy')
        return X, Y, Z

    def plot(self):
        # if True:
        #     print 'Currently a work in progress.'
        #     return
        if len(self.x_pts) < 4:
            print("Not enough values. Collect more data.")
            return
        X, Y, Z = self.grid()
        fig, axes = plt.subplots(1, 1)
        axes.set_aspect('equal')
        # axes.hold(True)
        graph = axes.contourf(X, Y, Z)
        axes.scatter(self.x_pts, [k for k in self.y_pts], c=self.z_pts, s=60, cmap=graph.cmap)
        # axes.scatter(self.x_pts, [k for k in self.y_pts], c=self.z_pts, s=60, cmap=graph.cmap)
        cbar = fig.colorbar(graph)
        cbar.set_label('Signal Level')
        axes.margins(0.05)
        plt.show(block=False)

    def save_data(self):
        if not os.path.exists('results'):
            os.makedirs('results')
        my_path = os.path.join(os.getcwd(), 'results')
        if plt.get_fignums():
            plt.savefig(os.path.join(my_path, 'manual_contour_plot.png'), bbox_inches='tight')
        else:
            print("No graph to save.")
        file = open(os.path.join(my_path, 'manual_data.txt'), 'w+')
        file.write('X: ' + str(self.x_pts) + '\n')
        file.write('Y: ' + str(self.y_pts) + '\n')
        file.write('Z: ' + str(self.z_pts) + '\n')
        file.close()

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
    man.motor.destroy()



if __name__ == '__main__': main()
