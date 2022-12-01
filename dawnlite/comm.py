import attr 
import jsonpickle
import redis
import datetime

import dawnlite
import logging
import sys

redis_cli = redis.Redis()
last_message_time = datetime.datetime(1953, 7, 21)
last_message = ""
LOGGER = logging.getLogger('dawnlite')

@attr.s
class Message:
    pass

@attr.s
class StopMessage(Message):
    pass

@attr.s
class SetLightStateMessage(Message):
    level = attr.ib(type=int)
    ramped = attr.ib(type=bool, default=False)
    rampDuration = attr.ib(type=float, default= 2.0) #ramp time

@attr.s
class ReloadAlarmsMessage(Message):
    wasStopped = attr.ib(type=bool, default=False)

    def __init__(self, wasStopped=False):
        self.wasStopped = wasStopped

@attr.s
class State:
    defaultLevel = attr.ib(type=int, default=100) 
    level = attr.ib(type=int, default=100)
    next_level = attr.ib(type=int, default=100)
    active_alarm = attr.ib(type=str, default='none')
    alarmDuration = attr.ib(type=int, default=20 * 60)  # 20 minute duration
    ramped = attr.ib(type=bool, default=False)
    rampDuration = attr.ib(type=int, default=2) # 2 second ramp as default



    def _repr(self, **fields):
        '''
        Helper for __repr__
        '''
        field_strings = []
        at_least_one_attached_attribute = False
        for key, field in fields.items():
            field_strings.append(f'{key}={field!r}')
            at_least_one_attached_attribute = True
        if at_least_one_attached_attribute:
            return f"<{self.__class__.__name__}({','.join(field_strings)})>"
        return f"<{self.__class__.__name__} {id(self)}>"


    def __repr__(self):
        return self._repr(
            level = self.level, 
            next_level = self.next_level,
            active_alarm = self.active_alarm,
            alarmDuration = self.alarmDuration,
            ramped = self.ramped,
            rampDuration = self.rampDuration)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if not hasattr(self, key):
                LOGGER.error(f"state does not have key/value {key}/{value}")
                sys.exit(1)
            setattr(self, key, value)








@attr.s
class WiFi:
    address = attr.ib(type=str, default = "")
    ssid = attr.ib(type=str, default = "")
    password = attr.ib(type=str, default = "")

def send_message(app, message, queue_key):
    global last_message, last_message_time
    # LOGGER.debug(f"send_message msg={message}, queue={queue_key}")
    now = datetime.datetime.now()
    # supress a repeat message sooner than the cutoff
    if message == last_message and (now - last_message_time).total_seconds() < app.config['REMOTE_REPEAT_DELAY']:
        pass
    else:
        data = jsonpickle.encode(message)
        redis_cli.rpush(queue_key, data)
    last_message = message
    last_message_time = now
    


def receive_message(queue_key, timeout=1):
    data = redis_cli.blpop(queue_key, timeout)
    if data == None:
        return None
    msg = jsonpickle.decode(data[1])
    return msg

def set_state(app, state):
    # LOGGER.debug(f"in set_state state={state}")
    state.defaultLevel = 100 if app.config['LED_TYPE'] == "common_anode" else 0
    data = jsonpickle.encode(state)
    redis_cli.set(app.config['DAWNLITE_STATE_KEY'], data)

def get_state(app):
    data = redis_cli.get(app.config['DAWNLITE_STATE_KEY'])
    if data is None:
        LOGGER.error("no state available, initializing")
        state = State()
        set_state(state)
    else:
        state = jsonpickle.decode(data)
    # LOGGER.debug(f"in get_state state={state}")
    return state

def get_ramping(app):
    value = float(redis_cli.get(app.config['DAWNLITE_RAMPING_KEY']))
    if type(value) != float:
        LOGGER.error(f'Ramping return non floating point result {value}')
        sys.exit(1)
    else:
        return value

def set_ramping(app, value):
    if type(value) != float:
        LOGGER.error(f'Ramping return non floating point result {value}')
        sys.exit(1)
    else:
         redis_cli.set(app.config['DAWNLITE_RAMPING_KEY'], value)
        


def clearQueue(queName):
    redis_cli.delete(queName)


if __name__=='__main__':
    LOGGER.debug("starting comm")