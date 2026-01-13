import tkinter as tk
from tkinter import ttk

class Footer(ttk.Frame):
    def __init__(self, parent, add_tab_callback=None, remove_tab_callback=None, render_all_callback=None, save_callback=None, load_callback=None, change_all_output_callback=None, change_all_audio_callback=None, load_video_all_callback=None):
        super().__init__(parent)
        self.pack(side="bottom", fill="x")  # ocupa largura total

        # Frame interno para alinhar botão à esquerda
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x")

        # Primeira linha de botões
        row1 = ttk.Frame(btn_frame)
        row1.pack(fill="x")

        self.add_tab_btn = ttk.Button(row1, text="➕ Adicionar Aba", command=add_tab_callback)
        self.add_tab_btn.pack(side="left", padx=5, pady=5)

        self.remove_tab_btn = ttk.Button(row1, text="🗑️ Remover Aba", command=remove_tab_callback)
        self.remove_tab_btn.pack(side="left", padx=5, pady=5)

        self.render_all_btn = ttk.Button(row1, text="🎬 Renderizar Todas as Abas", command=render_all_callback)
        self.render_all_btn.pack(side="left", padx=5, pady=5)

        self.save_btn = ttk.Button(row1, text="💾 Salvar Projeto", command=save_callback)
        self.save_btn.pack(side="left", padx=5, pady=5)

        self.load_btn = ttk.Button(row1, text="📂 Importar Projeto", command=load_callback)
        self.load_btn.pack(side="left", padx=5, pady=5)

        # Segunda linha de botões (Ações Globais)
        row2 = ttk.Frame(btn_frame)
        row2.pack(fill="x")

        self.change_output_btn = ttk.Button(row2, text="📁 Alterar Saída (Todas)", command=change_all_output_callback)
        self.change_output_btn.pack(side="left", padx=5, pady=5)

        self.change_audio_btn = ttk.Button(row2, text="🎵 Alterar Pasta Áudio (Todas)", command=change_all_audio_callback)
        self.change_audio_btn.pack(side="left", padx=5, pady=5)

        self.load_video_btn = ttk.Button(row2, text="🎥 Carregar Vídeo (Todas)", command=load_video_all_callback)
        self.load_video_btn.pack(side="left", padx=5, pady=5)

class EditorUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Teste Footer")
        self.geometry("600x400")

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True)

        # Aba inicial
        aba1 = ttk.Frame(self.notebook)
        self.notebook.add(aba1, text="Aba 1")

        # Footer
        Footer(container, add_tab_callback=self.add_new_tab)

    def add_new_tab(self):
        new_tab = ttk.Frame(self.notebook)
        self.notebook.add(new_tab, text=f"Aba {len(self.notebook.tabs())+1}")

if __name__ == "__main__":
    EditorUI().mainloop()
