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


    def get_next_window(self):
        if len(self.data_source.data) < type(self).WINDOW_SIZE:
            return None

        if len(self.data) == 0:
            return self.data_source.data[:type(self).WINDOW_SIZE]

        last_time = self.data[-1].time

        for i in range(len(self.data_source.data) - 1, -1, -1):
            if self.data_source.data[i].time == last_time:
                sliced = self.data_source.data[i-1:i+4]
                if len(sliced) == type(self).WINDOW_SIZE:
                    return sliced
                return None

    def update(self):
        while True:
            window = self.get_next_window()

            if window is None:
                return

            self.data.append(type(self).transformation(window))
