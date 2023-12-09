from api.lib.classes import Music
from api.lib.config import *

class GenerateMusic:
    class GenerateMusicError(Exception):
        def __init__(self):
            self.message = "Error generating music"

    def call(self):
        try:
            # MIDI should be generate by MusicVAE
            # Use mock data for now
            midi =  '20230313_123209_hierdec_trio_16bar_sample_0.mid'
            midi_path = os.path.join(MIDIS_DIR, midi)
            music = Music(COUGHS_DIR, midi_path).generate().write()
            return music

        except Exception as e:
            print("ERROR GENERATING MUSIC", e)
            raise self.GenerateMusicError()
