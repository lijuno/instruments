"""
This is done under Windows 7 
"""

import ni
import misc
import matplotlib.pyplot as plt
import numpy as np
import utilib as ut
import time
import sys
import os
import re
import ConfigParser


def usb6211_get(filename='', **kwargs):
    # Default values below
    channel='Dev1/ai6'  #  default channel
    voltage_limit = 0.2   # default voltage limit, unit: V
    duration = 1   # default recording time, unit: s
    sampling_freq = 50e3  # default sampling frequency, 10kHz

    for key, value in kwargs.iteritems():
        if key.lower() == 'channel':
            channel == value
        elif key.lower() == 'voltage_limit':
            voltage_limit = value
        elif key.lower() == 'duration':
            duration = value
        elif key.lower() == 'sampling_freq':
            sampling_freq = value
        else:
            raise ValueError("Unrecognized input parameter '%s'" % key)

    sampling_pts = sampling_freq * duration
    daq = ni.USB6211()
    data = daq.get_voltage_ai(channel=channel, voltage_limit=voltage_limit, clock_freq=sampling_freq,
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


def sweep_ac(bias_list, param_suffix, **kwargs):
    # LFN measurement with bandpass filter
    # Input: bias_list: an int array containing bias levels of SR570
    #        param_suffix: a string representing other parameters as part of the file name
    #        (optional) voltage_limit: the voltage range for the input signal
    # The saved data files should have names like "Vbias600_gain1e6.dat" where "gain_1e6" is given by param_suffix

    # Use the global sr570 object defined in the outer space
    channel = 'Dev1/ai6'
    voltage_limit = 0.2   # default voltage limit, unit: V
    recording_time = 1   # default recording time, unit: s
    sampling_freq = 10e3  # default sampling frequency, 10kHz
    freq_lb_arg = 2    # Command arg for frequency lower bound, default 0.3Hz
    freq_ub_arg = 11   # Command arg for frequency upper bound, default 10 kHz

    for key, value in kwargs.iteritems():
        if key.lower() == 'voltage_limit':
            voltage_limit = value
        elif key.lower() == 'channel':
            channel = value
        elif key.lower() == 'recording_time':
            recording_time = value
        elif key.lower() == 'sampling_freq':
            sampling_freq = value
        elif key.lower() == 'freq_lb_arg':
            freq_lb_arg_list = value
        elif key.lower() == 'freq_ub_arg':
            freq_ub_arg_list = value
        else:
            raise ValueError("Unrecognized input parameter '%s'" % key)
    sr570.write('FLTT 2')   # 6 dB bandpass filter
    sr570.write('LFRQ %d' % freq_ub_arg)   # frequency upper bound (the bandwidth of low-pass filter)
    sr570.write('HFRQ %d' % freq_lb_arg)   # frequency lower bound (the bandwidth of high-pass filter)

    sr570.write('BSLV %d' % bias_list[0])   # set initial bias level
    sr570.write('BSON 1')     # turn on bias
    print 'Bias on'

    for ii in range(len(bias_list)):
        sr570.write('BSLV %d' % bias_list[ii])   # set bias level
        time.sleep(100)          # stabilize
        print 'Start recording AC-coupled data \nSR570 bias level = %d, fs=%.0f Hz' % (bias_list[ii], sampling_freq)
        usb6211_get('Vbias%d_%s.dat' % (bias_list[ii], param_suffix),
                    channel=channel,   # channel name is a global variable
                    voltage_limit=voltage_limit,
                    duration=recording_time,
                    sampling_freq=sampling_freq)    # record data
    sr570.write('BSON 0')   # turn off bias


def sweep_ac2(bias_list, param_suffix, **kwargs):
    # LFN measurement with bandpass filter
    # Input: bias_list: an int array containing bias levels of SR570
    #        param_suffix: a string representing other parameters as part of the file name
    #        (optional) voltage_limit: the voltage range for the input signal
    # The saved data files should have names like "Vbias600_gain1e6.dat" where "gain_1e6" is given by param_suffix

    # Use the global sr570 object defined in the outer space
    channel = 'Dev1/ai6'
    voltage_limit = 0.2   # default voltage limit, unit: V
    recording_time_list = [0.1, 10]   # default recording time, 0.1s, 10s
    sampling_freq_list = [50e3, 1e3]  # default sampling frequency, 50kHz, 1kHz
    freq_lb_arg_list = [2, 2]   # Command arg for frequency lower bound, default 0.3Hz, 0.3Hz
    freq_ub_arg_list = [11, 8]   # Command arg for frequency upper bound, default 10 kHz, 300Hz

    for key, value in kwargs.iteritems():
        if key.lower() == 'voltage_limit':
            voltage_limit = value
        elif key.lower() == 'channel':
            channel = value
        elif key.lower() == 'recording_time_list':
            recording_time_list = value
        elif key.lower() == 'sampling_freq_list':
            sampling_freq_list = value
        elif key.lower() == 'freq_lb_arg_list':
            freq_lb_arg_list = value
        elif key.lower() == 'freq_ub_arg_list':
            freq_ub_arg_list = value
        else:
            raise ValueError("Unrecognized input parameter '%s'" % key)

    sr570.write('FLTT 2')   # 6 dB bandpass filter

    sr570.write('BSLV %d' % bias_list[0])   # set initial bias level
    sr570.write('BSON 1')     # turn on bias
    print 'Bias on'

    for ii in range(len(bias_list)):
        sr570.write('BSLV %d' % bias_list[ii])   # set bias level
        time.sleep(10)          # stabilize
        for jj in range(len(recording_time_list)):
            sr570.write('LFRQ %d' % freq_ub_arg_list[jj])   # frequency upper bound (the bandwidth of low-pass filter)
            sr570.write('HFRQ %d' % freq_lb_arg_list[jj])   # frequency lower bound (the bandwidth of high-pass filter)

            print 'Start recording AC-coupled data \nSR570 bias level = %d, fs=%.0f Hz, recording_time=%.1f s, jj=%d' % (bias_list[ii], sampling_freq_list[jj], recording_time_list[jj], jj)
            usb6211_get('Vbias%d_%s_%d.dat' % (bias_list[ii], param_suffix, jj),
                        channel=channel,
                        voltage_limit=voltage_limit,
                        duration=recording_time_list[jj],
                        sampling_freq=sampling_freq_list[jj])    # record data
    sr570.write('BSON 0')   # turn off bias

def dc(bias_list, param_suffix):
    # DC coupled measurement
    # Input: bias_list: an int array containing bias levels of SR570
    #        param_suffix: a string representing other parameters as part of the file name
    # The saved data files should have names like "Vbias600_DC_gain1e6.dat" where "gain_1e6" is given by param_suffix
    sr570.write('FLTT 3')   # 6 dB lowpass filter
    sr570.write('LFRQ 11')  # 10kHz lower bound
    recording_time = 10
    print "Start DC measurement"
    for ii in range(len(bias_list)):
        sr570.write('BSLV %d' % bias_list[ii])   # set bias level
        sr570.write('BSON 1')     # turn on bias
        time.sleep(5)
        print "Start recording DC-coupled data"
        usb6211_get('Vbias%d_DC_%s.dat' % (bias_list[ii], param_suffix), voltage_limit=5, duration=recording_time)
        sr570.write('BSON 0')   # turn off bias


def lfn_config_parser(config_filename):
    """
    Return an array containing the LFN measurement parameters. The array looks like [{xx}, {xx}], with  format of each
    array element (an dictionary) like this:
        {gain, SR570_sens_cmd_arg, bias_list}
    The returned list should be something like
        [{'gain': 5e8, 'sr570_sens_cmd_arg': 15, 'bias_list': [-2000, -1800, -1600]},
         {'gain': 5e7, 'sr570_sens_cmd_arg': 18, 'bias_list': [100, 200, 300]}]
    The format of config_file
    """
    cfg = ConfigParser.ConfigParser()
    cfg.read(config_filename)
    sections = cfg.sections()
    cfg_list = []
    for sect in sections:
        post_amp_gain = float(cfg.get(sect, 'post_amp_gain'))
        sr570_gain = float(cfg.get(sect, 'sr570_gain'))
        # sr570_sens_cmd_arg = int(cfg.get(sect, 'sr570_sens_cmd_arg'))
        voltage_limit = float(cfg.get(sect, 'voltage_limit'))
        #freq_lb_arg = int(cfg.get(sect, 'freq_lb_arg'))  # Command arg for frequency lower bound, refer to SR570 manual
        #freq_ub_arg = int(cfg.get(sect, 'freq_ub_arg'))  # Command arg for frequency higher bound, refer to SR570 manual
        bias_list_str = cfg.get(sect, 'bias_list').split()
        bias_list = [int(s) for s in bias_list_str]

        # Generate dictionary
        cfg_dict = {}
        cfg_dict.update({'post_amp_gain': post_amp_gain})
        cfg_dict.update({'sr570_gain': sr570_gain})
        # cfg_dict.update({'sr570_sens_cmd_arg': sr570_sens_cmd_arg})
        cfg_dict.update({'bias_list': bias_list})
        cfg_dict.update({'voltage_limit': voltage_limit})
        #cfg_dict.update({'freq_lb_arg': freq_lb_arg})
        #cfg_dict.update({'freq_ub_arg': freq_ub_arg})

        # Append to cfg_list
        cfg_list.append(cfg_dict)
    return cfg_list


if __name__ == "__main__":
    sr570_port = 'COM7'
    sr570 = misc.SR570(sr570_port)
    usb6211_channel = 'Dev1/ai6'
    if sys.argv[1] == 'main':
        # Example: python lfn_ni.py main lfn1.cfg lfn2.cfg ...
        for config_filename in sys.argv[2:]:
            config_list = lfn_config_parser(config_filename)
            for cfg in config_list:
                post_amp_gain = cfg['post_amp_gain']
                sr570_gain = cfg['sr570_gain']
                sr570_sens_cmd_arg = sr570.sensitivity_mapping(1/sr570_gain, direction='n2c')
                #sr570_sens_cmd_arg = cfg['sr570_sens_cmd_arg']
                bias_list = cfg['bias_list']
                voltage_limit = cfg['voltage_limit']
                gain = sr570_gain * post_amp_gain
                gain_str = re.sub('\+', '', 'gain%.1e' % gain)  # remove '+' in the string
                sr570.write('SENS %d' % sr570_sens_cmd_arg)  # set gain
                sweep_ac(bias_list, gain_str,
                                channel=usb6211_channel,
                                voltage_limit=voltage_limit,
                                recording_time=10,
                                sampling_freq=50e3)
                #sweep_ac2(bias_list, gain_str, channel=usb6211_channel, voltage_limit=voltage_limit)

    elif sys.argv[1].lower() == 'sr570':
        # Example: python lfn_ni.py sr570
        # To issue a command to SR570
        # misc.sr570_write(sys.argv[2], sr570_port)
        sr570.write(sys.argv[2])
    elif sys.argv[1].lower() == 'usb6211':
        # Example: python lfn_ni.py usb6211
        # To take a voltage analog input measurement with USB6211
        usb6211_get('data.dat', channel='Dev1/ai6', voltage_limit=0.5, duration=10, sampling_freq=50e3)
    elif sys.argv[1].lower() == 'multiple':
        # Repeat the measurement for several times
        N = 4
        t_interval = 10   # measurement interval, unit: s
        time.sleep(5)  # stabilize
        for ii in range(N):
            time.sleep(t_interval) 
            usb6211_get('data%d.dat' % ii, channel='Dev1/ai6', voltage_limit=0.5, duration=10, sampling_freq=50e3)            
    elif sys.argv[1].lower() == "iv":
        # Example: python lfn_ni.py iv dev1
        # Merge IV characteristics
        ut.iv_merger(sys.argv[2])
