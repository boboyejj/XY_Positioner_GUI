"""
NS Testing Program/XY Positioner GUI

This is the main frame/driver script for NS testing. Built on the wxPython GUI framework, the MainFrame class
handles all of the GUI elements of the entire testing program.

MainFrame and all other GUI elements run on the main thread, starting threads for analysis and computation functions.

The script contains a single class:
    - MainFrame(wx.Frame): main GUI window/frame, starts children GUIs and children threads.

Authors:
Chang Hwan 'Oliver' Choi, Biomedical/Software Engineering Intern (Aug. 2018) - changhwan.choi@pctest.com
"""

import sys
import os
from src.area_scan import AreaScanThread, ZoomScanThread, CorrectionThread
from src.post_scan_gui import PostScanGUI
from src.location_select_gui import LocationSelectGUI
from src.manual_move import ManualMoveGUI
from src.console_gui import TextRedirector, ConsoleGUI
from src.motor_driver import ResetThread
import numpy as np
import matplotlib.pyplot as plt
import wx
from wx.lib.agw import multidirdialog as mdd
import json
from src.logger import logger
from datetime import datetime
import time
import keyboard

class MainFrame(wx.Frame):
    """
    Main GUI frame of the entire NS testing program. Handles all children GUI and children threads for automated
    measurement-taking.
    """
    def __init__(self, parent, title):
        """
        :param parent: Parent object calling the MainFrame.
        :param title: Title for the MainFrame window.
        """
        wx.Frame.__init__(self, parent, title=title, size=(600, 750))
        self.scan_panel = wx.Panel(self)

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
        self.max_fname = ''  # Name of the image file for the max measurement

        # Accelerator Table/Shortcut Keys
        save_id = 115
        run_id = 116
        manual_id = 117
        reset_id = 118
        help_id = 119
        pause_id = 120
        resume_id = 121
        self.accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('s'), save_id),
                                              (wx.ACCEL_CTRL, ord('r'), run_id),
                                              (wx.ACCEL_CTRL, ord('m'), manual_id),
                                              (wx.ACCEL_CTRL, ord('t'), reset_id),
                                              (wx.ACCEL_CTRL, ord('p'), pause_id),
                                              (wx.ACCEL_CTRL, ord('e'), resume_id),
                                              (wx.ACCEL_CTRL, ord('h'), help_id)])
        self.SetAcceleratorTable(self.accel_tbl)

        # UI Elements
        self.scan_settings_text = wx.StaticText(self.scan_panel, label="Area Scan Settings")
        self.scan_settings_text.SetFont(wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.x_distance_text = wx.StaticText(self.scan_panel, label="X Distance")
        self.x_distance_text.SetFont(wx.Font(9, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.xdesc_text = wx.StaticText(self.scan_panel, label="Horizontal length of measurement region (in cm)")
        self.x_tctrl = wx.TextCtrl(self.scan_panel)
        self.x_tctrl.SetValue(str(4 * 2.8))

        self.y_distance_text = wx.StaticText(self.scan_panel, label="Y Distance")
        self.y_distance_text.SetFont(wx.Font(9, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.ydesc_text = wx.StaticText(self.scan_panel, label="Vertical length of measurement region (in cm)")
        self.y_tctrl = wx.TextCtrl(self.scan_panel)
        self.y_tctrl.SetValue(str(6 * 2.8))

        self.grid_step_dist_text = wx.StaticText(self.scan_panel, label="Grid Step Distance")
        self.grid_step_dist_text.SetFont(wx.Font(9, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.griddesc_text = wx.StaticText(self.scan_panel, label="Distance between measurement points (in cm)")
        self.grid_tctrl = wx.TextCtrl(self.scan_panel)
        self.grid_tctrl.SetValue(str(2.8))

        self.start_point_text = wx.StaticText(self.scan_panel, label="Starting Point")
        self.start_point_text.SetFont(wx.Font(9, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.posdesc_text = wx.StaticText(self.scan_panel, label="To use default starting point, set grid number to 0")
        self.pos_text = wx.StaticText(self.scan_panel, label="grid number :")
        self.pos_tctrl = wx.TextCtrl(self.scan_panel)
        self.pos_tctrl.SetValue(str(0))

        self.times_text = wx.StaticText(self.scan_panel, label="Dwell Time Settings")
        self.times_text.SetFont(wx.Font(9, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.dwell_time_text = wx.StaticText(self.scan_panel, label="Pre-Measurement Dwell Time (Area scan, in sec)")
        self.dwell_tctrl = wx.TextCtrl(self.scan_panel)
        self.dwell_tctrl.SetValue(str(3))
        self.zoom_scan_dwell_time_text = wx.StaticText(self.scan_panel, label="Pre-Measurement Dwell Time (Zoom scan, in sec)")
        self.zdwell_tctrl = wx.TextCtrl(self.scan_panel)
        self.zdwell_tctrl.SetValue(str(3))

        self.span_text = wx.StaticText(self.scan_panel, label="Span Settings")
        self.span_text.SetFont(wx.Font(9, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.span_start_text = wx.StaticText(self.scan_panel, label="Start (MHz):")
        self.span_start_tctrl = wx.TextCtrl(self.scan_panel)
        self.span_start_tctrl.SetValue(str(0.005))
        self.span_stop_text = wx.StaticText(self.scan_panel, label="Stop (MHz):")
        self.span_stop_tctrl = wx.TextCtrl(self.scan_panel)
        self.span_stop_tctrl.SetValue(str(5))

        self.save_dir_text = wx.StaticText(self.scan_panel, label="Save Directory")
        self.save_dir_text.SetFont(wx.Font(9, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.savedesc_text = wx.StaticText(self.scan_panel, label="Directory to save measurement text and image files")
        self.save_tctrl = wx.TextCtrl(self.scan_panel)
        # self.save_tctrl.SetValue("C:\\Users\changhwan.choi\Desktop\hello")  # TODO :Debugging
        self.save_btn = wx.Button(self.scan_panel, save_id, "Browse")
        self.Bind(wx.EVT_BUTTON, self.select_save_dir, self.save_btn)

        self.auto_checkbox = wx.CheckBox(self.scan_panel, label="Automatic Measurements")  # TODO: may not use
        self.auto_checkbox.SetValue(True)

        self.zoom_checkbox = wx.CheckBox(self.scan_panel, label="Zoom Scan")
        self.zoom_checkbox.SetValue(False)

        self.test_info_text = wx.StaticText(self.scan_panel, label="Test Information")
        self.test_info_text.SetFont(wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.eut_model_text = wx.StaticText(self.scan_panel, label="Model of EUT: ")
        self.eut_model_tctrl = wx.TextCtrl(self.scan_panel)
        self.eut_sn_text = wx.StaticText(self.scan_panel, label="S/N of EUT: ")
        self.eut_sn_tctrl = wx.TextCtrl(self.scan_panel)
        self.initials_text = wx.StaticText(self.scan_panel, label="Test Engineer Initials: ")
        self.initials_tctrl = wx.TextCtrl(self.scan_panel)
        self.test_num_text = wx.StaticText(self.scan_panel, label="Test Number: ")
        self.test_num_tctrl = wx.TextCtrl(self.scan_panel)

        self.measurement_specs_text = wx.StaticText(self.scan_panel, label="Measurement Specifications")
        self.measurement_specs_text.SetFont(wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.type_rbox = wx.RadioBox(self.scan_panel, label="Type", choices=['Limb', 'Body'],
                                     style=wx.RA_SPECIFY_COLS, majorDimension=1)
        self.field_rbox = wx.RadioBox(self.scan_panel, label="Field",
                                      choices=['Electric', 'Magnetic (Mode A)', 'Magnetic (Mode B)'],
                                      style=wx.RA_SPECIFY_COLS, majorDimension=1)
        self.side_rbox = wx.RadioBox(self.scan_panel, label="Side",
                                     choices=['Front', 'Back', 'Top', 'Bottom', 'Left', 'Right'],
                                     style=wx.RA_SPECIFY_COLS, majorDimension=1)
        self.side_rbox.SetSelection(1)
        self.rbw_rbox = wx.RadioBox(self.scan_panel, label="RBW",
                                    choices=['300 kHz', '10 kHz', '100 kHz', '3 kHz', '30 kHz', '1 kHz'],
                                    style=wx.RA_SPECIFY_COLS, majorDimension=2)
        self.rbw_rbox.SetSelection(2)
        self.meas_rbox = wx.RadioBox(self.scan_panel, label="Measurement", choices=['Highest Peak', 'WideBand'],
                                     style=wx.RA_SPECIFY_COLS, majorDimension=1)

        self.reset_btn = wx.Button(self.scan_panel, reset_id, "Reset Motors")
        self.Bind(wx.EVT_BUTTON, self.reset_motors, self.reset_btn)
        self.manual_btn = wx.Button(self.scan_panel, manual_id, "Manual Movement")
        self.Bind(wx.EVT_BUTTON, self.manual_move, self.manual_btn)
        self.run_btn = wx.Button(self.scan_panel, run_id, "Run")
        self.Bind(wx.EVT_BUTTON, self.run_area_scan, self.run_btn)

        # Menu Bar
        menubar = wx.MenuBar()
        helpmenu = wx.Menu()
        shortcuthelp_item = wx.MenuItem(helpmenu, help_id, text="Shortcuts", kind=wx.ITEM_NORMAL)
        pause_item = wx.MenuItem(helpmenu, pause_id, text="Pause", kind=wx.ITEM_NORMAL)
        helpmenu.Append(shortcuthelp_item)
        helpmenu.Append(pause_item)
        menubar.Append(helpmenu, 'Help')
        self.Bind(wx.EVT_MENU, self.showshortcuts, id=help_id)
        self.Bind(wx.EVT_MENU, self.pauseProg, id=pause_id)
        self.SetMenuBar(menubar)

        # Sizers/Layout, Static Lines, & Static Boxes
        self.saveline_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.checkbox_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.pos_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.span_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.test_info_sizer = wx.GridSizer(rows=4, cols=2, hgap=0, vgap=0)
        self.text_input_sizer = wx.BoxSizer(wx.VERTICAL)
        self.radio_input_sizer = wx.BoxSizer(wx.VERTICAL)
        self.btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainh_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainv_sizer = wx.BoxSizer(wx.VERTICAL)

        self.text_input_sizer.Add(self.scan_settings_text, proportion=0, border=3, flag=wx.BOTTOM)
        self.text_input_sizer.Add(self.x_distance_text, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.xdesc_text, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.x_tctrl, proportion=0, flag=wx.LEFT | wx.EXPAND)
        self.text_input_sizer.Add(self.y_distance_text, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.ydesc_text, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.y_tctrl, proportion=0, flag=wx.LEFT | wx.EXPAND)
        self.text_input_sizer.Add(self.grid_step_dist_text, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.griddesc_text, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.grid_tctrl, proportion=0, flag=wx.LEFT | wx.EXPAND)

        self.text_input_sizer.Add(self.start_point_text, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.posdesc_text, proportion=0, flag=wx.LEFT)
        self.pos_sizer.Add(self.pos_text, proportion=0, flag=wx.LEFT)
        self.pos_sizer.Add(self.pos_tctrl, proportion=1, flag=wx.LEFT | wx.RIGHT | wx.EXPAND, border=5)
        self.text_input_sizer.Add(self.pos_sizer, proportion=0, flag=wx.EXPAND)

        self.text_input_sizer.Add(self.times_text, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.dwell_time_text, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.dwell_tctrl, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.zoom_scan_dwell_time_text, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.zdwell_tctrl, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.span_text, proportion=0, flag=wx.LEFT)
        self.span_sizer.Add(self.span_start_text, proportion=0, flag=wx.LEFT)
        self.span_sizer.Add(self.span_start_tctrl, proportion=1, flag=wx.LEFT | wx.RIGHT | wx.EXPAND, border=5)
        self.span_sizer.Add(self.span_stop_text, proportion=0, flag=wx.LEFT)
        self.span_sizer.Add(self.span_stop_tctrl, proportion=1, flag=wx.LEFT | wx.EXPAND, border=5)
        self.text_input_sizer.Add(self.span_sizer, proportion=0, flag=wx.EXPAND)
        self.text_input_sizer.Add(self.save_dir_text, proportion=0, flag=wx.LEFT)
        self.text_input_sizer.Add(self.savedesc_text, proportion=0, flag=wx.LEFT)
        self.saveline_sizer.Add(self.save_tctrl, proportion=1, flag=wx.LEFT | wx.EXPAND)
        self.saveline_sizer.Add(self.save_btn, proportion=0, flag=wx.ALIGN_RIGHT | wx.LEFT, border=5)
        self.checkbox_sizer.Add(self.auto_checkbox, proportion=0, flag=wx.ALIGN_LEFT | wx.ALL, border=5)
        self.checkbox_sizer.Add(self.zoom_checkbox, proportion=0, flag=wx.ALIGN_LEFT | wx.ALL, border=5)
        self.text_input_sizer.Add(self.saveline_sizer, proportion=0, flag=wx.LEFT | wx.EXPAND)
        self.text_input_sizer.Add(self.checkbox_sizer, proportion=0, flag=wx.LEFT | wx.EXPAND)
        self.text_input_sizer.Add(wx.StaticLine(self.scan_panel, wx.ID_ANY, style=wx.LI_HORIZONTAL),
                                  proportion=0, border=5, flag=wx.TOP | wx.BOTTOM | wx.EXPAND)
        self.text_input_sizer.Add(self.test_info_text, proportion=0, flag=wx.BOTTOM, border=3)
        self.test_info_sizer.Add(self.eut_model_text, proportion=0)
        self.test_info_sizer.Add(self.eut_model_tctrl, proportion=0, flag=wx.EXPAND)
        self.test_info_sizer.Add(self.eut_sn_text, proportion=0)
        self.test_info_sizer.Add(self.eut_sn_tctrl, proportion=0, flag=wx.EXPAND)
        self.test_info_sizer.Add(self.initials_text, proportion=0)
        self.test_info_sizer.Add(self.initials_tctrl, proportion=0, flag=wx.EXPAND)
        self.test_info_sizer.Add(self.test_num_text, proportion=0)
        self.test_info_sizer.Add(self.test_num_tctrl, proportion=0, flag=wx.EXPAND)
        self.text_input_sizer.Add(self.test_info_sizer, proportion=0, flag=wx.EXPAND)

        self.radio_input_sizer.Add(self.measurement_specs_text, proportion=0, border=3, flag=wx.BOTTOM)
        self.radio_input_sizer.Add(self.type_rbox, proportion=0, flag=wx.ALL | wx.EXPAND)
        self.radio_input_sizer.Add(self.field_rbox, proportion=0, flag=wx.ALL | wx.EXPAND)
        self.radio_input_sizer.Add(self.side_rbox, proportion=0, flag=wx.ALL | wx.EXPAND)
        self.radio_input_sizer.Add(self.rbw_rbox, proportion=0, flag=wx.ALL | wx.EXPAND)
        self.radio_input_sizer.Add(self.meas_rbox, proportion=0, flag=wx.ALL | wx.EXPAND)

        self.mainh_sizer.Add(self.text_input_sizer, proportion=2, border=5, flag=wx.ALL | wx.EXPAND)
        self.mainh_sizer.Add(wx.StaticLine(self.scan_panel, wx.ID_ANY, style=wx.LI_VERTICAL),
                             proportion=0, border=5, flag=wx.TOP | wx.BOTTOM | wx.EXPAND)
        self.mainh_sizer.Add(self.radio_input_sizer, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)

        self.btn_sizer.Add(self.reset_btn, proportion=1, border=5,
                           flag=wx.ALIGN_RIGHT | wx.LEFT | wx.TOP | wx.BOTTOM)
        self.btn_sizer.Add(self.manual_btn, proportion=1, border=5,
                           flag=wx.ALIGN_RIGHT | wx.LEFT | wx. TOP | wx.BOTTOM)
        self.btn_sizer.Add(self.run_btn, proportion=1, border=5, flag=wx.ALIGN_RIGHT | wx.ALL)

        self.mainv_sizer.Add(self.mainh_sizer, proportion=1, border=0, flag=wx.ALL | wx.EXPAND)
        self.mainv_sizer.Add(wx.StaticLine(self.scan_panel, wx.ID_ANY, style=wx.LI_HORIZONTAL),
                             proportion=0, border=0, flag=wx.ALL | wx.EXPAND)
        self.mainv_sizer.Add(self.btn_sizer, proportion=0, border=5, flag=wx.ALIGN_RIGHT)

        # load previous configuration when initialize the panel
        self.load_configuration()

        self.scan_panel.SetSizer(self.mainv_sizer)
        pan_size = self.scan_panel.GetSize()
        print(pan_size)
        self.SetSize(pan_size)
        self.SetMinSize(pan_size)
        self.SetMaxSize(pan_size)
        self.SetAutoLayout(True)
        # self.scan_panel.Fit()
        self.mainv_sizer.Fit(self.scan_panel)
        self.Layout()
        self.Show(True)

    def select_save_dir(self, e):
        """
        Opens quick dialog to select the save directory for the output files (.txt, .png) from the automatic
        measurements. Writes the directory name on the TextCtrl object on the GUI (self.save_tctrl).

        :param e: Event handler.
        :return: Nothing.
        """
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
        # with wx.DirDialog(self, "Select save directory for '.txt' and '.png' files.",
        #                   style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) as dlg:
        #    if dlg.ShowModal() == wx.ID_CANCEL:
        #        return
        #    self.save_dir = dlg.GetPath()
        #    self.save_tctrl.SetValue(self.save_dir)
        #    if os.path.exists(parentpath):

    def save_configuration(self, filename='prev_config.txt'):
        """
        Save current configuration to a txt file

        """
        try:
            config = {}
            config['x'] = self.x_tctrl.GetValue()
            config['y'] = self.y_tctrl.GetValue()
            config['step'] = self.grid_tctrl.GetValue()
            config['start_pos'] = self.pos_tctrl.GetValue()
            config['dwell'] = self.dwell_tctrl.GetValue()
            config['zdwell'] = self.zdwell_tctrl.GetValue()
            config['start'] = self.span_start_tctrl.GetValue()
            config['stop'] = self.span_stop_tctrl.GetValue()
            config['checkbox'] = self.auto_checkbox.GetValue()
            config['type'] = self.type_rbox.GetSelection()
            config['field'] = self.field_rbox.GetSelection()
            config['side'] = self.side_rbox.GetSelection()
            config['rbw'] = self.rbw_rbox.GetSelection()
            config['measurement'] = self.meas_rbox.GetSelection()
            config['dir'] = self.save_tctrl.GetValue()

            json.dump(config,open(filename,'w'))

        except ValueError:
            self.errormsg("Invalid scan parameters.\nCannot save current configuration.")
            return

        return

    def load_configuration(self, filename='prev_config.txt'):
        """
        Load the saved configuration

        """
        # TODO: Add error exception
        if os.path.exists(filename):
            config = json.load(open(filename))
            self.x_tctrl.SetValue(config['x'])
            self.y_tctrl.SetValue(config['y'])
            self.grid_tctrl.SetValue(config['step'])
            self.pos_tctrl.SetValue(config['start_pos'])
            self.dwell_tctrl.SetValue(config['dwell'])
            self.zdwell_tctrl.SetValue(config['zdwell'])
            self.span_start_tctrl.SetValue(config['start'])
            self.span_stop_tctrl.SetValue(config['stop'])
            self.auto_checkbox.SetValue(config['checkbox'])
            self.type_rbox.SetSelection(int(config['type']))
            self.field_rbox.SetSelection(int(config['field']))
            self.side_rbox.SetSelection(int(config['side']))
            self.rbw_rbox.SetSelection(int(config['rbw']))
            self.meas_rbox.SetSelection(int(config['measurement']))
            self.save_tctrl.SetValue(config['dir'])

    def run_area_scan(self, e):
        """
        Begins general area scan based on the measurement settings specified on the GUI.
        Starts and runs an instance of AreaScanThread to perform automatic area scan.
        Opens console GUI to help user track progress of the program.

        :param e: Event handler.
        :return: Nothing.
        """
        # Make sure entries are valid
        if self.save_tctrl.GetValue() is None or \
                self.save_tctrl.GetValue() is '' or \
                not os.path.exists(self.save_tctrl.GetValue()):
            self.errormsg("Please select a valid save directory for the output files.")
            return
        try:
            self.save_configuration()
            x = float(self.x_tctrl.GetValue())
            y = float(self.y_tctrl.GetValue())
            step = float(self.grid_tctrl.GetValue())
            dwell = float(self.dwell_tctrl.GetValue())
            span_start = float(self.span_start_tctrl.GetValue())
            span_stop = float(self.span_stop_tctrl.GetValue())
            start_pos = float(self.pos_tctrl.GetValue())
            zoom_scan = self.zoom_checkbox.GetValue()
        except ValueError:
            self.errormsg("Invalid scan parameters.\nPlease input numerical values only.")
            return
        # Build comment for savefiles
        if self.eut_model_tctrl.GetValue() is '' or self.eut_sn_tctrl.GetValue() is '' or \
                self.initials_tctrl.GetValue() is '' or self.test_num_tctrl.GetValue() is '':
            self.errormsg("Please fill out all entries in the 'Test Information' section.")
            return
        comment = "Model of EUT: " + self.eut_model_tctrl.GetValue() + \
                  " - \r\nS/N of EUT: " + self.eut_sn_tctrl.GetValue() + \
                  " - \r\nTest Engineer Initials: " + self.initials_tctrl.GetValue() + \
                  " - \r\nTest Number: " + self.test_num_tctrl.GetValue()
        savedir = self.save_tctrl.GetValue()
        # Finding the measurement type
        meas_type = self.type_rbox.GetStringSelection()
        # Finding the measurement field
        meas_field = self.field_rbox.GetStringSelection()
        # Finding the measurement side
        meas_side = self.side_rbox.GetStringSelection()
        # Finding the RBW setting
        meas_rbw = self.rbw_rbox.GetStringSelection()
        # Finding the measurement
        meas = self.meas_rbox.GetStringSelection()

        if zoom_scan == "True":
            self.run_thread = ZoomScanThread(self, x, y, step, dwell, span_start, span_stop, savedir,
                                             comment, meas_type, meas_field, meas_side, meas_rbw, meas,
                                             self.curr_row, self.curr_col)
        else:
            self.run_thread = AreaScanThread(self, x, y, step, dwell, span_start, span_stop, savedir,
                                             comment, meas_type, meas_field, meas_side, meas_rbw, meas, start_pos)

        # self.disablegui()
        logger.info("")
        logger.info(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        if not self.console_frame:
            self.console_frame = ConsoleGUI(self, "Console")
        self.console_frame.Show(True)
        sys.stdout = TextRedirector(self.console_frame.console_tctrl)  # Redirect text from stdout to the console
        sys.stderr = TextRedirector(self.console_frame.console_tctrl)  # Redirect text from stderr to the console
        print("Running general scan...")
        self.run_thread.start()

    def run_post_scan(self):
        """
        Plots the area scan results and prompts the user for a post-scan option ('Exit', 'Zoom Scan', 'Correct previous
        value', 'Save data'). Called by the area scan threads (AreaScanThread, ZoomScanThread, CorrectionThread)
        once threads are closed.

        :return: Nothing.
        """
        # Plot the scan
        plotvals = np.copy(self.values)
        plotvals = np.rot90(plotvals)
        plt.close()
        plt.imshow(plotvals, interpolation='bilinear',
                   extent=[0, plotvals.shape[1] - 1, 0, plotvals.shape[0] - 1])
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
            meas_type = self.type_rbox.GetStringSelection()
            # Finding the measurement field
            meas_field = self.field_rbox.GetStringSelection()
            # Finding the measurement side
            meas_side = self.side_rbox.GetStringSelection()
            # Finding the RBW setting
            meas_rbw = self.rbw_rbox.GetStringSelection()
            # Finding the measurement
            meas = self.meas_rbox.GetStringSelection()
            self.zoom_thread = ZoomScanThread(self, zdwell, self.run_thread.span_start, self.run_thread.span_stop,
                                              savedir, self.run_thread.comment, meas_type, meas_field, meas_side,
                                              meas_rbw, meas, self.run_thread.num_steps, self.values, self.grid,
                                              self.curr_row, self.curr_col)
            if not self.console_frame:
                self.console_frame = ConsoleGUI(self, "Console")
            self.console_frame.Show(True)
            sys.stdout = TextRedirector(self.console_frame.console_tctrl)  # Redirect text from stdout to the console
            sys.stderr = TextRedirector(self.console_frame.console_tctrl)  # Redirect text from stderr to the console
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
        """
        Updates the variables stored in the MainFrame based on the measurement results returned from the scans.
        Called by the area scan threads (AreaScanThread, ZoomScanThread, CorrectionThread).

        :param call_thread: The thread calling the update method and updating the variables stored in the MainFrame.
        :return: Nothing.
        """
        self.curr_row = call_thread.curr_row
        self.curr_col = call_thread.curr_col
        if type(call_thread) is AreaScanThread:
            self.values = call_thread.values
            self.grid = call_thread.grid
            self.max_fname = call_thread.max_fname
        elif type(call_thread) is CorrectionThread:
            self.values = call_thread.values
        elif type(call_thread) is ZoomScanThread:
            self.zoom_values = call_thread.zoom_values

    def run_correction(self, target_index):
        """
        Runs the 'Correct Previous Value' option from the Post Scan GUI. Starts and runs an instance of
        CorrectionThread to retake a measurement in the specified coordinate.

        :param target_index: the index in the grid that the user chooses to correct.
        :return: Nothing.
        """
        savedir = self.save_tctrl.GetValue()
        # Finding the measurement type
        meas_type = self.type_rbox.GetStringSelection()
        # Finding the measurement field
        meas_field = self.field_rbox.GetStringSelection()
        # Finding the measurement side
        meas_side = self.side_rbox.GetStringSelection()
        # Finding the RBW setting
        meas_rbw = self.rbw_rbox.GetStringSelection()
        self.corr_thread = CorrectionThread(self, target_index, self.run_thread.num_steps,
                                            float(self.dwell_tctrl.GetValue()), self.run_thread.span_start,
                                            self.run_thread.span_stop, self.values, self.grid,
                                            self.curr_row, self.curr_col, savedir, self.run_thread.comment,
                                            meas_type, meas_field, meas_side, meas_rbw, self.max_fname)
        if not self.console_frame:
            self.console_frame = ConsoleGUI(self, "Console")
        self.console_frame.Show(True)
        sys.stdout = TextRedirector(self.console_frame.console_tctrl)  # Redirect text from stdout to the console
        sys.stderr = TextRedirector(self.console_frame.console_tctrl)  # Redirect text from stderr to the console
        self.corr_thread.start()

    def manual_move(self, e):
        """
        Allows user to manually move the position of the NS probe. Opens a terminal console if not open already.
        Creates and shows instance of ManualMoveGUI to allow direct input from the user.

        :param e: Event handler.
        :return: Nothing.
        """
        if not self.console_frame:
            self.console_frame = ConsoleGUI(self, "Console")
        self.console_frame.Show(True)
        sys.stdout = TextRedirector(self.console_frame.console_tctrl)  # Redirect text from stdout to the console
        sys.stderr = TextRedirector(self.console_frame.console_tctrl)  # Redirect text from stderr to the console
        try:
            step = float(self.grid_tctrl.GetValue())
        except ValueError:
            self.errormsg("Invalid scan parameters.\nPlease input numerical values only.")
            return
        manual = ManualMoveGUI(self, "Manual Movement", step)
        manual.Show(True)

    def reset_motors(self, e):
        """
        Resets the motors back to their default position. Starts and runs instance of ResetThread to facilitate motor
        resets. Opens terminal console if not open already.

        :param e: Event handler.
        :return: Nothing.
        """
        self.disablegui()
        if not self.console_frame:
            self.console_frame = ConsoleGUI(self, "Console")
        self.console_frame.Show(True)
        sys.stdout = TextRedirector(self.console_frame.console_tctrl)  # Redirect text from stdout to the console
        sys.stderr = TextRedirector(self.console_frame.console_tctrl)  # Redirect text from stderr to the console
        ResetThread(self).start()

    def enablegui(self):
        """
        Re-enables all MainFrame GUI elements.

        :return: Nothing.
        """
        self.x_tctrl.Enable(True)
        self.y_tctrl.Enable(True)
        self.grid_tctrl.Enable(True)
        self.dwell_tctrl.Enable(True)
        self.zdwell_tctrl.Enable(True)
        self.span_start_tctrl.Enable(True)
        self.span_stop_tctrl.Enable(True)
        self.save_tctrl.Enable(True)
        self.auto_checkbox.Enable(True)
        self.zoom_checkbox.Enable(True)
        self.save_btn.Enable(True)
        self.eut_model_tctrl.Enable(True)
        self.eut_sn_tctrl.Enable(True)
        self.initials_tctrl.Enable(True)
        self.test_num_tctrl.Enable(True)
        self.type_rbox.Enable(True)
        self.field_rbox.Enable(True)
        self.side_rbox.Enable(True)
        self.rbw_rbox.Enable(True)
        self.reset_btn.Enable(True)
        self.manual_btn.Enable(True)
        self.run_btn.Enable(True)

    def disablegui(self):
        """
        Disables all MainFrame GUI elements.

        :return: Nothing.
        """
        self.x_tctrl.Enable(False)
        self.y_tctrl.Enable(False)
        self.grid_tctrl.Enable(False)
        self.dwell_tctrl.Enable(False)
        self.zdwell_tctrl.Enable(False)
        self.span_start_tctrl.Enable(False)
        self.span_stop_tctrl.Enable(False)
        self.save_tctrl.Enable(False)
        self.auto_checkbox.Enable(False)
        self.zoom_checkbox.Enable(False)
        self.save_btn.Enable(False)
        self.eut_model_tctrl.Enable(False)
        self.eut_sn_tctrl.Enable(False)
        self.initials_tctrl.Enable(False)
        self.test_num_tctrl.Enable(False)
        self.type_rbox.Enable(False)
        self.field_rbox.Enable(False)
        self.side_rbox.Enable(False)
        self.rbw_rbox.Enable(False)
        self.reset_btn.Enable(False)
        self.manual_btn.Enable(False)
        self.run_btn.Enable(False)

    def showshortcuts(self, e):
        """
        Opens simple dialog listing the different shortcuts of the program.

        :param e: Event handler.
        :return: Nothing.
        """
        shortcuts_string = "Shortcuts:\n" +\
                           "Select Save Directory: Ctrl + S\n" +\
                           "Reset Motors: Ctrl + T\n" +\
                           "Manual Movement: Ctrl + M\n" +\
                           "Run Analysis: Ctrl + E\n" +\
                           "Check Shortcut Keys: Ctrl + H"
        with wx.MessageDialog(self, shortcuts_string, 'Shortcut Keys',
                              style=wx.OK | wx.ICON_QUESTION | wx.CENTER) as dlg:
            dlg.ShowModal()

    def pauseProg(self,e):
        """
        pause the program
        """
        print("press Enter to continue")

        while True:
            key = keyboard.read_key()

            if key == "enter":
                print("Program is resumed")
                # exit(0)
                break

            time.sleep(0.5)

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
