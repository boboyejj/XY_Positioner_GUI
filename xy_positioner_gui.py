"""
    Created by Chang Hwan 'Oliver' Choi on 08/09/2018
    changhwan.choi@pctest.com
"""

import numpy as np
from src.grid_scan_manual import run_scan, generate_grid, move_to_pos_one
from src.motor_driver import MotorDriver
from src.location_select_gui import LocationSelectGUI
from src.manual_gui_grid import ManualGridGUI

class MainFrame(wx.Frame):
    def __init__(self):


