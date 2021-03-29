from ProjectDrone.utils.Datafolder import DataFolder
from ProjectDrone.utils.ProjectUtils import *
from ProjectDrone.DroneAssets.DroneConfiguration import loadDroneConfigurations, DroneCnf
from ProjectDrone.Client.ProjectGUI import *
import sys

__author__ = "Aiden"


class ProjectDrone:

    def __init__(self):

        __metadata__ = ReadOnly

        fplan_folder = setupIOConfig()
        self.DATAFOLDER = DataFolder(fplan_folder, self)
        self.DATAFOLDER.getFlightPlanFolder()

        self.DATAFOLDER.getImgItemsFolder()
        self._load_drivers()
        self.drivers = self.DATAFOLDER.getDriverFolder().getDrivers()

        self.config = self.DATAFOLDER.getConfig()
        loadDroneConfigurations(self)

        self._start_gui()

    def _start_gui(self):
        Client(self.config.getValue("Version"), self)

    def _load_drivers(self):
        self.DATAFOLDER.getDriverFolder().loadDrivers()

    def close(self):
        print("Closing...")
        sys.exit(-1)


ProjectDrone()
sys.exit(-1)
