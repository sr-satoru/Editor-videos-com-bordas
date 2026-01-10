import tkinter as tk
from tkinter import ttk, colorchooser

class ComponenteEstiloLegenda(ttk.LabelFrame):
    def __init__(self, parent, callbacks):
        """
        callbacks: dicionário com 'on_change'
        """
        super().__init__(parent, text="✏️ Estilo da Legenda")
        self.callbacks = callbacks
        
        # Variáveis de estado
        self.font_family = tk.StringVar(value="Arial Black")
        self.font_size = tk.IntVar(value=18)
        self.font_color = tk.StringVar(value="#FFFFFF")
        self.border_color = tk.StringVar(value="#000000")
        self.bg_color = tk.StringVar(value="")
        self.border_thickness = tk.IntVar(value=2)
        
        self.setup_ui()

    def setup_ui(self):
        self.indicators = {}
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        # Row 0: Fonte, Tamanho
        ttk.Label(controls_frame, text="Fonte:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        font_options = ["Arial", "Arial Black", "Helvetica", "Impact", "Verdana", "Comic Sans MS"]
        self.font_combo = ttk.Combobox(controls_frame, textvariable=self.font_family, values=font_options, width=15)
        self.font_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(controls_frame, text="Tamanho:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ttk.Spinbox(controls_frame, from_=10, to=200, textvariable=self.font_size, width=5).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        # Row 1: Cores
        self.criar_linha_cor(controls_frame, 1, "Cor Fonte:", self.font_color, "font")
        self.criar_linha_cor(controls_frame, 2, "Cor Borda:", self.border_color, "border")
        self.criar_linha_cor(controls_frame, 3, "Cor Fundo:", self.bg_color, "bg", allow_none=True)
        
        # Row 4: Espessura
        ttk.Label(controls_frame, text="Espessura Borda:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        ttk.Spinbox(controls_frame, from_=0, to=10, textvariable=self.border_thickness, width=5).grid(row=4, column=1, padx=5, pady=5, sticky="w")

    def criar_linha_cor(self, parent, row, label_text, var, key, allow_none=False):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, padx=5, pady=5, sticky="w")
        
        bg_color = var.get() if var.get() else "#f0f0f0"
        indicator = tk.Label(parent, width=3, bg=bg_color, relief="raised")
        indicator.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        self.indicators[key] = indicator
        
        def choose():
            color = colorchooser.askcolor(initialcolor=var.get() or "#FFFFFF")[1]
            if color:
                var.set(color)
                indicator.config(bg=color)
                if self.callbacks.get('on_change'): self.callbacks['on_change']()
            elif allow_none:
                var.set("")
                indicator.config(bg="#f0f0f0")
                if self.callbacks.get('on_change'): self.callbacks['on_change']()
                
        ttk.Button(parent, text="🎨", width=5, command=choose).grid(row=row, column=2, padx=5, pady=5, sticky="w")

    def get_estilo(self):
        return {
            "font": self.font_family.get(),
            "size": self.font_size.get(),
            "color": self.font_color.get(),
            "border": self.border_color.get(),
            "bg": self.bg_color.get(),
            "border_thickness": self.border_thickness.get()
        }
    def get_state(self):
        return self.get_estilo()

    def set_state(self, state):
        self.font_family.set(state.get("font", "Arial Black"))
        self.font_size.set(state.get("size", 18))
        self.font_color.set(state.get("color", "#FFFFFF"))
        self.border_color.set(state.get("border", "#000000"))
        self.bg_color.set(state.get("bg", ""))
        self.border_thickness.set(state.get("border_thickness", 2))
        
        # Atualizar indicadores visuais
        if hasattr(self, 'indicators'):
            self.indicators['font'].config(bg=self.font_color.get())
            self.indicators['border'].config(bg=self.border_color.get())
            self.indicators['bg'].config(bg=self.bg_color.get() if self.bg_color.get() else "#f0f0f0")
