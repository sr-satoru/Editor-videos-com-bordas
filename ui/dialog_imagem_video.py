import tkinter as tk
from tkinter import ttk, messagebox
from modules.config_global import global_config


class DialogImagemVideo(tk.Toplevel):
    """
    Diálogo simplificado para configurar conversão de imagens em vídeos.
    DEPRECADO: Funcionalidade agora integrada no DialogoConfiguracoes principal.
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configuração: Imagem → Vídeo")
        self.geometry("500x300")
        self.transient(parent)
        self.grab_set()
        
        # Tema e Estilo
        self.colors = parent.theme_manager.get_current_colors()
        parent.theme_manager.apply_to_widget(self)
        
        self._setup_ui()
        self._center_window()

    def _setup_ui(self):
        """Configura a interface do diálogo"""
        container = ttk.Frame(self, padding=20)
        container.pack(fill="both", expand=True)
        
        # Aviso de redirecionamento
        ttk.Label(
            container,
            text="ℹ️ Configuração Integrada",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=(0, 20))
        
        ttk.Label(
            container,
            text="As configurações de conversão de imagens agora estão\n"
                 "integradas no modal principal de Configurações Globais.\n\n"
                 "Por favor, use o menu de configurações principal\n"
                 "para ajustar todos os parâmetros.",
            font=("Segoe UI", 10),
            justify="center",
            wraplength=450
        ).pack(pady=20)
        
        # Botão OK
        ttk.Button(
            container,
            text="OK, Entendi",
            command=self.destroy
        ).pack(pady=10)

    def _center_window(self):
        """Centraliza a janela na tela"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
