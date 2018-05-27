from DataPoint import DataPoint


class Squaring:
    def __init__(self, data_source):
        self.data = []
        self.data_source = data_source

    def update(self):
        if len(self.data_source.data) == 0:
            return

        filtered_data = self.data_source.data[len(self.data):]

        self.data.extend([DataPoint(time=dataPoint.time, value=dataPoint.value**2) for dataPoint in filtered_data])
