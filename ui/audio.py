import tkinter as tk
from tkinter import ttk, filedialog

class AudioSettings(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="Configurações de Áudio")
        self.pack(fill="x", pady=10)

        self.remove_audio_var = tk.BooleanVar()
        self.use_folder_audio_var = tk.BooleanVar()
        self.select_folder_audio_var = tk.BooleanVar()
        self.sync_duration_var = tk.BooleanVar()
        self.audio_folder_path = tk.StringVar()

        ttk.Checkbutton(self, text="Remover Áudio", variable=self.remove_audio_var).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ttk.Checkbutton(self, text="Usar audios de forma aleatoria", variable=self.use_folder_audio_var).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        ttk.Checkbutton(self, text="Usar áudios da pasta selecionada", variable=self.select_folder_audio_var).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        ttk.Checkbutton(self, text="Sincronizar duração do vídeo com o áudio", variable=self.sync_duration_var).grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        ttk.Entry(self, textvariable=self.audio_folder_path, width=40, state="readonly").grid(row=2, column=1, padx=5)
        ttk.Button(self, text="📁 Selecionar Pasta", command=self.select_audio_folder, style="Accent.TButton").grid(row=2, column=2, padx=5)

    def select_audio_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.audio_folder_path.set(folder)
    def get_state(self):
        return {
            "remove_audio": self.remove_audio_var.get(),
            "use_folder_audio": self.use_folder_audio_var.get(),
            "select_folder_audio": self.select_folder_audio_var.get(),
            "sync_duration": self.sync_duration_var.get(),
            "audio_folder_path": self.audio_folder_path.get()
        }

    def set_state(self, state):
        self.remove_audio_var.set(state.get("remove_audio", False))
        self.use_folder_audio_var.set(state.get("use_folder_audio", False))
        self.select_folder_audio_var.set(state.get("select_folder_audio", False))
        self.sync_duration_var.set(state.get("sync_duration", False))
        self.audio_folder_path.set(state.get("audio_folder_path", ""))
