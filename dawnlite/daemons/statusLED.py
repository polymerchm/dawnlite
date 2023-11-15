import signal
import sys


from dawnlite import app
import logging
from dawnlite.enums import StatusLightMessage as MSG
from dawnlite import comm
from dawnlite import model
import dawnlite.hw.statusLEDControl as LED
import queue
import jsonpickle

commandQueue = queue.Queue()
redis = comm.redis_cli 
redisPubSub = redis.pubsub()

LOGGER = logging.getLogger('dawnlite')


# watch for status light messages on REDIS

# status light types are:
#   solid color (regd, green, yellow or white)
#   red flashing (threaded)
#   white heartbeat (threaded)
#   pulsed white (2, 4 , or 6) (threaded)


interpulseDelay = float(app.config['STATUS_LED_INTERPULSE_DELAY'])
PWM = app.config['STATUS_LED_PWM']


# convert so that it uses REDIS pubsub to look for a status light message

cycles = {
            MSG.PULSE_2 : 2, 
            MSG.PULSE_4 : 4, 
            MSG.PULSE_6 : 6
        }

def shutdown(*args):
    # clear the status queue
    sys.exit(0)

def stopThread(thread):
    """
    this stops the thread from LED
    """
    if thread.is_alive():
        thread.event.set()
        thread.join()


def commandReceived(message):
    commandQueue.put(jsonpickle.decode(message))

def main():
    global currentMessage
    redisPubSub.subscribe(**{'status_led': commandReceived})
    redisThread = redisPubSub.run_in_thread(sleep_time=0.010, daemon=True)
    # on startup, clear the status queue
    statusLED = LED.StatusLED(PWM)
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    LOGGER.info("starting statusLED daemon")
    while True:
        if commandQueue.empty():
            continue
        else:
            msg = commandQueue.get()
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



        
        
        


