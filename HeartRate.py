from DataPoint import DataPoint


class HeartRate:
    def __init__(self, data_source, number_of_peaks=10):
        self.data = []
        self.data_source = data_source
        self.number_of_peaks = number_of_peaks

    @staticmethod
    def calculate_heart_rate(data):
        if(len(data) < 2):
            return 60

        time_distance = data[-1].time - data[0].time
        print(60 * (len(data) - 1) / time_distance)
        return 60 * (len(data) - 1) / time_distance

    def update(self):
        if len(self.data) and self.data[-1].time == self.data_source.data[-1].time:
            return


        last_time = self.data[-1].time if len(self.data) else 0

        for index, r_peak in enumerate(self.data_source.data):
            if r_peak.time > last_time:

                start_index = index - self.number_of_peaks if index > self.number_of_peaks else 0
                self.data.append(
                    DataPoint(time=r_peak.time,
                              value=HeartRate.calculate_heart_rate(self.data_source.data[start_index:index])
                    )
                )
                last_time = r_peak.time
