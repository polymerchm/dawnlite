from dawnlite import comm
import signal
import time
from dawnlite import app
import logging

import sys

from rpi_hardware_pwm import HardwarePWM
from dawnlite.hw.rampLED import rampLED 
from threading import Thread
from threading import Event


LOGGER = logging.getLogger('dawnlite')



class StatusLED(Thread):
    def __init__(self, channel):
        if not channel in [0,1]:
            LOGGER.critical(f'Invalid channel value of {channel}')
            sys.exit(1)
        super().__init__()
        self.off = 0
        self.freq = app.config['PWM_FREQUENCY']
        self.pwm = HardwarePWM(channel, hz=self.freq)
        self.event = Event()
        self.pwm.off = self.off
        self.pwm.start(self.off)
        self.level = 0
        self.duration = 0
        self.pulseType = ""
        self.cyclicActive = False
        self.dutyCycle = 0.5 # %on-time
        self.numCycles = 0 # pulse train
        self.onTime = 0
        self.offTime = 0
        self.validPulseTypes = ['hard', 'soft', 'heartbeat']


    def setParameters(self,**kwargs):
        for key, value in kwargs.items():
            if not key in self.__dict__.keys():
                LOGGER.critical(f"invalid key [{key}] passed")
                sys.exit(1)
            if key == 'pulseType' and not value in self.validPulseTypes:
                LOGGER.critical(f'Invalid pulseType {value}')
                sys.exit(1)
            if (key  =='level' and not value in range(0,101)) or (key == 'dutyCycle' and not (0.0 <= value <= 1.0)):
                LOGGER.critical(f'{key} value {value} outside valid range')
                sys.exit(1)
            self.__dict__[key] = value



    def run(self):  # called after self.start
        if self.pulseType == "heartbeat":
            self.heartBeat()
        else:
            self.pulseTrain()

    def turnOff(self):
        self.pwm.change_duty_cycle(0)

    def turnOn(self,level=0):
        value = level if level > 0 else self.level
        self.pwm.change_duty_cycle(value)

    def hardPulse(self, train=False):
        if self.is_alive() and not train:
            return # dont interupt a train
        duration = self.duration if not train else self.onTime
        self.turnOff()
        time.sleep(0.01)
        self.turnOn() 
        time.sleep(duration)
        self.turnOff()

    def softPulse(self, train=False):
        # if self.is_alive() and not train:
        #     return # dont interupt a train
        duration = self.period if not train else self.onTime        
        rampLED(self.pwm, 0, self.level, duration/2)
        rampLED(self.pwm, self.level,0, duration/2)

    def pulseTrain(self):
        if self.dutyCycle == 0 or self.duration == 0:
            # print(f"dutyCycle={self.dutyCycle} or duration={self.duration} invalid")
            sys.exit(1)
        self.offTime = self.duration*(1-self.dutyCycle)
        self.onTime = self.duration*self.dutyCycle
        if self.numCycles != 0:
            count = self.numCycles
        while True:
            if self.event.is_set():
                self.turnOff()
                break
            if self.pulseType == "hard":
                self.hardPulse(train=True)
            else:
                self.softPulse(train=True)
            time.sleep(self.offTime)
            if self.numCycles != 0:
                count -= 1
                if count == 0:
                    self.turnOff()
                    break


    def heartBeat(self):
        if self.duration == 0:
            LOGGER.critical(f'Invalid duration={self.duration}')
            sys.exit(1)
        while True:
            if self.event.is_set():
                self.turnOff()
                break
            self.softPulse()

    def shutdown(self, signal, frame): 
        self.turnOff()
        self.pwm.stop()
        self.event.set()
        self.join()
        sys.exit(0)

    def stopPulseTrain(self):
        self.event.set()
        self.join()


def test():
    print("running test")
    test0 = StatusLED(0)
    test1 = StatusLED(1)
    signal.signal(signal.SIGINT, test0.shutdown)
    signal.signal(signal.SIGTERM, test0.shutdown)
    signal.signal(signal.SIGINT, test1.shutdown)
    signal.signal(signal.SIGTERM, test1.shutdown)
    test0.setParameters(level=10, duration=2, pulseType="soft", dutyCycle=0.2)
    test0.start()
    test1.setParameters(level=50, duration=2, pulseType="soft", dutyCycle=0.8)
    time.sleep(0.35)
    test1.start()
    for item in range(0,20):
        time.sleep(1)
        print("sleeping")
    test0.stopPulseTrain()
    test1.stopPulseTrain()


if __name__=='__main__':
    test()


     







    




    



    

    




