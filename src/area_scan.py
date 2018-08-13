import numpy as np
import serial
from src.motor_driver import MotorDriver
from src.post_scan_gui import PostScanGUI
from src.location_select_gui import LocationSelectGUI
from src.narda_navigator import NardaNavigator
from matplotlib import pyplot as plt
from pywinauto import application
import os
import threading
import time
import wx
from scipy import interpolate


class AreaScanThread(threading.Thread):
    def __init__(self, parent, x_distance, y_distance, grid_step_dist,
                 dwell_time, save_dir, meas_type, meas_field, meas_side):
        self.parent = parent
        self.x_distance = x_distance
        self.y_distance = y_distance
        self.grid_step_dist = grid_step_dist
        self.dwell_time = dwell_time
        self.save_dir = save_dir
        self.meas_type = meas_type
        self.meas_field = meas_field
        self.meas_side = meas_side

        self.values = None  # Placeholder for the array of values
        self.grid = None  # Placeholder for the coordinate grid array
        self.curr_row = None  # Current position row
        self.curr_col = None  # Current position col
        super(AreaScanThread, self).__init__()

    def run(self):
        print(self.meas_type, self.meas_field, self.meas_side)

        # Preparation
        x_points = int(np.ceil(np.around(self.x_distance / self.grid_step_dist, decimals=3))) + 1
        y_points = int(np.ceil(np.around(self.y_distance / self.grid_step_dist, decimals=3))) + 1
        # Check ports and instantiate relevant objects
        try:
            m = MotorDriver()
        except serial.SerialException:
            print("Error: Connection to C4 controller was not found")
            wx.CallAfter(self.parent.enablegui)
            return
        # narda = NardaNavigator()
        narda = None  # TODO: Debugging
        # Calculate number of motor steps necessary to move one grid space
        num_steps = self.grid_step_dist / m.step_unit

        # Run scan
        self.values, self.grid, self.curr_row, self.curr_col = run_scan(x_points, y_points, m, narda, num_steps,
                                                                        self.dwell_time, self.save_dir, self.meas_type,
                                                                        self.meas_field, self.meas_side)
        print("General Area Scan Complete.")
        wx.CallAfter(self.parent.run_post_scan)
        m.destroy()


class ZoomScanThread(threading.Thread):
    def __init__(self, parent, num_steps, dwell_time,
                 save_dir, meas_type, meas_field, meas_side, curr_row, curr_col):
        self.parent = parent
        self.num_steps = num_steps
        self.dwell_time = dwell_time
        self.save_dir = save_dir
        self.meas_type = meas_type
        self.meas_field = meas_field
        self.meas_side = meas_side
        self.curr_row = curr_row
        self.curr_col = curr_col

        self.values = None  # Placeholder for the array of values
        self.grid = None  # Placeholder for the coordinate grid array
        super(AreaScanThread, self).__init__()

    def run(self):
        print(self.meas_type, self.meas_field, self.meas_side)

        # Preparation
        x_points = 5
        y_points = 5
        # Check ports and instantiate relevant objects
        try:
            m = MotorDriver()
        except serial.SerialException:
            print("Error: Connection to C4 controller was not found")
            return -1
        # narda = NardaNavigator()
        narda = None  # TODO: Debugging
        # Calculate number of motor steps necessary to move one grid space
        znum_steps = self.num_steps / 4.0  # Zoom scan steps are scaled down

        # Move to coordinate with maximum value
        max_val = self.values.max()
        print("Max_val: %d" % max_val)
        max_row, max_col = np.where(self.values == int(max_val))
        row_steps = max_row - self.curr_row
        col_steps = max_col - self.curr_col
        print("R steps: %d   -   C steps %d" % (row_steps, col_steps))
        if row_steps > 0:
            m.forward_motor_two(int(self.num_steps * row_steps))
        else:
            m.reverse_motor_two(int(-1 * self.num_steps * row_steps))
        if col_steps > 0:
            m.forward_motor_one(int(self.num_steps * col_steps))
        else:
            m.reverse_motor_one(int(-1 * self.num_steps * col_steps))

        # Run scan
        self.values, self.grid, self.curr_row, self.curr_col = run_scan(x_points, y_points, m, narda, znum_steps,
                                                                        self.dwell_time, self.save_dir, self.meas_type,
                                                                        self.meas_field, self.meas_side)
        if self.values == -1:
            print("Area Scan Terminated.")
        else:
            print("General Area Scan Complete.")
            wx.CallAfter(self.parent.run_post_scan)
        m.destroy()


