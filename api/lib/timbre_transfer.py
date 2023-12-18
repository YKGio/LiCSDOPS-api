import copy
import os
import time
import crepe
import ddsp
import ddsp.training
from ddsp.training.postprocessing import (
    detect_notes, fit_quantile_transform
)
import gin
import librosa
import numpy as np
import pickle
import tensorflow.compat.v2 as tf
import soundfile
from tensorflow.python.ops.numpy_ops import np_config

from django.conf import settings

# Helper Functions
sample_rate = 16000  # 16000
np_config.enable_numpy_behavior()

def get_tuning_factor(f0_midi, f0_confidence, mask_on):
  """Get an offset in cents, to most consistent set of chromatic intervals."""
  # Difference from midi offset by different tuning_factors.
  tuning_factors = np.linspace(-0.5, 0.5, 101)  # 1 cent divisions.
  midi_diffs = (f0_midi[mask_on][:, np.newaxis] -
                tuning_factors[np.newaxis, :]) % 1.0
  midi_diffs[midi_diffs > 0.5] -= 1.0
  weights = f0_confidence[mask_on][:, np.newaxis]

  ## Computes mininmum adjustment distance.
  cost_diffs = np.abs(midi_diffs)
  cost_diffs = np.mean(weights * cost_diffs, axis=0)

  ## Computes mininmum "note" transitions.
  f0_at = f0_midi[mask_on][:, np.newaxis] - midi_diffs
  f0_at_diffs = np.diff(f0_at, axis=0)
  deltas = (f0_at_diffs != 0.0).astype(np.float)
  cost_deltas = np.mean(weights[:-1] * deltas, axis=0)

  # Tuning factor is minimum cost.
  norm = lambda x: (x - np.mean(x)) / np.std(x)
  cost = norm(cost_deltas) + norm(cost_diffs)
  return tuning_factors[np.argmin(cost)]

def auto_tune(f0_midi, tuning_factor, mask_on, amount=0.0, chromatic=False):
  """Reduce variance of f0 from the chromatic or scale intervals."""
  if chromatic:
    midi_diff = (f0_midi - tuning_factor) % 1.0
    midi_diff[midi_diff > 0.5] -= 1.0
  else:
    major_scale = np.ravel(
        [np.array([0, 2, 4, 5, 7, 9, 11]) + 12 * i for i in range(10)])
    all_scales = np.stack([major_scale + i for i in range(12)])

    f0_on = f0_midi[mask_on]
    # [time, scale, note]
    f0_diff_tsn = (
        f0_on[:, np.newaxis, np.newaxis] - all_scales[np.newaxis, :, :])
    # [time, scale]
    f0_diff_ts = np.min(np.abs(f0_diff_tsn), axis=-1)
    # [scale]
    f0_diff_s = np.mean(f0_diff_ts, axis=0)
    scale_idx = np.argmin(f0_diff_s)
    scale = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb',
             'G', 'Ab', 'A', 'Bb', 'B', 'C'][scale_idx]

    # [time]
    f0_diff_tn = f0_midi[:, np.newaxis] - all_scales[scale_idx][np.newaxis, :]
    note_idx = np.argmin(np.abs(f0_diff_tn), axis=-1)
    midi_diff = np.take_along_axis(
        f0_diff_tn, note_idx[:, np.newaxis], axis=-1)[:, 0]
    print('Autotuning... \nInferred key: {}  '
          '\nTuning offset: {} cents'.format(scale, int(tuning_factor * 100)))

  # Adjust the midi signal.
  return f0_midi - amount * midi_diff


