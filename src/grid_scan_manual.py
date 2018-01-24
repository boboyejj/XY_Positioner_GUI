import numpy as np
from motor_driver import MotorDriver
from post_scan_gui import PostScanGUI
from location_select_gui import LocationSelectGUI
from matplotlib import pyplot as plt
from matplotlib import mlab
from data_entry_gui import DataEntryGUI
import os
from scipy import interpolate
from timer_gui import TimerGUI
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


def convert_to_pts(arr, dist, x_off=0, y_off=0):
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
    print xpts, ypts, zpts
    return xpts, ypts, zpts


def run_scan(args):
    """Conduct grid search by moving motors to correct positions and measuring

    :param args: Arguments passed in from GUI (see GUI driver file for details)
    :return: None
    """
    # Calculate dimensions of grid and generate it
    x_points = int(np.ceil(np.around(args.x_distance / args.grid_step_dist, decimals=3)))
    y_points = int(np.ceil(np.around(args.y_distance / args.grid_step_dist, decimals=3)))
    grid = generate_grid(y_points, x_points)
    print 'Path: '
    print grid

    # For storing values of highest peak/wide-band
    values = np.zeros(grid.shape)
    print 'Current values: '
    print values
    grid_points = []

    # Check ports and instantiate relevant objects
    m = MotorDriver()
    narda = None

    # Visualization of robot progress will be done using python Turtle (temporary)
    # franklin = turtle.Turtle()
    # franklin.penup()
    # franklin.setposition(-100, 100)
    # franklin.pendown()

    # Calculate number of motor steps necessary to move one grid space
    num_steps = args.grid_step_dist / m.step_unit
    # Move to the initial position (top left) of grid scan and measure once
    move_to_pos_one(m, int(num_steps), x_points, y_points)
    # TODO: MEASURE HERE
    if args.measure:
        man = DataEntryGUI(None)
        man.title('Data Entry')
        man.mainloop()
        values[0][0] = man.getval()
        # loc = np.argwhere(grid == 1)[0]
        # grid_points.append((loc * args.grid_step_dist, man.getval()))
    count = 1  # Tracks our current progress through the grid

    print values
    # print np.argwhere(grid == count)[0], count

    # Create an accumulator for the fraction of a step lost each time a grid space is moved
    frac_step = num_steps - int(num_steps)
    num_steps = int(num_steps)
    x_error, y_error = 0, 0  # Accumulator for x and y directions


    # Main loop
    going_forward = True  # Start by moving forward
    j = 0
    for i in range(y_points):
        while j < x_points - 1:
            if going_forward:
                x_error += frac_step  # Add to error
                m.forward_motor_one(num_steps + int(x_error))  # Increase distance moved by adding error
                count += 1
                loc = np.argwhere(grid == count)[0]
                print '------------'
                # franklin.circle(2)
                # franklin.forward(20)
                # TODO: MEASURE HERE
                if args.measure:
                    man = DataEntryGUI(None)
                    man.title('Data Entry')
                    man.mainloop()
                    values[loc[0]][loc[1]] = man.getval()
                    # grid_points.append((loc * args.grid_step_dist, man.getval()))
                x_error = x_error - int(x_error)  # Subtract integer number of steps that were moved
            # Do the same for when the robot is moving backwards as well
            else:
                x_error -= frac_step
                m.reverse_motor_one(num_steps + int(x_error))  # Should be |x_error|?
                count += 1
                loc = np.argwhere(grid == count)[0]
                print '------------'
                # franklin.circle(2)
                # franklin.backward(20)
                # TODO: MEASURE HERE
                if args.measure:
                    man = DataEntryGUI(None)
                    man.title('Data Entry')
                    man.mainloop()
                    values[loc[0]][loc[1]] = man.getval()
                    # grid_points.append((loc * args.grid_step_dist, man.getval()))
                x_error = x_error - int(x_error)
            # Increment our progress counter and print out current set of values
            j += 1
            print values

        y_error += frac_step
        # m.forward_motor_two(num_steps + int(y_error))
        count += 1  # Increment our progress counter
        # If counter is outside accepted bounds, exit
        if count > x_points * y_points:
            count -= 1  # Reset count to end of grid
            loc = np.argwhere(grid == count)[0]
            # print loc
            # franklin.circle(2)
            break
        m.forward_motor_two(num_steps + int(y_error))
        # Else update counter, measure, and move down. Reverse direction
        loc = np.argwhere(grid == count)[0]
        print '------------'
        # franklin.circle(2)
        # franklin.right(90)
        # franklin.forward(20)
        # franklin.left(90)
        # TODO: MEASURE HERE
        if args.measure:
            man = DataEntryGUI(None)
            man.title('Data Entry')
            man.mainloop()
            values[loc[0]][loc[1]] = man.getval()
            # grid_points.append((loc * args.grid_step_dist, man.getval()))
        print values
        y_error = y_error - int(y_error)
        going_forward = not going_forward
        j = 0

    # print grid_points
    grid_points = convert_to_point_list(values)

    # Post area scan loop (unless auto zoom has been implemented)
    zoom_pts = []
    place = None
    while True:
        # Plot results
        if args.measure:
            # Known to work more or less
            # plt.imshow(values, interpolation='bilinear')
            # cbar = plt.colorbar()
            # cbar.set_label('Signal Level')
            # plt.show(block=False)

            # X, Y, Z = convert_to_pts(values, args.grid_step_dist)

            # X, Y = np.meshgrid(np.arange(-values.shape[0]/2, values.shape[0]/2), np.arange(-values.shape[1]/2, values.shape[1]/2))
            # print X, Y
            # plt.scatter(X, Y, c=values)
            # plt.show()
            if place is not None:
                x_off = (place[0] - values.shape[0] / 2) * args.grid_step_dist
                y_off = (place[1] - values.shape[1] / 2) * args.grid_step_dist
                zoomX, zoomY, zoomZ = convert_to_pts(zoom_pts, args.grid_step_dist / 4, x_off, y_off)
                print zoomX
                print zoomY
                print zoomZ
                # X.extend(zoomX)
                # Y.extend(zoomY)
                # Z.extend(zoomZ)

           # xi = np.linspace(min(X), max(X), 100)
           # yi = np.linspace(min(Y), max(Y), 100)
           # zi = mlab.griddata(X, Y, Z, xi, yi, interp='linear')
           # fig, axes = plt.subplots(1, 1)
           # axes.set_aspect('equal')
           # graph = axes.contour(xi, yi, zi, 15, linewidths=0.5)
           # graph = axes.contourf(xi, yi, zi, 15, vmax=abs(zi).max(), vmin=abs(zi).min())
           # axes.scatter(X, Y, marker='o', s=5, cmap=graph.cmap)
           # cbar = fig.colorbar(graph)
          #  cbar.set_label('Signal Level')
          #  axes.margins(0.05)
          #  plt.show(block=False)

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

        # TODO: Remember to uncomment plt save fig!

        elif choice == 'Save Data':
            # TODO: Save file method that creates place for files
            if args.measure:
                # plt.savefig(args.outfile_location + './results/contour_plot.png', bbox_inches='tight')
                plt.close()
                if not os.path.exists(args.outfile_location):
                    print 'Path does not exist, using default results folder'
                    os.chdir('..')
                    if not os.path.exists('results'):
                        os.makedirs('results')
                    args.outfile_location = 'results'
                my_path = os.path.join(os.getcwd(), args.outfile_location, 'raw_values.txt')
                print my_path
                file = open(my_path, 'w+')
                for line in values:
                    file.write(str(line) + '\n')
                file.close()
            else:
                print 'No data to save.'
        elif choice == 'Zoom Scan':
            # First need to move to correct position (find max and move to it)
            place = np.unravel_index(values.argmax(), values.shape)
            count = grid[place[0]][place[1]]
            print place
            print count

            plt.close()
            # print 'Please select location.'
            # loc_gui = LocationSelectGUI(None, grid)
            # loc_gui.title('Location Selection')
            # loc_gui.mainloop()
            # location = loc_gui.get_gui_value()
            # # print "Current location: ", np.argwhere(grid == count), "Desired location: ", np.argwhere(grid == location)
            # grid_move = (np.argwhere(grid == location) - np.argwhere(grid == count))[0]
            # # print 'Need to move', grid_move
            # if grid_move[1] > 0:
            #     m.forward_motor_one(num_steps * grid_move[1])
            # else:
            #     m.reverse_motor_one(num_steps * grid_move[1])
            # if grid_move[0] > 0:
            #     m.forward_motor_two(num_steps * grid_move[0])
            # else:
            #     m.reverse_motor_two(num_steps * grid_move[0])
            # count = location

            # TODO: Implement zoom scan GUI

            if not args.auto_zoom_scan:
                zoomed = auto_zoom(args, m)
                grid_points = combine_matrices(grid_points, zoomed, place)
                zoom_pts = 32 * np.ones((5, 5))
        elif choice == 'Correct Previous Value':
            plt.close()
            print 'Please select location.'
            loc_gui = LocationSelectGUI(None, grid)
            loc_gui.title('Location Selection')
            loc_gui.mainloop()
            location = loc_gui.get_gui_value()
            # print "Current location: ", np.argwhere(grid == count), "Desired location: ", np.argwhere(grid == location)
            grid_move = (np.argwhere(grid == location) - np.argwhere(grid == count))[0]
            # print 'Need to move', grid_move
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
                man = DataEntryGUI(None)
                man.title('Data Entry')
                man.mainloop()
                values[grid_loc[0]][grid_loc[1]] = man.getval()
                man.quit()
        else:
            print 'Invalid choice'
            m.destroy()
            if narda is not None:
                narda.destroy()
            exit(1)


