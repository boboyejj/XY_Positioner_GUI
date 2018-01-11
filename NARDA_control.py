# Created by Ganesh Arvapalli on 1/4/18
#
# NARDA Measurement Automatation Program


import serial
import time
import math
import struct


def read_one_mode(open_port, mode, start, stop, step):
    # time.sleep(2)
    open_port.flushInput()
    open_port.flushOutput()

    # 1 is Ex, 2 is Ey, 3 is Ez, magnetic modes require different commands
    modes = ['Ex', 'Ey', 'Ez', 'Hxh (Mode A)', 'Hyh (Mode A)', 'Hzh (Mode A)',
             'Hx (Mode B)', 'Hy (Mode B)', 'Hz (Mode B)']
    if mode < 6:
        open_port.write(str.encode('#00' + chr(126) + 'C' + chr(mode + 1) + chr(0) + '*\r'))
    else:
        open_port.write(str.encode('#00' + chr(126) + 'C' + chr(mode + 1) + chr(80) + '*\r'))
    out = open_port.readline()
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
    open_port.write(str.encode('#00(g*\r'))
    output = open_port.read(num_bytes)
    while open_port.in_waiting:
        output += open_port.read(num_bytes)
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
        exp = int(output[5*i+2:5*i+4].encode('hex'), 16)
        #print 'Exp', output[5*i+2].encode('hex')
        mantissa = int(output[5*i+4:5*i+6].encode('hex'), 16)
        #print 'Mantissa', output[5*i+4].encode('hex')
        # print output[5*i:5*i+5].encode('hex')
        fld = kf * mantissa / 8.0 * math.sqrt(math.pow(2.0, exp))  # ** 2
        # print 'Sync ', sync, 'Exp', exp, 'Mantissa', mantissa, '\nField', fld
        # print 'Field at step ' + str(sync) + ': ', fld
        print modes[mode] + ' Field at ' + str(start + i * step)+' Hz: ', fld


def read_data(ser):
    ser.write(str.encode('#00v*\r'))
    out = ser.readline()
    print 'Setting to request mode: ', out
    ser.flush()

    # Lowest frequency of scan in Hz
    start_freq = 13000
    ser.write(str.encode('#00(i' + str(start_freq) + '*\r'))
    out = ser.readline()
    print 'Set start freq to ' + str(start_freq) + ' Hz: Done'#, out
    ser.flush()

    # Steps to climb from lowest to highest frequency in Hz
    step_freq = 1000
    ser.write(str.encode('#00(s' + str(step_freq) + '*\r'))
    out = ser.readline()
    print 'Set freq step to ' + str(step_freq) + ' Hz: Done'#, out
    ser.flush()

    # Highest frequency of scan in Hz
    stop_freq = 20000+step_freq
    ser.write(str.encode('#00(f' + str(stop_freq) + '*\r'))
    out = ser.readline()
    print 'Set stop freq to ' + str(stop_freq-step_freq) + ' Hz: Done'#, out
    ser.flush()

    # 6 modes, all electrical axes + mode A magnetics
    for i in range(3, 6):
        read_one_mode(ser, i, start_freq, stop_freq+step_freq, step_freq)
        ser.flush()
        ser.flushOutput()
        ser.flushInput()

    # ser.close()


if __name__ == '__main__':
    port = serial.Serial('COM4', baudrate=38400, timeout=2)
    port.flushInput()
    port.flushOutput()
    port.flush()
    read_data(port)
