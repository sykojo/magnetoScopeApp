from data_processing import DataProcessor
from app_config import Axis, AppConfig


import pyqtgraph as pg

import numpy as np


class SpaceScope:
    def __init__(
        self,
        which_axis: Axis,
        x_label: str,
        y_label: str,
        title: str,
        data_processor: DataProcessor,
    ) -> None:
        self.sen_axis = which_axis
        self.data_processor = data_processor
        self.x_axis = pg.AxisItem(orientation="bottom")
        self.x_axis.setLabel(x_label,"senNum")
        self.y_axis = pg.AxisItem(orientation="left")
        self.y_axis.setLabel(y_label,"mT")

        self.plt_item = pg.PlotItem(axisItems={"left": self.y_axis, "bottom": self.x_axis})
        self.plt_item.setYRange(-80, 80)
        self.plt_item.setTitle(title)

        self.frame = []
        self.frame = self._init_frame()

    def get_plt_item(self) -> pg.PlotItem:
        return self.plt_item

    def _init_frame(self) -> list:
        frame = []
        for i in range(AppConfig.N_SENSORS):
            frame.append(0)
        return frame

    def convert2Np(self, data: list) -> np.ndarray:
        np_array = np.array(data)
        return np_array

    def add_data_to_frame(self) -> None:
        for i in range(0, AppConfig.N_SENSORS, 1):
            sensor_data = self.data_processor.get_one_sensor_data(i)
            axis_data = self.data_processor.get_one_axis_data(
                sensor_data, self.sen_axis
            )
            self.frame.append(axis_data)


class TimeScope:
    def __init__(
        self,
        which_sen: int,
        which_axis: Axis,
        data_processor: DataProcessor,
        x_label: str,
        y_label: str,
        title: str,
        # num_frames:int
    ) -> None:
        self.data_processor = data_processor
        self.sen_num = which_sen
        self.sen_axis = which_axis
        self.x_axis = pg.AxisItem(orientation="bottom")
        self.x_axis.setLabel(x_label,units="N")
        self.y_axis = pg.AxisItem(orientation="left")
        self.y_axis.setLabel(y_label,units="mT")
        self.t = 0

        self.frame = []
        self.frame = self._init_frame()

        """ self.plt = pg.PlotItem(title="tvojeMama",axisItems={"left":self.y_axis,
                                                            "bottom":self.x_axis}) """
        self.plt_item = pg.PlotItem(axisItems={"left": self.y_axis, "bottom": self.x_axis})
        self.plt_item.setYRange(-80, 80)
        self.plt_item.setTitle(title)
        #self.plt_item.setAxisItems()

    def get_plt_item(self) -> pg.PlotItem:
        return self.plt_item

    def add_data_to_frame(self) -> None:
        sensor_data = self.data_processor.get_one_sensor_data(self.sen_num)
        axis_data = self.data_processor.get_one_axis_data(sensor_data, self.sen_axis)
        self.frame.append(axis_data)

    def _init_frame(self) -> list:
        frame = []
        for i in range(self.data_processor.n_samples):
            frame.append(0)
        return frame

    def convert2Np(self, data: list) -> np.ndarray:
        np_array = np.array(data)
        return np_array

