import serial
import time
import sys
import turtle
import random
from NARDA_control import read_data
import numpy as np
import motor_driver
from post_scan_gui import PostScanGUI
from location_select_gui import LocationSelectGUI


def move_to_pos_one(moto, num_steps, x, y):
    """
    Move motor to first position in grid.

    :param moto: MotorDriver to control motion
    :param num_steps: Number of motor steps between grid points
    :param x: Number of grid columns
    :param y: Number of grid rows
    :return: None
    """
    moto.reverse_motor_one(int(num_steps * x / 2))
    moto.reverse_motor_two(int(num_steps * y / 2))

def generate_grid(rows, columns):
    """Create grid traversal visual in format of numpy matrix.
    Looks like a normal sequential matrix, but every other row is in reverse order.

    :param rows: Number of rows in grid
    :param columns: Number of columns in grid
    :return: Numpy matrix of correct values
    """
    g = np.zeros((rows, columns))
    for i in range(rows):
        row = range(i * columns + 1, (i + 1) * columns + 1)
        if i % 2 != 0:
            row.reverse()
        g[i] = row
    return g


def run_scan(args):
    """Conduct grid search by moving motors to correct positions and measuring

    :param args: Arguments passed in from GUI (see GUI driver file for details)
    :return: None
    """
    x_points = int(np.ceil(np.around(args.x_distance / args.grid_step_dist, decimals=3)))
    y_points = int(np.ceil(np.around(args.y_distance / args.grid_step_dist, decimals=3)))
    grid = generate_grid(y_points, x_points)
    m = motor_driver.MotorDriver()

    num_steps = args.grid_step_dist / m.step_unit
    move_to_pos_one(m, num_steps, x_points, y_points)
    # TODO: MEASURE HERE
    count = 1
    print np.argwhere(grid == count)[0], count

    frac_step = num_steps - int(num_steps)
    x_error, y_error = 0, 0

    going_forward = True
    for i in range(y_points):
        for j in range(x_points - 1):
            if going_forward:
                x_error += frac_step
                m.forward_motor_one(num_steps + int(x_error))
                # TODO: MEASURE HERE
                x_error = x_error - int(x_error)
            else:
                x_error -= frac_step
                m.reverse_motor_one(num_steps + int(x_error))   # Should be |x_error|?
                # TODO: MEASURE HERE
                x_error = x_error - int(x_error)
            count += 1
            print np.argwhere(grid == count)[0], count
        y_error += frac_step
        m.forward_motor_two(num_steps + int(y_error))
        # TODO: MEASURE HERE
        y_error = y_error - int(y_error)
        going_forward = not going_forward
        count += 1
        if count > x_points * y_points:
            # TODO: MEASURE HERE
            count -= 1  # Reset count to end of grid
            break
        print np.argwhere(grid == count)[0], count

    while True:
        post_gui = PostScanGUI(None)
        post_gui.title('Post Scan Options')
        post_gui.mainloop()

        choice = post_gui.get_gui_value()
        print choice
        if choice == 'Exit':
            print 'Exiting program...'
            m.destroy()
            exit(0)
        elif choice == 'Zoom Scan':
            print 'Please select location.'
            loc_gui = LocationSelectGUI(None, grid)
            loc_gui.title('Location Selection')
            loc_gui.mainloop()
            location = loc_gui.get_gui_value()
            print "Current location: ", np.argwhere(grid == count), "Desired location: ", np.argwhere(grid == location)
            print 'Please enter required parameters'
            count = location
        elif choice == 'Correct Previous Value':
            print 'Please select location.'
            loc_gui = LocationSelectGUI(None, grid)
            loc_gui.title('Location Selection')
            loc_gui.mainloop()
            location = loc_gui.get_gui_value()
            print "Current location: ", np.argwhere(grid == count), "Desired location: ", np.argwhere(grid == location)
            print 'Need to Move', np.argwhere(grid == count) - np.argwhere(grid == location)
            count = location
        else:
            print 'Invalid choice'
            m.destroy()
            exit(1)
