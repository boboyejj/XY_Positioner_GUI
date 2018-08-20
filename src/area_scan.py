"""
Area Scan Scripts

This module contains the threads and functions to perform general area scans and zoom scans.
The threads in the module are intended to be run in conjunction with 'xy_positioner_gui.py' only, as the
threads refer to specific callback functions from this file.

The module has the following classes:
    - AreaScanThread(threading.Thread): performs general area scans.
    - ZoomScanThread(threading.Thread): performs zoom scans at the maximum value.
                                        position found during the general area scan.
    - CorrectionThread(threading.Thread): retakes a previous measurement from the general area scan.

Authors:
Chang Hwan 'Oliver' Choi, Biomedical/Software Engineering Intern (Aug. 2018) - changhwan.choi@pctest.com
Ganesh Arvapalli, Software Engineering Intern (Jan. 2018) - ganesh.arvapalli@pctest.com
"""

import os
import threading
from src.motor_driver import MotorDriver
from src.narda_navigator import NardaNavigator
import numpy as np
import serial
import wx


class AreaScanThread(threading.Thread):
    """
    Thread for handling general area scans.
    """
    def __init__(self, parent, x_distance, y_distance, grid_step_dist, dwell_time,
                 save_dir, comment, meas_type, meas_field, meas_side, meas_rbw):
        """
        :param parent: Parent object (i.e. the Frame/GUI calling the thread).
        :param x_distance: Width of the scanning area.
        :param y_distance: Length of the scanning area.
        :param grid_step_dist: Step distance between each measurement point.
        :param dwell_time: Wait time at each scan point before measurements are recorded.
        :param save_dir: Directory for output files (.txt, .png).
        :param comment: Comment saved in the output file (.txt).
        :param meas_type: Measurement type (limb or body).
        :param meas_field: Measurement field (Electric or magnetic (mode A or B)).
        :param meas_side: Side of the phone being scanned.
        :param meas_rbw: Resolution bandwidth for the FFT.
        """
        self.parent = parent
        self.callback = parent.update_values
        self.x_distance = x_distance
        self.y_distance = y_distance
        self.grid_step_dist = grid_step_dist
        self.dwell_time = dwell_time
        self.save_dir = save_dir
        self.comment = comment
        self.meas_type = meas_type
        self.meas_field = meas_field
        self.meas_side = meas_side
        self.meas_rbw = meas_rbw

        self.num_steps = None  # Placeholder for number of motor steps needed to move one grid space
        self.values = None  # Placeholder for the array of values
        self.grid = None  # Placeholder for the coordinate grid array
        self.curr_row = None  # Current position row
        self.curr_col = None  # Current position col
        self.max_fname = None  # The filename of the screenshot for the maximum measurement
        super(AreaScanThread, self).__init__()

    def run(self):
        """
        Script run on thread start. Performs area scan on a separate thread.

        :return: Nothing.
        """
        print("Measurement Parameters:")
        print("Type: %s | Field: %s | Side: %s" % (self.meas_type, self.meas_field, self.meas_side))

        # Preparation
        x_points = int(np.ceil(np.around(self.x_distance / self.grid_step_dist, decimals=3))) + 1
        y_points = int(np.ceil(np.around(self.y_distance / self.grid_step_dist, decimals=3))) + 1
        # Check ports and instantiate relevant objects (motors, NARDA driver)
        try:
            m = MotorDriver()
        except serial.SerialException:
            print("Error: Connection to C4 controller was not found")
            wx.CallAfter(self.parent.enablegui)
            return
        narda = NardaNavigator()
        # Set measurement settings
        narda.selectTab('mode')
        narda.selectInputField(self.meas_field)
        narda.selectTab('span')
        narda.inputTextEntry('start', str(0.005))
        narda.inputTextEntry('stop', str(5))
        narda.selectRBW(self.meas_rbw)
        narda.selectTab('data')
        narda.enableMaxHold()

        # Calculate number of motor steps necessary to move one grid space
        self.num_steps = self.grid_step_dist / m.step_unit

        # Run scan
        self.values, self.grid, self.curr_row,\
        self.curr_col, self.max_fname = run_scan(x_points, y_points, m, narda, self.num_steps,
                                                 self.dwell_time, self.save_dir, self.comment,
                                                 self.meas_type, self.meas_field, self.meas_side)
        print("General area scan complete.")
        self.callback(self)
        wx.CallAfter(self.parent.run_post_scan)
        m.destroy()


