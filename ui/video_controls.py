import tkinter as tk
from tkinter import ttk
from modules.video_selector import VideoSelector
from ui.componentes_custom import ToggleSwitch

class VideoControls(ttk.LabelFrame):
    def __init__(self, parent, processar_pasta_var, preview_canvas):
        super().__init__(parent, text="Controles de Vídeo")
        self.pack(fill="x", pady=5, padx=10)

        # Variável para controlar enhancement
        self.enable_enhancement = tk.BooleanVar(value=False)

        # Botão de selecionar vídeo
        self.video_selector = VideoSelector(self, preview_canvas)
        self.video_selector.on_duration_changed = self.update_duration
        self.video_selector.on_time_changed = self.update_time_ui
        self.video_selector.on_playback_status_changed = self.update_play_btn

        # Frame de Controles de Playback

        # Frame de Controles de Playback
        playback_frame = ttk.Frame(self)
        playback_frame.pack(fill="x", padx=10, pady=(5, 5))

        # Botão Play/Pause (Estilo Ícone)
        self.play_btn = ttk.Button(playback_frame, text="▶", command=self.toggle_play, width=3, style="Icon.TButton")
        self.play_btn.pack(side="left", padx=(0, 10))

        # Slider de Tempo
        self.seek_var = tk.DoubleVar()
        self.seek_slider = ttk.Scale(
            playback_frame, 
            from_=0, 
            to=100, 
            orient="horizontal", 
            variable=self.seek_var
        )
        self.seek_slider.pack(side="left", fill="x", expand=True, padx=5)
        
        # Eventos para melhorar o feedback do slider
        self.is_dragging_slider = False
        self.seek_slider.bind("<Button-1>", self.on_slider_press)
        self.seek_slider.bind("<ButtonRelease-1>", self.on_slider_release)
        self.seek_slider.bind("<B1-Motion>", self.on_slider_drag)
        
        # Label de Tempo
        self.time_label = ttk.Label(playback_frame, text="00:00 / 00:00", font=("Segoe UI", 9))
        self.time_label.pack(side="left", padx=(5, 0))

        # --- Linha de Switches ---
        switch_container = ttk.Frame(self)
        switch_container.pack(fill="x", pady=(0, 5))

        # Pasta
        row_folder = ttk.Frame(switch_container)
        row_folder.pack(side="left", padx=(0, 20))
        ToggleSwitch(row_folder, processar_pasta_var).pack(side="left", padx=(0, 8))
        ttk.Label(row_folder, text="Processar Pasta", font=("Segoe UI", 9)).pack(side="left")

        # Enhancement
        row_enh = ttk.Frame(switch_container)
        row_enh.pack(side="left")
        ToggleSwitch(row_enh, self.enable_enhancement).pack(side="left", padx=(0, 8))
        ttk.Label(row_enh, text="Melhorar Qualidade", font=("Segoe UI", 9)).pack(side="left")
        
        self.duration = 0
        self.is_seeking = False

    def on_slider_press(self, event):
        self.is_dragging_slider = True

    def on_slider_drag(self, event):
        # Atualizar frame em tempo real durante o arraste
        try:
            val = float(self.seek_slider.get())
            self.video_selector.show_frame(val)
            self.update_time_label(val, self.duration)
        except: pass

    def on_slider_release(self, event):
        self.is_dragging_slider = False
        try:
            val = float(self.seek_slider.get())
            self.video_selector.seek(val)
        except: pass

    def toggle_play(self):
        self.video_selector.toggle_play()

    def on_seek(self, value):
        # Este método agora é menos crítico, mas mantemos para compatibilidade
        if not self.is_seeking and not self.is_dragging_slider:
             self.video_selector.seek(float(value))

    def update_duration(self, duration):
        self.duration = duration
        self.seek_slider.config(to=duration)
        self.update_time_label(0, duration)

    def update_time_ui(self, current_time):
        # Se estiver arrastando manualmente, não atualiza via automação para evitar jitter
        if self.is_dragging_slider:
            return
            
        # Atualiza slider sem disparar o command logic
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


        return {
            "current_video_path": self.video_selector.current_video_path,
            "enable_enhancement": self.enable_enhancement.get()
        }

    def set_state(self, state):
        import os
        
        path = state.get("current_video_path")
        enhancement = state.get("enable_enhancement", False)
        self.enable_enhancement.set(enhancement)
        
        if path:
            # Verificar se o arquivo existe
            if os.path.exists(path):
                self.video_selector.load_video(path)
                return {"success": True, "video_path": path}
            else:
                # Vídeo não encontrado - retornar erro mas não falhar
                return {"success": False, "video_path": path, "error": "Vídeo não encontrado"}
        
        return {"success": True, "video_path": ""}

