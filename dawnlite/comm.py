import attr
import pickle
import redis
from dawnlite import app

redis_cli = redis.Redis()

@attr.s
class Message:
    pass


@attr.s
class StopMessage(Message):
    pass


@attr.s
class SetLightStateMessage(Message):
    on = attr.ib(type=bool)
    level = attr.ib(type=int)


@attr.s
class ReloadAlarmsMessage(Message):
    pass


@attr.s
class State:
    light_on = attr.ib(type=bool, default=False)
    defaultLevel = 100 if app.config['LED_TYPE'] == "common_anove" else 0
    light_level = attr.b(type=int, default=defaultLevel)
    active_alarm = attr.ib(type=int, default=-1)


def send_message(app, message, queue_key):
    data = pickle.dumps(message)
    redis_cli.rpush(queue_key, data)


def receive_message(app, queue_key, timeout=1):
    data = redis_cli.blpop(queue_key, timeout)
    if data is None:
        return None
    msg = pickle.loads(data[1])
    return msg

def set_state(app, state):
    data = pickle.dumps(state)
    redis_cli.set(app.config['REDIS_STATE_KEY'], data)


def get_state(app):
    data = redis_cli.get(app.config['REDIS_STATE_KEY'])
    if data is None:
        return State()
    return pickle.loads(data)