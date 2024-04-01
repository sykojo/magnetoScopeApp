from communication import CommunicationWrapper,DataDecode,Serial
import time
import pyqtgraph as pg
from visualisation import Window
from PyQt5.QtWidgets import QApplication
import sys


def read_till_end_of_time(decode:DataDecode):
    while True:
        data = decode.get_all()
        if len(data) != 0:
            print("--------------------------------------------------")
            for i, (x, y, z) in enumerate(data):
                print(f"sensor number:{i} -> x:{x}, y:{y}, z:{z}")
            print("--------------------------------------------------")
        time.sleep(0.03)

def main():
    decode = DataDecode(CommunicationWrapper(Serial("COM9", 115200)))
    read_till_end_of_time(decode)

if __name__ == "__main__":
    """ app = pg.mkQApp("MagnetoScope")
    layout = pg.GraphicsLayout()
    view = layout.addViewBox(row=2, col=0, colspan=2)
    graph_item = pg.GraphItem()
    view.addItem(graph_item) """

    app = QApplication(sys.argv)
    window = Window()

    sys.exit(app.exec())


    
    
    #app.exec()