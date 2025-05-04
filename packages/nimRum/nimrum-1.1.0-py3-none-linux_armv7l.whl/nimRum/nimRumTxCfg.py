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

import os
import sys
import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from nimRum import nimRumTxRemote
from nimRum import nimRumRotaryEnc


class nimRumTxCfg(nimRumTxRemote.nimRumTxRemote):
    def __init__(
        self,
        volumeCallback,
        latencyCallback,
        configFile="./txConfig.yaml",
    ):

        self.volumeCallback = volumeCallback
        self.latencyCallback = latencyCallback
        self.configFile = configFile

        try:
            print("Reading: " + configFile)
            cfgFile = open(configFile)
            self.cfg = yaml.load(cfgFile, Loader=Loader)["nimRumTXConfig"]
            cfgFile.close()
        except Exception as e:
            print("Failed opening TX configuration file: " + configFile)
            print("Error message:{}".format(e))
            whereAmI = os.path.dirname(os.path.abspath(__file__))
            print(" You can find an example here: " + whereAmI + "/txConfig.yaml")
            quit()

        self.volume = self._getTxVal("mainVolume", default=10)
        self.latency = self._getTxVal("latency_us", default=100000)
        self.logEnable = self._getTxVal("logEnable", default=0)
        defTmp = os.path.dirname(os.path.abspath(configFile))
        self.logPath = self._getTxVal("logPath", default=defTmp)
        self.pcmDevInputName = self._getTxVal("pcmDevInputName", default="")
        self.clientData = self._getTxVal("clients", default=[])
        self.virtualChannels = self._getTxVal("virtualChannels", default=[])
        self.cliIdErrorInsertion = self._getTxVal("cliIdErrorInsertion", default=-1)

        self.numOfCli = len(self.clientData)
        self.cliIds = list(range(0, self.numOfCli))

        self.cliNames = self._getCliVals("name", default="Missing")
        self.cliLocation = self._getCliVals("location")
        self.cliVolStereoAdj = self._getCliVals("volStereoAdj", default=0)
        self.cliVolMultiAdj = self._getCliVals("volMultiAdj", default=0)
        self.cliLatencyOffset = self._getCliVals("offset_us", default=0)

        self.multiChannelMap = self._getCliVals("multiChannel", default=[])
        self.stereoChannelMap = self._getCliVals("stereoChannel", default=[])

        self.latencyError = 0
        self.muteEnable = 0
        self.activeChannels = 0


        # #### Set CODEC for audio transport ####
        CODEC_NONE = 0 # 'Empty', dummy packets are sent
        CODEC_WAVE = 1 # RAW samples, probably just ONE channel per client reasonable
        CODEC_FLAC = 2 # Lossless, and 2 channels per client possible. NOTE: Be aware of CPU load on TX if using may channels!
        CODEC_OPUS = 3 # Potential packet loss healing, and 2 channels per client possible. NOTE: Be aware of CPU load on TX if using may channels!
        self.codec = self._getTxVal("codec", default=CODEC_WAVE)

        testErrFound = False
        for chListTmp in ([self.stereoChannelMap] + [self.multiChannelMap]):
            for idx, test in enumerate(chListTmp):
                if self.codec == CODEC_WAVE:
                    if len(test) > 1:
                        print("Found > 1 channels assigned to client {}, in CODEC_WAVE mode".format(idx))
                        testErrFound = True
                else:
                    if len(test) > 2:
                        print("Found > 2 channels assigned to client {}")
                        testErrFound = True
        if testErrFound:
            print("See {} for more info".format(__file__))
            quit()


        nimRumTxRemote.nimRumTxRemote.__init__(self,
            remote=self._getTxVal("remoteModel", default="LG_AKB72915207"), 
            up=self._getTxVal("keyUp", default="KEY_VOLUMEUP"), 
            down=self._getTxVal("keyDown", default="KEY_VOLUMEDOWN"), 
            mute=self._getTxVal("keyMute", default="KEY_MUTE"), 
            timeError=self._getTxVal("keyTimeError", default="KEY_RED")
            )

        # If Remote not avaiable, then enable a "volume knob" (currently used to insert fake timing error)
        if self.lircAvailable == False:
            self.nimRumRotaryEnc = nimRumRotaryEnc.nimRumRotaryEnc(callback=self.latencyErrorRotate)

        self.printCfg()
        sys.stdout.flush()

    def _getTxVal(self, keyName, default=None):
        res = default
        if keyName in self.cfg:
            res = self.cfg[keyName]
        else:
            print("Using default value for: " + str(keyName) + " = " + str(default))

        return res

    def _getCliVals(self, keyName, default=None):
        res = []
        for idx, d in enumerate(self.clientData):
            if keyName in d:
                res.append(d[keyName])
            else:
                print("Using default value for client number {}/{}: {}={}".format(idx, d["name"], keyName, default))

                res.append(default)
        return res

    def _printList(self, name, L):
        print("".join("{0:<17}".format(str(k)) for k in [name] + L))

    def printCfg(self):
        print("#### txConfig:")
        self._printList("Index:", self.cliIds)
        self._printList("Name:", self.cliNames)
        self._printList("Location:", self.cliLocation)
        self._printList("Vol.Adj. stereo:", self.cliVolStereoAdj)
        self._printList("Vol.Adj. multi:", self.cliVolMultiAdj)
        self._printList("Offset:", self.cliLatencyOffset)
        self._printList("Stereo mode:", self.stereoChannelMap)
        self._printList("Multi mode:", self.multiChannelMap)
        print("####")

    def volumeUp(self):
        if self.muteEnable == 0:
            self.volume = self.volume + 2
            if self.volume > 100:
                self.volume = 100
        else:
            self.volume = self.muteEnable
            self.muteEnable = 0

        self.volumeCallback()

    def volumeDown(self):
        if self.muteEnable == 0:
            self.volume = self.volume - 2
            if self.volume < 0:
                self.volume = 0
        else:
            self.volume = self.muteEnable
            self.muteEnable = 0

        self.volumeCallback()

    def volumeMuteToggle(self):
        # Stores last volume setting in muteEnable
        if self.muteEnable == 0:
            self.muteEnable = self.volume
            self.volume = 0
        else:
            self.volume = self.muteEnable
            self.muteEnable = 0

        self.volumeCallback()

    def latencyErrorToggle(self):
        if self.cliIdErrorInsertion == -1:
            print("cliIdErrorInsertion not set")
            return 

        if self.latencyError == 0:
            self.latencyError = 100
        elif self.latencyError == 100:
            self.latencyError = 500
        elif self.latencyError == 500:
            self.latencyError = 1000
        elif self.latencyError == 1000:
            self.latencyError = 2000
        elif self.latencyError == 2000:
            self.latencyError = 10000
        elif self.latencyError >= 10000:
            self.latencyError = 0

        print(
            "#### "
            + self.cliNames[self.cliIdErrorInsertion]
            + ", error insertion: "
            + str(self.latencyError)
        )
        self.latencyCallback(cliId=self.cliIdErrorInsertion, error=self.latencyError)

    def latencyErrorRotate(self, val, dir):
        if self.cliIdErrorInsertion == -1:
            print("cliIdErrorInsertion not set")
            return 

        self.latencyError = val * 20

        print(
            "#### "
            + self.cliNames[self.cliIdErrorInsertion]
            + ", error insertion: "
            + str(self.latencyError)
        )
        self.latencyCallback(cliId=self.cliIdErrorInsertion, error=self.latencyError)

    def getVolume(self, cliId):
        volAdj = self.cliVolMultiAdj[cliId]
        if self.activeChannels <= 2:
            volAdj = self.cliVolStereoAdj[cliId]

        volRes = int(round(self.volume + volAdj))

        if volRes <= 0: # If 0 then proper silence (volAdj can be negative)
            return 0
        elif volRes > 100:
            return 100
        else:
            return volRes

    def setVolumeMode(self, activeChannels):
        self.activeChannels = activeChannels

    def getLatency(self, cliId):
        lat = self.latency + self.cliLatencyOffset[cliId]
        return lat
