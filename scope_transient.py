"""
Measure the transient signal with Agilent infiniium DSO81004B oscilloscope
"""

import i9s 
import matplotlib.pyplot as plt
import numpy as np
import time

a = i9s.agilent81004B(7)
a.initialize()
#a.reset()

a.set_triggering(source=3, slope=1, level=0.5)
a.set_timerange(50e-3)
a.set_yrange(source=4, yrange=1)

a.record_data(4)
time.sleep(5)

t = a.get_timeaxis()
y = a.get_ydata(4)
print t.__len__()
print y.__len__()
plt.plot(t,y)
plt.show()
a.close()