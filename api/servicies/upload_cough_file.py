import os
from django.conf import settings
import soundfile

class UploadCoughFile:
    class UploadFileError(Exception):
        def __init__(self):
            self.message = "Error uploading file"

    def call(self, file):
        try:
            coughs_dir = os.path.join(settings.MEDIA_ROOT, "audios/coughs")
            file_path = os.path.join(coughs_dir, file['name'])

            soundfile.write(file_path, file['audio_raw'], file['sample_rate'], 'PCM_16')
        except Exception as e:
            print("ERROR UPLOADING FILE", e)
            raise self.UploadFileError()
