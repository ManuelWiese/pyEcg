import numpy as np
from scipy.signal import butter, lfilter

from DataPoint import DataPoint


class Butterworth:
    WINDOW_SIZE = 512
    START_INDEX = 128
    STOP_INDEX = 3*128

    @staticmethod
    def calculate_frequency(data):
        return len(data) / (data[-1].time - data[0].time)

    @staticmethod
    def butter_lowpass(highcut, fs, order=2):
        nyq = 0.5 * fs
        high = highcut / nyq
        b, a = butter(order, high, btype='low')
        return b, a

    @staticmethod
    def butter_highpass(lowcut, fs, order=1):
        nyq = 0.5 * fs
        low = lowcut / nyq
        b, a = butter(order, low, btype='high')
        return b, a

    @staticmethod
    def butter_bandpass_filter(data, fs, lowcut, highcut, order_lowcut, order_highcut):
        b1, a1 = Butterworth.butter_lowpass(highcut, fs, order=order_highcut)
        y1 = lfilter(b1, a1, data)

        b2, a2 = Butterworth.butter_highpass(lowcut, fs, order=order_lowcut)
        y2 = lfilter(b2, a2, y1)
        return y2

    def __init__(self, data_source, lowcut, highcut, order_lowcut=2, order_highcut=1):
        self.data = []
        self.data_source = data_source
        self.lowcut = lowcut
        self.highcut = highcut
        self.order_lowcut = order_lowcut
        self.order_highcut = order_highcut

    def update(self):
        if len(self.data_source.data) < type(self).WINDOW_SIZE:
            return

        if len(self.data) and self.data_source.data[-type(self).WINDOW_SIZE + type(self).START_INDEX].time <= self.data[-1].time:
            return

        data_samples, time_samples = zip(*[(dp.value, dp.time) for dp in self.data_source.data[-type(self).WINDOW_SIZE:]])

        frequency = type(self).calculate_frequency(self.data_source.data[-type(self).WINDOW_SIZE:])
        filtered_data = type(self).butter_bandpass_filter(
            data_samples,
            frequency,
            self.lowcut,
            self.highcut,
            self.order_lowcut,
            self.order_highcut
        )

        assert len(time_samples) == len(filtered_data)

        data_points = [DataPoint(time=time_samples[i], value=filtered_data[i])
                        for i in range(type(self).START_INDEX, type(self).STOP_INDEX)]

        self.data += data_points
