# -*- coding: utf-8 -*-

# This is the base class that all picoscope modules use. As much as possible logic is
# put into this file. At minimum each instrument file requires you to modify the name
# of the API function call (e.g. ps6000xxxx vs ps4000xxxx). You can find pico-python
# at github.com/colinoflynn/pico-python .
#
# pico-python is Copyright (c) 2013-2014 By:
# Colin O'Flynn <coflynn@newae.com>
# Mark Harfouche <mark.harfouche@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Inspired by Patrick Carle's code at http://www.picotech.com/support/topic11239.html
# which was adapted from http://www.picotech.com/support/topic4926.html

"""This is the base class for PicoScope instruments."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__author__ = "Colin O'Flynn, Mark Harfouche"
__license__ = "FreeBSD"

import inspect
import time
#import warnings

import numpy as np


class _PicoscopeBase(object):

    """
    This class defines a general interface for Picoscope oscilloscopes.

    This  class should not be called directly since it relies on lower level
    functions to communicate with the actual devices.

    """

    ###You must reimplement this in device specific classes

    # Do not include .dll or .so, these will be appended automatically
    
    # LIBNAME = "ps4000a"
    
    # MAX_VALUE = 32764
    # MIN_VALUE = -32764
    
    # EXT_MAX_VALUE = 32767
    # EXT_MIN_VALUE = -32767
    
    # MAX_PULSE_WIDTH_QUALIFIER_COUNT = 16777215
    # MAX_DELAY_COUNT                 = 8388607
    
    # MAX_SIG_GEN_BUFFER_SIZE = 16384
    
    # MIN_SIG_GEN_BUFFER_SIZE = 10
    # MIN_DWELL_COUNT         = 10
    # MAX_SWEEPS_SHOTS        = 2**30 - 1
    # AWG_DAC_FREQUENCY       = 80e6
    # AWG_PHASE_ACCUMULATOR   = 4294967296.0
    
    # PS4000A_MAX_ANALOGUE_OFFSET_50MV_200MV = 0.250
    # PS4000A_MIN_ANALOGUE_OFFSET_50MV_200MV = -0.250
    # PS4000A_MAX_ANALOGUE_OFFSET_500MV_2V   = 2.500
    # PS4000A_MIN_ANALOGUE_OFFSET_500MV_2V   = -2.500
    # PS4000A_MAX_ANALOGUE_OFFSET_5V_20V     = 20
    # PS4000A_MIN_ANALOGUE_OFFSET_5V_20V     = -20
    
    # EXTRA_OPERATIONS = ...
    
    # BANDWIDTH_LIMITER = ...
    
    # CHANNEL_COUPLINGS = ...
    
    # NUM_CHANNELS = ...
    # CHANNELS = ...
    
    # CHANNEL_BUFFER_INDEX = ...
    
    # EXT_RANGE_VOLTS = ...
    
    # CHANNEL_RANGE = ...
    
    # RESISTANCE_RANGE = ...
    
    # ETS_MODE = ...
    
    # TIME_UNITS = ...
    
    # SWEEP_TYPE = ...
    
    # WAVE_TYPE = ...
    
    # MAX_EXC_FREQUENCY = ...
    # MIN_EXC_FREQUENCY = ...
    
    # CHANNEL_LED = ...
    
    # META_TYPE = ...
    
    # META_OPERATION = ...
    
    # META_FORMAT = ...
     
    # SIGGEN_TRIG_TYPE = ...
                        
    # SIGGEN_TRIG_SOURCE = ...
    
    # INDEX_MODE = ...
    
    # THRESHOLD_MODE = ...
    
    # THRESHOLD_DIRECTION = ...
    
    # TRIGGER_STATE = ...
    
    # SENSOR_STATE = ...
    
    # FREQUENCY_COUNTER_RANGE = ...
    
    # CHANNEL_LED_SETTING = ...
    
    # DIRECTION = ...
    
    # CONDITION = ...
    
    # CONDITIONS_INFO = ...
    
    # TRIGGER_CHANNEL_PROPERTIES = ...
    
    # CONNECT_DETECT = ...
    
    # RATIO_MODE = ...
    
    # PULSE_WIDTH_TYPE = ...
    
    # CHANNEL_INFO = ...
    
    
    
    ###End of things you must reimplement (I think).

    # If we don't get this CaseInsentiveDict working, I would prefer to stick
    # with their spelling of archaic C all caps for this. I know it is silly,
    # but it removes confusion for certain things like
    # DC_VOLTAGE = DCVoltage or DcVoltage or DC_Voltage
    # or even better
    # SOFT_TRIG = SoftwareTrigger vs SoftTrig

    ### getUnitInfo parameter types
    UNIT_INFO_TYPES = {"DriverVersion"          : 0x0,
                       "USBVersion"             : 0x1,
                       "HardwareVersion"        : 0x2,
                       "VariantInfo"            : 0x3,
                       "BatchAndSerial"         : 0x4,
                       "CalDate"                : 0x5,
                       "KernelVersion"          : 0x6,
                       "DigitalHardwareVersion" : 0x7,
                       "AnalogueHardwareVersion": 0x8,
                       "PicoFirmwareVersion1"   : 0x9,
                       "PicoFirmwareVersion2"   : 0xA,
    #                   "MacAdress"              : 0xB,
                       "ShadowCal"              : 0xC,
                       "IPPVersion"             : 0xD,
                       "DriverPath"             : 0xE}
    ### PICO_STATUS
    PICO_STATUS = {"PICO_SV_MEMORY": 0,
                   "PICO_SV_MEMORY_NO_OF_SEGMENTS": 1,
                   "PICO_SV_MEMORY_MAX_SAMPLES": 2,
                   "PICO_SV_NO_OF_CHANNELS": 3,
                   "PICO_SV_ARRAY_OF_CHANNELS": 4,
                   "PICO_SV_CHANNEL": 5,
                   "PICO_SV_CHANNEL_NAME": 6,
                   "PICO_SV_CHANNEL_RANGE": 7,
                   "PICO_SV_CHANNEL_COUPLING": 8,
                   "PICO_SV_CHANNEL_ENABLED": 9,
                   "PICO_SV_CHANNEL_ANALOGUE_OFFSET": 10,
                   "PICO_SV_CHANNEL_BANDWIDTH": 11,
                   "PICO_SV_TRIGGER": 12,
                   "PICO_SV_TRIGGER_AUXIO_OUTPUT_ENABLED": 13,
                   "PICO_SV_TRIGGER_AUTO_TRIGGER_MILLISECONDS": 14,
                   "PICO_SV_TRIGGER_PROPERTIES": 15,
                   "PICO_SV_NO_OF_TRIGGER_PROPERTIES": 16,
                   "PICO_SV_TRIGGER_PROPERTIES_CHANNEL": 17,
                   "PICO_SV_TRIGGER_PROPERTIES_THRESHOLD_UPPER": 18,
                   "PICO_SV_TRIGGER_PROPERTIES_THRESHOLD_UPPER_HYSTERESIS": 19,
                   "PICO_SV_TRIGGER_PROPERTIES_THRESHOLD_LOWER": 20,
                   "PICO_SV_TRIGGER_PROPERTIES_THRESHOLD_LOWER_HYSTERESIS": 21,
                   "PICO_SV_TRIGGER_PROPERTIES_THRESHOLD_MODE": 22,
                   "PICO_SV_TRIGGER_ARRAY_OF_BLOCK_CONDITIONS": 23,
                   "PICO_SV_TRIGGER_NO_OF_BLOCK_CONDITIONS": 24,
                   "PICO_SV_TRIGGER_CONDITIONS": 25,
                   "PICO_SV_TRIGGER_NO_OF_CONDITIONS": 26,
                   "PICO_SV_TRIGGER_CONDITION_SOURCE": 27,
                   "PICO_SV_TRIGGER_CONDITION_STATE": 28,
                   "PICO_SV_TRIGGER_DIRECTION": 29,
                   "PICO_SV_TRIGGER_NO_OF_DIRECTIONS": 30,
                   "PICO_SV_TRIGGER_DIRECTION_CHANNEL": 31,
                   "PICO_SV_TRIGGER_DIRECTION_DIRECTION": 32,
                   "PICO_SV_TRIGGER_DELAY": 33,
                   "PICO_SV_TRIGGER_DELAY_MS": 34,
                   "PICO_SV_FREQUENCY_COUNTER": 35,
                   "PICO_SV_FREQUENCY_COUNTER_ENABLED": 36,
                   "PICO_SV_FREQUENCY_COUNTER_CHANNEL": 37,
                   "PICO_SV_FREQUENCY_COUNTER_RANGE": 38,
                   "PICO_SV_FREQUENCY_COUNTER_TRESHOLDMAJOR": 39,
                   "PICO_SV_FREQUENCY_COUNTER_TRESHOLDMINOR": 40,
                   "PICO_SV_PULSE_WIDTH_PROPERTIES": 41,
                   "PICO_SV_PULSE_WIDTH_PROPERTIES_DIRECTION": 42,
                   "PICO_SV_PULSE_WIDTH_PROPERTIES_LOWER": 43,
                   "PICO_SV_PULSE_WIDTH_PROPERTIES_UPPER": 44,
                   "PICO_SV_PULSE_WIDTH_PROPERTIES_TYPE": 45,
                   "PICO_SV_PULSE_WIDTH_ARRAY_OF_BLOCK_CONDITIONS": 46,
                   "PICO_SV_PULSE_WIDTH_NO_OF_BLOCK_CONDITIONS": 47,
                   "PICO_SV_PULSE_WIDTH_CONDITIONS": 48,
                   "PICO_SV_PULSE_WIDTH_NO_OF_CONDITIONS": 49,
                   "PICO_SV_PULSE_WIDTH_CONDITIONS_SOURCE": 50,
                   "PICO_SV_PULSE_WIDTH_CONDITIONS_STATE": 51,
                   "PICO_SV_SAMPLE_PROPERTIES": 52,
                   "PICO_SV_SAMPLE_PROPERTIES_PRE_TRIGGER_SAMPLES": 53,
                   "PICO_SV_SAMPLE_PROPERTIES_POST_TRIGGER_SAMPLES": 54,
                   "PICO_SV_SAMPLE_PROPERTIES_TIMEBASE": 55,
                   "PICO_SV_SAMPLE_PROPERTIES_NO_OF_CAPTURES": 56,
                   "PICO_SV_SAMPLE_PROPERTIES_RESOLUTION": 57,
                   "PICO_SV_SAMPLE_PROPERTIES_OVERLAPPED": 58,
                   "PICO_SV_SAMPLE_PROPERTIES_OVERLAPPED_DOWN_SAMPLE_RATIO": 59,
                   "PICO_SV_SAMPLE_PROPERTIES_OVERLAPPED_DOWN_SAMPLE_RATIO_MODE": 60,
                   "PICO_SV_SAMPLE_PROPERTIES_OVERLAPPED_REQUERSTED_NO_OF_SAMPLES": 61,
                   "PICO_SV_SAMPLE_PROPERTIES_OVERLAPPED_SEGMENT_INDEX_FROM": 62,
                   "PICO_SV_SAMPLE_PROPERTIES_OVERLAPPED_SEGMENT_INDEX_TO": 63,
                   "PICO_SV_SIGNAL_GENERATOR": 64,
                   "PICO_SV_SIGNAL_GENERATOR_BUILT_IN": 65,
                   "PICO_SV_SIGNAL_GENERATOR_BUILT_IN_WAVE_TYPE": 66,
                   "PICO_SV_SIGNAL_GENERATOR_BUILT_IN_START_FREQUENCY": 67,
                   "PICO_SV_SIGNAL_GENERATOR_BUILT_IN_STOP_FREQUENCY": 68,
                   "PICO_SV_SIGNAL_GENERATOR_BUILT_IN_INCREMENT": 69,
                   "PICO_SV_SIGNAL_GENERATOR_BUILT_IN_DWELL_TIME": 70,
                   "PICO_SV_SIGNAL_GENERATOR_AWG": 71,
                   "PICO_SV_SIGNAL_GENERATOR_AWG_START_DELTA_PHASE": 72,
                   "PICO_SV_SIGNAL_GENERATOR_AWG_STOP_DELTA_PHASE": 73,
                   "PICO_SV_SIGNAL_GENERATOR_AWG_DELTA_PHASE_INCREMENT": 74,
                   "PICO_SV_SIGNAL_GENERATOR_AWG_DWELL_COUNT": 75,
                   "PICO_SV_SIGNAL_GENERATOR_AWG_INDEX_MODE": 76,
                   "PICO_SV_SIGNAL_GENERATOR_AWG_WAVEFORM_SIZE": 77,
                   "PICO_SV_SIGNAL_GENERATOR_ARRAY_OF_AWG_WAVEFORM_VALUES": 78,
                   "PICO_SV_SIGNAL_GENERATOR_OFFSET_VOLTAGE": 79,
                   "PICO_SV_SIGNAL_GENERATOR_PK_TO_PK": 80,
                   "PICO_SV_SIGNAL_GENERATOR_OPERATION": 81,
                   "PICO_SV_SIGNAL_GENERATOR_SHOTS": 82,
                   "PICO_SV_SIGNAL_GENERATOR_SWEEPS": 83,
                   "PICO_SV_SIGNAL_GENERATOR_SWEEP_TYPE": 84,
                   "PICO_SV_SIGNAL_GENERATOR_TRIGGER_TYPE": 85,
                   "PICO_SV_SIGNAL_GENERATOR_TRIGGER_SOURCE": 86,
                   "PICO_SV_SIGNAL_GENERATOR_EXT_IN_THRESHOLD": 87,
                   "PICO_SV_ETS": 88,
                   "PICO_SV_ETS_STATE": 89,
                   "PICO_SV_ETS_CYCLE": 90,
                   "PICO_SV_ETS_INTERLEAVE": 91,
                   "PICO_SV_ETS_SAMPLE_TIME_PICOSECONDS": 92}

    def __init__(self, serialNumber=None, connect=True):
        """ Create a picoscope class, and by default also connect to the scope. """

        # TODO: Make A class for each channel
        # that way the settings will make more sense

        # These do not correspond to API values, but rather to
        # the "true" voltage as seen at the oscilloscope probe
        self.CHRange = [5.0] * self.NUM_CHANNELS
        self.CHOffset = [0.0] * self.NUM_CHANNELS
        self.ProbeAttenuation = [1.0] * self.NUM_CHANNELS

        self.handle = None

        if connect is True:
            self.open(serialNumber)
    
    def open(self, serialNumber=None):
        """ Open the scope, if serialNumber is None just opens first one found. """

        self._lowLevelOpenUnit(serialNumber)

    def openUnitAsync(self, serialNumber=None):
        """ Open the scope asynchronously. """
        self._lowLevelOpenUnitAsync(serialNumber)

    def openUnitProgress(self):
        """ Return a tuple (progress, completed). """
        return self._lowLevelOpenUnitProgress()

    def close(self):
        """
        Close the scope.

        You should call this yourself because the Python garbage collector
        might take some time.

        """
        if not self.handle is None:
            self._lowLevelCloseUnit()
            self.handle = None

    def __del__(self):
        self.close()
    
    def enumerateUnits(self):
        """ Enumerate connceted units. Return serial numbers as list of strings. """
        return self._lowLevelEnumerateUnits()
        
    def getAllUnitInfo(self):
        """ Return: human readible unit information as a string. """
        s = ""
        for key in sorted(self.UNIT_INFO_TYPES.keys(), key=self.UNIT_INFO_TYPES.get):
            s += key.ljust(30) + ": " + self.getUnitInfo(key) + "\n"

        s = s[:-1]
        return s
    
    def getUnitInfo(self, info):
        """ Return: A string containing the requested information. """
        if not isinstance(info, int):
            info = self.UNIT_INFO_TYPES[info]
        return self._lowLevelGetUnitInfo(info)
    
    def stop(self):
        """ Stop scope acquisition. """
        self._lowLevelStop()
    
    def setSigGenBuiltIn(self, offsetVoltage=0, pkToPk=2, waveType="sine", 
                         frequency=1E6, shots=1, triggerType="rising", 
                         triggerSource="none", stopFreq=None, increment = 10.0, 
                         dwellTime=1E-3, sweepType="up", extraOperations="ESOff", numSweeps=0):

        """
        This function generates simple signals using the built-in waveforms
 
        Supported waveforms include: 
           Sine, Square, Triangle, RampUp, RampDown, and DCVoltage

        Some hardware also supports these additional waveforms:
           Sinc, Gaussian, HalfSine, and WhiteNoise

        To sweep the waveform, set the stopFrequency and optionally the
        increment, dwellTime, sweepType and numSweeps.

        Supported sweep types: Up, Down, UpDown, DownUp
        """
        # I put this here, because the python idiom None is very
        # close to the "None" string we expect
        if triggerSource is None:
            triggerSource = "None"

        if not isinstance(waveType, int):
            waveType = self.WAVE_TYPE[waveType]
        if not isinstance(triggerType, int):
            triggerType = self.SIGGEN_TRIG_TYPE[triggerType]
        if not isinstance(triggerSource, int):
            triggerSource = self.SIGGEN_TRIG_SOURCE[triggerSource]
        if not isinstance(sweepType, int):
            sweepType = self.SWEEP_TYPE[sweepType]
        if not isinstance(extraOperations, int):
            extraOperations = self.EXTRA_OPERATIONS[extraOperations]
        
        shots = int(shots)
        if shots > self.MAX_SWEEPS_SHOTS:
            shots = self.MAX_SWEEPS_SHOTS
            print("Warning\n shots > MAX_SWEEP_SHOTS -> set shots = MAX_SWEEP_SHOTS\n")

  
        self._lowLevelSetSigGenBuiltIn(offsetVoltage, pkToPk, waveType,
                                             frequency, shots, triggerType,
                                             triggerSource, stopFreq, increment, 
                                             dwellTime, sweepType, extraOperations, numSweeps)
                                             
                                             
                                                 
                                                 
    def setAWGSimple(self, waveform, duration, offsetVoltage=None,
                     pkToPk=None, indexMode="Single", shots=1, triggerType="Rising",
                     triggerSource="ScopeTrig"):
        """
        Set the AWG to output your desired wavefrom.
        If you require precise control of the timestep increment, you should use
        setSigGenAritrarySimpleDelaPhase instead
        Check setSigGenAritrarySimpleDelaPhase for parameter explanation
        Returns: The actual duration of the waveform
        """
        sampling_interval = duration / len(waveform)

        if not isinstance(indexMode, int):
            indexMode = self.AWG_INDEX_MODES[indexMode]

        if indexMode == self.AWG_INDEX_MODES["Single"]:
            pass
        elif indexMode == self.AWG_INDEX_MODES["Dual"]:
            sampling_interval /= 2
        elif indexMode == self.AWG_INDEX_MODES["Quad"]:
            sampling_interval /= 4

        deltaPhase = self.getAWGDeltaPhase(sampling_interval)
        
        
        

        actual_druation = self.setAWGSimpleDeltaPhase(waveform, deltaPhase, offsetVoltage,
                                                      pkToPk, indexMode, shots, triggerType,
                                                      triggerSource)

        return (actual_druation, deltaPhase)

    def setAWGSimpleDeltaPhase(self, waveform, deltaPhase, offsetVoltage=None,
                               pkToPk=None, indexMode="Single", shots=1, triggerType="Rising",
                               triggerSource="ScopeTrig"):
        """
        Specify deltaPhase between each sample instead of the total waveform duration.
        Returns the actual time duration of the waveform
        If pkToPk and offset Voltage are both set to None, then their values are computed as
        pkToPk = np.max(waveform) - np.min(waveform)
        offset = (np.max(waveform) + np.min(waveform)) / 2
        This should in theory minimize the quantization error in the ADC.
        else, the waveform shoudl be a numpy int16 type array with the containing
        waveform
        For the Quad mode, if offset voltage is not provided, then waveform[0]
        is assumed to be the offset. In quad mode, the offset voltage is the point of symmetry
        This is function provides a little more control than
        setAWGSimple in the sense that you are able to specify deltaPhase
        directly. It should only be used when deltaPhase becomes very large.
        Warning. Ideally, you would want this to be a power of 2 that way each
        sample is given out at exactly the same difference in time otherwise,
        if you give it something closer to .75 you would obtain
         T  | phase accumulator value | sample
         0  |      0                  |      0
         5  |      0.75               |      0
        10  |      1.50               |      1
        15  |      2.25               |      2
        20  |      3.00               |      3
        25  |      3.75               |      3
        notice how sample 0 and 3 were played twice  while others were only
        played once.
        This is why this low level function is exposed to the user so that he
        can control these edge cases
        I would suggest using something like this: if you care about obtaining
        evenly spaced samples at the expense of the precise duration of the your
        waveform
        To find the next highest power of 2
            always a smaller sampling interval than the one you asked for
        math.pow(2, math.ceil(math.log(deltaPhase, 2)))
        To find the next smaller power of 2
            always a larger sampling interval than the one you asked for
        math.pow(2, math.floor(math.log(deltaPhase, 2)))
        To find the nearest power of 2
        math.pow(2, int(math.log(deltaPhase, 2), + 0.5))
        """

        """
        This part of the code is written for the PS6403 (PS6403B if that matters)
        I don't really know a good way to differentiate between PS6403 versions
        It essentially does some autoscaling for the waveform so that it can be sent
        to the Picoscope to allow for maximum resolution from the DDS.
        I haven't tested if you can actually obtain more resolution than simply setting
        the DDS to output from -2 to +2
        I assume they have some type of adjustable gain and offset on their DDS
        allowing them to claim that they can get extremely high resolution.
        """

        if not isinstance(indexMode, int):
            indexMode = self.AWG_INDEX_MODES[indexMode]
        if not isinstance(triggerType, int):
            triggerType = self.SIGGEN_TRIG_TYPES[triggerType]
        if not isinstance(triggerSource, int):
            triggerSource = self.SIGGEN_TRIG_SOURCES[triggerSource]

        if waveform.dtype == np.int16:
            if offsetVoltage is None:
                offsetVoltage = 0.0
            if pkToPk is None:
                pkToPk = 1.1*(np.max(waveform)-np.min(waveform))
                
        else:
            if indexMode == self.AWG_INDEX_MODES["Quad"]:
                # Optimize for the Quad mode.
                """
                Quad mode. The generator outputs the contents of the buffer,
                then on its second pass through the buffer outputs the same
                data in reverse order. On the third and fourth passes
                it does the same but with a negative version of the data. This
                allows you to specify only the first quarter of a waveform with
                fourfold symmetry, such as a sine wave, and let the generator
                fill in the other three quarters.
                """
                if offsetVoltage is None:
                    offsetVoltage = waveform[0]
            else:
                # Nothing to do for the dual mode or the single mode
                if offsetVoltage is None:
                    offsetVoltage = (np.max(waveform) + np.min(waveform)) / 2

            # make a copy of the original data as to not clobber up the array
            waveform = waveform - offsetVoltage
            if pkToPk is None:
                pkToPk = np.max(np.absolute(waveform)) * 2

            # waveform should now be baised around 0
            # with
            #     max(waveform) = +pkToPk/2
            #     min(waveform) = -pkToPk/2
            waveform /= pkToPk

            # waveform should now be a number between -0.5 and +0.5

            waveform += 0.5
            # and now the waveform is between 0 and 1
            # inclusively???

            # now the waveform is properly quantized
            waveform *= (self.AWGMaxVal - self.AWGMinVal)
            waveform += self.AWGMinVal

            waveform.round(out=waveform)

            # convert to an int16 typqe as requried by the function
            waveform = np.array(waveform, dtype=np.int16)

            # funny floating point rounding errors
            waveform.clip(self.AWGMinVal, self.AWGMaxVal, out=waveform)

        self._lowLevelSetAWGSimpleDeltaPhase(waveform, deltaPhase, offsetVoltage, pkToPk,
                                             indexMode, shots, triggerType, triggerSource)

        timeIncrement = self.getAWGTimeIncrement(deltaPhase)
        waveform_duration = timeIncrement * len(waveform)

        #if   indexMode == self.AWG_INDEX_MODES["Single"]:
            #pass
        #elif
        if indexMode == self.AWG_INDEX_MODES["Dual"]:
            waveform_duration *= 2
        elif indexMode == self.AWG_INDEX_MODES["Quad"]:
            waveform_duration *= 4

        return waveform_duration

    def getAWGDeltaPhase(self, timeIncrement):
        """
        Return the deltaPhase integer used by the AWG.
        This is useful when you are trying to generate very fast waveforms when
        you are getting close to the limits of your waveform generator.
        For example, the PS6000's DDS phase accumulator increments by
        deltaPhase every AWGDACInterval.
        The top 2**self.AWGBufferAddressWidth bits indicate which sample is
        being output by the DDS.
        """
        samplingFrequency = 1 / timeIncrement
        deltaPhase = int(samplingFrequency / self.AWGDACFrequency *
                          2 ** (self.AWGPhaseAccumulatorSize - self.AWGBufferAddressWidth))
        return deltaPhase

    def getAWGTimeIncrement(self, deltaPhase):
        """
        Return the time between AWG samples given a certain deltaPhase.
        You should use this function in conjunction with
        getAWGDeltaPhase to obtain the actual timestep of AWG.
        """
        samplingFrequency = deltaPhase * self.AWGDACFrequency / \
                            2 ** (self.AWGPhaseAccumulatorSize - self.AWGBufferAddressWidth)
        return 1 / samplingFrequency




    
    def sigGenSoftwareControl(self, state):
        """
        This function causes a trigger event, or starts and stops gating. 
        It is used when the signal generator is set to SIGGEN_SOFT_TRIG .
        
        Sets the trigger gate high or low when the trigger type is set 
        to either SIGGEN_GATE_HIGH or SIGGEN_GATE_LOW. Ignored for other trigger types.
        
        Applicability
        Use with ps4000aSetSigGenBuiltIn or ps4000aSetSigGenArbitrary.
        """
        
        if not isinstance(state, int):
            waveType = self.SIGGEN_TRIG_TYPE[state]
        
        self._lowLevelSigGenSoftwareControl(state)
    
    def flashLed(self, times=5, start=False, stop=False):
        """
        Flash the front panel LEDs.

        Use one of input arguments to specify how the Picoscope will flash the
        LED

        times = The number of times the picoscope will flash the LED
        start = If true, will flash the LED indefinitely
        stop  = If true, will stop any flashing.

        Note that calls to the RunStreaming or RunBlock will stop any flashing.

        """
        if start:
            times = -1
        if stop:
            times = 0

        self._lowLevelFlashLed(times)
        
    def setChannel(self, channel='A', coupling="DC", vRange=2.0, vOffset=0.0, enabled=True,
                   BWLimited=False, probeAttenuation=1.0):
        """
        Set up a specific channel.

        It finds the smallest range that is capable of accepting your signal.
        Return actual range of the scope as double.

        The vOffset, is an offset that the scope will ADD to your signal.

        If using a probe (or a sense resitor), the probeAttenuation value is used to find
        the approriate channel range on the scope to use.

        e.g. to use a 10x attenuation probe, you must supply the following parameters
        ps.setChannel('A', "DC", 20.0, 5.0, True, False, 10.0)

        The scope will then be set to use the +- 2V mode at the scope allowing you to measure
        your signal from -25V to +15V.
        After this point, you can set everything in terms of units as seen at the tip of the probe.
        For example, you can set a trigger of 15V and it will trigger at the correct value.

        When using a sense resistor, lets say R = 1.3 ohm, you obtain the relation:

        V = IR, meaning that your probe as an attenuation of R compared to the current you are
        trying to measure.

        You should supply probeAttenuation = 1.3
        The rest of your units should be specified in amps.

        Unfortunately, you still have to supply a vRange that is very close to the allowed values.
        This will change in furture version where we will find the next largest range to
        accomodate the desired range.

        If you want to use units of mA, supply a probe attenuation of 1.3E3.
        Note, the authors recommend sticking to SI units because it makes it easier to guess
        what units each parameter is in.

        """
        if enabled:
            enabled = 1
        else:
            enabled = 0

        if not isinstance(channel, int):
            chNum = self.CHANNELS[channel]
        else:
            chNum = channel

        if not isinstance(coupling, int):
            coupling = self.CHANNEL_COUPLINGS[coupling]

        # finds the next largest range accounting for small floating point errors
        vRangeAPI = None
        for item in self.CHANNEL_RANGE:
            if item["rangeV"] - vRange / probeAttenuation > -1E-4:
                if vRangeAPI is None:
                    vRangeAPI = item
                    # break
                # Don't know if this is necessary assuming that it will iterate in order
                elif vRangeAPI["rangeV"] > item["rangeV"]:
                    vRangeAPI = item

        if vRangeAPI is None:
            raise ValueError("Desired range %f is too large. Maximum range is %f." %
                             (vRange, self.CHANNEL_RANGE[-1]["rangeV"] * probeAttenuation))

        # store the actually chosen range of the scope
        vRange = vRangeAPI["rangeV"] * probeAttenuation

        if BWLimited == 2:
            BWLimited = 2  # Bandwidth Limiter for PicoScope 6404
        elif BWLimited == 1:
            BWLimited = 1  # Bandwidth Limiter for PicoScope 6402/6403
        else:
            BWLimited = 0

        self._lowLevelSetChannel(chNum, enabled, coupling, vRangeAPI["apivalue"],
                                 vOffset / probeAttenuation, BWLimited)

        # if all was successful, save the parameters
        self.CHRange[chNum] = vRange
        self.CHOffset[chNum] = vOffset
        self.ProbeAttenuation[chNum] = probeAttenuation

        return vRange
    
    def setSamplingFrequency(self, sampleFreq, noSamples, oversample=0, segmentIndex=0, maxChannelsEnabled=8):
        """ Return (actualSampleFreq, maxSamples). """
        # TODO: make me more like the functions above
        #       at least in terms of what I return
        sampleInterval = 1.0 / sampleFreq
        duration = noSamples * sampleInterval
        self.setSamplingInterval(sampleInterval, duration, oversample, segmentIndex,maxChannelsEnabled)
        return (self.sampleRate, self.maxSamples)
        
    def getMaxValue(self):
        """ Return the maximum ADC value, used for scaling. """
        # TODO: make this more consistent accross versions
        # This was a "fix" when we started supported PS5000a
        return self.MAX_VALUE

    def getMinValue(self):
        """ Return the minimum ADC value, used for scaling. """
        return self.MIN_VALUE
    
    def setSimpleTrigger(self, trigSrc, threshold_V=0, direction="rising", delay=0, timeout_ms=100,
                         enabled=True):
        """
        Simple Trigger setup.

        trigSrc can be either a number corresponding to the low level
        specifications of the scope or a string such as 'A' or 'AUX'

        direction can be a text string such as "Rising" or "Falling",
        or the value of the dict from self.THRESHOLD_DIRECTION  [] corresponding
        to your trigger type.

        delay is number of clock cycles to wait from trigger conditions met
        until we actually trigger capture.

        timeout_ms is time to wait in mS from calling runBlock() or similar
        (e.g. when trigger arms) for the trigger to occur. If no trigger
        occurs it gives up & auto-triggers after timeout_ms.

        Support for offset is currently untested

        Note, the AUX port (or EXT) only has a range of +- 1V (at least in PS6000)

        """
        if not isinstance(trigSrc, int):
            trigSrc = self.CHANNELS[trigSrc]

        if not isinstance(direction, int):
            direction = self.THRESHOLD_DIRECTION  [direction]

        if trigSrc >= self.NUM_CHANNELS:
            threshold_adc = int((threshold_V / self.EXT_RANGE_VOLTS) * self.EXT_MAX_VALUE)

            # The external port is typically used as a clock. So I don't think we should
            # raise errors
            threshold_adc = min(threshold_adc, self.EXT_MAX_VALUE)
            threshold_adc = max(threshold_adc, self.EXT_MIN_VALUE)
        else:
            a2v = self.CHRange[trigSrc] / self.getMaxValue()
            threshold_adc = int((threshold_V + self.CHOffset[trigSrc]) / a2v)

            if threshold_adc > self.getMaxValue() or threshold_adc < self.getMinValue():
                raise IOError("Trigger Level of %fV outside allowed range (%f, %f)" % (
                    threshold_V, -self.CHRange[trigSrc] - self.CHOffset[trigSrc],
                    self.CHRange[trigSrc] - self.CHOffset[trigSrc]))

        enabled = int(bool(enabled))

        self._lowLevelSetSimpleTrigger(enabled, trigSrc, threshold_adc, direction, delay, timeout_ms)
    
    def runBlock(self, pretrig=0.0, segmentIndex=0):
        """ Run a single block, must have already called setSampling for proper setup. """

        # getting max samples is riddiculous. 1GS buffer means it will take so long
        nSamples = min(self.noSamples, self.maxSamples)

        self._lowLevelRunBlock(int(round(nSamples * pretrig)),          # to return the same No. Samples ( if pretrig != 0.0 ) I'm wrong ?
                               int(round(nSamples * (1 - pretrig))),
                               self.timebase, self.oversample, segmentIndex)

    def isReady(self):
        """
        Check if scope done.

        Returns: bool.

        """
        return self._lowLevelIsReady()
    
    def waitReady(self):
        """ Block until the scope is ready. """
        while not self.isReady():
            time.sleep(0.01)
    
    def getData(self, channels=['A'], numSamples=0, startIndex=0, downSampleRatio=1,
                   downSampleMode="none", segmentIndex=0, data=None):
        """
        Return the data in the purest form.

        it returns a tuple containing:
        (data, numSamplesReturned, overflow)
        data is an array of size numSamples
        numSamplesReturned is the number of samples returned by the Picoscope
                (I don't know when this would not be equal to numSamples)
        overflow is a flag that is true when the signal was either too large
                 or too small to be properly digitized
        """
        
        channelsNum = {}
        for channel in channels:
            if not isinstance(channel, int):
                channelsNum[channel] = self.CHANNELS[channel]
            else:
                channelsNum[channel] = channel

        if not isinstance(downSampleMode, int):
            downSampleMode = self.RATIO_MODE[downSampleMode]

        if numSamples == 0:
            # maxSamples is probably huge, 1Gig Sample can be HUGE....
            numSamples = min(self.maxSamples, self.noSamples)

        if data is None:
            data = {}
            for channel in channels:
                data[channel] = np.empty(numSamples, dtype=np.int16)
        else:
            for channel in channels:
                    if data[channel].dtype != np.int16:
                        raise TypeError('Provided array must be int16')
                    if data[channel].size < numSamples:
                        raise ValueError('Provided array must be at least as big as numSamples.')
                        # see http://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.flags.html
                    if data[channel].flags['CARRAY'] is False:
                        raise TypeError('Provided array must be c_contiguous, aligned and writeable.')
        
        # register data buffers for the different channel/segemntIndex combinations
        for channel in channels:
            self._lowLevelSetDataBuffer(channelsNum[channel], data[channel], downSampleMode, segmentIndex)
        
        # fill in the data buffers registered before for the given segmentIndex. All channels are done simultaneously
        (numSamplesReturned, overflow) = self._lowLevelGetValues(numSamples, startIndex,
                                                                 downSampleRatio, downSampleMode,
                                                                 segmentIndex)
        # necessary or else the next call to getValues will try to fill this array
        # unless it is a call trying to read the same channel.
        for channel in channels:
            self._lowLevelClearDataBuffer(channelsNum[channel], segmentIndex)
        
        overflows = []
        # overflow is a bitwise mask
        for channel in channels:
            overflows.append(bool(overflow & (1 << channelsNum[channel])))

        return (data, numSamplesReturned, overflows)
        
    def rawToV(self, dataRaw):
        """ Convert the raw data to voltage units. Return as numpy array. """
        
        dataV = {}
        for channel in dataRaw.keys():
            if not isinstance(channel, int):
                channelNum = self.CHANNELS[channel]
            dataV[channel] = np.empty(dataRaw[channel].size)
            a2v = self.CHRange[channelNum] / float(self.getMaxValue())
            np.multiply(dataRaw[channel], a2v, dataV[channel])
            np.subtract(dataV[channel], self.CHOffset[channelNum], dataV[channel])
        return dataV
        
    def getDataV(self, channels, numSamples=0, startIndex=0, downSampleRatio=1, downSampleMode=0,
                 segmentIndex=0, returnOverflow=False, exceptOverflow=False, data=None):
                 
        """
        Return the data as an array of voltage values.

        it returns (dataV, overflow) if returnOverflow = True
        else, it returns returns dataV
        dataV is an array with size numSamplesReturned
        overflow is a flag that is true when the signal was either too large
                 or too small to be properly digitized

        if exceptOverflow is true, an IOError exception is raised on overflow if
        returnOverflow is False. This allows you to detect overflows at
        higher layers w/o complicated return trees. You cannot however read the '
        good' data, you only get the exception information then.

        """

        (data, numSamplesReturned, overflow) = self.getData(channels, numSamples, startIndex,
                                                                  downSampleRatio, downSampleMode,
                                                                  segmentIndex, data)
        
        dataV = self.rawToV(data)
        
        if returnOverflow:
            return (dataV, overflow)
        else:
            if sum(overflow)>0 and exceptOverflow:
                raise IOError("Overflow detected in data")
            return dataV
        
    ####################################################################################################
    ##### Tested up to here.
    ####################################################################################################
    

    def setSamplingInterval(self, sampleInterval, duration, oversample=0, segmentIndex=0,maxChannelsEnabled=8):
        """ Return (actualSampleInterval, noSamples, maxSamples). 
            
            oversample not used with ps4000a
        """
        self.oversample = oversample
        self.timebase = self.getTimeBaseNum(sampleInterval,maxChannelsEnabled)

        timebase_dt = self.getTimestepFromTimebase(self.timebase)

        noSamples = int(round(duration / timebase_dt))
        
        (self.sampleInterval, self.maxSamples) = \
            self._lowLevelGetTimebase(self.timebase, noSamples, oversample, segmentIndex)

        self.noSamples = noSamples
        self.sampleRate = 1.0 / self.sampleInterval
        return (self.sampleInterval, self.noSamples, self.maxSamples)

    def setNoOfCaptures(self, noCaptures):
        self._lowLevelSetNoOfCaptures(noCaptures)

    def memorySegments(self, noSegments):
        maxSamples = self._lowLevelMemorySegments(noSegments)
        self.maxSamples = maxSamples
        self.noSegments = noSegments
        return self.maxSamples

    def getMaxMemorySegments(self):
        segments = self._lowLevelGetMaxSegments()
        return segments
    
    def getTriggerTimeOffset(self, segmentIndex = 0):
        return self._lowLevelGetTriggerTimeOffset(segmentIndex)

    def getScaleAndOffset(self,channel):
        """ 
        Return the scale and offset used to convert the raw waveform
        
        To use: first multiply by the scale, then subtract the offset

        Returns a dictionary with keys scale and offset
        """ 
        if not isinstance(channel, int):
            channel = self.CHANNELS[channel]
        return {'scale': self.CHRange[channel] / float(self.getMaxValue()), 'offset': self.CHOffset[channel]}


    

    
    
    
    def getDataRawBulk(self, channel='A', numSamples=0, fromSegment=0,
        toSegment=None, downSampleRatio=1, downSampleMode=0, data=None):
        '''
        Get data recorded in block mode.
        '''
        if not isinstance(channel, int):
            channel = self.CHANNELS[channel]
        if toSegment is None:
            toSegment = self.noSegments - 1
        if numSamples == 0:
            numSamples = min(self.maxSamples, self.noSamples)

        numSegmentsToCopy = toSegment - fromSegment + 1
        if data is None:
            data = np.ascontiguousarray(
                np.zeros((numSegmentsToCopy, numSamples), dtype=np.int16)
                )

        # set up each row in the data array as a buffer for one of
        # the memory segments in the scope
        for i, segment in enumerate(range(fromSegment, toSegment+1)):
            self._lowLevelSetDataBufferBulk(channel,
                                            data[i],
                                            segment,
                                            downSampleMode)
        overflow = np.ascontiguousarray(
            np.zeros(numSegmentsToCopy, dtype=np.int16)
            )

        self._lowLevelGetValuesBulk(numSamples, fromSegment, toSegment,
            downSampleRatio, downSampleMode, overflow)

        return (data, numSamples, overflow)
 


    def setAWGSimple(self, waveform, duration, offsetVoltage=None,
                     pkToPk=None, indexMode="Single", shots=1, triggerType="Rising",
                     triggerSource="ScopeTrig"):
        """
        Set the AWG to output your desired wavefrom.

        If you require precise control of the timestep increment, you should use
        setSigGenAritrarySimpleDelaPhase instead


        Check setSigGenAritrarySimpleDelaPhase for parameter explanation

        Returns: The actual duration of the waveform

        """
        sampling_interval = duration / len(waveform)

        if not isinstance(indexMode, int):
            indexMode = self.AWG_INDEX_MODES[indexMode]

        if indexMode == self.AWG_INDEX_MODES["Single"]:
            pass
        elif indexMode == self.AWG_INDEX_MODES["Dual"]:
            sampling_interval /= 2
        elif indexMode == self.AWG_INDEX_MODES["Quad"]:
            sampling_interval /= 4

        deltaPhase = self.getAWGDeltaPhase(sampling_interval)

        actual_druation = self.setAWGSimpleDeltaPhase(waveform, deltaPhase, offsetVoltage,
                                                      pkToPk, indexMode, shots, triggerType,
                                                      triggerSource)

        return (actual_druation, deltaPhase)

    def setAWGSimpleDeltaPhase(self, waveform, deltaPhase, offsetVoltage=None,
                               pkToPk=None, indexMode="Single", shots=1, triggerType="Rising",
                               triggerSource="ScopeTrig"):
        """
        Specify deltaPhase between each sample instead of the total waveform duration.

        Returns the actual time duration of the waveform

        If pkToPk and offset Voltage are both set to None, then their values are computed as

        pkToPk = np.max(waveform) - np.min(waveform)
        offset = (np.max(waveform) + np.min(waveform)) / 2

        This should in theory minimize the quantization error in the ADC.

        else, the waveform shoudl be a numpy int16 type array with the containing
        waveform

        For the Quad mode, if offset voltage is not provided, then waveform[0]
        is assumed to be the offset. In quad mode, the offset voltage is the point of symmetry

        This is function provides a little more control than
        setAWGSimple in the sense that you are able to specify deltaPhase
        directly. It should only be used when deltaPhase becomes very large.

        Warning. Ideally, you would want this to be a power of 2 that way each
        sample is given out at exactly the same difference in time otherwise,
        if you give it something closer to .75 you would obtain

         T  | phase accumulator value | sample
         0  |      0                  |      0
         5  |      0.75               |      0
        10  |      1.50               |      1
        15  |      2.25               |      2
        20  |      3.00               |      3
        25  |      3.75               |      3

        notice how sample 0 and 3 were played twice  while others were only
        played once.
        This is why this low level function is exposed to the user so that he
        can control these edge cases

        I would suggest using something like this: if you care about obtaining
        evenly spaced samples at the expense of the precise duration of the your
        waveform
        To find the next highest power of 2
            always a smaller sampling interval than the one you asked for
        math.pow(2, math.ceil(math.log(deltaPhase, 2)))

        To find the next smaller power of 2
            always a larger sampling interval than the one you asked for
        math.pow(2, math.floor(math.log(deltaPhase, 2)))

        To find the nearest power of 2
        math.pow(2, int(math.log(deltaPhase, 2), + 0.5))
        """

        """
        This part of the code is written for the PS6403 (PS6403B if that matters)
        I don't really know a good way to differentiate between PS6403 versions

        It essentially does some autoscaling for the waveform so that it can be sent
        to the Picoscope to allow for maximum resolution from the DDS.

        I haven't tested if you can actually obtain more resolution than simply setting
        the DDS to output from -2 to +2

        I assume they have some type of adjustable gain and offset on their DDS
        allowing them to claim that they can get extremely high resolution.
        """

        if not isinstance(indexMode, int):
            indexMode = self.AWG_INDEX_MODES[indexMode]
        if not isinstance(triggerType, int):
            triggerType = self.SIGGEN_TRIG_TYPE[triggerType]
        if not isinstance(triggerSource, int):
            triggerSource = self.SIGGEN_TRIG_SOURCE[triggerSource]

        if waveform.dtype == np.int16:
            if offsetVoltage is None:
                offsetVoltage = 0.0
            if pkToPk is None:
                pkToPk = 2.0  # TODO: make this a per scope function assuming 2.0 V AWG
        else:
            if indexMode == self.AWG_INDEX_MODES["Quad"]:
                # Optimize for the Quad mode.
                """
                Quad mode. The generator outputs the contents of the buffer,
                then on its second pass through the buffer outputs the same
                data in reverse order. On the third and fourth passes
                it does the same but with a negative version of the data. This
                allows you to specify only the first quarter of a waveform with
                fourfold symmetry, such as a sine wave, and let the generator
                fill in the other three quarters.
                """
                if offsetVoltage is None:
                    offsetVoltage = waveform[0]
            else:
                # Nothing to do for the dual mode or the single mode
                if offsetVoltage is None:
                    offsetVoltage = (np.max(waveform) + np.min(waveform)) / 2

            # make a copy of the original data as to not clobber up the array
            waveform = waveform - offsetVoltage
            if pkToPk is None:
                pkToPk = np.max(np.absolute(waveform)) * 2

            # waveform should now be baised around 0
            # with
            #     max(waveform) = +pkToPk/2
            #     min(waveform) = -pkToPk/2
            waveform /= pkToPk

            # waveform should now be a number between -0.5 and +0.5

            waveform += 0.5
            # and now the waveform is between 0 and 1
            # inclusively???

            # now the waveform is properly quantized
            waveform *= (self.AWGMaxVal - self.AWGMinVal)
            waveform += self.AWGMinVal

            waveform.round(out=waveform)

            # convert to an int16 typqe as requried by the function
            waveform = np.array(waveform, dtype=np.int16)

            # funny floating point rounding errors
            waveform.clip(self.AWGMinVal, self.AWGMaxVal, out=waveform)

        self._lowLevelSetAWGSimpleDeltaPhase(waveform, deltaPhase, offsetVoltage, pkToPk,
                                             indexMode, shots, triggerType, triggerSource)

        timeIncrement = self.getAWGTimeIncrement(deltaPhase)
        waveform_duration = timeIncrement * len(waveform)

        #if   indexMode == self.AWG_INDEX_MODES["Single"]:
            #pass
        #elif
        if indexMode == self.AWG_INDEX_MODES["Dual"]:
            waveform_duration *= 2
        elif indexMode == self.AWG_INDEX_MODES["Quad"]:
            waveform_duration *= 4

        return waveform_duration

    def getAWGDeltaPhase(self, timeIncrement):
        """
        Return the deltaPhase integer used by the AWG.

        This is useful when you are trying to generate very fast waveforms when
        you are getting close to the limits of your waveform generator.

        For example, the PS6000's DDS phase accumulator increments by
        deltaPhase every AWGDACInterval.
        The top 2**self.AWGBufferAddressWidth bits indicate which sample is
        being output by the DDS.

        """
        samplingFrequency = 1 / timeIncrement
        deltaPhase = int(samplingFrequency / self.AWGDACFrequency *
                          2 ** (self.AWGPhaseAccumulatorSize - self.AWGBufferAddressWidth))
        return deltaPhase

    def getAWGTimeIncrement(self, deltaPhase):
        """
        Return the time between AWG samples given a certain deltaPhase.

        You should use this function in conjunction with
        getAWGDeltaPhase to obtain the actual timestep of AWG.

        """
        samplingFrequency = deltaPhase * self.AWGDACFrequency / \
                            2 ** (self.AWGPhaseAccumulatorSize - self.AWGBufferAddressWidth)
        return 1 / samplingFrequency

    def setResolution(self, resolution):
        """For 5000-series scopes ONLY, sets the resolution. Error on other devices."""
        self._lowLevelSetDeviceResolution(self.ADC_RESOLUTIONS[resolution])

    def checkResult(self, ec):
        """ Check result of function calls, raise exception if not 0. """
        # NOTE: This will break some oscilloscopes that are powered by USB.
        # Some of the newer scopes, can actually be powered by USB and will return
        # a useful value. That should be given back to the user.
        # I guess we can deal with these edge cases in the functions themselves
        if ec == 0:
            return

        else:
            #print("Error Num: 0x%x"%ec)
            ecName = self.errorNumToName(ec)
            ecDesc = self.errorNumToDesc(ec)
            raise IOError('Error calling %s: %s (%s)' % (str(inspect.stack()[1][3]), ecName, ecDesc))

    def errorNumToName(self, num):
        """ Return the name of the error as a string. """
        for t in self.PICO_INFO:
            if t[0] == num:
                return t[1]

    def errorNumToDesc(self, num):
        """ Return the description of the error as a string. """
        for t in self.PICO_INFO:
            if t[0] == num:
                try:
                    return t[2]
                except IndexError:
                    return ""

    def changePowerSource(self, powerstate):
        """ Change the powerstate of the scope. Valid only for PS54XXA/B? """
        # I should probably make an enumerate table for these two cases, but htey are in fact just the
        # error codes. Picoscope should have made it a separate enumerate themselves.
        # I'll just keep this hack for now
        if not isinstance(powerstate, int):
            if powerstate == "PICO_POWER_SUPPLY_CONNECTED":
                powerstate = 0x119
            elif powerstate == "PICO_POWER_SUPPLY_NOT_CONNECTED":
                powerstate = 0x11A
        self._lowLevelChangePowerSource(powerstate)

    ### Info codes - copied PicoStatus.h.
    PICO_INFO = [[0x00000000, "PICO_OK", "The PicoScope is functioning correctly."],
        [0x00000001, "PICO_MAX_UNITS_OPENED", "An attempt has been made to open more than <API>_MAX_UNITS."],
        [0x00000002, "PICO_MEMORY_FAIL", "Not enough memory could be allocated on the host machine."],
        [0x00000003, "PICO_NOT_FOUND", "No Pico Technology device could be found."],
        [0x00000004, "PICO_FW_FAIL", "Unable to download firmware."],
        [0x00000005, "PICO_OPEN_OPERATION_IN_PROGRESS", "The driver is busy opening a device."],
        [0x00000006, "PICO_OPERATION_FAILED", "An unspecified failure occurred."],
        [0x00000007, "PICO_NOT_RESPONDING", "The PicoScope is not responding to commands from the PC."],
        [0x00000008, "PICO_CONFIG_FAIL", "The configuration information in the PicoScope is corrupt or missing."],
        [0x00000009, "PICO_KERNEL_DRIVER_TOO_OLD", "The picopp.sys file is too old to be used with the device driver."],
        [0x0000000A, "PICO_EEPROM_CORRUPT", "The EEPROM has become corrupt, so the device will use a default setting."],
        [0x0000000B, "PICO_OS_NOT_SUPPORTED", "The operating system on the PC is not supported by this driver."],
        [0x0000000C, "PICO_INVALID_HANDLE", "There is no device with the handle value passed."],
        [0x0000000D, "PICO_INVALID_PARAMETER", "A parameter value is not valid."],
        [0x0000000E, "PICO_INVALID_TIMEBASE", "The timebase is not supported or is invalid."],
        [0x0000000F, "PICO_INVALID_VOLTAGE_RANGE", "The voltage range is not supported or is invalid."],
        [0x00000010, "PICO_INVALID_CHANNEL", "The channel number is not valid on this device or no channels have been set."],
        [0x00000011, "PICO_INVALID_TRIGGER_CHANNEL", "The channel set for a trigger is not available on this device."],
        [0x00000012, "PICO_INVALID_CONDITION_CHANNEL", "The channel set for a condition is not available on this device."],
        [0x00000013, "PICO_NO_SIGNAL_GENERATOR", "The device does not have a signal generator."],
        [0x00000014, "PICO_STREAMING_FAILED", "Streaming has failed to start or has stopped without user request."],
        [0x00000015, "PICO_BLOCK_MODE_FAILED", "Block failed to start - a parameter may have been set wrongly."],
        [0x00000016, "PICO_NULL_PARAMETER", "A parameter that was required is NULL."],
        [0x00000017, "PICO_ETS_MODE_SET", "The current functionality is not available while using ETS capture mode."],
        [0x00000018, "PICO_DATA_NOT_AVAILABLE", "No data is available from a run block call."],
        [0x00000019, "PICO_STRING_BUFFER_TO_SMALL", "The buffer passed for the information was too small."],
        [0x0000001A, "PICO_ETS_NOT_SUPPORTED", "ETS is not supported on this device."],
        [0x0000001B, "PICO_AUTO_TRIGGER_TIME_TO_SHORT", "The auto trigger time is less than the time it will take to collect the pre-trigger data."],
        [0x0000001C, "PICO_BUFFER_STALL", "The collection of data has stalled as unread data would be overwritten."],
        [0x0000001D, "PICO_TOO_MANY_SAMPLES", "Number of samples requested is more than available in the current memory segment."],
        [0x0000001E, "PICO_TOO_MANY_SEGMENTS", "Not possible to create number of segments requested."],
        [0x0000001F, "PICO_PULSE_WIDTH_QUALIFIER", "A null pointer has been passed in the trigger function or one of the parameters is out of range."],
        [0x00000020, "PICO_DELAY", "One or more of the hold-off parameters are out of range."],
        [0x00000021, "PICO_SOURCE_DETAILS", "One or more of the source details are incorrect."],
        [0x00000022, "PICO_CONDITIONS", "One or more of the conditions are incorrect."],
        [0x00000023, "PICO_USER_CALLBACK", "The driver's thread is currently in the <API>Ready callback function and therefore the action cannot be carried out."],
        [0x00000024, "PICO_DEVICE_SAMPLING", "An attempt is being made to get stored data while streaming. Either stop streaming by calling <API>Stop, or use <API>GetStreamingLatestValues."],
        [0x00000025, "PICO_NO_SAMPLES_AVAILABLE", "Data is unavailable because a run has not been completed."],
        [0x00000026, "PICO_SEGMENT_OUT_OF_RANGE", "The memory segment index is out of range."],
        [0x00000027, "PICO_BUSY", "The device is busy so data cannot be returned yet."],
        [0x00000028, "PICO_STARTINDEX_INVALID", "The start time to get stored data is out of range."],
        [0x00000029, "PICO_INVALID_INFO", "The information number requested is not a valid number."],
        [0x0000002A, "PICO_INFO_UNAVAILABLE", "The handle is invalid so no information is available about the device. Only PICO_DRIVER_VERSION is available."],
        [0x0000002B, "PICO_INVALID_SAMPLE_INTERVAL", "The sample interval selected for streaming is out of range."],
        [0x0000002C, "PICO_TRIGGER_ERROR", "ETS is set but no trigger has been set. A trigger setting is required for ETS."],
        [0x0000002D, "PICO_MEMORY", "Driver cannot allocate memory."],
        [0x0000002E, "PICO_SIG_GEN_PARAM", "Incorrect parameter passed to the signal generator."],
        [0x0000002F, "PICO_SHOTS_SWEEPS_WARNING", "Conflict between the shots and sweeps parameters sent to the signal generator."],
        [0x00000030, "PICO_SIGGEN_TRIGGER_SOURCE", "A software trigger has been sent but the trigger source is not a software trigger."],
        [0x00000031, "PICO_AUX_OUTPUT_CONFLICT", "An <API>SetTrigger call has found a conflict between the trigger source and the AUX output enable."],
        [0x00000032, "PICO_AUX_OUTPUT_ETS_CONFLICT", "ETS mode is being used and AUX is set as an input."],
        [0x00000033, "PICO_WARNING_EXT_THRESHOLD_CONFLICT", "Attempt to set different EXT input thresholds set for signal generator and oscilloscope trigger."],
        [0x00000034, "PICO_WARNING_AUX_OUTPUT_CONFLICT", "An <API>SetTrigger... function has set AUX as an output and the signal generator is using it as a trigger."],
        [0x00000035, "PICO_SIGGEN_OUTPUT_OVER_VOLTAGE", "The combined peak to peak voltage and the analog offset voltage exceed the maximum voltage the signal generator can produce."],
        [0x00000036, "PICO_DELAY_NULL", "NULL pointer passed as delay parameter."],
        [0x00000037, "PICO_INVALID_BUFFER", "The buffers for overview data have not been set while streaming."],
        [0x00000038, "PICO_SIGGEN_OFFSET_VOLTAGE", "The analog offset voltage is out of range."],
        [0x00000039, "PICO_SIGGEN_PK_TO_PK", "The analog peak-to-peak voltage is out of range."],
        [0x0000003A, "PICO_CANCELLED", "A block collection has been cancelled."],
        [0x0000003B, "PICO_SEGMENT_NOT_USED", "The segment index is not currently being used."],
        [0x0000003C, "PICO_INVALID_CALL", "The wrong GetValues function has been called for the collection mode in use."],
        [0x0000003D, "PICO_GET_VALUES_INTERRUPTED", ""],
        [0x0000003F, "PICO_NOT_USED", "The function is not available."],
        [0x00000040, "PICO_INVALID_SAMPLERATIO", "The aggregation ratio requested is out of range."],
        [0x00000041, "PICO_INVALID_STATE", "Device is in an invalid state."],
        [0x00000042, "PICO_NOT_ENOUGH_SEGMENTS", "The number of segments allocated is fewer than the number of captures requested."],
        [0x00000043, "PICO_DRIVER_FUNCTION", "A driver function has already been called and not yet finished. Only one call to the driver can be made at any one time."],
        [0x00000044, "PICO_RESERVED", "Not used"],
        [0x00000045, "PICO_INVALID_COUPLING", "An invalid coupling type was specified in <API>SetChannel."],
        [0x00000046, "PICO_BUFFERS_NOT_SET", "An attempt was made to get data before a data buffer was defined."],
        [0x00000047, "PICO_RATIO_MODE_NOT_SUPPORTED", "The selected downsampling mode (used for data reduction) is not allowed."],
        [0x00000048, "PICO_RAPID_NOT_SUPPORT_AGGREGATION", "Aggregation was requested in rapid block mode."],
        [0x00000049, "PICO_INVALID_TRIGGER_PROPERTY", "An invalid parameter was passed to <API>SetTriggerChannelProperties."],
        [0x0000004A, "PICO_INTERFACE_NOT_CONNECTED", "The driver was unable to contact the oscilloscope."],
        [0x0000004B, "PICO_RESISTANCE_AND_PROBE_NOT_ALLOWED", "Resistance-measuring mode is not allowed in conjunction with the specified probe."],
        [0x0000004C, "PICO_POWER_FAILED", "The device was unexpectedly powered down."],
        [0x0000004D, "PICO_SIGGEN_WAVEFORM_SETUP_FAILED", "A problem occurred in <API>SetSigGenBuiltIn or <API>SetSigGenArbitrary."],
        [0x0000004E, "PICO_FPGA_FAIL", "FPGA not successfully set up."],
        [0x0000004F, "PICO_POWER_MANAGER", ""],
        [0x00000050, "PICO_INVALID_ANALOGUE_OFFSET", "An impossible analog offset value was specified in <API>SetChannel."],
        [0x00000051, "PICO_PLL_LOCK_FAILED", "There is an error within the device hardware."],
        [0x00000052, "PICO_ANALOG_BOARD", "There is an error within the device hardware."],
        [0x00000053, "PICO_CONFIG_FAIL_AWG", "Unable to configure the signal generator."],
        [0x00000054, "PICO_INITIALISE_FPGA", "The FPGA cannot be initialized, so unit cannot be opened."],
        [0x00000056, "PICO_EXTERNAL_FREQUENCY_INVALID", "The frequency for the external clock is not within 15% of the nominal value."],
        [0x00000057, "PICO_CLOCK_CHANGE_ERROR", "The FPGA could not lock the clock signal."],
        [0x00000058, "PICO_TRIGGER_AND_EXTERNAL_CLOCK_CLASH", "You are trying to configure the AUX input as both a trigger and a reference clock."],
        [0x00000059, "PICO_PWQ_AND_EXTERNAL_CLOCK_CLASH", "You are trying to congfigure the AUX input as both a pulse width qualifier and a reference clock."],
        [0x0000005A, "PICO_UNABLE_TO_OPEN_SCALING_FILE", "The requested scaling file cannot be opened."],
        [0x0000005B, "PICO_MEMORY_CLOCK_FREQUENCY", "The frequency of the memory is reporting incorrectly."],
        [0x0000005C, "PICO_I2C_NOT_RESPONDING", "The I2C that is being actioned is not responding to requests."],
        [0x0000005D, "PICO_NO_CAPTURES_AVAILABLE", "There are no captures available and therefore no data can be returned."],
        [0x0000005F, "PICO_TOO_MANY_TRIGGER_CHANNELS_IN_USE", "The number of trigger channels is greater than 4, except for a PS4824 where 8 channels are allowed for rising/falling/rising_or_falling trigger directions."],
        [0x00000060, "PICO_INVALID_TRIGGER_DIRECTION", "When more than 4 trigger channels are set on a PS4824 and the direction is out of range."],
        [0x00000061, "PICO_INVALID_TRIGGER_STATES", " When more than 4 trigger channels are set and their trigger condition states are not <API>_CONDITION_TRUE."],
        [0x0000005E, "PICO_NOT_USED_IN_THIS_CAPTURE_MODE", "The capture mode the device is currently running in does not support the current request."],
        [0x00000103, "PICO_GET_DATA_ACTIVE", ""],
        [0x00000104, "PICO_IP_NETWORKED", "The device is currently connected via the IP Network socket and thus the call made is not supported."],
        [0x00000105, "PICO_INVALID_IP_ADDRESS", "An incorrect IP address has been passed to the driver."],
        [0x00000106, "PICO_IPSOCKET_FAILED", "The IP socket has failed."],
        [0x00000107, "PICO_IPSOCKET_TIMEDOUT", "The IP socket has timed out."],
        [0x00000108, "PICO_SETTINGS_FAILED", "Failed to apply the requested settings."],
        [0x00000109, "PICO_NETWORK_FAILED", "The network connection has failed."],
        [0x0000010A, "PICO_WS2_32_DLL_NOT_LOADED", "Unable to load the WS2 DLL."],
        [0x0000010B, "PICO_INVALID_IP_PORT", "The specified IP port is invalid."],
        [0x0000010C, "PICO_COUPLING_NOT_SUPPORTED", "The type of coupling requested is not supported on the opened device."],
        [0x0000010D, "PICO_BANDWIDTH_NOT_SUPPORTED", "Bandwidth limiting is not supported on the opened device."],
        [0x0000010E, "PICO_INVALID_BANDWIDTH", "The value requested for the bandwidth limit is out of range."],
        [0x0000010F, "PICO_AWG_NOT_SUPPORTED", "The arbitrary waveform generator is not supported by the opened device."],
        [0x00000110, "PICO_ETS_NOT_RUNNING", "Data has been requested with ETS mode set but run block has not been called, or stop has been called."],
        [0x00000111, "PICO_SIG_GEN_WHITENOISE_NOT_SUPPORTED", "White noise output is not supported on the opened device."],
        [0x00000112, "PICO_SIG_GEN_WAVETYPE_NOT_SUPPORTED", "The wave type requested is not supported by the opened device."],
        [0x00000113, "PICO_INVALID_DIGITAL_PORT", "The requested digital port number is out of range (MSOs only)."],
        [0x00000114, "PICO_INVALID_DIGITAL_CHANNEL", "The digital channel is not in the range <API>_DIGITAL_CHANNEL0 to <API>_DIGITAL_CHANNEL15, the digital channels that are supported."],
        [0x00000115, "PICO_INVALID_DIGITAL_TRIGGER_DIRECTION", "The digital trigger direction is not a valid trigger direction and should be equal in value to one of the <API>_DIGITAL_DIRECTION enumerations."],
        [0x00000116, "PICO_SIG_GEN_PRBS_NOT_SUPPORTED", "Signal generator does not generate pseudo-random binary sequence."],
        [0x00000117, "PICO_ETS_NOT_AVAILABLE_WITH_LOGIC_CHANNELS", "When a digital port is enabled, ETS sample mode is not available for use."],
        [0x00000118, "PICO_WARNING_REPEAT_VALUE", ""],
        [0x00000119, "PICO_POWER_SUPPLY_CONNECTED", "4-channel scopes only: The DC power supply is connected."],
        [0x0000011A, "PICO_POWER_SUPPLY_NOT_CONNECTED", "4-channel scopes only: The DC power supply is not connected."],
        [0x0000011B, "PICO_POWER_SUPPLY_REQUEST_INVALID", "Incorrect power mode passed for current power source."],
        [0x0000011C, "PICO_POWER_SUPPLY_UNDERVOLTAGE", "The supply voltage from the USB source is too low."],
        [0x0000011D, "PICO_CAPTURING_DATA", "The oscilloscope is in the process of capturing data."],
        [0x0000011E, "PICO_USB3_0_DEVICE_NON_USB3_0_PORT", "A USB 3.0 device is connected to a non-USB 3.0 port."],
        [0x0000011F, "PICO_NOT_SUPPORTED_BY_THIS_DEVICE", "A function has been called that is not supported by the current device."],
        [0x00000120, "PICO_INVALID_DEVICE_RESOLUTION", "The device resolution is invalid (out of range)."],
        [0x00000121, "PICO_INVALID_NUMBER_CHANNELS_FOR_RESOLUTION", "The number of channels that can be enabled is limited in 15 and 16-bit modes. (Flexible Resolution Oscilloscopes only)"],
        [0x00000122, "PICO_CHANNEL_DISABLED_DUE_TO_USB_POWERED", "USB power not sufficient for all requested channels."],
        [0x00000123, "PICO_SIGGEN_DC_VOLTAGE_NOT_CONFIGURABLE", "The signal generator does not have a configurable DC offset."],
        [0x00000124, "PICO_NO_TRIGGER_ENABLED_FOR_TRIGGER_IN_PRE_TRIG", "An attempt has been made to define pre-trigger delay without first enabling a trigger."],
        [0x00000125, "PICO_TRIGGER_WITHIN_PRE_TRIG_NOT_ARMED", "An attempt has been made to define pre-trigger delay without first arming a trigger."],
        [0x00000126, "PICO_TRIGGER_WITHIN_PRE_NOT_ALLOWED_WITH_DELAY", "Pre-trigger delay and post-trigger delay cannot be used at the same time."],
        [0x00000127, "PICO_TRIGGER_INDEX_UNAVAILABLE", "The array index points to a nonexistent trigger."],
        [0x00000128, "PICO_AWG_CLOCK_FREQUENCY", ""],
        [0x00000129, "PICO_TOO_MANY_CHANNELS_IN_USE", "There are more 4 analog channels with a trigger condition set."],
        [0x0000012A, "PICO_NULL_CONDITIONS", "The condition parameter is a null pointer."],
        [0x0000012B, "PICO_DUPLICATE_CONDITION_SOURCE", "There is more than one condition pertaining to the same channel."],
        [0x0000012C, "PICO_INVALID_CONDITION_INFO", "The parameter relating to condition information is out of range."],
        [0x0000012D, "PICO_SETTINGS_READ_FAILED", "Reading the metadata has failed."],
        [0x0000012E, "PICO_SETTINGS_WRITE_FAILED", "Writing the metadata has failed."],
        [0x0000012F, "PICO_ARGUMENT_OUT_OF_RANGE", "A parameter has a value out of the expected range."],
        [0x00000130, "PICO_HARDWARE_VERSION_NOT_SUPPORTED", "The driver does not support the hardware variant connected."],
        [0x00000131, "PICO_DIGITAL_HARDWARE_VERSION_NOT_SUPPORTED", "The driver does not support the digital hardware variant connected."],
        [0x00000132, "PICO_ANALOGUE_HARDWARE_VERSION_NOT_SUPPORTED", "The driver does not support the analog hardware variant connected."],
        [0x00000133, "PICO_UNABLE_TO_CONVERT_TO_RESISTANCE", "Converting a channel's ADC value to resistance has failed."],
        [0x00000134, "PICO_DUPLICATED_CHANNEL", "The channel is listed more than once in the function call."],
        [0x00000135, "PICO_INVALID_RESISTANCE_CONVERSION", "The range cannot have resistance conversion applied."],
        [0x00000136, "PICO_INVALID_VALUE_IN_MAX_BUFFER", "An invalid value is in the max buffer."],
        [0x00000137, "PICO_INVALID_VALUE_IN_MIN_BUFFER", "An invalid value is in the min buffer."],
        [0x00000138, "PICO_SIGGEN_FREQUENCY_OUT_OF_RANGE", "When calculating the frequency for phase conversion, the frequency is greater than that supported by the current variant."],
        [0x00000139, "PICO_EEPROM2_CORRUPT", "The device's EEPROM is corrupt. Contact Pico Technology support: https://www.picotech.com/tech-support."],
        [0x0000013A, "PICO_EEPROM2_FAIL", "The EEPROM has failed."],
        [0x0000013B, "PICO_SERIAL_BUFFER_TOO_SMALL", "The serial buffer is too small for the required information."],
        [0x0000013C, "PICO_SIGGEN_TRIGGER_AND_EXTERNAL_CLOCK_CLASH", "The signal generator trigger and the external clock have both been set. This is not allowed."],
        [0x0000013D, "PICO_WARNING_SIGGEN_AUXIO_TRIGGER_DISABLED", "The AUX trigger was enabled and the external clock has been enabled, so the AUX has been automatically disabled."],
        [0x00000013E, "PICO_SIGGEN_GATING_AUXIO_NOT_AVAILABLE", "The AUX I/O was set as a scope trigger and is now being set as a signal generator gating trigger. This is not allowed."],
        [0x00000013F, "PICO_SIGGEN_GATING_AUXIO_ENABLED", "The AUX I/O was set by the signal generator as a gating trigger and is now being set as a scope trigger. This is not allowed."],
        [0x000000141, "PICO_TEMPERATURE_TYPE_INVALID", "The temperature type is out of range"],
        [0x000000142, "PICO_TEMPERATURE_TYPE_NOT_SUPPORTED", "A requested temperature type is not supported on this device"],
        [0x01000000, "PICO_DEVICE_TIME_STAMP_RESET", "The time stamp per waveform segment has been reset."],
        [0x10000000, "PICO_WATCHDOGTIMER", "An internal erorr has occurred and a watchdog timer has been called."],
        [0x10000001, "PICO_IPP_NOT_FOUND", "The picoipp.dll has not been found."],
        [0x10000002, "PICO_IPP_NO_FUNCTION", "A function in the picoipp.dll does not exist."],
        [0x10000003, "PICO_IPP_ERROR", "The Pico IPP call has failed."],
        [0x10000004, "PICO_SHADOW_CAL_NOT_AVAILABLE", "Shadow calibration is not available on this device."],
        [0x10000005, "PICO_SHADOW_CAL_DISABLED", "Shadow calibration is currently disabled."],
        [0x10000006, "PICO_SHADOW_CAL_ERROR", "Shadow calibration error has occurred."],
        [0x10000007, "PICO_SHADOW_CAL_CORRUPT", "The shadow calibration is corrupt."]]