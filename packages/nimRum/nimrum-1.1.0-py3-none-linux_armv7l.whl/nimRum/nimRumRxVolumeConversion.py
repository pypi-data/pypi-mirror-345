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

import math

"""
Convert volume value between 0-100 to match your speakers and enables/disables 'soft' volume
Return value must match your PCM/DAC API

*** DACs ***
IQ Audio, Pi-DAC Zero
  dtoverlay=iqaudio-dacplus
  hw:CARD=IQaudIODAC, volMin: 0, volMax: 207 
  -> PCM 5122 <-
  
HifiBerry DAC+ (+ADC)
  dtoverlay=hifiberry-dacplus
  hw:CARD=sndrpihifiberry, volMin: 0, volMax: 207
  -> PCM 5122 <-

Raspyplay
  dtoverlay=iqaudio-dacplus
  hw:CARD=IQaudIODAC, volMin: 0, volMax: 207 
  -> PCM 5122 <-

DM, DIY More
  dtoverlay=hifiberry-dac
  hw:CARD=sndrpihifiberry, volMin: 0, volMax: 255
  -> PCM5102A <-

*** AMPs ***
JustBoom Amp HAT, peak power output of 2 x 55 Watts *Note1
  dtoverlay=justboom-dac
  hw:CARD=sndrpijustboomd, volMin: 0, volMax: 207
  20dB gain (adj. between 20/26dB)
  -> TAS 5756M <-

IQ Audio, Pi-DigiAMP+, up to 2 x 35W *Note1
  dtoverlay=iqaudio-dacplus
  hw:CARD=IQaudIODAC, volMin: 0, volMax: 207 
  20dB gain (adj. between 20/26dB)
  -> TAS 5756M <-

pHAT-HIFI
  dtoverlay=hifiberry-dac
  hw:CARD=sndrpihifiberry, volMin: 0, volMax: 255
  20dB gain typically, 6+6W at 8ohm (at 10% THD+N From a 10V Supply)
  -> PCM5102A  + TPA3113-D2 <-

NOTE 1:
  TAS 5756M: 30-W stereo, 40-W mono

"""

class nimRumRxVolumeConversion():

  def __init__(self, pcmType="default"):
      self.pcmType = pcmType
      self.nimRumRange = 100

      self.softVolumeEnable = 0
      self.volInLast = -1
      self.volOut = -1

  def getVolVal(self, volIn):
    if volIn != self.volInLast:
      self.volInLast = volIn

      if self.pcmType == "PCM_5122":
          self._pcm5122(volIn)
      elif self.pcmType == "TAS_5756M":
          self._pcm5122(volIn)
      elif self.pcmType == "PCM5102A":
          # Have no HW volume control.
          self._nimRumSftVol(volIn)
      elif self.pcmType == "ALSA_SFT_VOL":
          self._alsaSftVol(volIn)
      elif self.pcmType == "NIMRUM_SFT_VOL":
          self._nimRumSftVol(volIn)
      elif self.pcmType == "default":
          self._default(volIn)
      else:
          print("{}, Cannot convert volume. pcmType:{} volIn:{}".format(__file__, self.pcmType, volIn))
          self.softVolumeEnable = 1
          self.volInLast = 0
          self.volOut = 0

    return self.softVolumeEnable, self.volOut


  def _default(self, volIn):
    self.softVolumeEnable = 0
    self.volOut = volIn

  def _pcm5122(self, volIn):
    """
    Converts to register settings for PCM512x
    See pcm512x_TAS5756_regTodB()

    Lowest needed value -60dB => 207 + (-60 / 0.5) = 87
    Lowest needed value -60dB => 207 + (-61.5 / 0.5) = 84
    """
    devSilent = 0
    devMin = 84 #66
    devMax = 207
    devRange = devMax - devMin
    rate = float(devRange)/float(self.nimRumRange)

    self.volOut = devSilent
    if volIn > 0:
      self.volOut = int(devMin + round(rate * float(volIn)))

    self.softVolumeEnable = 0

  def _alsaSftVol(self, volIn):
    """
    Expects ALSA to be configured like this:

    pcmDevName: 'default'
    volumeDevName: 'default'

    asound.conf:
    pcm.sftvol {
        type softvol
        slave.pcm "plughw:0"
        control {
            name "Master"
            card 0
        }
    }

    pcm.!default {
        type plug
        slave.pcm "sftvol"
    }

    ctl.!default {
        type hw
        card 0
    }
    """
    devSilent = 0
    devMin = 0
    devMax = 255
    devRange = devMax - devMin
    rate = float(devRange)/float(self.nimRumRange)

    self.volOut = devSilent
    if volIn > 0:
      self.volOut = int(devMin + round(rate * float(volIn)))

    self.softVolumeEnable = 0

  def _nimRumSftVol(self, volIn):
    """
    Using nimRum built in, experimental, volume control
    """
    devSilent = 0
    devMin = 28 #16
    devMax = 100
    devRange = devMax - devMin
    rate = float(devRange)/float(self.nimRumRange)

    self.volOut = devSilent
    if volIn > 0:
      self.volOut = int(devMin + round(rate * float(volIn)))

    self.softVolumeEnable = 1

