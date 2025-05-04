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

import sys
import os

from nimRum import libNimRumTx_py as txLib

capLibAvail = True
try:
    from nimRum import libNimRumAlsaCapture_py as capLib
except:
    capLibAvail = False
    print('Audio capture module NOT available on this platform')


from nimRum import nimRumPyCommon
from nimRum import nimRumTxReadFile_wavio
from nimRum import nimRumTxCfg
from nimRum import nimRumPyLed
from nimRum import nimRumToneGen


class nimRumTx(nimRumPyCommon.nimRumPyCommon):
    def __init__(self, configFile="./txConfig.yaml"):
        nimRumPyCommon.nimRumPyCommon.__init__(self, meName=os.path.basename(__file__))

        self.cfg = nimRumTxCfg.nimRumTxCfg(
            self.volumeSet, self.latencySet, configFile=configFile
        )
        self.led = nimRumPyLed.nimRumPyLed()
        self.file = nimRumTxReadFile_wavio.nimRumTxReadFile()
        self.tonGen = {}

    def volumeSet(self):
        for cliId in self.cfg.cliIds:
            txLib.c_libNimRumTxSetVolume(cliId, self.cfg.getVolume(cliId))

    def latencySet(self, cliId=None, error=0):
        if cliId == None:  # Set for all clients
            for cliId in self.cfg.cliIds:
                txLib.c_libNimRumTxSetLatency(cliId, self.cfg.getLatency(cliId) + error)
        else:  # Set for specific client
            txLib.c_libNimRumTxSetLatency(cliId, self.cfg.getLatency(cliId) + error)

    def assignChannels(self, activeChannels):
        for cliId in self.cfg.cliIds:
            chLst = [0]

            if activeChannels > 2:
                chLst = self.cfg.multiChannelMap[cliId]
            elif activeChannels == 2:
                chLst = self.cfg.stereoChannelMap[cliId]
            else:
                pass

            txLib.c_libNimRumTxSetChannel(cliId, chLst)

    def runTx(self, fileName=None):
        if (capLibAvail == False) and (fileName == None):
            print("Audio capture lib not available. Can only transmit audio from file, like this:")
            print("runNimRumTx yourFavouriteSong.wav")
            quit()

        # INIT SOURCE TO PLAY
        bytePerSample = 2  # This is what libNimRumAlsaCapture supports
        sampleRate = 48000  # This is what libNimRumAlsaCapture supports

        if fileName == None:
            # INIT SPDIF INPUT
            frameStretchEnable = 1
            if capLib.c_libNimRumAlsaCapture_init(frameStretchEnable, self.cfg.pcmDevInputName) != 0:
                self.lclPrint("CAPT init failed")
                quit()

        else:
            # OPEN INPUT FILE
            (sampleRate, bytePerSample) = self.file.open(fileName)


        # INIT TONEGENERATOR(S)
        for virtCh in self.cfg.virtualChannels:
            if "toneGeneratorMode" in virtCh:
                volume = None
                if 'toneGeneratorVolume' in virtCh:
                    volume = virtCh["toneGeneratorVolume"]
                mode = virtCh["toneGeneratorMode"]
                self.tonGen[ virtCh["channelNumber"] ] = nimRumToneGen.nimRumToneGen(mode, sampleRate, bytePerSample, volume)

        # INIT TX
        if txLib.c_libNimRumTxInit(self.getMyUniqueId(), self.cfg.cliNames) != 0:
            self.lclPrint("TX Init failed")
            quit()

        (res, framesPerInterval) = txLib.c_libNimRumTxConfigure(
            bytePerSample, sampleRate, self.cfg.codec
        )
        if res != 0:
            self.lclPrint("TX Cfg failed")
            quit()

        # txLib.c_libNimRumTXForceWave(0) # prezo30 TODO: Add to cfg yaml file
        txLib.c_libNimRumTxLogs(self.cfg.logEnable)
        txLib.c_libNimRumTxSetLogsPath(self.cfg.logPath)

        self.latencySet()
        self.volumeSet()

        ###########################################################
        # LOOP FOREVER (Until Ctrl-C, or severe error)
        ###########################################################
        activeChannels = -1  # -1 to force initial configureation
        activeChannelsNew = 0
        dataValid = 0

        # INIT ARRAY FOR DATA TRANSFER
        maxChannels = 32
        dataOut = []
        while maxChannels > 0:
            dataOut.append(bytearray(4 * 2400))
            maxChannels = maxChannels - 1

        while self.run == 1:

            if fileName == None:
                # GET DATA - FROM SPDIF
                # Will fill channel 0..7
                (
                    res,
                    samplesQueued,
                    activeChannelsNew,
                    layout,
                    frameTimeActual,
                    dataValid,
                ) = capLib.c_libNimRumAlsaCapture_getData(dataOut, framesPerInterval)

            else:
                # GET DATA - FROM FILE
                # TODO: Mono file make tone generator to fail?
                dataArr, activeChannelsNew = self.file.read(framesPerInterval)
                txLib.c_libNimRumTxListToBuf(dataArr, dataOut)

            # Ctrl LED, if any
            if (dataValid < 0) or (self.cfg.latencyError != 0):
                self.led.red()
            else:
                if activeChannelsNew > 2:
                    self.led.blue()
                else:
                    self.led.green()

            # CREATE VIRTUAL CHANNELS, IF ANY
            for virtCh in self.cfg.virtualChannels:
                if "crossfaderPosition" in virtCh:
                    txLib.c_libNimRumChannelMixer(
                        dataOut,
                        framesPerInterval,
                        virtCh["channelNumber"],
                        virtCh["crossfaderChannelA"],
                        virtCh["crossfaderChannelB"],
                        virtCh["crossfaderPosition"],
                    )

                if "toneGeneratorMode" in virtCh:
                    chNumb = virtCh["channelNumber"]
                    self.tonGen[chNumb].read(framesPerInterval, dataOut[chNumb])

           # UPDATE CHANNEL MAPPING IF NEEDED
            if activeChannels != activeChannelsNew:
                activeChannels = activeChannelsNew
                self.assignChannels(activeChannels)
                self.cfg.setVolumeMode(activeChannels)
                self.volumeSet()

            # SEND DATA
            # totFrameTime_ns = int(round(frameTimeActual * numOfFrames))
            totFrameTime_ns = 0
            txLib.c_libNimRumTxProcess(dataOut, framesPerInterval, totFrameTime_ns)

            # CHECK REMOTE
            self.cfg.lircCheck()

        ###########################################################
        # CLEAN UP
        ###########################################################
        self.led.off()
        capLib.c_libNimRumAlsaCapture_close()
        txLib.c_libNimRumTxClose()

        self.lclPrint("TX Done")


###########################################################
#### MAIN ####
###########################################################
if __name__ == "__main__":

    fileName = None
    if len(sys.argv) > 1:
        fileName = sys.argv[1]

    t = nimRumTx(configFile="./txConfig.yaml")
    t.runTx(fileName=fileName)
