
import wx
import serial
from src.narda_navigator import NardaNavigator
from src.motor_driver import MotorDriver


class ManualMoveGUI(wx.Frame):
    def __init__(self, parent, title):
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
        self.distx = 2.8
        self.disty = 2.8
        self.errx = 0.0
        self.erry = 0.0
        self.stepx = int(self.distx / self.motor.step_unit)
        self.stepy = int(self.disty / self.motor.step_unit)
        self.fracx = self.distx / self.motor.step_unit - self.stepx
        self.fracy = self.disty / self.motor.step_unit - self.stepy

        # Accelerator Table/Shortcut Keys
        up_id = 301
        down_id = 302
        left_id = 303
        right_id = 304
        self.Bind(wx.EVT_KEY_UP, self.OnKey)  # Binding on "up" event to only register once

        # UI Elements
        self.up_btn = wx.Button(self, up_id, "Up")
        self.down_btn = wx.Button(self, down_id, "Down")
        self.left_btn = wx.Button(self, left_id, "Left")
        self.right_btn = wx.Button(self, right_id, "Right")
        self.coord_box = wx.StaticText(self, label="Coordinates:\n[%.3f, %.3f]" % (self.currx, self.curry))

        # Bindings
        self.Bind(wx.EVT_BUTTON, self.move_up, self.up_btn)
        self.Bind(wx.EVT_BUTTON, self.move_down, self.down_btn)
        self.Bind(wx.EVT_BUTTON, self.move_left, self.left_btn)
        self.Bind(wx.EVT_BUTTON, self.move_right, self.right_btn)

        # Sizers/Layout, Static Lines, & Static Boxes
        self.mainh_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_stbox = wx.StaticBoxSizer(wx.VERTICAL, self, "Control Buttons")
        self.btn_sizer = wx.GridSizer(rows=3, cols=3, hgap=0, vgap=0)

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

        self.mainh_sizer.Add(self.btn_stbox, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizer(self.mainh_sizer)
        self.SetAutoLayout(True)
        self.mainh_sizer.Fit(self)
        self.Show(True)

    def move_up(self, e):
        self.curry -= self.stepy
        self.erry -= self.fracy
        self.motor.reverse_motor_two(self.stepy + int(self.erry))
        self.erry -= int(self.erry)
        self.coord_box.SetLabel("Coordinates:\n[%.3f, %.3f]" % (self.currx, self.curry))
        print(self.curry)

    def move_down(self, e):
        self.curry += self.stepy
        self.erry += self.fracy
        self.motor.forward_motor_two(self.stepy + int(self.erry))
        self.erry -= int(self.erry)
        self.coord_box.SetLabel("Coordinates:\n[%.3f, %.3f]" % (self.currx, self.curry))
        print(self.curry)

    def move_left(self, e):
        self.currx -= self.stepx
        self.errx -= self.fracx
        self.motor.reverse_motor_one(self.stepx + int(self.errx))
        self.errx -= int(self.errx)
        self.coord_box.SetLabel("Coordinates:\n[%.3f, %.3f]" % (self.currx, self.curry))
        print(self.currx)

    def move_right(self, e):
        self.currx += self.stepx
        self.errx += self.fracx
        self.motor.forward_motor_one(self.stepx + int(self.errx))
        self.errx -= int(self.errx)
        self.coord_box.SetLabel("Coordinates:\n[%.3f, %.3f]" % (self.currx, self.curry))
        print(self.currx)

    def OnKey(self, e):
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

    def OnClose(self, e):
        print("Closing")
        self.motor.destroy()
        self.Destroy()


if __name__ == "__main__":
    manual_move_gui = wx.App()
    fr = ManualMoveGUI(None, title="Manual Movement GUI")
    manual_move_gui.MainLoop()
