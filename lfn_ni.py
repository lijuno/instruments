"""
This is done under Windows 7 
"""

import ni
from misc import sr570_write
import numpy as np
import matplotlib.pyplot as plt
import utilib as ut
import time
import sys


def usb6211_get(filename='', voltage_limit=0.2, duration=5):
    # duration: measurement duration, in s
    channel = 'Dev1/ai6'
    sampling_freq = 5e4
    #sampling_pts = 250000  # too many points will make the program fail
    sampling_pts = sampling_freq * duration
    daq = ni.USB6211()
    data = daq.get_voltage_ai(channel, voltage_limit, sampling_freq, sampling_pts)

    if filename == '':
        filename = 'data'
    plt.plot(data)
    plt.savefig('%s.png' % filename)
    plt.close()  # avoid "hold on" for the next plot
    ut.write_data_n1('%s.dat' % filename, data)
    # plt.show()

def main(bias_list):
    # LFN measurement with bandpass filter
    sr570_write('FLTT 2', sr570_port)   # 6 dB bandpass filter
    sr570_write('LFRQ 11', sr570_port)   # 10kHz upper bound
    sr570_write('HFRQ 2', sr570_port)   # 0.3Hz lower bound
    for ii in range(len(bias_list)):
        sr570_write('BSLV %d' % bias_list[ii], sr570_port)   # set bias level
        sr570_write('BSON 1', sr570_port)     # turn on bias
        time.sleep(10)          # stabilize
        for jj in range(4):
            usb6211_get('Vbias%d_m%d' % (bias_list[ii], jj), voltage_limit=0.2, duration=5)       # record data
        sr570_write('BSON 0', sr570_port)   # turn off bias
        time.sleep(1)

def dc(bias_list):
    # DC coupled measurement
    sr570_write('FLTT 3', sr570_port)   # 6 dB lowpass filter
    sr570_write('LFRQ 11', sr570_port)
    for ii in range(len(bias_list)):
        sr570_write('BSLV %d' % bias_list[ii], sr570_port)   # set bias level
        sr570_write('BSON 1', sr570_port)     # turn on bias
        time.sleep(3)
        usb6211_get('Vbias%d_DC' % bias_list[ii], voltage_limit=2, duration=2)
        sr570_write('BSON 0', sr570_port)   # turn off bias
        time.sleep(1)

if __name__ == "__main__":
    sr570_port = 'COM6'
    if sys.argv[1] == 'main':
        # Example: python lfn_ni.py main
        # To run the main routine
        # bias_lst = [-800]
        bias_lst = [-800, -400, -200, 100, 200, 300]
        main(bias_lst)

    elif sys.argv[1] == 'dc':
        bias_lst = [-800, -400, -200, 100, 200, 300]
        dc(bias_lst)

    elif sys.argv[1] == 'sr570':
        # Example: python lfn_ni.py sr570
        # To issue a command to SR570
        sr570_write(sys.argv[2], sr570_port)
    elif sys.argv[1] == 'usb6211':
        # Example: python lfn_ni.py usb6211
        # To take a voltage analog input measurement with USB6211
        usb6211_get('data')