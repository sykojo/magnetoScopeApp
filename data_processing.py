from serial_thread import SerialThread
from communication import DataDecode
from app_config import AppConfig, Axis

import numpy as np
import threading
import time




class DataProcessor:
    def __init__(self, serial_thread: SerialThread, n_samples:int,n_sensors:int,app_exit:threading.Event) -> None:
        self.serial_thread = serial_thread
        self._app_exit = app_exit
        self.n_samples = n_samples
        self.n_sensors = n_sensors
        self._lock = threading.Lock()
        self.running = True

        self._processed_samples: list[list[tuple[int,int,int]]] = []
        self._old_samples: list[list[tuple[int,int,int]]] = []
        self._max_values:list[list[int]]= [[0,0,0] for _ in range(self.n_sensors)]

    def get_one_sensor_data(self,which_sample, which_sensor: int) -> tuple[int, int, int]:
        sample = which_sample
        return sample[which_sensor]

    def get_one_axis_data(
        self, sensor_data: tuple[int, int, int], which_axis: Axis
    ) -> int:
        return sensor_data[which_axis.value]

    def calculate_max_for_each_axis(self,sample:list[tuple[int,int,int]])->list[list[int]]:
        for sen_adr in range(self.n_sensors):
            sensor_data =self.get_one_sensor_data(sample,sen_adr)
            max_of_sen = self._max_values[sen_adr]
            for axis in Axis:
                axis_data = self.get_one_axis_data(sensor_data,axis)
                with self._lock:
                    if axis_data > max_of_sen[axis.value]:
                        self._max_values[sen_adr][axis.value] = axis_data
        return self._max_values

    def get_max(self,which_sen:int,which_axis:Axis) -> int:
        with self._lock:
            return self._max_values[which_sen][which_axis.value]
        
    def get_max_of_all_sen(self) -> list[int]:
        max_xyz:list[int] = [int(1e-9),int(1e-9),int(1e-9)]
        for sen_adr in range(self.n_sensors):
            for axis in Axis:
                with self._lock:
                    if self._max_values[sen_adr][axis.value] > max_xyz[axis.value]:
                        max_xyz[axis.value] = self._max_values[sen_adr][axis.value]

        return max_xyz
    
    def get_processed_samples(self)->list[list[tuple[int,int,int]]]:
        samples = []
        with self._lock:
            samples=self._processed_samples
            self._processed_samples=[]
        return samples

    def run_data_processing(self):
        while not self._app_exit.is_set():
            if self.running:
                data = self.serial_thread.get_all_samples()
                for sample in data:
                    self._old_samples.append(sample)
                    self.calculate_max_for_each_axis(sample)  
                    #TODO WHEN you have other prcessing functions place them here
                    #-----processing functions will modify sample
                    self._processed_samples.append(sample)
                time.sleep(AppConfig.DATA_PROCESSOR_SLEEP)
            else:
                time.sleep(0.1)



