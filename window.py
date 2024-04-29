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
from abc import ABC,abstractmethod

class Window(QMainWindow):
    def __init__(
        self,
        data_processor: DataProcessor,
    ) -> None:
        super().__init__()
        self.data_processor = data_processor
        self.window_layout = QHBoxLayout()
        self.mainWindow = QWidget()
        self.plot_view = QWidget()
        self.plot_view_layout = QHBoxLayout()
        self.plot_view.setLayout(self.plot_view_layout)
        self.mainWindow.setLayout(self.window_layout)
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
        self.create_timer_toggle_button()
        

        self.time_view = TimeView(self,AppConfig.ACTIVE_SEN)
        self.space_view = SpaceView(self)
        self.active_view = self.space_view
        
        but1.clicked.connect(lambda:self.switch_view(AppConfig.TIME_VIEW))
        but2.clicked.connect(lambda:self.switch_view(AppConfig.SPACE_VIEW))
        
        """Menu"""
        self.menu_widget.layoutVBox.addWidget(but1)
        self.menu_widget.layoutVBox.addWidget(but2)
        self.menu_widget.layoutVBox.addWidget(self.toggle_button)
        self.menu_widget.layoutVBox.addWidget(self.space_view.info_labels.labels_container)
        self.menu_widget.layoutVBox.addWidget(self.time_view.info_labels.labels_container)
        
        """Window Layout"""
        self.window_layout.addWidget(self.menu_widget.widget)
        self.plot_view_layout.addWidget(self.plot_container)
        self.window_layout.addWidget(self.plot_view)

        self.setCentralWidget(self.mainWindow)

    def app_exit(self, exit: Event):
        exit.set()

    def switch_view(self, view_name: str):

        if not self.active_view.hidden:
            self.active_view.deactivate()
        
        if view_name == AppConfig.SPACE_VIEW:
            self.active_view = self.space_view
        elif view_name == AppConfig.TIME_VIEW:
            self.active_view = self.time_view
        else:
            raise ValueError("Invalid view name")

        if self.active_view.hidden:
            self.active_view.activate()

    def create_timer_toggle_button(self):
        self.toggle_button = QPushButton(text="Start")
        self.toggle_button.setIcon(QIcon("icons/start_button_icon.png"))
        

class MenuWidgetWrapper:
    def __init__(self, data_processor) -> None:
        self.data_processor = data_processor
        self.widget = QWidget()
        self.layoutVBox = QVBoxLayout()
        self.widget.setLayout(self.layoutVBox)

    def get_menu_widget(self)->QWidget:
        return self.widget
    
class Timer:
    def __init__(self,window:Window) -> None:
        self.window = window
        self.timer = QTimer()
        self.timeout = self.timer.timeout
        
    def toggle_timer(self):
        if self.timer.isActive():
            self.timer.stop()
            self.window.toggle_button.setText('Start')  
        else:
            self.timer.start(AppConfig.PLOT_TIMER_SLEEP_MS)  
            self.window.toggle_button.setText('Stop')

    def start(self,period_ms):
        return self.timer.start(period_ms)

    def stop(self):
        return self.timer.stop()
            
