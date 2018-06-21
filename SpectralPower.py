from DataPoint import DataPoint
from scipy.interpolate import interp1d
from scipy.signal import periodogram


class SpectralPower:

    def __init__(self, data_source, low_freq, high_freq, window_size=None, fs=1/0.25):
        self.data_source = data_source
        self.data = []

        self.low_freq = low_freq
        self.high_freq = high_freq
        self.window_size = window_size
        self.fs = fs

    def get_start_index(self):
        if len(self.data) == 0:
            return 0

        for index, value in reversed(list(enumerate(self.data_source.data))):
            if value.time <= self.data[-1].time:
                return index + 1

    def interpolate(self, data_points):
        X = [dp.time for dp in data_points]
        Y = [dp.value for dp in data_points]

        interpolated = interp1d(X, Y)

        step = 1 / self.fs
        X2 = [step * i for i in range(int(min(X)/step)+1, int(max(X)/step))]
        return [interpolated(x) for x in X2]

    def power(self, values):
        freqs, density = periodogram(values, self.fs)

        power = 0
        for index, f in enumerate(freqs):
            if f >= self.low_freq and f <= self.high_freq:
                try:
                    power += density[index] * (freqs[index] - freqs[index-1])
                except IndexError:
                    pass
        return power

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
            try:
                self.data.append(
                    DataPoint(
                        time=window[-1].time,
                        value=self.power(self.interpolate(window))
                    )
                )
            except ValueError:
                pass
