#!/usr/bin/env python

"""
Measure the transient signal with Agilent infiniium DSO81004B oscilloscope
"""

import i9s 
import matplotlib.pyplot as plt
import numpy as np
import time
import sys
import getopt
import utilib as ut

def config(argv):
    """
    Configure the oscilloscope before measurement
    Usage: python transient.py config -t 100e-3 --average-count 16
    options: -t: pulse width, in s
    """
    usage_str = 'Usage: python transient.py config -t 100e-3 --average-count 16 -s 1e6'
    try:
        opts, args = getopt.getopt(argv, "ht:a:s:", ['help', 'pulse-width=', 'average-count=', 'sampling-rate'])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)
        sys.exit(2)

    pulse_period = 100e-3   # default value for pulse width, in s
    average_count = 0
    srate = 0
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print usage_str
            sys.exit()
        elif opt in ('-t', "--pulse-width"):
            pulse_period = float(arg)
        elif opt in ('-a', "--average-count"):
            average_count = int(arg)
        elif opt in ('-s', '--sampling-rate'):
            srate = float(arg)
        else:
            raise ValueError("Unrecognized option %s" % arg)

    a = i9s.Agilent81004B(7)
    a.initialize()
    #a.reset()

    # Configure triggering:
    #    * triggering source: Channel 3
    #    * triggering level: 0.5V
    #    * sweep mode: triggered
    #    * y range: 2V
    a.config_triggering(source=3, slope=1, level=0.5, sweep=1)
    a.set_yrange(source=3, yrange=2)

    # Configure signal source
    a.set_timerange(pulse_period)
    a.set_yrange(source=4, yrange=1)

    # Configure averaging
    if average_count != 0:
        a.config_average(count=average_count, status=1)
    if srate != 0:
        a.set_srate(srate)
    a.close()

def data(filename):
    """
    Get traces from oscilloscope
    Usage: python transient.py data filename
    """
    a = i9s.Agilent81004B(7)
    a.initialize()

    t = a.get_timeaxis()
    filename = '%s.dat' % filename

    y4 = 0
    y3 = 0
    y = a.get_ydata(4)
    y4 = y4 + np.array(y) - a.src4_gnd
    y = a.get_ydata(3)
    y3 = y3 + np.array(y) - a.src3_gnd
    a.close()

    ut.write_data_n3(filename, t, y4, y3)
    plot_on = 1
    if plot_on:
        plt.semilogx(y4)
        plt.semilogx(y3)
        plt.show()

def timeshift(argv):
    usage_str = 'Usage: python transient.py timeshift -i 300K -o 300K_out'
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ['help', 'infile=', 'outfile='])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)
        sys.exit(2)

    outfile = ''
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print usage_str
            sys.exit()
        elif opt in ('-i', '--infile'):
            infile = str(arg)
        elif opt in ('-o', '--outfile'):
            outfile = str(arg)

    ut.osc_time_shift(infile=infile, outfile=outfile)

def config1():
    config(['-a', '10', '-t', '4', '-s', '50e3'])

def config2():
    config(['-a', '10', '-t', '100e-3', '-s', '1e6'])

if __name__ == "__main__":
    usage_str = 'Usage: python transient.py config/data/timeshift/rtd'
    if sys.argv[1] == 'config':
        config(sys.argv[2:])
    elif sys.argv[1] == 'data':
        data(sys.argv[2])
    elif sys.argv[1] == 'timeshift':
        timeshift(sys.argv[2:])
    elif sys.argv[1] == 'rtd':
        print '%.1f K' % ut.rtd(float(sys.argv[2]))
    elif sys.argv[1] == 'config_long_time':
        config1()
    elif sys.argv[1] == 'config_short_time':
        config2()
    else:
        raise ValueError('Unrecognized argument')
    
