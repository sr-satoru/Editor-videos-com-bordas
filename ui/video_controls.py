import tkinter as tk
from tkinter import ttk
from modules.video_selector import VideoSelector

class VideoControls(ttk.LabelFrame):
    def __init__(self, parent, processar_pasta_var, preview_canvas):
        super().__init__(parent, text="Controles de Vídeo")
        self.pack(fill="x", pady=10)

        # Variável para controlar enhancement
        self.enable_enhancement = tk.BooleanVar(value=False)

        # Botão de selecionar vídeo
        self.video_selector = VideoSelector(self, preview_canvas)

        # Frame para checkboxes
        checkbox_frame = ttk.Frame(self)
        checkbox_frame.pack(side="left", padx=10, pady=10)

        # Checkbox de processar toda a pasta
        ttk.Checkbutton(
            checkbox_frame,
            text="Processar toda pasta",
            variable=processar_pasta_var
        ).pack(side="left", padx=(0, 10))

        # Checkbox de melhoramento de vídeo
        ttk.Checkbutton(
            checkbox_frame,
            text="🎨 Melhorar Qualidade (GFPGAN)",
            variable=self.enable_enhancement
        ).pack(side="left", padx=(0, 10))
    
    def get_state(self):
        return {
            "current_video_path": self.video_selector.current_video_path,
            "enable_enhancement": self.enable_enhancement.get()
        }

    def set_state(self, state):
        path = state.get("current_video_path")
        if path:
            self.video_selector.load_video(path)
        
        # Restaurar estado do enhancement
        enhancement = state.get("enable_enhancement", False)
        self.enable_enhancement.set(enhancement)
