from serial import Serial


class CommunicationWrapper:
    def __init__(self, serial: Serial) -> None:
        self.serial = serial

    def get_data(self) -> bytes:
        res = self.serial.read_all()
        if res is None:
            return bytes()
        return res


class DataDecode:
    def __init__(self, communication_wrapper: CommunicationWrapper) -> None:
        self.raw_buffer = bytearray()
        self.time_samples = []
        # self.decoded_buffer = list[tuple[int,int,int]]
        self.communication = communication_wrapper
        self.data_miss = 0
        self.data_hit = 1

    def get_all_sensor_data(self) -> list[tuple[int, int, int]]:
        # lets assume that we are fast enough to alway read 8x32bit of data and we are never late
        raw_data = self.communication.get_data()
        if len(raw_data) == 0:
            return []
        if len(raw_data) != 96:
            self.data_miss += 1
            # print(f"Oh no, we shat the bucket. We arwe so wewe sowy. Shat bucket rate: {(self.data_miss/self.data_hit)*100}%")
            return []
        self.data_hit += 1
        return self._decode_fixed(raw_data)

    def _decode_fixed(self, raw_data: bytes) -> list[tuple[int, int, int]]:
        result = []
        temp_tuple = []
        last = 0
        for i in range(4, len(raw_data) + 1, 4):
            temp_tuple.append(
                int.from_bytes(raw_data[last:i], byteorder="little", signed=True)/1000000            # <----conversion to mT here!
            )
            if i % 3 == 0:
                result.append(tuple(temp_tuple))
                temp_tuple = []
            last = i
        return result

    def print_decoded_data(self, data: list[tuple[int, int, int]]):
        if len(data) != 0:
            print("--------------------------------------------------")
            for i, (x, y, z) in enumerate(data):
                print(f"sensor number:{i} -> x:{x}, y:{y}, z:{z}")
            print("--------------------------------------------------")
