import numpy as np
from src.motor_driver import MotorDriver
from src.post_scan_gui import PostScanGUI
from src.location_select_gui import LocationSelectGUI
from src.narda_navigator import NardaNavigator
from matplotlib import pyplot as plt
from pywinauto import application
from matplotlib import mlab
from src.data_entry_gui import DataEntryGUI
import os
import threading
import time
from scipy import interpolate
from src.timer_gui import TimerGUI
# import turtle

class AreaScanThread(threading.Thread):
    def __init__(self, parent, x_distance, y_distance, grid_step_dist,
                 dwell_time, zdwell_time, save_dir, auto_zoom_scan, meas_type, meas_field, meas_side):
        self.parent = parent
        self.x_distance = x_distance
        self.y_distance = y_distance
        self.grid_step_dist = grid_step_dist
        self.dwell_time = dwell_time
        self.zdwell_time = zdwell_time
        self.save_dir = save_dir
        self.auto_zoom_scan = auto_zoom_scan
        self.meas_type = meas_type
        self.meas_field = meas_field
        self.meas_side = meas_side
        self.callback = parent.enablegui
        super(AreaScanThread, self).__init__()

    def run(self):
        time.sleep(4)
        print(self.meas_type, self.meas_field, self.meas_side)
        run_scan(self.x_distance, self.y_distance, self.grid_step_dist, self.dwell_time, self.zdwell_time,
                 self.save_dir, self.auto_zoom_scan, self.meas_type, self.meas_field, self.meas_side)
        self.callback()
        print("Area Scan Complete.")


def move_to_pos_one(moto, num_steps, x, y):
    """Move motor to first position in grid.

    :param moto: MotorDriver to control motion
    :param num_steps: Number of motor steps between grid points
    :param x: Number of grid columns
    :param y: Number of grid rows
    :return: None
    """
    moto.reverse_motor_one(int(num_steps * x / 2.0))
    moto.reverse_motor_two(int(num_steps * y / 2.0))


def generate_grid(rows, columns):
    """Create grid traversal visual in format of numpy matrix.
    Looks like a normal sequential matrix, but every other row is in reverse order.

    :param rows: Number of rows in grid
    :param columns: Number of columns in grid
    :return: Numpy matrix of correct values
    """
    #g = np.zeros((rows, columns))
    g = []
    for i in range(rows):
        row = list(range(i * columns + 1, (i + 1) * columns + 1))
        if i % 2 != 0:
            row = list(reversed(row))
        g += row
        #g[i] = row
    print(g)
    g = np.array(g).reshape(rows, columns)
    return g


def convert_to_pts(arr, dist, x_off=0, y_off=0):
    """Convert matrix to set of points

    :param arr: matrix to convert
    :param dist: distance between points in matrix
    :param x_off: offset to add in x direction (if not at (0,0))
    :param y_off: offset to add in y direction (if not at (0,0))
    :return: xpts, ypts, zpts: List of points on each axis
    """
    x_dim = arr.shape[1]
    y_dim = arr.shape[0]
    xpts = []
    ypts = []
    zpts = []
    for j in range(x_dim):
        for i in range(y_dim):
            if j < x_dim / 2.0:
                x_pt = -1.0 / 2 * i * dist + x_off
            else:
                x_pt = 1.0 / 2 * i * dist + x_off
            if i < y_dim / 2.0:
                y_pt = -1.0 / 2 * j * dist + y_off
            else:
                y_pt = 1.0 / 2 * j * dist + y_off
            xpts.append(x_pt)
            ypts.append(y_pt)
            zpts.append(arr[i][j])
    print(xpts, ypts, zpts)
    return xpts, ypts, zpts


def run_scan(x_distance, y_distance, grid_step_dist, dwell_time, zdwell_time, savedir, auto_zoom_scan,
             meas_type, meas_field, meas_side):
    # Calculate dimensions of grid and generate it
    x_points = int(np.ceil(np.around(x_distance / grid_step_dist, decimals=3))) + 1
    y_points = int(np.ceil(np.around(y_distance / grid_step_dist, decimals=3))) + 1
    grid = generate_grid(y_points, x_points)
    print("Path: ")
    print(grid)

    # For storing values of highest peak/wide-band
    values = np.zeros(grid.shape)
    print("Current values: ")
    print(values)
    print("------------")

    # Check ports and instantiate relevant objects
    m = MotorDriver()
    #narda = NardaNavigator()

    # Calculate number of motor steps necessary to move one grid space
    num_steps = grid_step_dist / m.step_unit
    # Move to the initial position (top left) of grid scan and measure once
    move_to_pos_one(m, int(num_steps), x_points, y_points)

    # Create an accumulator for the fraction of a step lost each time a grid space is moved
    frac_step = num_steps - int(num_steps)
    num_steps = int(num_steps)
    x_error, y_error = 0, 0  # Accumulator for x and y directions

    count = 1  # Tracks our current progress through the grid
    curr_x, curr_y = 0, 0
    # Take first measurement
    fname = build_filename(meas_type, meas_field, meas_side, count)
    #narda.takeMeasurement(dwell_time, fname)
    values[0][0] = 1
    print(values)

    for i in range(1, grid.size + 1):
        next_x, next_y = np.where(grid == i)
        next_x = next_x[0]
        next_y = next_y[0]
        print("i: %d" % i)
        print(next_x, next_y)
        if next_y > curr_y:  # Move downwards
            curr_y = next_y
        elif next_x > curr_x:  # Move rightwards
            curr_x = next_x
        elif next_x < curr_x:  # Move leftwards
            curr_x = next_x

    pass


def zoom_scan(m, narda):
    pass


def build_filename(type, field, side, number):
    filename = ''
    # Adding type marker
    if type == 'Limb':
        filename += 'L'
    else:
        filename += 'B'
    filename += '_'
    # Adding field marker
    if field == 'Electric':
        filename += 'E'
    else:
        filename += 'H'
    # Adding side marker
    if field == 'Back':
        filename += 'S'
    else:
        filename += side.lower()
    filename += str(int(number))
    return filename

