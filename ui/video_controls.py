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

        # Frame de Controles de Playback
        playback_frame = ttk.Frame(self)
        playback_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Botão Play/Pause
        self.play_btn = ttk.Button(playback_frame, text="▶", command=self.toggle_play, width=5)
        self.play_btn.pack(side="left", padx=(0, 5))

        # Slider de Tempo
        self.seek_var = tk.DoubleVar()
        self.seek_slider = ttk.Scale(
            playback_frame, 
            from_=0, 
            to=100, 
            orient="horizontal", 
            variable=self.seek_var,
            command=self.on_seek
        )
        self.seek_slider.pack(side="left", fill="x", expand=True, padx=5)
        
        # Label de Tempo
        self.time_label = ttk.Label(playback_frame, text="00:00 / 00:00", font=("Arial", 9))
        self.time_label.pack(side="left", padx=(5, 0))

        # Configurar callbacks do VideoSelector
        self.video_selector.on_duration_changed = self.update_duration
        self.video_selector.on_time_changed = self.update_time_ui
        self.video_selector.on_playback_status_changed = self.update_play_btn

        # Frame para checkboxes (Mover para baixo ou manter?) Manter abaixo dos controles
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
        
        self.duration = 0
        self.is_seeking = False

    def toggle_play(self):
        self.video_selector.toggle_play()

    def on_seek(self, value):
        # Evitar conflito se estiver atualizando automaticamente
        if not self.is_seeking:
             self.video_selector.seek(float(value))

    def update_duration(self, duration):
        self.duration = duration
        self.seek_slider.config(to=duration)
        self.update_time_label(0, duration)

    def update_time_ui(self, current_time):
        # Atualiza slider sem disparar o command (se possível, ou flag)
        self.is_seeking = True
        self.seek_var.set(current_time)
        self.is_seeking = False
        
        self.update_time_label(current_time, self.duration)

    def update_play_btn(self, is_playing):
        self.play_btn.config(text="⏸" if is_playing else "▶")

    def update_time_label(self, current, total):
        def fmt(s):
            m = int(s // 60)
            s = int(s % 60)
            return f"{m:02d}:{s:02d}"
        self.time_label.config(text=f"{fmt(current)} / {fmt(total)}")

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
