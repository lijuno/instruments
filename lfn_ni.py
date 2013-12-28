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


def usb6211_get(filename=''):
    channel = 'Dev1/ai6'
    voltage_limit = 0.2
    sampling_freq = 1e5
    sampling_pts = 1e4
    daq = ni.USB6211()
    data = daq.get_voltage_ai(channel, voltage_limit, sampling_freq, sampling_pts)

    if filename == '':
        filename = 'data'
    plt.plot(data)
    plt.savefig('%s.png' % filename)
    plt.close()  # avoid "hold on" for the next plot
    ut.write_data_n1('%s.dat' % filename, data)
    # plt.show()
    
if __name__ == "__main__":
    sr570_port = 'COM6'
    if sys.argv[1] == 'main':
        # Example: python lfn_ni.py main
        # To run the main routine
        bias_lst = [100, 200, 400, 800]
        for ii in range(len(bias_lst)):
            sr570_write('BSLV %d' % bias_lst[ii], sr570_port)   # set bias level
            sr570_write('BSON 1', sr570_port)     # turn on bias
            time.sleep(1)          # stabilize
            usb6211_get('V%d_Vbias%d' % (ii, bias_lst[ii]))              # record data
            sr570_write('BSON 0', sr570_port)   # turn off bias
    elif sys.argv[1] == 'sr570':
        # Example: python lfn_ni.py sr570
        # To issue a command to SR570
        sr570_write(sys.argv[2], sr570_port)
    elif sys.argv[1] == 'usb6211':
        # Example: python lfn_ni.py usb6211
        # To take a voltage analog input measurement with USB6211
        usb6211_get('data')
    

