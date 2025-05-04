#!/usr/bin/python

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

try:
    import wavio
except:
    pass


class nimRumTxReadFile:
    def __init__(self):
        pass

    def open(self, fileName):

        try:
            wav = wavio.read(fileName)
            self.available = True
        except:
            self.available = False
            return None, None

        sampleBytes = wav.sampwidth

        [self.bufLen, self.numOfChannels] = wav.data.shape
        if self.numOfChannels == None:
            self.numOfChannels = 1

        self.buf = wav.data.T

        print(
            "Read:{} [ Channels:{}, SampleSize:{} bytes, Rate:{}Hz, Frames:{}, Duration:{} seconds ]".format(
                fileName,
                self.numOfChannels,
                sampleBytes,
                wav.rate,
                self.bufLen,
                self.bufLen / wav.rate,
            )
        )

        self.bufPos = 0

        return wav.rate, sampleBytes

    def read(self, frames):

        if not self.available:
            return None, None

        bufRemaning = self.bufLen - self.bufPos
        framesToRead = frames
        framesLeft = 0
        if bufRemaning < framesToRead:
            framesToRead = bufRemaning
            framesLeft = frames - framesToRead

        dataOut = [None] * self.numOfChannels
        ch = self.numOfChannels - 1
        while ch >= 0:
            dataOut[ch] = [0] * frames

            dataOut[ch][0:framesToRead] = self.buf[ch][
                self.bufPos : self.bufPos + framesToRead
            ]

            if framesLeft > 0:
                dataOut[ch][framesToRead : framesToRead + framesLeft] = self.buf[ch][
                    0:framesLeft
                ]

            ch = ch - 1

        self.bufPos = self.bufPos + frames
        self.bufPos = self.bufPos % self.bufLen

        return dataOut, self.numOfChannels
