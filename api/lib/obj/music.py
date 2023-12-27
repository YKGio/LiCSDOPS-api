import librosa as rosa
import os
import numpy as np
import mido as md
import soundfile as sf
import time

# costum imports
from api.lib.obj.melody import Melody
from api.lib.obj.drum import Drum
from api.lib.config import *
import api.lib.audio_processing as ap
from api.lib.obj.metadata import Metadata

class Music:
    def __init__(self, cough_dir:str, midi_path:str):
        # Constructor
        self.cough_dir = cough_dir
        self.midi_path = midi_path
        self.midi = self.__load_midi()
        self.tpb = self.midi.ticks_per_beat
        self.tempo = self.__get_midi_tempo()
        self.notes_melody = self.__midi_parse(self.midi.tracks[1])
        self.notes_bass = self.__midi_parse(self.midi.tracks[2])
        self.notes_drum = self.__midi_parse(self.midi.tracks[3])

    def generate(self):
        # Generate the music

        # generate the melody, bass and drum
        print('Generatimg melody...')
        melody_np = Melody(self.notes_melody, self.random_choose_cough()).generate()
        print('Generating bass...')
        bass_np = Melody(self.notes_bass, self.random_choose_cough()).generate()
        print('Generating drum...')
        drum_np = Drum(self.notes_drum, self.random_choose_cough()).generate()

        # adjust volumn
        print('Adjusting volumn...')
        melody_np = ap.volumn_normalize(melody_np, MELODY_VOLUMN)
        bass_np = ap.volumn_normalize(bass_np, BASS_VOLUMN)
        drum_np = ap.volumn_normalize(drum_np, DRUM_VOLUMN)

        # merge the melody, bass and drum
        tracks_np = [melody_np, bass_np, drum_np]
        music_np = self.__merge(tracks_np)

        self.music_np = music_np

        print("Writing final music...")
        music = MusicWriter(music_np, self.sr)

        return music

    def __merge(self, tracks_np):
        # Merge the tracks
        music_np = np.zeros(max([len(track) for track in tracks_np]))
        for track_np in tracks_np:
            normalized = ap.normalize_length(track_np, len(music_np))
            music_np += normalized


        return music_np


    def random_choose_cough(self):
        # Randomly choose coughs from the coughs directory
        cough_dir = self.cough_dir + '/' + np.random.choice(os.listdir(self.cough_dir))
        Metadata().write("COUGH DIR: " + cough_dir)
        cough_np, sr = self.__load_audio_from(cough_dir)

        self.sr = sr
        return cough_np, sr

    def __load_audio_from(self, path: str, db=0):
        # Load audio from path with volumn change
        audio_np, sr = rosa.load(path)
        audio_np = self.__volumn_adjust(audio_np, db)

        return audio_np, sr


    def __load_midi(self):
        # Load midi file as mido object
        return md.MidiFile(self.midi_path)

    def __volumn_adjust(self, audio_np, db):
        # Scale the amplitude by the given decibels
        amplitude_ratio = 10**(db/20)
        audio_np = audio_np * amplitude_ratio

        return audio_np

    def __midi_parse(self, midi_track):
        # parse midi track to notes and ontimes
        on_time = 0
        notes = []
        for msg in midi_track:
            on_time += msg.time

            if msg.type == 'note_on':
                note = msg.note
                on_time_second = md.tick2second(on_time, self.tpb, self.tempo)
                notes.append([note, on_time_second])

        return notes

    def __get_midi_tempo(self):
        # Get the tempo of the midi file
        for msg in self.midi:
            if msg.type == 'set_tempo':
                return msg.tempo


class MusicWriter:
    def __init__(self, music_np, sr):
        self.music_np = music_np
        self.sr = sr
        self.path = OUTPUT_DIR

    def write(self):
        # Write the music to the output directory
        # set file name to the current time
        current_time = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        self.path += f'/{current_time}'
        print(f'Writing music to {self.path}...')
        sf.write(self.path+'.wav', self.music_np, self.sr)
        Metadata().move(self.path)


        