import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

class MediaPoolDialog(tk.Toplevel):
    def __init__(self, parent, pool_manager):
        super().__init__(parent)
        self.title("Gerenciar Pool de Mídias")
        self.geometry("600x450")
        self.transient(parent)
        self.grab_set()
        
        self.pool_manager = pool_manager
        self.result_pool = None # Para retornar ao pai
        
        # Copiar estado atual para edição local
        self.local_primary = self.pool_manager.primary_video
        self.local_secondaries = list(self.pool_manager.secondary_videos)
        
        self._setup_ui()
        self._refresh_list()

    def _setup_ui(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        ttk.Label(main_frame, text="Pool de Mídias (Distribuição Sequencial)", font=("Segoe UI", 12, "bold")).pack(pady=(0, 10))
        
        # Info Label
        self.info_label = ttk.Label(main_frame, text="Aba 1 = Principal, Aba 2 = Secundário 1...", foreground="gray")
        self.info_label.pack(pady=(0, 15))

        # Lista de vídeos
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill="both", expand=True)
        
        self.listbox = tk.Listbox(list_frame, font=("Segoe UI", 10), selectmode="single")
        self.listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        # Botões laterais/abaixo
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(btn_frame, text="+ Adicionar Secundário", command=self._add_video).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="- Remover", command=self._remove_video).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Limpar Tudo", command=self._clear_all).pack(side="left", padx=5)
        
        # Rodapé com OK/Cancelar
        footer = ttk.Frame(main_frame)
        footer.pack(fill="x", pady=(20, 0))
        
        ttk.Button(footer, text="Confirmar", command=self._on_confirm, style="Accent.TButton" if hasattr(self, 'style') else None).pack(side="right", padx=5)
        ttk.Button(footer, text="Cancelar", command=self.destroy).pack(side="right", padx=5)

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        
        if self.local_primary:
            name = os.path.basename(self.local_primary)
            self.listbox.insert(tk.END, f"[PRINCIPAL] {name}")
            self.listbox.itemconfig(tk.END, {'fg': 'blue'})
            
        for vid in self.local_secondaries:
            name = os.path.basename(vid)
            self.listbox.insert(tk.END, f"[SECUNDÁRIO] {name}")

    def _add_video(self):
        filepaths = filedialog.askopenfilenames(
            title="Selecionar Vídeos Secundários",
            filetypes=[
                ("Vídeos", "*.mp4 *.mov *.avi *.mkv"),
                ("Imagens", "*.png *.jpg *.jpeg *.bmp *.webp"),
                ("Todos Suportados", "*.mp4 *.mov *.avi *.mkv *.png *.jpg *.jpeg *.bmp *.webp")
            ]
        )
        if filepaths:
            for path in filepaths:
                if path not in self.local_secondaries and path != self.local_primary:
                    self.local_secondaries.append(path)
            self._refresh_list()

    def _remove_video(self):
        selection = self.listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        # Se tem principal, o index 0 é o principal
        if self.local_primary:
            if index == 0:
                self.local_primary = None # Usuário removeu o principal da lista
            else:
                self.local_secondaries.pop(index - 1)
        else:
            self.local_secondaries.pop(index)
            
        self._refresh_list()

    def _clear_all(self):
        if messagebox.askyesno("Confirmar", "Deseja limpar todo o pool?"):
            self.local_primary = None
            self.local_secondaries = []
            self._refresh_list()

    def _on_confirm(self):
        self.pool_manager.clear()
        if self.local_primary:
            self.pool_manager.add_primary(self.local_primary)
        for vid in self.local_secondaries:
            self.pool_manager.add_secondary(vid)
            
        self.result_pool = self.pool_manager
        self.destroy()
