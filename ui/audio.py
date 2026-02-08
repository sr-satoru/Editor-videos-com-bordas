import tkinter as tk
from tkinter import ttk, filedialog
from ui.componentes_custom import ToggleSwitch

class AudioSettings(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="Configurações de Áudio", padding=10)
        self.pack(fill="x", pady=10, padx=10)

        self.remove_audio_var = tk.BooleanVar()
        self.use_folder_audio_var = tk.BooleanVar()
        self.select_folder_audio_var = tk.BooleanVar()
        self.sync_duration_var = tk.BooleanVar()
        self.audio_folder_path = tk.StringVar()

        # Helper para criar linhas de switch
        def create_switch_row(parent, row, text, var):
            f = ttk.Frame(parent)
            f.grid(row=row, column=0, columnspan=3, sticky="w", pady=5, padx=5)
            ToggleSwitch(f, var).pack(side="left", padx=(0, 10))
            ttk.Label(f, text=text).pack(side="left")
            return f

        create_switch_row(self, 0, "Remover Áudio", self.remove_audio_var)
        create_switch_row(self, 1, "Usar áudios de forma aleatória", self.use_folder_audio_var)
        
        row_sel = ttk.Frame(self)
        row_sel.grid(row=2, column=0, columnspan=3, sticky="w", pady=5, padx=5)
        ToggleSwitch(row_sel, self.select_folder_audio_var).pack(side="left", padx=(0, 10))
        ttk.Label(row_sel, text="Usar áudios da pasta:").pack(side="left")
        
        ttk.Entry(self, textvariable=self.audio_folder_path, width=30, state="readonly").grid(row=3, column=0, columnspan=2, padx=(35, 5), sticky="we")
        ttk.Button(self, text="📁 Pasta", command=self.select_audio_folder, style="Accent.TButton", width=10).grid(row=3, column=2, padx=5)

        create_switch_row(self, 4, "Sincronizar duração do vídeo com o áudio", self.sync_duration_var)
        
        self.columnconfigure(0, weight=1)

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
