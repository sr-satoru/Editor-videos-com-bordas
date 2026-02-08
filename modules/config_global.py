import json
import os

CONFIG_FILE = "global_settings.json"

DEFAULT_SETTINGS = {
    "num_threads": 4,
    "parallel_jobs": 1,
    "global_subtitles_style": False,  # Se True, ignora estilo de cada aba e usa o padrão
    "default_output_path": "",
    "export_format": "mp4",
}

class GlobalConfig:
    def __init__(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self):
        """Carrega configurações do JSON com tratamento de erro e fallbacks"""
        if not os.path.exists(CONFIG_FILE):
            self.save()
            return

        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Merge seguro: Mantém chaves padrão se não existirem no arquivo
            for key, value in DEFAULT_SETTINGS.items():
                if key in data:
                    self.settings[key] = data[key]
                else:
                    self.settings[key] = value
                    
            # Validação específica de caminhos
            if "default_output_path" in self.settings:
                path = self.settings["default_output_path"]
                if path and not os.path.exists(path):
                    print(f"Aviso: Caminho de saída '{path}' inválido no JSON. Resetando para vazio.")
                    self.settings["default_output_path"] = ""

        except (json.JSONDecodeError, IOError) as e:
            print(f"Erro ao carregar configurações: {e}. Usando padrões.")
            self.settings = DEFAULT_SETTINGS.copy()

    def save(self):
        """Salva as configurações atuais no JSON"""
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")

    def get(self, key):
        """Retorna um valor com fallback para o padrão se a chave sumir"""
        return self.settings.get(key, DEFAULT_SETTINGS.get(key))

    def set(self, key, value):
        """Atualiza uma configuração e salva"""
        self.settings[key] = value
        self.save()

# Instância Singleton
global_config = GlobalConfig()
