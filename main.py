from serial_thread import SerialThread
from data_processing import DataProcessor,Axis,SenNum
from communication import DataDecode, CommunicationWrapper, Serial
from visualisation import Window
from app_config import AppConfig

import pyqtgraph as pg

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

import sys
import threading
import time

    
def main():

    app_exit = threading.Event()
    decode = DataDecode(CommunicationWrapper(Serial("COM9", 921600)))
    serial_thread = SerialThread(decode, app_exit)
    data_processor = DataProcessor(serial_thread,AppConfig.N_SAMPLES)

    app = QApplication(sys.argv)
    window = Window(data_processor)
    app.aboutToQuit.connect(lambda: window.app_exit(app_exit))
    timer = QTimer()
    timer.timeout.connect(window.p1.animate)
    timer.start(AppConfig.TIMER_SLEEP_MS)

    serialThread = threading.Thread(target=lambda: serial_thread.run_read_serial())
    serialThread.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
    # app.exec()
