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

from nimRum import nimRumTx

def main():
    soundFileName = None
    if len(sys.argv) > 1:
        soundFileName = sys.argv[1]


    configFile = "./txConfig.yaml"
    if os.path.exists(configFile) == False:
        configFile = os.path.join(os.path.expanduser("~"), "nimRum/txConfig.yaml")

    tx = nimRumTx.nimRumTx(configFile=configFile)
    tx.runTx(fileName=soundFileName)

if __name__ == '__main__':
    main()
