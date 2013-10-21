"""
Gpib base class based on linux-gpib library
Library website: http://linux-gpib.sourceforge.net/
"""

import gpib

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