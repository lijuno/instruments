"""
Classes for National Instruments
"""

import PyDAQmx as daq
import numpy

class USB6211():
    def __init__(self):
        pass
        
    def get_voltage_ai(self, channel='Dev1/ai6', voltage_limit = 10, clock_freq = 1e4, sampling_pts = 1000):
        sampling_pts = int(sampling_pts)
        analog_input = daq.Task()
        read = daq.int32()
        data = numpy.zeros((sampling_pts,), dtype=numpy.float64)

        # DAQmx Configure Code
        #analog_input.CreateAIVoltageChan("Dev1/ai6","",DAQmx_Val_Cfg_Default,-voltage_range,voltage_range,DAQmx_Val_Volts,None)
        analog_input.CreateAIVoltageChan(channel,"",daq.DAQmx_Val_Diff,-voltage_limit,voltage_limit,daq.DAQmx_Val_Volts,None)
        analog_input.CfgSampClkTiming("",clock_freq,daq.DAQmx_Val_Rising,daq.DAQmx_Val_FiniteSamps, sampling_pts)

        # DAQmx Start Code
        analog_input.StartTask()
        # DAQmx Read Code
        analog_input.ReadAnalogF64(sampling_pts,10.0,daq.DAQmx_Val_GroupByChannel,data,sampling_pts, daq.byref(read),None)
        # the 10.0 here is the "fillMode" -- need to find out what that means
        
        print "Acquired %d points" % read.value
        return data
        
