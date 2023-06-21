import os
from django.conf import settings

class UploadCoughFile:
    class UploadFileError(Exception):
        def __init__(self):
            self.message = "Error uploading file"

    def call(self, file):
        try:
            file_path = os.path.join(settings.MEDIA_ROOT, "audios/coughs", file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
        except Exception:
            raise self.UploadFileError()
