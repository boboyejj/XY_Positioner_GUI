"""
    Created by Chang Hwan 'Oliver' Choi on 08/09/2018
    changhwan.choi@pctest.com
"""
import os
import sys
from src.area_scan import AreaScanThread, ZoomScanThread, CorrectionThread
from src.post_scan_gui import PostScanGUI
from src.location_select_gui import LocationSelectGUI
from src.manual_move import ManualMoveGUI
from src.console_gui import TextRedirecter, ConsoleGUI
from src.reset_motors import ResetThread
import numpy as np
import matplotlib.pyplot as plt
import wx
from wx.lib.agw import multidirdialog as mdd


class AreaScanPanel(wx.Panel):
    pass


class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800, 700))
        #wx.Window.SetMinSize(self, self.GetSize())

        # Variables
        self.run_thread = None
        self.zoom_thread = None
        self.corr_thread = None
        self.console_frame = None

        self.curr_row = 0  # Grid coordinate row
        self.curr_col = 0  # Grid coordinate col
        self.values = None  # np.array storing area scan values
        self.zoom_values = None  # np.array storing zoom scan values
        self.grid = None  # np.array storing 'trajectory' of scans

        # Accelerator Table/Shortcut Keys
        save_id = 115
        run_id = 116
        manual_id = 117
        reset_id = 118

        # UI Elements
        self.x_distance_text = wx.StaticText(self, label="X Distance")
        self.x_distance_text.SetFont(wx.Font(9, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.xdesc_text = wx.StaticText(self, label="Horizontal length of measurement region (in cm)")
        self.x_tctrl = wx.TextCtrl(self)
        self.x_tctrl.SetValue(str(1 * 2.8))

        self.y_distance_text = wx.StaticText(self, label="Y Distance")
        self.y_distance_text.SetFont(wx.Font(9, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.ydesc_text = wx.StaticText(self, label="Vertical length of measurement region (in cm)")
        self.y_tctrl = wx.TextCtrl(self)
        self.y_tctrl.SetValue(str(1 * 2.8))

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
        self.save_tctrl.SetValue("C:\\Users\changhwan.choi\Desktop\henlo")  # TODO :Debugging
        self.save_btn = wx.Button(self, save_id, "Browse")
        self.Bind(wx.EVT_BUTTON, self.select_save_dir, self.save_btn)

        self.auto_checkbox = wx.CheckBox(self, label="Automatic Measurements")  # TODO: may not use
        self.auto_checkbox.SetValue(True)

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

        self.reset_btn = wx.Button(self, reset_id, "Reset Motors")
        self.Bind(wx.EVT_BUTTON, self.reset_motors, self.reset_btn)
        self.manual_btn = wx.Button(self, manual_id, "Manual Movement")
        self.Bind(wx.EVT_BUTTON, self.manual_move, self.manual_btn)
        self.run_btn = wx.Button(self, run_id, "Run")
        self.Bind(wx.EVT_BUTTON, self.run_area_scan, self.run_btn)

        # Menu Bar

        # Sizers/Layout, Static Lines, & Static Boxes
        self.saveline_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.checkbox_sizer = wx.BoxSizer(wx.HORIZONTAL)
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
        self.checkbox_sizer.Add(self.auto_checkbox, proportion=0, flag=wx.ALIGN_LEFT | wx.ALL, border=5)
        self.text_input_sizer.Add(self.saveline_sizer, proportion=0, flag=wx.LEFT | wx.EXPAND)
        self.text_input_sizer.Add(self.checkbox_sizer, proportion=0, flag=wx.LEFT | wx.EXPAND)

        self.radio_input_sizer.Add(self.measurement_specs_text, proportion=0, flag=wx.LEFT)
        self.radio_input_sizer.Add(self.type_rbox, proportion=0, flag=wx.ALL | wx.EXPAND)
        self.radio_input_sizer.Add(self.field_rbox, proportion=0, flag=wx.ALL | wx.EXPAND)
        self.radio_input_sizer.Add(self.side_rbox, proportion=0, flag=wx.ALL | wx.EXPAND)

        self.mainh_sizer.Add(self.text_input_sizer, proportion=2, border=5, flag=wx.ALL | wx.EXPAND)
        self.mainh_sizer.Add(wx.StaticLine(self, wx.ID_ANY, style=wx.LI_VERTICAL), proportion=0, border=5,
                             flag=wx.TOP | wx.BOTTOM | wx.EXPAND)
        self.mainh_sizer.Add(self.radio_input_sizer, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)

        self.btn_sizer.Add(self.reset_btn, proportion=1, border=5,
                           flag=wx.ALIGN_RIGHT | wx.LEFT | wx.TOP | wx.BOTTOM)
        self.btn_sizer.Add(self.manual_btn, proportion=1, border=5,
                           flag=wx.ALIGN_RIGHT | wx.LEFT | wx. TOP | wx.BOTTOM)
        self.btn_sizer.Add(self.run_btn, proportion=1, border=5, flag=wx.ALIGN_RIGHT | wx.ALL)

        self.mainv_sizer.Add(self.mainh_sizer, proportion=1, border=0, flag=wx.ALL | wx.EXPAND)
        self.mainv_sizer.Add(wx.StaticLine(self, wx.ID_ANY, style=wx.LI_HORIZONTAL), proportion=0, border=0,
                             flag=wx.ALL | wx.EXPAND)
        self.mainv_sizer.Add(self.btn_sizer, proportion=0, border=5, flag=wx.ALIGN_RIGHT)

        self.SetSizer(self.mainv_sizer)
        self.SetAutoLayout(True)
        self.mainv_sizer.Fit(self)
        self.Show(True)

    def select_save_dir(self, e):
        # TODO: Currently, there is a problem with wx.DirDialog, so I have resorted to using multidirdialog
        # TODO: When the bugs are fixed on their end, revert back to the nicer looking wx.DirDialog
        with mdd.MultiDirDialog(None, "Select save directory for output files.",
                                style=mdd.DD_DIR_MUST_EXIST | mdd.DD_NEW_DIR_BUTTON) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            # Correcting name format to fit future save functions
            path = dlg.GetPaths()[0]
            path = path.split(':')[0][-1] + ':' + path.split(':)')[1]
            self.save_tctrl.SetValue(path)
        #with wx.DirDialog(self, "Select save directory for '.txt' and '.png' files.",
        #                  style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) as dlg:
        #    if dlg.ShowModal() == wx.ID_CANCEL:
        #        return
        #    self.save_dir = dlg.GetPath()
        #    self.save_tctrl.SetValue(self.save_dir)
            #if os.path.exists(parentpath):

    def run_area_scan(self, e):
        if self.save_tctrl.GetValue() is None or self.save_tctrl.GetValue() is '':
            self.errormsg("Please select a save directory for the output files.")
            return
        try:
            x = float(self.x_tctrl.GetValue())
            y = float(self.y_tctrl.GetValue())
            step = float(self.grid_tctrl.GetValue())
            dwell = float(self.dwell_tctrl.GetValue())
        except ValueError:
            self.errormsg("Invalid scan parameters.\nPlease input numerical values only.")
            return
        savedir = self.save_tctrl.GetValue()
        # Finding the measurement type
        meas_type = self.type_rbox.GetString(self.type_rbox.GetSelection())
        # Finding the measurement field
        meas_field = self.field_rbox.GetString(self.field_rbox.GetSelection())
        # Finding the measurement side
        meas_side = self.side_rbox.GetString(self.side_rbox.GetSelection())
        self.run_thread = AreaScanThread(self, x, y, step, dwell, savedir,
                                         meas_type, meas_field, meas_side)
        self.disablegui()
        if not self.console_frame:
            self.console_frame = ConsoleGUI(self, "Console")
        self.console_frame.Show(True)
        sys.stdout = TextRedirecter(self.console_frame.console_tctrl)  # Redirect text from stdout to the console
        sys.stderr = TextRedirecter(self.console_frame.console_tctrl)  # Redirect text from stderr to the console
        print("Running thread...")
        self.run_thread.start()

    def run_post_scan(self):
        # Plot the scan
        plt.close()
        plt.imshow(self.values, interpolation='bilinear')
        plt.title('Area Scan Heat Map')
        cbar = plt.colorbar()
        cbar.set_label('Signal Level')
        plt.show(block=False)

        # Post Scan GUI - User selects which option to proceed with
        with PostScanGUI(self, title="Post Scan Options", style=wx.DEFAULT_DIALOG_STYLE | wx.OK) as post_dlg:
            if post_dlg.ShowModal() == wx.ID_OK:
                choice = post_dlg.option_rbox.GetStringSelection()
                print("Choice: ", choice)
            else:
                print("No option selected - Area Scan Complete.")
                self.enablegui()
                return

        if choice == 'Zoom Scan':
            try:
                zdwell = float(self.zdwell_tctrl.GetValue())
            except ValueError:
                self.errormsg("Invalid scan parameters.\nPlease input numerical values only.")
                return
            savedir = self.save_tctrl.GetValue()
            # Finding the measurement type
            meas_type = self.type_rbox.GetString(self.type_rbox.GetSelection())
            # Finding the measurement field
            meas_field = self.field_rbox.GetString(self.field_rbox.GetSelection())
            # Finding the measurement side
            meas_side = self.side_rbox.GetString(self.side_rbox.GetSelection())
            self.zoom_thread = ZoomScanThread(self, zdwell, savedir, meas_type, meas_field, meas_side,
                                              self.run_thread.num_steps, self.values, self.grid,
                                              self.curr_row, self.curr_col)
            if not self.console_frame:
                self.console_frame = ConsoleGUI(self, "Console")
            self.console_frame.Show(True)
            sys.stdout = TextRedirecter(self.console_frame.console_tctrl)  # Redirect text from stdout to the console
            sys.stderr = TextRedirecter(self.console_frame.console_tctrl)  # Redirect text from stderr to the console
            self.zoom_thread.start()

        elif choice == 'Correct Previous Value':
            loc_gui = LocationSelectGUI(self, "Location Selection", self.grid)
            loc_gui.Show(True)
        elif choice == 'Save Data':
            pass
        elif choice == 'Exit':
            print("Area Scan Complete. Exiting module.")
            self.enablegui()

    def update_values(self, call_thread):
        self.curr_row = call_thread.curr_row
        self.curr_col = call_thread.curr_col
        if type(call_thread) is AreaScanThread:
            self.values = call_thread.values
            self.grid = call_thread.grid
        elif type(call_thread) is CorrectionThread:
            self.values = call_thread.values
        elif type(call_thread) is ZoomScanThread:
            self.zoom_values = call_thread.zoom_values

    def run_correction(self, val):
        self.corr_thread = CorrectionThread(self, val, self.run_thread.num_steps,
                                            self.values, self.grid, self.curr_row, self.curr_col)
        if not self.console_frame:
            self.console_frame = ConsoleGUI(self, "Console")
        self.console_frame.Show(True)
        sys.stdout = TextRedirecter(self.console_frame.console_tctrl)  # Redirect text from stdout to the console
        sys.stderr = TextRedirecter(self.console_frame.console_tctrl)  # Redirect text from stderr to the console
        self.corr_thread.start()

    def manual_move(self, e):
        if not self.console_frame:
            self.console_frame = ConsoleGUI(self, "Console")
        self.console_frame.Show(True)
        sys.stdout = TextRedirecter(self.console_frame.console_tctrl)  # Redirect text from stdout to the console
        sys.stderr = TextRedirecter(self.console_frame.console_tctrl)  # Redirect text from stderr to the console
        try:
            step = float(self.grid_tctrl.GetValue())
        except ValueError:
            self.errormsg("Invalid scan parameters.\nPlease input numerical values only.")
            return
        manual = ManualMoveGUI(self, "Manual Movement", step)
        manual.Show(True)

    def reset_motors(self, e):
        self.disablegui()
        if not self.console_frame:
            self.console_frame = ConsoleGUI(self, "Console")
        self.console_frame.Show(True)
        sys.stdout = TextRedirecter(self.console_frame.console_tctrl)  # Redirect text from stdout to the console
        sys.stderr = TextRedirecter(self.console_frame.console_tctrl)  # Redirect text from stderr to the console
        ResetThread(self).start()

    def enablegui(self):
        self.x_tctrl.Enable(True)
        self.y_tctrl.Enable(True)
        self.grid_tctrl.Enable(True)
        self.dwell_tctrl.Enable(True)
        self.zdwell_tctrl.Enable(True)
        self.save_tctrl.Enable(True)
        self.save_btn.Enable(True)
        self.type_rbox.Enable(True)
        self.field_rbox.Enable(True)
        self.side_rbox.Enable(True)
        self.reset_btn.Enable(True)
        self.manual_btn.Enable(True)
        self.run_btn.Enable(True)

    def disablegui(self):
        self.x_tctrl.Enable(False)
        self.y_tctrl.Enable(False)
        self.grid_tctrl.Enable(False)
        self.dwell_tctrl.Enable(False)
        self.zdwell_tctrl.Enable(False)
        self.save_tctrl.Enable(False)
        self.save_btn.Enable(False)
        self.type_rbox.Enable(False)
        self.field_rbox.Enable(False)
        self.side_rbox.Enable(False)
        self.reset_btn.Enable(False)
        self.manual_btn.Enable(False)
        self.run_btn.Enable(False)

    def errormsg(self, errmsg):
        """
        Shows an error message as a wx.Dialog.
        :param errmsg: String error message to show in the message dialog.
        :return: Nothing
        """
        with wx.MessageDialog(self, errmsg, style=wx.OK | wx.ICON_ERROR | wx.CENTER) as dlg:
            dlg.ShowModal()


if __name__ == "__main__":
    xy_positioner_gui = wx.App()
    fr = MainFrame(None, title='XY Positioner (for NS Testing)')
    xy_positioner_gui.MainLoop()
