import itertools
import math
import statistics

class ninjalib:
    def __init__(self,data,a=0,b=0,c=0):
        self.data = data
        self.a = a
        self.b = b
        self.c = c

    def anomaly(self):
        hits = []
        average = sum(self.data) / len(self.data)
        deviate = statistics.stdev(self.data)
        lower_bounds = average - deviate
        upper_bounds = average + deviate
        for i,value in enumerate(self.data):
            if not lower_bounds <= value <= upper_bounds:
                hits.append(value)
        return hits

    def flatten_list(self):
        new_data = self.data
        while True:
            if isinstance(new_data[0],list):
                new_data = list(itertools.chain(*new_data))
            else:
                break
        return new_data

    def flatten_tuple(self):
        new_data = self.data
        while True:
            if isinstance(new_data[0],tuple):
                new_data = tuple(itertools.chain(*new_data))
            else:
                break
        return new_data

    def project(self):
        try:
            screen_x = math.floor(self.data * (self.a / self.c))
        except ZeroDivisionError:
            screen_x = self.data + self.a
        try:
            screen_y = math.floor(self.data * (self.b / self.c))
        except ZeroDivisionError:
            screen_y = self.data + self.b
        return [screen_x, screen_y]

    def rotate_camera(self):
        hits = []
        theta = math.radians(self.b)
        center_x = []
        center_y = []
        center_z = []
        for i in range(len(self.data)):
            center_x.append(self.data[i][0])
            center_y.append(self.data[i][1])
            center_z.append(self.data[i][2])
        cx = statistics.mean(center_x)
        cy = statistics.mean(center_y)
        cz = statistics.mean(center_z)
        for i in range(len(self.data)):
            x = self.data[i][0] - cx
            y = self.data[i][1] - cy
            z = self.data[i][2] - cz
            if self.a == "x":
                hits.append([cx+x,cy+math.cos(theta)*y-math.sin(theta)*z,cz+math.sin(theta)*y+math.cos(theta)*z])
            if self.a == "y":
                hits.append([cx+math.cos(theta)*x+math.sin(theta)*z,cy+y,cz+-math.sin(theta)*x+math.cos(theta)*z])
            if self.a == "z":
                hits.append([cx+math.cos(theta)*x-math.sin(theta)*y,cy+math.sin(theta)*x+math.cos(theta)*y,cz+z])
        return hits

    def mean(self):
        return sum(self.data) / len(self.data)

    def odds(self):
        return str(round(sum(self.data) / (sum(self.data) + sum(self.a)) * 100,3)) + "%"

    def varint(self):
        return b"".join([bytes([(b := (self.data >> 7 * i) & 0x7F) | (0x80 if self.data >> 7 * (i + 1) else 0)]) for i in range(5) if (self.data >> 7 * i)])
