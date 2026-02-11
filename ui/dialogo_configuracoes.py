import tkinter as tk
from tkinter import ttk, messagebox
import psutil
from modules.config_global import global_config
from ui.dialog_imagem_video import DialogImagemVideo
from ui.componentes_custom import ToggleSwitch


class DialogoConfiguracoes(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configurações Globais")
        self.geometry("650x600")
        self.transient(parent)
        self.grab_set()
        
        # Tema e Estilo
        self.colors = parent.theme_manager.get_current_colors()
        parent.theme_manager.apply_to_widget(self)
        
        # Detectar informações do sistema
        self.cpu_count_physical = psutil.cpu_count(logical=False)
        self.cpu_count_logical = psutil.cpu_count(logical=True)
        
        self._setup_ui()
        self._center_window()

    def _setup_ui(self):
        # Container principal com scroll
        main_container = ttk.Frame(self)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Canvas e scrollbar
        canvas = tk.Canvas(main_container, highlightthickness=0, bg=self.colors["bg"])
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configurar scroll region
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Criar janela no canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas e scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Habilitar scroll com mouse wheel (padrão do main_ui)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<Enter>", lambda e: (
            canvas.bind_all("<MouseWheel>", _on_mousewheel),
            canvas.bind_all("<Button-4>", _on_mousewheel),
            canvas.bind_all("<Button-5>", _on_mousewheel)
        ))
        canvas.bind("<Leave>", lambda e: (
            canvas.unbind_all("<MouseWheel>"),
            canvas.unbind_all("<Button-4>"),
            canvas.unbind_all("<Button-5>")
        ))
        
        # Conteúdo do scroll
        container = ttk.Frame(scrollable_frame, padding=20)
        container.pack(fill="both", expand=True)
        
        # Título
        ttk.Label(
            container,
            text="⚙️ Preferências do Sistema",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(0, 20))
        
        # --- Informações do Sistema ---
        info_frame = ttk.LabelFrame(
            container,
            text=" 💻 Informações do Sistema ",
            padding=15
        )
        info_frame.pack(fill="x", pady=(0, 10))
        
        # CPU Info
        cpu_info_text = f"CPU: {self.cpu_count_physical} núcleos físicos, {self.cpu_count_logical} threads lógicas"
        ttk.Label(
            info_frame,
            text=cpu_info_text,
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=2)
        
        # Memória RAM
        ram = psutil.virtual_memory()
        ram_gb = ram.total / (1024**3)
        ttk.Label(
            info_frame,
            text=f"RAM: {ram_gb:.1f} GB total ({ram.percent}% em uso)",
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=2)
        
        # --- Performance de Renderização ---
        perf_frame = ttk.LabelFrame(
            container,
            text=" ⚡ Performance de Renderização ",
            padding=15
        )
        perf_frame.pack(fill="x", pady=10)
        
        # Threads com detecção automática
        thread_row = ttk.Frame(perf_frame)
        thread_row.pack(fill="x", pady=8)
        
        ttk.Label(
            thread_row,
            text="Threads (CPU):",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")
        
        # Frame para Entry e botão auto
        thread_input_frame = ttk.Frame(thread_row)
        thread_input_frame.pack(side="left", padx=10)
        
        self.threads_var = tk.StringVar(value=str(global_config.get("num_threads")))
        thread_entry = ttk.Entry(
            thread_input_frame,
            textvariable=self.threads_var,
            width=6,
            font=("Segoe UI", 10)
        )
        thread_entry.pack(side="left", padx=(0, 5))
        
        ttk.Button(
            thread_input_frame,
            text="🔄 Auto",
            width=8,
            command=self.auto_detect_threads
        ).pack(side="left")
        
        ttk.Label(
            thread_row,
            text=f"(Recomendado: {self.cpu_count_logical})",
            font=("Segoe UI", 8),
            foreground="gray"
        ).pack(side="left", padx=5)
        
        # Explicação
        ttk.Label(
            perf_frame,
            text="💡 Use o botão 'Auto' para detectar automaticamente o melhor valor",
            font=("Segoe UI", 8),
            foreground="#666"
        ).pack(anchor="w", pady=(0, 10))
        
        # Jobs Simultâneos
        jobs_row = ttk.Frame(perf_frame)
        jobs_row.pack(fill="x", pady=8)
        
        ttk.Label(
            jobs_row,
            text="Jobs Simultâneos:",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")
        
        self.jobs_var = tk.StringVar(value=str(global_config.get("parallel_jobs")))
        jobs_entry = ttk.Entry(
            jobs_row,
            textvariable=self.jobs_var,
            width=6,
            font=("Segoe UI", 10)
        )
        jobs_entry.pack(side="left", padx=10)
        
        ttk.Label(
            jobs_row,
            text="(1-10)",
            font=("Segoe UI", 8),
            foreground="gray"
        ).pack(side="left")
        
        # --- Conversão Imagem → Vídeo ---
        image_frame = ttk.LabelFrame(
            container,
            text=" 🎬 Conversão Imagem → Vídeo ",
            padding=15
        )
        image_frame.pack(fill="x", pady=10)
        
        # Duração com campo de entrada direto
        duration_row = ttk.Frame(image_frame)
        duration_row.pack(fill="x", pady=8)
        
        ttk.Label(
            duration_row,
            text="Duração (segundos):",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")
        
        self.duration_var = tk.StringVar(
            value=str(global_config.get("image_to_video_duration"))
        )
        duration_entry = ttk.Entry(
            duration_row,
            textvariable=self.duration_var,
            width=6,
            font=("Segoe UI", 10)
        )
        duration_entry.pack(side="left", padx=10)
        
        ttk.Label(
            duration_row,
            text="(1-60s)",
            font=("Segoe UI", 8),
            foreground="gray"
        ).pack(side="left")
        
        # Aplicação global com Switch
        self.global_image_var = tk.BooleanVar(
            value=global_config.get("global_image_to_video_settings")
        )
        
        switch_row = ttk.Frame(image_frame)
        switch_row.pack(anchor="w", pady=(10, 0), fill="x")
        
        ToggleSwitch(switch_row, self.global_image_var).pack(side="left", padx=(0, 10))
        ttk.Label(
            switch_row,
            text="Aplicar globalmente em todas as abas",
            font=("Segoe UI", 10)
        ).pack(side="left")
        
        # Info
        ttk.Label(
            image_frame,
            text="ℹ️  Imagens serão convertidas automaticamente antes do processamento",
            font=("Segoe UI", 8),
            foreground="#666",
            wraplength=480
        ).pack(anchor="w", pady=(8, 0))
        
        # --- Rodapé (fora do scroll) ---
        btn_container = ttk.Frame(self, padding=(20, 10))
        btn_container.pack(side="bottom", fill="x")
        
        ttk.Button(
            btn_container,
            text="Cancelar",
            command=self.destroy
        ).pack(side="right", padx=5)
        
        ttk.Button(
            btn_container,
            text="💾 Salvar Configurações",
            style="Accent.TButton",
            command=self.save_and_close
        ).pack(side="right", padx=5)

    def auto_detect_threads(self):
        """Detecta automaticamente o número ideal de threads"""
        # Usar threads lógicas como padrão
        optimal = self.cpu_count_logical
        self.threads_var.set(str(optimal))
        
        messagebox.showinfo(
            "Detecção Automática",
            f"Detectado: {optimal} threads lógicas\n"
            f"({self.cpu_count_physical} núcleos físicos)\n\n"
            f"Este valor foi configurado automaticamente."
        )

    def save_and_close(self):
        """Validar e salvar configurações"""
        try:
            # Validar threads
            threads = int(self.threads_var.get())
            if threads < 1 or threads > 128:
                messagebox.showerror(
                    "Valor Inválido",
                    "Threads deve estar entre 1 e 128"
                )
                return
            
            # Validar jobs
            jobs = int(self.jobs_var.get())
            if jobs < 1 or jobs > 10:
                messagebox.showerror(
                    "Valor Inválido",
                    "Jobs simultâneos deve estar entre 1 e 10"
                )
                return
            
            # Validar duração
            duration = int(self.duration_var.get())
            if duration < 1 or duration > 60:
                messagebox.showerror(
                    "Valor Inválido",
                    "Duração deve estar entre 1 e 60 segundos"
                )
                return
            
            # Salvar todas as configurações
            global_config.set("num_threads", threads)
            global_config.set("parallel_jobs", jobs)
            global_config.set("image_to_video_duration", duration)
            global_config.set("global_image_to_video_settings", self.global_image_var.get())
            
            messagebox.showinfo(
                "Sucesso",
                f"✓ Configurações salvas com sucesso!\n\n"
                f"Threads: {threads}\n"
                f"Jobs: {jobs}\n"
                f"Duração imagem→vídeo: {duration}s"
            )
            
            self.destroy()
            
        except ValueError:
            messagebox.showerror(
                "Erro de Validação",
                "Por favor, insira apenas números válidos nos campos"
            )

    def _center_window(self):
        """Centraliza a janela na tela"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
