import tkinter as tk
from tkinter import ttk
from modules.video_selector import VideoSelector

class VideoControls(ttk.LabelFrame):
    def __init__(self, parent, processar_pasta_var, preview_canvas):
        super().__init__(parent, text="Controles de Vídeo")
        self.pack(fill="x", pady=10)

        # Botão de selecionar vídeo
        self.video_selector = VideoSelector(self, preview_canvas)

        # Checkbox de processar toda a pasta
        ttk.Checkbutton(
            self,
            text="Processar toda pasta",
            variable=processar_pasta_var
        ).pack(side="left", padx=10, pady=10)
    def get_state(self):
        return {
            "current_video_path": self.video_selector.current_video_path
        }

    def set_state(self, state):
        path = state.get("current_video_path")
        if path:
            self.video_selector.load_video(path)