class ZoomScanThread(threading.Thread):
    """
    Thread for handling zoom scans.
    """
    def __init__(self, parent, dwell_time, save_dir, comment, meas_type, meas_field,
                 meas_side, meas_rbw, num_steps, values, grid, curr_row, curr_col):
        """
        :param parent: Parent object (i.e. the Frame/GUI calling the thread).
        :param dwell_time: Wait time at each scan point before measurements are recorded.
        :param save_dir: Directory for output files (.txt, .png).
        :param comment: Comment saved in the output file (.txt).
        :param meas_type: Measurement type (limb or body).
        :param meas_field: Measurement field (Electric or magnetic (mode A or B)).
        :param meas_side: Side of the phone being scanned.
        :param meas_rbw: Resolution bandwidth for the FFT.
        :param num_steps: Number of motor steps per grid step.
        :param values: Numpy array of the recorded values.
        :param grid: Numpy array of index values (1-index).
        :param curr_row: The NS probe's current row position.
        :param curr_col: The NS probe's current column position.
        """
        self.parent = parent
        self.callback = parent.update_values
        self.num_steps = num_steps
        self.dwell_time = dwell_time
        self.save_dir = save_dir
        self.comment = comment
        self.meas_type = meas_type
        self.meas_field = meas_field
        self.meas_side = meas_side
        self.meas_rbw = meas_rbw
        self.curr_row = curr_row
        self.curr_col = curr_col

        self.values = values  # original array of values
        self.zoom_values = None  # Placeholder for zoom coordinates
        self.grid = grid  # Placeholder for the coordinate grid array
        super(ZoomScanThread, self).__init__()

    def run(self):
        """
        Script run on thread start. Performs zoom scan on a separate thread.

        :return: Nothing.
        """
        print("Measurement Parameters:")
        print("Type: %s | Field: %s | Side: %s" % (self.meas_type, self.meas_field, self.meas_side))

        # Preparation
        x_points = 5
        y_points = 5
        # Check ports and instantiate relevant objects (motors, NARDA driver)
        try:
            m = MotorDriver()
        except serial.SerialException:
            print("Error: Connection to C4 controller was not found")
            return -1
        narda = NardaNavigator()
        # Set measurement settings
        narda.selectTab('mode')
        narda.selectInputField(self.meas_field)
        narda.selectTab('span')
        narda.inputTextEntry('start', str(0.005))
        narda.inputTextEntry('stop', str(5))
        narda.selectRBW(self.meas_rbw)
        narda.selectTab('data')

        # Calculate number of motor steps necessary to move one grid space
        znum_steps = self.num_steps / 4.0  # Zoom scan steps are scaled down

        # Move to coordinate with maximum value
        max_val = self.values.max()
        max_row, max_col = np.where(self.values == float(max_val))
        print("Max value: %f" % max_val)
        print(max_row, max_col)
        print("Max value coordinates: Row - %d / Col - %d" % (max_row, max_col))
        row_steps = max_row - self.curr_row
        col_steps = max_col - self.curr_col
        self.curr_row = max_row
        self.curr_col = max_col
        if row_steps > 0:
            m.forward_motor_two(int(self.num_steps * row_steps))
        else:
            m.reverse_motor_two(int(-1 * self.num_steps * row_steps))
        if col_steps > 0:
            m.forward_motor_one(int(self.num_steps * col_steps))
        else:
            m.reverse_motor_one(int(-1 * self.num_steps * col_steps))

        # Run scan
        self.zoom_values, _, _, _, _ = run_scan(x_points, y_points, m, narda, znum_steps,
                                                self.dwell_time, self.save_dir, self.comment,
                                                self.meas_type, self.meas_field, 'z')
        # Move back to original position
        m.reverse_motor_one(int(2 * znum_steps))
        m.reverse_motor_two(int(2 * znum_steps))

        print("Zoom scan complete.")
        self.callback(self)
        wx.CallAfter(self.parent.run_post_scan)
        m.destroy()


