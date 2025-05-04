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
import signal
import socket
import re
import socket
import os
from nimRum import nimRumCheckHW

import netifaces as ni


class nimRumPyCommon:
    def __init__(self, meName=os.path.basename(__file__)):

        self.meStr = "**" + meName + "**: "

        self.run = 1
        signal.signal(signal.SIGINT, self.signal_handler)

        try:
            self.myName = socket.gethostname()
        except:
            self.myName = "Unknown1"

        try:
            # TODO: This is not failsafe. Expect all devices to be named 'prezoXX'
            self.myId = int(re.findall(r"\d+", self.myName)[0])
        except:
            self.myId = 666

        t = nimRumCheckHW.nimRumCheckHW()

    def lclPrint(self, pStr):
        print(self.meStr + pStr)
        sys.stdout.flush()

    def signal_handler(self, sig, frame):
        self.lclPrint("Catched Ctrl-C, stopping")
        self.run = 0

    def getMyUniqueName(self):
        return self.myName

    def getMyUniqueId(self):
        return self.myId

    def getBCAddr(self, nicName):
        try:
            useLocalClock = 0
            if nicName == "lo":
                useLocalClock = 1
                bcastAddr = "127.0.0.255"
            else:
                bcastAddr = ni.ifaddresses(nicName)[ni.AF_INET][0]["broadcast"]
        except:
            self.lclPrint("'nic' must be one of the following:")
            self.lclPrint(str(ni.interfaces()))
            quit()

        self.lclPrint("BCAddr:" + str(bcastAddr))
        return bcastAddr, useLocalClock
