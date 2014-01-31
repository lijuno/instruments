"""
Instrument classes
"""

import sys
if 'linux' in sys.platform:
    from linuxgpib import ib_dev
elif 'win' in sys.platform:
    from win_pyvisa import ib_dev
else:
    print "Unrecognized OS!"
    sys.exit()

import utilib as ut
import time
import numpy as np
from scipy import stats


class HP3582A(ib_dev):
    """
    HP3582A FFT spectrum analyzer
    The memory wordsize is 16 bit, or 2 bytes
    The HPIB read byte size must match the requested byte size, or there will be errors
    """

    def __init__(self, port=11):
        """
        For HP3582A, the default HP-IB address is 11
        To change it, one needs to open up the top cover and configure the switches inside
        """
        ib_dev.__init__(self, port)

    def rest(self):
        time.sleep(1)

    def get_spectrum(self):
        """
        Get the spectrum data on the screen (only y axis data); return a float type array
        
        Note that the y data are the power in dB within a resolution bandwidth. So one needs 
        to divide y data by resolution bandwidth to get the power density. The resolution 
        bandwidth is 4Hz when frequency upper bound f_ub == 1kHz, and it scales with f_ub.
        """
        bytes_per_pt = 9
        pts = 256  # single trace in singla channel mode: 256 points
        bytes_separator = pts - 1  # how many '.'s in the string
        self.write('LDS')
        data = self.read(bytes_per_pt * pts + bytes_separator)
        # return an ascii string like '-2.47E+01,-2.52E+01'

        data_float = [float(d) for d in data.split(',')]
        return data_float  # return a float type array


class Keithley2400C(ib_dev):
    """
    Keithley 2400C sourcemeter
    """

    def __init__(self, port):
        print "Keithley 2400C sourcemeter"
        ib_dev.__init__(self, port)

    def initialize(self):
        ib_dev.initialize(self)
        self.write('*RST')
        self.write(':SENSe:AVERage ON')
        self.write(
            ':SENSe:FUNCtion:CONCurrent 0')  # disable the ability of measuring more than one function simultaneously
        self.write(':SOURce:DELay 0.5')
        self.write(':SOURce:CLEar:AUTO 0')
        self.write(':DISPLay:ENABle 1')
        self.write(':DISPLay:DIGits 6')
        self.write(':SYSTem:AZERo ON')

    def get_idn(self):
        return self.query('*IDN?')

    def set_current(self, I, V_compliance):
        pass

    def set_voltage(self, V, I_compliance):
        pass

    def on(self):
        self.write(':OUTPut:STATe ON')

    def off(self):
        self.write(':OUTPut:STATe OFF')

    def IV_sweep(self, vlist=None, fourwire=True):
        """
        IV sweep: source V, measure I 
        """
        vlist_str = ','.join([str(v) for v in vlist])
        print vlist_str
        vlist_pts = len(vlist)

        self.write(':SENSe:CURRent:NPLCycles 0.2') # set integration time
        self.write(':SENSe:CURRent:PROTection 1e-1') # current compliance, unit: A
        self.write(':SOURce:VOLTage:MODE LIST')
        self.write(':SOURce:VOLTage:RANGe 50')
        self.write(':SENSe:FUNCtion:ON "CURRent"')
        self.write(':SENSe:FUNCtion:OFF "VOLTage"')
        self.write(':FORMat:ELEMents CURRent')
        if fourwire:
            # If doing four-wire measurement
            self.write(':SYSTem:RSENse ON')
        self.write(':SOURce:LIST:VOLTage %s' % vlist_str)
        self.write(':TRIGger:COUNt %d' % vlist_pts)

        self.write(':OUTPut:STATe ON')
        self.write(':INITiate')
        self.write(':FETCh?')
        # Need to tweak the GPIB timeout to cater for different measurement time
        data_str = self.read(1024)
        self.write(':OUTPut:STATe OFF')

        data_int = [float(d) for d in data_str.split(',')]
        return data_int