class CorrectionThread(threading.Thread):
    """
    Thread for handling corrections of previous values from the general area scan.
    """
    def __init__(self, parent, target, num_steps, dwell_time, values, grid, curr_row, curr_col,
                 save_dir, meas_type, meas_field, meas_side, meas_rbw, max_fname):
        """
        :param parent: Parent object (i.e. the Frame/GUI calling the thread).
        :param target: index of the target position (index by the grid).
        :param num_steps: Number of motor steps per grid step.
        :param dwell_time: Wait time at each scan point before measurements are recorded.
        :param values: Numpy array of the recorded values.
        :param grid: Numpy array of index values (1-index).
        :param curr_row: The NS probe's current row position.
        :param curr_col: The NS probe's current column position.
        :param save_dir: Directory for output files (.txt, .png).
        :param meas_type: Measurement type (limb or body).
        :param meas_field: Measurement field (Electric or magnetic (mode A or B)).
        :param meas_side: Side of the phone being scanned.
        :param meas_rbw: Resolution bandwidth for the FFT.
        :param max_fname: Filename corresponding to highest measurement.
        """
        self.parent = parent
        self.callback = self.parent.update_values
        self.target = target
        self.num_steps = num_steps
        self.dwell_time = dwell_time
        self.values = values
        self.grid = grid
        self.curr_row = curr_row
        self.curr_col = curr_col
        self.save_dir = save_dir
        self.meas_type = meas_type
        self.meas_field = meas_field
        self.meas_side = meas_side
        self.meas_rbw = meas_rbw
        self.max_fname = max_fname
        super(CorrectionThread, self).__init__()

    def run(self):
        """
        Script run on thread start. Corrects a previous value from the general area scan results on a separate thread.

        :return: Nothing.
        """
        print("Measurement Parameters:")
        print("Type: %s | Field: %s | Side: %s" % (self.meas_type, self.meas_field, self.meas_side))

        # Check ports and instantiate relevant objects (motors, NARDA driver)
        try:
            m = MotorDriver()
        except serial.SerialException:
            print("Error: Connection to C4 controller was not found.")
            return -1
        narda = NardaNavigator()
        # Set measurement settings
        narda.selectTab('mode')
        narda.selectInputField(self.meas_field)
        narda.selectTab('span')
        narda.inputTextEntry('start', str(0.005))
        narda.inputTextEntry('stop', str(5))
        narda.selectRBW(self.meas_rbw)
        narda.selectTab('data')

        # Find the target location
        target_row, target_col = np.where(self.grid == int(self.target))
        row_steps = target_row - self.curr_row
        col_steps = target_col - self.curr_col

        # Move to target location
        print("R steps: %d   -   C steps %d" % (row_steps, col_steps))
        if row_steps > 0:
            m.forward_motor_two(int(self.num_steps * row_steps))
        else:
            m.reverse_motor_two(int(-1 * self.num_steps * row_steps))
        if col_steps > 0:
            m.forward_motor_one(int(self.num_steps * col_steps))
        else:
            m.reverse_motor_one(int(-1 * self.num_steps * col_steps))
        self.curr_row = target_row
        self.curr_col = target_col
        print(self.values)
        print("row:", self.curr_row, "col:", self.curr_col)
        fname = build_filename(self.meas_type, self.meas_field, self.meas_side, self.target)
        # Take measurement
        value = narda.takeMeasurement(self.dwell_time, fname, self.save_dir)
        self.values[self.curr_row, self.curr_col] = value
        print(self.values)
        # Check if max and take screenshot of plot/UI accordingly
        if value > self.values.max():
            print("New max val: %f" % value)
            # Switch to Snipping Tool in front of the NARDA program
            narda.saveBitmap(fname, self.save_dir)
            narda.bringToFront()  # Once bitmap is saved, return focus to NARDA
            os.rename(self.save_dir + '/' + self.max_fname + '.PNG', self.save_dir + '/' + fname + '.PNG')
        print("Correction of previous value complete.")
        self.callback(self)
        wx.CallAfter(self.parent.run_post_scan)
        m.destroy()


