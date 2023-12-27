import os

class Metadata:
    def __init__(self):
        self.dir = 'api/medias/audios/tmp/tmp.txt'
    
    def write(self, text):
        print(f'[METADATA] {text}')
        with open(self.dir, 'a') as f:
            f.write(text + '\n')
            
    def move(self, dir):
        os.rename(self.dir, dir + '.txt')