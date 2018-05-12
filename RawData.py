import serial
import time

from DataPoint import DataPoint


class RawData:

    BAUD_RATE = 38400
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
        self.warmup_counter = 0

    def read(self):
        self.buffer += self.serial_device.read(RawData.PACKAGE_SIZE)

    def add_data(self, data_value):
        if self.warmup_counter < RawData.WARMUP_STEPS:
            self.warmup_counter += 1
            return

        data_value = int(data_value)
        if data_value >= RawData.MIN_VALUE and data_value <= RawData.MAX_VALUE:
            self.data.append(DataPoint(time=time.time(), value=data_value))

    def parse(self):
        split_position = self.buffer.find(RawData.SPLIT_STRING)

        if split_position != -1:
            try:
                data_value = self.buffer[:split_position].decode('utf-8')
                self.add_data(data_value)
            except ValueError as e:
                print("Warning: ", e)
            except UnicodeDecodeError as e:
                print("Warning: ", e)

            self.buffer = self.buffer[split_position + len(RawData.SPLIT_STRING):]

    def update(self):
        self.read()
        self.parse()
