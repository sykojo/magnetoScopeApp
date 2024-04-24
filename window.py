from data_processing import DataProcessor, Axis
from app_config import AppConfig
from scopes import TimeScope, SpaceScope

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QGridLayout,
    QPushButton,
    QVBoxLayout,
    QComboBox,
    QGraphicsWidget,
    QGraphicsItem,
    QHBoxLayout,
    QLabel
)
from PySide6.QtGui import QIcon

import pyqtgraph as pg
from threading import Event
import numpy as np

x = 0

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
        self.active_timers = []
        """Window Properties"""
        self.setWindowTitle("MagnetoScope")
        self.setGeometry(200, 100, 800, 600)
        pg.setConfigOptions(antialias=True)

        """Containers"""
        menu_widget = MenuWidgetWrapper(self)
        self.plot_container = pg.GraphicsLayoutWidget()

        """Plots"""
        # self.display_time_scopes3()

        """Buttons"""
        but1 = QPushButton(text="Time Measurment")
        but2 = QPushButton(text="Space Measurment")
        but1.clicked.connect(lambda:TimeView(self))
        but2.clicked.connect(lambda:SpaceView(self))
        self.start_stop_button = QPushButton(text="Start")
        self.start_stop_button.setIcon(QIcon("icons/start_button_icon.png"))
        self.start_stop_button.clicked.connect(self.toggle_timer)

        max_label = InfoLabels("MAX")
        self.label_timer = QTimer()
        self.label_timer.timeout.connect(lambda:max_label.animate())
        self.label_timer.start(10)

        """Menu"""
        menu_widget.layout.addWidget(but1)
        menu_widget.layout.addWidget(but2)
        menu_widget.layout.addWidget(InfoLabels("MAX").labels_container)
        menu_widget.layout.addWidget(InfoLabels("MIN").labels_container)
        menu_widget.layout.addWidget(self.start_stop_button)
        
        """Window Layout"""
        self.window_layout.addWidget(menu_widget.get_menu_widget())
        self.window_layout.addWidget(self.plot_container)

        self.setCentralWidget(self.mainWindow)

    def app_exit(self, exit: Event):
        exit.set()
        
    def animateTimeScope(self, scopes: list[TimeScope])-> None:
        for scope in scopes:
            if len(scope.frame) == self.data_processor.n_samples:
                scope.plt_item.clear()
                y = []
                x = []
                n_samples = self.data_processor.n_samples
                y = scope.convert2Np(scope.frame)
                y = y/1000000.0
                x = np.linspace(scope.t, scope.t + n_samples, n_samples)
                scope.plt_item.setXRange(scope.t, scope.t + n_samples)
                scope.plt_item.plot(x, y,pen=(0,250,154))
                scope.t += n_samples
                scope.frame.pop(0)
            scope.add_data_to_frame()
        self.data_processor.set_current_sample()

    def animateSpaceScope(self, scopes: list[SpaceScope])-> None:
        for scope in scopes:
            scope.plt_item.clear()
            x = []
            y = []
            x = np.linspace(0, AppConfig.N_SENSORS - 1, AppConfig.N_SENSORS)
            y = scope.convert2Np(scope.frame)
            y = y/1000000.0
            scope.plt_item.plot(x, y,pen=(0,250,154), symbolBrush=(0,255,0), symbolPen='w')
            scope.frame = []
            scope.add_data_to_frame()
        self.data_processor.set_current_sample()

    def toggle_timer(self):
        if self.plt_timer.isActive():
            self.plt_timer.stop()
            self.start_stop_button.setText('Start')
            
        else:
            self.plt_timer.start(AppConfig.PLOT_TIMER_SLEEP_MS)  
            self.start_stop_button.setText('Stop')
            
    def set_max_time_scope(self,new_max:int):
        pass

    def set_average(self,nes_average:int):
        pass

class MenuWidgetWrapper:
    def __init__(self, data_processor) -> None:
        self.data_processor = data_processor
        self.menu = QWidget()
        self.layout = QVBoxLayout()
        self.menu.setLayout(self.layout)

    def get_menu_widget(self)->QWidget:
        return self.menu
    
