import tkinter as tk
from tkinter import ttk, filedialog
import os
from ui.componentes_custom import ToggleSwitch

class MesclagemFront(ttk.LabelFrame):
    def __init__(self, parent, video_controls):
        super().__init__(parent, text=" Finalizadores (Mesclagem & CTA) ", padding=10)
        self.pack(fill="x", pady=10, padx=10)
        
        self.video_controls = video_controls
        self.setup_ui()

    def setup_ui(self):
        # --- Opções de Legenda ---
        config_frame = ttk.Frame(self)
        config_frame.pack(fill="x", pady=(0, 10))
        
        self.hide_subtitles_var = tk.BooleanVar(value=False)
        
        # Switch Row
        row_subs = ttk.Frame(config_frame)
        row_subs.pack(fill="x", pady=2)
        
        self.sw_hide_subs = ToggleSwitch(row_subs, self.hide_subtitles_var)
        self.sw_hide_subs.pack(side="left", padx=(0, 10))
        ttk.Label(row_subs, text="🚫 Ocultar Legendas no Vídeo Principal", font=("Segoe UI", 9)).pack(side="left")

        # --- Vídeo de Mesclagem (Intermediário) ---
        merge_frame = ttk.LabelFrame(self, text=" Vídeo de Mesclagem (Intermediário) ", padding=10)
        merge_frame.pack(fill="x", pady=5)
        
        row_merge_sw = ttk.Frame(merge_frame)
        row_merge_sw.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        self.use_merge_var = tk.BooleanVar(value=False)
        self.sw_merge = ToggleSwitch(row_merge_sw, self.use_merge_var)
        self.sw_merge.pack(side="left", padx=(0, 10))
        ttk.Label(row_merge_sw, text="Ativar Mesclagem").pack(side="left")
        
        self.merge_path_var = tk.StringVar()
        ttk.Entry(merge_frame, textvariable=self.merge_path_var).grid(row=1, column=0, sticky="we", padx=(0, 5))
        ttk.Button(merge_frame, text="Procurar", width=10, command=self._browse_merge).grid(row=1, column=1, sticky="w")
        merge_frame.columnconfigure(0, weight=1)

        # --- Vídeo de CTA (Final) ---
        cta_frame = ttk.LabelFrame(self, text=" Vídeo de CTA (Chamada para Ação) ", padding=10)
        cta_frame.pack(fill="x", pady=5)
        
        row_cta_sw = ttk.Frame(cta_frame)
        row_cta_sw.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        self.use_cta_var = tk.BooleanVar(value=False)
        self.sw_cta = ToggleSwitch(row_cta_sw, self.use_cta_var)
        self.sw_cta.pack(side="left", padx=(0, 10))
        ttk.Label(row_cta_sw, text="Ativar Vídeo CTA").pack(side="left")
        
        self.cta_path_var = tk.StringVar()
        ttk.Entry(cta_frame, textvariable=self.cta_path_var).grid(row=1, column=0, sticky="we", padx=(0, 5))
        ttk.Button(cta_frame, text="Procurar", width=10, command=self._browse_cta).grid(row=1, column=1, sticky="w")
        cta_frame.columnconfigure(0, weight=1)

    def _browse_merge(self):
        path = filedialog.askopenfilename(title="Selecionar Vídeo de Mesclagem", filetypes=[("Video", "*.mp4 *.mov *.avi *.mkv")])
        if path: self.merge_path_var.set(path)

    def _browse_cta(self):
        path = filedialog.askopenfilename(title="Selecionar Vídeo de CTA", filetypes=[("Video", "*.mp4 *.mov *.avi *.mkv")])
        if path: self.cta_path_var.set(path)

    def get_state(self):
        return {
            "hide_subtitles": self.hide_subtitles_var.get(),
            "use_merge": self.use_merge_var.get(),
            "merge_path": self.merge_path_var.get(),
            "use_cta": self.use_cta_var.get(),
            "cta_path": self.cta_path_var.get()
        }

    def set_state(self, state):
        self.hide_subtitles_var.set(state.get("hide_subtitles", False))
        self.use_merge_var.set(state.get("use_merge", False))
        self.merge_path_var.set(state.get("merge_path", ""))
        self.use_cta_var.set(state.get("use_cta", False))
        self.cta_path_var.set(state.get("cta_path", ""))
