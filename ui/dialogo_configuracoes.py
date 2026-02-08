import tkinter as tk
from tkinter import ttk, messagebox
from modules.config_global import global_config

class DialogoConfiguracoes(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configurações Globais")
        self.geometry("450x400")
        self.transient(parent)
        self.grab_set()
        
        # Tema e Estilo
        self.colors = parent.theme_manager.get_current_colors()
        parent.theme_manager.apply_to_widget(self)
        
        self._setup_ui()
        self._center_window()

    def _setup_ui(self):
        container = ttk.Frame(self, padding=20)
        container.pack(fill="both", expand=True)
        
        ttk.Label(container, text="⚙️ Preferências do Sistema", font=("Segoe UI", 12, "bold")).pack(pady=(0, 20))
        
        # --- Performance ---
        perf_frame = ttk.LabelFrame(container, text=" Performance de Renderização ", padding=10)
        perf_frame.pack(fill="x", pady=10)
        
        ttk.Label(perf_frame, text="Threads (CPU):").grid(row=0, column=0, sticky="w", pady=5)
        self.threads_var = tk.IntVar(value=global_config.get("num_threads"))
        self.spin_threads = ttk.Spinbox(perf_frame, from_=1, to=32, textvariable=self.threads_var, width=5)
        self.spin_threads.grid(row=0, column=1, sticky="w", padx=10)
        
        ttk.Label(perf_frame, text="Jobs Simultâneos:").grid(row=1, column=0, sticky="w", pady=5)
        self.jobs_var = tk.IntVar(value=global_config.get("parallel_jobs"))
        self.spin_jobs = ttk.Spinbox(perf_frame, from_=1, to=10, textvariable=self.jobs_var, width=5)
        self.spin_jobs.grid(row=1, column=1, sticky="w", padx=10)
        
        # --- Comportamento ---
        comp_frame = ttk.LabelFrame(container, text=" Comportamento Global ", padding=10)
        comp_frame.pack(fill="x", pady=10)
        
        self.override_style_var = tk.BooleanVar(value=global_config.get("global_subtitles_style"))
        ttk.Checkbutton(comp_frame, text="Forçar Estilo Único em Todas as Abas", variable=self.override_style_var).pack(anchor="w")
        
        # --- Rodapé ---
        btn_frame = ttk.Frame(container)
        btn_frame.pack(side="bottom", fill="x", pady=10)
        
        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Salvar", style="Accent.TButton", command=self.save_and_close).pack(side="right", padx=5)

    def save_and_close(self):
        global_config.set("num_threads", self.threads_var.get())
        global_config.set("parallel_jobs", self.jobs_var.get())
        global_config.set("global_subtitles_style", self.override_style_var.get())
        
        messagebox.showinfo("Sucesso", "Configurações globais salvas!")
        self.destroy()

    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
