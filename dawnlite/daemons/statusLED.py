import signal
import sys


from dawnlite import app
import logging
from dawnlite.enums import StatusLightMessage as MSG
from dawnlite import comm
from dawnlite import model
import dawnlite.hw.statusLEDControl as LED


LOGGER = logging.getLogger('dawnlite')


# watch for status light messages on REDIS

# status light types are:
#   solid color (regd, green, yellow or white)
#   red flashing (threaded)
#   white heartbeat (threaded)
#   pulsed white (2, 4 , or 6) (threaded)

status_queue = app.config['STATUS_LIGHT_QUEUE_KEY']
interpulseDelay = float(app.config['STATUS_LED_INTERPULSE_DELAY'])
PWM = app.config['STATUS_LED_PWM']




cycles = {
            MSG.PULSE_2 : 2, 
            MSG.PULSE_4 : 4, 
            MSG.PULSE_6 : 6
        }

def shutdown(*args):
    # clear the status queue
    sys.exit(0)

def stopThread(thread):
    if thread.is_alive():
        thread.event.set()
        thread.join()

def main():
    # on startup, clear the status queue
    comm.clearQueue(status_queue)
    statusLED = LED.StatusLED(PWM)
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    LOGGER.info("starting statusLED daemon")
    while True:
        msg = comm.receive_message(status_queue, timeout=1) # hold for a 250 ms then cycle
        if msg == None:
            continue
        # process the incomeing message
        if msg == MSG.OFF:
            statusLED.turnOff()
        elif msg == MSG.HEARTBEAT:
            stopThread(statusLED)
            statusLED = LED.StatusLED(PWM)
            statusLED.setParameters(level=50, duration=6, pulseType='heartbeat')
            statusLED.start()
        elif msg in cycles.keys():
            stopThread(statusLED)
            statusLED = LED.StatusLED(PWM)
            statusLED.setParameters(level=50, duration=0.500, dutyCycle=0.25, numCycles=cycles[msg], pulseType='hard')
            statusLED.pulseTrain()
        elif msg == MSG.SHUTDOWN:
            LOGGER.critical("called shutdown")
            shutdown()
        else:
            pass
if __name__=='__main__':
    main()



        
        
        


