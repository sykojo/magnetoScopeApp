from serial_thread import SerialThread
from data_processing import DataProcessor
from communication import DataDecode, CommunicationWrapper, Serial
from window import Window
from app_config import AppConfig
from style import app_style

import pyqtgraph as pg

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

import sys
import threading
import time


def main():
    app_exit = threading.Event()
    decode = DataDecode(CommunicationWrapper(Serial("COM7", 921600)))
    serial_thread = SerialThread(decode, app_exit)
    data_processor = DataProcessor(serial_thread, AppConfig.N_SAMPLES,AppConfig.N_SENSORS,app_exit)

    app = QApplication(sys.argv)
    app.setStyleSheet(app_style)
    window = Window(data_processor,serial_thread)
    app.aboutToQuit.connect(lambda: window.app_exit(app_exit))
    # timer = QTimer()
    # timer.timeout.connect(window.p1.animate)
    # timer.start(AppConfig.PLOT_TIMER_SLEEP_MS)

    serialThread = threading.Thread(target=lambda: serial_thread.run_read_serial_handshake())
    dataProcessThread = threading.Thread(target=lambda: data_processor.run_data_processing())
    serialThread.start()
    dataProcessThread.start()
    window.show()


    # sys.exit(app.exec())
    app.exec()


if __name__ == "__main__":
    print("hello")
    main()
    # app.exec()
