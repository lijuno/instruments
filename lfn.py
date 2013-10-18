#!/usr/bin/env python
"""
Test script for low-frequency noise experiment
"""

import i9s 
import sys
import getopt
import time
import matplotlib.pyplot as plt
import numpy as np

    
if __name__=='__main__':
    if len(sys.argv) == 1:
        print "No input options!"
    elif sys.argv[1] == 'k2400c':
        # IV sweep with Keithley 2400C
        
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
        vlist = np.linspace(0.4, 1, 41)
        ilist = k.IV_sweep(vlist, fourwire=False)
        print ilist
        k.close()
        plt.semilogy(vlist, np.array(ilist))
        plt.xlabel('Voltage (V)')
        plt.ylabel('Current (A)')
        plt.savefig('IV.png')
        i9s.write_data_n2('IV.dat', vlist, ilist)
        
    elif sys.argv[1] == 'hp3582a':
        # Read the FFT trace from HP3582A 
        # Input argument "-u" sets the upper limit frequency 
        
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
        print "Frequency upper bound = %d Hz" % freq_ub
        
        hp = i9s.hp3582a(11)
        hp.initialize()
        spectrum_data = hp.get_spectrum()  # in dB
        hp.close()
        
        # Plotting
        # First find the resolution bandwidth by scaling it against 1kHz
        # At frequency upper bound == 1kHz, the integration bandwidth == 4Hz
        res_bw = freq_ub/1e3 * 4
        freq_axis = np.linspace(0, freq_ub, 256)  # 256 points for single trace in single channel mode
        y_power = 10**(np.array(spectrum_data)/10)  # unit: V^2
        y_power_density = y_power / res_bw
        plt.loglog(freq_axis, y_power)
        plt.xlabel('Freuqency (Hz)')
        plt.ylabel('FFT spectrum (V^2)')
        plt.savefig('FFT_spectrum.png')
        i9s.write_data_n3('fft_spectrum.dat', freq_axis, y_power, y_power_density)
    
    elif sys.argv[1] == 'sr810':
        sr = i9s.sr810(10)
        sr.initialize()
        sr.set_input_source('I1')
        sr.set_display_mode('xn')  # measure noise
        sr.set_time_constant(300e-3)
        
        freq_lb = 4    # Frequency lower bound
        freq_ub = 100  # Frequency upper bound
        pts = 10       # number of data points along frequency axis
        
        # Sample in logspace
        freq_list = np.logspace(np.log10(freq_lb), np.log10(freq_ub), pts)
        # Need to notch out the 60Hz harmonics points
        
        xn_list = np.zeros(len(freq_list))
        
        for ii in range(len(freq_list)):
            sr.set_frequency(freq_list[ii])
            print "Setting frequency to %0.1f" % freq_list[ii]
            if ii == 0: 
                # Since this is a 1/f measurement, I assume that the noise in lower frequency 
                # is higher than that in higher frequency. So only h
                sr.exec_auto('gain')
                time.sleep(5)
            time.sleep(2)
            sr.exec_auto('reserve')
            
            # Now enter a sensitivity adjustment loop till the output stablizes in some level
            poll_pts = 15
            poll_step = 1
            mean_over_sens_threshold = 0.1
            std_over_sens_threshold = 0.01
            # The above four parameters are for the 300ms time constant setting
            
            # Initialize
            mean, std = sr.poll_ch1(poll_pts, poll_step)
            sens = sr.get_sensitivity('current')
            
            tstart = time.time()
            while (1):
                if mean/sens < mean_over_sens_threshold:
                    # Value too small
                    i = sr.get_sensitivity_c()
                    if i == 0: 
                        print "Sensitivity limit reached"
                    else: 
                        # Enhance the sensitivity to the next level
                        # (Or reduce the range to the next level)
                        sr.set_sensitivity_c(i-1)
                        time.sleep(3)
                        sr.exec_auto('reserve')
                        mean, std = sr.poll_ch1(poll_pts, poll_step)
                        sens = sr.get_sensitivity('current')
                        
                elif std/sens > std_over_sens_threshold:
                    # Data not stable enough
                    # Continue the poll    
                    mean, std = sr.poll_ch1(poll_pts, poll_step)
                    sens = sr.get_sensitivity('current')
                    
                else:
                    xn_list[ii] = mean
                    break
                print 'mean/sens = %f'  % (mean/sens) 
                print 'std/mean = %f'  % (std/mean)
            
            tstop = time.time()            
            print 'Frequency = %.2f Hz, elapsed time = %.2f s, Xn = %e' % (freq_list[ii], tstop-tstart, xn_list[ii])
            
        sr.close()
        
        # Saveing and plotting
        i9s.write_data_n2('Xn.dat', freq_list, xn_list)
        
    else:
        print 'Unrecognized input arguments!'
        
        