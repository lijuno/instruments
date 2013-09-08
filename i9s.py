"""
Instruments
* GPIB is implemented with linux-gpib kernel modules

by Lijun
"""

import gpib
#import binascii
import time
import sys
import getopt

## Helper functions below
def twoscomplement(int_in, bitsize):
    """
    Compute two's complement
    http://stackoverflow.com/a/1604701/1527875
    """
    return int_in- (1<<bitsize)
        
def split_string(str_in, stepsize):
    """
    Split a string every N charaters and store into an array 
    """
    str_out = [str_in[ii:ii+stepsize] for ii in range(0, len(str_in), stepsize)]
    return str_out
    

def write_data_1d(filename, arr1):
    """
    Write array to data
    """
    file = open(filename, 'w')
    for ii in range(len(arr1)):
        file.write('%s\n' % str(arr1[ii]))
    file.close()
    
def write_data_2d(filename, arr1, arr2):
    """
    Write array to data
    """
    file = open(filename, 'w')
    for ii in range(len(arr1)):
        file.write('%s\t%s\n' % (str(arr1[ii]), str(arr2[ii])))
    file.close()
    
def write_data(filename, arr1, **kwargs):
    pass
        

## Instrument classes below
class ib_dev():
    def __init__(self, port=None):
        self.port = port
        
    def initialize(self):
        self.handle = gpib.dev(0, self.port)
        #gpib.timeout(self.handle, 12)  # timeout T3s = 12; check help(gpib)
        print "GPIB::%d is initialized" % self.port
        print "GPIB handle = %d" % self.handle
        # Time delay dictionary below

        
    def write(self, msg):
        """
        GPIB write. Input argument msg must be a string
        """
        gpib.write(self.handle, msg)
        
    def read(self, bytesize=1024): 
        return gpib.read(self.handle, bytesize)
        
    def query(self, msg, bytesize=1024):
        gpib.write(self.handle, msg)
        return gpib.read(self.handle, bytesize)
    
    def close(self):
        gpib.close(self.handle)
        print "GPIB::%d is closed" % self.port    

class hp3582a(ib_dev):
    """
    HP 3582A FFT spectrum analyzer
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
        bytes_per_pt = 9
        pts = 256  # single trace in singla channel mode: 256 points
        bytes_separator = pts -1  # how many '.'s in the string
        self.write('LDS')
        data = self.read(bytes_per_pt*pts + bytes_separator)
        # return an ascii string like '-2.47E+01,-2.52E+01'
        
        data_float = [float(d) for d in data.split(',')]
        return data_float

        
class keithley2400c(ib_dev): 
    """
    Keithley 2400C sourcemeter
    """
    def __init__(self, port):
        ib_dev.__init__(self, port)
    
    def initialize(self):
        ib_dev.initialize(self)
        self.write('*RST')
        self.write(':SENSe:AVERage ON')
        self.write(':SENSe:FUNCtion:CONCurrent 0')  # disable the ability of measuring more than one function simultaneously      
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
        
    def IV_sweep(self, vlist=None, fourwire=False):
        """
        IV sweep: source V, measure I 
        """
        vlist_str = ','.join([str(v) for v in vlist]) 
        print vlist_str
        vlist_pts = len(vlist)
        
        self.write(':SENSe:CURRent:NPLCycles 0.1' ) # set integration time
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
    


        
        