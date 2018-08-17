"""
Manual Move GUI

This is the GUI module for manual motor control.

The GUI handles motor movements and step distance settings.

This module contains a single class:
    - ManualMoveGUI(wx.Frame): GUI interfaced with the MotorDriver class, provides manual control for users.

Authors:
Chang Hwan 'Oliver' Choi, Biomedical/Software Engineering Intern (Aug. 2018) - changhwan.choi@pctest.com
"""

from src.motor_driver import MotorDriver
import serial
import wx


class ManualMoveGUI(wx.Frame):
    """
    GUI interfaced with the MotorDriver class that allows manual control over the motors.
    """
    def __init__(self, parent, title, grid_step):
        """
        :param parent: Parent frame invoking the LocationSelectGUI.
        :param title: Title for the GUI window.
        :param grid_step: The grid step size.
        """
        wx.Frame.__init__(self, parent, title=title, size=(400, 400))

        # Variables
        try:
            self.motor = MotorDriver()
        except serial.SerialException:
            print("Error: Connection to C4 controller was not found")
            self.Close()
            return

        # self.narda = NardaNavigator()
        self.currx = 0.0
        self.curry = 0.0
        self.distx = grid_step
        self.disty = grid_step
        self.errx = 0.0
        self.erry = 0.0
        self.stepx = int(self.distx / self.motor.step_unit)
        self.stepy = int(self.disty / self.motor.step_unit)
        self.fracx = self.distx / self.motor.step_unit - self.stepx
        self.fracy = self.disty / self.motor.step_unit - self.stepy

        # UI Elements
        up_id = 301
        down_id = 302
        left_id = 303
        right_id = 304
        self.up_btn = wx.Button(self, up_id, "Up")
        self.down_btn = wx.Button(self, down_id, "Down")
        self.left_btn = wx.Button(self, left_id, "Left")
        self.right_btn = wx.Button(self, right_id, "Right")
        self.coord_box = wx.StaticText(self, label="Coordinates:\n[%.3f, %.3f]" % (self.currx, self.curry))

        self.x_text = wx.StaticText(self, label="X Step Distance (in cm)")
        self.x_tctrl = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.x_tctrl.SetValue(str(self.distx))
        self.y_text = wx.StaticText(self, label="Y Step Distance (in cm)")
        self.y_tctrl = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.y_tctrl.SetValue(str(self.disty))

        # Bindings/Shortcuts
        self.Bind(wx.EVT_KEY_UP, self.OnKey)  # Binding on "up" event to only register once
        self.Bind(wx.EVT_TEXT_ENTER, self.update_settings)
        self.Bind(wx.EVT_CHILD_FOCUS, self.update_settings)
        self.Bind(wx.EVT_BUTTON, self.move_up, self.up_btn)
        self.Bind(wx.EVT_BUTTON, self.move_down, self.down_btn)
        self.Bind(wx.EVT_BUTTON, self.move_left, self.left_btn)
        self.Bind(wx.EVT_BUTTON, self.move_right, self.right_btn)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Sizers/Layout, Static Lines, & Static Boxes
        self.mainh_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_stbox = wx.StaticBoxSizer(wx.VERTICAL, self, "Control Buttons")
        self.btn_sizer = wx.GridSizer(rows=3, cols=3, hgap=0, vgap=0)
        self.settings_stbox = wx.StaticBoxSizer(wx.VERTICAL, self, "Settings")

        self.btn_sizer.AddStretchSpacer(prop=1)
        self.btn_sizer.Add(self.up_btn, proportion=1, flag=wx.EXPAND)
        self.btn_sizer.AddStretchSpacer(prop=1)
        self.btn_sizer.Add(self.left_btn, proportion=1, flag=wx.EXPAND)
        self.btn_sizer.AddStretchSpacer(prop=1)
        self.btn_sizer.Add(self.right_btn, proportion=1, flag=wx.EXPAND)
        self.btn_sizer.AddStretchSpacer(prop=1)
        self.btn_sizer.Add(self.down_btn, proportion=1, flag=wx.EXPAND)
        self.btn_sizer.AddStretchSpacer(prop=1)

        self.btn_stbox.Add(self.btn_sizer, proportion=5, flag=wx.EXPAND)
        self.btn_stbox.Add(self.coord_box, proportion=1, flag=wx.EXPAND)

        self.settings_stbox.Add(self.x_text, proportion=0, flag=wx.EXPAND)
        self.settings_stbox.Add(self.x_tctrl, proportion=0, flag=wx.EXPAND)
        self.settings_stbox.Add(self.y_text, proportion=0, flag=wx.EXPAND)
        self.settings_stbox.Add(self.y_tctrl, proportion=0, flag=wx.EXPAND)

        self.mainh_sizer.Add(self.btn_stbox, proportion=5, flag=wx.EXPAND | wx.ALL, border=5)
        self.mainh_sizer.Add(self.settings_stbox, proportion=2, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizer(self.mainh_sizer)
        self.SetAutoLayout(True)
        self.mainh_sizer.Fit(self)
        self.Show(True)

    def move_up(self, e):
        """
        Moves the NS probe forward (i.e. negative X direction of the phone).

        :param e: Event handler.
        :return: Nothing.
        """
        self.curry -= self.disty
        self.erry -= self.fracy
        self.motor.reverse_motor_two(self.stepy + int(self.erry))
        self.erry -= int(self.erry)
        self.coord_box.SetLabel("Coordinates:\n[%.3f, %.3f]" % (self.currx, self.curry))

    def move_down(self, e):
        """
        Moves the NS probe backward (i.e. positive X direction of the phone).

        :param e: Event handler.
        :return: Nothing.
        """
        self.curry += self.disty
        self.erry += self.fracy
        self.motor.forward_motor_two(self.stepy + int(self.erry))
        self.erry -= int(self.erry)
        self.coord_box.SetLabel("Coordinates:\n[%.3f, %.3f]" % (self.currx, self.curry))

    def move_left(self, e):
        """
        Moves the NS probe leftward (i.e. negative Y direction of the phone).

        :param e: Event handler.
        :return: Nothing.
        """
        self.currx -= self.distx
        self.errx -= self.fracx
        self.motor.reverse_motor_one(self.stepx + int(self.errx))
        self.errx -= int(self.errx)
        self.coord_box.SetLabel("Coordinates:\n[%.3f, %.3f]" % (self.currx, self.curry))

    def move_right(self, e):
        """
        Moves the NS probe rightward (i.e. positive Y direction of the phone).

        :param e: Event handler.
        :return: Nothing.
        """
        self.currx += self.distx
        self.errx += self.fracx
        self.motor.forward_motor_one(self.stepx + int(self.errx))
        self.errx -= int(self.errx)
        self.coord_box.SetLabel("Coordinates:\n[%.3f, %.3f]" % (self.currx, self.curry))

    def OnKey(self, e):
        """
        Handles wx.EVT_KEY_UP events (releasing a pressed key) to allow keyboard controlled movement.
        Registers arrow keys for movement.

        :param e: Event handler.
        :return: Nothing.
        """
        if e.GetKeyCode() == wx.WXK_UP:
            self.move_up(None)
        elif e.GetKeyCode() == wx.WXK_DOWN:
            self.move_down(None)
        elif e.GetKeyCode() == wx.WXK_LEFT:
            self.move_left(None)
        elif e.GetKeyCode() == wx.WXK_RIGHT:
            self.move_right(None)
        else:
            e.Skip()

    def update_settings(self, e):
        """
        Handles automatic X and Y grid step distance edits. Called when [Enter] is pressed or when the user clicks
        on any element/widget of the GUI.

        :param e: Event handler.
        :return: Nothing.
        """
        try:
            xval = float(self.x_tctrl.GetValue())
            yval = float(self.y_tctrl.GetValue())
            if self.distx == xval and self.disty == yval:
                return
            self.distx = xval
            self.disty = yval
        except ValueError:
            print("Invalid distance values.\nPlease input numeric values.")
            self.x_tctrl = float(self.distx)
            self.y_tctrl = float(self.disty)
            return
        self.stepx = int(self.distx / self.motor.step_unit)
        self.stepy = int(self.disty / self.motor.step_unit)
        self.fracx = self.distx / self.motor.step_unit - self.stepx
        self.fracy = self.disty / self.motor.step_unit - self.stepy

        print("New step distances: X =", self.distx, "Y =", self.disty)

    def OnClose(self, e):
        """
        Exit script for the GUI, called when the window is closed. Notifies the user about exiting the manual movement
        module, destorys the motor object, and destroys the GUI object.

        :param e: Event handler.
        :return: Nothing.
        """
        print("Exiting Manual Movement module.")
        self.motor.destroy()
        self.Destroy()


if __name__ == "__main__":
    manual_move_gui = wx.App()
    fr = ManualMoveGUI(None, title="Manual Movement GUI")
    manual_move_gui.MainLoop()
