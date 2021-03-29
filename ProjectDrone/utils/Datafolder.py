import os
import json
import importlib.util


class DataFolder(object):

    def __init__(self, fplan_folder, runtime):

        self.cwd = os.getcwd()
        self.runtime = runtime
        self.assets_folder = os.path.join(self.cwd, "assets")
        self.flight_plan_folder = fplan_folder
        self.imgitems = os.path.join(self.assets_folder, "img_items")
        self.driver_folder = DriverFolder(os.path.join(self.assets_folder, "drivers"), self.runtime)
        self.config = ConfigurationFile(os.path.join(self.assets_folder, "config.json"))

    def getFlightPlanFolder(self):
        return self.flight_plan_folder

    def getAssetsFolder(self):
        return self.assets_folder

    def getImgItemsFolder(self):
        return self.imgitems

    def getDriverFolder(self):
        return self.driver_folder

    def join(self, path, paths):
        return os.path.join(path, paths)

    def getConfig(self):
        return self.config


class DriverFolder(object):

    def __init__(self, url, runtime):

        self.url = url
        self.runtime = runtime
        self.drivers = []
        # import, runtime_driver
        self.driver_imports = []

        for driver in os.listdir(self.url):
            if os.path.isfile(os.path.join(self.url, driver)):
                self.drivers.append(os.path.join(self.url, driver))

    def getFolder(self):
        return self.url

    def getDrivers(self):
        return self.drivers

    def loadDrivers(self):
        for i in self.drivers:
            mod = self._import_module_from_file(i)
            cur_mod = mod.DroneDriver(self.runtime)
            self.driver_imports.append([mod, cur_mod])

    def _import_module_from_file(self, full_path_to_module):
        module = None
        try:
            module_dir, module_file = os.path.split(full_path_to_module)
            module_name, module_ext = os.path.splitext(module_file)
            spec = importlib.util.spec_from_file_location(module_name, full_path_to_module)
            module = spec.loader.load_module()
        except Exception as ec:
            print(ec)
        finally:
            return module


class ConfigurationFile(object):

    def __init__(self, url):

        self.url = url

        with open(r'%s' % url, "r") as read_file:
            self.data = json.load(read_file)
            read_file.close()

    def getPath(self):
        return self.url

    def getConfigurationSection(self, name):
        return ConfigurationSection(self.url, self.data[name])

    def getValue(self, path):
        try:
            section = self.data
            if str(path).__contains__("."):
                sp = str(path).split(".")
                for i in range(len(sp)):
                    if i == len(sp) - 1:
                        if type(section[sp[i]]) is dict or type(section[sp[i]]) is list:
                            return ConfigurationSection(self.url, section[sp[i]])
                        else:
                            return section[sp[i]]
                    section = section[sp[i]]
            else:
                return section[path]
        except KeyError:
            return False

    def setValue(self, path, value):

        if str(path).__contains__("."):
            sp = str(path).split(".")
            if len(sp) == 2:
                self.data[sp[0]][sp[1]] = value
            elif len(sp) == 3:
                self.data[sp[0]][sp[1]][sp[2]] = value
            elif len(sp) == 4:
                self.data[sp[0]][sp[1]][sp[2]][sp[3]] = value
            elif len(sp) == 5:
                self.data[sp[0]][sp[1]][sp[2]][sp[3]][sp[4]] = value
            with open(self.url, "w") as write_file:
                json.dump(self.data, write_file)
                write_file.close()
        else:
            self.data[path] = value
            with open(r'%s' % self.url, "w") as write_file:
                json.dump(self.data, write_file)
                write_file.close()


class ConfigurationSection(object):

    def __init__(self, url, section):

        self.section = section
        self.url = url

    def getCurrentSection(self):
        return self.section

    def getConfigurationSection(self, name):
        return ConfigurationSection(self.url, self.section[name])

    def getValue(self, path):
        try:
            section = self.section
            if str(path).__contains__("."):
                sp = str(path).split(".")
                for i in range(len(sp)):
                    if i == len(sp) - 1:
                        if type(section[sp]) is dict or type(section[sp]) is list:
                            return ConfigurationSection(self.url, section[sp])
                        else:
                            return section[sp]
                    section = section[sp]
            else:
                return section[path]
        except KeyError:
            return False

    def setValue(self, path, value):

        if str(path).__contains__("."):
            sp = str(path).split(".")
            if len(sp) == 2:
                self.section[sp[0]][sp[1]] = value
            elif len(sp) == 3:
                self.section[sp[0]][sp[1]][sp[2]] = value
            elif len(sp) == 4:
                self.section[sp[0]][sp[1]][sp[2]][sp[3]] = value
            elif len(sp) == 5:
                self.section[sp[0]][sp[1]][sp[2]][sp[3]][sp[4]] = value
            with open(self.url, "w") as write_file:
                json.dump(self.section, write_file)
                write_file.close()
        else:
            self.section[path] = value
            with open(r'%s' % self.url, "w") as write_file:
                json.dump(self.section, write_file)
                write_file.close()

