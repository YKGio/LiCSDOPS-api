import ddsp.training.metrics
import librosa as ls
import numpy as np
from scipy.signal import butter, lfilter

def get_pitch(audio_np):
    # Get the pitch of the audio
    # compute audio features
    audio_features = ddsp.training.metrics.compute_audio_features(audio_np)
    f0s = ls.hz_to_midi(audio_features['f0_hz'])

    # fileter out large difference
    filtered_f0s = filter_outliers(f0s, 0.5)

    # get the most frequent pitch
    filtered_f0s = np.round(filtered_f0s).astype(int)
    pitchs, count = np.unique(filtered_f0s, return_counts=True)
    pitch = pitchs[np.argmax(count)]

    return pitch

def filter_outliers(arr_np, threshold):
    # Filter out the outliers of the array
    mean = np.mean(arr_np)
    std = np.std(arr_np)
    filtered_arr = [x for x in arr_np if abs(x - mean) <= threshold * std]

    return filtered_arr

def pitch_shift(audio_np, sr, pitch):
    # Pitch shift the audio
    bias = pitch - get_pitch(audio_np)
    return ls.effects.pitch_shift(audio_np, sr=sr, n_steps=bias)

def butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def volumn_normalize(audio_np, db=-30):
    # Normalize the audio to the given decibels
    before_db = get_max_db(audio_np)
    bias = db - int(before_db)

    amplitude_ratio = 10**(bias/20)
    audio_np = audio_np * amplitude_ratio

    return audio_np

def get_max_db(audio_np):
    # Get the maximum decibels of the audio
    return ls.amplitude_to_db(audio_np).max()


def fadeout(audio_np, time):
    # trim the cough
    # create fade out env
    length = len(audio_np)
    time = length * time/100
    time = int(time)
    env = np.linspace(1, 0, time)
    env = np.pad(env, (0, length-time), mode='constant', constant_values=0)

    # apply fade out env
    cough_np_trimed = audio_np * env

    return cough_np_trimed

def normalize_length(audio_np, length):

    silent = np.zeros(length - len(audio_np))
    normalized = np.append(audio_np, silent)
    return normalized
