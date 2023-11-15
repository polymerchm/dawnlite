
import logging
from dawnlite import app
import re
from gpiozero import Button as GPIOZEROButton
import sys

LOGGER = logging.getLogger('dawnlite')


#assumed button connect to +3V when pressed.



class Button(GPIOZEROButton):

    def __init__(self, channel, 
                    pull_up, 
                    active_state,
                    hold_time=5):
        super(GPIOZEROButton, self).__init__(channel, pull_up=pull_up, active_state=active_state, bounce_time=0.02)
        self.state = 0
        self.hold_time = hold_time

    def resetState(self):
        self.state = 0


def buttonPort(buttonString):
    if not buttonString in app.config(buttonString):
        print(f'{buttonString} is an invalid key')
        sys.exit(1)

    
    match = re.match('^GPIO(\d*)$', app.config[buttonString])
    if match == None:
        print(f'{buttonString} is an invalid key')
        sys.exit(1)

    return int(match[0])

    
        
    

 







        
 
    
        






