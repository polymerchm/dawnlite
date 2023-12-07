import redis
import re
import ast


        
class Monitor():
    def __init__(self, connection_pool):
        self.connection_pool = connection_pool
        self.connection = None
        
    def __del__(self):
        try:
            self.reset()
        except:
            pass

    def reset(self):
        if self.connection:
            self.connection_pool.release(self.connection)
            self.connection = None

    def monitor(self):
        if self.connection is None:
            self.connection = self.connection_pool.get_connection(
                'monitor', None)
        self.connection.send_command("monitor")
        return self.listen()
    
    def parse_response(self):
        return self.connection.read_response()

    def listen(self):
        while True:
            yield self.parse_response()

def parseCommand(c):
    line = c.decode('utf-8')
    command = ""
    queue = ""
    value = ""
    pattern = r'\d{10}.*(\".*\") (\".*\") (.*$)'
    result = re.match(pattern, line)
    if result != None:
        (command, queue, value) = result.groups()
        return (command, queue, value)
    else:
        return None
        
if  __name__ == '__main__':

    queues = ['dawnlite_alarm_queue', 'dawnlite_remote_queue', 'dawnlite_main_light_queue']
    
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    monitor = Monitor(pool)
    commands = monitor.monitor()

    for c in commands :
        result = parseCommand(c)
        if result != None:
            
            command = ast.literal_eval(result[0])
            queue = ast.literal_eval(result[1])
            value = ast.literal_eval(result[2])
            if queue in queues:
                if command != 'BLPOP':
                    print(f"{command} {queue} {value}")
        
