import datetime
import logging
import signal
# import subprocess
# import sys
import threading
import time
from ast import Pass
from multiprocessing.managers import RemoteError

# import dawnlite
from dawnlite import app, comm, model
from dawnlite.enums import RemoteMessage
from dawnlite.hw.button_utils import Button
from dawnlite.hw.ip_utils import get_ip_address
from dawnlite.hw.mainLEDControl import MainLED

import redis
import queue
import json

from sqlalchemy import create_engine, select, update, delete
from sqlalchemy.orm import Session
from dawnlite.utils import debounce

alarm_queue  = app.config['ALARM_QUEUE_KEY']
remote_queue =  app.config['REMOTE_QUEUE_KEY']
light_queue = app.config['MAIN_LIGHT_QUEUE_KEY']

remoteQueue = queue.Queue()

redis_cli = redis.Redis()
pubsub = redis_cli.pubsub()

engine = create_engine("sqlite:///instance/alarms.db", future=True)
Alarm = model.Alarm

LOGGER = logging.getLogger('dawnlite')
AlarmTimer = None # timer will "bind" here

def call_sse(arg, wait=1):
    @debounce(wait)
    def callit(arg):
        jsonified = json.dumps(arg)
        comm.publish('dawnlite', jsonified)
    callit(arg)



def shutdown(*args):
    comm.send_message(app,comm.StopMessage(), alarm_queue)

def reschedule_alarms(alarms, session=None, wasStopped=False):  
    if session == None:
        session = Session(Alarm)
    upccomingAlarms = []
    dirty = False
    #TODO: try to remove the alarm post duration thingy.
    seconds = 10  if wasStopped else int(app.config['ALARM_POST_DURATION'])
    now = datetime.datetime.now()
    delay = datetime.timedelta(seconds=seconds)
    cutoff = now - delay
    updatedAlarms = []
    for alarm in alarms:
        if alarm.next_alarm is not None and alarm.next_alarm < cutoff:
            dirty = True
            alarm.schedule_next_alarm()
            upccomingAlarms.append(alarm.next_alarm)

        if len(upccomingAlarms) != 0:
            session.commit()
        session.close()
        return sorted(upccomingAlarms) if len(upccomingAlarms) != 0 else None

def find_active_alarm(alarms):
    now = datetime.datetime.now()
    for alarm in alarms:

        alarm_time = alarm.next_alarm
        if alarm_time == None:
            continue
        diff = (now - alarm_time).total_seconds()
        if diff > 0 and diff < alarm.alarmDuration*60: #within the alarm timeframe
            return alarm, True
    return None, False




def manageActiveAlarm(alarms, led, state):
    global AlarmTimer
    if state.level != 0:  # if light is on, don't bother.
        return
    else:
        active_alarm, alarm_pos = find_active_alarm(alarms)
        if active_alarm != None and  AlarmTimer == None :
            if state.active_alarm != active_alarm.id:
                state.update(active_alarm=active_alarm.id, next_level=active_alarm.level)
                comm.set_state(app, state)
                led.setLevel(updateLevel=True)
                AlarmTimer = threading.Timer(active_alarm.alarmDuration*60, endAlarm, args=[led])
                AlarmTimer.start()
 
def endAlarm(*args): # called at end of an alarm duration
    global AlarmTimer
    led = args[0]
    state = comm.get_state(app)
    if  state.active_alarm != 'none':
        state.update(next_level = 0, active_alarm = 'none')
        comm.set_state(app, state)
        led.setLevel(updateLevel=True)
        if AlarmTimer != None:
            AlarmTimer.cancel()
            AlarmTimer = None
        
    


def stopAlarmAndRamp():
    comm.send_message(app, comm.ReloadAlarmsMessage(wasStopped=True), alarm_queue ) 
    rampFlag = comm.get_ramping(app)
    if  rampFlag != 0.0: #if ramping set signal to stop it
        comm.set_ramping(app,-1.0)
        time.sleep(rampFlag) # wait out an extra cycle of hte ramp loop
        comm.set_ramping(app,0.0) # set flap to non-ramping
    
