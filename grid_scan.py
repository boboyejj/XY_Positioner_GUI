from NARDA_control import NARDAcontroller
import numpy as np
from motor_driver import MotorDriver
from post_scan_gui import PostScanGUI
from location_select_gui import LocationSelectGUI
from matplotlib import pyplot as plt
import turtle


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
    # Calculate dimensions of grid and generate it
    x_points = int(np.ceil(np.around(args.x_distance / args.grid_step_dist, decimals=3)))
    y_points = int(np.ceil(np.around(args.y_distance / args.grid_step_dist, decimals=3)))
    grid = generate_grid(y_points, x_points)

    # For showing progress through grid
    progress = np.matrix(grid)
    # For storing values of highest peak/wide-band
    values = [[tuple() for i in range(y_points)] for j in range(x_points)]

    # Check ports and instantiate relevant objects
    m = MotorDriver()
    narda = None
    if args.measure:
        narda = NARDAcontroller(args.start_freq, args.step_freq, args.stop_freq)

    # Visualization of robot progress will be done using python Turtle (temporary)
    franklin = turtle.Turtle()
    franklin.penup()
    franklin.setposition(-100, 100)
    franklin.pendown()

    # Calculate number of motor steps necessary to move one grid space
    num_steps = args.grid_step_dist / m.step_unit
    # Move to the initial position (top left) of grid scan and measure once
    move_to_pos_one(m, int(num_steps), x_points, y_points)
    # TODO: MEASURE HERE
    if args.measure:
        narda.reset()
        narda.read_data()
        values[0][0] = tuple((narda.get_wide_band(), narda.get_highest_peak()))
    count = 1   # Tracks our current progress through the grid
    progress[progress == count] = 0
    print values
    # print np.argwhere(grid == count)[0], count

    # Create an accumulator for the fraction of a step lost each time a grid space is moved
    frac_step = num_steps - int(num_steps)
    num_steps = int(num_steps)
    x_error, y_error = 0, 0     # Accumulator for x and y directions

    # Main loop
    going_forward = True    # Start by moving forward
    j = 0
    for i in range(y_points):
        while j < x_points - 1:
            if going_forward:
                x_error += frac_step    # Add to error
                m.forward_motor_one(num_steps + int(x_error))   # Increase distance moved by adding error
                franklin.circle(2)
                franklin.forward(20)
                # TODO: MEASURE HERE
                if args.measure:
                    narda.reset()
                    narda.read_data()
                    values[i][j] = tuple((narda.get_wide_band(), narda.get_highest_peak()))
                x_error = x_error - int(x_error)    # Subtract integer number of steps that were moved
            # Do the same for when the robot is moving backwards as well
            else:
                x_error -= frac_step
                m.reverse_motor_one(num_steps + int(x_error))   # Should be |x_error|?
                franklin.circle(2)
                franklin.backward(20)
                # TODO: MEASURE HERE
                if args.measure:
                    narda.reset()
                    narda.read_data()
                    values[i][j] = tuple((narda.get_wide_band(), narda.get_highest_peak()))
                x_error = x_error - int(x_error)
            # Increment our progress counter and print out current set of values
            count += 1
            j += 1
            progress[progress == count] = 0
            print values
        count += 1      # Increment our progress counter
        # If counter is outside accepted bounds, measure once and exit
        if count > x_points * y_points:
            franklin.circle(2)
            # TODO: MEASURE HERE
            if args.measure:
                narda.reset()
                narda.read_data()
                values[i][j] = tuple((narda.get_wide_band(), narda.get_highest_peak()))
            count -= 1  # Reset count to end of grid
            progress[progress == count] = 0
            print values
            break
        # Else update counter, measure, and move down. Reverse direction
        progress[progress == count] = 0
        y_error += frac_step
        m.forward_motor_two(num_steps + int(y_error))
        franklin.circle(2)
        franklin.right(90)
        franklin.forward(20)
        franklin.left(90)
        print values
        # TODO: MEASURE HERE
        if args.measure:
            narda.reset()
            narda.read_data()
            values[i][j] = tuple((narda.get_wide_band(), narda.get_highest_peak()))
        y_error = y_error - int(y_error)
        going_forward = not going_forward
        j = 0

    # Post area scan loop (unless auto zoom has been implemented)
    while True:
        # Plot results
        if args.measure:
            highest_peak = np.zeros(grid.shape)
            wide_band = np.zeros(grid.shape)
            for i in range(len(values)):
                for j in range(len(values[0])):
                    wide_band[i][j] = values[i][j][0]
                    highest_peak[i][j] = values[i][j][1][0]
            plt.figure(1)
            wide = plt.subplot(211)
            wide.set_title('Wide Band Measurement')
            plt.contourf(wide_band)

            high = plt.subplot(212)
            high.set_title('Highest Peak Measurement')
            plt.contourf(highest_peak)
            plt.show(block=False)

        post_gui = PostScanGUI(None)
        post_gui.title('Post Scan Options')
        post_gui.mainloop()

        choice = post_gui.get_gui_value()
        print choice
        if choice == 'Exit':
            print 'Exiting program...'
            m.destroy()
            if narda is not None:
                narda.destroy()
            exit(0)
        elif choice == 'Zoom Scan':
            print 'Please select location.'
            loc_gui = LocationSelectGUI(None, grid)
            loc_gui.title('Location Selection')
            loc_gui.mainloop()
            location = loc_gui.get_gui_value()
            print "Current location: ", np.argwhere(grid == count), "Desired location: ", np.argwhere(grid == location)
            grid_move = (np.argwhere(grid == location) - np.argwhere(grid == count))[0]
            print 'Need to move', grid_move
            if grid_move[1] > 0:
                m.forward_motor_one(num_steps * grid_move[1])
            else:
                m.reverse_motor_one(num_steps * grid_move[1])
            if grid_move[0] > 0:
                m.forward_motor_two(num_steps * grid_move[0])
            else:
                m.reverse_motor_two(num_steps * grid_move[0])
            count = location
            grid_loc = np.argwhere(grid == count)[0]
            print 'Please enter required parameters'

            # TODO: Implement zoom scan GUI

            count = location
        elif choice == 'Correct Previous Value':
            print 'Please select location.'
            loc_gui = LocationSelectGUI(None, grid)
            loc_gui.title('Location Selection')
            loc_gui.mainloop()
            location = loc_gui.get_gui_value()
            print "Current location: ", np.argwhere(grid == count), "Desired location: ", np.argwhere(grid == location)
            grid_move = (np.argwhere(grid == location) - np.argwhere(grid == count))[0]
            print 'Need to move', grid_move
            if grid_move[1] > 0:
                m.forward_motor_one(num_steps * grid_move[1])
            else:
                m.reverse_motor_one(num_steps * grid_move[1])
            if grid_move[0] > 0:
                m.forward_motor_two(num_steps * grid_move[0])
            else:
                m.reverse_motor_two(num_steps * grid_move[0])
            count = location
            grid_loc = np.argwhere(grid == count)[0]
            print grid_loc
            # TODO: MEASURE HERE
            if args.measure:
                narda.reset()
                narda.read_data()
                values[grid_loc[0]][grid_loc[1]] = tuple((narda.get_wide_band(), narda.get_highest_peak()))
        else:
            print 'Invalid choice'
            m.destroy()
            if narda is not None:
                narda.destroy()
            exit(1)

    # TODO: Auto-zoom-scan mode
