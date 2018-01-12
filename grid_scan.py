import Tkinter as tk
import math
import serial
import time
import sys
import turtle
import random
from NARDA_control import read_data
import numpy as np
import motor_driver


def generate_grid(rows, columns):
    g = np.zeros((rows, columns))
    for i in range(rows):
        row = range(i * columns + 1, (i + 1) * columns + 1)
        if i % 2 != 0:
            row.reverse()
        g[i] = row
    return g


def run_scan(args):
    x_points = int(np.ceil(np.around(args.x_distance / args.grid_step_dist, decimals=3)))
    y_points = int(np.ceil(np.around(args.y_distance / args.grid_step_dist, decimals=3)))
    grid = generate_grid(y_points, x_points)
    print y_points, 'x', x_points, ':', grid
    m = motor_driver.MotorDriver()

