import os
from PIL import Image

class GerenciadorEmojis:
    def __init__(self):
        self.emojis = {}
        self.folder = None

    def get_project_root(self):
        """Encontra a raiz do projeto onde está o run.py"""
        try:
            # Pega o diretório atual do arquivo
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Sobe até encontrar o diretório que contém run.py
            while current_dir != os.path.dirname(current_dir):  # Não chegou na raiz do sistema
                # Verifica se run.py está em scripts/run.py ou diretamente
                if os.path.exists(os.path.join(current_dir, 'scripts', 'run.py')):
                    return current_dir
                if os.path.exists(os.path.join(current_dir, 'run.py')):
                    return current_dir
                current_dir = os.path.dirname(current_dir)
        except:
            pass
        return None

    def auto_detect_folder(self):
        """Tenta detectar automaticamente a pasta de emojis na raiz do projeto"""
        root = self.get_project_root()
        if not root:
            return None
        
        # Procura por pasta 'emojis' ou 'emoji' na raiz
        possible_names = ['emojis', 'emoji', 'Emojis', 'Emoji']
        for name in possible_names:
            emoji_path = os.path.join(root, name)
            if os.path.exists(emoji_path) and os.path.isdir(emoji_path):
                return emoji_path
        
        return None

    def load_emojis(self, folder):
        """Carrega emojis de uma pasta específica"""
        self.folder = folder
        self.emojis = {}
        if not folder or not os.path.exists(folder): 
            return 0
        
        count = 0
        try:
            for f in os.listdir(folder):
                if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                    try:
                        img = Image.open(os.path.join(folder, f))
                        if img.mode != 'RGBA':
                            img = img.convert('RGBA')
                        self.emojis[f] = img
                        count += 1
                    except: 
                        pass
        except Exception:
            pass
        
        return count

    def get_emoji(self, name):
        return self.emojis.get(name)

    def get_emoji_list(self):
        return sorted(list(self.emojis.keys()))
