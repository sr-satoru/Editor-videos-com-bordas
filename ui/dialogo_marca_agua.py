import tkinter as tk
from tkinter import ttk, colorchooser

class DialogoMarcaAgua(tk.Toplevel):
    def __init__(self, parent, current_state, callback):
        super().__init__(parent)
        self.title("Editar Marca d'Água em Texto")
        self.geometry("420x380")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.callback = callback
        self.state = current_state.copy()
        
        self._setup_ui()

    def _setup_ui(self):
        main_frame = ttk.Frame(self, padding="20 20 20 20")
        main_frame.pack(fill="both", expand=True)

        # --- Seção de Texto ---
        ttk.Label(main_frame, text="Texto da Marca:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.text_var = tk.StringVar(value=self.state.get("text_mark", ""))
        self.entry_text = ttk.Entry(main_frame, textvariable=self.text_var, font=("Arial", 10))
        self.entry_text.grid(row=1, column=0, columnspan=2, sticky="we", pady=(0, 15))

        # --- Configurações de Fonte ---
        config_frame = ttk.LabelFrame(main_frame, text=" Estilo do Texto ", padding=10)
        config_frame.grid(row=2, column=0, columnspan=2, sticky="we", pady=(0, 15))

        # Fonte
        ttk.Label(config_frame, text="Fonte:").grid(row=0, column=0, sticky="w", pady=5)
        self.font_var = tk.StringVar(value=self.state.get("font", "Arial"))
        fonts = ["Arial", "Verdana", "Courier", "Times New Roman", "Impact", "Comic Sans MS", "Tahoma", "Georgia", "Helvetica", "Trebuchet MS"]
        self.combo_font = ttk.Combobox(config_frame, textvariable=self.font_var, values=fonts, state="readonly")
        self.combo_font.grid(row=0, column=1, sticky="we", pady=5, padx=(10, 0))

        # Tamanho
        ttk.Label(config_frame, text="Tamanho:").grid(row=1, column=0, sticky="w", pady=5)
        self.size_var = tk.IntVar(value=self.state.get("font_size", 30))
        self.spin_size = ttk.Spinbox(config_frame, from_=10, to=500, textvariable=self.size_var, width=10)
        self.spin_size.grid(row=1, column=1, sticky="w", pady=5, padx=(10, 0))

        # Opacidade
        ttk.Label(config_frame, text="Opacidade (0-100):").grid(row=2, column=0, sticky="w", pady=5)
        self.opacity_var = tk.IntVar(value=self.state.get("opacity", 100))
        self.spin_opacity = ttk.Spinbox(config_frame, from_=0, to=100, textvariable=self.opacity_var, width=10)
        self.spin_opacity.grid(row=2, column=1, sticky="w", pady=5, padx=(10, 0))

        # Cor
        ttk.Label(config_frame, text="Cor do Texto:").grid(row=3, column=0, sticky="w", pady=5)
        self.color_btn = tk.Button(
            config_frame, 
            bg=self.state.get("text_color", "#FFFFFF"), 
            width=12, 
            height=1,
            relief="groove",
            command=self._choose_color
        )
        self.color_btn.grid(row=3, column=1, sticky="w", pady=5, padx=(10, 0))

        # --- Botões de Ação ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky="e")
        
        self.btn_cancel = ttk.Button(btn_frame, text="Cancelar", command=self.destroy)
        self.btn_cancel.pack(side="right", padx=(5, 0))
        
        self.btn_save = ttk.Button(btn_frame, text="Salvar Alterações", command=self._save)
        self.btn_save.pack(side="right")

        main_frame.columnconfigure(1, weight=1)
        config_frame.columnconfigure(1, weight=1)

    def _choose_color(self):
        color = colorchooser.askcolor(title="Escolher cor da marca d'água", color=self.state.get("text_color", "#FFFFFF"))
        if color[1]:
            self.state["text_color"] = color[1]
            self.color_btn.config(bg=color[1])

    def _save(self):
        self.state["text_mark"] = self.text_var.get()
        self.state["font"] = self.font_var.get()
        try:
            self.state["font_size"] = int(self.size_var.get())
            self.state["opacity"] = max(0, min(100, int(self.opacity_var.get())))
        except ValueError:
            pass # Manter valores anteriores se inválidos
            
        self.callback(self.state)
        self.destroy()
