import tkinter as tk
from tkinter import ttk, colorchooser
from PIL import Image, ImageTk
from modules.video_editor import VideoEditor
from ui.componentes_custom import ToggleSwitch

class VideoBorders(ttk.LabelFrame):
    def __init__(self, parent, video_controls, subtitle_manager, emoji_manager):
        super().__init__(parent, text="Bordas do Vídeo", padding=10)
        self.pack(fill="x", pady=10, padx=10)
        
        self.video_controls = video_controls
        self.subtitle_manager = subtitle_manager
        self.emoji_manager = emoji_manager
        self.editor = VideoEditor()
        self.preview_image_tk = None

        self.add_border = tk.BooleanVar()
        
        # Row 0: Switch + Style
        row0 = ttk.Frame(self)
        row0.grid(row=0, column=0, columnspan=5, sticky="w", pady=5)
        
        self.sw_border = ToggleSwitch(row0, self.add_border, command=self.update_preview)
        self.sw_border.pack(side="left", padx=(0, 10))
        ttk.Label(row0, text="Ativar Moldura/Estilo", font=("Segoe UI", 9)).pack(side="left", padx=(0, 20))

        ttk.Label(row0, text="Estilo:").pack(side="left", padx=5)
        self.style_var = tk.StringVar(value="Sem moldura")
        self.style_combo = ttk.Combobox(row0, textvariable=self.style_var, values=["Moldura", "Sem moldura", "black", "black + Moldura", "White", "Blur", "Blur + Moldura"], width=15)
        self.style_combo.pack(side="left", padx=5)
        self.style_combo.bind("<<ComboboxSelected>>", self.update_preview)
        self.style_combo.bind("<<ComboboxSelected>>", self.update_preview)
        
        ttk.Label(self, text="Cor da Moldura:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.border_color = "#FFFFFF" # Default white
        self.color_btn = ttk.Button(self, text="Escolher", command=self.choose_color)
        self.color_btn.grid(row=1, column=1, padx=5)
        
        # Label para mostrar a cor selecionada (opcional, mas bom para UX)
        self.color_indicator = tk.Label(self, text="   ", bg=self.border_color, relief="solid")
        self.color_indicator.ignore_theme = True
        self.color_indicator.grid(row=1, column=2, padx=5)

        ttk.Label(self, text="Tamanho:").grid(row=1, column=3, padx=5, sticky="w")
        self.border_size_var = tk.IntVar(value=14)
        self.border_size_spin = ttk.Spinbox(self, from_=10, to=200, textvariable=self.border_size_var, width=5, command=self.update_preview)
        self.border_size_spin.grid(row=1, column=4, padx=5, sticky="w")
        self.border_size_spin.bind("<Return>", self.update_preview)

        self.video_w_ratio_var = tk.DoubleVar(value=0.78)
        self.video_h_ratio_var = tk.DoubleVar(value=0.70)
        
        # Dica para UX
        ttk.Label(self, text="💡 Dica: Arraste o canto amarelo no preview para redimensionar o vídeo.", 
                  font=("Segoe UI", 8, "italic"), foreground="gray").grid(row=2, column=0, columnspan=5, pady=(5, 0))

    def choose_color(self):
        color = colorchooser.askcolor(title="Escolher cor da Moldura", color=self.border_color)
        if color[1]:
            self.border_color = color[1]
            self.color_indicator.config(bg=self.border_color)
            self.update_preview()

    def get_effective_style(self):
        """Retorna o estilo efetivo considerando o checkbox"""
        if not self.add_border.get():
            return "Sem moldura"
        return self.style_var.get()

    def update_preview(self, event=None):
        video_path = self.video_controls.video_selector.current_video_path
        if not video_path:
            return

        style = self.get_effective_style()

        # Atualizar proporções dinâmicas no editor
        self.editor.video_width_ratio = self.video_w_ratio_var.get()
        self.editor.video_height_ratio = self.video_h_ratio_var.get()

        # Gerar frame processado
        frame = self.editor.generate_preview_image(
            video_path, 
            style, 
            self.border_color,
            subtitles=self.subtitle_manager.get_subtitles(),
            emoji_manager=self.emoji_manager,
            border_size_preview=self.border_size_var.get()
        )
        
        if frame is not None:
            # Redimensionar para o canvas (360x640 - definido em preview.py)
            # O frame gerado pelo editor já deve estar em 1080x1920 (ou proporcional).
            # Precisamos redimensionar para caber no canvas.
            
            img = Image.fromarray(frame)
            img.thumbnail((360, 640), Image.Resampling.LANCZOS)
            
            self.preview_image_tk = ImageTk.PhotoImage(img)
            
            canvas = self.video_controls.video_selector.preview_canvas
            canvas.delete("all")
            
            # Centralizar
            c_width = canvas.winfo_width()
            c_height = canvas.winfo_height()
            if c_width < 10: c_width = 360 # Fallback se canvas não foi desenhado ainda
            if c_height < 10: c_height = 640
            
            x = c_width // 2
            y = c_height // 2
            
            canvas.create_image(x, y, anchor="center", image=self.preview_image_tk)

    def get_style(self):
        return self.style_var.get()

    def get_border_color(self):
        return self.border_color
    def get_state(self):
        return {
            "add_border": self.add_border.get(),
            "style": self.style_var.get(),
            "border_color": self.border_color,
            "border_size": self.border_size_var.get(),
            "video_w_ratio": self.video_w_ratio_var.get(),
            "video_h_ratio": self.video_h_ratio_var.get()
        }

    def set_state(self, state):
        self.add_border.set(state.get("add_border", False))
        self.style_var.set(state.get("style", "Sem moldura"))
        self.border_color = state.get("border_color", "#FFFFFF")
        self.color_indicator.config(bg=self.border_color)
        self.border_size_var.set(state.get("border_size", 14))
        self.video_w_ratio_var.set(state.get("video_w_ratio", 0.78))
        self.video_h_ratio_var.set(state.get("video_h_ratio", 0.70))
        self.update_preview()
