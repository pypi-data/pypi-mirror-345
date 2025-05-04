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

# So many hours wasted on various internet tips.
# Ended up using this one: https://forums.raspberrypi.com/viewtopic.php?t=235256

# cat /etc/os-release -> bullseye
#
# sudo apt update
# sudo apt install lirc
#
# Edit /etc/lirc/lirc_options.conf as follows by changing these two lines:
# driver = default
# device = /dev/lirc0
#
# sudo nano /boot/config.txt
# dtoverlay=gpio-ir,gpio_pin=17
#
# pip3 install lirc
# sudo nano  /usr/lib/arm-linux-gnueabihf/python3.9/site-packages/lirc/paths.py
# Comment out
# #   try:
# #       os.unlink(os.path.join(HERE, '_client.so'))
# #   except PermissionError:
# #       pass
#
# sudo systemctl stop lircd.service
# sudo systemctl start lircd.service
# sudo systemctl status lircd.service
# sudo reboot

try:
    import lirc
except BaseException as e:
    print('Loading Python package lirc for remote control failed') #: ' + str(e))

class nimRumTxRemote:
    def __init__(self, remote="", up="", down="", mute="", timeError=""):

        self.remoteModel=remote
        self.keyUp=up
        self.keyDown=down
        self.keyMute=mute
        self.keyTimeError=timeError

        self.lircAvailable = False
        try:
            self.lircConn = lirc.LircdConnection(timeout=0.0001)
            self.lircConn.connect()
            self.lircAvailable = True
        except:
            print("nimRumTxRemote NOT enabled, reading " + __file__ + " migth help")

    def lircCheck(self):
        if not self.lircAvailable:
            return None

        try:
            keypress = self.lircConn.readline()
        except:
            return None

        if keypress != "" and keypress != None:

            data = keypress.split()
            # hexcode = data[0]
            repeat = data[1]
            command = data[2]
            remote = data[3]
            # print("remote:{}, command:{}, repeat:{}".format(remote, command, repeat))
            # ignore command repeats

            if remote == self.remoteModel:
                if command == self.keyUp:
                    self.volumeUp()

                if command == self.keyDown:
                    self.volumeDown()

                if command == self.keyMute:
                    if repeat != "00":
                        return None
                    self.volumeMuteToggle()

                if command == self.keyTimeError:
                    if repeat != "00":
                        return None
                    self.latencyErrorToggle()

        return None
