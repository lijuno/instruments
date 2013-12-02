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

if __name__ == "__main__":
    usage_str = 'Usage: python transient.py -a T300K'
    args = sys.argv[1:]
    try:
        opts, args = getopt.getopt(args, "ha:", ['help'])
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
            
    
    a = i9s.agilent81004B(7)
    a.initialize()
    #a.reset()
    
    a.set_triggering(source=3, slope=1, level=0.5, sweep=1)
    a.set_timerange(50e-3)
    a.set_yrange(source=4, yrange=2)
    a.set_average(count=8, status=1)
    t = a.get_timeaxis()
    filename = 'V_%s.dat' % notes_str
    
    y2 = 0
    a.record_data(4, mtime = 10)
    y = a.get_ydata(4)
    y2 = y2 + np.array(y)
    #print len(y2)
    
    ut.write_data_n2(filename, t, y2)
    plt.plot(y2)
    plt.show()
    a.close()
    
    