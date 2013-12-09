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

def p1(argv):
    usage_str = 'Usage: python transient.py p1 -a T300K'
    try:
        opts, args = getopt.getopt(argv, "ha:", ['help'])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)
        sys.exit(2)
    
    notes_str = ''
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print usage_str
            sys.exit()
        elif opt == '-a':
            notes_str = str(arg)
            
    
    a = i9s.Agilent81004B(7)
    a.initialize()
    #a.reset()
    
    pulse_period = 100e-3 # the input pulse period in s, also the recording length
    average_count = 16
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
    a.config_average(count=average_count, status=1)
    time.sleep(average_count * pulse_period * 2.5)
    
    t = a.get_timeaxis()
    filename = 'V_%s.dat' % notes_str
    
    y4 = 0
    y3 = 0
    # a.record_data(4, mtime = 10)
    y = a.get_ydata(4)
    y4 = y4 + np.array(y) - a.src4_gnd
    y = a.get_ydata(3)
    y3 = y3 + np.array(y) - a.src3_gnd
    #print len(y2)
    a.close()  
    
    ut.write_data_n3(filename, t, y4, y3)
    plot_on = 1
    if plot_on:     
        plt.semilogx(y4)
        plt.semilogx(y3)
        plt.show()
 
    
if __name__ == "__main__":
    usage_str = 'Usage: python transient.py p1 -a T300K'
    if sys.argv[1] == 'p1':
        p1(sys.argv[2:])
    else:
        raise ValueError('Unrecognized argument')
    
    
    