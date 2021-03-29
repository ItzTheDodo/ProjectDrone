from ProjectDrone.utils.ProjectUtils import *

DroneCnf = []


class DroneConfiguration:

    def __init__(self, name, battery, avg_flight_time, avg_speed, img):

        __metadata__ = ReadOnly

        self.name = name
        self.battery = battery
        self.avgft = avg_flight_time
        self.avgsp = avg_speed
        self.img = img

    def getName(self):
        return self.name

    def getBattery(self):
        return self.battery

    def getAverageFlightTime(self):
        return self.avgft

    def getAverageSpeed(self):
        return self.avgsp

    def getImg(self):
        return self.img

    def setName(self, name):
        self.name = name

    def setBattery(self, battery):
        self.battery = battery

    def setAverageFlightTime(self, ft):
        self.avgft = ft

    def setAverageSpeed(self, sp):
        self.avgsp = sp

    def setImg(self, img):
        self.img = img


def loadDroneConfigurations(runtime):
    cnf = runtime.DATAFOLDER.getConfig()
    for i in cnf.getValue("Drone-Configurations"):
        cur_drone_cnf = cnf.getValue("Drone-Configurations.%s" % i)
        DroneCnf.append(DroneConfiguration(i, cur_drone_cnf.getValue("Battery"), cur_drone_cnf.getValue("avg-flight-time"), cur_drone_cnf.getValue("avg-speed"), cur_drone_cnf.getValue("image")))
