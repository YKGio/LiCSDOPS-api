import numpy as np
import librosa as ls
import mido as md
import ddsp.training.metrics

class Melody:
    def __init__(self, midi, cough):
        # Constructor
        self.midi = midi
        self.cough_np, self.sr = cough
        self.notes = self.__midi_parse()
        self.tpb = self.midi.ticks_per_beat
        self.tempo = self.__get_midi_tempo()
        self.audio_np = self.__generate()

    def __generate(self):
        cough_pitch = self.__get_pitch(self.cough_np)

        # Map the cough to the midi notes
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

        return np.concatenate(melody)

    def __filter_outliers(self, arr_np, threshold):
        # Filter out the outliers of the array
        mean = np.mean(arr_np)
        std = np.std(arr_np)
        filtered_arr = [x for x in arr_np if abs(x - mean) <= threshold * std]

        return filtered_arr

    def __get_pitch(self, audio_np):
        # Get the pitch of the audio
        # compute audio features
        audio_features = ddsp.training.metrics.compute_audio_features(audio_np)
        f0s = ls.hz_to_midi(audio_features['f0_hz'])

        # fileter out large difference
        filtered_f0s = self.__filter_outliers(f0s, 0.5)

        # get the most frequent pitch
        filtered_f0s = np.round(filtered_f0s).astype(int)
        pitchs, count = np.unique(filtered_f0s, return_counts=True)
        pitch = pitchs[np.argmax(count)]

        return pitch

    def __midi_parse(self):
        on_time = 0
        notes = []
        for msg in self.midi:
            note = msg.note
            on_time_second = md.tick2second(on_time, self.tpb, self.tempo)
            notes.append([note, on_time_second])

        return notes

    def __get_midi_tempo(self):
        # Get the tempo of the midi file
        for msg in self.midi:
            if msg.type == 'set_tempo':
                return msg.tempo
