import os
import random

class GerenciadorAudio:
    def __init__(self):
        self.indices = {} # folder_path -> current_index

    def get_audio_files(self, folder):
        """Retorna lista de arquivos de áudio suportados na pasta"""
        if not folder or not os.path.exists(folder):
            return []
        
        extensions = ('.mp3', '.wav', '.aac', '.ogg', '.m4a')
        files = [os.path.join(folder, f) for f in os.listdir(folder) 
                 if f.lower().endswith(extensions)]
        return sorted(files)

    def get_next_audio(self, folder, random_mode=False):
        """Retorna o caminho do próximo áudio a ser usado"""
        files = self.get_audio_files(folder)
        if not files:
            return None

        if random_mode:
            return random.choice(files)
        
        # Modo sequencial
        idx = self.indices.get(folder, 0)
        audio_path = files[idx % len(files)]
        self.indices[folder] = idx + 1
        return audio_path
