import serial
import sys
import time
import datetime
import numpy as np
from collections import namedtuple
import peakutils
import json
import matplotlib.pyplot as plt


DataPoint = namedtuple("DataPoint", ["time", "value"])


class RawData:

    BAUD_RATE = 9600
    PACKAGE_SIZE = 5
    SPLIT_STRING = "\r\n".encode()

    def __init__(self, serial_name):
        try:
            self.serial_device = serial.Serial(serial_name, RawData.BAUD_RATE, timeout=0.5)
        except serial.SerialException as exception:
            print(exception)
            raise(exception)

        self.buffer = b""
        self.data = []

    def read(self):
        self.buffer += self.serial_device.read(RawData.PACKAGE_SIZE)

    def parse(self):
        split_position = self.buffer.find(RawData.SPLIT_STRING)

        if split_position != -1:
            data_value = self.buffer[:split_position].decode('utf-8')
            data_time = time.time()

            try:
                data_value = int(data_value)
                self.data.append(DataPoint(time=data_time, value=data_value))
            except ValueError:
                pass

            self.buffer = self.buffer[split_position + len(RawData.SPLIT_STRING):]

    def update(self):
        self.read()
        self.parse()


class RPeaks:
    TIME_WINDOW = 5

    def __init__(self, data_source):
        self.data = []
        self.data_source = data_source

    def update(self):
        if (len(self.data_source.data) and self.data_source.data[-1].time - self.data_source.data[0].time) < RPeaks.TIME_WINDOW:
            return

        if len(self.data):
            window_start_time = self.data[-1].time - RPeaks.TIME_WINDOW
        else:
            window_start_time = self.data_source.data[-1].time - RPeaks.TIME_WINDOW

        filtered_data = []

        for data_point in reversed(self.data_source.data):
            if data_point.time < window_start_time:
                break
            filtered_data.append(data_point)

        filtered_data = list(reversed(filtered_data))

        new_data = RPeaks.find_peaks(filtered_data)

        try:
            max_r_time = max([data.time for data in self.data])
        except ValueError:
            max_r_time = 0

        new_data = [data for data in new_data if data.time > max_r_time]

        self.data += new_data

    @staticmethod
    def find_peaks(data_points):
        filtered_values = [data_point.value for data_point in data_points]
        x_peaks = peakutils.indexes(np.array(filtered_values), thres=0.8, min_dist=30)
        return [data_points[index] for index in x_peaks]


class HeartRate:
    def __init__(self, data_source, number_of_peaks=10):
        self.data = []
        self.data_source = data_source
        self.number_of_peaks = number_of_peaks

    @staticmethod
    def calculate_heart_rate(data):
        time_distance = data[-1].time - data[0].time
        return 60 * (len(data) - 1) / time_distance

    def update(self):
        if len(self.data_source.data) < self.number_of_peaks:
            return

        if len(self.data) and self.data_source.data[-1].time == self.data[-1].time:
            return

        self.data.append(
            DataPoint(time=self.data_source.data[-1].time,
                      value=HeartRate.calculate_heart_rate(self.data_source.data[-self.number_of_peaks:])
            )
        )


class ECG:
    def __init__(self, serial_name):
        self.start_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        self.raw_data = RawData(serial_name)
        self.r_peaks = RPeaks(self.raw_data)
        self.heart_rate = HeartRate(self.r_peaks)

    def update(self):
        self.raw_data.update()
        self.r_peaks.update()
        self.heart_rate.update()

    def save(self):
        print("Saving data to {}.json ...".format(self.start_time))

        model = {
            'raw_data': self.raw_data.data,
            'r_peaks': self.r_peaks.data,
            'heart_rate': self.heart_rate.data
        }

        with open('{}.json'.format(self.start_time), 'w') as outfile:
            json.dump(model, outfile)

    def plot(self):
        X = [data_point.time for data_point in self.raw_data.data]
        Y = [data_point.value for data_point in self.raw_data.data]

        plt.plot(X, Y)

        X = [data_point.time for data_point in self.r_peaks.data]
        Y = [data_point.value for data_point in self.r_peaks.data]

        plt.plot(X, Y, "ro")


        X = [data_point.time for data_point in self.heart_rate.data]
        Y = [data_point.value for data_point in self.heart_rate.data]

        plt.figure()

        plt.plot(X, Y)

        plt.show()


if __name__ == "__main__":

    if sys.platform == "darwin":
        serial_name = "/dev/tty.usbmodemFD1241"
    else:
        serial_name = "/dev/ttyACM1"

    ecg = ECG(serial_name)

    try:
        while True:
            ecg.update()
    except KeyboardInterrupt as e:
        pass
    finally:
        ecg.save()
        ecg.plot()
