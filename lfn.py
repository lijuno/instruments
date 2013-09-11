#!/usr/bin/env python
"""
Test script for low-frequency noise experiment
"""

import i9s 
import sys
import getopt
import matplotlib.pyplot as plt
import numpy as np

    
if __name__=='__main__':
    if len(sys.argv) == 1:
        print "No input options!"
    elif sys.argv[1] == 'k2400c':
        usage_str = 'Usage: python lfn.py k2400c'
        args = sys.argv[2:]
        try:
            opts, args = getopt.getopt(args, "h", ['help'])
        except getopt.GetoptError as err:
            # print help information and exit:
            print str(err)
            sys.exit(2)
        
        k = i9s.keithley2400c(24)
        k.initialize()
        vlist = np.linspace(0, 2, 41)
        ilist = k.IV_sweep(vlist, fourwire=False)
        print ilist
        k.close()
        plt.semilogy(vlist, np.array(ilist))
        plt.xlabel('Voltage (V)')
        plt.ylabel('Current (A)')
        plt.savefig('IV.png')
        i9s.write_data_2d('IV.dat', vlist, ilist)
    elif sys.argv[1] == 'hp3582a':
        usage_str = 'Usage: python lfn.py hp3582a -u 1000'
        args = sys.argv[2:]
        try:
            opts, args = getopt.getopt(args, "hu:", ['help'])
        except getopt.GetoptError as err:
            # print help information and exit:
            print str(err)
            sys.exit(2)
        
        freq_ub = 1000  # default frequency upper bound
        for o, a in opts:
            if o in ("-h", "--help"):
                print usage_str
                sys.exit()
            elif o == '-u':
                freq_ub = int(a)
        print "Frequency upper bound = %d" % freq_ub
        
        hp = i9s.hp3582a(11)
        hp.initialize()
        spectrum_data = hp.get_spectrum()
        hp.close()
        
        # Plotting
        freq_axis = np.linspace(0, freq_ub, 256)  # 256 points for single trace in single channel mode
        plt.semilogx(freq_axis, spectrum_data)
        plt.xlabel('Freuqency (Hz)')
        plt.ylabel('FFT spectrum (dBV)')
        plt.savefig('FFT_spectrum.png')
        i9s.write_data_2d('fft_spectrum.dat', freq_axis, spectrum_data)
    else:
        print 'Unrecognized input arguments!'
        
        