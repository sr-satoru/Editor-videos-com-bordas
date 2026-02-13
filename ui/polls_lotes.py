import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from modules.polls.manager import MediaPoolManager

class PoolLotesUI(ttk.LabelFrame):
    """
    Componente de interface para gerenciar um Pool de Mídias dentro do contexto de Lotes.
    Garante isolamento ao trabalhar com uma instância local de MediaPoolManager.
    """
    def __init__(self, parent, initial_pool_data=None):
        super().__init__(parent, text="Pool de Mídias do Lote", padding=10)
        
        # Inicializar manager local isolado
        if initial_pool_data:
            self.pool_manager = MediaPoolManager.from_dict(initial_pool_data)
        else:
            self.pool_manager = MediaPoolManager()
            
        self._setup_ui()
        self._refresh_list()

    def _setup_ui(self):
        # Container superior
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(top_frame, text="Mídias selecionadas para este lote:", font=("Segoe UI", 9, "bold")).pack(side="left")

        # Lista e Scrollbar
        list_container = ttk.Frame(self)
        list_container.pack(fill="both", expand=True)
        
        self.listbox = tk.Listbox(list_container, height=4, font=("Segoe UI", 9))
        self.listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        # Botões de ação
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=(5, 0))
        
        ttk.Button(btn_frame, text="+ Adicionar", command=self._add_media, width=12).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="- Remover", command=self._remove_media, width=12).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Limpar", command=self._clear_pool, width=12).pack(side="left", padx=2)

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        for vid in self.pool_manager.secondary_videos:
            name = os.path.basename(vid)
            self.listbox.insert(tk.END, f"📁 Mídia: {name}")

    def _add_media(self):
        filepaths = filedialog.askopenfilenames(
            title="Selecionar Mídias Adicionais para o Pool",
            filetypes=[
                ("Todos Suportados", "*.mp4 *.mov *.avi *.mkv *.png *.jpg *.jpeg *.bmp *.webp"),
                ("Vídeos", "*.mp4 *.mov *.avi *.mkv"),
                ("Imagens", "*.png *.jpg *.jpeg *.bmp *.webp")
            ]
        )
        if filepaths:
            for path in filepaths:
                self.pool_manager.add_secondary(path)
            self._refresh_list()

    def _remove_media(self):
        selection = self.listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        self.pool_manager.secondary_videos.pop(index)
        self._refresh_list()

    def _clear_pool(self):
        self.pool_manager.clear()
        self._refresh_list()

    def get_pool_data(self):
        """Retorna os dados do pool para serem salvos no lote"""
        return self.pool_manager.to_dict()
    
    def set_pool_data(self, data):
        """Atualiza o pool com novos dados (ex: ao herdar de aba)"""
        if data:
            self.pool_manager = MediaPoolManager.from_dict(data)
            self._refresh_list()
