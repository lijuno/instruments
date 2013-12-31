"""
Miscellaneous devices
"""

import serial


def sr570_write(cmd, port='COM5'):
    """
    Write to SR570 low noise preamplifier
    RS232 communication interface, listen-only
    """

    ser = serial.Serial(port=port, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_TWO, bytesize=serial.EIGHTBITS)
    if not ser.isOpen():
        ser.open()
    else:
        ser.write(cmd + '\r\n')
        ser.close()