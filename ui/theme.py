import tkinter as tk
from tkinter import ttk

# Definição das Paletas de Cores
LIGHT_THEME = {
    "bg": "#f0f0f0",
    "fg": "#000000",
    "select_bg": "#0078d7",
    "select_fg": "#ffffff",
    "button_bg": "#e1e1e1",      # Padrão
    "accent_bg": "#0078d7",      # Azul (Ação)
    "accent_fg": "#ffffff",      # Texto Branco (Ação)
    "accent_active": "#005a9e",  # Azul Escuro
    "entry_bg": "#ffffff",
    "entry_fg": "#000000",
    "notebook_bg": "#f0f0f0",
    "notebook_tab_bg": "#e1e1e1",
    "notebook_tab_fg": "#000000",
    "notebook_tab_selected_bg": "#f0f0f0",
}

DARK_THEME = {
    "bg": "#2d2d2d",
    "fg": "#ffffff",
    "select_bg": "#0078d7",
    "select_fg": "#ffffff",
    "button_bg": "#3e3e3e",      # Padrão
    "accent_bg": "#0078d7",      # Azul (Ação)
    "accent_fg": "#ffffff",      # Texto Branco (Ação)
    "accent_active": "#005a9e",  # Azul Escuro
    "entry_bg": "#3e3e3e",
    "entry_fg": "#ffffff",
    "notebook_bg": "#2d2d2d",
    "notebook_tab_bg": "#3e3e3e",
    "notebook_tab_fg": "#cccccc",
    "notebook_tab_selected_bg": "#2d2d2d",
}

class ThemeManager:
    def __init__(self, root):
        self.root = root
        self.current_theme = "light"  # Padrão
        self.style = ttk.Style(root)
        self.apply_theme("light")

    def toggle_theme(self):
        if self.current_theme == "light":
            self.apply_theme("dark")
        else:
            self.apply_theme("light")

    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        colors = LIGHT_THEME if theme_name == "light" else DARK_THEME
        
        # Configurar estilo ttk
        self.style.theme_use('clam')  # 'clam' permite maior customização de cores

        # Estilos Genéricos
        self.style.configure(".", 
            background=colors["bg"], 
            foreground=colors["fg"],
            fieldbackground=colors["entry_bg"],
            darkcolor=colors["bg"], 
            lightcolor=colors["bg"]
        )
        
        self.style.configure("TLabel", background=colors["bg"], foreground=colors["fg"])
        
        # Botões Padrão (Gerais)
        self.style.configure("TButton", 
            background=colors["button_bg"], 
            foreground=colors["fg"], 
            borderwidth=1
        )
        self.style.map("TButton",
            background=[('active', colors["select_bg"]), ('disabled', colors["bg"])],
            foreground=[('active', colors["select_fg"]), ('disabled', '#888888')]
        )

        # Botões de Ação (Azul) - Accent.TButton
        self.style.configure("Accent.TButton", 
            background=colors["accent_bg"], 
            foreground=colors["accent_fg"], 
            borderwidth=1,
            focuscolor=colors["accent_bg"]
        )
        self.style.map("Accent.TButton",
            background=[('active', colors["accent_active"]), ('disabled', colors["bg"])],
            foreground=[('active', colors["accent_fg"]), ('disabled', '#888888')]
        )

        self.style.configure("TEntry", fieldbackground=colors["entry_bg"], foreground=colors["entry_fg"])
        self.style.configure("TFrame", background=colors["bg"])
        self.style.configure("TLabelframe", background=colors["bg"], foreground=colors["fg"])
        self.style.configure("TLabelframe.Label", background=colors["bg"], foreground=colors["fg"])
        
        self.style.configure("TNotebook", background=colors["notebook_bg"])
        self.style.configure("TNotebook.Tab", 
            background=colors["notebook_tab_bg"], 
            foreground=colors["notebook_tab_fg"],
            padding=[10, 2]
        )
        self.style.map("TNotebook.Tab", 
            background=[("selected", colors["notebook_tab_selected_bg"])],
            foreground=[("selected", colors["fg"])]
        )

        self.style.configure("TCheckbutton", background=colors["bg"], foreground=colors["fg"])
        self.style.configure("TRadiobutton", background=colors["bg"], foreground=colors["fg"])

        # Atualizar elementos TK (não-ttk)
        self.root.configure(bg=colors["bg"])
        
        # Recursivamente atualizar widgets tk que não herdam estilo global automaticamente (como Canvas)
        self._update_tk_widgets(self.root, colors)

    def apply_to_widget(self, widget):
        """Aplica o tema atual a um widget específico (útil para Toplevels)"""
        colors = LIGHT_THEME if self.current_theme == "light" else DARK_THEME
        # Configura background do widget pai se necessário (ex: Toplevel)
        try:
            widget.configure(bg=colors["bg"])
        except: pass
        self._update_tk_widgets(widget, colors)

    def _update_tk_widgets(self, widget, colors):
        try:
            # Tenta configurar background se o widget suportar e não for um widget TTK
            if getattr(widget, "ignore_theme", False):
                pass
            elif isinstance(widget, (tk.Text, tk.Listbox)):
                widget.configure(bg=colors["entry_bg"], fg=colors["entry_fg"])
                if isinstance(widget, tk.Text):
                    widget.configure(insertbackground=colors["fg"])
            elif isinstance(widget, tk.Button):
                 if getattr(widget, "is_accent", False):
                     # Botão Accent (Azul)
                     widget.configure(bg=colors["accent_bg"], fg=colors["accent_fg"], activebackground=colors["accent_active"], activeforeground=colors["accent_fg"])
                 else:
                     # Botão Padrão
                     widget.configure(bg=colors["button_bg"], fg=colors["fg"], activebackground=colors["select_bg"], activeforeground=colors["select_fg"])
            elif isinstance(widget, (tk.Canvas, tk.Frame, tk.Label, tk.Checkbutton, tk.Radiobutton)) and not isinstance(widget, (ttk.Frame, ttk.Label, ttk.Button, ttk.Checkbutton, ttk.Radiobutton)):
                 widget.configure(bg=colors["bg"])
                 if hasattr(widget, "fg"): # Canvas não tem fg
                     widget.configure(fg=colors["fg"])
        except tk.TclError:
            pass # Ignora erros de configuração inválida para certos widgets

        # Itera sobre filhos
        for child in widget.winfo_children():
            self._update_tk_widgets(child, colors)