class HP3314a(ib_dev):
    """
    HP3314A function generator, using HP-IB
    """

    def __init__(self, port=7):
        """
        For HP3314A, the default HP-IB address is 7
        To view the current HP-IB address: press blue button --> Lcl (Local)
        To change HP-IB address, press Rcl (Recall) and then Lcl --> uss knob to change the 
        port number --> press Sto (Store) and then Lcl 
        """
        print "HP3314A function generator"
        ib_dev.__init__(self, port)

    def initialize(self):
        ib_dev.initialize(self)


    def set_amplitude(self, ampl):
        """
        Input amplitude unit: V
        """
        if ampl >= 1:
            self.write('AP%0.2fVO' % ampl)
        elif ampl < 1:
            self.write('AP%0.2fMV' % (ampl * 1000.0))

    def set_frequency(self, freq):
        """
        Input frequency unit: Hz
        """
        if freq < 1e3:
            self.write('FR%0.2fHZ' % freq)
        elif (freq >= 1e3) and (freq < 1e6):
            self.write('FR%0.2fKZ' % (freq / 1e3))
        elif freq >= 1e6:
            self.write('FR%0.2fMZ' % (freq / 1e6))


class SR810(ib_dev):
    """
    SR810 DSP lock-in amplifier
    """

    def __init__(self, port=10):
        print "SR810 DSP lock-in amplifier"
        ib_dev.__init__(self, port)

    def initialize(self):
        ib_dev.initialize(self)

        # Set the SR810 to output responses to the GPIB port
        # The OUTX i command MUST be at the start of ANY SR810 program to direct responses to the interface in use
        self.write('OUTX1')

        ########################

    ## Helper functions
    def time_constant_mapping(self, tc):
        """
        Map the numerical time constant to the commmand line argument
        Return an int
        tc: unit s
        """
        # Normalize the time constant to 10us
        # tc*1.01 to avoid the precision problem during the float point operation
        # e.g., 1/1e-5 results in 99999.99999999999, which makes exponent == 4 and fsdigit == 9 below
        val = int(tc * 1.01 / 1e-5)

        # Now use an alogrithm to get the command line argument
        # Decompose the number val to fsdigit * 10** exponent
        exponent = int(np.floor(np.log10(val)))
        fsdigit = int(val / 10 ** exponent)   # the first significant digit
        if fsdigit * 10 ** exponent < 1 or fsdigit * 10 ** exponent > 3 * 10 ** 8:
            raise RuntimeError('Time constant out of range')

        if fsdigit == 1:
            a = 0
        elif fsdigit == 3:
            a = 1
        else:
            raise RuntimeError('Unrecognized time constant')

        i = a + 2 * exponent
        return i

    def sensitivity_mapping(self, sens, source_mode, direction='n2c'):
        """
        Map the numerical sensitivity to the commmand line argument
        Return an int for 'n2c', or a float for 'c2n'
        Input arg: 
            sens: sensitivity
              * when in 'n2c'(numerical to command line) mode: unit A or V, depending on source_mode
              * when in 'c2n' mode: unitless, just an int
        """
        if not (source_mode == 'voltage' or source_mode == 'current'):
            raise RuntimeError('Invalid source mode: should be either "current" or "voltage"')

        if direction == 'n2c': # Convert from numerical to command line argument
            # sens*1.01 to avoid the precision problem during the float point operation
            # e.g., 1/1e-5 results in 99999.99999999999, which makes exponent == 4 and fsdigit == 9 below
            if source_mode == 'current':
                # Normalize the value to 1fA
                val = int(sens * 1.01 / 1e-15)
            elif source_mode == 'voltage':
                # Normalize the value to 1nV
                val = int(sens * 1.01 / 1e-9)

            # Now use an alogrithm to get the command line argument
            # Decompose the number val to fsdigit * 10** exponent
            exponent = int(np.floor(np.log10(val)))
            fsdigit = int(val / 10 ** exponent)   # the first significant digit
            if fsdigit * 10 ** exponent > 10 ** 9 or fsdigit * 10 ** exponent < 2:
                raise RuntimeError('Sensitivity out of range')

            if fsdigit == 2:
                a = 0
            elif fsdigit == 5:
                a = 1
            elif fsdigit == 1:
                a = 2
                exponent = exponent - 1
            else:
                raise RuntimeError('Unrecognized sensitivity')

            i = a + exponent * 3
            return i

        elif direction == 'c2n':  # Convert from command line argument to numerical (unit: A or V)
            sens = int(sens)
            if sens < 0 or sens > 26:
                raise RuntimeError('Sensitivity out of range')

            # Do the reverse of "n2c" algorithm
            exponent = sens / 3
            a = sens % 3
            if a == 0:
                fsdigit = 2
            elif a == 1:
                fsdigit = 5
            elif a == 2:
                fsdigit = 1
                exponent = exponent + 1

            val = fsdigit * 10 ** exponent
            if source_mode == 'current':
                val = val / 1e15
            elif source_mode == 'voltage':
                val = val / 1e9

            return val

            ## End of helper functions

    #############################

    # Now begin instrument operation functions

    def set_reference_source(self, ref_src):
        # SR810 sets reference source to external by default
        if ref_src == 'external':
            self.write('FMOD0')
        elif ref_src == 'internal':
            self.write('FMOD1')
        else:
            raise RuntimeError('Unrecognized reference source string')

    def get_reference_source(self):
        fmod_str = self.query('FMOD?')
        if fmod_str[-1] == '\n':
            return int(fmod_str[:-1])
        else:
            return int(fmod_str)

    def set_input_source(self, input_src):
        if input_src == 'A' or input_src == 0:
            # Single ended voltage input
            self.write('ISRC0')
        elif input_src == 'AB' or input_src == 1:
            # Differential voltage input
            self.write('ISRC1')
        elif input_src == 'I1' or input_src == 2:
            # Current input, 1M Ohm
            self.write('ISRC2')
        elif input_src == 'I2' or input_src == 3:
            # Current input, 100M Ohm
            self.write('ISRC3')
        else:
            raise RuntimeError('Unrecognized input source')


    def set_frequency(self, freq):
        # Frequency unit: Hz
        if self.get_reference_source() == 0:
            print "External reference source; Frequency not changeabled"
        else:
            self.write('FREQ%.2f' % freq)

    def get_frequency(self):
        freq_str = self.query('FREQ?')
        if freq_str[-1] == '\n':
            return float(freq_str[:-1])
        else:
            return float(freq_str)

    def set_sensitivity(self, sens, source_mode):
        # sens: unit A or V
        # source_mode: 'current' or 'voltage'
        i = self.sensitivity_mapping(sens, source_mode, 'n2c')
        self.write('SENS%d' % i)
        print 'Sensitivity set to %e' % sens

    def get_sensitivity(self, source_mode):
        i = int(self.query('SENS?'))
        return self.sensitivity_mapping(i, source_mode, 'c2n')

    def set_sensitivity_c(self, i):
        """
        Set sensitivity with the command line argument rather than the real numerical value
        """
        self.write('SENS%d' % i)

    def get_sensitivity_c(self):
        """
        Get the command line argument of sensitivity rather than the real numerical value
        Return an int 
        """
        return int(self.query('SENS?'))

    def set_time_constant(self, tc):
        i = self.time_constant_mapping(tc)
        self.write('OFLT%d' % i)

    def get_time_constant(self):
        oflt_str = self.query('OFLT?')
        if oflt_str[-1] == '\n':
            return int(oflt_str[:-1])
        else:
            return int(oflt_str)

    def set_filter_order(self, order=4):
        if order == 1:
            i = 0  # 6 dB/oct
        elif order == 2:
            i = 1  # 12 dB/oct
        elif order == 3:
            i = 2   # 18 dB/oct
        elif order == 4:
            i = 3   # 24 dB/oct
        else:
            raise RuntimeError('Unrecognized filter order')

        self.write('OFSL%d' % i)

    def set_reserve(self, rsv_mode):
        if rsv_mode == 'high' or rsv_mode == 0:
            # High reserve
            self.write('RMOD0')
        elif rsv_mode == 'normal' or rsv_mode == 1:
            # normal
            self.write('RMOD1')
        elif rsv_mode == 'low' or rsv_mode == 2:
            # Low noise
            self.write('RMOD2')
        else:
            raise RuntimeError('Unrecognized reserve mode')

    def get_reserve(self):
        rsv_str = self.query('RMOD?')
        if rsv_str[-1] == '\n':
            return int(rsv_str[:-1])
        else:
            return int(rsv_str)

    def set_sync_filter(self, sf_status):
        if sf_status == 'on' or sf_status == 1:
            self.write('SYNC1')
        elif sf_status == 'off' or sf_status == 0:
            self.write('SYNC0')
        else:
            raise RuntimeError('Unrecognized sync filter status')

    def set_coupling_mode(self, coupling_mode):
        if coupling_mode == 'ac':
            self.write('ICPL0')
        elif coupling_mode == 'dc':
            self.write('ICPL1')
        else:
            raise RuntimeError('Unrecognized coupling mode')

    def set_grounding_mode(self, grounding_mode):
        if grounding_mode == 'float' or grounding_mode == 0:
            self.write('IGND0')
        elif grounding_mode == 'ground' or grounding_mode == 1:
            self.write('IGND1')
        else:
            raise RuntimeError('Unrecognized grounding mode')

    def set_display_mode(self, ch1, ratio='none'):
        if ch1 == 'x':
            ch1_mode = 0
        elif ch1 == 'r':
            ch1_mode = 1
        elif ch1 == 'xn':
            ch1_mode = 2
        elif ch1 == 'aux1':
            ch1_mode = 3
        elif ch1 == 'aux2':
            ch1_mode = 4
        else:
            raise RuntimeError('Unrecognized CH1')

        if ratio == 'none':
            ratio_mode = 0
        elif ratio == 'aux1':
            ratio_mode = 1
        elif ratio == 'aux2':
            ratio_mode = 2
        else:
            raise RuntimeError('Unrecognized ratio')

        self.write('DDEF%d,%d' % (ch1_mode, ratio_mode))

    def get_ch1(self):
        """
        Get CH1 display number
        Return a float 
        """
        return float(self.query('OUTR?'))

    def get_overload_status(self, info_type):
        """
        Query overload status 
        Return a Boolean
        """
        if info_type == 'input':
            bit = 0
        elif info_type == 'output':
            bit = 2
        elif info_type == 'filter':
            bit = 1
        else:
            raise RuntimeError('Unrecognized status type')
        ovl = int(self.query('LIAS?%d' % bit))
        if ovl:
            return True
        else:
            return False

    def exec_auto(self, auto_option):
        if auto_option == 'gain':
            # Auto gain
            print "Executing auto gain ..."
            self.write('AGAN')
        elif auto_option == 'reserve':
            # Auto reserve
            print "Executing auto reserve ..."
            self.write('ARSV')
        elif auto_option == 'phase':
            # Auto phase
            print "Executing auto phase ..."
            self.write('APHS')
        elif auto_option == 'offsetx':
            # Auto offset X
            print "Executing auto offset on X ..."
            self.write('AOFF1')
        elif auto_option == 'offsety':
            # Auto offset Y
            print "Executing auto offset on Y ..."
            self.write('AOFF2')
        elif auto_option == 'offsetr':
            # Auto offset R
            print "Executing auto offset on R ..."
            self.write('AOFF3')
        else:
            raise RuntimeError('Unrecognized auto functions')

    # Here are some utility functions useful in real measurements
    def poll_ch1(self, pts, time_step, verbose=True):
        """
        This function reads some number of CH1 data points with certain time intervals 
        under the current measurement condition, and calculate the mean and deviation
        
        Input args: 
            pts: number of CH1 data points, int type
            time_step: time interval between two adjacent sampling, float type, unit: s
        Return: (mean, standard_deviation, slope_from_linear_fit)
        """
        ch1_data = [0] * (int(pts))
        time_axis = range(int(pts))
        for ii in range(len(ch1_data)):
            ch1_data[ii] = self.get_ch1()
            ut.iprint("CH1 = %e" % ch1_data[ii], verbose)
            time_axis[ii] = time_axis[ii] * time_step
            time.sleep(time_step)
            #print time_axis
        #print ch1_data
        slope, intercept, r_value, p_value, std_err = stats.linregress(time_axis, ch1_data) # unit: V/s or A/s
        mean = np.array(ch1_data).mean()
        std = np.array(ch1_data).std()
        ut.iprint("Summary: %d points, mean = %e, std = %e, slope=%e" % (pts, mean, std, slope), verbose)
        return mean, std, slope

    def sensitivity_change(self, n):
        """
        Change the sensitivity up or down by n levels. There are 27 levels specified in
        the SR810 manual page 5-6. 
        Positive n means less sensitive; negative n means more sensitive. 
        Auto reserve is executed after the change. 
        """
        if not (type(n) is int):
            raise RuntimeError('Input n must be int type')

        i1 = self.get_sensitivity_c()   # current sensitivity
        i2 = i1 + n
        if i2 > 26 or i2 < 0:
            raise RuntimeError('Final sensitivity out of range. Make |n| smaller')

        self.set_sensitivity_c(i2)
        time.sleep(3)
        self.exec_auto('reserve')


