import tkinter as tk
from tkinter import ttk, colorchooser
from PIL import Image, ImageTk
from modules.video_editor import VideoEditor

class VideoBorders(ttk.LabelFrame):
    def __init__(self, parent, video_controls):
        super().__init__(parent, text="Bordas do Vídeo")
        self.pack(fill="x", pady=10)
        
        self.video_controls = video_controls
        self.editor = VideoEditor()
        self.preview_image_tk = None # Manter referência para não ser coletado pelo GC

        self.add_border = tk.BooleanVar()
        # Checkbutton parece redundante se temos o combobox com "Sem moldura", mas mantendo por compatibilidade ou lógica extra
        self.check_border = ttk.Checkbutton(self, text="Adicionar Borda ao Vídeo", variable=self.add_border, command=self.update_preview)
        self.check_border.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        ttk.Label(self, text="Estilo:").grid(row=0, column=1, padx=5)
        
        self.style_var = tk.StringVar(value="Sem moldura")
        self.style_combo = ttk.Combobox(self, textvariable=self.style_var, values=["Moldura", "Sem moldura", "black", "black + Moldura", "White", "Blur", "Blur + Moldura"], width=15)
        self.style_combo.grid(row=0, column=2)
        self.style_combo.bind("<<ComboboxSelected>>", self.update_preview)
        
        ttk.Label(self, text="Cor da Moldura:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.border_color = "#FFFFFF" # Default white
        self.color_btn = ttk.Button(self, text="Escolher", command=self.choose_color)
        self.color_btn.grid(row=1, column=1, padx=5)
        
        # Label para mostrar a cor selecionada (opcional, mas bom para UX)
        self.color_indicator = tk.Label(self, text="   ", bg=self.border_color, relief="solid")
        self.color_indicator.grid(row=1, column=2, padx=5)

    def choose_color(self):
        color = colorchooser.askcolor(title="Escolher cor da Moldura", color=self.border_color)
        if color[1]:
            self.border_color = color[1]
            self.color_indicator.config(bg=self.border_color)
            self.update_preview()

    def update_preview(self, event=None):
        video_path = self.video_controls.video_selector.current_video_path
        if not video_path:
            return

        style = self.style_var.get()
        # Se o check "Adicionar Borda" estiver desmarcado, talvez devêssemos ignorar? 
        # Mas o combobox tem "Sem moldura". Vamos assumir que o combobox manda.
        # Ou podemos usar o check para ligar/desligar o efeito.
        if not self.add_border.get() and event is None: 
            # Se foi chamado sem evento (ex: inicialização), e check tá off, não faz nada?
            # Mas se o usuário muda o combo, ele espera ver o resultado.
            # Vou forçar o check a ficar True se mudar o combo para algo que não seja "Sem moldura"?
            pass

        # Gerar frame processado
        frame = self.editor.generate_preview_image(video_path, style, self.border_color)
        
        if frame is not None:
            # Redimensionar para o canvas (360x640 - definido em preview.py)
            # O frame gerado pelo editor já deve estar em 1080x1920 (ou proporcional).
            # Precisamos redimensionar para caber no canvas.
            
            img = Image.fromarray(frame)
            img.thumbnail((360, 640), Image.Resampling.LANCZOS)
            
            self.preview_image_tk = ImageTk.PhotoImage(img)
            
            canvas = self.video_controls.video_selector.preview_canvas
            canvas.delete("all")
            canvas.create_image(0, 0, anchor="nw", image=self.preview_image_tk)

    def get_style(self):
        return self.style_var.get()

    def get_border_color(self):
        return self.border_color
