import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import psutil
from modules.config_global import global_config
from ui.dialog_imagem_video import DialogImagemVideo
from ui.componentes_custom import ToggleSwitch
from ui.lotes_in_videos import LotesInVideos


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
        self.tab_notifications = ttk.Frame(self.notebook, padding=15)
        self.tab_lotes = LotesInVideos(self.notebook, self.editor_ui)
        
        self.notebook.add(self.tab_general, text=" ⚙️ Geral ")
        self.notebook.add(self.tab_notifications, text=" 🔔 Notificações ")
        self.notebook.add(self.tab_lotes, text=" 📦 Lotes ")
        
        # Preencher abas
        self._create_general_tab()
        self._create_notifications_tab()
        
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

    def _create_notifications_tab(self):
        container = self.tab_notifications
        
        # --- Som de Notificação ---
        sound_frame = ttk.LabelFrame(container, text=" 🎵 Som da Notificação ", padding=15)
        sound_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(sound_frame, text="Escolha um som da galeria:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        # Dropdown para sons locais
        self.local_sounds_var = tk.StringVar()
        local_sounds_row = ttk.Frame(sound_frame)
        local_sounds_row.pack(fill="x", pady=5)
        
        # Listar arquivos na pasta audio_notification
        sounds_dir = os.path.join(os.getcwd(), "audio_notification")
        available_sounds = ["🔇 Sem Som (Mudo)", "Vazio (Usar Padrão do Sistema)"]
        if os.path.exists(sounds_dir):
            files = [f for f in os.listdir(sounds_dir) if f.endswith(('.mp3', '.wav', '.oga', '.ogg'))]
            available_sounds.extend(sorted(files))
        
        self.sound_dropdown = ttk.Combobox(
            local_sounds_row, 
            values=available_sounds, 
            textvariable=self.local_sounds_var,
            state="readonly"
        )
        self.sound_dropdown.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Tentar selecionar o som atual se ele estiver na pasta local
        current_path = global_config.get("notification_sound_path")
        if current_path == "mute":
            self.local_sounds_var.set("🔇 Sem Som (Mudo)")
        elif current_path:
            filename = os.path.basename(current_path)
            if filename in available_sounds:
                self.local_sounds_var.set(filename)
            else:
                self.local_sounds_var.set(available_sounds[1]) # Vazio
        else:
            self.local_sounds_var.set(available_sounds[1]) # Vazio
            
        # Botão para som externo
        self.sound_path_var = tk.StringVar(value=current_path if current_path != "mute" else "")
        ttk.Button(
            local_sounds_row,
            text="📁 Externo",
            width=10,
            command=self.browse_sound
        ).pack(side="left")

        # --- Volume ---
        volume_frame = ttk.LabelFrame(container, text=" 🔊 Volume e Teste ", padding=15)
        volume_frame.pack(fill="x", pady=10)
        
        volume_row = ttk.Frame(volume_frame)
        volume_row.pack(fill="x", pady=8)
        ttk.Label(volume_row, text="Volume:", font=("Segoe UI", 10, "bold")).pack(side="left")
        
        self.volume_var = tk.DoubleVar(value=global_config.get("notification_volume"))
        volume_scale = ttk.Scale(volume_row, from_=0.0, to=1.0, orient="horizontal", variable=self.volume_var)
        volume_scale.pack(side="left", fill="x", expand=True, padx=10)
        
        self.vol_label_var = tk.StringVar(value=f"{int(self.volume_var.get()*100)}%")
        self.volume_var.trace_add("write", lambda *args: self.vol_label_var.set(f"{int(self.volume_var.get()*100)}%"))
        ttk.Label(volume_row, textvariable=self.vol_label_var, font=("Segoe UI", 8), width=4).pack(side="left")
        
        # Botão Testar com borda de destaque
        test_btn = ttk.Button(
            volume_frame,
            text="📣 Testar Som Agora",
            command=self.test_notification,
            style="Accent.TButton"
        )
        test_btn.pack(pady=(10, 0), fill="x")

    def auto_detect_threads(self):
        """Detecta automaticamente o número ideal de threads"""
        optimal = self.cpu_count_logical
        self.threads_var.set(str(optimal))
        messagebox.showinfo("Detecção Automática", f"Detectado: {optimal} threads lógicas")

    def browse_sound(self):
        filename = filedialog.askopenfilename(
            title="Selecionar Som de Notificação",
            filetypes=[("Arquivos de Áudio", "*.wav *.oga *.mp3 *.ogg"), ("Todos os arquivos", "*.*")]
        )
        if filename:
            self.sound_path_var.set(filename)
            self.local_sounds_var.set("Arquivo Personalizado (Externo)")
            if "Arquivo Personalizado (Externo)" not in self.sound_dropdown['values']:
                vals = list(self.sound_dropdown['values'])
                vals.append("Arquivo Personalizado (Externo)")
                self.sound_dropdown['values'] = vals

    def test_notification(self):
        from modules.notifier import Notifier
        old_vol = global_config.get("notification_volume")
        global_config.settings["notification_volume"] = self.volume_var.get()
        
        # Determinar qual som tocar
        selected = self.local_sounds_var.get()
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        
        if selected == "🔇 Sem Som (Mudo)":
            path = "mute"
        elif selected == "Vazio (Usar Padrão do Sistema)":
            path = None
        elif selected == "Arquivo Personalizado (Externo)":
            path = self.sound_path_var.get()
        else:
            path = os.path.join(project_root, "audio_notification", selected)
            
        Notifier.notify("Teste de Som", f"Tocando: {selected}", sound_path=path)
        global_config.settings["notification_volume"] = old_vol

    def save_and_close(self):
        """Validar e salvar configurações"""
        try:
            threads = int(self.threads_var.get())
            jobs = int(self.jobs_var.get())
            duration = int(self.duration_var.get())
            
            # Determinar path final do som
            selected = self.local_sounds_var.get()
            if selected == "🔇 Sem Som (Mudo)":
                sound_path = "mute"
            elif selected == "Vazio (Usar Padrão do Sistema)":
                sound_path = ""
            elif selected == "Arquivo Personalizado (Externo)":
                sound_path = self.sound_path_var.get()
            else:
                sound_path = os.path.join("audio_notification", selected)

            # Salvar
            global_config.set("num_threads", threads)
            global_config.set("parallel_jobs", jobs)
            global_config.set("image_to_video_duration", duration)
            global_config.set("global_image_to_video_settings", self.global_image_var.get())
            global_config.set("notification_sound_path", sound_path)
            global_config.set("notification_volume", self.volume_var.get())
            
            messagebox.showinfo("Sucesso", "✓ Configurações salvas com sucesso!")
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
