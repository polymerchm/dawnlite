from rpi_hardware_pwm import HardwarePWM
from dawnlite import comm, app
import time

# assumes boot set to hardware PWM

# dtoverlay=pwm-2chan, default pins 18 pwm0 and 19 pwn1
# CURRENTLY CONFIGURED FOR PIN 18/19

pwm = None
freq = None

# set the freqwuency
# set the duty cycle


def initialize():
    global freq, off, pwm
    freq = app.config['PWM_FREQUENCY']
    off = 100 if app.config['LED_TYPE'] == 'common_anode' else 0
    pwm = HardwarePWM(0, hz=freq)
    pwm.off = off
    pwm.start(pwm.off)
    state = comm.State()
    state.light_level = 0
    state.light_on = False
    comm.set_state(app, state)
 
def ramp(initialLevel, finalLevel, duration):
    # ramp up or down the LED intensity
    global pwm
    if initialLevel == -1: # get current level 
        currentState = comm.get_state(app)
        if currentState == None:
            currentLevel = 0
        else:
            currentLevel = currentState.light_level
    else:
        currentLevel = initialLevel
    
    delta = abs(finalLevel - initialLevel)
    inc_dec = +1 if (finalLevel - initialLevel) > 1 else  -1
    delay = float(duration/delta)
        
    for i in range(1,delta+1):
        currentLevel += inc_dec
        if pwm.off == 0:
            level = currentLevel
        else:
            level = 100 - currentLevel
        pwm.change_duty_cycle(level) 
        time.sleep(delay)
    state = comm.State()
    state.light_on = True
    state.light_level = finalLevel
    comm.set_state(app, state)   

def hardStop():
    global pwm
    # turn of the LED immediately
    pwm.change_duty_cycle(pwm.off) # or zero
    state = comm.State()
    state.light_on = False
    state.light_level = 0
    comm.set_state(app, state)

def hardStart(level):
    global pwm
    #set the LED to level immediately
    if pwm.off == 100:
        pwm.change_duty_cycle(100 - level)
    else:
        pwm.change_duty_cycle(level)
    state = comm.State()
    state.light_on = True
    state.light_level = level
    comm.set_state(app, state)


def setlevel(level, ramped=True):
    global pwm
    # get the current level
    state = comm.get_state(app)
    if state == None:
        currentLevel = 0
    else:
        currentLevel = state.light_level
    defaultRamp = app.config['RAMP_DURATION']
    if ramped:
        ramp(currentLevel, level, defaultRamp)
    else:
        if pwm.off == 100:
            pwm.change_duty_cyle(100 - level)
        else:
            pwm.change_duty_cycle(level)
    state.light_on = True
    state.light_level = level
    comm.set_state(app, state)
    

def hearbeat(maxIntensity, period):
    ramp(0,maxIntensity, period/2)
    ramp(maxIntensity,0,period/2)
    state = comm.State()
    state.light_on = False
    state.light_level = 0
    comm.set_state(app, state)
