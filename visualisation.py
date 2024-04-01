from PyQt5.QtCore import Qt
from communication import DataDecode
import pyqtgraph as pg
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QWidget




class QtGraph:
    def __init__(self,x_axis:np.ndarray,y_axis:np.ndarray,n_points:int,) -> None:
        self.plt_widget = pg.PlotWidget()
        self.x_axis=x_axis
        self.y_axis=y_axis
        self.n_point=n_points
        self.plt_widget.plot()

class Window(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
    
        # setting title
        self.setWindowTitle("PyQtGraph")

        # setting geometry
        self.setGeometry(100, 100, 600, 500)

        # showing all the widgets
        self.show()

