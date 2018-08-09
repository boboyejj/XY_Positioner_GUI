#!/usr/bin/env python

"""
    Created by Ganesh Arvapalli on 1/12/18
    ganesh.arvapalli@pctest.com
"""

from gooey import Gooey, GooeyParser
import numpy as np
import argparse
from src.grid_scan_manual import run_scan, generate_grid, move_to_pos_one
from src.motor_driver import MotorDriver
from src.location_select_gui import LocationSelectGUI
from src.manual_gui_grid import ManualGridGUI


@Gooey(program_name='NARDA Grid Scan', monospace_display=True, default_size=(800, 600), advanced=True)
def run_gui():
    parser = GooeyParser(description='Scan over basic grid area. Built for C4 Motor Controller.')

    sub = parser.add_subparsers(help='Subparser help goes here.', dest='subparser_name')

    # Arguments for conducting a general area scan
    area_scan = sub.add_parser('area_scan', help='Run a standard grid scan or specified size.')
    area_scan.add_argument('x_distance', type=float, default=3 * 2.8, help='distance in the x direction (in cm)')
    area_scan.add_argument('y_distance', type=float, default=3 * 2.8, help='distance in the y direction (in cm)')
    #area_scan.add_argument('x_distance', type=float, default=6 * 2.8, help='distance in the x direction (in cm)')
    #area_scan.add_argument('y_distance', type=float, default=4 * 2.8, help='distance in the y direction (in cm)')
    area_scan.add_argument('grid_step_dist', type=float, default=2.8, help='distance to between grid points (in cm)')
    area_scan.add_argument('type', choices=['Limb', 'Body'], default='Limb')
    area_scan.add_argument('field', choices=['Electric', 'Magnetic (Mode A)', 'Magnetic (Mode B)'],
                                 default='Electric')
    area_scan.add_argument('side', choices=['front', 'S', 'left', 'right', 'top', 'bottom'], default='front')
    area_scan.add_argument('dwell_time', type=float, default=1, help='dwell time at single measurement point (in s)')
    area_scan.add_argument('zoom_scan_dwell_time', type=float, default=1.5,
                           help='dwell time at single measurement point (in s) for zoom scan measurements')
    area_scan.add_argument('save_directory', help='directory to save txt files and GUI images',
                           type=argparse.FileType('r'), widget='DirChooser',
                           default='C:\\Users\changhwan.choi\PycharmProjects\XY_Positioner_GUI\\temp')
    area_scan.add_argument('--measure', action='store_true', default=True, help='perform measurement '
                                                                                '(can be disabled to test motors)')
    area_scan.add_argument('--auto_zoom_scan', action='store_true', default=False,
                           help='perform zoom scan automatically (can be disabled to conduct multiple area scans')
    area_scan.add_argument('--filename', default='raw_values', help='choose what to call the saved file')

    # Arguments for moving to a specific position in the grid
    pos_move = sub.add_parser('pos_move', help='Move to specified position')
    pos_move.add_argument('x_distance', type=float, default=6 * 2.8, help='distance in the x direction (in cm)')
    pos_move.add_argument('y_distance', type=float, default=4 * 2.8, help='distance in the y direction (in cm)')
    pos_move.add_argument('grid_step_dist', type=float, default=2.8, help='distance to between grid points (in cm)')
    # pos_move.add_argument('--measure', action='store_true', default=False, help='perform measurement '
    #                                                                             '(can be disabled to test motors)')
    # pos_move.add_argument('--outfile_location', default='', help='choose directory where data will be output')

    # Arguments for moving motors back to center position
    reset_motors = sub.add_parser('reset_motors', help='Move motors back to their original positions')
    reset_motors.add_argument('--wait', action='store_true', default=False,
                              help='Check this box to say that you understand you are not allowed to touch '
                                   'anything while the motors are homing!')
    reset_motors.add_argument('--scan_30', action='store_true', default=True,
                              help='choose if you are using the 30-inch system')

    # Arguments for moving motors manually
    manual_move = sub.add_parser('manual', help='Move motors manually according to a specified distance')
    manual_move.add_argument('x_distance', default=2.8, help='How far an x step will move left or right (in cm)')
    manual_move.add_argument('y_distance', default=2.8, help='How far a y step will move up or down (in cm)')
    # manual_move.add_argument('dwell_time', default=240, help='Dwell time at single measurement point (in s)')

    args = parser.parse_args()
    print(args)

    # Main cases
    if args.subparser_name == 'area_scan':
        run_scan(args)
    elif args.subparser_name == 'pos_move':
        # Generate grid following scan path
        x_points = int(np.ceil(np.around(args.x_distance / args.grid_step_dist, decimals=3)))
        y_points = int(np.ceil(np.around(args.y_distance / args.grid_step_dist, decimals=3)))
        grid = generate_grid(y_points, x_points)

        # Show GUI with selectable buttons for where you want to go
        location = 0
        loc_gui = LocationSelectGUI(None, grid)
        loc_gui.title('Location Selection')
        loc_gui.mainloop()
        location = loc_gui.get_gui_value()
        if location == None or location == 0:
            print("Please select an appropriate value")
            exit(1)
        grid_loc = np.argwhere(grid == location)[0]

        m = MotorDriver()
        num_steps = int(args.grid_step_dist / m.step_unit)

        # Move to first position in grid, then move to correct grid location
        move_to_pos_one(m, num_steps, x_points, y_points)
        m.forward_motor_one(num_steps * grid_loc[1])
        m.forward_motor_two(num_steps * grid_loc[0])
        exit(0)
    elif args.subparser_name == 'reset_motors':
        # Ensure that user waits until motors are completely done homing before continuing on
        if args.wait:
            if args.scan_30:
                m = MotorDriver(home=(5000, 6000))
            else:
                m = MotorDriver()
            m.home_motors()
            m.destroy()
            exit(0)
        else:
            print("Please check the box and try again. You must wait until the motors are done resetting.")
            exit(1)
    elif args.subparser_name == 'manual':
        man = ManualGridGUI(None, float(args.x_distance), float(args.y_distance))
        man.title('Manual Control')
        man.mainloop()
        exit(0)


if __name__ == '__main__':
    run_gui()
