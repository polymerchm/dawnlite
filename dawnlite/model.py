import datetime
import uuid
import flask_sqlalchemy
import typing
import logging
LOGGER = logging.getLogger('dawnlite')



db = flask_sqlalchemy.SQLAlchemy()


class Alarm(db.Model):
    id = db.Column(db.String, primary_key=True, default = "")
    time = db.Column(db.String, nullable=False, default='00:00')
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    repeat_days = db.Column(db.Integer, nullable=False, default=0)
    alarmDuration = db.Column(db.Integer, nullable=False, default=30) #in minutes
    rampDuration = db.Column(db.Integer, nullable=True, default=3)
    level = db.Column(db.Integer, nullable=False, default=50) # 50%
    next_alarm = db.Column(db.DateTime, nullable=True)

    @classmethod
    def nextAlarm(cls, alarm):
        if not alarm.enabled:
            return None
        now = datetime.datetime.now()
        today = datetime.date.today()
        hour, minute = alarm.time.split(':')
        hour, minute = int(hour), int(minute)
        if alarm.repeat_days != 0:
            wd = today.weekday()
            day_offsets = [d - wd for d in range(wd, wd+8) if (2**(d%7)) & alarm.repeat_days]
        else:
            day_offsets = [0, 1]
        for day_offset in day_offsets:
            next_alarm = datetime.datetime(today.year, today.month, today.day, hour, minute)
            next_alarm += datetime.timedelta(days=day_offset)
            if next_alarm > now:
                return next_alarm
        # fell through
        return None

    def repeat2string(self,bitmask):
        out = ""
        pointer = 1
        days = ['Su','Mo','Tu','We','Th','Fr','Sa']
        for i in range(0,len(days)):
            value = days[i] if (bitmask & pointer) != 0 else '__'
            out += value
            pointer = pointer * 2
        return out




    def __repr__(self) -> str:
        day_string = self.repeat2string(self.repeat_days)
        return self._repr(  id=self.id, 
                            time=self.time,
                            enabled=self.enabled,
                            repeat_days=day_string,
                            alarmDuration=self.alarmDuration,
                            rampDuration=self.rampDuration,
                            level=self.level,
                            next_alarm=self.next_alarm)

    def _repr(self, **fields: typing.Dict[str, typing.Any]) -> str:
        '''
        Helper for __repr__
        '''
        field_strings = []
        at_least_one_attached_attribute = False
        for key, field in fields.items():
            try:
                field_strings.append(f'{key}={field!r}')
            except flask_sqlalchemy.orm.exc.DetachedInstanceError:
                field_strings.append(f'{key}=DetachedInstanceError')
            else:
                at_least_one_attached_attribute = True
        if at_least_one_attached_attribute:
            return f"<{self.__class__.__name__}({','.join(field_strings)})>"
        return f"<{self.__class__.__name__} {id(self)}>"


    def to_dict(self):
        return {
            'id': self.id,
            'time': self.time,
            'alarmDuration': self.alarmDuration,
            'rampDuration': self.rampDuration,
            'enabled': self.enabled,
            'level': self.level,
            'repeatDays': self.repeat_days,
            'nextAlarm': self.next_alarm.isoformat() if self.next_alarm else None
        }

    

    def update_from_dict(self, data):
        LOGGER.debug(f"the data to update with is {data}")
        self.id = data.get('id', self.id)
        self.time = data.get('time', self.time if self.time != None else "00:00")
        self.alarmDuration = data.get('alarmDuration', self.alarmDuration)
        self.rampDuration = data.get('rampDuration', self.rampDuration)
        self.enabled = data.get('enabled', self.enabled)
        self.level = data.get('intensity', self.level)
        self.repeat_days = data.get('repeatDays', self.repeat_days)

    def schedule_next_alarm(self):
        newNext = Alarm.nextAlarm(self)
        if not self.enabled:
            self.next_alarm = None
            return
        self.next_alarm  = Alarm.nextAlarm(self)
        # now = datetime.datetime.now()
        # today = datetime.date.today()
        # hour, minute = self.time.split(':')
        # hour, minute = int(hour), int(minute)
        # if self.repeat_days != 0:
        #     wd = today.weekday()
        #     day_offsets = [d - wd for d in range(wd, wd+8) if (2**(d%7)) & self.repeat_days]
        # else:
        #     day_offsets = [0, 1]
        # for day_offset in day_offsets:
        #     next_alarm = datetime.datetime(today.year, today.month, today.day, hour, minute)
        #     next_alarm += datetime.timedelta(days=day_offset)
        #     if next_alarm > now:
        #         self.next_alarm = next_alarm
        #         return
        # # fell through
        # self.next_alarm = None

    