def auto_zoom(args, m):
    x_points = 5
    y_points = 5
    grid = generate_grid(x_points, y_points)
    values = np.zeros(grid.shape)
    zoom_points = []

    # Calculate number of motor steps necessary to move one grid space
    num_steps = args.grid_step_dist / (4.0 * m.step_unit)
    # Move to the initial position (top left) of grid scan and measure once
    move_to_pos_one(m, int(num_steps), x_points, y_points)
    # TODO: MEASURE HERE
    if args.measure:
        man = DataEntryGUI(None)
        man.title('Data Entry')
        man.mainloop()
        values[0][0] = man.getval()
        loc = np.argwhere(grid == 1)[0]
        zoom_points.append((loc * args.grid_step_dist, man.getval()))
    count = 1  # Tracks our current progress through the grid

    print values

    # Create an accumulator for the fraction of a step lost each time a grid space is moved
    frac_step = num_steps - int(num_steps)
    num_steps = int(num_steps)
    x_error, y_error = 0, 0  # Accumulator for x and y directions

    # Main loop
    going_forward = True  # Start by moving forward
    j = 0
    for i in range(y_points):
        while j < x_points - 1:
            if going_forward:
                x_error += frac_step  # Add to error
                m.forward_motor_one(num_steps + int(x_error))  # Increase distance moved by adding error
                count += 1
                loc = np.argwhere(grid == count)[0]
                print '------------'
                # TODO: MEASURE HERE
                if args.measure:
                    man = DataEntryGUI(None)
                    man.title('Data Entry')
                    man.mainloop()
                    values[loc[0]][loc[1]] = man.getval()
                    zoom_points.append((loc * args.grid_step_dist, man.getval()))
                x_error = x_error - int(x_error)  # Subtract integer number of steps that were moved
            # Do the same for when the robot is moving backwards as well
            else:
                x_error -= frac_step
                m.reverse_motor_one(num_steps + int(x_error))  # Should be |x_error|?
                count += 1
                loc = np.argwhere(grid == count)[0]
                print '------------'
                # TODO: MEASURE HERE
                if args.measure:
                    man = DataEntryGUI(None)
                    man.title('Data Entry')
                    man.mainloop()
                    values[loc[0]][loc[1]] = man.getval()
                    zoom_points.append((loc * args.grid_step_dist, man.getval()))
                x_error = x_error - int(x_error)
            # Increment our progress counter and print out current set of values
            j += 1
            print values

        y_error += frac_step
        # m.forward_motor_two(num_steps + int(y_error))
        count += 1  # Increment our progress counter
        # If counter is outside accepted bounds, exit
        if count > x_points * y_points:
            count -= 1  # Reset count to end of grid
            loc = np.argwhere(grid == count)[0]
            break
        m.forward_motor_two(num_steps + int(y_error))
        # Else update counter, measure, and move down. Reverse direction
        loc = np.argwhere(grid == count)[0]
        print '------------'
        # TODO: MEASURE HERE
        if args.measure:
            man = DataEntryGUI(None)
            man.title('Data Entry')
            man.mainloop()
            values[loc[0]][loc[1]] = man.getval()
            zoom_points.append((loc * args.grid_step_dist, man.getval()))
        print values
        y_error = y_error - int(y_error)
        going_forward = not going_forward
        j = 0

    return zoom_points


# Puts m2 into m1 with equal spacing between positions
# Matrix list formatted as (array(x, y), z)
# pos formatted as (i, j)
def combine_matrices(m1_list, m2_list, pos):
    print 'Initial list:', m1_list
    print 'To combine with:', m2_list
    final_list = m1_list
    for point in m2_list:
        xy = point[0]
        xy = ((xy[0] - 2) / 4 + pos[0], (xy[1] - 2) / 4 + pos[1])
        xy += pos
        z = point[1]
        final_list.append((xy, z))
    print 'Final results:', final_list
    return final_list

def convert_to_point_list(matrix):
    point_list = []
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            point_list.append(((i, j), matrix[i, j]))

    return point_list


def main():
    a = Args()
    run_scan(a)
    # vals = np.ones((2, 3))
    # X, Y, Z = convert_to_pts(2.4, vals)
    # print X
    # print Y
    # print Z


class Args:
    def __init__(self):
        self.x_distance = 2
        self.y_distance = 2
        self.grid_step_dist = 1
        self.outfile_location = ''
        self.measure = True
        self.auto_zoom_scan = True


if __name__ == '__main__':
    main()
