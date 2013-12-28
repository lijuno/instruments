"""
This is done under Windows 7 
"""

import ni
import serial
import matplotlib.pyplot as plt
import utilib as ut
import time 

def SR570_write(cmd, port='COM6'):
    ser = serial.Serial(port=port, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_TWO, bytesize=serial.EIGHTBITS)
    if not ser.isOpen():
        ser.open()
    else:           
        ser.write(cmd + '\r\n')
        ser.close()

def usb6211_get():
    channel = 'Dev1/ai6'
    voltage_limit = 0.2
    sampling_freq = 1e5
    sampling_pts = 1e4
    daq = ni.USB6211()
    data = daq.get_voltage_ai(channel, voltage_limit, sampling_freq, sampling_pts)
    plt.plot(data)
    plt.show()
    
if __name__ == "__main__":
    SR570_write('BSLV -100')   # set bias level
    SR570_write('BSON 1')     # turn on bias
    time.sleep(1)          # stabilize
    usb6211_get()              # record data
    SR570_write('BSON 0')   # turn off bias
    


    
    
