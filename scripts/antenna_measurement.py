#!/usr/bin/env python

import i9s
import time
import numpy as np
import utilib as ut

if __name__ == "__main__":
    rs = i9s.RSFSU(20)  # spectrum analyzer
    rs.initialize()
    tc = i9s.LDT5910B(1)  # temperature controller
    tc.initialize()
    pm = i9s.AgilentE4418B(17)  # power meter
    pm.initialize()

    T_list = np.arange(12.4, 12.46, 0.02)
    freq = range(len(T_list))
    power = range(len(T_list))

    for ii in range(len(T_list)):
        tc_delay = 5  # stabilization delay for the temperature controller
        tc.set_temperature(T_list[ii])
        time.sleep(5)
        rs.single_sweep(50, 10, 0.1)
        freq[ii] = rs.detect_peak()[0]
        print "Peak frequency = %f GHz" % freq[ii]
        power[ii] = pm.measure(freq[ii]/1e9)
        print "Read power = %.2f" % power[ii]

    ut.write_data_n2('power.txt', freq, power, ftype='ff')

    rs.close()
    tc.close()
    pm.close()