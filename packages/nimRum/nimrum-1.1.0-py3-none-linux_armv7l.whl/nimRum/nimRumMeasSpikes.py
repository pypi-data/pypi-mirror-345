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

import numpy as np
import matplotlib.pyplot as plt
import wavio
import time
import statistics
from pathlib import Path
import os 

class NIMRUM_MEAS_SPIKES():

    def __init__(self, capRate=48000, maxTime_sec=200, maxDiff_us=250*1000, maxInt=1, resultFolder=None):
        self.capRate = capRate
        self.maxDiff_us = maxDiff_us
        self.trigMinLvl = maxInt / 500

        self.synchDiff_X = np.array([])
        self.synchDiff_Y = np.array([])
        self.rXArr = np.array([])
        self.lXArr = np.array([])

        self.maxTime_sec = maxTime_sec # To limit size of stored data
        self.currentTime_sec = 0.0

        self.storeInterval_sec = 10*60

        self.plotTitle = "Synch Diff - Px VS Py"
        plotFileName = self.plotTitle.replace(" ", "_") + ".pdf"
        if resultFolder == None:
            resultFolder = str(Path.home())
        self.plotFileName = os.path.join(resultFolder, plotFileName)
        self.plotLabel = "Px VS Py"

        self.lastStorageTime = time.time()

    def storeResult(self):
        if len(self.synchDiff_X) == 2:
            print("No result to store")
            return 

        ax1 = plt.subplot(111)
        ax1.clear()

        ax1.plot(self.synchDiff_X, self.synchDiff_Y, label=self.plotLabel, color="black")#, marker=".")

        ax1.set_title(self.plotTitle)
        ax1.set_xlabel("Time [s]")
        ax1.set_ylabel("Channel accuracy [us]")
        #ax1.set_ylim(-550, 550)

        plt.savefig(self.plotFileName, format="pdf", bbox_inches="tight")

        npyFileName = self.plotFileName+'.npy'
        with open(npyFileName, 'wb') as f:
            np.save(f, self.synchDiff_X)
            np.save(f, self.synchDiff_Y)

        print("Stored: {} and {}".format(self.plotFileName, npyFileName))

    def _limitdata(self):
        """
        Just keep latest latest self.maxTime_sec seconds
        In case not spikes detected for a long time, or at least 20 data points 
        """
        while (self.currentTime_sec > self.maxTime_sec) and (len(self.synchDiff_X) > 20):
            self.currentTime_sec -= self.synchDiff_X[0]
            self.synchDiff_X -= self.synchDiff_X[0]

            self.synchDiff_X = np.delete(self.synchDiff_X, 0)
            self.synchDiff_Y = np.delete(self.synchDiff_Y, 0)

            self.rXArr = np.delete(self.rXArr, 0)
            self.lXArr = np.delete(self.lXArr, 0)

    def add(self, indata):
        capR = indata[:,0]
        capL = indata[:,1]

        capRSpikeIdxs = self.getSpikeIdxs(capR)
        capLSpikeIdxs = self.getSpikeIdxs(capL)

        capRIdxs, capLIdxs, diffXVals = self.removeUnmatchedSpikes(
            capRSpikeIdxs, capLSpikeIdxs
        )

        if (capRIdxs.size!=0) and (capLIdxs.size!=0):

            rX = self.approxZeroCrossing(capR, capRIdxs)
            lX = self.approxZeroCrossing(capL, capLIdxs)

            synchDiffTime_us = rX - lX

            # This just stored what can be plotted/stored to file
            self.synchDiff_X = np.append(self.synchDiff_X, self.currentTime_sec + (np.array(capRIdxs)/float(self.capRate)) )
            self.synchDiff_Y = np.append(self.synchDiff_Y, list(synchDiffTime_us))

            if (len(self.rXArr) > 3) and (len(self.lXArr) > 3):
                # TODO: This must be improved
                rD = (rX-self.rXArr[-1]) - np.round(np.median(np.diff(self.rXArr)))
                lD = (lX-self.lXArr[-1]) - np.round(np.median(np.diff(self.lXArr)))

                meanY = statistics.mean(self.synchDiff_Y)
            else:
                rD = [0]
                lD = [0]

                meanY = 0.0

            self.rXArr = np.append(self.rXArr, rX)
            self.lXArr = np.append(self.lXArr, lX)

            # TODO: This script will soon need cleanup. This is to avoid when captured sample array wraps
            if np.abs(rD) > 500000 and np.abs(lD) > 500000 and len(self.rXArr) > 1:
                self.rXArr = np.delete(self.rXArr, 0)
                self.lXArr = np.delete(self.lXArr, 0)

            sTimeInt = int(np.round(synchDiffTime_us[0]))
            print("synchDiffTime_us: {:4d}  Mean: {:4.0f}  DistanceToMean: {:4.0f} Diff R/L: {:4.0f}/{:4.0f} (R-L={:4.0f})".format(
                sTimeInt, np.round(meanY), np.round(sTimeInt - meanY), rD[0], lD[0], rD[0]-lD[0]))

        self.currentTime_sec += ( float(len(capR)) / float(self.capRate) ) 
        self._limitdata()

        if (self.lastStorageTime + self.storeInterval_sec) < time.time():
            print("Storing to file every {}s".format(self.storeInterval_sec))
            self.storeResult()
            self.lastStorageTime = time.time()


    def getSpikeIdxs(self, din):
        """
        Return index where input array is about to cross 0 with highest gradient
        Expects about one spike per capture
        Only returns max 1 peak
        """

        # Detect if too low signal
        trigLvl = np.max(din)/2
        highValArr = np.where(din > trigLvl)[0]

        #if (len(highValArr) >  len(din)/500) or (trigLvl < self.trigMinLvl):
        if trigLvl < self.trigMinLvl:
            print("Just noise? High Samples:{}/{} TrigLvl:{}<{}".format(len(highValArr), len(din), trigLvl, self.trigMinLvl))
            return np.array([])

        # Float to ensure no overflow when retreiving diff
        #dinF = din.astype("float64")

        # Get where din is passing 0, while 'going up'
        a = np.gradient(din)
        resIdx = np.argmax(a)

        # Want to get the idx of the last negative valued sample before crossing 0
        while (din[resIdx] > 0) and (resIdx > 0):
            resIdx -= 1
        if resIdx == 0:
            print("Max gradient at fishy position")
            return np.array([])

        # Double check we are in the middle of a square wave
        # Some soundcards have strong overshoot from the transient
        w = 10
        ok = True
        numOfHigh = (din[resIdx+1:resIdx+w+1] >= 0).sum()
        numOfLow = (din[resIdx-w:resIdx] < 0).sum()
        if (numOfHigh != w):
            ok = False
        if (numOfLow != w):
            ok = False

        if ok == False:
            print("Failed 'middle of square' check. H/L: {}/{}".format(numOfLow, numOfHigh))
            return np.array([])


        return np.array([resIdx])


    def removeUnmatchedSpikes(self, rIxds, lIdxs):
        """
        Compare two arrays with indexes.
        Return two arrays where indexes with too large diff has been removed
        TODO: This function made more sense when getSpikeIdxs could return multiple indexes
        """
        maxAllowedDiff = (self.maxDiff_us * self.capRate) / 1000000
        rRes = []
        lRes = []
        xRes = []  # X-values for kept indexes

        maxCnt = min(len(rIxds), len(lIdxs))
        idx = 0
        while idx < maxCnt:
            rVal = rIxds[idx]
            lVal = lIdxs[idx]
            idxDiff = rVal - lVal

            # Spikes seems missing in R
            if idxDiff > maxAllowedDiff:
                idx += 2
                print("Skipped L")
                continue
            # Seems to be missing from L
            if idxDiff < -maxAllowedDiff:
                idx += 2
                print("Skipped R")
                continue

            rRes.append(rIxds[idx])
            lRes.append(lIdxs[idx])
            xRes.append(idx)
            idx += 1

        return np.asarray(rRes), np.asarray(lRes), np.asarray(xRes)


    def approxZeroCrossing(self, dinArrInt, dinArrXPrevCross):
        """
        Returns X values in us where zero corrings occur in us.
        Linear approximation
        """
        timePerSample = 1000000.0 / float(self.capRate)

        # Float to ensure no overflow when retreiving diff
        dinArr = dinArrInt.astype("float64")

        newX = []
        for idx in dinArrXPrevCross:
            k = (dinArr[idx + 1] - dinArr[idx])
            k /= timePerSample

            zeroYatX = (idx * timePerSample) - (dinArr[idx] / k)

            newX.append(zeroYatX) # round(zeroYatX) )

        return np.asarray(newX)




def main():
    import sys

    f = wavio.read(sys.argv[1])
    print("Opened: {} ({},{})".format(sys.argv[1], f.rate, f.sampwidth))

    o = NIMRUM_MEAS_SPIKES(capRate=f.rate)
    o.add(f.data)

    o.storeResult()
    plt.show()

if __name__ == '__main__':
    main()
