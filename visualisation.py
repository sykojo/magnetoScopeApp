from data_processing import DataProcessor, Axis
from threading import Event


from PySide6.QtCore import Qt,QTimer
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QGridLayout,
    QPushButton,
    QVBoxLayout,
    QComboBox,
    QGraphicsWidget,
    QGraphicsItem,
    QHBoxLayout
)

import pyqtgraph as pg

import numpy as np


class SpaceScope:
    def __init__(
        self, which_axis, x_label, y_label, title, data_processor, bar_graph
    ) -> None:
        pass


class Window(QMainWindow):
    def __init__(
        self,
        data_processor: DataProcessor,
    ) -> None:
        super().__init__()
        self.data_processor = data_processor
        self.window_layout = QHBoxLayout()
        self.mainWindow = QWidget()
        self.plt_timer = QTimer()
        self.mainWindow.setLayout(self.window_layout)
        self.active_scopes = []
        """Window Properties"""
        self.setWindowTitle("MagnetoScope")
        self.setGeometry(200, 100, 800, 600)
        pg.setConfigOptions(antialias=True)

        """Containers"""
        menu_widget = MenuWidgetWrapper(self)
        self.plot_container = pg.GraphicsLayoutWidget()
        
        """Plots"""
        self.display_time_scopes(3,Axis.x)

        """Buttons"""
        but1 = QPushButton(text="joeMama")
        but2 = QPushButton(text="daineMutter")

        """Menu"""
        menu_widget.layout.addWidget(but1)
        menu_widget.layout.addWidget(but2)

        """Window Layout"""
        self.window_layout.addWidget(menu_widget.get_menu_widget())
        self.window_layout.addWidget(self.plot_container)

        self.setCentralWidget(self.mainWindow)

    def app_exit(self, exit: Event):
        exit.set()
    
    def display_time_scopes(self,n:int,axis:Axis):
        self.active_scopes = []
        self.plot_container.clear()
        for i in range(n):
            ts = TimeScope(0,axis,self.data_processor,"t","B","title")
            self.active_scopes.append(ts)
            self.plot_container.addItem(ts.get_plt(),i,0)

    def display_space_scopes(self):
        raise NotImplemented()
                
    
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
        self.x_axis.setLabel(x_label)
        self.y_axis = pg.AxisItem(orientation="left")
        self.y_axis.setLabel(y_label)
        self.t = 0

        self.frame = self._init_frame()

        """ self.plt = pg.PlotItem(title="tvojeMama",axisItems={"left":self.y_axis,
                                                            "bottom":self.x_axis}) """
        self.plt = pg.PlotItem()
        self.plt.setYRange(-8e7, 8e7)
        self.plt.setTitle(title)
        #self.plt.setAxisItems({"left": self.y_axis, "bottom": self.x_axis})

    def get_plt(self)->pg.PlotItem:
        return self.plt
    
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

    def animate(self) -> None:
        if len(self.frame) == self.data_processor.n_samples:
            self.plt.clear()
            y = []
            n_samples = self.data_processor.n_samples
            y = self.convert2Np(self.frame)
            x = np.linspace(self.t, self.t + n_samples, n_samples)
            self.plt.setXRange(self.t, self.t + self.data_processor.n_samples)
            self.plt.plot(x, y)
            self.t += n_samples
            self.frame.pop(0)

        self.data_processor.set_current_sample()
        self.add_data_to_frame()



class MenuWidgetWrapper:
    def __init__(self, data_processor) -> None:
        self.data_processor = data_processor
        self.menu = QWidget()
        self.layout = QVBoxLayout()
        self.menu.setLayout(self.layout)

    def get_menu_widget(self):
        return self.menu
    
