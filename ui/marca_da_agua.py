import tkinter as tk
from tkinter import ttk, colorchooser, filedialog
from ui.dialogo_marca_agua import DialogoMarcaAgua
from modules.logo_image_var import LogoManager
from ui.componentes_custom import ToggleSwitch

class WatermarkUI(ttk.LabelFrame):
    def __init__(self, parent, video_controls, subtitle_manager, emoji_manager, video_borders):
        super().__init__(parent, text=" Marcas D' àguas ", padding=10)
        self.pack(fill="x", pady=10, padx=10)
        
        self.video_controls = video_controls
        self.subtitle_manager = subtitle_manager
        self.emoji_manager = emoji_manager
        self.video_borders = video_borders
        
        self.logo_manager = LogoManager()
        
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

    def update_logo_position(self, x, y):
        self.logo_manager.update_position(x, y)
        self.update_preview()

    def update_logo_scale(self, scale):
        self.logo_manager.update_scale(scale)
        self.update_preview()

    def _setup_ui(self):
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
        
        row_sw = ttk.Frame(text_mark_frame)
        row_sw.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        self.sw_text_mark = ToggleSwitch(row_sw, self.add_text_mark_var, command=self.update_preview)
        self.sw_text_mark.pack(side="left", padx=(0, 10))
        ttk.Label(row_sw, text="Ativar marca d'água em texto", font=("Segoe UI", 9)).pack(side="left")
        
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

    def _browse_logo(self):
        path = filedialog.askopenfilename(
            title="Selecionar Logo",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.webp")]
        )
        if path:
            self.logo_path_var.set(path)
            if self.logo_manager.set_logo(path):
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
        
        # Adicionar estado da logo
        logo_state = self.logo_manager.get_state()
        state.update({
            "logo_path": logo_state["logo_path"],
            "logo_x": logo_state["x"],
            "logo_y": logo_state["y"],
            "logo_scale": logo_state["scale"],
            "logo_opacity": logo_state["opacity"]
        })
        
        state.update({
            "add_text_mark": self.add_text_mark_var.get(),
        })
        return state

    def set_state(self, state):
        self.logo_path_var.set(state.get("logo_path", ""))
        self.add_text_mark_var.set(state.get("add_text_mark", False))
        
        # Restaurar estado da logo
        self.logo_manager.set_state({
            "logo_path": state.get("logo_path", ""),
            "x": state.get("logo_x", 50),
            "y": state.get("logo_y", 50),
            "scale": state.get("logo_scale", 0.2),
            "opacity": state.get("logo_opacity", 1.0)
        })
        
        # Atualizar config de texto
        for key in self.text_config:
            if key in state:
                self.text_config[key] = state[key]
        
        self._update_ui_from_config()
