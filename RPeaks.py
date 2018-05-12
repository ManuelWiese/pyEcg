import peakutils
import numpy as np

from DataPoint import DataPoint


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
        x_peaks = peakutils.indexes(np.array(filtered_values), thres=0.8, min_dist=30)
        return [data_points[index] for index in x_peaks]
