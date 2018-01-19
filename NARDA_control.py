"""
    Created by Ganesh Arvapalli on 1/4/18
    ganesh.arvapalli@pctest.com
"""

import serial
import time
import math
import numpy as np
import struct


class NARDAcontroller():
    def __init__(self, start_freq=13000, step_freq=1000, stop_freq=15000, type='E', dwell=1):
        try:
            self.port = serial.Serial('COM4', baudrate=38400, timeout=2)
            self.port.flushInput()
            self.port.flushOutput()
            self.port.flush()
            self.start = start_freq
            self.step = step_freq
            self.stop = stop_freq + self.step
            self.modes = ['Ex', 'Ey', 'Ez', 'Hxh (Mode A)', 'Hyh (Mode A)', 'Hzh (Mode A)',
                          'Hx (Mode B)', 'Hy (Mode B)', 'Hz (Mode B)']
            self.type = type
            self.electrical = []
            self.magnetic_a = []
            self.magnetic_b = []
            self.dwell = dwell
        except serial.SerialException:
            print 'Error opening NARDA port'
            exit(1)

    def read_one_mode(self, mode, start=None, stop=None, step=None):
        # If reading custom, allow for changes
        if start is None and stop is None and step is None:
            start = self.start
            step = self.step
            stop = self.stop

        self.port.flushInput()
        self.port.flushOutput()

        # 1 is Ex, 2 is Ey, 3 is Ez, magnetic modes require different commands
        if mode < 6:
            self.port.write(str.encode('#00' + chr(126) + 'C' + chr(mode + 1) + chr(0) + '*\r'))
        else:
            self.port.write(str.encode('#00' + chr(126) + 'C' + chr(mode + 1) + chr(80) + '*\r'))
        self.port.readline()
        # print 'Select ' + self.modes[mode] + ': ', out

        if mode < 3:
            kf = 0.125
        elif mode < 6:
            kf = 0.075
        else:
            kf = 0.0075

        time.sleep(self.dwell)
        n = (stop - start) / step
        num_bytes = 5 * n
        self.port.write(str.encode('#00(g*\r'))
        output = self.port.read(num_bytes)
        while self.port.in_waiting:
            output += self.port.read(num_bytes)
        # print output
        time.sleep(1)

        # print output.encode('hex')
        output = output[11:]
        print output.encode('hex')

        fields = []
        for i in range(len(output) / 5):
            # print output[5*i].encode('hex'),'^',output[5*i+1].encode('hex'),'^',output[5*i+2].encode('hex'),'^',output[5*i+3].encode('hex'),'^',output[5*i+4].encode('hex')
            # sync = ((int(output[5*i].encode('hex'), 16)) / (step/1000.0)) % 256 + 1
            # print 'Sync', output[5*i].encode('hex')
            # EXP is either 5*i+2 or 5*i+3 still not sure
            exp = int(output[5 * i + 2].encode('hex'), 16)
            # print 'Exp', output[5*i+2].encode('hex')
            mantissa = int(output[5 * i + 4].encode('hex'), 16)
            # print 'Mantissa', output[5*i+4].encode('hex')
            # print output[5*i:5*i+5].encode('hex')
            fld = kf * mantissa / 8.0 * math.sqrt(math.pow(2.0, exp))  # ** 2
            # print 'Sync ', sync, 'Exp', exp, 'Mantissa', mantissa, '\nField', fld
            # print 'Field at step ' + str(sync) + ': ', fld
            fields.append(fld)
            # print self.modes[mode] + ' Field at ' + str(start + i * step) + ' Hz: ', fld
        return fields

    def read_data(self, start=None, step=None, stop=None):
        # If reading custom, allow for changes
        if start is None and stop is None and step is None:
            start = self.start
            step = self.step
            stop = self.stop

        self.port.write(str.encode('#00v*\r'))
        self.port.readline()
        # print 'Setting to request mode: ', out
        self.port.flush()

        # Lowest frequency of scan in Hz
        self.port.write(str.encode('#00(i' + str(start) + '*\r'))
        self.port.readline()
        # print 'Set start freq to ' + str(start) + ' Hz: Done'  # , out
        self.port.flush()

        # Steps to climb from lowest to highest frequency in Hz
        self.port.write(str.encode('#00(s' + str(step) + '*\r'))
        self.port.readline()
        # print 'Set freq step to ' + str(step) + ' Hz: Done'  # , out
        self.port.flush()

        # Highest frequency of scan in Hz
        self.port.write(str.encode('#00(f' + str(stop) + '*\r'))
        self.port.readline()
        # print 'Set stop freq to ' + str(stop - step) + ' Hz: Done'  # , out
        self.port.flush()

        modes_to_do = []
        if 'E' in self.type:
            modes_to_do.append(1)
        if 'Ha' in self.type:
            modes_to_do.append(3)
        if 'Hb' in self.type:
            modes_to_do.append(5)

        for i in modes_to_do:
            out1 = self.read_one_mode(i, start, stop + step, step)
            self.port.flush()
            self.port.flushOutput()
            self.port.flushInput()
            out2 = self.read_one_mode(i + 1, start, stop + step, step)
            self.port.flush()
            self.port.flushOutput()
            self.port.flushInput()
            out3 = self.read_one_mode(i + 2, start, stop + step, step)
            self.port.flush()
            self.port.flushOutput()
            self.port.flushInput()
            for j in range(len(out1)):
                mag = self.get_magnitude(out1[j], out2[j], out3[j])
                if i == 1:
                    self.electrical.append(mag)
                elif i == 3:
                    self.magnetic_a.append(mag)
                elif i == 5:
                    self.magnetic_b.append(mag)

    def get_magnitude(self, x, y, z):
        return x ** 2.0 + y ** 2.0 + z ** 2.0

    def get_wide_band(self, mode='E'):
        # Integral of squared values to calculate Wide Band
        # return np.trapz([k ** 2 for k in self.totals[mode]], dx=self.step / 1000.0)
        if 'E' in mode:
            return np.trapz([k for k in self.electrical], dx=self.step / 1000.0)
        elif 'Ha' in mode:
            return np.trapz([k for k in self.magnetic_a], dx=self.step / 1000.0)
        elif 'Hb' in mode:
            return np.trapz([k for k in self.magnetic_b], dx=self.step / 1000.0)
        return

    def get_highest_peak(self, mode='E'):
        if 'E' in mode:
            highest = np.amax(self.electrical)
            return highest, int(np.argwhere(self.electrical == highest)[0]) * self.step + self.start
        elif 'Ha' in mode:
            highest = np.amax(self.magnetic_a)
            return highest, int(np.argwhere(self.magnetic_a == highest)[0]) * self.step + self.start
        elif 'Hb' in mode:
            highest = np.amax(self.magnetic_b)
            return highest, int(np.argwhere(self.magnetic_b == highest)[0]) * self.step + self.start

    def reset(self):
        self.electrical = []
        self.magnetic_a = []
        self.magnetic_b = []

    def set_dwell(self, x):
        self.dwell = x

    def destroy(self):
        self.port.flush()
        self.port.flushOutput()
        self.port.flushInput()
        self.port.close()


if __name__ == '__main__':
    n = NARDAcontroller()
    n.read_data()
    print n.get_wide_band()
    print n.get_highest_peak()
    n.destroy()