####################################################################################################
# *********** MAIN ***********
####################################################################################################
if __name__ == '__main__':

  import matplotlib.pyplot as plt
  import numpy as np

  def pcm512x_TAS5756_regTodB(regIn):
    """
    PCM512x

    Default value: 00110000
    00000000: +24.0 dB = 0
    00000001: +23.5 dB
    . . .
    00101111: +0.5 dB
    00110000: 0.0 dB = 48
    00110001: -0.5 dB
    ...
    11111110: -103 dB = 254
    11111111: Mute

    Driver seems to stop at +0dB and invert the volume value
    """
    if regIn < 0 or regIn > 207:
      print("pcm512x_TAS5756_dB out of range")

    regVal = (255 - regIn)

    dB = 24 - 0.5 * regVal

    if regVal == 255: # Mute
        dB=-103

    return dB

  def gainTodB(gain):
    dB = -103
    if gain > 0:
      dB = 20*math.log10(gain)
    return dB

  def swVol(volume):
    vol = float(volume) / 100.0

    k = 4.23
    y = (vol * k) - k
    d = pow(10, y)

    if volume == 0:
      d = 0
    if d > 1.0:
      d = 1.0
    return d



  NUMPY_VOL_RANGE = 100 # nimRUm implements a volume between 0 and 40
  volRange = range(NUMPY_VOL_RANGE +1)

  dev_512x = nimRumRxVolumeConversion(pcmType="PCM_5122")
  dev_aSft = nimRumRxVolumeConversion(pcmType="ALSA_SFT_VOL")
  dev_nSft = nimRumRxVolumeConversion(pcmType="NIMRUM_SFT_VOL")

  regVal_512x = []
  regVal_aSft = []
  regVal_nSft = []
  dB_512x = []
  dB_aSft = []
  dB_nSft = []

  for volIn in volRange:

    softVal, regVal = dev_512x.getVolVal(volIn)
    #regVal += 6
    regVal_512x.append(regVal)
    dB = pcm512x_TAS5756_regTodB(regVal)
    dB_512x.append(dB)

    softVal, regVal = dev_aSft.getVolVal(volIn)
    regVal_aSft.append(regVal)
    dB = gainTodB(float(regVal)/255.0)
    dB_aSft.append(dB)

    softVal, regVal = dev_nSft.getVolVal(volIn)
    regVal_nSft.append(regVal)
    nimRumGainCurve = swVol(regVal)
    dB = gainTodB(nimRumGainCurve)
    dB_nSft.append(dB)


  for idx, volIn in enumerate(volRange):
    print("VolIn:{} ".format(volIn), end='')
    print("512x:{}({}dB) ".format(regVal_512x[idx], dB_512x[idx]), end='')
    print("aSft:{}({}dB) ".format(regVal_aSft[idx], dB_aSft[idx]), end='')
    print("nSft:{}({}dB) ".format(regVal_nSft[idx], dB_nSft[idx]), end='')
    print("")

  figure, axis = plt.subplots(2, 1) 
  axis[0].plot(volRange, dB_512x, 'r', label='dB_512x')
  axis[0].plot(volRange, dB_aSft, 'g', label='dB_aSft')
  axis[0].plot(volRange, dB_nSft, 'b', label='dB_nSft')


  axis[1].plot(np.diff(dB_512x), 'r', label='dB_512x_diff')
  axis[1].plot(np.diff(dB_aSft), 'g', label='dB_aSft_diff')
  axis[1].plot(np.diff(dB_nSft), 'b', label='dB_nSft_diff')
  plt.ylim((-1,+4))

  print("dB_512x: dB / vol:{}".format(np.mean(np.diff(dB_512x)[2:])))
  print("dB_aSft: dB / vol:{}".format(np.mean(np.diff(dB_aSft)[2:])))
  print("dB_nSft: dB / vol:{}".format(np.mean(np.diff(dB_nSft)[2:])))

  axis[0].legend()
  axis[1].legend()
  plt.show()
