from DataPoint import DataPoint

class TimeIntervals:

    def __init__(self, data_source):
        self.data_source = data_source
        self.data = []

    def get_new_data(self):
        if len(self.data) == 0:
            return self.data_source.data
        else:
            current_time = self.data[-1].time

        new_data_points = []
        for dp in reversed(self.data_source.data):
            if dp.time >= current_time:
                new_data_points.append(dp)
            else:
                break

        return list(reversed(new_data_points))

    def update(self):
        new_data = self.get_new_data()

        for i in range(len(new_data)-1):
            self.data.append(
                DataPoint(
                    time=new_data[i+1].time,
                    value=new_data[i+1].time - new_data[i].time
                )
            )
