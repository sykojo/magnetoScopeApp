from enum import Enum


class AppConfig:
    """Time constants"""
    SERIAL_SLEEP = 0.048
    PLOT_TIMER_SLEEP_MS = 20
    TIME_FOR_MSG_TRANSFER = 0.012 #s
    DATA_PROCESSOR_SLEEP = 0.008

    DEBUG_MODE_ENABLED = True

    N_SAMPLES = 2000
    N_SENSORS = 8
    N_AXES = 3
    ACTIVE_SEN = 7
    SPACE_VIEW = "SpaceView"
    TIME_VIEW = "TimeView"
    

    REQUEST_DATA_CHAR = '?'


class Axis(Enum):
    x = 0
    y = 1
    z = 2
    def as_string(self)->str:
        if self == Axis.x:
            return "X"
        elif self == Axis.y:
            return "Y"
        elif self == Axis.z:
            return "Z"
        else:
            return "UnknownAxe"



""" class SenNum(Enum):
    sen0 = 0
    sen1 = 1
    sen2 = 2
    sen3 = 3
    sen4 = 4
    sen5 = 5
    sen6 = 6
    sen7 = 7 """
