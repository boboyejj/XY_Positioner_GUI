"""
Motor Driver

This module contains scripts for initializing, communicating with, and controlling the C4 motor controller from
Arrick Robotics.

The module contains the following classes:
    - ResetThread(threading.Thread): performs motor resets.
    - MotorDriver(): establishes connection with the C4 controller and contains all motor movement functions.

Authors:
Ganesh Arvapalli, Software Engineering Intern (Jan. 2018) - ganesh.arvapalli@pctest.com
Chang Hwan 'Oliver' Choi, Biomedical/Software Engineering Intern (Aug. 2018) - changhwan.choi@pctest.com

"""

import serial
import threading
import wx


class ResetThread(threading.Thread):
    """
    Thread for handling resetting the motors. NS probe is moved back to its 'home' position.
    """
    def __init__(self, parent):
        """
        :param parent: Parent frame invoking the LocationSelectGUI.
        """
        self.parent = parent
        self.motor = None  # Placeholder variable for the motor
        super(ResetThread, self).__init__()

    def run(self):
        """
        Script run on thread start. Resets the NS probe position to its home coordinates on a separate thread.

        :return: Nothing.
        """
        # Variables
        try:
            self.motor = MotorDriver()
            self.motor.home_motors()
            self.motor.destroy()
        except serial.SerialException:
            print("Error: Connection to C4 controller was not found")
            return
        with wx.MessageDialog(self.parent, "Motor resetting completed.",
                              style=wx.OK | wx.ICON_INFORMATION | wx.CENTER) as dlg:
            dlg.ShowModal()
        wx.CallAfter(self.parent.enablegui)


class MotorDriver:
    """
    Attempts to open serial port to control two MD2 stepper motors.
    Automatically flushes input and output.

        Attributes:
            port: Serial port through which motors are controlled
            step_unit: Size of individual motor step (consult manual)
    """

    def __init__(self, step_unit_=0.00508, home=(3788, 4300)):
        """
        :param step_unit_: Size of individual motor step (consult C4 controller manual for more details).
        :param home: Home/Reset coordinates for the motors. NS probe returns to these coordinates.
        """
        self.home = home
        entered = False
        for i in range(256):
            try:
                self.port = serial.Serial('COM'+str(i), timeout=1.5)
                self.port.write('!1fp\r'.encode())  # Check if we have connected to the right COM Port/machine
                received_str = self.port.read(2)
                if received_str.decode() == "C4":
                    print("Established connection with motor controller (PORT %d)" % i)
                    self.port.flushOutput()
                    self.port.flushInput()
                    self.port.flush()
                    self.step_unit = step_unit_
                    entered = True
                    break
            except serial.SerialException as e:
                pass
                # print e.message
        if not entered:
            raise serial.SerialException

    def forward_motor_one(self, steps):
        """
        Move motor 1 forward the specified number of steps. Blocks thread until a 'Completed' acknowledgment signal
        is received.

        :param steps: Number of steps to move the stepper motor by.
        :return: Nothing.
        """
        self.port.flushInput()
        self.port.flushOutput()
        self.port.flush()
        self.port.write(('!1m1r' + str(steps) + 'n\r').encode())
        while self.port.read().decode() != 'o':
            pass
        self.port.flush()

    def reverse_motor_one(self, steps):
        """
        Move motor 1 backward the specified number of steps. Blocks thread until a 'Completed' acknowledgment signal
        is received.

        :param steps: Number of steps to move the stepper motor by.
        :return: Nothing.
        """
        self.port.flushInput()
        self.port.flushOutput()
        self.port.flush()
        self.port.write(('!1m1f' + str(steps) + 'n\r').encode())
        while self.port.read().decode() != 'o':
            pass
        self.port.flush()

    def forward_motor_two(self, steps):
        """
        Move motor 2 forward the specified number of steps. Blocks thread until a 'Complete' acknowledgment signal
        is received.

        :param steps: Number of steps to move the stepper motor by.
        :return: Nothing.
        """
        self.port.flushInput()
        self.port.flushOutput()
        self.port.flush()
        self.port.write(('!1m2r' + str(steps) + 'n\r').encode())
        while self.port.read().decode() != 'o':
            pass
        self.port.flush()

    def reverse_motor_two(self, steps):
        """
        Move motor 2 backward the specified number of steps. Blocks thread until a 'Complete' acknowledgment signal
        is received.

        :param steps: Number of steps to move the stepper motor by.
        :return: Nothing.
        """
        self.port.flushInput()
        self.port.flushOutput()
        self.port.flush()
        self.port.write(('!1m2f' + str(steps) + 'n\r').encode())
        while self.port.read().decode() != 'o':
            pass
        self.port.flush()

    # Home both motors to preset positions
    def home_motors(self):
        """
        Resets the NS probe position to its home coordinates. Blocks thread until the motors have fully reset.
        :return: Nothing.
        """
        # Set home of motor 1 to be 6000 steps away, home of motor 2 to be 13000 steps away
        self.port.write(str.encode('!1wh1,r,'+str(self.home[0])+'\r'))
        self.port.readline()
        self.port.write(str.encode('!1wh2,r,'+str(self.home[1])+'\r'))
        self.port.readline()
        # print 'Home settings written (a if yes), ', port.readline()
        self.port.flush()

        # Home both motors
        motor_home = str.encode('!1h12\r')
        self.port.write(motor_home)
        while self.port.read().decode() != 'o':
            pass
        print("Motor 1 reset.")
        while self.port.read().decode() != 'o':
            pass
        print("Motor 2 reset.")
        self.port.flush()
        print("Motors reset successfully.")

    def set_start_point(self, offset=(3788, 4300)):
        """
        Set the NS probe position to a starting point.

        :param offset: number of steps from the home coordinates.
        :return: Nothing
        """
        self.port.write(str.encode('!1wh1,r,' + str(offset[0]) + '\r'))
        self.port.readline()
        self.port.write(str.encode('!1wh2,r,' + str(offset[1]) + '\r'))
        self.port.readline()
        # print 'Home settings written (a if yes), ', port.readline()
        self.port.flush()

        # Home both motors
        motor_start = str.encode('!1h12\r')
        self.port.write(motor_start)
        while self.port.read().decode() != 'o':
            pass
        print("Motor 1 reset.")
        while self.port.read().decode() != 'o':
            pass
        print("Motor 2 reset.")
        self.port.flush()
        print("Motors set to the start point successfully.")

    def destroy(self):
        """
        Flush remaining data and close port.

        :return: Nothing.
        """
        self.port.flush()
        self.port.flushInput()
        self.port.flushOutput()
        self.port.close()
