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


    def update(self):
        if len(self.data_source.data) < self.box_size:
            return

        filtered_data = self.data_source.data[-self.box_size:]

        self.data.append(type(self).transformation(filtered_data))
