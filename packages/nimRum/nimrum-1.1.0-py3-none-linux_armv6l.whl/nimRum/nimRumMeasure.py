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

import argparse
import signal
import numpy as np

import sounddevice
import wavio
from pathlib import Path
import os 

from nimRum import nimRumMeasSpikes

"""
sudo pip3 install sounddevice
sudo apt-get install libportaudio2
sudo apt-get install libopenblas-dev
"""

class NIMRUM_MEAS(): 

    def __init__(self, cfg, maxTime_sec=5*60):
        self.cfg = cfg
        self.maxTime_sec = float(maxTime_sec)
        self.dataEmpty = True

        self.dataFileName = os.path.join(self.cfg['resultFolder'], "nimRumMeas.wav") 

        if self.cfg['measMode'] == 'synchErr':
            self.measType = nimRumMeasSpikes.NIMRUM_MEAS_SPIKES(capRate=self.cfg['sampleRate'], maxTime_sec=60*60, maxInt=self.cfg['maxInt'], resultFolder=self.cfg['resultFolder'])
        else:
            print("ERROR: Unknown measure type: {}".format(capRate=self.cfg['measMode']))

    def _limitdata(self):
        blockSize = int(self.cfg['sampleRate'] * self.cfg['interval'])

        while (float(self.data.shape[0]) / float(self.cfg['sampleRate'])) > self.maxTime_sec:
            self.data = np.delete(self.data, np.s_[0:blockSize], axis=0)

    def add(self, indata):
        if self.dataEmpty or not self.cfg['storeData']:
            self.data = indata
            self.dataEmpty = False
        else:
            self.data = np.concatenate((self.data, indata), axis=0)
            self._limitdata()

        # TODO: This behavior depends on measType...
        self.measType.add(indata)

    def storeData(self):
        wavio.write(self.dataFileName, self.data, self.cfg['sampleRate'], sampwidth=self.cfg['sampW'])
        print("Stored: {} (Rate:{} SampleSize:{} Shape:{} )".format(self.dataFileName, self.cfg['sampleRate'], self.cfg['sampW'], self.data.shape))

    def storeResult(self):
        self.measType.storeResult()

def getCfg():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--listDevices', '-l', action="store_true", help='List audio devices')
    parser.add_argument('--device', '-d', default=0, help='Input device ID')
    parser.add_argument('--interval', '-i', type=float, default=1.0, help='Capture interval: Seconds')
    parser.add_argument('--sampleRate', '-f', type=float, default=48000, help='Sample rate: 0=Use device default')
    parser.add_argument('--sampleSize', '-s', type=str, default='int32', help='Sample size: float32|int32|int16|int8|uint8')
    parser.add_argument('--measMode', '-m', type=str, default='synchErr', help='Meaure mode: synchErr|chirp|...')
    parser.add_argument('--storeData', '-S',  action="store_true", help='Store all collected data to file')
    parser.add_argument('--resultFolder', '-R',  default='/home/pi/LOGS', help='Folder where measurements are stored')

    args = parser.parse_args()

    if args.listDevices:
        print(sounddevice.query_devices())
        quit()

    if args.sampleRate == 0:
        args.sampleRate = sounddevice.query_devices(args.device, 'input')['default_samplerate']

    cfg = vars(args) # Convert to dict

    cfg['sampW'] = 0
    if args.sampleSize == 'int32':
        cfg['sampW'] = 4
        cfg['maxInt'] = 2147483647
    elif args.sampleSize == 'int16':
        cfg['sampW'] = 2
        cfg['maxInt'] = 32767
    else:
        print("ERROR: Only supports int32 or int16, not {}".format(args.sampleSize))
        quit()

    return cfg


def signal_handler(sig, frame):
    print("Catched Ctrl-C")
    global storeData
    global measObj
    global run
    global alreadyClosing

    run = False

    if not alreadyClosing:
        alreadyClosing = True

        if storeData:
            measObj.storeData()

        measObj.storeResult()


def callBack(indata, frames, time, status):
    global measObj

    if status:
        print("Got callback status:{}".format(status))

    #print("CAPTURES: ", indata.shape, frames, time)
    measObj.add(indata)

def main():
    signal.signal(signal.SIGINT, signal_handler)

    global storeData
    global measObj
    global run
    global alreadyClosing

    cfg = getCfg()
    storeData = cfg['storeData']

    measObj = NIMRUM_MEAS(cfg)
    run = True
    alreadyClosing = False

    blockSize = int(cfg['sampleRate'] * cfg['interval'])

    with sounddevice.InputStream(device=cfg['device'], channels=2, dtype=cfg['sampleSize'], callback=callBack,
                        blocksize=blockSize, samplerate=cfg['sampleRate']):
        while run:
            pass


if __name__ == '__main__':
    main()
