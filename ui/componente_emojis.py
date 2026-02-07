import os
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import ImageTk

class ComponenteEmojis(ttk.LabelFrame):
    emoji_folder_path = None # Inicialização no nível da classe para segurança extra

    def __init__(self, parent, emoji_manager, callback_inserir):
        super().__init__(parent, text="😊 Emojis")
        self.emoji_manager = emoji_manager
        self.callback_inserir = callback_inserir
        
        self.emoji_scale = tk.DoubleVar(value=1.0)
        self.selected_emoji_name = None
        self.emoji_folder_path = None
        
        self.setup_ui()
        
        # Tenta detectar automaticamente a pasta de emojis
        self.auto_load_emojis()

    def auto_load_emojis(self):
        """Tenta carregar emojis automaticamente da pasta detectada"""
        auto_folder = self.emoji_manager.auto_detect_folder()
        if auto_folder:
            self.emoji_folder_label.config(text=f"📂 {os.path.basename(auto_folder)} (auto-detectado)")
            self.load_emojis(auto_folder)

    def setup_ui(self):
        emoji_top = ttk.Frame(self)
        emoji_top.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(emoji_top, text="📁 Pasta Emojis", command=self.select_emoji_folder, style="Accent.TButton").pack(side="left")
        self.emoji_folder_label = ttk.Label(emoji_top, text="Nenhuma pasta selecionada", width=40)
        self.emoji_folder_label.pack(side="left", padx=5)
        
        # Barra de Emojis
        self.emoji_canvas = tk.Canvas(self, height=60)
        self.emoji_canvas.pack(fill="x", padx=10, pady=5)
        self.emoji_inner_frame = ttk.Frame(self.emoji_canvas)
        self.emoji_canvas.create_window((0, 0), window=self.emoji_inner_frame, anchor="nw")
        
        emoji_scroll = ttk.Scrollbar(self, orient="horizontal", command=self.emoji_canvas.xview)
        emoji_scroll.pack(fill="x", padx=10)
        self.emoji_canvas.configure(xscrollcommand=emoji_scroll.set)
        
        emoji_bottom = ttk.Frame(self)
        emoji_bottom.pack(fill="x", padx=10, pady=5)
        ttk.Label(emoji_bottom, text="Escala:").pack(side="left")
        ttk.Scale(emoji_bottom, from_=0.5, to=2.0, variable=self.emoji_scale, orient="horizontal").pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(emoji_bottom, text="Inserir Emoji", command=self.inserir_tag).pack(side="right")

    def select_emoji_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.emoji_folder_label.config(text=f"📁 {os.path.basename(folder)} (manual)")
            self.load_emojis(folder)

    def load_emojis(self, folder):
        self.emoji_folder_path = folder
        for widget in self.emoji_inner_frame.winfo_children():
            widget.destroy()
        
        self.emoji_manager.load_emojis(folder)
        emojis = self.emoji_manager.get_emoji_list()
        
        for emoji_name in emojis:
            img_data = self.emoji_manager.get_emoji(emoji_name)
            if img_data:
                thumb = img_data.copy()
                thumb.thumbnail((32, 32))
                photo = ImageTk.PhotoImage(thumb)
                
                btn = tk.Button(self.emoji_inner_frame, image=photo, command=lambda n=emoji_name: self.set_selected_emoji(n))
                btn.image = photo # Referência
                btn.pack(side="left", padx=2)
        
        self.emoji_inner_frame.update_idletasks()
        self.emoji_canvas.configure(scrollregion=self.emoji_canvas.bbox("all"))

    def get_state(self):
        try:
            return {
                "folder": getattr(self, 'emoji_folder_path', None),
                "scale": self.emoji_scale.get()
            }
        except Exception:
            return {"folder": None, "scale": 1.0}

    def set_state(self, state):
        folder = state.get("folder")
        if folder and os.path.exists(folder):
            # Verifica se é a pasta auto-detectada
            auto_folder = self.emoji_manager.auto_detect_folder()
            if auto_folder and os.path.abspath(folder) == os.path.abspath(auto_folder):
                self.emoji_folder_label.config(text=f"📂 {os.path.basename(folder)} (auto-detectado)")
            else:
                self.emoji_folder_label.config(text=f"📁 {os.path.basename(folder)} (manual)")
            self.load_emojis(folder)
        
        self.emoji_scale.set(state.get("scale", 1.0))

    def set_selected_emoji(self, name):
        self.selected_emoji_name = name

    def inserir_tag(self):
        if self.selected_emoji_name:
            self.callback_inserir(f"[EMOJI:{self.selected_emoji_name}]")
