import datetime
import logging
import signal
import subprocess
import sys
import threading
import time
from ast import Pass
from multiprocessing.managers import RemoteError

import dawnlite
from dawnlite import app, comm, model
from dawnlite.enums import RemoteMessage
from dawnlite.hw.button_utils import Button
from dawnlite.hw.ip_utils import get_ip_address
from dawnlite.hw.mainLEDControl import MainLED

alarm_queue  = dawnlite.app.config['ALARM_QUEUE_KEY']
remote_queue =  dawnlite.app.config['REMOTE_QUEUE_KEY']
light_queue = dawnlite.app.config['MAIN_LIGHT_QUEUE_KEY']

LOGGER = logging.getLogger('dawnlite')
AlarmTimer = None # timer will "bind" here


def shutdown(*args):
    comm.send_message(app,comm.StopMessage(), alarm_queue)

def reschedule_alarms(alarms, wasStopped=False):  
    dirty = False
    #TODO: try to remove the alarm post duration thingy.
    seconds = 10  if wasStopped else int(dawnlite.app.config['ALARM_POST_DURATION'])
    now = datetime.datetime.now()
    delay = datetime.timedelta(seconds=seconds)
    cutoff = now - delay
    for alarm in alarms:
        if alarm.next_alarm is not None and alarm.next_alarm < cutoff:
            dirty = True
            alarm.schedule_next_alarm()
    if dirty:
        model.db.session.commit()

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




def configure_light(alarms, led):
    global AlarmTimer
    state = comm.get_state(app)
    if state.level != 0:  # if light is on, don't bother.
        return
    else:
        active_alarm, alarm_pos = find_active_alarm(alarms)
        if active_alarm != None and  AlarmTimer == None :
            if state.active_alarm != active_alarm.id:
                state.update(active_alarm=active_alarm.id, next_level=active_alarm.level)
                comm.set_state(app, state)
                led.setLevel(updateLevel=True)
                AlarmTimer = threading.Timer(active_alarm.alarmDuration*60,
                                                endAlarm, args=[led])
                AlarmTimer.start()
 
def endAlarm(*args): # called at end of an alarm duration
    global AlarmTimer
    led = args[0]
    state = comm.get_state(app)
    if  state.active_alarm != 'none':
        # comm.send_message(app, comm.ReloadAlarmsMessage(), alarm_queue ) 
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
    

def main():
    global AlarmTimer
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    alarms = model.Alarm.query.order_by(model.Alarm.time).all()
    LOGGER.debug(f"initial state of alarms = {alarms}")
    led = MainLED()
    oldState = None

    LOGGER.info("starting main daemon")
    state = comm.get_state(app)
    comm.set_ramping(app, 0.0) # set ramping flag to non-ramping

    while True:
        state = comm.get_state(app)

        # handle the remote 
        #
        msg = comm.receive_message(remote_queue, timeout=1)
        if msg == None:
            pass
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
                elif msg == RemoteMessage.DARKER:
                    if state.level == 0:
                        pass
                    else:
                        newLevel = max(state.level - 10, 0)
                        state.update(next_level=newLevel, ramped=False)
                elif msg == RemoteMessage.TOGGLE:
                    if state.level != 0:
                        state.update(next_level=0, ramped=True)
                    else:
                        state.update(next_level=50)
                elif msg == RemoteMessage.OFF:
                    state.update(next_level=0, ramped=False)
                elif msg == RemoteMessage.LOW:
                    state.update(next_level = 25, ramped = True)
                elif msg == RemoteMessage.MEDIUM:
                    state.update(next_level = 50, ramped = True)
                elif msg == RemoteMessage.HIGH:
                    state.update(next_level = 100, ramped = True)
                elif msg == RemoteMessage.CLEARALARMTIMER:
                    if AlarmTimer != None:
                        AlarmTimer.cancel()
                        AlarmTimer = None
                        state.update(active_alarm='none')
                        comm.set_state(app,state)
                    continue 
                else:
                    LOGGER.error(f"invalid message {msg}")
                    comm.clearQueue(remote_queue)
                    continue
                comm.set_state(app,state)
                led.setLevel(updateLevel=True)
                continue
            else:
                pass # it's not a valid message in this queue

        #handle the alarms
        #
        msg = comm.receive_message(alarm_queue, timeout=1)
        if msg == None:
            pass
        elif isinstance(msg, comm.StopMessage):
            break
        elif isinstance(msg, comm.SetLightStateMessage):
            stopAlarmAndRamp()
            state.update(next_level=msg.level, ramped=msg.ramped)
            comm.set_state(app,state)
            led.setLevel(updateLevel=True)
            continue
        elif isinstance(msg, comm.ReloadAlarmsMessage):
            model.db.session.rollback()
            alarms = model.Alarm.query.order_by(model.Alarm.time).all()
            reschedule_alarms(alarms, wasStopped=msg.wasStopped)
            # continue        
          
        #check the light queue
        #
        msg = comm.receive_message(light_queue, timeout=1)
        if msg == None:
            pass
        else:
            stopAlarmAndRamp()
            state.update(next_level=msg.level, ramped=msg.ramped)
            comm.set_state(app,state)
            led.setLevel(updateLevel=True)
            # continue
        # no messages, so check/react to the alarms.
        configure_light(alarms, led)
        reschedule_alarms(alarms)

if __name__ == '__main__':
    main()




