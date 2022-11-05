
from re import A
import sys

import time
import signal
from dawnlite import app
import logging
from dawnlite import comm
from dawnlite.hw.button_utils import Button
from  dawnlite.hw.mainLEDControl import MainLED

LOGGER = logging.getLogger('dawnlite')


def shutdown(*args):
    LOGGER.critical("In button daemon, shutdown called")
    sys.exit(1)

def main():
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    comm.set_ramping(app, 0.0) # set ramping flag to non-ramping

    def pressed(button):
        button.state = 1

    def when_held(button):
        button.state = 2



    dim = Button(app.config['DIM_BUTTON'],None, True)
    dim.when_pressed = pressed

    toggle = Button(app.config['TOGGLE_BUTTON'], None, True)
    toggle.when_pressed = pressed
    toggle.when_held = when_held

    bright = Button(app.config['BRIGHT_BUTTON'], None, True)
    bright.when_pressed = pressed



    
    led = MainLED()
    LOGGER.info("starting button daemon")

    while True:
        if  toggle.state == 1:
            # toggle the light
            LOGGER.debug("toggle light in button")
            rampFlag = comm.get_ramping(app)
            if  rampFlag != 0.0: #if ramping set signal to stop it
                comm.set_ramping(app,-1.0)
                time.sleep(2*rampFlag) # wait out an extra cycle of hte ramp loop
                comm.set_ramping(app,0.0) # set flap to non-ramping
            state = comm.get_state(app)
            LOGGER.debug(f"on entry state={state}")
            if state.level != 0:
                state.level = 50
                state.next_level = 0           
            else:
                state.level = 0
                state.next_level = 50
            state.ramped = False
            comm.set_state(app, state)
            led.setLevel(updateLevel=True)
            toggle.resetState()
        elif toggle.state == 2:
            LOGGER.debug("wants to reset")
            toggle.resetState()
        elif dim.state == 1:
            LOGGER.debug("call for dimmer light")
            dim.resetState()
        elif bright.state == 1:
            LOGGER.debug("call for brighter")
            bright.resetState()

        

if __name__=='__main__':
    main()
