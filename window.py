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
)

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
        but1 = QPushButton(text="joeMama")
        but2 = QPushButton(text="daineMutter")
        but1.clicked.connect(self.display_time_scopes3)
        but2.clicked.connect(self.display_space_scopes)

        """Menu"""
        menu_widget.layout.addWidget(but1)
        menu_widget.layout.addWidget(but2)

        """Window Layout"""
        self.window_layout.addWidget(menu_widget.get_menu_widget())
        self.window_layout.addWidget(self.plot_container)

        self.setCentralWidget(self.mainWindow)

    def app_exit(self, exit: Event):
        exit.set()

    def display_time_scopes3(self):
        self.plt_timer.stop()
        self.active_scopes = []
        self.plot_container.clear()
        ts_x = TimeScope(0, Axis.x, self.data_processor, "t", "B", "X Axis")
        ts_y = TimeScope(0, Axis.y, self.data_processor, "t", "B", "Y Axis")
        ts_z = TimeScope(0, Axis.z, self.data_processor, "t", "B", "Z Axis")
        self.active_scopes.append(ts_x)
        self.active_scopes.append(ts_y)
        self.active_scopes.append(ts_z)
        self.plot_container.addItem(ts_x.get_plt_item(), 0, 0)
        self.plot_container.addItem(ts_y.get_plt_item(), 1, 0)
        self.plot_container.addItem(ts_z.get_plt_item(), 2, 0)
        self.plt_timer.timeout.connect(
            lambda: self.animateTimeScope(self.active_scopes)
        )
        self.plt_timer.start(AppConfig.PLOT_TIMER_SLEEP_MS)

    def display_space_scopes(self):
        self.plt_timer.stop()
        self.active_scopes = []
        self.plot_container.clear()
        ss_x = SpaceScope(Axis.x, "x", "nT", "X Axis", self.data_processor)
        ss_y = SpaceScope(Axis.y, "y", "nT", "Y Axis", self.data_processor)
        ss_z = SpaceScope(Axis.z, "z", "nT", "Z Axis", self.data_processor)
        self.active_scopes.append(ss_x)
        self.active_scopes.append(ss_y)
        self.active_scopes.append(ss_z)
        self.plot_container.addItem(ss_x.get_plt_item(), 0, 0)
        self.plot_container.addItem(ss_y.get_plt_item(), 1, 0)
        self.plot_container.addItem(ss_z.get_plt_item(), 2, 0)

        self.plt_timer.timeout.connect(
            lambda: self.animateSpaceScope(self.active_scopes)
        )
        self.plt_timer.start(AppConfig.PLOT_TIMER_SLEEP_MS)

    def animateTimeScope(self, scopes: list[TimeScope]):
        for scope in scopes:
            if len(scope.frame) == self.data_processor.n_samples:
                scope.plt_item.clear()
                y = []
                n_samples = self.data_processor.n_samples
                y = scope.convert2Np(scope.frame)
                x = np.linspace(scope.t, scope.t + n_samples, n_samples)
                scope.plt_item.setXRange(scope.t, scope.t + n_samples)
                scope.plt_item.plot(x, y)
                scope.t += n_samples
                scope.frame.pop(0)
            scope.add_data_to_frame()
        self.data_processor.set_current_sample()

    def animateSpaceScope(self, scopes: list[SpaceScope]):
        for scope in scopes:
            scope.plt_item.clear()
            x = np.linspace(0, AppConfig.N_SENSORS - 1, AppConfig.N_SENSORS)
            y = scope.convert2Np(scope.frame)
            scope.plt_item.plot(x, y)
            scope.frame = []
            scope.add_data_to_frame()
        self.data_processor.set_current_sample()


class MenuWidgetWrapper:
    def __init__(self, data_processor) -> None:
        self.data_processor = data_processor
        self.menu = QWidget()
        self.layout = QVBoxLayout()
        self.menu.setLayout(self.layout)

    def get_menu_widget(self):
        return self.menu
