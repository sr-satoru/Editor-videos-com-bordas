import tkinter as tk
from tkinter import ttk

class ComponenteListaLegendas(ttk.LabelFrame):
    def __init__(self, parent, subtitle_manager, callbacks):
        """
        callbacks: dicionário com 'on_select', 'on_remove', 'on_edit', 'on_move'
        """
        super().__init__(parent, text="📝 Lista de Legendas")
        self.subtitle_manager = subtitle_manager
        self.callbacks = callbacks
        
        self.setup_ui()

    def setup_ui(self):
        list_container = ttk.Frame(self)
        list_container.pack(fill="x", padx=10, pady=5)
        
        self.listbox = tk.Listbox(list_container, height=6)
        self.listbox.pack(side="left", fill="x", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.callbacks['on_select'])
        
        btn_frame = ttk.Frame(list_container)
        btn_frame.pack(side="right", padx=5)
        
        ttk.Button(btn_frame, text="🗑️", width=3, command=self.callbacks['on_remove']).pack(pady=2)
        ttk.Button(btn_frame, text="✏️", width=3, command=self.callbacks['on_edit']).pack(pady=2)
        ttk.Button(btn_frame, text="⬆️", width=3, command=lambda: self.callbacks['on_move'](-1)).pack(pady=2)
        ttk.Button(btn_frame, text="⬇️", width=3, command=lambda: self.callbacks['on_move'](1)).pack(pady=2)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        for sub in self.subtitle_manager.get_subtitles():
            self.listbox.insert(tk.END, f"#{sub['id']}: {sub['text'][:30]}...")

    def get_selection(self):
        sel = self.listbox.curselection()
        return sel[0] if sel else None

    def set_selection(self, index):
        self.listbox.selection_clear(0, tk.END)
        if index is not None:
            self.listbox.selection_set(index)
