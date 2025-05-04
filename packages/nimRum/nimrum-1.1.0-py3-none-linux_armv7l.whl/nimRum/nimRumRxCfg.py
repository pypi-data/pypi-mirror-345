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
import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class nimRumRxCfg:
    def __init__(self, configFile="./rxConfig.yaml"):

        try:
            cfgFile = open(configFile)
            self.cfg = yaml.load(cfgFile, Loader=Loader)
            cfgFile.close()
            self.usefulPath = os.path.dirname(os.path.abspath(configFile))
            print("Read: " + configFile)
        except:
            print("****************************************************************")
            print("Failed opening RX configuration file: " + configFile)
            print("  No worries. There will be one written when lib is closed down")
            print("  You just need to rename it to rxConfig.yaml")
            print("****************************************************************")
            self.cfg = {}
            self.cfg["nimRumRXConfig"] = {}
            self.usefulPath = os.getcwd()

        self._setDefault("nic", default="wlan0")
        self._setDefault("staticDelay_us", default=0)
        self._setDefault("outputChannelEnable", default=3)
        self._setDefault("logEnable", default=0)
        self._setDefault("logPath", default=self.usefulPath)
        self._setDefault("pcmMode", default=1)
        self._setDefault("pcmDevName", default="default")
        self._setDefault("volumeDevName", default="default")
        self._setDefault("volumeCtrl", default="NIMRUM_SFT_VOL")
        
    def _setDefault(self, keyName, default=None):
        if not keyName in self.cfg["nimRumRXConfig"]:
            print("Using default value for: " + keyName + " = " + str(default))
            self.cfg["nimRumRXConfig"][keyName] = default

    def get(self, keyName):
        return self.cfg["nimRumRXConfig"][keyName]

    def alterDelay(self, diff):
        val = self.get("staticDelay_us") + diff
        self.cfg["nimRumRXConfig"]["staticDelay_us"] = val

    def dump(self):

        helpStr = """
#
# This file should have the following name: rxConfig.yaml
# Either store it in:
#   1. The same folder where you found this file (rxConfig.last)
#   2. $HOME/nimRum
#
# nic:
#   Select a NIC. This is where a broadcast message will be sent
#   to get in touch with TX. This NIC will then be used for transmission.
#   lo | eth0 | wlan0 | ...
#
# staticDelay_us: 
#   Add a static latency offset
#
# outputChannelEnable:
#   Binary coded enable for audio out
#   3 = 2'b11 = channel0 and channel1 is enabled
#   Most soundcards has 2 (stereo outputs), so 3 is probably a good value
#   In case of only using one channel to connect to a speaker,
#   then this parameter can help saving the unused amplifier output
#
# pcmMode:
#   0: DUMMY PCM
#   1: ALSA
#
# pcmDevName: ""
#   If not set, sound device 'default' will be used.
#   If empty string, then first PCM device found starting with 'hw:' will be used.
#   Recommendation is to use a sound device starting with 'hw:...', like: "hw:CARD=IQaudIODAC,DEV=0"
#   This to avoid any unwanted signal processing or varying delays. 
#
# volumeDevName: ""
#   If not set, sound device 'default' will be used.
#   If empty string, then trying to find something matching pcmDevName.
#   Empty string is the recomendation if you know what you are doing.
#
#   NOTE: 
#   If volume control does not work, this migth(NOT GUARANTEED) enforce a simple SW volume control.
#   This to avoid breaking ears or speakers.
#   If the log shows somethng like: "Using Soft Volume, .." when changing volume, then the SW volume is in use.
#
#   REMEMBER: The license says '..without any warranties..', SO PLEASE BE CAREFUL in case
#   you using powerful amplifiers.
#
# volumeCtrl: ""
#   This allows you you finetune your own volume curve
#   If not set, 'NIMRUM_SFT_VOL' will be used.
#
#   FOR SOUNDCARDS LACKING HW VOLUME CONTROL, 'NIMRUM_SFT_VOL' is probably the safest choice
#
#   Here are some suggestions:
#
#   "NIMRUM_SFT_VOL"
#       pHAT-HIFI
#       PCM5102A, if not enabled ALSA soft volume
#
#   "PCM_5122"
#       IQ Audio, Pi-DAC Zero
#       HifiBerry DAC+ (+ADC)
#       Raspyplay
# 
#   "PCM5102A"
#       DM, DIY More
#       (pHAT-HIFI)
# 
#   "TAS_5756M"
#       JustBoom Amp HAT
#       IQ Audio, Pi-DigiAMP+
#
#   See nimRumRxVolumeConversion.py for more details
"""

        fileName = os.path.join(self.usefulPath, "rxConfig.last")

        try:
            file = open(fileName, "w")
            file.write(helpStr)
            yaml.dump(self.cfg, file)
            file.close()
        except:
            print("Failed writing: " + fileName)
