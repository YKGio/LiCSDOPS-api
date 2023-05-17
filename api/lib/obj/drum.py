from api.lib.classes import Config
from api.lib.obj.drumset import DrumSet

config = Config()

class Drum:
    def __init__(self, midi, cough):
        # Constructor
        self.midi = midi
        self.cough_np, self.sr = cough
        self.drumset = self.__generate()

    def __generate(self):
        drumset = config.params['DRUMSET']

        return list(map(lambda inst: DrumSet(inst), drumset)) # LAST EDIT

