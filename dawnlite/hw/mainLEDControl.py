from locale import setlocale
from rpi_hardware_pwm import HardwarePWM
from dawnlite import comm
import time
import math
import inspect

from dawnlite import app
from dawnlite.hw.rampLED import rampLED
import logging
LOGGER = logging.getLogger('dawnlite')

# assumes boot set to hardware PWM

# dtoverlay=pwm-2chan, default pins 18 pwm0 and 19 pwn1
# CURRENTLY CONFIGURED FOR PIN 18/19

class MainLED():
    def __init__(self):
        self.freq =  int(app.config['PWM_FREQUENCY'])
        self.off = 0 # 100 if app.config['LED_TYPE'] == 'common_anode' else 0
        self.pwm = HardwarePWM(1, hz=self.freq)
        self.pwm.off = self.off
        self.pwm.start(self.pwm.off)
        state = comm.State()
        state.level = 0
        state.ramped = False
        state.rampDuration = int(app.config['RAMP_DURATION'])
        comm.set_state(app, state)
 
    def ramp(self, initialLevel, finalLevel, 
                duration=int(app.config['RAMP_DURATION']), updateLevel = False):
    # ramp up or down the LED intensity
        rampLED(self.pwm, initialLevel, finalLevel, duration)
        if updateLevel:
            state = comm.get_state(app)
            state.level = finalLevel
            comm.set_state(app, state)   

    def hardStop(self, setLevel=False):
    # turn of the LED immediately
        self.pwm.change_duty_cycle(self.pwm.off) # or zero
        if setLevel:
            state = comm.get_state(app)
            state.level = 0
            comm.set_state(app, state)

    def hardStart(self,level, updateLevel=False):
        #set the LED to level immediately
        if self.pwm.off == 100:
            self.pwm.change_duty_cycle(100 - level)
        else:
            self.pwm.change_duty_cycle(level)
        if updateLevel:
            state = comm.get_state(app)
            state.level = level
            comm.set_state(app, state)


    def setLevel(self, updateLevel=False):
        # get the current level
        state = comm.get_state(app)
        LOGGER.debug(f"entered setLevel with state = {state}")
        if state == None:
            LOGGER.error("state not initialized")
            return
        if state.level != state.next_level:
            if state.ramped:
                self.ramp(state.level, state.next_level, state.rampDuration)
            else:
                if self.pwm.off == 100:
                    self.pwm.change_duty_cyle(100 - state.next_level)
                else:
                    self.pwm.change_duty_cycle(state.next_level)
            if updateLevel:
                state.level = state.next_level
                comm.set_state(app,state)
