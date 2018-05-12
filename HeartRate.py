from DataPoint import DataPoint


class HeartRate:
    def __init__(self, data_source, number_of_peaks=10):
        self.data = []
        self.data_source = data_source
        self.number_of_peaks = number_of_peaks

    @staticmethod
    def calculate_heart_rate(data):
        time_distance = data[-1].time - data[0].time
        return 60 * (len(data) - 1) / time_distance

    def update(self):
        if len(self.data_source.data) < self.number_of_peaks:
            return

        if len(self.data) and self.data_source.data[-1].time == self.data[-1].time:
            return

        self.data.append(
            DataPoint(time=self.data_source.data[-1].time,
                      value=HeartRate.calculate_heart_rate(self.data_source.data[-self.number_of_peaks:])
            )
        )