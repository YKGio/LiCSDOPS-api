from api.lib.classes import Music, Metadata
from api.lib.config import *
import magenta.music as mm
from magenta.models.music_vae import configs
from magenta.models.music_vae.trained_model import TrainedModel
import time
import os
from django.conf import settings
from api.lib.config import MIDIS_DIR
import shutil

class GenerateMusic:
    class GenerateMusicError(Exception):
        def __init__(self):
            self.message = "Error generating music"

    def __trio_16bar_generate(self):
        trio_models = {}
        hierdec_trio_16bar_config = configs.CONFIG_MAP['hierdec-trio_16bar']
        trio_models['hierdec_trio_16bar'] = TrainedModel(hierdec_trio_16bar_config, batch_size=2, checkpoint_dir_or_path=settings.MAGENTA_MODEL_DIR + '/trio_16bar_hierdec.ckpt')

        trio_sample_model = "hierdec_trio_16bar"
        temperature = 0.8

        print('Generating MIDI...')
        trio_16_samples = trio_models[trio_sample_model].sample(n=4, length=256, temperature=temperature)
        t = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        filename = os.path.join(MIDIS_DIR, t + '_%s_sample_' % (trio_sample_model))

        print('Writing MIDI...')
        try:
            for i, ns in enumerate(trio_16_samples):
                mm.sequence_proto_to_midi_file(ns, filename + str(i) + '.mid')

            return filename
        except Exception as e:
            print("ERROR WRITING SAMPLES", e)
            raise self.GenerateMusicError()

    def clear_cough_dir(self):
        cough_dir = COUGHS_DIR
        for filename in os.listdir(cough_dir):
            shutil.move(os.path.join(COUGHS_DIR, filename), COUGHS_HISTORY_DIR)

    def call(self):
        try:
            midi_dir = self.__trio_16bar_generate() + '0.mid'
            print("MIDI DIR", midi_dir)
            Metadata().write("MIDI DIR: " + midi_dir)
            midi_path = os.path.join(MIDIS_DIR, midi_dir)
            music = Music(COUGHS_DIR, midi_path).generate().write()
            self.clear_cough_dir()
            return music

        except Exception as e:
            print("ERROR GENERATING MUSIC", e)
            raise self.GenerateMusicError()

