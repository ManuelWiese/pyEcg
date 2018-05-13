from DataPoint import DataPoint


class Derivative:
    WINDOW_SIZE = 5

    def __init__(self, data_source):
        self.data = []
        self.data_source = data_source

    @classmethod
    def transformation(cls, signal):
        sampling_time = (signal[-1].time - signal[0].time) / (cls.WINDOW_SIZE - 1)
        result = (-signal[0].value - 2*signal[1].value + 2*signal[3].value + signal[4].value) / (8 * sampling_time)
        return DataPoint(time=signal[2].time, value=result)


    def update(self):
        if len(self.data_source.data) < type(self).WINDOW_SIZE:
            return

        filtered_data = self.data_source.data[-type(self).WINDOW_SIZE:]

        self.data.append(type(self).transformation(filtered_data))
