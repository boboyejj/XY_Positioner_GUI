"""
Created by Ganesh Arvapalli on 1/12/18
"""

from gooey import Gooey, GooeyParser
import Tkinter as tk
import random
from NARDA_control import read_data
import numpy as np
import argparse
from grid_scan import run_scan, generate_grid
import motor_driver
from location_select_gui import LocationSelectGUI
from post_scan_gui import PostScanGUI


@Gooey(program_name='NARDA Grid Scan', monospace_display=True, default_size=(800, 600), advanced=True)
def run_gui():
    parser = argparse.ArgumentParser(description='Scan over basic grid area. Built for C4 Motor Controller.')

    sub = parser.add_subparsers(title='Choose which command to run.', help='Subparser help goes here.',
                                dest='subparser_name')

    # Arguments for conducting a general area scan
    area_scan = sub.add_parser('area_scan', help='Run a standard grid scan or specified size.')
    area_scan.add_argument('x_distance', type=float, default=6 * 2.8, help='distance in the x direction')
    area_scan.add_argument('y_distance', type=float, default=4 * 2.8, help='distance in the y direction')
    area_scan.add_argument('grid_step_dist', type=float, default=2.8, help='distance to between grid points '
                                                                           '(default=2.8cm)')
    area_scan.add_argument('--measure', action='store_true', default=False, help='perform measurement '
                                                                                 '(can be disabled to test motors)')
    area_scan.add_argument('--dwell_time', type=float, default=2,
                           help='time in seconds to wait at each measurement point')
    area_scan.add_argument('--outfile_location', help='choose directory where data will be output')

    # Arguments for moving to a specific position in the grid
    pos_move = sub.add_parser('pos_move', help='Move to specified position')
    pos_move.add_argument('x_distance', type=float, default=6 * 2.8, help='distance in the x direction')
    pos_move.add_argument('y_distance', type=float, default=4 * 2.8, help='distance in the y direction')
    pos_move.add_argument('grid_step_dist', type=float, default=2.8, help='distance to between grid points '
                                                                          '(default=2.8cm)')
    pos_move.add_argument('--measure', action='store_true', default=False, help='perform measurement '
                                                                                '(can be disabled to test motors)')
    pos_move.add_argument('--dwell_time', type=float, default=2, help='time in seconds to wait at measurement point')
    pos_move.add_argument('--outfile_location', help='choose directory where data will be output')

    # Arguments for conduction tests on extensions outside of a point.
    extension = sub.add_parser('extension',
                               help='Run extensions on a data point. Must have already moved to that position.')
    extension.add_argument('level', choices=list(['1', '2']),
                           help='What level of extensions outward would you like to go?')
    extension.add_argument('--dwell_time', type=float, default=2,
                           help='time in seconds to wait at each measurement point')
    extension.add_argument('--outfile_location', help='choose directory where data will be output')

    # Arguments for moving motors back to center position
    reset_motors = sub.add_parser('reset_motors', help='Move motors back to their original positions')
    reset_motors.add_argument('--wait', action='store_true', default=False,
                              help='Check this box to signify that you understand you are not allowed to touch '
                                   'anything while the motors are moving back to their home positions')

    args = parser.parse_args()
    print args
    if args.subparser_name == 'area_scan':
        print 1
        run_scan(args)
    elif args.subparser_name == 'pos_move':
        x_points = int(np.ceil(np.around(args.x_distance / args.grid_step_dist, decimals=3)))
        y_points = int(np.ceil(np.around(args.y_distance / args.grid_step_dist, decimals=3)))
        grid = generate_grid(y_points, x_points)
        loc_gui = LocationSelectGUI(None, grid)
        loc_gui.title('Location Selection')
        loc_gui.mainloop()
        location = loc_gui.get_gui_value()
        print location
    elif args.subparser_name == 'extension':
        print 'Extensions not implemented as of yet.'
    elif args.subparser_name == 'reset_motors':
        if args.wait:
            m = motor_driver.MotorDriver()
            m.home_motors()
            m.destroy()
        else:
            print 'Please check the box and try again. You must wait until the motors are done resetting.'
            exit(1)

    # x_distance, y_distance, step_size, scan, reset = args.X_distance, args.Y_distance, args.Motor_step_distance, \
    #                                                 args.scan, args.reset
    # xpoints = int(x_distance / step_size) + 1
    # ypoints = int(y_distance / step_size) + 1
    # print xpoints, ypoints, step_size, scan, reset


if __name__ == '__main__':
    run_gui()
