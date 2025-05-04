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

import platform

"""
This is kind of a placeholder for future development
"""
class nimRumCheckHW:
    def __init__(self):
        print(platform.uname())
        self.cpuArch = platform.machine()
        self.testHW()

    def testHW(self):
        if self.cpuArch not in ['aarch64', 'armv6l', 'armv7l']:
            print("Platform not supported")
            quit()

        return True

if __name__ == "__main__":
    t = nimRumCheckHW()
