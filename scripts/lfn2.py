#!/usr/bin/env python
"""
"""

import i9s
import misc
from lfn_ni import lfn_config_parser
import utilib as ut
import sys
import getopt
import time
import matplotlib.pyplot as plt
import numpy as np

    
if __name__=='__main__':
    if len(sys.argv) == 1:
        print "No input options!"
    elif sys.argv[1].lower() == 'bias_cal':
        config_filename = sys.argv[2]
        # Calibration the bias of SR570 with Keithley2400
        keithley = i9s.KeithleySMU(24, '6430')
        sr570 = misc.SR570('COM3')
        config_list = lfn_config_parser(config_filename)
        sr570_bias_list = []
        for cfg in config_list:
            sr570_bias_list.extend(cfg['bias_list'])

        vlist = []
        keithley.initialize()
        sr570.write('SENS 27')  # set to the lowest gain to protect the output
        for bias in sr570_bias_list:
            sr570.write('BSLV %d' % bias)
            sr570.write('BSON 1')
            vlist.extend(keithley.sm(0, 'current', compliance=5, nplc=1, delay=0.5))
        sr570.write('BSON 0')
        keithley.close()
        print vlist