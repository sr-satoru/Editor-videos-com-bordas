import tkinter as tk
from tkinter import ttk, filedialog

class EmojiSystem(ttk.LabelFrame):
    def __init__(self, parent, emoji_manager, subtitles_ui):
        super().__init__(parent, text="😊 Sistema de Emojis")
        self.pack(fill="x", pady=10)
        
        self.emoji_manager = emoji_manager
        self.subtitles_ui = subtitles_ui

        self.emoji_folder = tk.StringVar()
        self.emoji_scale = tk.DoubleVar(value=1.0)

        controls = ttk.Frame(self)
        controls.pack(fill="x", padx=10, pady=10)

        ttk.Label(controls, text="Pasta de Emojis:").grid(row=0, column=0, sticky="w")
        ttk.Entry(controls, textvariable=self.emoji_folder, width=40, state="readonly").grid(row=0, column=1, padx=5)
        ttk.Button(controls, text="📁 Selecionar Pasta", command=self.select_emoji_folder).grid(row=0, column=2, padx=5)

        # Canvas horizontal para emojis
        canvas_frame = ttk.Frame(self)
        canvas_frame.pack(fill="x", padx=10, pady=5)

        self.emoji_canvas = tk.Canvas(canvas_frame, height=80, bg="white", relief="sunken", bd=1)
        self.emoji_canvas.pack(side="left", fill="both", expand=True)

        emoji_scroll = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.emoji_canvas.xview)
        emoji_scroll.pack(side="bottom", fill="x")
        self.emoji_canvas.configure(xscrollcommand=emoji_scroll.set)

        self.emoji_inner_frame = ttk.Frame(self.emoji_canvas)
        self.emoji_canvas.create_window((0, 0), window=self.emoji_inner_frame, anchor="nw")
        self.emoji_inner_frame.bind("<Configure>", lambda e: self.emoji_canvas.configure(scrollregion=self.emoji_canvas.bbox("all")))

        # Escala e botão
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(btn_frame, text="Escala do Emoji:").grid(row=0, column=0, sticky="w")
        ttk.Scale(btn_frame, from_=0.5, to=2.0, variable=self.emoji_scale, orient="horizontal", length=150).grid(row=0, column=1, padx=5)
        # Botão removido pois clicar no emoji já adiciona
        # ttk.Button(btn_frame, text="➕ Adicionar Emoji ao Texto", command=self.add_emoji_to_text).grid(row=0, column=2, padx=5)

    def select_emoji_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.emoji_folder.set(folder)
            count = self.emoji_manager.load_emojis(folder)
            self.populate_emojis()
            print(f"Carregados {count} emojis.")

    def populate_emojis(self):
        # Limpar frame anterior
        for widget in self.emoji_inner_frame.winfo_children():
            widget.destroy()
            
        # Adicionar botões
        for filename, data in self.emoji_manager.emoji_images.items():
            btn = tk.Button(self.emoji_inner_frame, image=data['display_image'], 
                            command=lambda f=filename: self.insert_emoji(f))
            btn.pack(side="left", padx=2, pady=2)
            
    def insert_emoji(self, filename):
        tag = f"[EMOJI:{filename}]"
        self.subtitles_ui.text_entry.insert("insert", tag)
        self.subtitles_ui.text_entry.focus()
