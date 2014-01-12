"""
Miscellaneous devices
"""

import serial
import numpy as np

def sr570_write(cmd, port='COM5'):
    """
    A standalone function writing to SR570 low noise preamplifier via RS232 link
    RS232 communication interface, listen-only
    """

    ser = serial.Serial(port=port, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_TWO, bytesize=serial.EIGHTBITS)
    if not ser.isOpen():
        ser.open()
    else:
        ser.write(cmd + '\r\n')
        ser.close()


class SR570():
    """
    SR570 low-noise current amplifier
    """

    def __init__(self, port='COM5'):
        self.port = port

    def write(self, cmd):
        ser = serial.Serial(port=self.port, baudrate=9600, parity=serial.PARITY_NONE,
                               stopbits=serial.STOPBITS_TWO, bytesize=serial.EIGHTBITS)
        if not ser.isOpen():
            ser.open()
        else:
            ser.write(cmd + '\r\n')
            ser.close()

    def sensitivity_mapping(self, sens, direction='n2c'):
        """
        Map the numerical sensitivity to the commmand line argument
        Return an int for 'n2c', or a float for 'c2n'
        Input arg:
            sens: sensitivity
              * when in 'n2c'(numerical to command line) mode, unit A/V
              * when in 'c2n' mode: unitless, just an int
        """

        if direction == 'n2c': # Convert from numerical to command line argument
            # sens*1.01 to avoid the precision problem during the float point operation
            # e.g., 1/1e-5 results in 99999.99999999999, which makes exponent == 4 and fsdigit == 9 below

            # Now use an alogrithm to get the command line argument
            # Decompose the number val to fsdigit * 10** exponent
            # Normalize the value to 1pA
            val = int(sens * 1.01 / 1e-12)
            exponent = int(np.floor(np.log10(val)))
            fsdigit = int(val / 10 ** exponent)   # the first significant digit
            if fsdigit * 10 ** exponent > 10 ** 9 or fsdigit * 10 ** exponent < 1:
                raise RuntimeError('Sensitivity out of range')

            if fsdigit == 2:
                a = 1
            elif fsdigit == 5:
                a = 2
            elif fsdigit == 1:
                a = 0
            else:
                raise RuntimeError('Unrecognized sensitivity')

            i = a + exponent * 3
            return i

        elif direction == 'c2n':  # Convert from command line argument to numerical (unit: A or V)
            sens = int(sens)
            if sens < 0 or sens > 27:
                raise RuntimeError('Sensitivity out of range')

            # Do the reverse of "n2c" algorithm
            exponent = sens / 3
            a = sens % 3
            if a == 0:
                fsdigit = 1
            elif a == 1:
                fsdigit = 2
            elif a == 2:
                fsdigit = 5

            val = fsdigit * 10 ** exponent
            val = val / 1e12
            return val