class SR760(ib_dev):
    """
    SR760 FFT spectrum analyzer
    """

    def __init__(self, port=11):
        # The GPIB port can be set in the front panel: 
        # System setup --> GPIB --> GPIB address
        print "SR760 FFT spectrum analyzer"
        ib_dev.__init__(self, port)

    def initialize(self):
        ib_dev.initialize(self)

    # Helper functions
    def span_mapping(self, x, direction='c2n'):
        """
        Convert span from real value (in Hz) to command line number or vice versa
        'c2n': from command line number to real number in Hz
        'n2c': from real number in Hz to command line number
        """
        if direction.lower() == 'n2c':
            # Convert from real value in Hz to command line number
            # In this case x has unit Hz
            if x > 100e3 or x < 100e3 / 2.0 ** 19:
                raise RuntimeError('Input value out of range')
            else:
                c = 19 - np.log2(100e3 / x)
                return int(np.round(c))    # round to the nearest integer
        elif direction.lower() == 'c2n':
            if x > 19 or x < 0:
                raise RuntimeError('Input value out of range')
            else:
                return 100e3 / 2 ** (19 - x)
        else:
            raise RuntimeError('Invalid input arguments')

    # End of helper function

    def set_span(self, s, stype='c'):
        """
        set_frequency_span(self, s, stype='c');
        s: span;
        stype: 'c' for command line number, 'n' for real number in Hz
        """
        if stype.lower() == 'c':
            # Command line number
            self.write('SPAN%d' % s)
        elif stype.lower() == 'n':
            c = self.span_mapping(s, 'n2c')
            self.write('SPAN%d' % c)

    def get_span(self, stype='c'):
        # Get command line number
        c = int(self.query('SPAN?'))
        if stype.lower() == 'c':
            return c
        elif stype.lower() == 'n':
            # Get real frequency number in Hz
            return self.span_mapping(c, 'c2n')

    def set_frequency(self, f, ftype):
        """
        set_frequency(self, f, ftype); 
        f: frequency in Hz; ftype: 'start' or 'center'
        """
        if ftype.lower() == 'start':
            self.write('STRF%.3f' % f)
        elif ftype.lower() == 'center':
            self.write('CTRF%.3f' % f)
        else:
            raise RuntimeError('Invalid input ftype')

    def get_frequency(self, ftype):
        """
        get_frequency(self, ftype)
        ftype: 'start' or 'center'
        """
        if ftype.lower() == 'start':
            return float(self.query('STRF?'))
        elif ftype.lower() == 'center':
            return float(self.query('CTRF?'))
        else:
            raise RuntimeError('Invalid input ftype')

    def set_coupling(self, ctype):
        if ctype.lower() == 'ac':
            self.write('ICPL0')
        elif ctype.lower() == 'dc':
            self.write('ICPL1')
        else:
            raise RuntimeError('Wrong input coupling type')

    def exec_front_panel(self, task):
        """
        Execute front panel commands (like press the button)
        """
        if task.lower() == 'start':
            self.write('STRT')
        elif task.lower() == 'autoscale':
            self.write('AUTS')
        else:
            pass

    def get_status(self, stype):
        """
        get_status(self, stype);
        Get the status of SR760
        """
        pass

    def get_data(self):
        """
        get_data(self);
        Get spectrum data from SR760; return x- and y-axis values
        """
        data_pts = 400
        x = [0 for _ in range(data_pts)]
        y = [0 for _ in range(data_pts)]  # 400 data points are stored for the active trace
        for ii in range(data_pts):
            # The reason to use this for loop to read data rather than a single SPEC?0
            # command is that the latter is not stable enough yet for some reason...
            # For loop is slower, but at least it gives stable output
            x[ii] = float(self.query('BVAL?0,%d' % ii))
            y[ii] = float(self.query('SPEC?0,%d' % ii))
        return x, y

    # Here are some useful procedure in measurement
    def measure_full_span(self, span=None, filename_prefix=None, stype='c'):
        """
        Measure from the minimum frequency step to the full span and save the data
        """
        if stype.lower() == 'c':
            c = span
        elif stype.lower() == 'n':
            c = self.span_mapping(span, 'n2c')
        else:
            raise RuntimeError('Invalid span input')

        self.set_span(c)
        fspan = self.get_span('n')
        self.set_frequency(fspan / 400, 'start')  # set minimum start frequency
        self.exec_front_panel('start')   # start the measurement  
        time.sleep(30)  # waiting for the experiment; 30 s for 1500 linear averaging
        self.exec_front_panel('autoscale')
        x, y = self.get_data()   # fetch the data from SR760
        data_filename = '%s_%.0fHz.dat' % (filename_prefix, fspan)
        ut.write_data_n2(data_filename, x, y, ftype='ee')
        ut.plot_lfn_data(data_filename)
        return x, y


