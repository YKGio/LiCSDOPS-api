import random
import numpy as np
import librosa as ls
import mido as md
from scipy import rand
import api.lib.audio_processing as ap
from api.lib import timbre_transfer
import api.lib.config as config


class Melody:
    def __init__(self, notes, cough):
        # Constructor
        self.cough_np, self.sr = cough
        self.notes = notes

    def generate(self):
        cough_pitch = ap.get_pitch(self.cough_np)

        cough_np = ap.noise_reduce(self.cough_np, self.sr)

        # Map the cough to the midi notes
        print("Scale Mapping...")
        melody = []
        for i, note in enumerate(self.notes):
            pitch, on_time = note
            _, on_time_next = self.notes[i + 1] if i < len(self.notes) - 1 else (0, 0)
            cough_duration = len(self.cough_np)

            bias = pitch - cough_pitch
            shifted_cough = ls.effects.pitch_shift(self.cough_np, sr=self.sr, n_steps=bias - 12)

            note_duration = int(np.round((on_time_next - on_time) * self.sr))

            if note_duration < cough_duration:
                note = shifted_cough[:note_duration]
            elif note_duration >= cough_duration:
                silent = np.zeros(note_duration - cough_duration)
                note = np.concatenate((shifted_cough, silent))

            melody.append(note)

        melody = np.concatenate(melody)

        melody = ap.pitch_shift_by(melody, self.sr, 12)

        inst = random.choice(config.INST_LIST)
        print("Timbre Transfer...")
        tt_melody = timbre_transfer.call(melody, inst)

        return tt_melody

