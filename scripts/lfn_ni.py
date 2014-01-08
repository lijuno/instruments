"""
This is done under Windows 7 
"""

import ni
from misc import sr570_write
import matplotlib.pyplot as plt
import numpy as np
import utilib as ut
import time
import sys
import os


def usb6211_get(filename='', voltage_limit=0.2, duration=5):
    # duration: measurement duration, in s
    channel = 'Dev1/ai6'
    sampling_freq = 5e4
    sampling_pts = sampling_freq * duration
    daq = ni.USB6211()
    data = daq.get_voltage_ai(channel=channel, voltage_limit=voltage_limit, sampling_freq=sampling_freq,
                              sampling_pts=sampling_pts, input_mode='diff')

    fn = os.path.splitext(filename)[0]   # fn is the filename string without extension name
    if fn == '':
        fn = 'data'
    if sampling_pts >= 1e4:
        # down sampling the data for plot
        down_sampling_factor = 1e4/sampling_pts
        data_plot = ut.down_sampling(data, down_sampling_factor)
    else:
        data_plot = data
    t = np.linspace(0, duration, len(data_plot))
    plt.plot(t, data_plot)
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (V)')
    plt.savefig('%s.png' % fn)
    plt.close()  # avoid "hold on" to the next plot
    ut.write_data_n1(filename, data)


def ac(bias_list, param_suffix):
    # LFN measurement with bandpass filter
    # Input: bias_list: an int array containing bias levels of SR570
    #        param_suffix: a string representing other parameters as part of the file name
    # The saved data files should have names like "Vbias600_gain1e6.dat" where "gain_1e6" is given by param_suffix
    sr570_write('FLTT 2', sr570_port)   # 6 dB bandpass filter
    sr570_write('LFRQ 11', sr570_port)   # 10kHz upper bound
    sr570_write('HFRQ 2', sr570_port)   # 0.3Hz lower bound
    recording_time = 10    # unit: s
    print "Start AC measurement"
    for ii in range(len(bias_list)):
        sr570_write('BSLV %d' % bias_list[ii], sr570_port)   # set bias level
        sr570_write('BSON 1', sr570_port)     # turn on bias
        time.sleep(12)          # stabilize
        print 'Start recording AC-coupled data'
        usb6211_get('Vbias%d_%s.dat' % (bias_list[ii], param_suffix), voltage_limit=0.2, duration=recording_time)    # record data
        sr570_write('BSON 0', sr570_port)   # turn off bias


def dc(bias_list, param_suffix):
    # DC coupled measurement
    # Input: bias_list: an int array containing bias levels of SR570
    #        param_suffix: a string representing other parameters as part of the file name
    # The saved data files should have names like "Vbias600_DC_gain1e6.dat" where "gain_1e6" is given by param_suffix
    sr570_write('FLTT 3', sr570_port)   # 6 dB lowpass filter
    sr570_write('LFRQ 11', sr570_port)  # 10kHz lower bound
    recording_time = 2
    print "Start DC measurement"
    for ii in range(len(bias_list)):
        sr570_write('BSLV %d' % bias_list[ii], sr570_port)   # set bias level
        sr570_write('BSON 1', sr570_port)     # turn on bias
        time.sleep(5)
        print "Start recording DC-coupled data"
        usb6211_get('Vbias%d_DC_%s.dat' % (bias_list[ii], param_suffix), voltage_limit=5, duration=recording_time)
        sr570_write('BSON 0', sr570_port)   # turn off bias


if __name__ == "__main__":
    sr570_port = 'COM6'
    #bias_lst = [100, 200, 300]
    bias_lst = [-800]
    #bias_lst = [-1200, -600, -300, 100, 200, 300]
    #bias_lst = [500, 600, 750]
    #bias_lst = [-400, -200, -100, 100, 200, 300]
    if sys.argv[1] == 'main':
        dc(bias_lst, sys.argv[2])
        time.sleep(1)
        ac(bias_lst, sys.argv[2])

    if sys.argv[1] == 'ac':
        # Example: python lfn_ni.py main
        # To run the main routine
        ac(bias_lst, sys.argv[2])

    elif sys.argv[1] == 'dc':
        dc(bias_lst, sys.argv[2])

    elif sys.argv[1] == 'sr570':
        # Example: python lfn_ni.py sr570
        # To issue a command to SR570
        sr570_write(sys.argv[2], sr570_port)
    elif sys.argv[1] == 'usb6211':
        # Example: python lfn_ni.py usb6211
        # To take a voltage analog input measurement with USB6211
        usb6211_get('data')