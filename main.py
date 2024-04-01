from communication import CommunicationWrapper,DataDecode,Serial
import time
import pyqtgraph as pg
from visualisation import Window, SensorData
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QMutex
import sys
import threading



def read_serial(samples_buf:list,decode:DataDecode,lock:threading.Lock,app_exit:threading.Event):
    max_t_samples=10000
    while not app_exit.is_set():
        print(f"Samples buffer length: {len(samples_buf)}")
        data = decode.get_all()
        #decode.print_decoded_data(data)
        if len(samples_buf)<max_t_samples:
            if(len(data) != 0):
                with lock:
                    samples_buf.append(data)
                    
        else:
            print("Time Samples Buffer is full")

        
        time.sleep(0.03)
            


def main():


    app = QApplication(sys.argv)
    window = Window()
    lock=threading.Lock()
    app_exit = threading.Event()
    app.aboutToQuit.connect(lambda:window.app_exit(app_exit))
    decode = DataDecode(CommunicationWrapper(Serial("COM9", 115200)))
    time_samples:list[tuple[int,int,int]] = []
    sensor_data = SensorData(time_samples)

    window.p1.animate()

    serialThread = threading.Thread(target=lambda:read_serial(time_samples,decode,lock,app_exit))
    serialThread.start()

    #read_till_end_of_time(decode)

    sys.exit(app.exec())

if __name__ == "__main__":

    main()
    


    


    
    
    #app.exec()