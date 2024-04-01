from communication import DataDecode
import threading
import time


class SerialThread:
    def __init__(self, decode: DataDecode, app_exit: threading.Event) -> None:
        self._decode = decode
        self._samples_buf = []
        self._samples_buf_lock = threading.Lock()
        self._app_exit = app_exit
        pass

    def run_read_serial(self) -> None:
        while not self._app_exit.is_set():
            data = self._decode.get_all_sensor_data()
            # decode.print_decoded_data(data)
            with self._samples_buf_lock:
                self._samples_buf.append(data)
            
            # data processing?

            time.sleep(0.03)

    def get_samples(self) -> list[list[tuple[int, int, int]]]:
        returnList = []
        with self._samples_buf_lock:
            returnList = self._samples_buf
            self._samples_buf = []
        return returnList