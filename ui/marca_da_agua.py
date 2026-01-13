import tkinter as tk
from tkinter import ttk, colorchooser, filedialog
from ui.dialogo_marca_agua import DialogoMarcaAgua

class WatermarkUI(ttk.LabelFrame):
    def __init__(self, parent, video_controls, subtitle_manager, emoji_manager, video_borders):
        super().__init__(parent, text=" Marcas D' àguas ", padding=10)
        self.pack(fill="x", pady=10, padx=10)
        
        self.video_controls = video_controls
        self.subtitle_manager = subtitle_manager
        self.emoji_manager = emoji_manager
        self.video_borders = video_borders
        
        # Estado interno para configurações avançadas
        self.text_config = {
            "text_mark": "",
            "font": "Arial",
            "font_size": 30,
            "opacity": 100,
            "text_color": "#FFFFFF",
            "x": 135,
            "y": 400
        }
        
        self._setup_ui()

    def update_position(self, x, y):
        """Atualiza a posição da marca d'água (chamado pelo drag-and-drop)"""
        self.text_config["x"] = x
        self.text_config["y"] = y
        # Não precisa atualizar a UI inteira, apenas o preview
        self.update_preview()

    def _setup_ui(self):
        # --- Seção: Logo de Finalização ---
        video_frame = ttk.LabelFrame(self, text=" Logo de Finalização ", padding=10)
        video_frame.pack(fill="x", pady=(0, 10))
        
        self.add_final_video_var = tk.BooleanVar()
        self.check_final_video = ttk.Checkbutton(
            video_frame, text="Adicionar um vídeo final ao projeto", variable=self.add_final_video_var, command=self.update_preview
        )
        self.check_final_video.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        
        self.video_path_var = tk.StringVar()
        self.entry_video_path = ttk.Entry(video_frame, textvariable=self.video_path_var)
        self.entry_video_path.grid(row=1, column=0, sticky="we", padx=(0, 5))
        self.entry_video_path.bind("<KeyRelease>", self.update_preview)
        
        self.btn_browse_video = ttk.Button(video_frame, text="Procurar", width=10, command=self._browse_video)
        self.btn_browse_video.grid(row=1, column=1, sticky="w")
        video_frame.columnconfigure(0, weight=1)

        # --- Seção: Logo ---
        logo_frame = ttk.LabelFrame(self, text=" Logo / Imagem ", padding=10)
        logo_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(logo_frame, text="Caminho da Logo:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.logo_path_var = tk.StringVar()
        self.entry_logo_path = ttk.Entry(logo_frame, textvariable=self.logo_path_var)
        self.entry_logo_path.grid(row=1, column=0, sticky="we", padx=(0, 5))
        self.entry_logo_path.bind("<KeyRelease>", self.update_preview)
        
        self.btn_browse_logo = ttk.Button(logo_frame, text="Procurar", width=10, command=self._browse_logo)
        self.btn_browse_logo.grid(row=1, column=1, sticky="w")
        logo_frame.columnconfigure(0, weight=1)

        # --- Seção: Marca d'Água em Texto ---
        text_mark_frame = ttk.LabelFrame(self, text=" Marca d'Água em Texto ", padding=10)
        text_mark_frame.pack(fill="x")
        
        self.add_text_mark_var = tk.BooleanVar()
        self.check_text_mark = ttk.Checkbutton(
            text_mark_frame, text="Ativar marca d'água em texto", variable=self.add_text_mark_var, command=self.update_preview
        )
        self.check_text_mark.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        
        input_frame = ttk.Frame(text_mark_frame)
        input_frame.grid(row=1, column=0, columnspan=2, sticky="we")
        
        self.entry_text_mark_display = ttk.Entry(input_frame)
        self.entry_text_mark_display.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry_text_mark_display.bind("<KeyRelease>", self._on_text_entry_change)
        
        self.btn_edit_text = ttk.Button(input_frame, text="Personalizar", command=self._open_edit_dialog)
        self.btn_edit_text.pack(side="right")

        # Resumo do Estilo
        self.style_summary_label = ttk.Label(
            text_mark_frame, 
            text="Estilo: Arial, 30px, 100% opacidade",
            font=("Arial", 9, "italic"),
            foreground="gray"
        )
        self.style_summary_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        text_mark_frame.columnconfigure(0, weight=1)

        self._update_ui_from_config()

    def _on_text_entry_change(self, event=None):
        self.text_config["text_mark"] = self.entry_text_mark_display.get()
        self.update_preview()

    def _browse_video(self):
        path = filedialog.askopenfilename(
            title="Selecionar Vídeo Final",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")]
        )
        if path:
            self.video_path_var.set(path)
            self.update_preview()

    def _browse_logo(self):
        path = filedialog.askopenfilename(
            title="Selecionar Logo",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.webp")]
        )
        if path:
            self.logo_path_var.set(path)
            self.update_preview()

    def _open_edit_dialog(self):
        DialogoMarcaAgua(self, self.text_config, self._update_config)

    def _update_config(self, new_config):
        self.text_config = new_config
        self._update_ui_from_config()
        self.update_preview()

    def _update_ui_from_config(self):
        # Sincronizar entry de texto
        self.entry_text_mark_display.delete(0, tk.END)
        self.entry_text_mark_display.insert(0, self.text_config["text_mark"])
        
        # Atualizar resumo
        summary = f"Estilo: {self.text_config['font']}, {self.text_config['font_size']}px, {self.text_config['opacity']}% opacidade"
        self.style_summary_label.config(text=summary)

    def update_preview(self, event=None):
        """Dispara a atualização do preview global"""
        # Como o Subtitles é o orquestrador do preview (por causa do drag-and-drop),
        # vamos tentar chamar o update_preview dele se ele existir.
        # Caso contrário, podemos ter uma lógica centralizada.
        
        # No main_ui.py, as abas têm referências a todos os módulos.
        # Vamos assumir que o 'subtitles' na tabs_data é o orquestrador.
        # Mas aqui não temos acesso direto ao tabs_data da EditorUI.
        
        # Uma solução comum é passar o callback de update_preview no init.
        # Mas vamos tentar encontrar o componente de legendas via parent se necessário,
        # ou simplesmente disparar um evento que o main_ui escuta.
        
        # Por enquanto, vamos tentar chamar o update_preview do video_borders 
        # ou do subtitles se tivermos a referência.
        
        # Se tivermos a referência do subtitles_ui (que passaremos no main_ui):
        if hasattr(self, 'subtitles_ui') and self.subtitles_ui:
            self.subtitles_ui.update_preview()
        elif self.video_borders:
            # O VideoBorders também sabe atualizar o preview
            self.video_borders.update_preview()

    def get_state(self):
        state = self.text_config.copy()
        state.update({
            "add_final_video": self.add_final_video_var.get(),
            "video_path": self.video_path_var.get(),
            "logo_path": self.logo_path_var.get(),
            "add_text_mark": self.add_text_mark_var.get(),
        })
        return state

    def set_state(self, state):
        self.add_final_video_var.set(state.get("add_final_video", False))
        self.video_path_var.set(state.get("video_path", ""))
        self.logo_path_var.set(state.get("logo_path", ""))
        self.add_text_mark_var.set(state.get("add_text_mark", False))
        
        # Atualizar config de texto
        for key in self.text_config:
            if key in state:
                self.text_config[key] = state[key]
        
        self._update_ui_from_config()
