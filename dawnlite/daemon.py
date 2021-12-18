import signal
import datetime



from dawnlite import app
from dawnlite import comm
from dawnlite import graphics
from dawnlite import model
import hw.ledControl as LED

alarm_queue = app.config['REDIS_ALARM_QUEUE_KEY']
remote_queue = app.config['REDIS_REMOTE_QUEUE_KEY']

def shutdown(signum, frame):
    comm.send_message(app, comm.StopMessage(), alarm_queue)


def clear_screen(led_screen):
    surface = led_screen.make_surface()
    surface.fill(0, 0, 0)
    led_screen.draw_surface(surface)





def reschedule_alarms(alarms):
    dirty = False
    cutoff = datetime.datetime.now() - datetime.timedelta(seconds=app.config['ALARM_POST_DURATION'])
    for alarm in alarms:
        if alarm.next_alarm is not None and alarm.next_alarm < cutoff:
            dirty = True
            if not alarm.repeat:
                alarm.enabled = False
            alarm.schedule_next_alarm()
    if dirty:
        model.db.session.commit()


def find_active_alarm(alarms):
    now = datetime.datetime.now()
    for alarm in alarms:
        alarm_time = alarm.next_alarm
        if alarm_time is None:
            continue
        diff = (now - alarm_time).total_seconds()
        if diff < 0 and -diff < app.config['ALARM_PRE_DURATION']:
            return alarm, diff / app.config['ALARM_PRE_DURATION']
        elif diff > 0 and diff < app.config['ALARM_POST_DURATION']:
            return alarm, diff / app.config['ALARM_POST_DURATION']
    return None, 0


def main():

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    state = comm.State()

    sunrise_alarm = graphics.Sunrise(led_screen)
    alarms = model.Alarm.query.order_by(model.Alarm.time).all()

    while True:
        # handle the remote first
        #
        msg = comm.receive_message(app, remote_queue, timeout=1)
        if msg == None:
            pass

        # handle the alarms
        #
        msg = comm.receive_message(app, alarm_queue, timeout=1)
        if isinstance(msg, comm.StopMessage):
            clear_screen(led_screen)
            break
        elif isinstance(msg, comm.SetLightStateMessage):
            state.light_on = msg.on
        elif isinstance(msg, comm.ReloadAlarmsMessage):
            model.db.session.rollback()
            alarms = model.Alarm.query.order_by(model.Alarm.time).all()
        LED.ramp(-1, state.light_level, app.config["RAMP_DURATION"])
        reschedule_alarms(alarms)
        comm.set_state(app, state)

if __name__ == '__main__':
    main()

