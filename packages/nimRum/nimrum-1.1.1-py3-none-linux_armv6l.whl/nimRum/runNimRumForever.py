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

import subprocess
import signal
import os
import sys
import sys

helpStr = """
#### The idea is...
# In case of severe error (uncontrolled crash), then start a new process.
# Hopefully previous process will be cleaned up by the OS.
# Probably only useful if taking audio stream from some external source, like S/PDIF
# The idea is also to never really need this

#### This file can be triggered at boot by:
# sudo nano /etc/rc.local 
# Then add one of these to the end of that file ('nice -n -10' is optional and usually does not matter):
# screen -d -m nice -n -10 /usr/local/bin/runNimRumForever /usr/local/bin/runNimRumTx
# screen -d -m nice -n -10 /usr/local/bin/runNimRumForever /usr/local/bin/runNimRumRx

# Depending on your installation these can come in handy:
# which ...
# pip show nimRum 
#
# Also, please put the tx|rxConfig.yaml-files in a folder named /root/nimRum/
#
# If you want to take a look at what is started in the background with screen, use:
# Connect to screen started by root:    sudo screen -r
# Leave screen:                         Ctrl-a + Ctrl-d
# Scroll inside screen:                 Ctrl-a + Esc
"""

if len(sys.argv) != 2:
    print(helpStr)
    quit()
    
commandLine = sys.argv[1]

logLength = 10000
logFileName = "/var/log/runNimRumForever.log"

meStr = "**" + os.path.basename(__file__) + "**: "

logList = [None] * logLength
logCnt = 0
logWrap = 0
run = 1

def lclPrint(pStr):
    global meStr
    print(meStr + pStr)
    sys.stdout.flush()

def signal_handler(sig, frame):
    global run
    lclPrint ("Catched Ctrl-C")
    run = 0

signal.signal(signal.SIGINT, signal_handler)

def runCmd(cmd):
    global logList
    global logCnt
    global logLength
    global logWrap

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        output = p.stdout.readline()
        if not output and p.poll() is not None:
            break
        if output:
            print (str(output.strip(), 'utf-8'))
            sys.stdout.flush()
            logList[logCnt] = output.strip()
            logCnt = logCnt + 1
            if logCnt >= logLength:
                logWrap = 1
                logCnt = 0

    rc = p.poll()
    return rc

def wrLog(logName):
    global logList
    global logCnt
    global logLength
    global logWrap

    f = open(logName, "w")
    if logWrap == 1:
        f.writelines("%s\n" % L for L in logList[logCnt:logLength])

    f.writelines("%s\n" % L for L in logList[0:logCnt])
    f.close()
    lclPrint ("Wrote: " + logName)

def main():

    while run == 1:
        lclPrint ("***************************************************")
        lclPrint ("                    RESTART ")
        lclPrint ( "***************************************************")

        if os.path.exists(commandLine):
            runCmd(commandLine)
        else:
            lclPrint ("Could not find executable file")

        wrLog(logFileName)

if __name__ == '__main__':
    main()
