"""
Classes for National Instruments
"""

import PyDAQmx as daq
import numpy


class USB6211():
    def __init__(self):
        pass
        
    def get_voltage_ai(self, **kwargs):
        """
        get_voltage_ai(self, **kwargs)
        Usage example:
        get_voltage_ai(self, channel='Dev1/ai6', voltage_limit=10, clock_freq=1e4, sampling_pts=1000, input_mode='diff')
        """

        # Set the default values below
        channel = 'Dev1/ai6'
        voltage_limit = 10
        clock_freq = 1e4
        sampling_pts = 1000
        input_mode = daq.DAQmx_Val_Diff

        # Read input args
        for key, value in kwargs.items():
            if key == 'channel':
                channel = value
            elif key == 'voltage_limit':
                voltage_limit = value
            elif key == 'clock_freq':
                clock_freq = value
            elif key == 'sampling_pts':
                sampling_pts = value
            elif key == 'input_mode':
                if value.lower() == 'diff':
                    input_mode = daq.DAQmx_Val_Diff
                elif value.lower() == 'nrse':
                    input_mode = daq.DAQmx_Val_NRSE
                elif value.lower() == 'rse':
                    input_mode = daq.DAQmx_Val_RSE
                else:
                    raise ValueError('Unrecognized input mode!')

        # The code below is adopted from http://pythonhosted.org/PyDAQmx/usage.html
        sampling_pts = int(sampling_pts)   # force int type for sampling_pts, otherwise will be type error
        analog_input = daq.Task()
        read = daq.int32()
        data = numpy.zeros((sampling_pts,), dtype=numpy.float64)

        recording_time = float(sampling_pts) / clock_freq
        if recording_time <= 5:
            fill_mode = 5
        else:
            fill_mode = recording_time * 1.01
        # The fill_mode here determines the max recording time USB6211 can go

        # DAQmx Configure Code
        #analog_input.CreateAIVoltageChan("Dev1/ai6","",DAQmx_Val_Cfg_Default,-voltage_range,voltage_range,DAQmx_Val_Volts,None)
        analog_input.CreateAIVoltageChan(channel,"",input_mode,-voltage_limit,voltage_limit,daq.DAQmx_Val_Volts,None)
        analog_input.CfgSampClkTiming("",clock_freq,daq.DAQmx_Val_Rising,daq.DAQmx_Val_FiniteSamps, sampling_pts)

        # DAQmx Start Code
        analog_input.StartTask()
        # DAQmx Read Code
        analog_input.ReadAnalogF64(sampling_pts, fill_mode, daq.DAQmx_Val_GroupByChannel,data,sampling_pts, daq.byref(read), None)
        
        print "Acquired %d points" % read.value
        return data


