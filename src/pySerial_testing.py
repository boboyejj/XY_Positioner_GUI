# Created by Ganesh Arvapalli on 1/3/18
#
# Testing file for pySerial as an alternative to Visual Basic


import serial
import time


def main():
    ser = serial.Serial('COM3', timeout=2)
    # ser.write(b'!1h1\r')
    steps = 100
    steps_str = str(steps)
    motor1_home_set = str.encode('!1wh1,r,10000\r')
    motor2_home_set = str.encode('!1wh2,r,10000\r')
    motor_home = str.encode('!1h12\r')
    motor1_forward = str.encode('!1m1f'+steps_str+'n\r')
    motor1_backward = str.encode('!1m1r'+steps_str+'n\r')
    motor2_forward = str.encode('!1m2f'+steps_str+'n\r')
    motor2_backward = str.encode('!1m2r' + steps_str + 'n\r')
    hold = str.encode('!1wk1,10\r')
    # ser.write(str.encode('!1m1f'+step_size+'n'+'m1r'+step_size+'n\r'))
    # ser.flush()
    ser.flushInput()
    ser.flushOutput()

    command_list = list()
    command_list.append(motor1_home_set)
    command_list.append(motor2_home_set)
    command_list.append(motor_home)
    # command_list.append(hold)
    # command_list.append(motor1_home)
    # ser.write(motor2_home)
    ser.flush()
    command_list.append(motor1_forward)
    # command_list.append(hold)
    command_list.append(motor1_backward)
    # command_list.append(hold)
    command_list.append(motor2_forward)
    # command_list.append(hold)
    command_list.append(motor2_backward)
    # k = ser.write(str.encode('!1bawk1,10'))
    # time.sleep(1)
    # out = ser.readline()
    # out, k
    # ser.write(str.encode('!1bs'))
    for c in command_list:
        ser.write(c)
        ser.flush()
        out = ser.readline()
        print command_list.index(c), out
        # if 'o' in out:
        #    continue
        # else:
        #   break
    ser.close()


if __name__ == "__main__":
    main()
