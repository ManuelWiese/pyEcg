import numpy as np

from DataPoint import DataPoint


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
