import serial
import sys
import time
import datetime
import numpy as np
from collections import namedtuple
import peakutils
import json
import matplotlib.pyplot as plt
from math import exp


DataPoint = namedtuple("DataPoint", ["time", "value"])


class RawData:

    BAUD_RATE = 38400
    PACKAGE_SIZE = 5
    SPLIT_STRING = "\r\n".encode()
    WARMUP_STEPS = 100

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


class Equalizer:
    WINDOW_SIZE = 512

    def __init__(self, data_source, transfer_function):
        self.data = []
        self.data_source = data_source
        self.transfer_function = transfer_function

    @classmethod
    def index_to_freq(cls, index, mean_time):
        index = index % cls.WINDOW_SIZE
        nyquist_freq = 1 / (2*mean_time)

        if index <= cls.WINDOW_SIZE / 2:
            return nyquist_freq * index / (cls.WINDOW_SIZE / 2)
        else:
            return nyquist_freq * ( (index - cls.WINDOW_SIZE / 2) / (cls.WINDOW_SIZE / 2) - 1 )

    def update(self):
        if len(self.data_source.data) < type(self).WINDOW_SIZE:
            return

        filtered_data = self.data_source.data[-type(self).WINDOW_SIZE:]
        index_base = int(len(filtered_data)/2)

        mean_time = (filtered_data[-1].time - filtered_data[0].time)/len(filtered_data)
        frequency_resolution = 1/(mean_time * type(self).WINDOW_SIZE)

        mean_value = np.mean([data.value for data in filtered_data])

        fft = np.fft.fft(np.array([data.value - mean_value for data in filtered_data]))

        fft = np.array([value * self.transfer_function(type(self).index_to_freq(index, mean_time)) for index, value in enumerate(fft)])
        ifft = np.fft.ifft(fft)

        self.data.append(DataPoint(time=filtered_data[index_base].time, value=ifft[index_base].real))


class BandPass(Equalizer):
    @staticmethod
    def transfer_function(frequency):
        return exp( - (abs(frequency)-10)**2 / 12.5 )

class RPeaks:
    TIME_WINDOW = 5

    def __init__(self, data_source):
        self.data = []
        self.data_source = data_source

    def get_time_window(self):
        if len(self.data):
            window_start_time = self.data[-1].time - type(self).TIME_WINDOW
        else:
            window_start_time = self.data_source.data[-1].time - type(self).TIME_WINDOW

        filtered_data = []

        for data_point in reversed(self.data_source.data):
            if data_point.time < window_start_time:
                break
            filtered_data.append(data_point)

        filtered_data = list(reversed(filtered_data))
        return filtered_data

    def update(self):
        if (len(self.data_source.data) and self.data_source.data[-1].time - self.data_source.data[0].time) < type(self).TIME_WINDOW:
            return

        filtered_data = self.get_time_window()

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
        x_peaks = peakutils.indexes(np.array(filtered_values), thres=0.75, min_dist=30)
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
        self.band_pass = Equalizer(self.raw_data, transfer_function=lambda frequency : exp( - (abs(frequency)-10)**2 / 12.5 ))
        self.r_peaks_raw = RPeaks(self.raw_data)
        self.r_peaks = RPeaks(self.band_pass)
        self.heart_rate = HeartRate(self.r_peaks)

    def update(self):
        self.raw_data.update()
        self.band_pass.update()
        self.r_peaks.update()
        self.r_peaks_raw.update()
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

        X = [data_point.time for data_point in self.r_peaks_raw.data]
        Y = [data_point.value for data_point in self.r_peaks_raw.data]

        plt.plot(X, Y, "ro")

        plt.figure()

        X = [data_point.time for data_point in self.r_peaks.data]
        Y = [data_point.value for data_point in self.r_peaks.data]

        plt.plot(X, Y, "ro")

        X = [data_point.time for data_point in self.band_pass.data]
        Y = [data_point.value for data_point in self.band_pass.data]

        plt.plot(X, Y)

        plt.figure()

        X = [data_point.time for data_point in self.heart_rate.data]
        Y = [data_point.value for data_point in self.heart_rate.data]

        plt.plot(X, Y)

        plt.show()


if __name__ == "__main__":

    if sys.platform == "darwin":
        serial_name = "/dev/tty.usbmodemFD1241"
    else:
        serial_name = "/dev/ttyACM0"

    ecg = ECG(serial_name)

    try:
        while True:
            ecg.update()
    except KeyboardInterrupt as e:
        pass
    finally:
        ecg.save()
        ecg.plot()
