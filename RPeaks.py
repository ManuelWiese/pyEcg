from scipy.signal import find_peaks
import numpy as np

from DataPoint import DataPoint


class RPeaks:
    TIME_WINDOW = 5

    def __init__(self, data_source, raw_data):
        self.data = []
        self.data_source = data_source
        self.raw_data = raw_data

    def get_time_window(self):
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

        new_data = self.find_peaks(filtered_data)

        if len(self.data) > 0:
            max_r_time = self.data[-1].time
        else:
            max_r_time = 0

        new_data = [data for data in new_data if data.time > max_r_time]

        self.data += new_data

    def __time_to_index(self, time, data_points):
        for index, data in enumerate(reversed(data_points)):
            if data.time == time:
                return len(data_points) - index

    def find_peaks(self, data_points):
        filtered_values = [data_point.value for data_point in data_points]
        max_height = max(filtered_values)

        x_peaks, _ = find_peaks(filtered_values, distance=40, prominence=0.3*max_height)

        times = [data_points[index].time for index in x_peaks]

        r_data_points = []
        for time in times:
            index = self.__time_to_index(time, self.raw_data.data)
            peak = max(self.raw_data.data[index-30:index+30], key=lambda x: x.value)
            r_data_points.append(peak)

        return r_data_points

        # return [data_points[index] for index in x_peaks]
