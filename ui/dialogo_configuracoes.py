import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import psutil
from modules.config_global import global_config
from ui.dialog_imagem_video import DialogImagemVideo
from ui.componentes_custom import ToggleSwitch
from ui.lotes import AbaLotes, GerenciadorFilas, PoolLotesUI
from ui.notifications import TabNotifications


class DialogoConfiguracoes(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configurações Globais")
        self.geometry("1080x960")  # Aumentado para acomodar aba de lotes
        self.transient(parent)
        self.grab_set()
        
        # Referência ao editor principal
        self.editor_ui = parent
        
        # Tema e Estilo
        self.colors = parent.theme_manager.get_current_colors()
        parent.theme_manager.apply_to_widget(self)
        
        # Detectar informações do sistema
        self.cpu_count_physical = psutil.cpu_count(logical=False)
        self.cpu_count_logical = psutil.cpu_count(logical=True)
        
        self._setup_ui()
        self._center_window()

    def _setup_ui(self):
        # Container principal
        main_container = ttk.Frame(self)
        main_container.pack(fill="both", expand=True)
        
        # Notebook para abas
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        
        # Criar abas
        self.tab_general = ttk.Frame(self.notebook, padding=15)
        self.tab_notifications = TabNotifications(self.notebook)
        self.tab_lotes = AbaLotes(self.notebook, self.editor_ui)
        self.tab_arquivos_lotes = GerenciadorFilas(self.notebook, self.editor_ui)
        self.tab_pool_abas = PoolLotesUI(self.notebook, self.editor_ui.global_tab_pool.to_dict())
        self.tab_pool_abas.config(text=" 🎬 Pool de Mídias (Abas) ")
        
        self.notebook.add(self.tab_general, text=" ⚙️ Geral ")
        self.notebook.add(self.tab_notifications, text=" 🔔 Notificações ")
        self.notebook.add(self.tab_pool_abas, text=" 🎬 Pool (Abas) ")
        self.notebook.add(self.tab_lotes, text=" 📦 Lotes ")
        self.notebook.add(self.tab_arquivos_lotes, text=" 📂 Arquivos Lotes ")
        
        # Preencher aba geral
        self._create_general_tab()
        
        # --- Rodapé (Fixo) ---
        btn_container = ttk.Frame(main_container, padding=(20, 15))
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

    def _create_general_tab(self):
        container = self.tab_general
        
        # --- Informações do Sistema ---
        info_frame = ttk.LabelFrame(container, text=" 💻 Informações do Sistema ", padding=15)
        info_frame.pack(fill="x", pady=(0, 10))
        
        cpu_info_text = f"CPU: {self.cpu_count_physical} núcleos físicos, {self.cpu_count_logical} threads lógicas"
        ttk.Label(info_frame, text=cpu_info_text, font=("Segoe UI", 9)).pack(anchor="w", pady=2)
        
        ram = psutil.virtual_memory()
        ram_gb = ram.total / (1024**3)
        ttk.Label(info_frame, text=f"RAM: {ram_gb:.1f} GB total ({ram.percent}% em uso)", font=("Segoe UI", 9)).pack(anchor="w", pady=2)
        
        # --- Performance ---
        perf_frame = ttk.LabelFrame(container, text=" ⚡ Performance ", padding=15)
        perf_frame.pack(fill="x", pady=10)
        
        # Threads
        thread_row = ttk.Frame(perf_frame)
        thread_row.pack(fill="x", pady=8)
        ttk.Label(thread_row, text="Threads (CPU):", font=("Segoe UI", 10, "bold")).pack(side="left")
        
        thread_input_frame = ttk.Frame(thread_row)
        thread_input_frame.pack(side="left", padx=10)
        self.threads_var = tk.StringVar(value=str(global_config.get("num_threads")))
        ttk.Entry(thread_input_frame, textvariable=self.threads_var, width=6, font=("Segoe UI", 10)).pack(side="left", padx=(0, 5))
        ttk.Button(thread_input_frame, text="🔄 Auto", width=8, command=self.auto_detect_threads).pack(side="left")
        ttk.Label(thread_row, text=f"(Sugerido: {self.cpu_count_logical})", font=("Segoe UI", 8), foreground="gray").pack(side="left")
        
        # Jobs
        jobs_row = ttk.Frame(perf_frame)
        jobs_row.pack(fill="x", pady=8)
        ttk.Label(jobs_row, text="Jobs Simultâneos:", font=("Segoe UI", 10, "bold")).pack(side="left")
        self.jobs_var = tk.StringVar(value=str(global_config.get("parallel_jobs")))
        ttk.Entry(jobs_row, textvariable=self.jobs_var, width=6, font=("Segoe UI", 10)).pack(side="left", padx=10)
        ttk.Label(jobs_row, text="(1-10)", font=("Segoe UI", 8), foreground="gray").pack(side="left")
        
        # --- Imagem para Vídeo ---
        image_frame = ttk.LabelFrame(container, text=" 🎬 Conversão Imagem → Vídeo ", padding=15)
        image_frame.pack(fill="x", pady=10)
        
        duration_row = ttk.Frame(image_frame)
        duration_row.pack(fill="x", pady=8)
        ttk.Label(duration_row, text="Duração (segundos):", font=("Segoe UI", 10, "bold")).pack(side="left")
        self.duration_var = tk.StringVar(value=str(global_config.get("image_to_video_duration")))
        ttk.Entry(duration_row, textvariable=self.duration_var, width=6, font=("Segoe UI", 10)).pack(side="left", padx=10)
        ttk.Label(duration_row, text="(1-60s)", font=("Segoe UI", 8), foreground="gray").pack(side="left")
        
        self.global_image_var = tk.BooleanVar(value=global_config.get("global_image_to_video_settings"))
        switch_row = ttk.Frame(image_frame)
        switch_row.pack(anchor="w", pady=(10, 0), fill="x")
        ToggleSwitch(switch_row, self.global_image_var).pack(side="left", padx=(0, 10))
        ttk.Label(switch_row, text="Aplicar globalmente em todas as abas", font=("Segoe UI", 10)).pack(side="left")



    def auto_detect_threads(self):
        """Detecta automaticamente o número ideal de threads"""
        optimal = self.cpu_count_logical
        self.threads_var.set(str(optimal))
        messagebox.showinfo("Detecção Automática", f"Detectado: {optimal} threads lógicas")



    def save_and_close(self):
        """Validar e salvar configurações"""
        try:
            threads = int(self.threads_var.get())
            jobs = int(self.jobs_var.get())
            duration = int(self.duration_var.get())
            
            # Verificar se parallel_jobs mudou para resetar o pool
            old_jobs = global_config.get("parallel_jobs")
            jobs_changed = (old_jobs != jobs)
            
            # Obter configurações de notificação da aba
            notification_settings = self.tab_notifications.get_settings()

            # Salvar configurações gerais
            global_config.set("num_threads", threads)
            global_config.set("parallel_jobs", jobs)
            global_config.set("image_to_video_duration", duration)
            global_config.set("global_image_to_video_settings", self.global_image_var.get())
            
            # Salvar configurações de notificação
            global_config.set("notification_sound_path", notification_settings["notification_sound_path"])
            global_config.set("notification_volume", notification_settings["notification_volume"])
            
            # Resetar o executor global se parallel_jobs mudou
            if jobs_changed:
                from modules.global_executor import global_executor
                global_executor.reset_executor()
                print(f"[Config] Pool de workers será recriado com {jobs} workers na próxima renderização")
            
            # Salvar pool global das abas
            pool_data = self.tab_pool_abas.get_pool_data()
            from modules.polls.manager import MediaPoolManager
            self.editor_ui.global_tab_pool = MediaPoolManager.from_dict(pool_data)
            
            messagebox.showinfo("Sucesso", "✓ Configurações salvas com sucesso!\n\nAs mudanças foram aplicadas imediatamente.")
            self.destroy()
            
        except ValueError:
            messagebox.showerror("Erro de Validação", "Por favor, insira apenas números válidos.")

    def _center_window(self):
        """Centraliza a janela na tela"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