def call(audio, inst):
  MODEL_DIR = f'{settings.DDSP_MODEL_DIR}/{inst}/'
  if len(audio.shape) == 1:
    audio = audio[np.newaxis, :]

  # Setup the session.
  ddsp.spectral_ops.reset_crepe()

  # Compute features.
  start_time = time.time()
  audio_features = ddsp.training.metrics.compute_audio_features(audio)
  audio_features['loudness_db'] = audio_features['loudness_db'].numpy()
  audio_features_mod = None
  print('Audio features took %.1f seconds' % (time.time() - start_time))

  # Load the dataset statistics.
  DATASET_STATS = None
  dataset_stats_file = MODEL_DIR+'dataset_statistics.pkl'
  print(f'Loading dataset statistics from {dataset_stats_file}')
  try:
    if tf.io.gfile.exists(dataset_stats_file):
      with tf.io.gfile.GFile(dataset_stats_file, 'rb') as f:
        DATASET_STATS = pickle.load(f)
  except Exception as err:
    print('Loading dataset statistics from pickle failed: {}.'.format(err))


  # Parse gin config,
  gin_file = MODEL_DIR+'operative_config-0.gin'
  with gin.unlock_config():
    gin.parse_config_file(gin_file, skip_unknown=True)

  if inst == 'Violin':
    ckpt = MODEL_DIR+'ckpt-40000'
  else:
    ckpt = MODEL_DIR+'ckpt-20000'

  # Ensure dimensions and sampling rates are equal
  time_steps_train = gin.query_parameter('F0LoudnessPreprocessor.time_steps')
  n_samples_train = gin.query_parameter('Harmonic.n_samples')
  hop_size = int(n_samples_train / time_steps_train)

  time_steps = int(audio.shape[1] / hop_size)
  n_samples = time_steps * hop_size


  gin_params = [
      'Harmonic.n_samples = {}'.format(n_samples),
      'FilteredNoise.n_samples = {}'.format(n_samples),
      'F0LoudnessPreprocessor.time_steps = {}'.format(time_steps),
      'oscillator_bank.use_angular_cumsum = True',  # Avoids cumsum accumulation errors.
  ]

  with gin.unlock_config():
    gin.parse_config(gin_params)


  # Trim all input vectors to correct lengths
  for key in ['f0_hz', 'f0_confidence', 'loudness_db']:
    audio_features[key] = audio_features[key][:time_steps]
  audio_features['audio'] = audio_features['audio'][:, :n_samples]


  # Set up the model just to predict audio given new conditioning
  model = ddsp.training.models.Autoencoder()
  model.restore(ckpt)

  # Build model by running a batch through it.
  start_time = time.time()
  _ = model(audio_features, training=False)
  print('Restoring model took %.1f seconds' % (time.time() - start_time))

  threshold = 1
  ADJUST = True
  quiet = 20
  autotune = 0.5
  pitch_shift =  0
  loudness_shift = 10

  audio_features_mod = {k: v.copy() for k, v in audio_features.items()}

  ## Helper functions.
  def shift_ld(audio_features, ld_shift=0.0):
    """Shift loudness by a number of ocatves."""
    audio_features['loudness_db'] += ld_shift
    return audio_features

  def shift_f0(audio_features, pitch_shift=0.0):
    """Shift f0 by a number of ocatves."""
    audio_features['f0_hz'] *= 2.0 ** (pitch_shift)
    audio_features['f0_hz'] = np.clip(audio_features['f0_hz'],
                                      0.0,
                                      librosa.midi_to_hz(110.0))
    return audio_features


  mask_on = None

  if ADJUST and DATASET_STATS is not None:
    # Detect sections that are "on".
    mask_on, note_on_value = detect_notes(audio_features['loudness_db'],
                                          audio_features['f0_confidence'],
                                          threshold)

    if np.any(mask_on):
      # Shift the pitch register.
      target_mean_pitch = DATASET_STATS['mean_pitch']
      pitch = ddsp.core.hz_to_midi(audio_features['f0_hz'])
      mean_pitch = np.mean(pitch[mask_on])
      p_diff = target_mean_pitch - mean_pitch
      p_diff_octave = p_diff / 12.0
      round_fn = np.floor if p_diff_octave > 1.5 else np.ceil
      p_diff_octave = round_fn(p_diff_octave)
      audio_features_mod = shift_f0(audio_features_mod, p_diff_octave)


      # Quantile shift the note_on parts.
      _, loudness_norm = fit_quantile_transform(
          audio_features['loudness_db'],
          mask_on,
          inv_quantile=DATASET_STATS['quantile_transform'])

      # Turn down the note_off parts.
      mask_off = np.logical_not(mask_on)
      loudness_norm[mask_off] -=  quiet * (1.0 - note_on_value[mask_off][:, np.newaxis])
      loudness_norm = np.reshape(loudness_norm, audio_features['loudness_db'].shape)

      audio_features_mod['loudness_db'] = loudness_norm

      # Auto-tune.
      if autotune:
        f0_midi = np.array(ddsp.core.hz_to_midi(audio_features_mod['f0_hz']))
        tuning_factor = get_tuning_factor(f0_midi, audio_features_mod['f0_confidence'], mask_on)
        f0_midi_at = auto_tune(f0_midi, tuning_factor, mask_on, amount=autotune)
        audio_features_mod['f0_hz'] = ddsp.core.midi_to_hz(f0_midi_at)

    else:
      print('\nSkipping auto-adjust (no notes detected or ADJUST box empty).')

  else:
    print('\nSkipping auto-adujst (box not checked or no dataset statistics found).')

  # Manual Shifts.
  audio_features_mod = shift_ld(audio_features_mod, loudness_shift)
  audio_features_mod = shift_f0(audio_features_mod, pitch_shift)

  #Resynthesize Audio
  af = audio_features if audio_features_mod is None else audio_features_mod

  # Run a batch of predictions.
  start_time = time.time()
  outputs = model(af, training=False)
  audio_gen = model.get_audio_from_outputs(outputs)
  print('Prediction took %.1f seconds' % (time.time() - start_time))

  audio_gen = audio_gen[0]
  return audio_gen
