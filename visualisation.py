from PyQt5.QtCore import Qt
from communication import DataDecode
import pyqtgraph as pg
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout,QPushButton,QVBoxLayout
from threading import Event

class Axes:
    def __init__(self) -> None:
        x=0
        y=1
        z=2

class SensorData:
    def __init__(self,time_samples:list[list[tuple[int,int,int]]]) -> None:
        self.time_samples = time_samples

    """ def get_sen_axis_data(self,axis:int,sen:int) -> int:
        return self.time_samples[sen][axis] """

class QtGraphWrapper:
    def __init__(self,plt:pg.PlotItem,x_label:str,y_label:str,title:str) -> None:
        self.time_samples=[]
        '''Axes'''
        self.x_axis=pg.AxisItem(orientation="bottom")
        self.x_axis.setLabel(x_label)
        self.y_axis=pg.AxisItem(orientation="left")
        self.y_axis.setLabel(y_label)

        self.n_samples = 50

        """ self.plt = pg.PlotItem(title="tvojeMama",axisItems={"left":self.y_axis,
                                                            "bottom":self.x_axis}) """
        self.plt = plt
        self.plt.setTitle(title)
        self.plt.setAxisItems({"left":self.y_axis,
                                "bottom":self.x_axis})
        
    def setNSamples(self,n_samples:int=50):
        self.n_samples = n_samples
    
    def setTimeSamples(self,data:list[list[tuple[int,int,int]]]):
        self.time_samples=data

    def create_frame(self,sen,axis) -> list:
        #print(f"samples: {self.time_samples}")
        #print(f"frame: {[sublist[sen][axis] for sublist in self.time_samples[:self.n_samples]]}")
        return [sublist[sen][axis] for sublist in self.time_samples[:self.n_samples]]
        
            
    def convert2Np(self,data:list)-> np.ndarray:
        np_array = np.array(data)
        return np_array
    
    def animate(self) ->None:
        frame = self.convert2Np(data=self.create_frame(0,0))
        x_axis = np.linspace(0,self.n_samples,self.n_samples)

        self.plt.plot(x_axis,frame)
        if(len(self.time_samples) > self.n_samples):
            print("here")
            self.deleteNsamples()

    def deleteNsamples(self):
        print("deleted samples")
        del self.time_samples[:self.n_samples]


        
        
        


class Window(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        """Window Properties"""
        self.setWindowTitle("PyQtGraph")
        self.setGeometry(200, 100, 1920, 1080)
        pg.setConfigOptions(antialias=True)

        widget = QWidget()
        menu = QWidget()
    
        """Buttons""" 
        win = pg.GraphicsLayoutWidget()
        but1 = QPushButton(text="joeMama")
        but2 = QPushButton(text="daineMutter")
        
    
        p1 = win.addPlot(row=0, col=0)

        #view = win.addViewBox(row=1, col=0, colspan=2)
        self.p1 = QtGraphWrapper(p1,"x","y","title")

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
    
    def app_exit(self,exit:Event):
        exit.set()


