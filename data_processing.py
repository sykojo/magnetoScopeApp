from serial_thread import SerialThread


class DataProcessor:
    def __init__(self, serial_thread:SerialThread) -> None:
        self.serial_thread = serial_thread


    def get_one_sensor_data(self, which_sensor:int) -> list[int]:
        samples = self.serial_thread.get_samples()
        # do some processing
        return []
    
    # do data processing here?