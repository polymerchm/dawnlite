from email.mime import message
import sys


import socket
import time
import signalls 
from dawnlite import app
from dawnlite import comm
import dawnlite.hw.statusLEDControl as StatusLEDControl
from dawnlite.enums import RemoteMessage
from dawnlite.enums import StatusLightMessage as STATUS
from dawnlite.hw.button_utils import Button

SOCKPATH = "/var/run/lirc/lircd"

#globals

remote_queue = app.config['REDIS_REMOTE_QUEUE_KEY']
status_queue = app.config['REDIS_STATUS_LIGHT_QUEUE_KEY']




message = {
    "A"     : RemoteMessage.LOW,
    "B"     : RemoteMessage.MEDIUM,
    "C"     : RemoteMessage.HIGH,
    "power" : RemoteMessage.TOGGLE,
    "up"    : RemoteMessage.BRIGHTER,
    "down"  : RemoteMessage.DARKER,
    "left"  : RemoteMessage.BRIGHTER,
    "right" : RemoteMessage.DARKER,
    "enter" : RemoteMessage.OFF,
}

class IRW():
    def __init__(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(SOCKPATH)


    def next_key(self):
        '''Get the next key pressed. Return keyname, updown.
        '''
        try:
            data = self.sock.recv(128) # this is a blocking read 
            data = data.strip()
            words = data.split()
            return words[2].decode('utf-8'), int(words[1])
        except: 
            # too many signals, warn the user then pause
            comm.send_message(app, STATUS.PULSE_6, status_queue)
            time.sleep(5)
            return -1, -1

def sendRemoteMessage(msg):
    comm.send_message(app,msg,remote_queue)

def shutdown(*arg):
    sendRemoteMessage(comm.StopMessage())
    sys.exit(1)




def main():
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    irRemote = IRW()
    button = Button()

    statusLed = StatusLEDControl.StatusLED(int(app.config['STATUS_LED_PWM']))
    statusLed.setParameters(duration=0.05, level=100)
    while True:
        # next command is blocking, so waits for an IR code
        command, code  = irRemote.next_key() 
        if code == 0:
            statusLed.hardPulse() # echo the IR pulse
            if command in message.keys():
                sendRemoteMessage(message[command])
            else:
                continue

if __name__=='__main__':
    main()



   
        






    
        
    


    






