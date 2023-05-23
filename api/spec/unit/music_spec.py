import sys
sys.path.append('C:/Users/DavidLin/NTHU/DB/ACADEMIC/LAB/COUGHit/COUGHit-api')

from api.lib.classes import Music
from api.lib.config import *

midi_path = '20230313_123209_hierdec_trio_16bar_sample_0.mid'
MIDI_PATH = os.path.join(MIDIS_DIR, midi_path)

Music(COUGHS_DIR, MIDI_PATH).generate().write()
