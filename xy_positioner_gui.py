"""
    Created by Chang Hwan 'Oliver' Choi on 08/09/2018
    changhwan.choi@pctest.com
"""
import os
import threading
from src.grid_scan_manual import run_scan, generate_grid, move_to_pos_one
from src.motor_driver import MotorDriver
from src.location_select_gui import LocationSelectGUI
from src.manual_gui_grid import ManualGridGUI
import numpy as np
import wx


class AreaScanPanel(wx.Panel):
    pass


class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800, 700))
        #wx.Window.SetMinSize(self, self.GetSize())

        # Variables
        # Instantiating variables with default parameters
        self.x_distance = 3 * 2.8  # Horizontal length of measurement region
        self.y_distance = 3 * 2.8  # Vertical length of measurement region
        self.grid_step_dist = 2.8  # Steps between each measurement point
        self.type = 'Limb'  # Type of measurement (Limb or Body)
        self.field = 'Electric'  # Type of field to measure (Electric, Magnetic A/B)
        self.side = 'Front'  # Side of phone being measured
        self.dwell_time = 1  # Time before measurement is taken (area scan)
        self.zoom_scan_dwell_time = 1.5  # Time before measurement is taken (zoom scan)
        self.save_dir = ''  # Where t
        self.auto_zoom = False

        # Accelerator Table/Shortcut Keys
        save_id = 115
        run_id = 116

        # UI Elements
        self.x_distance_text = wx.StaticText(self, label="X Distance")
        self.x_distance_text.SetFont(wx.Font(9, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.xdesc_text = wx.StaticText(self, label="Horizontal length of measurement region (in cm)")
        self.x_tctrl = wx.TextCtrl(self)
        self.x_tctrl.SetValue(str(2 * 2.8))

        self.y_distance_text = wx.StaticText(self, label="Y Distance")
        self.y_distance_text.SetFont(wx.Font(9, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.ydesc_text = wx.StaticText(self, label="Vertical length of measurement region (in cm)")
        self.y_tctrl = wx.TextCtrl(self)
        self.y_tctrl.SetValue(str(2 * 2.8))

        self.grid_step_dist_text = wx.StaticText(self, label="Grid Step Distance")
        self.grid_step_dist_text.SetFont(wx.Font(9, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.griddesc_text = wx.StaticText(self, label="Distance between measurement points (in cm)")
        self.grid_tctrl = wx.TextCtrl(self)
        self.grid_tctrl.SetValue(str(2.8))

        self.dwell_time_text = wx.StaticText(self, label="Pre-Measurement Dwell Time (in sec)")
        self.dwell_tctrl = wx.TextCtrl(self)
        self.dwell_tctrl.SetValue(str(1))
        self.zoom_scan_dwell_time_text = wx.StaticText(self, label="Pre-Measurement Dwell Time (in sec)")
        self.zdwell_tctrl = wx.TextCtrl(self)
        self.zdwell_tctrl.SetValue(str(1.5))

        self.save_dir_text = wx.StaticText(self, label="Save Directory")
        self.save_dir_text.SetFont(wx.Font(9, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.savedesc_text = wx.StaticText(self, label="Directory to save measurement text and image files")
        self.save_tctrl = wx.TextCtrl(self)
        self.save_btn = wx.Button(self, save_id, "Browse")
        self.Bind(wx.EVT_BUTTON, self.select_save_dir, self.save_btn)

        self.measurement_specs_text = wx.StaticText(self, label="Measurement Specifications")
        self.measurement_specs_text.SetFont(wx.Font(9, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.type_rbox = wx.RadioBox(self, label="Type", choices=['Limb', 'Body'],
                                     style=wx.RA_SPECIFY_COLS, majorDimension=1)
        self.field_rbox = wx.RadioBox(self, label="Field",
                                      choices=['Electric', 'Magnetic (Mode A)', 'Magnetic (Mode B)'],
                                      style=wx.RA_SPECIFY_COLS, majorDimension=1)
        self.side_rbox = wx.RadioBox(self, label="Side",
                                     choices=['Front', 'Back', 'Top', 'Bottom', 'Left', 'Right'],
                                     style=wx.RA_SPECIFY_COLS, majorDimension=1)

        self.run_btn = wx.Button(self, run_id, "Run")
        self.Bind(wx.EVT_BUTTON, self.run, self.run_btn)

        # Menu Bar

        # Sizers/Layout, Static Lines & Static Boxes
        self.saveline_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.text_input_sizer = wx.BoxSizer(wx.VERTICAL)
        self.radio_input_sizer = wx.BoxSizer(wx.VERTICAL)
        self.btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainh_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainv_sizer = wx.BoxSizer(wx.VERTICAL)

        self.text_input_sizer.Add(self.x_distance_text, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.xdesc_text, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.x_tctrl, proportion=0, flag=wx.LEFT | wx.EXPAND)
        self.text_input_sizer.Add(self.y_distance_text, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.ydesc_text, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.y_tctrl, proportion=0, flag=wx.LEFT | wx.EXPAND)
        self.text_input_sizer.Add(self.grid_step_dist_text, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.griddesc_text, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.grid_tctrl, proportion=0, flag=wx.LEFT | wx.EXPAND)
        self.text_input_sizer.Add(self.dwell_time_text, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.dwell_tctrl, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.zoom_scan_dwell_time_text, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.zdwell_tctrl, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.save_dir_text, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.savedesc_text, proportion=0, flag=wx.LEFT)
        self.saveline_sizer.Add(self.save_tctrl, proportion=1, flag=wx.LEFT | wx.EXPAND)
        self.saveline_sizer.Add(self.save_btn, proportion=0, flag=wx.ALIGN_RIGHT | wx.LEFT, border=5)
        self.text_input_sizer.Add(self.saveline_sizer, proportion=0, flag=wx.LEFT | wx.EXPAND)

        self.radio_input_sizer.Add(self.measurement_specs_text, proportion=0, flag=wx.LEFT)
        self.radio_input_sizer.Add(self.type_rbox, proportion=0, flag=wx.ALL | wx.EXPAND)
        self.radio_input_sizer.Add(self.field_rbox, proportion=0, flag=wx.ALL | wx.EXPAND)
        self.radio_input_sizer.Add(self.side_rbox, proportion=0, flag=wx.ALL | wx.EXPAND)

        self.mainh_sizer.Add(self.text_input_sizer, proportion=2, border=5, flag=wx.ALL | wx.EXPAND)
        self.mainh_sizer.Add(wx.StaticLine(self, wx.ID_ANY, style=wx.LI_VERTICAL), proportion=0, border=5,
                             flag=wx.TOP | wx.BOTTOM | wx.EXPAND)
        self.mainh_sizer.Add(self.radio_input_sizer, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)

        self.btn_sizer.Add(self.run_btn, proportion=1, border=5, flag=wx.ALIGN_RIGHT | wx.ALL)

        self.mainv_sizer.Add(self.mainh_sizer, proportion=1, border=0, flag=wx.ALL | wx.EXPAND)
        self.mainv_sizer.Add(wx.StaticLine(self, wx.ID_ANY, style=wx.LI_HORIZONTAL), proportion=0, border=0,
                             flag=wx.ALL | wx.EXPAND)
        self.mainv_sizer.Add(self.btn_sizer, proportion=0, border=5, flag=wx.ALIGN_RIGHT)

        self.Refresh()
        self.SetSizer(self.mainv_sizer)
        self.Refresh()
        self.SetAutoLayout(True)
        self.Refresh()
        self.mainv_sizer.Fit(self)
        self.Refresh()
        self.Show(True)
        self.Refresh()

    def select_save_dir(self, e):
        with wx.DirDialog(self, "Select save directory for '.txt' and '.png' files.",
                          style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            self.save_dir = dlg.GetPath()
            self.save_tctrl.SetValue(self.save_dir)
            #if os.path.exists(parentpath):
        pass

    def run(self, e):
        pass


if __name__ == "__main__":
    xy_positioner_gui = wx.App()
    fr = MainFrame(None, title='XY Positioner (for NS Testing)')
    xy_positioner_gui.MainLoop()
