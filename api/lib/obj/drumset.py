import yaml
from api.lib.classes import Config

class DrumSet:
    def __init__(self, name):
        self.name = name
        self.params = self.__get_params()
        self.pitch = self.params['PITCH']
        self.volume = self.params['VOLUME']
        self.fadeout = self.params['FADEOUT']
        self.filter = self.params['FILTER']

    def __get_params(self):
        config = Config()
        NAME = self.name.upper()
        return config.params[NAME]
