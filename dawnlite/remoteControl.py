import sys

sys.path.append("/home/pi/Programming/dawn_lite")

import socket
import time
import signal
import dawnlite
from dawnlite import comm




SOCKPATH = "/var/run/lirc/lircd"

#globals

app = None
remote_queue_key = None
alarm_queue_key = None



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
            shutdown()
            exit()

def shutdown():
    comm.send_message(app, comm.StopMessage(), alarm_queue_key)


def main():
    global remotee_queue_key, alarm_queue_key, app
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    irRemote = IRW()
    app = dawnlite.app
    remote_queue_key = app.config['REDIS_REMOTE_QUEUE_KEY']
    alarm_queue_key =  app.config['REDIS_ALARM_QUEUE_KEY']
    
    while True:
        command, code  = irRemote.next_key() #thi sis blocked
        if code == 0:
            if command == "A":
                comm.send_message(app, "low", remote_queue_key)
            elif command == "B":
                comm.send_message(app, "medium", remote_queue_key)
            elif command == "C":
                comm.send_message(app, "high", remote_queue_key)
            elif command == "power":
                comm.send_message(app, "toggle", remote_queue_key)
            elif command == "up":
                comm.send_message(app, "darker", remote_queue_key)
            elif command == "down":
                comm.send_message(app, "lighter", remote_queue_key)
            elif command == "left":
                    comm.send_message(app, "darker", remote_queue_key)
            elif command == "right":
                    comm.send_message(app, "lighter", remote_queue_key)
            elif command == "enter":
                comm.send_message(app, "off", remote_queue_key)
            else:
                continue



if __name__ == "__main__":
    main()

   
        






    
        
    


    






