import tkinter as tk
from tkinter import ttk, colorchooser
from ui.componentes_custom import ToggleSwitch

class ComponenteEstiloLegenda(ttk.LabelFrame):
    def __init__(self, parent, callbacks):
        """
        callbacks: dicionário com 'on_change' e 'get_current_time'
        """
        super().__init__(parent, text="✏️ Estilo da Legenda")
        self.callbacks = callbacks
        
        # Variáveis de estado
        self.font_family = tk.StringVar(value="Arial Black")
        self.font_size = tk.IntVar(value=18)
        self.font_color = tk.StringVar(value="#FFFFFF")
        self.border_color = tk.StringVar(value="#000000")
        self.bg_color = tk.StringVar(value="")
        self.border_thickness = tk.IntVar(value=2)
        
        # Controle de tempo manual
        self.use_manual_timing = tk.BooleanVar(value=False)
        self.start_time = tk.DoubleVar(value=0.0)
        self.end_time = tk.DoubleVar(value=1000.0)  # Padrão alto para auto-detecção
        
        self.setup_ui()

    def setup_ui(self):
        self.indicators = {}
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        # Row 0: Fonte, Tamanho
        ttk.Label(controls_frame, text="Fonte:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        font_options = ["Arial", "Arial Black", "Helvetica", "Impact", "Verdana", "Comic Sans MS"]
        self.font_combo = ttk.Combobox(controls_frame, textvariable=self.font_family, values=font_options, width=15)
        self.font_combo.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="w")
        
        ttk.Label(controls_frame, text="Tamanho:").grid(row=0, column=3, padx=5, pady=5, sticky="w")
        ttk.Spinbox(controls_frame, from_=1, to=200, textvariable=self.font_size, width=8).grid(row=0, column=4, padx=5, pady=5, sticky="w")
        
        # Row 1-3: Cores
        self.criar_linha_cor(controls_frame, 1, "Cor Fonte:", self.font_color, "font")
        self.criar_linha_cor(controls_frame, 2, "Cor Borda:", self.border_color, "border")
        self.criar_linha_cor(controls_frame, 3, "Cor Fundo:", self.bg_color, "bg", allow_none=True)
        
        # Row 4: Espessura
        ttk.Label(controls_frame, text="Espessura Borda:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        thickness_spinbox = ttk.Spinbox(controls_frame, from_=0, to=10, textvariable=self.border_thickness, width=8, 
                                        command=lambda: self.callbacks.get('on_change', lambda: None)())
        thickness_spinbox.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        
        # Row 5: Toggle para controle manual de tempo
        timing_toggle_frame = ttk.Frame(controls_frame)
        timing_toggle_frame.grid(row=5, column=0, columnspan=5, sticky="w", pady=(10, 5))
        
        self.timing_toggle = ToggleSwitch(timing_toggle_frame, self.use_manual_timing, command=self.toggle_timing_controls)
        self.timing_toggle.pack(side="left", padx=(0, 10))
        ttk.Label(timing_toggle_frame, text="⏱️ Controle Manual de Tempo", font=("Segoe UI", 9, "bold")).pack(side="left")
        
        # Row 6: Controles de tempo (inicialmente ocultos)
        self.timing_controls_frame = ttk.Frame(controls_frame)
        self.timing_controls_frame.grid(row=6, column=0, columnspan=5, sticky="we", pady=5)
        
        ttk.Label(self.timing_controls_frame, text="Início:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.start_spin = ttk.Spinbox(self.timing_controls_frame, from_=0, to=3600, increment=0.1, textvariable=self.start_time, width=8,
                                  command=lambda: self.callbacks.get('on_change', lambda: None)())
        self.start_spin.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Button(self.timing_controls_frame, text="⏱️ Atual", width=10, command=self.set_start).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
        ttk.Label(self.timing_controls_frame, text="Fim:").grid(row=0, column=3, padx=(15, 5), pady=5, sticky="w")
        self.end_spin = ttk.Spinbox(self.timing_controls_frame, from_=0, to=3600, increment=0.1, textvariable=self.end_time, width=8,
                                command=lambda: self.callbacks.get('on_change', lambda: None)())
        self.end_spin.grid(row=0, column=4, padx=5, pady=5, sticky="w")
        
        ttk.Button(self.timing_controls_frame, text="⏱️ Atual", width=10, command=self.set_end).grid(row=0, column=5, padx=5, pady=5, sticky="w")
        
        # Inicialmente ocultar controles de tempo
        self.toggle_timing_controls()

    def toggle_timing_controls(self):
        """Mostra/oculta controles de tempo baseado no toggle"""
        if self.use_manual_timing.get():
            # Mostrar controles
            self.timing_controls_frame.grid()
        else:
            # Ocultar controles e resetar para valores automáticos
            self.timing_controls_frame.grid_remove()
            self.start_time.set(0.0)
            self.end_time.set(1000.0)  # Valor alto para auto-detecção
            if 'on_change' in self.callbacks: 
                self.callbacks['on_change']()

    def set_start(self):
        if 'get_current_time' in self.callbacks:
            t = self.callbacks['get_current_time']()
            self.start_time.set(round(t, 2))
            if 'on_change' in self.callbacks: self.callbacks['on_change']()
    
    def set_end(self):
        if 'get_current_time' in self.callbacks:
            t = self.callbacks['get_current_time']()
            self.end_time.set(round(t, 2))
            if 'on_change' in self.callbacks: self.callbacks['on_change']()

    def criar_linha_cor(self, parent, row, label_text, var, key, allow_none=False):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, padx=5, pady=5, sticky="w")
        
        bg_color = var.get() if var.get() else "#f0f0f0"
        indicator = tk.Label(parent, width=3, bg=bg_color, relief="raised")
        indicator.ignore_theme = True
        indicator.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        self.indicators[key] = indicator
        
        def choose():
            color = colorchooser.askcolor(initialcolor=var.get() or "#FFFFFF")[1]
            if color:
                var.set(color)
                indicator.config(bg=color)
                if self.callbacks.get('on_change'): self.callbacks['on_change']()
            elif allow_none:
                var.set("")
                indicator.config(bg="#f0f0f0")
                if self.callbacks.get('on_change'): self.callbacks['on_change']()
                
        ttk.Button(parent, text="🎨", width=8, command=choose).grid(row=row, column=2, padx=5, pady=5, sticky="w")

    def get_estilo(self):
        return {
            "font": self.font_family.get(),
            "size": self.font_size.get(),
            "color": self.font_color.get(),
            "border": self.border_color.get(),
            "bg": self.bg_color.get(),
            "border_thickness": self.border_thickness.get(),
            "start_time": self.start_time.get(),
            "end_time": self.end_time.get(),
            "use_manual_timing": self.use_manual_timing.get()
        }
    
    def get_state(self):
        return self.get_estilo()

    def set_state(self, state):
        self.font_family.set(state.get("font", "Arial Black"))
        self.font_size.set(state.get("size", 18))
        self.font_color.set(state.get("color", "#FFFFFF"))
        self.border_color.set(state.get("border", "#000000"))
        self.bg_color.set(state.get("bg", ""))
        self.border_thickness.set(state.get("border_thickness", 2))
        self.use_manual_timing.set(state.get("use_manual_timing", False))
        self.start_time.set(state.get("start_time", 0.0))
        self.end_time.set(state.get("end_time", 1000.0))
        
        # Atualizar indicadores visuais
        if hasattr(self, 'indicators'):
            self.indicators['font'].config(bg=self.font_color.get())
            self.indicators['border'].config(bg=self.border_color.get())
            self.indicators['bg'].config(bg=self.bg_color.get() if self.bg_color.get() else "#f0f0f0")
        
        # Atualizar visibilidade dos controles
        if hasattr(self, 'timing_controls_frame'):
            self.toggle_timing_controls()
