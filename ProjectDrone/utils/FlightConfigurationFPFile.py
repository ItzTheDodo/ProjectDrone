import os
from ast import literal_eval


class FPFile(object):

    def __init__(self, runtime, name, map_data, geo_coords):

        self.RUNTIME = runtime
        self.name = name + ".fp"
        # [lat, long, zoom]
        self.map_data = map_data
        # [[[lat, long], [lat, long]], [[lat, long], [lat, long]], [[lat, long], [lat, long]]]
        self.geocoords = geo_coords
        self.path = os.path.join(self.RUNTIME.DATAFOLDER.getFlightPlanFolder(), self.name)

    def getName(self):
        return self.name

    def getMapData(self):
        return self.map_data

    def getGeoCoords(self):
        return self.geocoords

    def setName(self, name):
        self.name = name

    def setMapData(self, md):
        self.map_data = md

    def setGeoCoords(self, gc):
        self.geocoords = gc

    def create(self):
        with open(self.path, "w") as temp_file:
            temp_file.write("meta:%s\n" % str(self.map_data))
            for i in self.geocoords:
                temp_file.write("coord:%s\n" % str(i))
            temp_file.close()


def parse_FPFile(path):
    meta = []
    data = []
    with open(path, "r") as temp_file:
        lines = temp_file.readlines()
        for i in lines:
            line_sp = i.replace("\n", "").split(":")
            if line_sp[0].lower() == "meta":
                meta = literal_eval(line_sp[1])
            elif line_sp[0].lower() == "coord":
                data.append(line_sp[1])
        temp_file.close()
    return [meta, data]