class View(ABC):
    def __init__(self, window: Window) -> None:
        super().__init__()
        self.window = window
        self.timer = Timer(window)
        self.info_labels = InfoLabels(self,"MAX")
        self.window.toggle_button.setText("Stop")
        self.active_scopes:list[TimeScope|SpaceScope] = []
        self.hidden = False
        self.connected = False
        self.timer_connected=False
        self.window.plot_container.clear()
        self.hide()

    @abstractmethod
    def animate_max(self):
        pass

    @abstractmethod
    def animate_scopes(self,scopes:list):
        pass

    @abstractmethod
    def create_scope(self,axis:Axis)->TimeScope|SpaceScope:
        pass

    def create_scopes(self)->None: 
        for axis in Axis:
            scope = self.create_scope(axis)
            self.active_scopes.append(scope)  
            plt_item = scope.get_plt_item()
            self.window.plot_container.addItem(plt_item,axis.value,0)

    def destroy_scopes(self):
        if len(self.active_scopes) == AppConfig.N_AXES:
            for scope in self.active_scopes:
                self.window.plot_container.removeItem(scope.plt_item)
            self.active_scopes = []
        
    def animate(self,scopes:list):
        self.animate_max()
        self.animate_scopes(self.active_scopes)

    def connect_animate(self):
        if not self.connected:
            self.timer.timeout.connect(
                lambda: self.animate(self.active_scopes)
            )
        self.connected = True
    
    def disconnect_animate(self):
        if self.connected:
            self.timer.timeout.disconnect()
            self.connected = False

    def show(self)->None:
        self.window.plot_view.show()
        self.create_scopes()
        self.info_labels.labels_container.show()
        self.hidden=False

    def hide(self)->None:
        self.window.plot_view.hide()
        self.destroy_scopes()
        self.info_labels.labels_container.hide()
        self.hidden=True

    def activate(self):
        self.connect_animate()
        self.connect_timer_toggle()
        self.show()
        self.timer.start(AppConfig.PLOT_TIMER_SLEEP_MS)
         
    def deactivate(self):
        self.hide()
        self.timer.stop()
        self.disconnect_animate()
        self.disconnect_timer_toggle()

    def connect_timer_toggle(self):
        if not self.timer_connected:
            self.window.toggle_button.clicked.connect(self.timer.toggle_timer)
            self.timer_connected=True

    def disconnect_timer_toggle(self):
        if not self.timer_connected:
            self.window.toggle_button.clicked.disconnect() 
            self.timer_connected = False
        

class TimeView(View):
    def __init__(self,window,sen_n) -> None:
        self.current_sensor:int = sen_n
        super().__init__(window)
        
    def create_scope(self,axis:Axis)->TimeScope:
        return  TimeScope(self.current_sensor, axis, self.window.data_processor, "sample", "B", f"{axis.as_string()} Axis")
        
    def animate_max(self):
        for axis in Axis:
            max_value = self.window.data_processor.get_max(self.current_sensor,axis)
            self.info_labels.set_value(axis,max_value)
    
    def animate_scopes(self,scopes:list[TimeScope]):
        for scope in scopes:
            if len(scope.frame) == self.window.data_processor.n_samples:
                scope.plt_item.clear()
                y = []
                x = []
                n_samples = self.window.data_processor.n_samples
                y = scope.convert2Np(scope.frame)
                x = np.linspace(scope.t, scope.t + n_samples, n_samples)
                scope.plt_item.setXRange(scope.t, scope.t + n_samples)
                scope.plt_item.plot(x, y,pen=pg.mkPen((61,142,201), width=4)) #3d8ec9
                scope.t += n_samples
                scope.frame.pop(0)
            scope.add_data_to_frame()
        self.window.data_processor.load_new_sample()
        

class SpaceView(View):
    def __init__(self,window) -> None:
        super().__init__(window)

    def create_scope(self, axis: Axis) -> TimeScope | SpaceScope:
        return SpaceScope(axis, axis.as_string(), "B", f"{axis.as_string()} Axis", self.window.data_processor)

    def animate_max(self):
            max_values = self.window.data_processor.get_max_of_all_sen()
            for value,axis in zip(max_values,Axis):
                self.info_labels.set_value(axis,value)

    def animate_scopes(self, scopes: list[SpaceScope]):
        for scope in scopes:
            scope.plt_item.clear()
            x = []
            y = []
            x = np.linspace(0, AppConfig.N_SENSORS - 1, AppConfig.N_SENSORS)
            y = scope.convert2Np(scope.frame)
            scope.plt_item.plot(x, y,pen=pg.mkPen((61,142,201), width=5), symbolBrush=(61,142,201), symbolPen='b',symbol='o') 
            scope.frame = []
            scope.add_data_to_frame()
        self.window.data_processor.load_new_sample()


class InfoLabels:
    def __init__(self,view:View,which_info:str) -> None:
        self.window = view.window
        self.view = view
        self.which_info = which_info
        self.labels_container = QWidget()
        self.labels_container_layout = QVBoxLayout()
        self.labels_container.setLayout(self.labels_container_layout)
        self.axes_labels:list[QLabel] = []
        self.values_labels:list[QLabel] = []

        self.create_labels()
        
    def create_labels(self):
        self.labels_container_layout.addWidget(QLabel(self.which_info))
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
        self.values_labels[which_axis.value].setText(f"{value} mT") 



