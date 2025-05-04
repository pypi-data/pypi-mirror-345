#!/usr/bin/python3

#/******************************************************************************
# *  COPYRIGHT (c) 2021-2025, AbtAudio AB, All rights reserved.
# *
# *  The copyright to the computer program(s) herein is the property of
# *  AbtAudio AB. The computer programs(s) may implement properties protected by
# *  patent(s) such as arising from SE544478C2, US12034828B2 or WO2021/220149.
# *
# *  Redistribution in any form, with or without modification, is only permitted
# *  with the written permission from AbtAudio AB.
# *
# *  The computer program(s) may be used for private purposes and for evaluation
# *  purposes.
# *
# *  The computer program(s) may NOT be used for any commercial purposes without
# *  the written permission from AbtAudio AB.
# *
# *  The computer program(s) are provided as is, without any warranties, but
# *  feedback in form of suggestions for improvements is encouraged.
# ******************************************************************************/

import math

nimRumToneGenAvail = False
try:
    import struct
    import numpy as np
    nimRumToneGenAvail = True

except Exception as e:
    print("NOTE: nimRumToneGen not available: {}".format(str(e)))

class nimRumToneGen:
    def __init__(self, mode, sampleRate, bytePerSample, volume):

        if not nimRumToneGenAvail:
            return

        self.mode = mode
        self.sampleRate = sampleRate
        self.bytePerSample = bytePerSample

        self.volume = 100
        if volume != None:
            self.volume = volume
        if self.volume > 100:
            self.volume = 100
        if self.volume < 0:
            self.volume = 0
        self.volumeFrac = float(self.volume)/100.0

        self.amplitudeMax = 2 ** ((self.bytePerSample * 8) - 1)
        self.amplitudeMax -= 2  # Safety margin, including adding of noise
        self.amp = int(round(self.amplitudeMax * self.volumeFrac))

        self.bufPos = 0

        if self.mode.lower() == 'sinus':
            self.generate_sinus()
        elif self.mode.lower() == 'spikes':
            self.generate_spikes()
        elif self.mode.lower() == 'chirp':
            self.generate_chirp()
        else:
            print("ERROR: nimRumToneGen got unknown mode: {}".format(self.mode))

    def read(self, frames, dataOutBuf):

        if not nimRumToneGenAvail:
            print("ERROR: nimRumToneGen not available")
            return

        dataOut = np.zeros(frames, dtype=int)

        bufRemaning = len(self.buf) - self.bufPos
        framesToRead = frames
        framesLeft = 0
        if bufRemaning < framesToRead:
            framesToRead = bufRemaning
            framesLeft = frames - framesToRead

        dataOut[0:framesToRead] = self.buf[
            self.bufPos : self.bufPos + framesToRead
        ]

        if framesLeft > 0:
            dataOut[framesToRead : framesToRead + framesLeft] = self.buf[
                0:framesLeft
            ]

        self.bufPos = self.bufPos + frames
        self.bufPos = self.bufPos % len(self.buf)

        dataOutBuf[0:4*len(dataOut)] = self._convertToBytes(dataOut)


    def _convertToBytes(self, din):
        return struct.pack('@%il' % len(din), *din)

    ########################
    #### TEST PATTERNS  ####
    ########################
    def generate_sinus(self):
        freq = 1000.0
        seconds = 10.0
        self.buf = self.getSinus(freq, seconds)

    def generate_spikes(self):
        freq = 500.0
        self.buf = self.getSilence(0.5)
        self.buf = np.append(self.buf, self.getSpike(freq))
        self.buf = np.append(self.buf, self.getSilence(0.5))

    def generate_chirp(self):
        freqStart = 20.0
        freqStop = 20000.0
        seconds = 60.0
        self.buf = self.getSilence(0.5)
        self.buf = np.append(self.buf, self.getChirp(freqStart, freqStop, seconds))
        self.buf = np.append(self.buf, self.getSilence(0.5))

    def generate_magic_sqr_wave(self):
        # TODO: Implement
        pass

    ##############################
    #### GET SIGNAL FUNCTIONS ####
    ##############################
    def getSinus(self, freq=5000, lenInSecs=1):
        """
        Will add integer number of periods so result might not be exactly lenInSecs long
        """

        samplesPerPeriod = float(self.sampleRate) / float(freq)
        totPeriods = int(round(freq * lenInSecs))
        totSamples = int(round(samplesPerPeriod * totPeriods))

        t = np.arange(0, totSamples)
        val = self.amp * np.sin(2 * np.pi * t * float(freq) / float(self.sampleRate))

        # Hide rounding artifacts by randomly round up/down
        noiseParticles = np.random.random(totSamples)
        dOut = (np.rint(noiseParticles + val)).astype(int)
        return dOut

    def getChirp(self, freqStart=100, freqStop=200, lenInSecs=1.0):

        totSamples = int(round(self.sampleRate * float(lenInSecs)))
        t = np.linspace(0, lenInSecs, totSamples)
        k = (freqStop/freqStart)
        kExp = t/(lenInSecs)
        f = freqStart * ( np.power(k,kExp) -1 )
        fi = 2*np.pi*f/np.log(k)
        dOutRaw = np.cos( fi )

        dOutRaw *= self.amp

        # Hide rounding artifacts by randomly round up/down
        noiseParticles = np.random.random(totSamples)
        dOut = (np.rint(noiseParticles + dOutRaw)).astype(int)
        return dOut

    def getSqr(self, freq=5000, lenInSecs=1):
        """
        Will add integer number of periods so result might not be exactly lenInSecs long
        """
        dOut = []
        # For number of periods
        for i in range(0, int(lenInSecs * freq)):
            # Add period
            for j in range(0, int(self.sampleRate / (2 * freq))):  # Low
                dOut.append(-self.amp)
            for j in range(0, int(self.sampleRate / (2 * freq))):  # High
                dOut.append(self.amp)
        return (np.rint(np.array(dOut))).astype(int)

    def getSpike(self, freq=1000):
        spikeHalfPulseWidth = int(self.sampleRate / (2 * freq))

        dOut = np.full(spikeHalfPulseWidth, -self.amp)
        dOut = np.append(dOut, np.full(spikeHalfPulseWidth, self.amp))
        return (np.rint(dOut)).astype(int)

    def getSilence(self, lenInSecs=1):
        totSamples = int(round(self.sampleRate * lenInSecs))
        return np.zeros(totSamples, dtype=int)


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    mode = 'chirp'
    sampleRate = 48000
    bytePerSample = 2
    volume = 1.0

    o = nimRumToneGen(mode, sampleRate, bytePerSample, volume)

    freq = 10.0
    freqStart = 2.0
    freqStop = 20.0
    lenInSecs = 1.0

    sinTest = o.getSinus(freq, lenInSecs)
    chirpTest = o.getChirp(freqStart, freqStop, lenInSecs)
    sqrTest = o.getSqr(freq, lenInSecs)
    spikeTest = o.getSpike(freq*2)
    silenceTest = o.getSilence(lenInSecs)

    plt.figure(1)
    plt.title("ABC")

    plt.plot(sinTest, label='sinTest')
    plt.plot(chirpTest, label='chirpTest')
    plt.plot(sqrTest, label='sqrTest')
    plt.plot(spikeTest, label='spikeTest')
    plt.plot(silenceTest, label='silenceTest')

    plt.legend()
    plt.show()
