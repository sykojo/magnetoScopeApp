from serial_thread import SerialThread
from app_config import AppConfig

from enum import Enum

class Axis(Enum):
    x = 0
    y = 1
    z = 2

class SenNum(Enum):
    sen0 = 0
    sen1 = 1
    sen2 = 2
    sen3 = 3
    sen4 = 4
    sen5 = 5
    sen6 = 6
    sen7 = 7

class DataProcessor():
    def __init__(self, serial_thread:SerialThread,n_samples) -> None:
        self.serial_thread = serial_thread
        self.n_samples=n_samples
        self.previous_sample:tuple[int,int,int] = (0,0,0)
        
    def setNsamples(self, n_samples: int = 50):
        self.n_samples = n_samples

    def get_one_sensor_data(self, which_sensor:SenNum) -> tuple[int,int,int]:
        samples = self.serial_thread.get_oldest_sample()
        if samples == []:
            return self.previous_sample
        try:
            self.previous_sample = samples[which_sensor.value]
            return samples[which_sensor.value]
        except IndexError: 
            return self.previous_sample 

    def get_one_axis_data(self, sensor_data:tuple[int,int,int],which_axis:Axis) -> int:
        if sensor_data == (0,0,0):
            return 0
        try:
            return sensor_data[which_axis.value]
        except IndexError:
            raise ValueError("")
    

    
    # do data processing here?