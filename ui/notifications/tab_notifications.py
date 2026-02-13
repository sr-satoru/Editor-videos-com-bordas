import os
import tkinter as tk
from tkinter import ttk, filedialog
from modules.config_global import global_config


class TabNotifications(ttk.Frame):
    """Aba de configurações de notificações"""
    
    def __init__(self, parent):
        super().__init__(parent, padding=15)
        
        # Variáveis de controle
        self.sound_path_var = tk.StringVar()
        self.local_sounds_var = tk.StringVar()
        self.volume_var = tk.DoubleVar(value=global_config.get("notification_volume"))
        self.vol_label_var = tk.StringVar()
        
        self._setup_ui()
        self._load_current_settings()
    
    def _setup_ui(self):
        """Configura a interface da aba de notificações"""
        # --- Som de Notificação ---
        sound_frame = ttk.LabelFrame(self, text=" 🎵 Som da Notificação ", padding=15)
        sound_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(sound_frame, text="Escolha um som da galeria:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        # Dropdown para sons locais
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
        
        # Botão para som externo
        ttk.Button(
            local_sounds_row,
            text="📁 Externo",
            width=10,
            command=self.browse_sound
        ).pack(side="left")

        # --- Volume ---
        volume_frame = ttk.LabelFrame(self, text=" 🔊 Volume e Teste ", padding=15)
        volume_frame.pack(fill="x", pady=10)
        
        volume_row = ttk.Frame(volume_frame)
        volume_row.pack(fill="x", pady=8)
        ttk.Label(volume_row, text="Volume:", font=("Segoe UI", 10, "bold")).pack(side="left")
        
        volume_scale = ttk.Scale(volume_row, from_=0.0, to=1.0, orient="horizontal", variable=self.volume_var)
        volume_scale.pack(side="left", fill="x", expand=True, padx=10)
        
        self.vol_label_var.set(f"{int(self.volume_var.get()*100)}%")
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
    
    def _load_current_settings(self):
        """Carrega as configurações atuais do global_config"""
        current_path = global_config.get("notification_sound_path")
        
        # Obter lista de sons disponíveis
        available_sounds = list(self.sound_dropdown['values'])
        
        if current_path == "mute":
            self.local_sounds_var.set("🔇 Sem Som (Mudo)")
        elif current_path:
            filename = os.path.basename(current_path)
            if filename in available_sounds:
                self.local_sounds_var.set(filename)
            else:
                # Arquivo externo
                self.sound_path_var.set(current_path)
                self.local_sounds_var.set("Arquivo Personalizado (Externo)")
                if "Arquivo Personalizado (Externo)" not in available_sounds:
                    vals = list(available_sounds)
                    vals.append("Arquivo Personalizado (Externo)")
                    self.sound_dropdown['values'] = vals
        else:
            self.local_sounds_var.set("Vazio (Usar Padrão do Sistema)")
    
    def browse_sound(self):
        """Abre diálogo para selecionar arquivo de som externo"""
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
        """Testa o som de notificação com as configurações atuais"""
        from modules.notifier import Notifier
        
        # Salvar volume antigo e aplicar temporariamente o novo
        old_vol = global_config.get("notification_volume")
        global_config.settings["notification_volume"] = self.volume_var.get()
        
        # Determinar qual som tocar
        selected = self.local_sounds_var.get()
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        
        if selected == "🔇 Sem Som (Mudo)":
            path = "mute"
        elif selected == "Vazio (Usar Padrão do Sistema)":
            path = None
        elif selected == "Arquivo Personalizado (Externo)":
            path = self.sound_path_var.get()
        else:
            path = os.path.join(project_root, "audio_notification", selected)
        
        Notifier.notify("Teste de Som", f"Tocando: {selected}", sound_path=path)
        
        # Restaurar volume antigo
        global_config.settings["notification_volume"] = old_vol
    
    def get_settings(self):
        """Retorna as configurações atuais para serem salvas"""
        selected = self.local_sounds_var.get()
        
        if selected == "🔇 Sem Som (Mudo)":
            sound_path = "mute"
        elif selected == "Vazio (Usar Padrão do Sistema)":
            sound_path = ""
        elif selected == "Arquivo Personalizado (Externo)":
            sound_path = self.sound_path_var.get()
        else:
            sound_path = os.path.join("audio_notification", selected)
        
        return {
            "notification_sound_path": sound_path,
            "notification_volume": self.volume_var.get()
        }
