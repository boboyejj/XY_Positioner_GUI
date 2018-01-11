# Class for controlling motors using serial port communication

import serial
import time


class MotorDriver:
    def __init__(self, step_unit_=0.00508, port_=serial.Serial('COM3', timeout=1.5)):
        self.port = port_
        self.port.flushOutput()
        self.port.flushInput()
        self.port.flush()
        self.step_unit = step_unit_

    def forward_motor_one(self, steps):
        self.port.flushInput()
        self.port.flushOutput()
        self.port.flush()
        self.port.write('!1m1r' + str(steps) + 'n\r')
        out = self.port.readline()
        self.port.flush()
        return out

    def reverse_motor_one(self, steps):
        self.port.flushInput()
        self.port.flushOutput()
        self.port.flush()
        self.port.write('!1m1f' + str(steps) + 'n\r')
        out = self.port.readline()
        self.port.flush()
        return out

    def forward_motor_two(self, steps):
        self.port.flushInput()
        self.port.flushOutput()
        self.port.flush()
        self.port.write('!1m2r' + str(steps) + 'n\r')
        out = self.port.readline()
        self.port.flush()
        return out

    def reverse_motor_two(self, steps):
        self.port.flushInput()
        self.port.flushOutput()
        self.port.flush()
        self.port.write('!1m2f' + str(steps) + 'n\r')
        out = self.port.readline()
        self.port.flush()
        return out

    # Home both motors to preset positions
    def reset_motors(self):
        # Set home of motor 1 to be 6000 steps away, home of motor 2 to be 13000 steps away
        self.port.write(str.encode('!1wh1,r,10000\r'))
        self.port.readline()
        self.port.write(str.encode('!1wh2,r,13000\r'))
        self.port.readline()
        # print 'Home settings written (a if yes), ', port.readline()
        self.port.flush()

        # Home both motors
        motor_home = str.encode('!1h12\r')
        self.port.write(motor_home)
        # time.sleep(60)
        output = self.port.read(1000)
        while self.port.in_waiting:
            time.sleep(1)
            output += self.port.read(1000)
        # print 'Moving home: ', port.readline()
        self.port.flush()

        print 'Motors reset. Exit program and run again.'