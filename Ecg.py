import sys
import time
import datetime

import json
import matplotlib.pyplot as plt
from math import exp

from DataPoint import DataPoint
from RawData import RawData
from Butterworth import Butterworth
from Equalizer import Equalizer
from Derivative import Derivative
from Squaring import Squaring
from Integration import Integration
from RPeaks import RPeaks
from HeartRate import HeartRate
from TimeIntervals import TimeIntervals
from StandardDeviation import StandardDeviation
from RMSSD import RMSSD
from PRR50 import PRR50

import numpy as np

class ECG:
    def __init__(self, serial_name):
        self.start_time = time.time()
        self.start_timestamp = datetime.datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')

        self.raw_data = RawData(serial_name)
        # self.band_pass = Equalizer(self.raw_data, transfer_function=lambda frequency : 1 if abs(frequency) > 5 and abs(frequency) < 15 else 0 )
        self.band_pass = Butterworth(self.raw_data, 5, 15)
        self.derivative = Derivative(self.band_pass)
        self.squaring = Squaring(self.derivative)
        self.integration = Integration(self.squaring)
        self.r_peaks = RPeaks(self.integration, self.band_pass)
        self.heart_rate = HeartRate(self.r_peaks)
        self.rr_intervals = TimeIntervals(self.r_peaks)
        self.sdrr = StandardDeviation(self.rr_intervals)
        self.rmssd = RMSSD(self.rr_intervals)
        self.prr50 = PRR50(self.rr_intervals)

    def update(self):
        self.raw_data.update()
        self.band_pass.update()
        self.derivative.update()
        self.squaring.update()
        self.integration.update()
        self.r_peaks.update()
        self.heart_rate.update()
        self.rr_intervals.update()
        self.sdrr.update()
        self.rmssd.update()
        self.prr50.update()

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
        X = [data_point.time for data_point in self.raw_data.data]
        Y = [data_point.value for data_point in self.raw_data.data]

        plt.plot(X, Y)

        X = [data_point.time for data_point in self.r_peaks.data]
        max_y = max(Y)
        min_y = min(Y)

        for r_time in X:
            plt.plot([r_time, r_time], [min_y, max_y], "b")


        plt.figure()

        X = [data_point.time for data_point in self.band_pass.data]
        Y = [data_point.value for data_point in self.band_pass.data]

        plt.plot(X, Y)

        X = [data_point.time for data_point in self.r_peaks.data]
        max_y = max(Y)
        min_y = min(Y)

        for r_time in X:
            plt.plot([r_time, r_time], [min_y, max_y], "b")

        # plt.figure()
        #
        # X = [data_point.time for data_point in self.integration.data]
        # Y = [data_point.value for data_point in self.integration.data]
        #
        # plt.plot(X, Y)

        plt.figure()

        X = [data_point.time for data_point in self.heart_rate.data]
        Y = [data_point.value for data_point in self.heart_rate.data]

        plt.plot(X, Y)

        plt.figure()

        Y = [dp.value for dp in self.rr_intervals.data]

        plt.bar(range(len(Y)), Y)

        plt.figure()

        X_sdrr = [data_point.time for data_point in self.sdrr.data]
        Y_sdrr = [data_point.value for data_point in self.sdrr.data]
        X_rmssd = [data_point.time for data_point in self.rmssd.data]
        Y_rmssd = [data_point.value for data_point in self.rmssd.data]

        plt.plot(X_sdrr, Y_sdrr, label="sdrr")
        plt.plot(X_rmssd, Y_rmssd, label="rmssd")
        plt.legend(loc='upper left')

        plt.figure()

        X = [data_point.time for data_point in self.prr50.data]
        Y = [data_point.value for data_point in self.prr50.data]

        plt.plot(X, Y)

        plt.figure()

        time_intervals = TimeIntervals(self.raw_data)
        time_intervals.update()

        plt.hist([dp.value for dp in time_intervals.data], bins=np.linspace(0.0049,0.0051,100))

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
