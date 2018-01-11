# Created by Ganesh Arvapalli on 1/2/18
#
# GUI for reading input from user regarding scan dimensions

from gooey import Gooey, GooeyParser
import Tkinter as tk
import math
import serial
import time
import sys
import turtle
import random
from NARDA_control import read_data
import numpy as np


# Home both motors to preset positions
def reset_motors(port):
    # Set home of motor 1 to be 6000 steps away, home of motor 2 to be 13000 steps away
    port.write(str.encode('!1wh1,r,10000\r'))
    port.readline()
    port.write(str.encode('!1wh2,r,13000\r'))
    port.readline()
    # print 'Home settings written (a if yes), ', port.readline()
    port.flush()

    # Home both motors
    motor_home = str.encode('!1h12\r')
    port.write(motor_home)
    # time.sleep(60)
    output = port.read(1000)
    while port.in_waiting:
        time.sleep(1)
        output += port.read(1000)
    # print 'Moving home: ', port.readline()
    port.flush()

    print 'Motors reset. Exit program and run again.'


@Gooey(program_name='NARDA Grid Scan', monospace_display=True, default_size=(600, 600))
def run_scan():
    parser = GooeyParser(description='Scan over basic grid area. Built for C4 Motor Controller.')

    parser.add_argument('X_Steps', type=int, default=6, help='number of grid points in the x direction')
    parser.add_argument('Y_Steps', type=int, default=4, help='number of grid points in the y direction')
    parser.add_argument('Motor_step_distance', type=float, default=2.8, help='distance to between grid points'
                                                                             ' (default=2.8cm)')
    parser.add_argument('--reset', action='store_true', default=False, help='Reset motors to their home positions '
                                                                            'and exit (WARNING: PLEASE '
                                                                            'WAIT UNTIL MOTORS ARE HOMED BEFORE '
                                                                            'RUNNING PROGRAM AGAIN!)')
    parser.add_argument('--scan', action='store_true', default=False, help='perform scan action '
                                                                           '(can be disabled to test motors)')
    parser.add_argument('--outfile_location', help='choose directory where data will be output', widget='DirChooser')
    args = parser.parse_args()
    xpoints, ypoints, step_size, scan, reset = args.X_Steps, args.Y_Steps, args.Motor_step_distance, \
                                                   args.scan, args.reset
    print xpoints, ypoints, step_size, scan, reset



    if reset:
        motors = serial.Serial('COM3', timeout=1.5)
        motors.flush()
        motors.flushInput()
        motors.flushOutput()
        reset_motors(motors)
        exit(0)

    names = []
    for i in range(ypoints):
        row = range(i * xpoints + 1, (i + 1) * xpoints + 1)
        if i % 2 != 0:
            row.reverse()
        names.append(row)
    flat_names = [i for sub in names for i in sub]  # Flatten array

    names = np.matrix(names)
    print np.argwhere(names == 3)

    root = tk.Tk()
    v = tk.IntVar()
    count = 1
    buttons = list()
    buttons = [[0 for x in range(xpoints)] for y in range(ypoints)]
    for i in range(ypoints):
        for j in range(xpoints):
            btn = tk.Radiobutton(root, text=flat_names[count - 1], variable=v, value=count)
            btn['indicatoron'] = 0  # display button instead of radiobutton
            btn['selectcolor'] = 'orange'  # color after selection

            btn.grid(row=i, column=j, sticky='new', ipadx=5, ipady=5)
            #buttons.append(btn)
            buttons[i][j] = btn
            count += 1
    root.configure(background="grey")
    root.grid_rowconfigure(xpoints, weight=1)
    root.grid_columnconfigure(ypoints, weight=1)

    # Calculate number of motor steps to move one grid unit
    # motor_diam = 0.635  # (in cm) Diameter of motor effector
    # motor_circumference = 2 * math.pi * motor_diam  # (in cm)
    # steps_per_revolution = 400  # (known from documentation)
    # pulley_modifier = 2.5
    # steps_per_revolution /= pulley_modifier
    # step_unit = motor_circumference / steps_per_revolution  # (in cm) Motor constant

    step_unit = 0.005 * 2.54 / 2.5  # inches * cm/in / pulley_reducer (inches known from documentation)

    num_steps = step_size / step_unit
    frac_step = num_steps - int(num_steps)
    print 'Number of motor steps between grid points: ', num_steps
    print 'Fraction lost per step: ', frac_step
    num_steps = int(num_steps)

    # Set up motors in their initial position
    motors = serial.Serial('COM3', timeout=1.5)
    motors.flush()
    motors.flushInput()
    motors.flushOutput()
    # reset_motors(motors)
    # hold = str.encode('!1wk1,10\r')
    buttons[0][0].configure(bg='blue')
    narda = serial.Serial('COM4', baudrate=38400, timeout=1)
    if scan:
        read_data(narda)
    narda.flush()
    buttons[0][0].configure(bg='green')
    # Each loop, add correction to steps and update fraction
    x_update = 0
    y_update = 0
    count = 1
    # Main traversal (motion is num_points - 1)
    turtle.colormode(255)
    turtle.penup()
    # v.set(flat_names[count - 1])
    turtle.setposition(-10*step_size*xpoints, 10*step_size*ypoints)
    # time.sleep(1)
    turtle.pendown()
    turtle.width(5)
    turtle.circle(5)
    going = True
    count = 2
    for j in range(ypoints):
        for i in range(xpoints - 1):
            oldIndex = np.argwhere(names == count-1)
            newIndex = np.argwhere(names == count)
            buttons[oldIndex[0][0]][oldIndex[0][1]].configure(bg='green')
            buttons[newIndex[0][0]][newIndex[0][1]].configure(bg='blue')
            #v.set(flat_names[count])
            count += 1
            if going:
                x_update += frac_step
                # print 'Error x (in mm):', step_unit * x_update * 10
                turtle.forward((num_steps+int(x_update))/10)
                motor1_forward = str.encode('!1m1r' + str(num_steps+int(x_update)) + 'n\r')
                motors.write(motor1_forward)
                motors.flush()
                motors.readline()
                if scan:
                    read_data(narda)
                    narda.flush()
                turtle.pencolor(random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
                turtle.circle(5)
                # time.sleep(1)
                x_update = x_update - int(x_update)
            if not going:
                x_update -= frac_step
                # print 'Error x (in mm):', step_unit * x_update * 10
                turtle.backward((num_steps+int(math.fabs(x_update)))/10)
                motor1_backward = str.encode('!1m1f' + str(num_steps+int(x_update)) + 'n\r')
                motors.write(motor1_backward)
                motors.flush()
                motors.readline()
                if scan:
                    read_data(narda)
                    narda.flush()
                turtle.pencolor(random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
                turtle.circle(5)
                # time.sleep(1)
                x_update = x_update - int(x_update)
        if count != len(flat_names):    # If we have not reached the end of our list of grid points, move to next row
            oldIndex = np.argwhere(names == count-1)
            newIndex = np.argwhere(names == count)
            buttons[oldIndex[0][0]][oldIndex[0][1]].configure(bg='green')
            buttons[newIndex[0][0]][newIndex[0][1]].configure(bg='blue')
            #v.set(flat_names[count])
            count += 1
            y_update += frac_step
            # print 'Error y (in mm):', step_unit * y_update * 10
            turtle.right(90)
            turtle.forward((num_steps+int(y_update))/10)
            motor2_forward = str.encode('!1m2r' + str(num_steps+int(y_update)) + 'n\r')
            motors.write(motor2_forward)
            motors.flush()
            if scan:
                read_data(narda)
                narda.flush()
            # time.sleep(1)
            turtle.pencolor(random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
            turtle.circle(5)
            turtle.left(90)
            # time.sleep(1)
            y_update = y_update - int(y_update)
            going = not going

    newIndex = np.argwhere(names == count-1)
    buttons[newIndex[0][0]][newIndex[0][1]].configure(bg='green')
   # buttons[flat_names[count-1]].configure(bg='green')
    motors.close()

    root.mainloop()


if __name__ == '__main__':
    run_scan()
