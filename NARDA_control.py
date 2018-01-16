"""
    Created by Ganesh Arvapalli on 1/4/18
    ganesh.arvapalli@pctest.com
"""

import serial
import time
import math
import struct


class NARDAcontroller():
    def __init__(self, start_freq=13000, step_freq=1000, stop_freq=20000):
        try:
            self.port = serial.Serial('COM4', baudrate=38400, timeout=2)
            self.port.flushInput()
            self.port.flushOutput()
            self.port.flush()
            self.start = start_freq
            self.step = step_freq
            self.stop = stop_freq + self.step
        except serial.SerialException:
            print 'Error opening port'
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
        modes = ['Ex', 'Ey', 'Ez', 'Hxh (Mode A)', 'Hyh (Mode A)', 'Hzh (Mode A)',
                 'Hx (Mode B)', 'Hy (Mode B)', 'Hz (Mode B)']
        if mode < 6:
            self.port.write(str.encode('#00' + chr(126) + 'C' + chr(mode + 1) + chr(0) + '*\r'))
        else:
            self.port.write(str.encode('#00' + chr(126) + 'C' + chr(mode + 1) + chr(80) + '*\r'))
        out = self.port.readline()
        print 'Select ' + modes[mode] + ': ', out

        if mode < 3:
            kf = 0.125
        elif mode < 6:
            kf = 0.075
        else:
            kf = 0.0075

        time.sleep(1)
        n = (stop - start)/step
        # if type(n) is not int:
        #     print 'Error: Check if stop - start is divisible by step size.'
        #     exit(1)
        num_bytes = 5*n
        self.port.write(str.encode('#00(g*\r'))
        output = self.port.read(num_bytes)
        while self.port.in_waiting:
            output += self.port.read(num_bytes)
        # print output
        print output.encode('hex')
        output = output[11:]
        print output.encode('hex')

        for i in range(len(output)/5):
            # print output[5*i].encode('hex'),'^',output[5*i+1].encode('hex'),'^',output[5*i+2].encode('hex'),'^',output[5*i+3].encode('hex'),'^',output[5*i+4].encode('hex')
            # print output[5*i:5*i+5]
            # sync = ((int(output[5*i].encode('hex'), 16)) / (step/1000.0)) % 256 + 1
            #print 'Sync', output[5*i].encode('hex')
            # EXP is either 5*i+2 or 5*i+3 still not sure
            exp = int(output[5*i+2].encode('hex'), 16)
            #print 'Exp', output[5*i+2].encode('hex')
            mantissa = int(output[5*i+4].encode('hex'), 16)
            #print 'Mantissa', output[5*i+4].encode('hex')
            # print output[5*i:5*i+5].encode('hex')
            fld = kf * mantissa / 8.0 * math.sqrt(math.pow(2.0, exp))  # ** 2
            # print 'Sync ', sync, 'Exp', exp, 'Mantissa', mantissa, '\nField', fld
            # print 'Field at step ' + str(sync) + ': ', fld
            print modes[mode] + ' Field at ' + str(start + i * step)+' Hz: ', fld

    def read_data(self, start=None, step=None, stop=None):
        # If reading custom, allow for changes
        if start is None and stop is None and step is None:
            start = self.start
            step = self.step
            stop = self.stop

        self.port.write(str.encode('#00v*\r'))
        out = self.port.readline()
        print 'Setting to request mode: ', out
        self.port.flush()

        # Lowest frequency of scan in Hz
        self.port.write(str.encode('#00(i' + str(start) + '*\r'))
        out = self.port.readline()
        print 'Set start freq to ' + str(start) + ' Hz: Done'#, out
        self.port.flush()

        # Steps to climb from lowest to highest frequency in Hz
        self.port.write(str.encode('#00(s' + str(step) + '*\r'))
        out = self.port.readline()
        print 'Set freq step to ' + str(step) + ' Hz: Done'#, out
        self.port.flush()

        # Highest frequency of scan in Hz
        self.port.write(str.encode('#00(f' + str(stop) + '*\r'))
        out = self.port.readline()
        print 'Set stop freq to ' + str(stop - step) + ' Hz: Done'#, out
        self.port.flush()

        # 6 modes, all electrical axes + mode A magnetics
        for i in range(3, 6):
            self.read_one_mode(i, start, stop + step, step)
            self.port.flush()
            self.port.flushOutput()
            self.port.flushInput()

    def destroy(self):
        self.port.close()


if __name__ == '__main__':
    n = NARDAcontroller()
    n.read_data()
