import socket
import logging

LOGGER = logging.getLogger('dawnlite')



IP_HOST_NAME_FILE = 'host_name.txt'
IP_NETWORK_SSID = 'ssid.txt'
IP_NETWORK_PASSWORD = 'pass.txt'


def reset_ip_data():
    pass
#TODO: erase the existing files
# if the reset button has been held for > 5 seconds, 
# erase the ip config files
# assume if they exist, that the configuration files have been
# apprpriately edited.

def create_ip_data():
    pass

def get_ip_address():
    ip_address = None # default -  not connected
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80))
        ip_address = s.getsockname()[0]
        s.close()
    except:
        pass # can't get out
    return ip_address


if __name__ == '__main__':
    #test
    print(get_ip_address())

