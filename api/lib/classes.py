import api.lib.obj.music as music
import api.lib.obj.melody as melody
import api.lib.obj.drum as drum
import yaml

class Config:
    def __init__(self):
        self.params = self.__load_config()

    def __load_config(self):
        with open('api/lib/config.yaml', 'r') as f:
            return yaml.load(f, Loader=yaml.FullLoader)
