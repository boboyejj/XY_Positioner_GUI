from NARDA_control import NARDAcontroller
import numpy as np
from motor_driver import MotorDriver
from post_scan_gui import PostScanGUI
from location_select_gui import LocationSelectGUI
import turtle


def move_to_pos_one(moto, num_steps, x, y):
    """Move motor to first position in grid.

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
    progress = np.matrix(grid)
    values = [[tuple() for i in range(y_points)] for j in range(x_points)]
    print values
    m = MotorDriver()
    narda = None
    if args.measure:
        narda = NARDAcontroller()

    franklin = turtle.Turtle()
    franklin.penup()
    franklin.setposition(-100, 100)
    franklin.pendown()
    num_steps = args.grid_step_dist / m.step_unit
    move_to_pos_one(m, int(num_steps), x_points, y_points)
    # TODO: MEASURE HERE
    if args.measure:
        narda.reset()
        narda.read_data()
        values[0][0] = tuple((narda.get_wide_band(), narda.get_highest_peak()))
    count = 1
    progress[progress == count] = 0
    print values
    # print np.argwhere(grid == count)[0], count

    frac_step = num_steps - int(num_steps)
    num_steps = int(num_steps)
    x_error, y_error = 0, 0
    going_forward = True
    j = 0
    for i in range(y_points):
        while j < x_points - 1:
            if going_forward:
                x_error += frac_step
                m.forward_motor_one(num_steps + int(x_error))
                franklin.circle(2)
                franklin.forward(20)
                # TODO: MEASURE HERE
                if args.measure:
                    narda.reset()
                    narda.read_data()
                    values[i][j] = tuple((narda.get_wide_band(), narda.get_highest_peak()))
                x_error = x_error - int(x_error)
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
            count += 1
            j += 1
            progress[progress == count] = 0
            print values
            # print np.argwhere(grid == count)[0], count
        count += 1
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
        # print np.argwhere(grid == count)[0], count

    print values
    # Post area scan loop (unless auto zoom has been implemented
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
            narda.destory()
            exit(1)

    # TODO: Auto-zoom-scan mode
