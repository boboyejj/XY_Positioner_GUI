import pyautogui as pgui
import pywinauto as pwin
from win32com.client import GetObject
from pywinauto import application
import time
import os
import subprocess


class NardaNavigator:

    def __init__(self):
        pgui.PAUSE = 1
        self.refpics_path = 'narda_navigator_referencepics'
        self.ehp200_path = "C:\\Program Files (x86)\\NardaSafety\\EHP-TS\\EHP200-TS\\EHP200.exe"
        self.ehp200_app = application.Application()
        self.startNarda()

    def startNarda(self):
        WMI = GetObject('winmgmts:')
        processes = WMI.InstancesOf('Win32_Process')
        p_list = [p.Properties_('Name').Value for p in processes]
        # print(p_list)
        # ehp200_app = pwin.Application()
        if self.ehp200_path.split('\\')[-1] not in p_list:
            print("Starting EHP200 program - Connecting...")
            self.ehp200_app.start(self.ehp200_path)
            # Wait until the window has been opened
            while not pgui.locateOnScreen(self.refpics_path + '/window_title.PNG'):
                pass
            print("EHP200 Opened")
        else:
            print("EHP200 already opened - Connecting...")
            self.ehp200_app.connect(path=self.ehp200_path)

    def closeNarda(self):
        self.ehp200_app.kill()

    def selectTab(self, tabName):
        tabName = tabName.lower()
        # print(tabName)
        selectedName = '/' + tabName + '_tab_selected.PNG'
        deselectedName = '/' + tabName + '_tab_deselected.PNG'
        # print(selectedName, deselectedName)
        try:
            if not pgui.locateOnScreen(self.refpics_path + selectedName):
                print("Not located - clicking the position: " + self.refpics_path + deselectedName)
                x, y, w, h = pgui.locateOnScreen(self.refpics_path + '/' + tabName + '_tab_deselected.PNG',
                                                 grayscale=True)
                print(x, y, w, h)
                pgui.click(pgui.center((x, y, w, h)))
            else:
                print("Already in the '" + tabName + "' tab")
        except TypeError:
            print('Error: Reference images not found on screen...')
            exit(1)

    def selectInputType(self, type):
        if type.lower() == 'elec':
            pass
        elif type.lower() == 'mag_a':
            pass
        elif type.lower() == 'mag_b':
            pass
        else:
            print("Argument must be one of either 'elec', 'mag_a', or 'mag_b'")

    def takeMeasurement(self, dwell_time):
        # If not on the data tab, switch to it
        if not pgui.locateOnScreen(self.refpics_path + '/data_tab_selected.PNG'):
            pgui.click(pgui.center(pgui.locateOnScreen(self.refpics_path + '/data_tab_deselected.PNG')))

        # Reset measurement by clicking on 'Free Scan' radio button
        pgui.click(pgui.center(pgui.locateOnScreen(self.refpics_path + '/free_scan.PNG')))

        # Todo: figure out if we need to check max hold here too..

        # Wait for the measurements to settle before taking measurements
        time.sleep(dwell_time)

        # Take the actual measurement after marking the highest peak
        pgui.click(pgui.center(pgui.locateOnScreen(self.refpics_path + '/highest_peak.PNG')))
        pgui.click(pgui.center(pgui.locateOnScreen(self.refpics_path + '/save_as_text.PNG')))

        # Input comment
        pgui.click(pgui.center(pgui.locateOnScreen(self.refpics_path + '/comment.PNG')))
        pgui.typewrite("Hello world!")
        pgui.click(pgui.center(pgui.locateOnScreen(self.refpics_path + '/ok.PNG')))

        # Save file


    def saveCurrentLocation(self):
        return pgui.position()

    def loadSavedLocation(self, x, y):
        pgui.moveTo(x, y)

    def bringToFront(self):
        self.ehp200_app.EHP200.set_focus()

    def main(self):
        self.startNarda()
        self.bringToFront()
        python3 = application.Application()
        python3.connect(path="C:\\Users\\changhwan.choi\\AppData\\Local\\Continuum\\anaconda3\\Python.exe")
        python3.p3.set_focus()
        self.selectTab('Mode')
        time.sleep(0.5)
        self.selectTab('Data')
        time.sleep(0.5)
        self.selectTab('Data')
        time.sleep(0.5)
        self.selectTab('Span')
        time.sleep(0.5)
        self.selectTab('Span')
        time.sleep(0.5)
        self.selectTab('Mode')


if __name__ == '__main__':
    ehp200 = NardaNavigator()
    ehp200.main()
