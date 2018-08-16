"""
    Created by Ganesh Arvapalli on 1/12/18
    ganesh.arvapalli@pctest.com
"""

import serial
import time
import threading
import wx


class ResetThread(threading.Thread):
    def __init__(self, parent):
        self.parent = parent
        self.motor = None  # Placeholder variable for the motor
        super(ResetThread, self).__init__()

    def run(self):
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
    """Attempts to open serial port to control two MD2 stepper motors.

        Automatically flushes input and output

        Attributes:
            port: Serial port through which motors are controlled
            step_unit: Size of individual motor step (consult manual)
    """

    def __init__(self, step_unit_=0.00508, home=(3788, 4300)):
        """Init MotorDriver with step_unit and port = COM #, # = 1,2,3..."""
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
            exit(1)

    def forward_motor_one(self, steps):
        """Move motor 1 forward the specified number of steps."""
        self.port.flushInput()
        self.port.flushOutput()
        self.port.flush()
        self.port.write(('!1m1r' + str(steps) + 'n\r').encode())
        while self.port.read().decode() != 'o':
            pass
        self.port.flush()

    def reverse_motor_one(self, steps):
        """Move motor 1 backward the specified number of steps."""
        self.port.flushInput()
        self.port.flushOutput()
        self.port.flush()
        self.port.write(('!1m1f' + str(steps) + 'n\r').encode())
        while self.port.read().decode() != 'o':
            pass
        self.port.flush()

    def forward_motor_two(self, steps):
        """Move motor 2 forward the specified number of steps."""
        self.port.flushInput()
        self.port.flushOutput()
        self.port.flush()
        self.port.write(('!1m2r' + str(steps) + 'n\r').encode())
        while self.port.read().decode() != 'o':
            pass
        self.port.flush()

    def reverse_motor_two(self, steps):
        """Move motor 2 backward the specified number of steps."""
        self.port.flushInput()
        self.port.flushOutput()
        self.port.flush()
        self.port.write(('!1m2f' + str(steps) + 'n\r').encode())
        while self.port.read().decode() != 'o':
            pass
        self.port.flush()

    # Home both motors to preset positions
    def home_motors(self):
        """Reset motors back to center of grid."""
        # Set home of motor 1 to be 6000 steps away, home of motor 2 to be 13000 steps away
        self.port.write(str.encode('!1wh1,r,'+str(self.home[0])+'\r'))
        self.port.readline()
        #while self.port.read().decode() != 'o':
        #    pass
        self.port.write(str.encode('!1wh2,r,'+str(self.home[1])+'\r'))
        self.port.readline()
        #while self.port.read().decode() != 'o':
        #    pass
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

    def destroy(self):
        """Flush remaining data and close port."""
        self.port.flush()
        self.port.flushInput()
        self.port.flushOutput()
        self.port.close()
