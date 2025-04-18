from communication import DataDecode
from app_config import AppConfig

import threading
import time


class SerialThread:
    def __init__(self, decode: DataDecode, app_exit: threading.Event) -> None:
        self._decode = decode
        self._samples_buf: list[list[tuple[int, int, int]]] = []
        self._samples_buf_lock = threading.Lock()
        self._app_exit = app_exit
        self.running=True

    def run_read_serial(self) -> None:
        """Periodicaly reads whole serial buffer and appends it to samples buffer"""
        while not self._app_exit.is_set():
            data = self._decode.get_all_sensor_data()
            #self._decode.print_decoded_data(data)
            with self._samples_buf_lock:
                self._samples_buf.append(data)

            time.sleep(AppConfig.SERIAL_SLEEP)

    def run_read_serial_handshake(self):
        while not self._app_exit.is_set():
            if self.running:
                self._decode.request_new_data()
                time.sleep(AppConfig.TIME_FOR_MSG_TRANSFER)
                data = self._decode.get_all_sensor_data()
                #self._decode.print_decoded_data(data)
                with self._samples_buf_lock:
                    self._samples_buf.append(data)
            else:
                time.sleep(0.1)
                        

    def get_latest_sample(self) -> list[tuple[int, int, int]]:
        """Aquires sa from sample buffer and makes sample buffer empty"""
        returnList = []
        with self._samples_buf_lock:
            returnList = self._samples_buf
            print("-------------------------------------------------------------------")
            print(returnList)
            print("-------------------------------------------------------------------")
            self._samples_buf = []
        try:
            return returnList[-1]  
        except:
            return []
        
    def get_all_samples(self)->list[list[tuple[int,int,int]]]:
        returnList = []
        with self._samples_buf_lock:
            returnList = self._samples_buf 
            self._samples_buf = []
        return returnList
