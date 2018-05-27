from DataPoint import DataPoint
import numpy as np

class StandardDeviation:

    def __init__(self, data_source, window_size=None):
        self.data_source = data_source
        self.data = []
        self.window_size = window_size

    def get_start_index(self):
        if len(self.data) == 0:
            return 0

        for index, value in reversed(list(enumerate(self.data_source.data))):
            if value.time <= self.data[-1].time:
                return index + 1

    def update(self):
        start_index = self.get_start_index()

        if start_index == len(self.data_source.data):
            return

        for i in range(start_index, len(self.data_source.data)):
            if self.window_size is None:
                window = self.data_source.data[:i+1]
            elif i >= self.window_size-1:
                window = self.data_source.data[i-self.window_size+1:i+1]
            else:
                continue

            self.data.append(
                DataPoint(
                    time=window[-1].time,
                    value=np.std([data_point.value for data_point in window])
                )
            )
