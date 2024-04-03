from communication import DataDecode
from app_config import AppConfig

import threading
import time


class SerialThread:
    def __init__(self, decode: DataDecode, app_exit: threading.Event) -> None:
        self._decode = decode
        self._samples_buf:list[list[tuple[int,int,int]]] = []
        self._samples_buf_lock = threading.Lock()
        self._app_exit = app_exit
        pass

    def run_read_serial(self) -> None:
        """Periodicaly reads whole serial buffer and appends it to samples buffer"""
        while not self._app_exit.is_set():
            data = self._decode.get_all_sensor_data()
            #self._decode.print_decoded_data(data)
            with self._samples_buf_lock:
                self._samples_buf.append(data)

            time.sleep(AppConfig.SERIAL_SLEEP)

    def get_oldest_sample(self) -> list[tuple[int, int, int]]:
        '''Aquires sa from sample buffer and makes sample buffer empty'''
        returnList = []
        with self._samples_buf_lock:
            returnList = self._samples_buf
            self._samples_buf = []
        try:
            return returnList[0] #Returns oldest sample
        except:
            return []