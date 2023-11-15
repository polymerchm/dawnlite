

from locale import setlocale
from dawnlite import comm
import time
import math

from dawnlite import app
import logging
LOGGER = logging.getLogger('dawnlite')


# this ramps the designated LED
# the rampflag (stored n redis) hold the number of durection betwen lvel change steps (in seconds)
# if set to a negative number during a a ramp (by another process), it halts the ramp.

def rampLED(pwm, initialLevel=-1, finalLevel=-1, duration=app.config['RAMP_DURATION']):
    LOGGER.debug(f"In rampLED - initial={initialLevel} final={finalLevel}, duration={duration}")
    # ramp up or down the LED intensity
    rampSteps = app.config['RAMP_STEPS']
    state = comm.get_state(app)
    if initialLevel == -1: # get current level 
        if state == None:
            currentLevel = 0
        else:
            currentLevel = state.level
    else:
        currentLevel = initialLevel
    if finalLevel == -1: 
        nextLevel = state.next_level
    else:
        nextLevel = finalLevel

    
    delta = abs(finalLevel - initialLevel)
    if delta == 0:
        return
    inc_dec = +1 if (finalLevel - initialLevel) > 1 else  -1
    delay = float(duration/rampSteps)
    inc_delta = inc_dec * delta/rampSteps


    comm.set_ramping(app, delay) # set flag for ramping   
    for i in range(0,rampSteps):
        rampFlag = comm.get_ramping(app) # monitor for changes
        if rampFlag >= 0.0:
            currentLevel += inc_delta
            if pwm.off == 0:
                level = currentLevel
            else:
                level = 100 - currentLevel
            pwm.change_duty_cycle(min(100,max(math.floor(level),0)))
            time.sleep(delay)
        else:
            break
    
    # store the curent state
    state.level = min(100,max(math.floor(currentLevel),0))
    comm.set_state(app, state)
    comm.set_ramping(app,0.0)  #to be sure