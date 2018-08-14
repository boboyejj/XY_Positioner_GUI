import threading
import wx
import serial
from src.motor_driver import MotorDriver


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
