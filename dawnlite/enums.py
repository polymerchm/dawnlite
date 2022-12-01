from enum import auto, Enum

class StatusLightMessage(Enum):
    OFF = auto()
    HEARTBEAT = auto()
    ON = auto()
    PULSE_2 = auto()
    PULSE_4 = auto()
    PULSE_6 = auto()
    SHUTDOWN = auto()

class RemoteMessage(Enum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    TOGGLE = auto()
    BRIGHTER = auto()
    DARKER = auto()
    OFF = auto()
    CLEARALARMTIMER = auto()

class LightState(Enum):
    ON = "on"
    OFF = "off"
    ALARM_ACTIVE = "active"