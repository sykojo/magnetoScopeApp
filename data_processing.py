from serial_thread import SerialThread
from app_config import AppConfig, Axis

import numpy as np


class DataProcessor:
    def __init__(self, serial_thread: SerialThread, n_samples:int,n_sensors:int) -> None:
        self.serial_thread = serial_thread
        self.n_samples = n_samples
        self.n_sensors = n_sensors
        self._previous_sample: list[tuple[int, int, int]] = [(0,0,0) for _ in range(self.n_sensors)]
        self._current_sample:list[tuple[int,int,int]] = [(0,0,0) for _ in range(self.n_sensors)]
        self._old_samples: list[list[tuple[int,int,int]]] = []
        self._max_values:list[list[int]]= [[0,0,0] for _ in range(self.n_sensors)]

    def get_current_sample(self) -> list[tuple[int, int, int]]:
        return self._current_sample

    def load_new_sample(self) -> None:
        self._current_sample = self.serial_thread.get_oldest_sample()
        self._calculate_max()

    def setNsamples(self, n_samples: int):
        self.n_samples = n_samples

    def get_one_sensor_raw_data(self, which_sensor: int) -> tuple[int, int, int]:
        sample = self._current_sample
        if sample == []:
            return self._previous_sample[which_sensor]
        try:
            self._previous_sample[which_sensor] = sample[which_sensor]
            return sample[which_sensor]
        except IndexError as e:
            print(e)
            return self._previous_sample[which_sensor]

    def get_one_axis_raw_data(
        self, sensor_data: tuple[int, int, int], which_axis: Axis
    ) -> int:
        if sensor_data == (0, 0, 0):
            return 0
        try:
            return sensor_data[which_axis.value]
        except IndexError:
            raise ValueError("")

    def _calculate_max(self):
        for sen_adr in range(self.n_sensors):
            sensor_data:tuple[int,int,int]=self.get_one_sensor_raw_data(sen_adr)
            sen_data_max:list[int] = self._max_values[sen_adr]
            for axis in Axis:
                axis_data = self.get_one_axis_raw_data(sensor_data,axis)
                if axis_data > sen_data_max[axis.value]:
                    self._max_values[sen_adr][axis.value] = axis_data

    def get_max(self,which_sen:int,which_axis:Axis) -> int:
        return self._max_values[which_sen][which_axis.value]
        
    def get_max_of_all_sen(self) -> list[int]:
        max_xyz:list[int] = [int(float('-inf')),int(float('-inf')),int(float('-inf'))]
        for sen_adr in range(self.n_sensors):
            for axis in Axis:
                if self._max_values[sen_adr][axis.value] > max_xyz[axis.value]:
                    max_xyz[axis.value] = self._max_values[sen_adr][axis.value]

        return max_xyz
