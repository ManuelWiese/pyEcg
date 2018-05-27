from DataPoint import DataPoint


class Integration:

    def __init__(self, data_source, box_size=30):
        self.data = []
        self.data_source = data_source
        self.box_size = box_size

    @classmethod
    def transformation(cls, signal):
        result = sum([data.value for data in signal]) / len(signal)
        return DataPoint(time=signal[-1].time, value=result)


    def get_next_window(self):
        if len(self.data_source.data) < self.box_size:
            return None

        if len(self.data) == 0:
            return self.data_source.data[:self.box_size]

        last_time = self.data[-1].time

        for i in range(len(self.data_source.data) - 1, -1, -1):
            if self.data_source.data[i].time == last_time:
                sliced = self.data_source.data[i + 1:i + 1 + self.box_size]
                if len(sliced) == self.box_size:
                    return sliced
                return None

    def update(self):
        while True:
            window = self.get_next_window()

            if window is None:
                return

            self.data.append(type(self).transformation(window))
