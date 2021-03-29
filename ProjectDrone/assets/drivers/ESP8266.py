from ProjectDrone.utils.ProjectDriver import Driver
import os
import json
import urllib.request
import time
from ast import literal_eval


class DroneDriver(Driver):

    def __init__(self, runtime):
        Driver.__init__(self, runtime)

        self.cnf_path = os.path.join(self.RUNTIME.DATAFOLDER.getDriverFolder().getFolder(), "ESP8266DriverCore\\config.json")
        with open(r'%s' % self.cnf_path, "r") as read_file:
            self.cnf_data = json.load(read_file)
            read_file.close()
        self.ip = self.cnf_data["ip"]
        self.url = "http://" + self.ip

    def takeoff(self):
        n = urllib.request.urlopen(self.url + "/up")
        return n

    def land(self):
        n = urllib.request.urlopen(self.url + "/down")
        return n

    def up(self):
        n = urllib.request.urlopen(self.url + "/up")
        return n

    def down(self):
        n = urllib.request.urlopen(self.url + "/down")
        return n

    def forward(self):
        n = urllib.request.urlopen(self.url + "/forward")
        return n

    def backward(self):
        n = urllib.request.urlopen(self.url + "/backward")
        return n

    def right(self):
        n = urllib.request.urlopen(self.url + "/right")
        return n

    def left(self):
        n = urllib.request.urlopen(self.url + "/left")
        return n

    def FPV_Enabled(self):
        return False

    def getGeoLocation(self):
        urllib.request.urlopen(self.url + "/dist")
        time.sleep(1)
        n = literal_eval(urllib.request.urlopen(self.url + "/dist"))
        return n

    def geoLocationEnabled(self):
        return True
