import librosa as rosa
from pydub import AudioSegment as pa
import os
import numpy as np
import mido

# costum imports
from api.lib.obj.melody import Melody
from api.lib.obj.drum import Drum

class Music:
    def __init__(self, cough_dir:str, midi_path:str):
        # Constructor
        self.cough_dir = cough_dir
        self.midi_path = midi_path
        self.midi = self.__load_midi()
        self.tpb = self.midi.ticks_per_beat
        self.midi_track_melody = self.midi.tracks[1]
        self.midi_track_bass = self.midi.tracks[2]
        self.midi_track_drum = self.midi.tracks[3]

    def generate(self):
        # Generate the music

        # generate the melody, bass and drum
        melody = Melody(self.midi_track_melody, self.__random_choose_cough())
        bass = Melody(self.midi_track_bass, self.__random_choose_cough())
        drum = Drum(self.midi_track_drum, self.__random_choose_cough())


    def __random_choose_cough(self):
        # Randomly choose coughs from the coughs directory
        cough_np, sr = self.__load_audio_from(self.cough_dir + '/' + np.random.choice(os.listdir(self.cough_dir)))

        return cough_np, sr

    def __load_audio_from(self, path: str, db=0):
        # Load audio from path with volumn change
        audio_np, sr = rosa.load(path)
        audio_np = self.__volumn_adjust(audio_np, db)

        return audio_np, sr


    def __load_midi(self):
        # Load midi file as mido object
        return mido.MidiFile(self.midi_path)

    def __volumn_adjust(self, audio_np, db):
        # Scale the amplitude by the given decibels
        amplitude_ratio = 10**(db/20)
        audio_np = audio_np * amplitude_ratio

        return audio_np

    def __get_max_db(self, audio_np):
        # Get the maximum decibels of the audio
        return rosa.amplitude_to_db(audio_np).max()

    def __volumn_normalize(self, audio_np, sr, db=-30):
        # Normalize the audio to the given decibels
        before_db = self.__get_max_db(audio_np)
        bias = db - int(before_db)

        amplitude_ratio = 10**(bias/20)
        audio_np = audio_np * amplitude_ratio

        return audio_np
