import serial

from DataPoint import DataPoint


class RawData:

    BAUD_RATE = 115200
    PACKAGE_SIZE = 5
    SPLIT_STRING = "\r\n".encode()
    WARMUP_STEPS = 100

    MIN_VALUE = 0
    MAX_VALUE = 1000

    def __init__(self, serial_name):
        try:
            self.serial_device = serial.Serial(serial_name, RawData.BAUD_RATE, timeout=0.5)
        except serial.SerialException as exception:
            print(exception)
            raise(exception)

        self.buffer = b""
        self.data = []
        self.start_time = None
        self.warmup_counter = 0

    def read(self):
        self.buffer += self.serial_device.read(RawData.PACKAGE_SIZE)

    def add_data(self, time, value):
        if self.warmup_counter < RawData.WARMUP_STEPS:
            self.warmup_counter += 1
            return

        time = int(time) / 1000000
        value = int(value)

        if self.start_time is None:
            self.start_time = time

        time = time - self.start_time

        if value >= RawData.MIN_VALUE and value <= RawData.MAX_VALUE:
            self.data.append(DataPoint(time=time, value=value))


    def parse(self):
        split_position = self.buffer.find(RawData.SPLIT_STRING)

        if split_position != -1:
            try:
                data_value = self.buffer[:split_position].decode('utf-8')
                time, value = data_value.split("||")
                self.add_data(time, value)
            except ValueError as e:
                print("Warning: ", e)
            except UnicodeDecodeError as e:
                print("Warning: ", e)

            self.buffer = self.buffer[split_position + len(RawData.SPLIT_STRING):]

    def update(self):
        self.read()
        self.parse()