def run_scan(x_points, y_points, m, narda, num_steps, dwell_time, savedir, meas_type, meas_field, meas_side):
    # Set measurement params in the NARDA software

    # Move to the initial position (top left) of grid scan and measure once
    move_to_pos_one(m, int(num_steps), x_points, y_points)

    values, grid, curr_row, curr_col = area_scan(x_points, y_points, m, narda, num_steps,
                                                 dwell_time, meas_type, meas_field, meas_side)
    zoom_values = None

    return values, grid, curr_row, curr_col

    while True:
        # Plotting Results
        plt.clf()
        plt.imshow(values, interpolation='bilinear')
        plt.title('Area Scan Heat Map')
        cbar = plt.colorbar()
        cbar.set_label('Signal Level')
        plt.show(block=False)
        #if zoom_values != None:
        #    plt.figure()
        #    plt.imshow(zoom_values, interpolation='bilinear')
        #    plt.title('Area Scan Heat Map')
        #    cbar = plt.colorbar()
        #    cbar.set_label('Signal Level')
        #    plt.show(block=False)

        # Post Scan GUI - User selects which option to proceed with
        try:
            app = wx.App()
            frame = wx.Frame(None)
            frame.Center()
            frame.Show()
            with PostScanGUI(None, title="Post Scan Options") as post_gui:
                post_gui.ShowModal()
                choice = post_gui.get_selection()
            app.MainLoop()
        except:
            print("FAILED")
        print("HUE")
        #choice = post_gui.get_selection()
        print("Option selected: ", choice)

        #post_gui = PostScanGUI(None)
        #post_gui.title('Post Scan Options')
        #post_gui.mainloop()
        #choice = post_gui.get_gui_value()
        #print(choice)

        if choice == 'Exit':
            print("Exiting program...")
            m.destroy()
            exit(0)
        elif choice == 'Save Data':
            print("Saving data...")
        elif choice == 'Zoom Scan':
            # Move to coordinate with maximum value
            max_val = values.max()
            print("Max_val: %d" % max_val)
            max_row, max_col = np.where(values == int(max_val))
            row_steps = max_row - curr_row
            col_steps = max_col - curr_col
            print("R steps: %d   -   C steps %d" % (row_steps, col_steps))
            if row_steps > 0:
                m.forward_motor_two(int(num_steps * row_steps))
            else:
                m.reverse_motor_two(int(-1 * num_steps * row_steps))
            if col_steps > 0:
                m.forward_motor_one(int(num_steps * col_steps))
            else:
                m.reverse_motor_one(int(-1 * num_steps * col_steps))
            # Prepare zoom scan
            zx_points = 5
            zy_points = 5
            # Calculate number of motor steps necessary to move one grid space
            znum_steps = grid_step_dist / (4.0 * m.step_unit)
            # Move to the initial position (top left) of grid scan and measure once
            move_to_pos_one(m, znum_steps, zx_points, zy_points)
            # Perform zoom scan
            zoom_values = area_scan(zx_points, zy_points, m, narda, znum_steps,
                                     zdwell_time, meas_type, meas_field, meas_side)[0]
            # Move back to original position
            m.reverse_motor_one(int(2 * znum_steps))
            m.reverse_motor_two(int(2 * znum_steps))
        elif choice == 'Correct Previous Value':
            plt.close()
            print("Select location to correct.")
            loc_gui = LocationSelectGUI(None, "Location Selection", grid)
            location = loc_gui.get_location()
            print("Location Selected: ", location)
            loc_gui.Close()
            target_row, target_col = np.where(grid == int(location))
            row_steps = target_row - curr_row
            col_steps = target_col - curr_col
            print("R steps: %d   -   C steps %d" % (row_steps, col_steps))
            if row_steps > 0:
                m.forward_motor_two(int(num_steps * row_steps))
            else:
                m.reverse_motor_two(int(-1 * num_steps * row_steps))
            if col_steps > 0:
                m.forward_motor_one(int(num_steps * col_steps))
            else:
                m.reverse_motor_one(int(-1 * num_steps * col_steps))
            curr_row = target_row
            curr_col = target_col
            #fname = build_filename(meas_type, meas_field, meas_side, count)
            #narda.takeMeasurement(dwell_time, fname)
            #values[grid_loc[0]][grid_loc[1]] = 5
    return 0  # Successful area scan


def area_scan(x_points, y_points, m, narda, num_steps, dwell_time, meas_type, meas_field, meas_side):
    grid = generate_grid(x_points, y_points)
    values = np.zeros(grid.shape)

    print("Scan path:")
    print(grid)
    print("Current Values:")
    print(values)

    # Create an accumulator for the fraction of a step lost each time a grid space is moved
    frac_step = num_steps - int(num_steps)
    num_steps = int(num_steps)
    x_error, y_error = 0, 0  # Accumulator for x and y directions
    curr_row, curr_col = 0, 0
    max_row, max_col = -1, -1  # Placeholders for the max value's coordinates
    # Take first measurement
    fname = build_filename(meas_type, meas_field, meas_side, 1)
    # narda.takeMeasurement(dwell_time, fname)
    values[0][0] = 4

    # General Area Scan
    for i in range(2, grid.size + 1):
        next_row, next_col = np.where(grid == i)
        next_row = next_row[0]
        next_col = next_col[0]
        if next_row > curr_row:  # Move downwards
            y_error += frac_step
            m.forward_motor_two(num_steps + int(y_error))
            y_error -= int(y_error)
            curr_row = next_row
            values[curr_row][curr_col] = 3
        elif next_col > curr_col:  # Move rightwards
            x_error += frac_step
            m.forward_motor_one(num_steps + int(x_error))  # Adjust distance by error
            x_error -= int(x_error)  # Subtract integer number of steps that were moved
            curr_col = next_col
            values[curr_row][curr_col] = 1
        elif next_col < curr_col:  # Move leftwards
            x_error -= frac_step
            m.reverse_motor_one(num_steps + int(x_error))
            x_error -= int(x_error)
            curr_col = next_col
            values[curr_row][curr_col] = 2
        fname = build_filename(meas_type, meas_field, meas_side, i)
        # narda.takeMeasurement(dwell_time, fname)
        print("---------")
        print(values)

    return values, grid, curr_row, curr_col


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

