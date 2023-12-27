import os
import sys

### PATH SETTINGS ###
COUGHS_DIR = 'medias/audios/coughs'
MIDIS_DIR = 'medias/midis'
OUTPUT_DIR = 'medias/audios/output'

API_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(API_DIR)
sys.path.append(PROJECT_DIR)
COUGHS_DIR = os.path.join(API_DIR, COUGHS_DIR)
MIDIS_DIR = os.path.join(API_DIR, MIDIS_DIR)
OUTPUT_DIR = os.path.join(API_DIR, OUTPUT_DIR)

INST_LIST = ['Flute', 'Violin']

MELODY_VOLUMN = -10
BASS_VOLUMN = -10
DRUM_VOLUMN = -15

PITCH = 'PITCH'
VOLUMN = 'VOLUMN'
FADEOUT = 'FADEOUT'
FILTER = 'FILTER'

KICK = 'KICK'
SNARE = 'SNARE'
HIHAT = 'HIHAT'
TOM1 = 'TOM1'
TOM2 = 'TOM2'

DRUM_MAP = {36:KICK, 38:SNARE, 42:HIHAT, 45:TOM1, 46:HIHAT, 48: TOM2, 49: HIHAT, 50:TOM2, 51:HIHAT}

DRUMSET = {
    KICK : {
        PITCH : 40,
        VOLUMN : 0,
        FADEOUT : 50,
        FILTER : False
    },
    SNARE : {
        PITCH : 80,
        VOLUMN : 0,
        FADEOUT : 50,
        FILTER : False
    },
    HIHAT : {
        PITCH : 60,
        VOLUMN : -3,
        FADEOUT : 20,
        FILTER : True
    },
    TOM1 : {
        PITCH : 45,
        VOLUMN : -3,
        FADEOUT : 50,
        FILTER : False
    },
    TOM2 : {
        PITCH : 50,
        VOLUMN : -3,
        FADEOUT : 50,
        FILTER : False
    },
}
