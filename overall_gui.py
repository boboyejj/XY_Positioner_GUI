"""
Created by Ganesh Arvapalli on 1/12/18
"""

from gooey import Gooey, GooeyParser
import Tkinter as tk
import random
from NARDA_control import read_data
import numpy as np
import argparse


@Gooey(program_name='NARDA Grid Scan', monospace_display=True, default_size=(600, 600), advanced=True, optional_cols=2)
def run_gui():
    parser = argparse.ArgumentParser(description='Scan over basic grid area. Built for C4 Motor Controller.')
    sub = parser.add_subparsers(title='Choose which command to run.', help='Subparser help goes here.',
                                dest='subparser_name')

    area_scan = sub.add_parser('area_scan', help='Run a standard grid scan or specified size.')
    area_scan.add_argument('stuff', type=int, help='stuff help')
    area_scan.add_argument('other stuff', help='other stuff help')

    pos_move = sub.add_parser('pos_move', help='Move to specified position')
    pos_move.add_argument('b stuff', help='b stuff')
    pos_move.add_argument('b not stuff', help='b not stuff')

    extension = sub.add_parser('extension',
                               help='Run extensions on a data point. Must have already moved to that position.')
    extension.add_argument('level', choices=list(['1', '2']),
                           help='What level of extensions outward would you like to go?')

    reset_motors = sub.add_parser('reset_motors', help='Move motors back to their original positions')
    reset_motors.add_argument('wait', action='store_true', default=False,
                              help='Check this box to signify that you understand you are not allowed to touch '
                                   'anything while the motors are moving back to their home positions')

    #    area_scan.add_argument('X_distance', type=int, default=6 * 2.8, help='distance in the x direction')
    #    area_scan.add_argument('Y_distance', type=int, default=4 * 2.8, help='distance in the y direction')
    #    area_scan.add_argument('Motor_step_distance', type=float, default=2.8, help='distance to between grid points'
    #                                                                             ' (default=2.8cm)')
    #    reset_motors.add_argument('--reset', action='store_true', default=False, help='Reset motors to their home positions '
    #                                                                            'and exit (WARNING: PLEASE '
    #                                                                            'WAIT UNTIL MOTORS ARE HOMED BEFORE '
    #                                                                            'RUNNING PROGRAM AGAIN!)')
    #    parser.add_argument('--scan', action='store_true', default=False, help='perform scan action '
    #                                                                           '(can be disabled to test motors)')
    #    # parser.add_argument('--outfile_location', help='choose directory where data will be output', widget='DirChooser')

    args = parser.parse_args()
    print args
    if args.subparser_name == 'a':
        print 1
    if args.subparser_name == 'b':
        print 2

    # x_distance, y_distance, step_size, scan, reset = args.X_distance, args.Y_distance, args.Motor_step_distance, \
    #                                                 args.scan, args.reset
    # xpoints = int(x_distance / step_size) + 1
    # ypoints = int(y_distance / step_size) + 1
    # print xpoints, ypoints, step_size, scan, reset


if __name__ == '__main__':
    run_gui()
