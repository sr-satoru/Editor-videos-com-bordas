from tkinter import ttk
from ui.theme import LIGHT_THEME, DARK_THEME

class Footer(ttk.Frame):
    def __init__(self, parent, add_tab_callback=None, remove_tab_callback=None, render_all_callback=None, save_callback=None, load_callback=None, change_all_output_callback=None, change_all_audio_callback=None, load_video_all_callback=None):
        # Usamos tk.Frame internamente para ter controle de cores e bordas
        super().__init__(parent)
        self.pack(side="bottom", fill="x")
        
        # O ttk.Frame não aceita highlightthickness em muitos temas, 
        # então vamos usar um subframe tk para a borda superior se necessário
        # Ou simplesmente confiar no background contrastante.
        
        self.setup_ui(add_tab_callback, remove_tab_callback, render_all_callback, save_callback, load_callback, change_all_output_callback, change_all_audio_callback, load_video_all_callback)

    def setup_ui(self, add_tab_callback, remove_tab_callback, render_all_callback, save_callback, load_callback, change_all_output_callback, change_all_audio_callback, load_video_all_callback):
        # Frame interno com padding
        btn_frame = ttk.Frame(self, padding=(10, 5))
        btn_frame.pack(fill="x")

        # Primeira linha: Gestão de Abas e Projeto
        row1 = ttk.Frame(btn_frame)
        row1.pack(fill="x", pady=(0, 2))

        ttk.Button(row1, text="➕ Adicionar Aba", command=add_tab_callback, style="Accent.TButton", width=16).pack(side="left", padx=2)
        ttk.Button(row1, text="🗑️ Remover Aba", command=remove_tab_callback, width=16).pack(side="left", padx=2)
        
        # Separador visual à direita
        ttk.Button(row1, text="📂 Importar Projeto", command=load_callback, width=18).pack(side="right", padx=2)
        ttk.Button(row1, text="💾 Salvar Projeto", command=save_callback, width=18).pack(side="right", padx=2)

        # Segunda linha: Ações Globais e Renderização
        row2 = ttk.Frame(btn_frame)
        row2.pack(fill="x", pady=2)

        ttk.Button(row2, text="🎬 Renderizar Todas", command=render_all_callback, style="Accent.TButton", width=18).pack(side="right", padx=2)
        
        # Configurações em lote
        ttk.Label(row2, text="Ações em Lote:", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(5, 10))
        ttk.Button(row2, text="🎥 Vídeo (Todas)", command=load_video_all_callback).pack(side="left", padx=2)
        ttk.Button(row2, text="🎵 Áudio (Todas)", command=change_all_audio_callback).pack(side="left", padx=2)
        ttk.Button(row2, text="📁 Saída (Todas)", command=change_all_output_callback).pack(side="left", padx=2)

