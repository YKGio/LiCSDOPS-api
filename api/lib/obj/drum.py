from api.lib.config import *
import numpy as np
import api.lib.audio_processing as ap

class Drum:
    def __init__(self, notes, cough):
        self.notes = notes
        self.cough_np, self.sr = cough
        self.set_name = self.__name()
        self.set_sample_np = self.__sample_from_cough()

    def generate(self):
        # generate the drum track
        drum = []
        for i, note in enumerate(self.notes):
            # get the note info
            pitch, ont_time = note
            _, on_time_next = self.notes[i + 1] if i < len(self.notes) - 1 else (0, 0)

            # get the drum sample
            drum_name = DRUM_MAP[pitch]
            drum_sample_np = self.set_sample_np[drum_name]

            # get the duration of the note
            duration_drum_sample_np = len(drum_sample_np)
            note_duration = int(np.round((on_time_next - ont_time) * self.sr))

            if note_duration < duration_drum_sample_np:
                drum_sample_np = drum_sample_np[:note_duration]
            elif note_duration >= duration_drum_sample_np:
                silent = np.zeros(note_duration - duration_drum_sample_np)
                drum_sample_np = np.concatenate((drum_sample_np, silent))

            drum.append(drum_sample_np)

        return np.concatenate(drum)

    def __name(self):
        # get drumset name
        return list(DRUMSET.keys())

    def __sample_from_cough(self):
        # convert cough to drum sample
        drumset = {}
        for drum in self.set_name:
            # pitch shift
            cough_np = ap.pitch_shift(self.cough_np, self.sr, DRUMSET[drum][PITCH])

            # trim the cough
            cough_np = ap.fadeout(cough_np, DRUMSET[drum][FADEOUT])


            # filt
            if DRUMSET[drum][FILTER] == True:
                cough_np = ap.butter_highpass_filter(cough_np, 4096, self.sr, order=5)

            # set volumn
            cough_np = ap.volumn_normalize(cough_np, DRUMSET[drum][VOLUMN])

            drumset[drum] = cough_np

        return drumset


