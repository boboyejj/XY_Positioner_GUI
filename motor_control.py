# Created by Ganesh Arvapalli on 1/2/18
#
# GUI for reading input from user regarding scan dimensions

import math
import serial
import time
import sys
import turtle
import random
from NARDA_control import read_data


def main(xpoints, ypoints, step_size):
    names = []
    for i in range(ypoints):
        row = range(i * xpoints + 1, (i + 1) * xpoints + 1)
        if i % 2 != 0:
            row.reverse()
        names.append(row)
    flat_names = [i for sub in names for i in sub]  # Flatten array

    # root = tk.Tk()
    # v = tk.IntVar()
    # count = 1
    # for i in range(ypoints):
    #     for j in range(xpoints):
    #         btn = tk.Radiobutton(root, text=flat_names[count - 1], variable=v, value=count)
    #         btn['indicatoron'] = 0  # display button instead of radiobutton
    #         btn['selectcolor'] = 'orange'  # color after selection
    #
    #         btn.grid(row=i, column=j, sticky='new', ipadx=5, ipady=5)
    #         count += 1
    # root.configure(background="grey")
    # root.grid_rowconfigure(xpoints, weight=1)
    # root.grid_columnconfigure(ypoints, weight=1)

    # Calculate number of motor steps to move one grid unit
    motor_diam = 0.635  # (in cm) Diameter of motor effector
    motor_circumference = 2 * math.pi * motor_diam  # (in cm)
    steps_per_revolution = 400  # (known from documentation)
    pulley_modifier = 2.5
    steps_per_revolution /= pulley_modifier
    step_unit = motor_circumference / steps_per_revolution  # (in cm) Motor constant

    num_steps = step_size / step_unit
    frac_step = num_steps - int(num_steps)
    print 'Number of motor steps between grid points: ', num_steps
    print 'Fraction lost per step: ', frac_step
    num_steps = int(num_steps)

    motors = serial.Serial('COM3', timeout=1.5)
    motors.flushInput()
    motors.flushOutput()
    motors.flush()
    motors.write(str.encode('!1wh1,r,10000'))
    print motors.readline()
    motors.write(str.encode('!1wh2,r,10000'))
    print motors.readline()
    motor_home = str.encode('!1h12')
    motors.write(motor_home)
    print motors.readline()
    motors.flush()
    hold = str.encode('!1wk1,10\r')
    # motors.close()
    # exit(0)

    # Each loop, add correction to steps and update fraction
    x_update = 0
    y_update = 0
    count = 1
    # Main traversal (motion is num_points - 1)
    # turtle.colormode(255)
    # turtle.penup()
    # # v.set(flat_names[count - 1])
    # # turtle.setposition(-step_size*xpoints, step_size*ypoints)
    # # time.sleep(1)
    # turtle.pendown()
    # turtle.width(5)
    # turtle.circle(5)
    going = True
    for j in range(ypoints):
        for i in range(xpoints - 1):
            # v.set(flat_names[count])
            count += 1
            if going:
                x_update += frac_step
                print 'Error x (in mm):', step_unit*(x_update)*10
                # print 'forward', int(x_update)  # motor1_forward
                #turtle.forward((num_steps+int(x_update))/5)
                motor1_forward = str.encode('!1m1r' + str(num_steps+int(x_update)) + 'n\r')
                motors.write(motor1_forward)
                motors.flush()
                motors.readline()
                # turtle.pencolor(random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
                # turtle.circle(5)
                # time.sleep(1)
                x_update = x_update - int(x_update)
            if not going:
                x_update -= frac_step
                print 'Error x (in mm):', step_unit * (x_update)*10
                # print 'backward', int(math.fabs(x_update))  # motor1_backward
                # turtle.backward((num_steps+int(math.fabs(x_update)))/5)
                motor1_backward = str.encode('!1m1f' + str(num_steps+int(x_update)) + 'n\r')
                motors.write(motor1_backward)
                motors.flush()
                motors.readline()
                # turtle.pencolor(random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
                # turtle.circle(5)
                # time.sleep(1)
                x_update = x_update - int(x_update)
        if count != len(flat_names):    # If we have not reached the end of our list of grid points, move to next row
            # v.set(flat_names[count])
            count += 1
            y_update += frac_step
            print 'Error y (in mm):', step_unit * (y_update)*10
            # print 'change lanes', int(y_update)  # motor2_forward
            # turtle.right(90)
            # turtle.forward((num_steps+int(y_update))/5)
            motor2_forward = str.encode('!1m2r' + str(num_steps+int(y_update)) + 'n\r')
            motors.write(motor2_forward)
            motors.flush()
            time.sleep(1)
            # turtle.pencolor(random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
            # turtle.circle(5)
            # turtle.left(90)
            # time.sleep(1)
            y_update = y_update - int(y_update)
            going = not going

    motors.close()

    # pathos = os.path.join('C:\Users\ganesh.arvapalli\Documents\C4MotorControl', 'testMoveMotor1Fwd.vbs')
    # os.system(pathos)
    # root.mainloop()


def reset_motors(port):
    # Set home of motor 1 to be 6000 steps away, home of motor 2 to be 13000 steps away
    port.write(str.encode('!1wh1,r,6000wh2,r,13000\r'))
    print 'Home settings written (a if yes), ', port.readline()
    port.flush()

    # Home both motors simultaneously
    motor_home = str.encode('!1h12\r')
    port.write(motor_home)
    print 'Moving home: ', port.readline()
    port.flush()

    print 'Motors successfully reset'


if __name__ == '__main__':
    motors_port = serial.Serial('COM3', timeout=2)
    motors_port.flush()
    motors_port.flushInput()
    motors_port.flushOutput()
    reset_motors(motors_port)
    # exit(0)
    # main(3, 3, 2.8)
