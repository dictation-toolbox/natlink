import os, json

class Configuration:
    # Hardcoded constants
    TMP_FOLDER = os.getenv('APPDATA') + '\\natlink\\'
    NATLINK_INSTALL_DIR = "c:/natlink"
    SUPPORTED_PYTHON_VERSION = ["3.7", "3.8"]
    SUPPORTED_PYTHON_LINKS = {"3.7": "https://www.python.org/ftp/python/3.7.6/python-3.7.6.exe",
                              "3.8": "https://www.python.org/ftp/python/3.8.1/python-3.8.1.exe"}
    DRAGON_DEFAULT_PATHS = {
        # dragon version: paths for ( natspeak.exe, nsapps.ini nssystem.ini)
        15: ("C:/Program Files (x86)/Nuance/NaturallySpeaking15","C:/ProgramData/Nuance/NaturallySpeaking15")
    }

    # These values can change
    dragon = {
        "version":None,
        "program_path":None,
        "data_path": None,
    }


    def __init__(self, path):
        if os.path.isfile(path):
            with open('example.json', 'r') as myfile:
                data = myfile.read()
            # parse file
            obj = json.loads(data)
        else:
            self._find_dragon_installation()

    def _find_dragon_installation(self):
        if os.path.isdir(self.DRAGON_DEFAULT_PATHS[15][0]) and\
                os.path.isdir(self.DRAGON_DEFAULT_PATHS[15][1]):
            self.dragon["version"]=15
            self.dragon["program_path"] = self.DRAGON_DEFAULT_PATHS[15][0]
            self.dragon["data_path"] = self.DRAGON_DEFAULT_PATHS[15][1]