class Agilent81004B(ib_dev):
    """
    Agilent infiniium DSO81004B high-speed oscilloscope
    """

    def __init__(self, port=7):
        """
        The default GPIB address is 7, which can be changed via "Uilities" --> "GPIB Setup" on the screen
        """
        ib_dev.__init__(self, port)

    def initialize(self):
        ib_dev.initialize(self)
        self.write(":SYSTem:HEADer OFF")
        self.write(":TIMebase:REFerence LEFT")
        self.src4_gnd = 4.0e-3   # source 4 ground offset voltage in volt, an value averaged over 64 samples, var=5% under room temperature
        self.src3_gnd = 4.2e-3   # source 3 ground offset voltage in volt, an value averaged over 64 samples, var=5% under room temperature

    def reset(self):
        self.write("*RST")
        self.write(":SYSTem:HEADer OFF")
        self.write(":TIMebase:REFerence LEFT")

    #    def set_timescale(self, timescale):
    #        """
    #        Set the horizontal time per division in seconds; full range is ten times the division
    #        """
    #        self.write(':TIMebase:SCALe %e' % timescale)

    def set_timerange(self, timerange):
        """
        set_timerange(self, timerange)
        Set the horizontal time full range
        timerange: in s
        """
        self.write(':TIMebase:RANGe %e' % timerange)

    def set_yrange(self, source, yrange):
        """
        set_yrange(self, source, yrange)
        Set the vertical full range
        source: channel #
        yrange: in volts
        """
        self.write(':CHANnel%d:RANGe %e' % (source, yrange))

    def config_triggering(self, **kwargs):
        """
        config_triggering(self, **kwargs)
        Set up triggering
        kwargs options: 
            * source=x, an int: Channel x as triggering source
            * slope=x, an int: -1 for negative slope, 1 for positive slope, 0 for either
            * level=x, a float: triggering level
            * sweep = x, an int: sweep mode, 0 for AUTO, 1 for TRIGGEREd, 2 for SINGLE
        """
        for key, value in kwargs.iteritems():
            if key == "source":
                self.write(":TRIGger:EDGE:SOURce CHANnel%d" % int(value))
            elif key == "slope":
                if value == 1:
                    slope_str = 'POSitive'
                elif value == -1:
                    slope_str = "NEGative"
                elif value == 0:
                    slope_str = "EITHer"
                else:
                    raise ValueError('Unrecognized slope option')
                self.write(":TRIGger:EDGE:SLOPe %s" % slope_str)
            elif key == "sweep":
                if value == 0:
                    self.write(":TRIGger:SWEep AUTO")
                elif value == 1:
                    self.write(":TRIGger:SWEep TRIGgered")
                elif value == 2:
                    self.write(":TRIGger:SWEep SINGle")
                else:
                    ValueError("Unrecognized triggering sweep option")
            elif key == "level":
                pass  # postpone for later
            elif key == "coupling":
                pass
            else:
                raise ValueError("Unrecognized triggering option")

        # Run trigger level setting after the previous for loop because it is dependent on the trigger source
        for key, value in kwargs.iteritems():
            if key == "level":
                src_str = self.query(":TRIGger:EDGE:SOURce?")   # something like 'CHAN1'
                src = int(src_str[4])
                self.write(":TRIGger:LEVel CHANnel%d,%.2f" % (src, value))

    def config_average(self, **kwargs):
        """
        config_average(self, **kwargs)
        kwargs option:
            * count = x, an int: average count
            * status = x, an int: x =1 for ON, 0 for OFF
        """
        for key, value in kwargs.iteritems():
            if key == "count":
                self.write(":ACQuire:AVERage:COUNt %d" % value)
            elif key == "status":
                if value == 1:
                    self.write(":ACQuire:AVERage ON")
                elif value == 0:
                    self.write(":ACQuire:AVERage OFF")
                else:
                    raise ValueError("Unrecognized average status")

    def set_acquisition(self, **kwargs):
        """
        set_acquisition(self, **kwargs)
        Set up acquisition system
        kwargs options:
            * average = x, an int: x=1 for ON, 0 for OFF
            * average_count =x, an int: x is the number of averages
            * mode =x, an int: x =0 for real time (RTIMe), 1 for peak dection, 2 for high resolution
            * points =x, an int: number of sampling points
            * srate=x, a float: sampling rate
            * 
        """
        pass

    def set_srate(self, srate):
        self.write(':ACQuire:SRATe %e' % srate)

    def record_data(self, source, mtime=5):
        """
        record_data(self, source, mtime=5)
        source: acquisition channel, 
        mtime: measurement time, a delay before stopping the measurement
        """
        #        self.write(":DIGitize CHANnel%d" % source)
        #        self.write(":CHANnel%d:DISPlay ON" % source)
        self.write(":RUN")
        time.sleep(mtime)
        self.write(":STOP")

    def get_timeaxis(self):
        pts = int(self.query(":WAVeform:POINts?"))
        xinc = float(self.query(":WAVeform:XINCrement?"))
        xorg = float(self.query(":WAVeform:XORigin?"))
        t = [ii * xinc + xorg for ii in range(pts)]
        return t

    def get_ydata(self, source, mode='ascii'):
        if mode.lower() == "word":
            # For some reason, in WORD mode, some part of the obtained y data are not correct
            # Need to fix it in the future
            # For now, use ASCII mode, which is slower but works
            pts = int(self.query(":WAVeform:POINts?"))
            self.write(':WAVeform:SOURce CHANnel%d' % int(source))
            self.write(":WAVeform:BYTeorder MSBFirst")
            self.write(":WAVeform:FORMat WORD")  # the default is MSB first, and then LSB
            preamble_len = str(pts).__len__() + 2
            d = self.query(":WAVeform:DATA?",
                           pts * 2 + preamble_len + 1) # One word contains two bytes, and preamble, and 1 byte for '\n' by the end of the string
            d = d[preamble_len:-1]  # remove preamble

            # Now process the obtained raw data
            # Every word is made up of two bytes, representing the y axis level
            yinc = float(self.query(":WAVeform:YINCrement?"))
            yorg = float(self.query(":WAVeform:YORigin?"))
            yref = float(self.query(":WAVeform:YREFerence?"))
            print yinc
            print yorg
            print yref
            data = range(pts)  # pre-assign space for data
            for ii in range(pts):
                # MSB first by default
                byteM = ord(d[2 * ii])
                byteL = ord(d[2 * ii + 1])
                dlevel = (byteM << 8) + byteL
                data[ii] = (dlevel - yref) * yinc + yorg
            return data

        elif mode.lower() == "ascii":
            # Get data in ASCII format; it is slower than WORD, but no conversion is needed
            pts = int(self.query(":WAVeform:POINts?"))
            self.write(':WAVeform:SOURce CHANnel%d' % int(source))
            self.write(":WAVeform:FORMat ASCii")
            d = self.query(":WAVeform:DATA?", pts * 10 + pts - 1) # 10 byte per point max, plus comma separators
            data = [float(ii) for ii in d.split(',')]
            return data
        else:
            raise ValueError("Unrecognized mode")


