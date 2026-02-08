import tkinter as tk
from tkinter import ttk

# Definição das Paletas de Cores
# Paletas de Cores Profissionais (Inspiradas em layouts Web modernos)
LIGHT_THEME = {
    "bg": "#f8fafc",            # Slate 50
    "surface": "#ffffff",      # Card background
    "fg": "#0f172a",           # Slate 900
    "fg_dim": "#64748b",       # Slate 500
    "select_bg": "#3b82f6",    # Blue 500
    "select_fg": "#ffffff",
    "button_bg": "#f1f5f9",    # Slate 100
    "accent_bg": "#3b82f6",    # Blue 500 (Ação)
    "accent_fg": "#ffffff",    # Texto Branco
    "accent_active": "#2563eb",# Blue 600
    "entry_bg": "#ffffff",
    "entry_fg": "#0f172a",
    "notebook_bg": "#f1f5f9",
    "notebook_tab_bg": "#e2e8f0",
    "notebook_tab_fg": "#475569",
    "notebook_tab_selected_bg": "#f8fafc",
    "border": "#e2e8f0"        # Slate 200
}

DARK_THEME = {
    "bg": "#0f172a",            # Slate 900
    "surface": "#1e293b",      # Slate 800 (Card)
    "fg": "#f8fafc",           # Slate 50
    "fg_dim": "#94a3b8",       # Slate 400
    "select_bg": "#3b82f6",    # Blue 500
    "select_fg": "#ffffff",
    "button_bg": "#334155",    # Slate 700
    "accent_bg": "#3b82f6",    # Blue 500
    "accent_fg": "#ffffff",
    "accent_active": "#2563eb",
    "entry_bg": "#1e293b",
    "entry_fg": "#f8fafc",
    "notebook_bg": "#0f172a",
    "notebook_tab_bg": "#1e293b",
    "notebook_tab_fg": "#94a3b8",
    "notebook_tab_selected_bg": "#0f172a",
    "border": "#334155"        # Slate 700
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

    def get_current_colors(self):
        return LIGHT_THEME if self.current_theme == "light" else DARK_THEME

    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        colors = LIGHT_THEME if theme_name == "light" else DARK_THEME
        
        # Configurar estilo ttk
        self.style.theme_use('clam')

        # Fonte Padrão
        main_font = ("Segoe UI", 10)
        bold_font = ("Segoe UI", 10, "bold")

        # Estilos Genéricos
        self.style.configure(".", 
            background=colors["bg"], 
            foreground=colors["fg"],
            font=main_font,
            fieldbackground=colors["entry_bg"],
            darkcolor=colors["bg"], 
            lightcolor=colors["bg"],
            bordercolor=colors["border"]
        )
        
        self.style.configure("TLabel", background=colors["bg"], foreground=colors["fg"], font=main_font)
        
        # Botões Padrão (Mais "Web")
        self.style.configure("TButton", 
            background=colors["button_bg"], 
            foreground=colors["fg"], 
            borderwidth=0,
            padding=(15, 8),
            font=bold_font
        )
        self.style.map("TButton",
            background=[('active', colors["select_bg"]), ('disabled', colors["bg"])],
            foreground=[('active', colors["select_fg"]), ('disabled', colors["fg_dim"])]
        )

        # Botões de Ação (Azul Vibrante)
        self.style.configure("Accent.TButton", 
            background=colors["accent_bg"], 
            foreground=colors["accent_fg"], 
            borderwidth=0,
            padding=(15, 8),
            font=bold_font
        )
        self.style.map("Accent.TButton",
            background=[('active', colors["accent_active"]), ('disabled', colors["bg"])],
            foreground=[('active', colors["accent_fg"]), ('disabled', colors["fg_dim"])]
        )

        # Botões de Ícones (Menores)
        self.style.configure("Icon.TButton", 
            background=colors["button_bg"], 
            foreground=colors["fg"], 
            borderwidth=0,
            padding=(5, 5),
            font=("Segoe UI", 10, "bold")
        )
        self.style.map("Icon.TButton",
            background=[('active', colors["select_bg"]), ('disabled', colors["bg"])],
            foreground=[('active', colors["select_fg"]), ('disabled', colors["fg_dim"])]
        )

        self.style.configure("TEntry", 
            fieldbackground=colors["entry_bg"], 
            foreground=colors["entry_fg"],
            padding=5,
            borderwidth=1
        )
        
        self.style.configure("TFrame", background=colors["bg"])
        
        # Labelframe como "Cards"
        self.style.configure("TLabelframe", 
            background=colors["bg"], 
            foreground=colors["fg"],
            relief="solid",
            borderwidth=1,
            bordercolor=colors["border"]
        )
        self.style.configure("TLabelframe.Label", 
            background=colors["bg"], 
            foreground=colors["select_bg"], 
            font=bold_font,
            padding=(5, 0)
        )
        
        # Notebook (Abas Modernas)
        self.style.configure("TNotebook", background=colors["bg"], borderwidth=0)
        self.style.configure("TNotebook.Tab", 
            background=colors["notebook_tab_bg"], 
            foreground=colors["notebook_tab_fg"],
            padding=(20, 10),
            font=bold_font,
            borderwidth=0
        )
        self.style.map("TNotebook.Tab", 
            background=[("selected", colors["select_bg"])],
            foreground=[("selected", colors["select_fg"])]
        )

        self.style.configure("TCheckbutton", background=colors["bg"], foreground=colors["fg"], font=main_font)
        self.style.configure("TRadiobutton", background=colors["bg"], foreground=colors["fg"], font=main_font)
        
        # Scale Sleek
        self.style.configure("Horizontal.TScale", 
            background=colors["bg"], 
            troughcolor=colors["border"], 
            borderwidth=0, 
            sliderthickness=15
        )

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
            elif hasattr(widget, "update_colors"):
                # Componentes Customizados (ex: ToggleSwitch)
                widget.update_colors(colors)
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
