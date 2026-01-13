import tkinter as tk
from tkinter import ttk, colorchooser

class DialogoEdicaoLegenda(tk.Toplevel):
    def __init__(self, parent, subtitle_idx, gerenciador_legendas, callback_salvar):
        super().__init__(parent)
        self.subtitle_idx = subtitle_idx
        self.gerenciador_legendas = gerenciador_legendas
        self.callback_salvar = callback_salvar
        
        sub = self.gerenciador_legendas.get_subtitles()[subtitle_idx]
        
        self.title(f"Editar Legenda #{sub['id']}")
        self.geometry("500x450")
        
        # Variáveis locais para o diálogo
        self.text_var = tk.StringVar(value=sub["text"])
        self.font_var = tk.StringVar(value=sub["font"])
        self.size_var = tk.IntVar(value=sub["size"])
        self.color_var = tk.StringVar(value=sub["color"])
        self.border_var = tk.StringVar(value=sub["border"])
        self.bg_var = tk.StringVar(value=sub["bg"])
        self.thick_var = tk.IntVar(value=sub["border_thickness"])
        
        self.setup_ui()

    def setup_ui(self):
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text="Editar Legenda", font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        fields_frame = tk.Frame(main_frame)
        fields_frame.pack(fill="both", expand=True)
        
        # Texto
        tk.Label(fields_frame, text="Texto:", font=("Arial", 10, "bold")).pack(anchor="w")
        tk.Entry(fields_frame, textvariable=self.text_var, font=("Arial", 10)).pack(fill="x", pady=(0, 10))
        
        # Fonte e Tamanho
        row2 = tk.Frame(fields_frame)
        row2.pack(fill="x", pady=(0, 10))
        tk.Label(row2, text="Fonte:", font=("Arial", 10, "bold")).pack(side="left")
        font_options = ["Arial", "Arial Black", "Helvetica", "Impact", "Verdana", "Comic Sans MS"]
        ttk.Combobox(row2, textvariable=self.font_var, values=font_options, width=15).pack(side="left", padx=5)
        tk.Label(row2, text="Tamanho:", font=("Arial", 10, "bold")).pack(side="left", padx=(10, 0))
        tk.Spinbox(row2, from_=1, to=200, textvariable=self.size_var, width=5).pack(side="left", padx=5)
        
        # Cores
        self.criar_linha_cor(fields_frame, "Cor Texto:", self.color_var)
        self.criar_linha_cor(fields_frame, "Cor Borda:", self.border_var)
        self.criar_linha_cor(fields_frame, "Cor Fundo:", self.bg_var, allow_none=True)

        # Espessura
        row6 = tk.Frame(fields_frame)
        row6.pack(fill="x", pady=5)
        tk.Label(row6, text="Espessura Borda:", font=("Arial", 10, "bold")).pack(side="left")
        tk.Spinbox(row6, from_=0, to=10, textvariable=self.thick_var, width=5).pack(side="left", padx=5)
        
        # Botões
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(20, 0))
        tk.Button(btn_frame, text="Salvar", command=self.save, bg="green", fg="white", width=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancelar", command=self.destroy, bg="red", fg="white", width=10).pack(side="left", padx=5)

    def criar_linha_cor(self, parent, label_text, var, allow_none=False):
        row = tk.Frame(parent)
        row.pack(fill="x", pady=5)
        tk.Label(row, text=label_text, font=("Arial", 10, "bold")).pack(side="left")
        
        bg_color = var.get() if var.get() else "#f0f0f0"
        indicator = tk.Label(row, bg=bg_color, width=3, relief="raised")
        indicator.pack(side="left", padx=5)
        
        def choose():
            color = colorchooser.askcolor(initialcolor=var.get() or "#FFFFFF")[1]
            if color:
                var.set(color)
                indicator.config(bg=color)
            elif allow_none:
                var.set("")
                indicator.config(bg="#f0f0f0")
                
        tk.Button(row, text="🎨", command=choose).pack(side="left")

    def save(self):
        self.gerenciador_legendas.update_subtitle(
            self.subtitle_idx,
            text=self.text_var.get(),
            font=self.font_var.get(),
            size=self.size_var.get(),
            color=self.color_var.get(),
            border=self.border_var.get(),
            bg=self.bg_var.get(),
            border_thickness=self.thick_var.get()
        )
        if self.callback_salvar:
            self.callback_salvar()
        self.destroy()