def manageRemoteQueue(state,led):
    """
    Process messages on the Remote Queue
    Return true if the light level has changed

    Note to self '0' is falsey.   Must test for 'None'
    """
    global AlarmTimer
    msg = comm.receive_message(remote_queue, timeout=1)
    if msg == None:
        return None
    else:
        LOGGER.debug(f"receved valid remote message, state is {state}")
        if isinstance(msg, RemoteMessage):
            # cancel the alarm if one is in progress.
            stopAlarmAndRamp()
            if msg == RemoteMessage.BRIGHTER:
                if state.level == 0:
                    state.update(next_level = 10, ramped = False)
                elif state.level == 100:
                    pass
                else:
                    newLevel = min(state.level + 10, 100)
                    state.update(next_level = newLevel, ramped = False) 
                    call_sse({'type': 'sync light', 'value': newLevel, 'caller': 'manageRemoteQueue'})
            elif msg == RemoteMessage.DARKER:
                if state.level == 0:
                    pass
                else:
                    newLevel = max(state.level - 10, 0)
                    state.update(next_level=newLevel, ramped=False)
                    call_sse({'type': 'sync light', 'value': newLevel, 'caller': 'manageRemoteQueue'})
            elif msg == RemoteMessage.TOGGLE:
                if state.level != 0:
                    newLevel = 0
                else:
                    newLevel = 50
                state.update(next_level=newLevel, ramped=True)
                call_sse({'type': 'sync light', 'value': newLevel, 'caller': 'manageRemoteQueue'})
            elif msg == RemoteMessage.OFF:
                state.update(next_level=0, ramped=False)
                call_sse({'type': 'sync light', 'value': 0, 'caller': 'manageRemoteQueue'})
            elif msg == RemoteMessage.LOW:
                state.update(next_level = 25, ramped = True)
                call_sse({'type': 'sync light', 'value': 25, 'caller': 'manageRemoteQueue'})
            elif msg == RemoteMessage.MEDIUM:
                state.update(next_level = 50, ramped = True)
                call_sse({'type': 'sync light', 'value': 50, 'caller': 'manageRemoteQueue'})
            elif msg == RemoteMessage.HIGH:
                state.update(next_level = 100, ramped = True)
                call_sse({'type': 'sync light', 'value': 100, 'caller': 'manageRemoteQueue'})
            elif msg == RemoteMessage.CLEARALARMTIMER:
                if AlarmTimer != None:
                    AlarmTimer.cancel()
                    AlarmTimer = None
                    state.update(active_alarm='none')
                    comm.set_state(app,state)
                return None
            else:
                LOGGER.error(f"invalid message {msg}")
                comm.clearQueue(remote_queue)
                return False
            comm.set_state(app,state)
            led.setLevel(updateLevel=True)
            # comm.publish('dawnlite', f'{{"level": {state.next_level}}}')
            return state.next_level



def manageAlarmQueue(state, led):
    """
    Manages on the Alarm Queue
    If this is  light  change message, send new level
    """
    msg = comm.receive_message(alarm_queue, timeout=1)
    if msg == None:
        return None
    elif isinstance(msg, comm.StopMessage):
        return None
    elif isinstance(msg, comm.SetLightStateMessage):
        stopAlarmAndRamp()
        state.update(next_level=msg.level, ramped=msg.ramped)
        comm.set_state(app,state)
        led.setLevel(updateLevel=True)
        return {"level": msg.level, 'ramped': msg.ramped}
    elif isinstance(msg, comm.ReloadAlarmsMessage):
        with app.app_context():
            model.db.session.rollback()
            alarms = model.Alarm.query.order_by(model.Alarm.time).all()
            value = {"next_alarm": reschedule_alarms(alarms, wasStopped=msg.wasStopped)}
        return value

def manageLightQueue(state, led):
    msg = comm.receive_message(light_queue, timeout=1)
    if msg == None:
        return None
    else:
        stopAlarmAndRamp()
        state.update(next_level=msg.level, ramped=msg.ramped)
        comm.set_state(app,state)
        led.setLevel(updateLevel=True)
        return {"level": msg.level, 'ramped': msg.ramped}

def main():
    global AlarmTimer
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
   

    led = MainLED()

    LOGGER.info("starting main daemon")
    state = comm.get_state(app)
    comm.set_ramping(app, 0.0) # set ramping flag to non-ramping
    last_alarm_refresh = datetime.datetime(1970,1,1)
    last_alarm = datetime.datetime(1970,1,1)
    last_level = 999
    for key in [alarm_queue, remote_queue, light_queue]:
        comm.clearQueue(key)
    while True:
        state = comm.get_state(app)
        with Session(engine, future=True) as session: 
            alarms = session.query(Alarm).all()
            nextAlarms = reschedule_alarms(alarms, session=session)
            if nextAlarms != None:
                alarms = session.query(Alarm).all()


        # handle the remote and buttons
        result = manageRemoteQueue(state,led)
        if result != None and result != last_level:
            last_level = result
            print(f" Remote queue - new level is {result}")
        
        #handle the alarms
        #
        result = manageAlarmQueue(state, led)
        if result  == None:
            pass
        elif "level" in result.keys() and result["level"] != last_level:
            print(f"Alarm Queue - new level is {result}")
            last_level = result["level"]
        elif "next_alarm" in result.keys() and last_alarm != result['next_alarm']:
            print(f"AlarmQueue - next alarm to go off {result}")
            last_alarm = result["next_alarm"]
        
        #handle light messages 
        #
        result = manageLightQueue(state, led)
        if result != None:
            print(f"Light Queue  - new level is {result}")

        #  check/react to the alarms.
        #
        manageActiveAlarm(alarms, led, state)
        result = reschedule_alarms(alarms)
        if result != None and result != last_alarm:
            last_alarm = result
            print(f"ActiveAlarm - next alarm is {result}")

if __name__ == '__main__':
    main()




