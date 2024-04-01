from serial_thread import SerialThread
from communication import DataDecode, CommunicationWrapper, Serial

import pyqtgraph as pg

from visualisation import Window, SensorData
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

import sys
import threading


def data_count(serial_thread:SerialThread):
    data = serial_thread.get_samples()
    return len(data)//8
    

def main():
    app = QApplication(sys.argv)
    window = Window()
    lock = threading.Lock()
    app_exit = threading.Event()
    app.aboutToQuit.connect(lambda: window.app_exit(app_exit))

    decode = DataDecode(CommunicationWrapper(Serial("COM9", 115200)))
    serial_thread = SerialThread(decode, app_exit)

    # sensor_data = SensorData()
    # timer = QTimer()
    # timer.timeout.connect(window.p1.animate)
    # timer.start(10)
    # window.p1.setTimeSamples()

    serialThread = threading.Thread(target=lambda: serial_thread.run_read_serial())
    serialThread.start()

    count = 0
    while True:
        count += data_count(serial_thread)
        print(count)
        time.sleep()

    # sys.exit(app.exec())


if __name__ == "__main__":
    main()
    # app.exec()
