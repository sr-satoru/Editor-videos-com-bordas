import tkinter as tk
from ui.theme import LIGHT_THEME, DARK_THEME

class ToggleSwitch(tk.Canvas):
    def __init__(self, parent, variable, text="", command=None, width=45, height=22):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bd=0, cursor="hand2")
        self.variable = variable
        self.text = text
        self.command = command
        
        # Cores base (Serão atualizadas pelo ThemeManager se ignore_theme for False, 
        # mas aqui vamos gerenciar manualmente para o desenho)
        self.on_color = "#3b82f6"  # Blue 500
        self.off_color = "#cbd5e1" # Slate 300
        self.handle_color = "#ffffff"
        
        self.bind("<Button-1>", self._toggle)
        
        # Adicionar trace para redesenhar quando a variável mudar (fix para set_state)
        self.variable.trace_add("write", lambda *args: self._draw())
        
        self._draw()

    def _draw(self):
        self.delete("all")
        is_on = self.variable.get()
        
        # Cores dinâmicas baseadas no estado
        bg_color = self.on_color if is_on else self.off_color
        
        # Desenhar Trilho (Track) - Arredondado
        r = self.winfo_reqheight() / 2
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        
        self.create_round_rect(2, 2, w-2, h-2, radius=r, fill=bg_color, outline="")
        
        # Desenhar Botão (Handle)
        padding = 3
        handle_size = h - (padding * 2)
        
        if is_on:
            x_pos = w - handle_size - padding
        else:
            x_pos = padding
            
        self.create_oval(x_pos, padding, x_pos + handle_size, padding + handle_size, fill=self.handle_color, outline="")

    def create_round_rect(self, x1, y1, x2, y2, radius=10, **kwargs):
        points = [x1+radius, y1,
                  x1+radius, y1,
                  x2-radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1+radius,
                  x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def _toggle(self, event=None):
        self.variable.set(not self.variable.get())
        if self.command:
            self.command()
        self._draw()

    def update_colors(self, colors):
        """Chamado pelo ThemeManager para atualizar cores do switch"""
        self.configure(bg=colors["bg"])
        self.on_color = colors["select_bg"]
        self.off_color = colors["border"]
        self.handle_color = colors["surface"]
        self._draw()