def run_scan(x_points, y_points, m, narda, num_steps, dwell_time, savedir, comment, meas_type, meas_field, meas_side):
    """
    Performs an area scan according to the specified parameters.
    The scan consists of moving the NS probe to an intended coordinate, taking a measurement, saving the results,
    and repeating this process until all coordinate points have been measured.

    :param x_points: Number of x-coordinate points.
    :param y_points: Number of y-coordinate points.
    :param m: Motor driver object.
    :param narda: NARDA navigator object.
    :param num_steps: Number of motor steps per grid step.
    :param dwell_time: Wait time at each scan point before measurements are recorded.
    :param save_dir: Directory for output files (.txt, .png).
    :param comment: Comment saved in the output file (.txt).
    :param meas_type: Measurement type (limb or body).
    :param meas_field: Measurement field (Electric or magnetic (mode A or B)).
    :param meas_side: Side of the phone being scanned.
    :return: Numpy array of all measurements, Numpy array of the measurement grid, current NS probe's coordinates (rows
             and columns), and the filename corresponding to the highest measurement point.
    """
    # Move to the initial position (top left) of grid scan and measure once
    move_to_pos_one(m, int(num_steps), x_points, y_points)

    # Generate a 'traversal grid' with values starting from 1 showing the order of measurement taking
    grid = generate_grid(x_points, y_points)
    values = np.zeros(grid.shape)  # Placeholder for filling in with measurement values

    print("Scan path:")
    print(grid)
    print("Values:")
    print(values)

    # Create an accumulator for the fraction of a step lost each time a grid space is moved
    frac_step = num_steps - int(num_steps)
    num_steps = int(num_steps)
    x_error, y_error = 0, 0  # Accumulator for x and y directions
    curr_row, curr_col = 0, 0  # Current coordinates of the NS testing probe
    curr_max = -1  # Current maximum value
    max_filename = ''  # Filename of the maximum measurement point

    # General Area Scan
    for i in range(1, grid.size + 1):
        # Find the position of the next
        next_row, next_col = np.where(grid == i)
        next_row = next_row[0]
        next_col = next_col[0]
        # Move the NS probe to the next position
        if next_row > curr_row:  # Move downwards
            y_error += frac_step
            m.forward_motor_two(num_steps + int(y_error))
            y_error -= int(y_error)
            curr_row = next_row
        elif next_col > curr_col:  # Move rightwards
            x_error += frac_step
            m.forward_motor_one(num_steps + int(x_error))  # Adjust distance by error
            x_error -= int(x_error)  # Subtract integer number of steps that were moved
            curr_col = next_col
        elif next_col < curr_col:  # Move leftwards
            x_error -= frac_step
            m.reverse_motor_one(num_steps + int(x_error))
            x_error -= int(x_error)
            curr_col = next_col
        # Build the filename for the measurements at this point
        fname = build_filename(meas_type, meas_field, meas_side, i)
        # Take the measurement and save relevant files
        value = narda.takeMeasurement(dwell_time, fname, savedir, comment)
        values[curr_row, curr_col] = value
        # If new maximum value found, save take a screenshot of the GUI interface
        if value > curr_max:
            print("New max val: %f" % value)
            # Switch to Snipping Tool in front of the NARDA program
            narda.saveBitmap(fname, savedir)
            narda.bringToFront()  # Once bitmap is saved, return focus to NARDA
            curr_max = value
            max_filename = fname
        print("---------")
        print(values)
    print("Renaming tmp.PNG to %s.PNG" % max_filename)
    # End of scan - rename screenshot file with the correct name
    try:
        os.rename(savedir + '/tmp.PNG', savedir + '/' + max_filename + '.PNG')
    except FileExistsError:
        print("File " + max_filename + ".PNG already exists. Overwriting file with new image file.")
        os.remove(savedir + '/' + max_filename + '.PNG')
        os.rename(savedir + '/tmp.PNG', savedir + '/' + max_filename + '.PNG')
    return values, grid, curr_row, curr_col, max_filename


def build_filename(meas_type, meas_field, meas_side, number):
    """
    Builds a filename based on the measurement parameters.

    :param meas_type: Measurement type (limb or body).
    :param meas_field: Measurement field (electric or magnetic (mode A or B)).
    :param meas_side: Side of the phone being measured.
    :param number: Point on the grid where the measurement was taken.
    :return: String filename.
    """
    filename = ''
    # Adding type marker
    if meas_type == 'Limb':
        filename += 'L'
    else:
        filename += 'B'
    filename += '_'
    # Adding field marker
    if meas_field == 'Electric':
        filename += 'E'
    else:
        filename += 'H'
    # Adding side marker
    if meas_side == 'Back':
        filename += 'S'
    else:
        filename += meas_side.lower()
    filename += str(int(number))
    return filename


def move_to_pos_one(moto, num_steps, rows, cols):
    """Move motor to first position in grid.

    :param moto: MotorDriver to control motion.
    :param num_steps: Number of motor steps between grid points.
    :param rows: Number of grid rows.
    :param cols: Number of grid cols.
    :return: None
    """
    moto.reverse_motor_two(int(num_steps * rows / 2.0))
    moto.reverse_motor_one(int(num_steps * cols / 2.0))


def generate_grid(rows, columns):
    """Create grid traversal visual in format of numpy matrix.
    Looks like a normal sequential matrix, but every other row is in reverse order.

    :param rows: Number of rows in grid.
    :param columns: Number of columns in grid.
    :return: Numpy matrix of correct values.
    """
    g = []
    for i in range(rows):
        row = list(range(i * columns + 1, (i + 1) * columns + 1))
        if i % 2 != 0:
            row = list(reversed(row))
        g += row
    g = np.array(g).reshape(rows, columns)
    return g


def convert_to_pts(arr, dist, x_off=0, y_off=0):
    """
    Convert matrix to set of points.
    #TODO: Probably not going to be using this one anymore.

    :param arr: matrix to convert.
    :param dist: distance between points in matrix.
    :param x_off: offset to add in x direction (if not at (0,0)).
    :param y_off: offset to add in y direction (if not at (0,0)).
    :return: xpts, ypts, zpts: List of points on each axis.
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