class InfoLabels:
    def __init__(self,which_info:str) -> None:
        self.labels_container = QWidget()
        self.labels_container_layout = QVBoxLayout()
        self.labels_container_layout.addWidget(QLabel(which_info))
        self.labels_container.setLayout(self.labels_container_layout)
        self.axes:list[QLabel] = []
        self.values:list[QLabel] = []
        
        for axis in Axis:
            new_axis = self.create_axis(axis)
            new_value = self.create_new_value("-")
            self.axes.append(new_axis)
            self.values.append(new_value)
            container = self.create_label_container(new_axis,new_value)
            self.labels_container_layout.addWidget(container)
    
        self.label_timer = QTimer()
        self.label_timer.timeout.connect(lambda:self.animate())
        self.label_timer.start(100)
        
    def create_axis(self,which_axis:Axis)->QLabel:
        return QLabel(which_axis.as_string())

    def create_label_container(self,axis:QLabel,value:QLabel)->QWidget:
        label_container = QWidget()
        label_container_layout = QHBoxLayout()
        label_container.setLayout(label_container_layout)
        
        label_container_layout.addWidget(axis)
        label_container_layout.addWidget(value)
        return label_container

    def create_new_value(self,value:int | str)->QLabel:
        if type(value) == int:
            return QLabel(str(value))
        elif type(value) == str:
            return(QLabel(value))
        else:
            return QLabel("Invalid Type")

    def set_value(self,which_axis:Axis,value:int)->None:
        self.values[which_axis.value].setText(str(value))  

    def animate(self):
        pass


class TimeView:
    def __init__(self,window:Window) -> None:
        self.window = window
        window.start_stop_button.setText("Stop")
        window.plt_timer.stop()
        self.active_scopes = []
        window.plot_container.clear()
        ts_x = TimeScope(7, Axis.x, window.data_processor, "sample", "B", "X Axis")
        ts_y = TimeScope(7, Axis.y, window.data_processor, "sample", "B", "Y Axis")
        ts_z = TimeScope(7, Axis.z, window.data_processor, "sample", "B", "Z Axis")
        self.active_scopes.append(ts_x)
        self.active_scopes.append(ts_y)
        self.active_scopes.append(ts_z)
        window.plot_container.addItem(ts_x.get_plt_item(), 0, 0)
        window.plot_container.addItem(ts_y.get_plt_item(), 1, 0)
        window.plot_container.addItem(ts_z.get_plt_item(), 2, 0)
        try:
            window.plt_timer.timeout.disconnect()
        except:
            pass
        window.plt_timer.timeout.connect(
            lambda: window.animateTimeScope(self.active_scopes)
        )
        window.plt_timer.start(AppConfig.PLOT_TIMER_SLEEP_MS)

    def set_max(self, which_axis):
        pass


class SpaceView:
    def __init__(self,window) -> None:
        window.start_stop_button.setText("Stop")
        window.plt_timer.stop()
        window.active_scopes = []
        window.plot_container.clear()
        ss_x = SpaceScope(Axis.x, "x", "B", "X Axis", window.data_processor)
        ss_y = SpaceScope(Axis.y, "y", "B", "Y Axis", window.data_processor)
        ss_z = SpaceScope(Axis.z, "z", "B", "Z Axis", window.data_processor)
        window.active_scopes.append(ss_x)
        window.active_scopes.append(ss_y)
        window.active_scopes.append(ss_z)
        window.plot_container.addItem(ss_x.get_plt_item(), 0, 0)
        window.plot_container.addItem(ss_y.get_plt_item(), 1, 0)
        window.plot_container.addItem(ss_z.get_plt_item(), 2, 0)
        try:
            window.plt_timer.timeout.disconnect()
        except:
            pass
        window.plt_timer.timeout.connect(
            lambda: window.animateSpaceScope(window.active_scopes)
        )
        window.plt_timer.start(AppConfig.PLOT_TIMER_SLEEP_MS)