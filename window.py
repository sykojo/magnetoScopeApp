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

class Window(QMainWindow):
    def __init__(
        self,
        data_processor: DataProcessor,
    ) -> None:
        super().__init__()
        self.data_processor = data_processor
        self.window_layout = QHBoxLayout()
        self.mainWindow = QWidget()
        self.mainWindow.setLayout(self.window_layout)
        self.active_scopes = []
        self.active_timers = []
        """Window Properties"""
        self.setWindowTitle("MagnetoScope")
        self.setGeometry(200, 100, 800, 600)
        pg.setConfigOptions(antialias=True)

        """Containers"""
        self.menu_widget = MenuWidgetWrapper(self)
        self.plot_container = pg.GraphicsLayoutWidget()


        """Buttons"""
        but1 = QPushButton(text="Time Measurment")
        but2 = QPushButton(text="Space Measurment")
        self.start_stop_button = QPushButton(text="Start")
        self.start_stop_button.setIcon(QIcon("icons/start_button_icon.png"))
        
        self.time_view = TimeView(self)
        but1.clicked.connect(lambda:self.time_view.create_scopes())
        but2.clicked.connect(lambda:SpaceView(self))

        """Menu"""
        self.menu_widget.layout.addWidget(but1)
        self.menu_widget.layout.addWidget(but2)
        self.menu_widget.layout.addWidget(self.start_stop_button)
        self.menu_widget.layout.addWidget(self.time_view.info_labels.labels_container)
        
        """Window Layout"""
        self.window_layout.addWidget(self.menu_widget.get_menu_widget())
        self.window_layout.addWidget(self.plot_container)

        self.setCentralWidget(self.mainWindow)

    def app_exit(self, exit: Event):
        exit.set()

    """ def switch_view(self,view:TimeView|SpaceView):
        pass """

        
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
        self.data_processor.load_new_sample()
            

class MenuWidgetWrapper:
    def __init__(self, data_processor) -> None:
        self.data_processor = data_processor
        self.menu = QWidget()
        self.layout = QVBoxLayout()
        self.menu.setLayout(self.layout)

    def get_menu_widget(self)->QWidget:
        return self.menu
    
class Timer:
    def __init__(self,window:Window) -> None:
        self.window = window
        self.timer = QTimer()
        self.connect_start_stop()
        
    def toggle_timer(self):
        if self.timer.isActive():
            self.timer.stop()
            self.window.start_stop_button.setText('Start')  
        else:
            self.timer.start(AppConfig.PLOT_TIMER_SLEEP_MS)  
            self.window.start_stop_button.setText('Stop')

    def connect_start_stop(self)->None:
        try:
            self.window.start_stop_button.clicked.disconnect()
        except:
            pass
        self.window.start_stop_button.clicked.connect(self.toggle_timer)

class TimeView(Timer):
    def __init__(self,window:Window) -> None:
        Timer.__init__(self,window)
        self.window = window
        self.current_sensor:int = 7
        window.start_stop_button.setText("Stop")
        self.active_scopes = []
        self.info_labels = InfoLabels(self,"MAX")
        #self.create_scopes()

    def create_scopes(self):
        self.timer.stop()
        self.window.plot_container.clear()
        ts_x = TimeScope(self.current_sensor, Axis.x, self.window.data_processor, "sample", "B", "X Axis")
        ts_y = TimeScope(self.current_sensor, Axis.y, self.window.data_processor, "sample", "B", "Y Axis")
        ts_z = TimeScope(self.current_sensor, Axis.z, self.window.data_processor, "sample", "B", "Z Axis")
        self.active_scopes.append(ts_x)
        self.active_scopes.append(ts_y)
        self.active_scopes.append(ts_z)
        self.window.plot_container.addItem(ts_x.get_plt_item(), 0, 0)
        self.window.plot_container.addItem(ts_y.get_plt_item(), 1, 0)
        self.window.plot_container.addItem(ts_z.get_plt_item(), 2, 0)
        try:
            self.timer.timeout.disconnect()
        except:
            pass
        self.timer.timeout.connect(
            lambda: self.animate(self.active_scopes)
        )
        self.timer.start(AppConfig.PLOT_TIMER_SLEEP_MS)

    def animate(self, scopes: list[TimeScope])-> None:
        for axis in Axis:
            max_value = self.window.data_processor.get_max(self.current_sensor,axis)
            self.info_labels.set_value(axis,max_value)
            
        for scope in scopes:
            if len(scope.frame) == self.window.data_processor.n_samples:
                scope.plt_item.clear()
                y = []
                x = []
                n_samples = self.window.data_processor.n_samples
                y = scope.convert2Np(scope.frame)
                y = y/1000000.0
                x = np.linspace(scope.t, scope.t + n_samples, n_samples)
                scope.plt_item.setXRange(scope.t, scope.t + n_samples)
                scope.plt_item.plot(x, y,pen=(0,250,154))
                scope.t += n_samples
                scope.frame.pop(0)
            scope.add_data_to_frame()
        self.window.data_processor.load_new_sample()

class SpaceView:
    def __init__(self,window) -> None:
        self.window = window
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


class InfoLabels:
    def __init__(self,view:TimeView|SpaceView,which_info:str) -> None:
        self.window = view.window
        self.labels_container = QWidget()
        self.labels_container_layout = QVBoxLayout()
        self.labels_container_layout.addWidget(QLabel(which_info))
        self.labels_container.setLayout(self.labels_container_layout)
        self.axes_labels:list[QLabel] = []
        self.values_labels:list[QLabel] = []
        
        for axis in Axis:
            new_axis = self.create_axis(axis)
            new_value = self.create_new_value("-")
            self.axes_labels.append(new_axis)
            self.values_labels.append(new_value)
            container = self.create_label_container(new_axis,new_value)
            self.labels_container_layout.addWidget(container)
        
    def create_axis(self,which_axis:Axis)->QLabel:
        return QLabel(text=f"{which_axis.as_string()}: ")

    def create_label_container(self,axis:QLabel,value:QLabel)->QWidget:
        label_container = QWidget()
        label_container_layout = QHBoxLayout()
        label_container.setLayout(label_container_layout)
        
        label_container_layout.addWidget(axis)
        label_container_layout.addWidget(value)
        return label_container

    def create_new_value(self,value:int | str)->QLabel:
        if type(value) == int:
            return QLabel(text=str(value))
        elif type(value) == str:
            return(QLabel(text=value))
        else:
            return QLabel("Invalid Type")

    def set_value(self,which_axis:Axis,value:int)->None:
        self.values_labels[which_axis.value].setText(f"{value} nT")  



