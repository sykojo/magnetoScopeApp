from serial_thread import SerialThread
from app_config import AppConfig, Axis

import numpy as np


class DataProcessor:
    def __init__(self, serial_thread: SerialThread, n_samples) -> None:
        self.serial_thread = serial_thread
        self.n_samples = n_samples
        self._previous_sample: list[tuple[int, int, int]] = self._init_buffer()
        self._current_sample: list[tuple[int, int, int]] = self._init_buffer()

    def get_current_sample(self) -> list[tuple[int, int, int]]:
        return self._current_sample

    def _init_buffer(self) -> list[tuple[int, int, int]]:
        buffer = []
        for i in range(self.n_samples):
            buffer.append((0, 0, 0))
        return buffer

    def set_current_sample(self) -> None:
        self._current_sample = self.serial_thread.get_oldest_sample()

    def setNsamples(self, n_samples: int):
        self.n_samples = n_samples

    def get_one_sensor_data(self, which_sensor: int) -> tuple[int, int, int]:
        sample = self._current_sample
        if sample == []:
            return self._previous_sample[which_sensor]
        try:
            self._previous_sample[which_sensor] = sample[which_sensor]
            return sample[which_sensor]
        except IndexError as e:
            print(e)
            return self._previous_sample[which_sensor]

    def get_one_axis_data(
        self, sensor_data: tuple[int, int, int], which_axis: Axis
    ) -> int:
        if sensor_data == (0, 0, 0):
            return 0
        try:
            return sensor_data[which_axis.value]
        except IndexError:
            raise ValueError("")

    # do data processing here?
