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
    if sys.argv[1] == 'k2400c':
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
        hp = i9s.hp3582a(11)
        hp.initialize()
        spectrum_data = hp.get_spectrum()
        hp.close()
        
        plt.semilogx(spectrum_data)
        plt.savefig('FFT_spectrum.png')
        i9s.write_data_1d('spectrum.dat', spectrum_data)
    else:
        print 'Do nothing'
        
        