from DataPoint import DataPoint


class Squaring:
    WINDOW_SIZE = 1

    def __init__(self, data_source):
        self.data = []
        self.data_source = data_source

    @classmethod
    def transformation(cls, signal):
        return DataPoint(time=signal[0].time, value=signal[0].value**2)


    def update(self):
        if len(self.data_source.data) < type(self).WINDOW_SIZE:
            return

        filtered_data = self.data_source.data[-type(self).WINDOW_SIZE:]

        self.data.append(type(self).transformation(filtered_data))
