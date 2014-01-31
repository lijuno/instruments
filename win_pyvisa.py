"""
Placeholder for classes based on PyVISA
PyVISA source: https://github.com/hgrecco/pyvisa
"""

import visa

class ib_dev():
    def __init__(self, port=None):
        self.port = port

    def initialize(self):
        self.gpib = visa.instrument("GPIB::%d" % self.port)
        print "GPIB::%d is initialized" % self.port
        try:
        # Print IDN info if available
            self.ask("*IDN?")
        except:
            pass
        # Time delay dictionary below

    def write(self, msg):
        """
        GPIB write. Input argument msg must be a string
        """
        self.gpib.write(msg)

    def read(self, bytesize=1024):
        return self.gpib.read()

    def query(self, msg, bytesize=1024):
        self.gpib.write(msg)
        return self.gpib.read()

    def close(self):
        self.gpib.close()
        print "GPIB::%d is closed" % self.port

class rs232():
    pass

