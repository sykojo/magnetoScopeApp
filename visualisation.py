from data_processing import DataProcessor,Axis,SenNum
from threading import Event


from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QGridLayout,
    QPushButton,
    QVBoxLayout,
)

import pyqtgraph as pg

import numpy as np


class TimeScope:
    def __init__(
        self,
        which_sen:SenNum,
        which_axis:Axis,
        data_processor: DataProcessor,
        plt: pg.PlotItem,
        x_label: str,
        y_label: str,
        title: str,
        #num_frames:int
    ) -> None:
        self.data_processor = data_processor
        self.sen_num = which_sen
        self.sen_axis = which_axis
        self.x_axis = pg.AxisItem(orientation="bottom")
        self.x_axis.setLabel(x_label)
        self.y_axis = pg.AxisItem(orientation="left")
        self.y_axis.setLabel(y_label)
        self.t=0

        self.frame = []
        self.frames = []

        """ self.plt = pg.PlotItem(title="tvojeMama",axisItems={"left":self.y_axis,
                                                            "bottom":self.x_axis}) """
        self.plt = plt
        self.plt.setYRange(-8e7,8e7)
        self.plt.setTitle(title)
        self.plt.setAxisItems({"left": self.y_axis, "bottom": self.x_axis})

    def add_data_to_frame(self) ->None:
        sensor_data = self.data_processor.get_one_sensor_data(self.sen_num)
        axis_data = self.data_processor.get_one_axis_data(sensor_data,self.sen_axis)
        self.frame.append(axis_data)

    def convert2Np(self, data: list) -> np.ndarray:
        np_array = np.array(data)
        return np_array

    def animate(self) -> None:
        if len(self.frame) == self.data_processor.n_samples:
            #print(self.frame)
            self.plt.clear()
            y = []
            n_samples = self.data_processor.n_samples
            y=self.convert2Np(self.frame)
            x = np.linspace(self.t,self.t+n_samples,n_samples)
            self.plt.setXRange(self.t,self.t+self.data_processor.n_samples)
            self.plt.plot(x,y)
            self.t+=n_samples
            self.frame.pop(0)
        else:
            pass
            #print(self.frame)
            #print("Waiting for frame completation")
        self.add_data_to_frame()


class Window(QMainWindow):
    def __init__(self,
        data_processor:DataProcessor,        
        ) -> None:
        super().__init__()

        self.data_processor = data_processor

        """Window Properties"""
        self.setWindowTitle("PyQtGraph")
        self.setGeometry(200, 100, 800, 600)
        pg.setConfigOptions(antialias=True)

        widget = QWidget()
        menu = QWidget()

        """Buttons"""
        win = pg.GraphicsLayoutWidget()
        but1 = QPushButton(text="joeMama")
        but2 = QPushButton(text="daineMutter")

        p1 = win.addPlot(row=0, col=0)

        # view = win.addViewBox(row=1, col=0, colspan=2)
        self.p1 = TimeScope(
            SenNum.sen0,
            Axis.x,
            self.data_processor,
            p1,
            "x",
            "y",
            "Title"
            )

        """Menu"""
        menu_layout = QVBoxLayout()
        menu.setLayout(menu_layout)
        menu_layout.addWidget(but1)
        menu_layout.addWidget(but2)

        layout = QGridLayout()
        widget.setLayout(layout)
        layout.addWidget(win, 0, 1, 5, 3)
        layout.addWidget(menu, 0, 0)

        self.setCentralWidget(widget)
        self.show()

    def app_exit(self, exit: Event):
        exit.set()
