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

try:
    import platform
    if platform.machine() == 'aarch64':
        import wiringpi
    else:
        from gpiozero import LED
except:
    pass

class nimRumPyLed:
    def __init__(self, Rpin=12, Gpin=13, Bpin=26):

        self.ledAvailable = False
        try:
            self.platform = platform.machine()
            if self.platform == 'aarch64':
                wiringpi.wiringPiSetup()
                self.ledR = 24
                self.ledG = 26
                self.ledB = 25
            else:
                self.ledR = LED(Rpin)
                self.ledG = LED(Gpin)
                self.ledB = LED(Bpin)

            self.ledAvailable = True
        except:
            print("nimRumPyLed NOT enabled, reading " + __file__ + " migth help")

        self.off()

    def off(self):
        if self.ledAvailable:
            if self.platform == 'aarch64':
                wiringpi.pinMode(self.ledR, wiringpi.GPIO.INPUT)
                wiringpi.pinMode(self.ledG, wiringpi.GPIO.INPUT)
                wiringpi.pinMode(self.ledB, wiringpi.GPIO.INPUT)
            else:
                self.ledR.off()
                self.ledG.off()
                self.ledB.off()

    def red(self):
        if self.ledAvailable:
            if self.platform == 'aarch64':
                wiringpi.pinMode(self.ledR, wiringpi.GPIO.OUTPUT)
                wiringpi.pinMode(self.ledG, wiringpi.GPIO.INPUT)
                wiringpi.pinMode(self.ledB, wiringpi.GPIO.INPUT)
                wiringpi.digitalWrite(self.ledR, wiringpi.GPIO.LOW)
            else:
                self.ledR.on()
                self.ledG.off()
                self.ledB.off()

    def green(self):
        if self.ledAvailable:
            if self.platform == 'aarch64':
                wiringpi.pinMode(self.ledR, wiringpi.GPIO.INPUT)
                wiringpi.pinMode(self.ledG, wiringpi.GPIO.OUTPUT)
                wiringpi.pinMode(self.ledB, wiringpi.GPIO.INPUT)
                wiringpi.digitalWrite(self.ledG, wiringpi.GPIO.LOW)
            else:
                self.ledR.off()
                self.ledG.on()
                self.ledB.off()

    def blue(self):
        if self.ledAvailable:
            if self.platform == 'aarch64':
                wiringpi.pinMode(self.ledR, wiringpi.GPIO.INPUT)
                wiringpi.pinMode(self.ledG, wiringpi.GPIO.INPUT)
                wiringpi.pinMode(self.ledB, wiringpi.GPIO.OUTPUT)
                wiringpi.digitalWrite(self.ledB, wiringpi.GPIO.LOW)
            else:
                self.ledR.off()
                self.ledG.off()
                self.ledB.on()

    def white(self):
        if self.ledAvailable:
            if self.platform == 'aarch64':
                wiringpi.pinMode(self.ledR, wiringpi.GPIO.OUTPUT)
                wiringpi.digitalWrite(self.ledR, wiringpi.GPIO.LOW)
                wiringpi.pinMode(self.ledG, wiringpi.GPIO.OUTPUT)
                wiringpi.digitalWrite(self.ledG, wiringpi.GPIO.LOW)
                wiringpi.pinMode(self.ledB, wiringpi.GPIO.OUTPUT)
                wiringpi.digitalWrite(self.ledB, wiringpi.GPIO.LOW)
            else:
                self.ledR.on()
                self.ledG.on()
                self.ledB.on()
