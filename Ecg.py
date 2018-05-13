import sys
import time
import datetime

import json
import matplotlib.pyplot as plt
from math import exp

from DataPoint import DataPoint
from RawData import RawData
from Equalizer import Equalizer
from Derivative import Derivative
from Squaring import Squaring
from Integration import Integration
from RPeaks import RPeaks
from HeartRate import HeartRate


class ECG:
    def __init__(self, serial_name):
        self.start_time = time.time()
        self.start_timestamp = datetime.datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')

        self.raw_data = RawData(serial_name)
        self.band_pass = Equalizer(self.raw_data, transfer_function=lambda frequency : 1 if abs(frequency) > 5 and abs(frequency) < 15 else 0 )
        self.derivative = Derivative(self.band_pass)
        self.squaring = Squaring(self.derivative)
        self.integration = Integration(self.squaring)
        self.r_peaks = RPeaks(self.integration, self.band_pass)
        self.heart_rate = HeartRate(self.r_peaks)

    def update(self):
        self.raw_data.update()
        self.band_pass.update()
        self.derivative.update()
        self.squaring.update()
        self.integration.update()
        self.r_peaks.update()
        self.heart_rate.update()

    def save(self):
        print("Saving data to {}.json ...".format(self.start_timestamp))

        model = {
            'start_time': self.start_time,
            'raw_data': self.raw_data.data,
            'r_peaks': self.r_peaks.data,
            'heart_rate': self.heart_rate.data
        }

        with open('{}.json'.format(self.start_timestamp), 'w') as outfile:
            json.dump(model, outfile)

    def plot(self):
        X = [data_point.time - self.start_time for data_point in self.raw_data.data]
        Y = [data_point.value for data_point in self.raw_data.data]

        plt.plot(X, Y)

        X = [data_point.time - self.start_time for data_point in self.r_peaks.data]
        max_y = max(Y)
        min_y = min(Y)

        for r_time in X:
            plt.plot([r_time, r_time], [min_y, max_y], "b")


        plt.figure()

        X = [data_point.time - self.start_time for data_point in self.band_pass.data]
        Y = [data_point.value for data_point in self.band_pass.data]

        plt.plot(X, Y)

        X = [data_point.time - self.start_time for data_point in self.r_peaks.data]
        max_y = max(Y)
        min_y = min(Y)

        for r_time in X:
            plt.plot([r_time, r_time], [min_y, max_y], "b")

        plt.figure()

        X = [data_point.time - self.start_time for data_point in self.heart_rate.data]
        Y = [data_point.value for data_point in self.heart_rate.data]

        plt.plot(X, Y)

        plt.figure()

        X = [data_point.time - self.start_time for data_point in self.integration.data]
        Y = [data_point.value for data_point in self.integration.data]

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
