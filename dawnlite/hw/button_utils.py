
import logging
import dawnlite
from gpiozero import Button as GPIOZEROButton

LOGGER = logging.getLogger('dawnlite')


#assumed button connect to +3V when pressed.



class Button(GPIOZEROButton):

    def __init__(self, channel, 
                    pull_up, 
                    active_state,
                    hold_time=10):
        super(GPIOZEROButton, self).__init__(channel, pull_up, active_state, bounce_time=0.02)
        self.state = 0
        self.hold_time = hold_time

    def resetState(self):
        self.state = 0



 







        
 
    
        






