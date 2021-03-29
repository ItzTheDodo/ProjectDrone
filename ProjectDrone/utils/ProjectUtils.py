import os
import re
import json


def setupIOConfig():

    cnf_basic = {"flight-plan-folder": "cwd", "Version": "1.0.0", "fplan-height": "150", "fplan-vs": "3", "fplan-rotational-speed-dps": "10", "Drone-Configurations": {"Parrot Bebop": {"Battery": "2700", "avg-speed": "15", "avg-flight-time": "20"}, "Mavic Mini": {"Battery": "2400", "avg-speed": "10", "avg-flight-time": "30"}, "Mavic Pro": {"Battery": "3830", "avg-speed": "16", "avg-flight-time": "23"}, "Parrot Disco": {"Battery": "2700", "avg-speed": "20", "avg-flight-time": "40"}}}
    cnf_path = os.path.join(os.getcwd(), "assets\\config.json")

    if not os.path.exists(cnf_path):
        with open(r'%s' % cnf_path, "w") as file:
            json.dump(cnf_basic, file)
            file.close()
    configValidate(cnf_path)
    with open(r'%s' % cnf_path, "r") as rfile:
        data = json.load(rfile)
        fplan_folder = os.path.join(data["flight-plan-folder"], "flight_plans")
        if not os.path.exists(fplan_folder):
            os.mkdir(fplan_folder)
        rfile.close()
    return fplan_folder


def configValidate(cnf_path):
    cnf_write = False
    with open(r'%s' % cnf_path, "r") as rfile:
        data = json.load(rfile)
        if data["flight-plan-folder"] == "cwd":
            data["flight-plan-folder"] = os.path.join(os.getcwd(), "assets")
            cnf_write = True
        rfile.close()
    if cnf_write:
        with open(r'%s' % cnf_path, "w") as wfile:
            json.dump(data, wfile)
            wfile.close()


def parseCnfLine(str):
    return re.findall('"([^"]*)"', str.split(":"[1]))


class ReadOnly(type):

    def __setattr__(self, name, value):
        raise ValueError
