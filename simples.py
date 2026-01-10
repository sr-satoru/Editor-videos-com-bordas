import os
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from moviepy.video.fx.all import resize
import numpy as np
import json
from datetime import datetime
import tempfile

class ProfessionalVideoEditorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor Profissional de Vídeo 9:16 - Sistema Multi-Abas")
        
        # Configurar variáveis de ambiente
        self.setup_environment_variables()

        # Sistema de abas
        self.tabs = []
        self.current_tab_index = 0
        
        # Configurar interface principal
        self.setup_main_ui()

    def setup_environment_variables(self):
        """Configura variáveis de ambiente padrão"""
        if not os.getenv("DEFAULT_OUTPUT_PATH"):
            os.environ["DEFAULT_OUTPUT_PATH"] = os.path.join(os.getcwd(), "output")
        if not os.getenv("DEFAULT_FONT_PATH"):
            os.environ["DEFAULT_FONT_PATH"] = "arial.ttf"
        if not os.getenv("DEFAULT_FONT_FAMILY"):
            os.environ["DEFAULT_FONT_FAMILY"] = "Arial"
        if not os.getenv("DEFAULT_CONFIG_PATH"):
            os.environ["DEFAULT_CONFIG_PATH"] = os.path.join(os.getcwd(), "configs")
        if not os.getenv("MOVIEPY_TEMP_DIR"):
            os.environ["MOVIEPY_TEMP_DIR"] = os.path.join(os.getcwd(), "temp")
        if not os.getenv("MOVIEPY_VIDEO_CODEC"):
            os.environ["MOVIEPY_VIDEO_CODEC"] = "libx264"
        if not os.getenv("MOVIEPY_AUDIO_CODEC"):
            os.environ["MOVIEPY_AUDIO_CODEC"] = "aac"

    def setup_main_ui(self):
        """Configura a interface principal com sistema de abas"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sistema de abas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind para detectar mudança de aba
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Controles globais (fora das abas)
        self.setup_global_controls(main_frame)
        
        # Criar primeira aba
        self.create_new_tab()

    def setup_global_controls(self, parent):
        """Configura controles globais que afetam todas as abas"""
        global_frame = ttk.LabelFrame(parent, text="🌐 Controles Globais")
        global_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Frame para botões
        buttons_frame = ttk.Frame(global_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Botão para adicionar nova aba
        ttk.Button(buttons_frame, text="➕ Nova Aba", 
                  command=self.create_new_tab).pack(side=tk.LEFT, padx=5)
        
        # Botão para remover aba atual
        ttk.Button(buttons_frame, text="🗑️ Remover Aba", 
                  command=self.remove_current_tab).pack(side=tk.LEFT, padx=5)
        
        # Botão para renderizar todas as abas
        ttk.Button(buttons_frame, text="🎬 Renderizar Todas as Abas", 
                  command=self.render_all_tabs, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        
        # Informações sobre abas
        self.tabs_info_label = ttk.Label(buttons_frame, text="Aba 1 ativa")
        self.tabs_info_label.pack(side=tk.RIGHT, padx=5)
        
        # Frame para controles de configuração
        config_frame = ttk.Frame(global_frame)
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Botões para salvar e importar configurações
        ttk.Button(config_frame, text="💾 Salvar Configuração", 
                  command=self.save_configuration).pack(side=tk.LEFT, padx=5)
        ttk.Button(config_frame, text="📂 Importar Configuração", 
                  command=self.load_configuration).pack(side=tk.LEFT, padx=5)
        ttk.Button(config_frame, text="🔄 Aplicar Configuração", 
                  command=self.apply_configuration).pack(side=tk.LEFT, padx=5)
        
        # Botão para carregar vídeo em todas as abas
        ttk.Button(config_frame, text="🎥 Carregar Vídeo em Todas as Abas", 
                  command=self.load_video_all_tabs).pack(side=tk.LEFT, padx=5)
        
        # Botão para alterar caminho de saída de todas as abas
        ttk.Button(config_frame, text="📁 Alterar Saída de Todas as Abas", 
                  command=self.change_output_path_all_tabs).pack(side=tk.LEFT, padx=5)
        
        # Botão para aplicar bordas em todas as abas
        ttk.Button(config_frame, text="🖼️ Aplicar Bordas em Todas as Abas", 
                  command=self.apply_borders_all_tabs).pack(side=tk.LEFT, padx=5)

    def save_configuration(self):
        """Salva a configuração atual em um arquivo JSON"""
        if not self.tabs:
            messagebox.showwarning("Aviso", "Não há abas para salvar!")
            return
        
        # Verifica se pelo menos uma aba tem legendas
        has_subtitles = False
        for tab in self.tabs:
            if tab.subtitles:
                has_subtitles = True
                break
        
        if not has_subtitles:
            messagebox.showwarning("Aviso", "Adicione pelo menos uma legenda em alguma aba antes de salvar!")
            return
        
        # Solicita local para salvar
        config_dir = os.getenv("DEFAULT_CONFIG_PATH", os.path.join(os.getcwd(), "configs"))
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"config_video_{timestamp}.json"
        
        file_path = filedialog.asksaveasfilename(
            title="Salvar Configuração",
            initialdir=config_dir,
            initialfile=default_filename,
            defaultextension=".json",
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Prepara dados para salvar
            config_data = {
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.1",
                    "description": "Configuração de legendas e abas do Editor de Vídeo"
                },
                "global_settings": {
                    "default_output_path": os.getenv("DEFAULT_OUTPUT_PATH", ""),
                    "moviepy_temp_dir": os.getenv("MOVIEPY_TEMP_DIR", ""),
                    "moviepy_video_codec": os.getenv("MOVIEPY_VIDEO_CODEC", "libx264"),
                    "moviepy_audio_codec": os.getenv("MOVIEPY_AUDIO_CODEC", "aac")
                },
                "tabs": []
            }
            
            # Salva dados de cada aba
            for i, tab in enumerate(self.tabs):
                tab_data = {
                    "tab_index": i,
                    "tab_name": f"Aba {i + 1}",
                    "video_path": tab.video_path.get(),
                    "output_path": tab.output_path.get(),
                    "process_folder": tab.process_folder.get(),
                    "subtitles": tab.subtitles.copy(),
                    "font_settings": {
                        "font_family": tab.font_family.get(),
                        "font_size": tab.font_size.get(),
                        "font_color": tab.font_color.get(),
                        "border_color": tab.border_color.get(),
                        "bg_color": tab.bg_color.get(),
                        "border_thickness": tab.subtitle_border_thickness.get()
                    },
                    "performance_settings": {
                        "cpu_threads": tab.cpu_threads.get()
                    },
                    "emoji_settings": {
                        "emoji_folder": tab.emoji_folder.get(),
                        "emoji_scale": tab.emoji_scale.get()
                    },
                    "video_border_settings": {
                        "enabled": tab.video_border_enabled.get(),
                        "color": tab.video_border_color.get(),
                        "size": tab.video_border_size.get(),
                        "style": tab.video_border_style.get()
                    }
                }
                config_data["tabs"].append(tab_data)
            
            # Salva no arquivo
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Sucesso", f"Configuração salva com sucesso!\nArquivo: {file_path}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configuração: {e}")

    def load_configuration(self):
        """Carrega uma configuração de um arquivo JSON"""
        config_dir = os.getenv("DEFAULT_CONFIG_PATH", os.path.join(os.getcwd(), "configs"))
        
        file_path = filedialog.askopenfilename(
            title="Carregar Configuração",
            initialdir=config_dir,
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Armazena a configuração carregada
            self.loaded_config = config_data
            
            # Mostra informações da configuração
            num_tabs = len(config_data.get("tabs", []))
            total_subtitles = sum(len(tab.get("subtitles", [])) for tab in config_data.get("tabs", []))
            
            messagebox.showinfo("Configuração Carregada", 
                              f"Configuração carregada com sucesso!\n\n"
                              f"📊 Abas: {num_tabs}\n"
                              f"📝 Total de legendas: {total_subtitles}\n"
                              f"📁 Arquivo: {os.path.basename(file_path)}\n\n"
                              f"Clique em 'Aplicar Configuração' para usar.")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar configuração: {e}")

    def apply_configuration(self):
        """Aplica a configuração carregada"""
        if not hasattr(self, 'loaded_config'):
            messagebox.showwarning("Aviso", "Carregue uma configuração primeiro!")
            return
        
        try:
            config_data = self.loaded_config
            
            # Aplica configurações globais se existirem
            global_settings = config_data.get("global_settings", {})
            if global_settings:
                if global_settings.get("default_output_path"):
                    os.environ["DEFAULT_OUTPUT_PATH"] = global_settings["default_output_path"]
                if global_settings.get("moviepy_temp_dir"):
                    os.environ["MOVIEPY_TEMP_DIR"] = global_settings["moviepy_temp_dir"]
                if global_settings.get("moviepy_video_codec"):
                    os.environ["MOVIEPY_VIDEO_CODEC"] = global_settings["moviepy_video_codec"]
                if global_settings.get("moviepy_audio_codec"):
                    os.environ["MOVIEPY_AUDIO_CODEC"] = global_settings["moviepy_audio_codec"]
            
            # Confirma a aplicação
            num_tabs = len(config_data.get("tabs", []))
            global_info = "✅ Configurações globais incluídas" if global_settings else "⚠️  Sem configurações globais"
            if not messagebox.askyesno("Confirmar", 
                                     f"Aplicar configuração com {num_tabs} abas?\n"
                                     f"{global_info}\n\n"
                                     "Isso substituirá a configuração atual."):
                return
            
            # Remove abas existentes (exceto a primeira)
            while len(self.tabs) > 1:
                self.notebook.forget(1)
                removed_tab = self.tabs.pop(1)
                del removed_tab
            
            # Limpa a primeira aba
            first_tab = self.tabs[0]
            first_tab.subtitles.clear()
            first_tab.selected_subtitle_idx = None
            first_tab.update_subtitles_listbox()
            
            # Aplica configuração para cada aba
            for i, tab_data in enumerate(config_data.get("tabs", [])):
                if i == 0:
                    # Aplica na primeira aba
                    self.apply_tab_configuration(first_tab, tab_data)
                else:
                    # Cria novas abas
                    self.create_new_tab()
                    new_tab = self.tabs[-1]
                    self.apply_tab_configuration(new_tab, tab_data)
            
            # Atualiza interface
            self.update_tabs_info()
            self.notebook.select(0)
            
            messagebox.showinfo("Sucesso", "Configuração aplicada com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao aplicar configuração: {e}")

    def apply_tab_configuration(self, tab, tab_data):
        """Aplica configuração em uma aba específica"""
        # Aplica configurações básicas
        tab.video_path.set(tab_data.get("video_path", ""))
        tab.output_path.set(tab_data.get("output_path", os.getenv("DEFAULT_OUTPUT_PATH", os.getcwd())))
        tab.process_folder.set(tab_data.get("process_folder", False))
        
        # Aplica configurações de fonte
        font_settings = tab_data.get("font_settings", {})
        tab.font_family.set(font_settings.get("font_family", "Arial Black"))
        tab.font_size.set(font_settings.get("font_size", 12))
        tab.font_color.set(font_settings.get("font_color", "#FFFFFF"))
        tab.border_color.set(font_settings.get("border_color", "#000000"))
        tab.bg_color.set(font_settings.get("bg_color", "#000000"))
        tab.subtitle_border_thickness.set(font_settings.get("border_thickness", 2))
        
        # Aplica configurações de performance
        performance_settings = tab_data.get("performance_settings", {})
        tab.cpu_threads.set(performance_settings.get("cpu_threads", 4))
        
        # Atualiza labels de cor
        tab.font_color_label.config(bg=tab.font_color.get())
        tab.border_color_label.config(bg=tab.border_color.get())
        tab.bg_color_label.config(bg=tab.bg_color.get())
        
        # Aplica configurações de emoji
        emoji_settings = tab_data.get("emoji_settings", {})
        tab.emoji_folder.set(emoji_settings.get("emoji_folder", ""))
        tab.emoji_scale.set(emoji_settings.get("emoji_scale", 1.0))
        
        # Carrega emojis se a pasta existir
        if tab.emoji_folder.get() and os.path.exists(tab.emoji_folder.get()):
            tab.load_emoji_images()
        
        # Aplica configurações de borda do vídeo
        border_settings = tab_data.get("video_border_settings", {})
        tab.video_border_enabled.set(border_settings.get("enabled", False))
        tab.video_border_color.set(border_settings.get("color", "#FFFFFF"))
        tab.video_border_size.set(border_settings.get("size", 50))
        tab.video_border_style.set(border_settings.get("style", "uniforme"))
        
        # Atualiza label da cor da borda do vídeo
        if hasattr(tab, 'video_border_color_label'):
            tab.video_border_color_label.config(bg=tab.video_border_color.get())
        
        # Aplica legendas
        tab.subtitles = tab_data.get("subtitles", []).copy()
        tab.subtitle_counter = max([sub.get("id", 0) for sub in tab.subtitles], default=0)
        
        # Atualiza interface
        tab.update_subtitles_listbox()
        tab.update_preview()
        
        # Abre vídeo se existir
        if tab.video_path.get() and os.path.exists(tab.video_path.get()):
            tab.open_video(tab.video_path.get())

    def load_video_all_tabs(self):
        """Carrega um vídeo em todas as abas"""
        if not self.tabs:
            messagebox.showwarning("Aviso", "Não há abas para carregar o vídeo!")
            return
        
        # Solicita seleção do vídeo
        file_path = filedialog.askopenfilename(
            title="Selecione um vídeo para carregar em todas as abas",
            filetypes=[("Vídeos", "*.mp4 *.avi *.mov *.mkv *.wmv"), ("Todos os arquivos", "*.*")]
        )
        
        if not file_path:
            return
        
        # Confirma a operação
        if not messagebox.askyesno("Confirmar", 
                                 f"Carregar o vídeo '{os.path.basename(file_path)}' em todas as {len(self.tabs)} abas?"):
            return
        
        try:
            # Carrega o vídeo em todas as abas
            for i, tab in enumerate(self.tabs):
                tab.video_path.set(file_path)
                tab.open_video(file_path)
                tab.update_preview()
                
                # Atualiza status
                tab.status_label.config(text=f"Vídeo carregado: {os.path.basename(file_path)}")
            
            messagebox.showinfo("Sucesso", f"Vídeo carregado em {len(self.tabs)} abas!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar vídeo: {e}")

    def change_output_path_all_tabs(self):
        """Altera o caminho de saída de todas as abas"""
        if not self.tabs:
            messagebox.showwarning("Aviso", "Não há abas para alterar!")
            return
        
        # Mostra o caminho atual da primeira aba como referência
        current_path = self.tabs[0].output_path.get() if self.tabs else os.getenv("DEFAULT_OUTPUT_PATH", os.getcwd())
        
        # Solicita seleção da nova pasta de saída
        new_output_path = filedialog.askdirectory(
            title="Selecione a nova pasta de saída para TODAS as abas",
            initialdir=current_path
        )
        
        if not new_output_path:
            return
        
        # Confirma a operação
        if not messagebox.askyesno("Confirmar Alteração Global", 
                                 f"Alterar o caminho de saída de TODAS as {len(self.tabs)} abas para:\n\n"
                                 f"📁 {new_output_path}\n\n"
                                 f"Esta operação irá substituir os caminhos atuais de todas as abas.\n"
                                 f"Deseja continuar?"):
            return
        
        try:
            # Verifica se a pasta existe, se não, cria
            if not os.path.exists(new_output_path):
                os.makedirs(new_output_path)
                messagebox.showinfo("Pasta Criada", f"Pasta criada: {new_output_path}")
            
            # Atualiza todas as abas
            updated_count = 0
            for i, tab in enumerate(self.tabs):
                old_path = tab.output_path.get()
                tab.output_path.set(new_output_path)
                updated_count += 1
                
                # Log da alteração para debug
                print(f"Aba {i+1}: {old_path} → {new_output_path}")
            
            # Também atualiza a variável de ambiente padrão
            os.environ["DEFAULT_OUTPUT_PATH"] = new_output_path
            
            messagebox.showinfo("Sucesso", 
                              f"✅ Caminho de saída alterado com sucesso!\n\n"
                              f"📊 Abas atualizadas: {updated_count}\n"
                              f"📁 Nova pasta: {new_output_path}\n\n"
                              f"Todas as renderizações futuras usarão este caminho.")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao alterar caminhos de saída: {e}")

    def apply_borders_all_tabs(self):
        """Aplica configurações de borda em todas as abas"""
        if not self.tabs:
            messagebox.showwarning("Aviso", "Não há abas para aplicar bordas!")
            return
        
        # Cria janela de configuração de bordas
        border_window = tk.Toplevel(self.main_app.root)
        border_window.title("Aplicar Bordas em Todas as Abas")
        border_window.geometry("400x300")
        border_window.transient(self.main_app.root)
        border_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(border_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        ttk.Label(main_frame, text="Configurações de Borda para Todas as Abas", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        # Controles
        ttk.Checkbutton(main_frame, text="🖼️ Adicionar Borda ao Vídeo", 
                       variable=self.tabs[0].video_border_enabled).pack(anchor=tk.W, pady=5)
        
        # Frame para cor e tamanho
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(controls_frame, text="Cor da Borda:").pack(anchor=tk.W)
        color_frame = ttk.Frame(controls_frame)
        color_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(color_frame, text="🎨 Escolher", 
                  command=lambda: self.choose_global_border_color()).pack(side=tk.LEFT)
        self.global_border_color_label = tk.Label(color_frame, bg=self.tabs[0].video_border_color.get(), 
                                                 width=3, relief=tk.RAISED)
        self.global_border_color_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(controls_frame, text="Tamanho (px):").pack(anchor=tk.W, pady=(10, 5))
        ttk.Spinbox(controls_frame, from_=10, to=200, 
                   textvariable=self.tabs[0].video_border_size, width=8).pack(anchor=tk.W)
        
        ttk.Label(controls_frame, text="Estilo:").pack(anchor=tk.W, pady=(10, 5))
        border_styles = ["uniforme", "arredondada", "degradê"]
        ttk.Combobox(controls_frame, textvariable=self.tabs[0].video_border_style, 
                    values=border_styles, width=15).pack(anchor=tk.W)
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="✅ Aplicar em Todas as Abas", 
                  command=lambda: self.confirm_apply_borders_all_tabs(border_window)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Cancelar", 
                  command=border_window.destroy).pack(side=tk.RIGHT, padx=5)

    def choose_global_border_color(self):
        """Escolhe cor da borda para todas as abas"""
        color = colorchooser.askcolor(title="Escolha a cor da borda para todas as abas", 
                                    initialcolor=self.tabs[0].video_border_color.get())
        if color and color[1]:
            self.tabs[0].video_border_color.set(color[1])
            self.global_border_color_label.config(bg=color[1])

    def confirm_apply_borders_all_tabs(self, window):
        """Confirma e aplica bordas em todas as abas"""
        if not messagebox.askyesno("Confirmar", 
                                 f"Aplicar configurações de borda em TODAS as {len(self.tabs)} abas?\n\n"
                                 f"🖼️ Borda: {'Ativada' if self.tabs[0].video_border_enabled.get() else 'Desativada'}\n"
                                 f"🎨 Cor: {self.tabs[0].video_border_color.get()}\n"
                                 f"📏 Tamanho: {self.tabs[0].video_border_size.get()}px\n"
                                 f"🎭 Estilo: {self.tabs[0].video_border_style.get()}"):
            return
        
        try:
            # Aplica em todas as abas
            for i, tab in enumerate(self.tabs):
                tab.video_border_enabled.set(self.tabs[0].video_border_enabled.get())
                tab.video_border_color.set(self.tabs[0].video_border_color.get())
                tab.video_border_size.set(self.tabs[0].video_border_size.get())
                tab.video_border_style.set(self.tabs[0].video_border_style.get())
                
                # Atualiza label da cor se existir
                if hasattr(tab, 'video_border_color_label'):
                    tab.video_border_color_label.config(bg=tab.video_border_color.get())
            
            window.destroy()
            messagebox.showinfo("Sucesso", f"Configurações de borda aplicadas em {len(self.tabs)} abas!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao aplicar bordas: {e}")

    def create_new_tab(self):
        """Cria uma nova aba"""
        tab_index = len(self.tabs)
        tab_name = f"Aba {tab_index + 1}"
        
        # Criar frame da aba
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=tab_name)
        
        # Criar instância da aba
        tab_instance = VideoTab(tab_frame, tab_index, self)
        self.tabs.append(tab_instance)
        
        # Se não for a primeira aba, herda configurações da primeira
        if tab_index > 0 and len(self.tabs) > 1:
            first_tab = self.tabs[0]
            tab_instance.inherit_from_tab(first_tab)
        
        # Atualizar informações
        self.update_tabs_info()
        
        # Selecionar a nova aba
        self.notebook.select(tab_index)
        self.current_tab_index = tab_index

    def remove_current_tab(self):
        """Remove a aba atual"""
        if len(self.tabs) <= 1:
            messagebox.showwarning("Aviso", "Não é possível remover a última aba!")
            return
        
        current_index = self.notebook.index(self.notebook.select())
        
        if messagebox.askyesno("Confirmar", f"Remover {self.notebook.tab(current_index, 'text')}?"):
            # Remove a aba do notebook
            self.notebook.forget(current_index)
            
            # Remove da lista
            removed_tab = self.tabs.pop(current_index)
            del removed_tab
            
            # Renomear abas restantes
            for i, tab in enumerate(self.tabs):
                tab.tab_index = i
                self.notebook.tab(i, text=f"Aba {i + 1}")
            
            # Atualizar informações
            self.update_tabs_info()

    def on_tab_changed(self, event):
        """Callback quando a aba é alterada"""
        self.current_tab_index = self.notebook.index(self.notebook.select())
        self.update_tabs_info()

    def update_tabs_info(self):
        """Atualiza informações sobre as abas"""
        current_tab = self.current_tab_index + 1
        total_tabs = len(self.tabs)
        self.tabs_info_label.config(text=f"Aba {current_tab} de {total_tabs} ativa")

    def render_all_tabs(self):
        """Renderiza todas as abas em fila"""
        if not self.tabs:
            messagebox.showerror("Erro", "Não há abas para renderizar!")
            return
        
        # Verificar se pelo menos uma aba tem legendas
        has_subtitles = False
        for tab in self.tabs:
            if tab.subtitles:
                has_subtitles = True
                break
        
        if not has_subtitles:
            messagebox.showerror("Erro", "Adicione pelo menos uma legenda em alguma aba!")
            return
        
        # Verificar se pelo menos uma aba tem vídeo
        has_video = False
        for tab in self.tabs:
            if tab.video_path.get():
                has_video = True
                break
        
        if not has_video:
            messagebox.showerror("Erro", "Selecione um vídeo em pelo menos uma aba!")
            return
        

        
        # Iniciar renderização em thread separada
        import threading
        self.render_thread = threading.Thread(target=self.render_all_tabs_thread)
        self.render_thread.daemon = True
        self.render_thread.start()

    def render_all_tabs_thread(self):
        """Thread para renderizar todas as abas"""
        try:
            total_tabs = len(self.tabs)
            
            for i, tab in enumerate(self.tabs):
                if not tab.video_path.get() or not tab.subtitles:
                    continue
                
                # Atualizar status
                tab.status_label.config(text=f"Renderizando Aba {i+1}/{total_tabs}...")
                tab.progress_var.set(0)
                self.root.update_idletasks()
                
                # Renderizar a aba
                tab.render_video()
                
                # Pequena pausa entre renderizações
                import time
                time.sleep(1)
            
            messagebox.showinfo("Sucesso", f"Todas as {total_tabs} versões foram renderizadas!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro durante a renderização: {e}")

class VideoTab:
    def __init__(self, parent, tab_index, main_app):
        self.parent = parent
        self.tab_index = tab_index
        self.main_app = main_app
        
        # Variáveis principais
        self.video_path = tk.StringVar()
        self.process_folder = tk.BooleanVar()
        self.subtitle_text = tk.StringVar()
        self.font_family = tk.StringVar(value=os.getenv("DEFAULT_FONT_FAMILY", "Arial Black"))
        self.font_size = tk.IntVar(value=12)
        self.font_color = tk.StringVar(value="#FFFFFF")
        self.border_color = tk.StringVar(value="#000000")
        self.bg_color = tk.StringVar(value="#000000")
        self.output_path = tk.StringVar(value=os.getenv("DEFAULT_OUTPUT_PATH", os.getcwd()))
        
        # Sistema de emojis
        self.emoji_folder = tk.StringVar()
        self.emoji_images = {}
        self.selected_emoji = None
        self.emoji_scale = tk.DoubleVar(value=1.0)

        # Sistema de bordas do vídeo
        self.video_border_enabled = tk.BooleanVar(value=False)
        self.video_border_color = tk.StringVar(value="#FFFFFF")
        self.video_border_size = tk.IntVar(value=50)
        self.video_border_style = tk.StringVar(value="uniforme")

        # Variáveis para o preview do vídeo
        self.video_clip = None
        self.current_frame = None
        self.preview_image = None

        # Sistema de bordas das legendas
        self.subtitle_border_thickness = tk.IntVar(value=2)  # Espessura da borda das legendas

        # Controle de performance da CPU
        self.cpu_threads = tk.IntVar(value=4)  # Número de threads da CPU para renderização

        # Lista de legendas com IDs únicos
        self.subtitles = []
        self.subtitle_counter = 0

        # Para arrastar legendas
        self.dragging_subtitle_idx = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.selected_subtitle_idx = None

        # Configurar interface da aba
        self.setup_tab_ui()

    def inherit_from_tab(self, source_tab):
        """Herdar configurações de outra aba"""
        # Herda vídeo e caminho de saída
        self.video_path.set(source_tab.video_path.get())
        self.output_path.set(source_tab.output_path.get())
        
        # Herda configurações de borda
        self.video_border_enabled.set(source_tab.video_border_enabled.get())
        self.video_border_color.set(source_tab.video_border_color.get())
        self.video_border_size.set(source_tab.video_border_size.get())
        self.video_border_style.set(source_tab.video_border_style.get())
        
        # Herda configurações de borda das legendas
        self.subtitle_border_thickness.set(source_tab.subtitle_border_thickness.get())
        
        # Herda configurações de performance
        self.cpu_threads.set(source_tab.cpu_threads.get())
        
        # Atualiza label da cor da borda
        if hasattr(self, 'video_border_color_label'):
            self.video_border_color_label.config(bg=self.video_border_color.get())
        
        # Abre o vídeo se existir
        if self.video_path.get():
            self.open_video(self.video_path.get())
            self.update_preview()

    def setup_tab_ui(self):
        """Configura a interface da aba"""
        # Frame principal com scroll
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(main_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)

        inner_frame = ttk.Frame(canvas)
        inner_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        # Área de preview profissional
        self.setup_preview_area(inner_frame)
        
        # Controles de vídeo
        self.setup_video_controls(inner_frame)
        
        # Editor de legendas profissional
        self.setup_subtitle_editor(inner_frame)
        
        # Lista de legendas com controles
        self.setup_subtitles_list(inner_frame)
        
        # Controles de saída
        self.setup_output_controls(inner_frame)

    def setup_preview_area(self, parent):
        """Configura a área de preview profissional"""
        preview_frame = ttk.LabelFrame(parent, text="Preview 9:16 - Arraste as legendas aqui")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame para controles do preview
        preview_controls = ttk.Frame(preview_frame)
        preview_controls.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(preview_controls, text="🔄 Atualizar Preview", 
                  command=self.update_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(preview_controls, text="🎯 Centralizar Selecionada", 
                  command=self.center_selected_subtitle).pack(side=tk.LEFT, padx=5)
        ttk.Button(preview_controls, text="🖼️ Centralizar na Borda", 
                  command=self.center_subtitle_in_border).pack(side=tk.LEFT, padx=5)
        ttk.Button(preview_controls, text="🗑️ Limpar Todas", 
                  command=self.clear_all_subtitles).pack(side=tk.LEFT, padx=5)
        
        # Canvas do preview com borda (proporção 9:16 reduzida)
        self.preview_canvas = tk.Canvas(preview_frame, bg="black", width=270, height=480, 
                                       relief=tk.RAISED, bd=2)
        self.preview_canvas.pack(padx=10, pady=10)
        
        # Label para mostrar informações da borda
        self.border_info_label = ttk.Label(preview_frame, text="", font=("Arial", 8))
        self.border_info_label.pack(pady=2)
        
        # Bind eventos do mouse para arrastar legendas
        self.preview_canvas.bind("<Button-1>", self.on_preview_click)
        self.preview_canvas.bind("<B1-Motion>", self.on_preview_drag)
        self.preview_canvas.bind("<ButtonRelease-1>", self.on_preview_release)
        self.preview_canvas.bind("<Double-Button-1>", self.on_preview_double_click)

    def setup_video_controls(self, parent):
        """Configura os controles de vídeo"""
        video_frame = ttk.LabelFrame(parent, text="📹 Controles de Vídeo")
        video_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Frame para botões
        video_buttons = ttk.Frame(video_frame)
        video_buttons.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(video_buttons, text="📁 Selecionar Vídeo", 
                  command=self.select_video).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(video_buttons, text="📂 Processar toda a pasta", 
                       variable=self.process_folder).pack(side=tk.LEFT, padx=5)
        
        # Entry para mostrar o caminho do vídeo
        ttk.Entry(video_frame, textvariable=self.video_path, width=50, 
                 state="readonly").pack(fill=tk.X, padx=10, pady=5)
        
        # Sistema de bordas do vídeo
        self.setup_video_border_controls(video_frame)

    def setup_video_border_controls(self, parent):
        """Configura os controles de borda do vídeo"""
        border_frame = ttk.LabelFrame(parent, text="🖼️ Bordas do Vídeo")
        border_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Frame para controles de borda
        border_controls = ttk.Frame(border_frame)
        border_controls.pack(fill=tk.X, padx=10, pady=5)
        
        # Primeira linha - Ativar borda e estilo
        ttk.Checkbutton(border_controls, text="🖼️ Adicionar Borda ao Vídeo", 
                       variable=self.video_border_enabled).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(border_controls, text="Estilo:").grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        border_styles = ["uniforme", "arredondada", "degradê"]
        ttk.Combobox(border_controls, textvariable=self.video_border_style, 
                    values=border_styles, width=10).grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        
        # Segunda linha - Cor e tamanho da borda
        ttk.Label(border_controls, text="Cor da Borda:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        border_color_btn = ttk.Button(border_controls, text="🎨 Escolher", 
                                     command=self.choose_video_border_color)
        border_color_btn.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.video_border_color_label = tk.Label(border_controls, bg=self.video_border_color.get(), 
                                                width=3, relief=tk.RAISED)
        self.video_border_color_label.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(border_controls, text="Tamanho (px):").grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
        ttk.Spinbox(border_controls, from_=10, to=200, textvariable=self.video_border_size, 
                   width=8).grid(row=1, column=4, padx=5, pady=5, sticky=tk.W)
        
        # Botão para testar consistência
        ttk.Button(border_controls, text="🔍 Testar Consistência", 
                  command=self.test_preview_render_consistency).grid(row=1, column=5, padx=5, pady=5, sticky=tk.W)

    def setup_subtitle_editor(self, parent):
        """Configura o editor profissional de legendas"""
        subtitle_frame = ttk.LabelFrame(parent, text="✏️ Editor de Legendas")
        subtitle_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Grid para organizar os controles
        controls_frame = ttk.Frame(subtitle_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Primeira linha - Texto e Fonte
        ttk.Label(controls_frame, text="Texto:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        # Frame para o campo de texto com scroll
        text_frame = ttk.Frame(controls_frame)
        text_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # Text widget para múltiplas linhas
        self.text_widget = tk.Text(text_frame, width=60, height=3, wrap=tk.WORD)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar para o texto
        text_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.configure(yscrollcommand=text_scrollbar.set)
        
        # Bind para sincronizar com a variável
        self.text_widget.bind('<KeyRelease>', self.on_text_change)
        
        ttk.Label(controls_frame, text="Fonte:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        font_options = ["Arial", "Arial Black", "Helvetica", "Times", "Courier", "Verdana", "Impact", "Comic Sans MS"]
        ttk.Combobox(controls_frame, textvariable=self.font_family, values=font_options, width=12).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(controls_frame, text="Tamanho:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        ttk.Spinbox(controls_frame, from_=8, to=96, textvariable=self.font_size, width=5).grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        
        # Segunda linha - Cores
        ttk.Label(controls_frame, text="Cor da Fonte:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        font_color_btn = ttk.Button(controls_frame, text="🎨 Escolher", command=self.choose_font_color)
        font_color_btn.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.font_color_label = tk.Label(controls_frame, bg=self.font_color.get(), width=3, relief=tk.RAISED)
        self.font_color_label.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(controls_frame, text="Cor da Borda:").grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
        border_color_btn = ttk.Button(controls_frame, text="🎨 Escolher", command=self.choose_border_color)
        border_color_btn.grid(row=1, column=4, padx=5, pady=5, sticky=tk.W)
        self.border_color_label = tk.Label(controls_frame, bg=self.border_color.get(), width=3, relief=tk.RAISED)
        self.border_color_label.grid(row=1, column=5, padx=5, pady=5, sticky=tk.W)
        
        # Terceira linha - Fundo e espessura da borda
        ttk.Label(controls_frame, text="Cor do Fundo:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        bg_color_btn = ttk.Button(controls_frame, text="🎨 Escolher", command=self.choose_bg_color)
        bg_color_btn.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        self.bg_color_label = tk.Label(controls_frame, bg=self.bg_color.get(), width=3, relief=tk.RAISED)
        self.bg_color_label.grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(controls_frame, text="Espessura da Borda:").grid(row=2, column=3, padx=5, pady=5, sticky=tk.W)
        ttk.Spinbox(controls_frame, from_=1, to=10, textvariable=self.subtitle_border_thickness, 
                   width=5).grid(row=2, column=4, padx=5, pady=5, sticky=tk.W)
        
        # Quarta linha - Botão adicionar
        add_subtitle_btn = ttk.Button(controls_frame, text="➕ Adicionar Legenda", 
                                     command=self.add_subtitle, style="Accent.TButton")
        add_subtitle_btn.grid(row=3, column=0, columnspan=5, padx=5, pady=10, sticky=tk.W+tk.E)
        
        # Sistema de emojis
        self.setup_emoji_system(subtitle_frame)

    def setup_emoji_system(self, parent_frame):
        """Configura o sistema de emojis personalizados"""
        emoji_frame = ttk.LabelFrame(parent_frame, text="😊 Sistema de Emojis")
        emoji_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Frame para controles de emoji
        emoji_controls = ttk.Frame(emoji_frame)
        emoji_controls.pack(fill=tk.X, padx=10, pady=5)
        
        # Seleção de pasta de emojis
        ttk.Label(emoji_controls, text="Pasta de Emojis:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(emoji_controls, textvariable=self.emoji_folder, width=30, state="readonly").pack(side=tk.LEFT, padx=5)
        ttk.Button(emoji_controls, text="📁 Selecionar Pasta", 
                  command=self.select_emoji_folder).pack(side=tk.LEFT, padx=5)
        
        # Frame para visualização dos emojis
        emoji_view_frame = ttk.Frame(emoji_frame)
        emoji_view_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Canvas para mostrar os emojis
        self.emoji_canvas = tk.Canvas(emoji_view_frame, height=80, bg="white", relief=tk.SUNKEN, bd=1)
        self.emoji_canvas.pack(fill=tk.X, padx=5, pady=5)
        
        # Scrollbar para o canvas de emojis
        emoji_scrollbar = ttk.Scrollbar(emoji_view_frame, orient=tk.HORIZONTAL, command=self.emoji_canvas.xview)
        emoji_scrollbar.pack(fill=tk.X)
        self.emoji_canvas.configure(xscrollcommand=emoji_scrollbar.set)
        
        # Frame interno para os emojis
        self.emoji_inner_frame = ttk.Frame(self.emoji_canvas)
        self.emoji_canvas.create_window((0, 0), window=self.emoji_inner_frame, anchor="nw")
        
        # Controles de emoji
        emoji_buttons_frame = ttk.Frame(emoji_frame)
        emoji_buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(emoji_buttons_frame, text="Escala do Emoji:").pack(side=tk.LEFT, padx=5)
        ttk.Scale(emoji_buttons_frame, from_=0.5, to=2.0, variable=self.emoji_scale, 
                 orient=tk.HORIZONTAL, length=100).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(emoji_buttons_frame, text="➕ Adicionar Emoji ao Texto", 
                  command=self.add_emoji_to_text).pack(side=tk.LEFT, padx=5)
        
        # Bind para redimensionar o canvas
        self.emoji_inner_frame.bind("<Configure>", 
                                   lambda e: self.emoji_canvas.configure(scrollregion=self.emoji_canvas.bbox("all")))

    def setup_subtitles_list(self, parent):
        """Configura a lista de legendas com controles avançados"""
        subtitles_frame = ttk.LabelFrame(parent, text="📝 Legendas Adicionadas")
        subtitles_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Frame para lista e controles
        list_frame = ttk.Frame(subtitles_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Lista de legendas com scroll
        list_controls = ttk.Frame(list_frame)
        list_controls.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.subtitles_listbox = tk.Listbox(list_controls, height=6, selectmode=tk.SINGLE)
        self.subtitles_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        list_scrollbar = ttk.Scrollbar(list_controls, orient=tk.VERTICAL, command=self.subtitles_listbox.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.subtitles_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        # Bind para seleção
        self.subtitles_listbox.bind("<<ListboxSelect>>", self.on_subtitle_select)
        
        # Frame para botões de controle
        buttons_frame = ttk.Frame(list_frame)
        buttons_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        ttk.Button(buttons_frame, text="🗑️ Remover", 
                  command=self.remove_selected_subtitle).pack(fill=tk.X, pady=2)
        ttk.Button(buttons_frame, text="✏️ Editar", 
                  command=self.edit_selected_subtitle).pack(fill=tk.X, pady=2)
        ttk.Button(buttons_frame, text="⬆️ Mover Cima", 
                  command=self.move_subtitle_up).pack(fill=tk.X, pady=2)
        ttk.Button(buttons_frame, text="⬇️ Mover Baixo", 
                  command=self.move_subtitle_down).pack(fill=tk.X, pady=2)
        ttk.Button(buttons_frame, text="🎯 Selecionar no Preview", 
                  command=self.select_subtitle_in_preview).pack(fill=tk.X, pady=2)

    def setup_output_controls(self, parent):
        """Configura os controles de saída"""
        output_frame = ttk.LabelFrame(parent, text="💾 Salvar Vídeo Processado")
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Frame para caminho de saída
        path_frame = ttk.Frame(output_frame)
        path_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(path_frame, text="Caminho de saída:").pack(side=tk.LEFT)
        ttk.Entry(path_frame, textvariable=self.output_path, width=40).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(path_frame, text="📁 Escolher Pasta", 
                  command=self.choose_output_path).pack(side=tk.LEFT, padx=5)
        
        # Frame para controles de performance
        performance_frame = ttk.Frame(output_frame)
        performance_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Controle de threads da CPU
        ttk.Label(performance_frame, text="⚡ Threads da CPU:").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(performance_frame, from_=1, to=16, textvariable=self.cpu_threads, 
                   width=5).pack(side=tk.LEFT, padx=5)
        
        # Botão para detectar automaticamente
        ttk.Button(performance_frame, text="🔍 Detectar Máximo", 
                  command=self.detect_max_threads).pack(side=tk.LEFT, padx=5)
        
        # Frame para botões de renderização
        render_frame = ttk.Frame(output_frame)
        render_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Botão principal de renderização
        self.render_btn = ttk.Button(render_frame, text="🎬 Renderizar Esta Aba", 
                                    command=self.start_rendering, style="Accent.TButton")
        self.render_btn.pack(side=tk.LEFT, padx=5)
        
        # Barra de progresso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(render_frame, variable=self.progress_var, 
                                           maximum=100, length=200)
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
        
        # Label de status
        self.status_label = ttk.Label(render_frame, text="Pronto para renderizar")
        self.status_label.pack(side=tk.RIGHT, padx=5)

    def detect_max_threads(self):
        """Detecta automaticamente o número máximo de threads da CPU"""
        try:
            import os
            # Detecta número de cores físicos e lógicos
            physical_cores = os.cpu_count()  # Cores físicos
            logical_cores = os.cpu_count() * 2 if hasattr(os, 'cpu_count') else os.cpu_count()  # Com hyperthreading
            
            # Usa 75% dos cores lógicos para não sobrecarregar o sistema
            recommended_threads = max(1, int(logical_cores * 0.75))
            
            self.cpu_threads.set(recommended_threads)
            
            messagebox.showinfo("Threads Detectados", 
                              f"🔍 Cores físicos: {physical_cores}\n"
                              f"🧵 Cores lógicos: {logical_cores}\n"
                              f"⚡ Threads recomendados: {recommended_threads}\n\n"
                              f"Ajuste manualmente se necessário.")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao detectar threads: {e}")
            # Fallback para 4 threads
            self.cpu_threads.set(4)

    def select_video(self):
        """Seleciona um arquivo de vídeo"""
        file_path = filedialog.askopenfilename(
            title="Selecione um vídeo",
            filetypes=[("Vídeos", "*.mp4 *.avi *.mov *.mkv *.wmv"), ("Todos os arquivos", "*.*")]
        )
        if file_path:
            self.video_path.set(file_path)
            self.open_video(file_path)
            self.update_preview()

    def open_video(self, file_path):
        """Abre um arquivo de vídeo"""
        if hasattr(self, 'video_clip') and self.video_clip is not None:
            self.video_clip.close()
            self.video_clip = None
        try:
            self.video_clip = VideoFileClip(file_path)
            if self.video_clip is None:
                messagebox.showerror("Erro", "Não foi possível abrir o vídeo selecionado!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir vídeo: {e}")
            self.video_clip = None

    def on_text_change(self, event=None):
        """Sincroniza o conteúdo do text widget com a variável"""
        self.subtitle_text.set(self.text_widget.get("1.0", tk.END).strip())

    def add_subtitle(self):
        """Adiciona uma nova legenda"""
        text = self.text_widget.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Aviso", "Digite o texto da legenda.")
            return
            
        self.subtitle_counter += 1
        new_subtitle = {
            "id": self.subtitle_counter,
            "text": text,
            "font": self.font_family.get(),
            "size": self.font_size.get(),
            "color": self.font_color.get(),
            "border": self.border_color.get(),
            "bg": self.bg_color.get(),
            "x": 135,  # centro do canvas
            "y": 440   # parte inferior
        }
        
        self.subtitles.append(new_subtitle)
        self.update_subtitles_listbox()
        self.update_preview()
        self.text_widget.delete("1.0", tk.END)
        
        # Seleciona a nova legenda na lista
        self.subtitles_listbox.selection_clear(0, tk.END)
        self.subtitles_listbox.selection_set(len(self.subtitles) - 1)
        self.subtitles_listbox.see(len(self.subtitles) - 1)

    def update_subtitles_listbox(self):
        """Atualiza a lista de legendas"""
        self.subtitles_listbox.delete(0, tk.END)
        for idx, subtitle in enumerate(self.subtitles):
            # Formato mais profissional
            resumo = f'#{subtitle["id"]}: "{subtitle["text"]}" | {subtitle["font"]}, {subtitle["size"]}pt | Pos: ({subtitle["x"]}, {subtitle["y"]})'
            self.subtitles_listbox.insert(tk.END, resumo)

    def on_subtitle_select(self, event):
        """Callback quando uma legenda é selecionada na lista"""
        selection = self.subtitles_listbox.curselection()
        if selection:
            self.selected_subtitle_idx = selection[0]
            self.highlight_selected_subtitle()

    def highlight_selected_subtitle(self):
        """Destaca a legenda selecionada no preview"""
        if self.selected_subtitle_idx is not None and 0 <= self.selected_subtitle_idx < len(self.subtitles):
            self.update_preview()

    def remove_selected_subtitle(self):
        """Remove a legenda selecionada"""
        if self.selected_subtitle_idx is None:
            messagebox.showwarning("Aviso", "Selecione uma legenda para remover.")
            return
            
        idx = self.selected_subtitle_idx
        removed_subtitle = self.subtitles.pop(idx)
        self.update_subtitles_listbox()
        self.update_preview()
        self.selected_subtitle_idx = None
        
        messagebox.showinfo("Sucesso", f'Legenda "{removed_subtitle["text"]}" removida com sucesso!')

    def edit_selected_subtitle(self):
        """Edita a legenda selecionada"""
        if self.selected_subtitle_idx is None:
            messagebox.showwarning("Aviso", "Selecione uma legenda para editar.")
            return
            
        # Implementar janela de edição
        self.show_edit_subtitle_dialog()

    def show_edit_subtitle_dialog(self):
        """Mostra diálogo para editar legenda"""
        if self.selected_subtitle_idx is None:
            return
            
        subtitle = self.subtitles[self.selected_subtitle_idx]
        
        # Criar janela de edição simples
        edit_window = tk.Toplevel()
        edit_window.title(f"Editar Legenda #{subtitle['id']}")
        edit_window.geometry("500x400")
        edit_window.resizable(True, True)
        edit_window.minsize(400, 300)
        
        # Força a janela a aparecer
        edit_window.lift()
        edit_window.attributes('-topmost', True)
        edit_window.after_idle(lambda: edit_window.attributes('-topmost', False))
        
        # Variáveis
        text_var = tk.StringVar(value=subtitle["text"])
        font_var = tk.StringVar(value=subtitle["font"])
        size_var = tk.IntVar(value=subtitle["size"])
        color_var = tk.StringVar(value=subtitle["color"])
        
        # Frame principal com padding
        main_frame = tk.Frame(edit_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(main_frame, text=f"Editar Legenda #{subtitle['id']}", 
                font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        # Frame para campos
        fields_frame = tk.Frame(main_frame)
        fields_frame.pack(fill=tk.BOTH, expand=True)
        
        # Texto
        tk.Label(fields_frame, text="Texto da Legenda:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        text_entry = tk.Entry(fields_frame, textvariable=text_var, font=("Arial", 10))
        text_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Fonte
        tk.Label(fields_frame, text="Fonte:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        font_options = ["Arial", "Arial Black", "Helvetica", "Times", "Courier", "Verdana", "Impact", "Comic Sans MS"]
        font_combo = ttk.Combobox(fields_frame, textvariable=font_var, values=font_options, font=("Arial", 10))
        font_combo.pack(fill=tk.X, pady=(0, 15))
        
        # Frame para tamanho e cor lado a lado
        size_color_frame = tk.Frame(fields_frame)
        size_color_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Tamanho
        size_label_frame = tk.Frame(size_color_frame)
        size_label_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Label(size_label_frame, text="Tamanho:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        size_spinbox = tk.Spinbox(size_label_frame, from_=8, to=96, textvariable=size_var, width=10, font=("Arial", 10))
        size_spinbox.pack(anchor=tk.W)
        
        # Cor
        color_label_frame = tk.Frame(size_color_frame)
        color_label_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        tk.Label(color_label_frame, text="Cor:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        color_controls_frame = tk.Frame(color_label_frame)
        color_controls_frame.pack(anchor=tk.W)
        
        color_entry = tk.Entry(color_controls_frame, textvariable=color_var, width=15, font=("Arial", 10))
        color_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # Label para mostrar a cor atual
        color_preview = tk.Label(color_controls_frame, bg=color_var.get(), width=3, relief=tk.RAISED, bd=2)
        color_preview.pack(side=tk.LEFT, padx=(0, 5))
        
        def choose_color():
            from tkinter import colorchooser
            color = colorchooser.askcolor(title="Escolha a cor da fonte", initialcolor=color_var.get())
            if color and color[1]:
                color_var.set(color[1])
                color_preview.config(bg=color[1])
        
        tk.Button(color_controls_frame, text="🎨", command=choose_color, 
                 font=("Arial", 10), width=3).pack(side=tk.LEFT)
        
        # Botões
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def save_changes():
            # Valida e corrige a cor se estiver vazia
            color_value = color_var.get().strip()
            if not color_value:
                color_value = "#FFFFFF"  # Cor padrão branca
            
            subtitle["text"] = text_var.get()
            subtitle["font"] = font_var.get()
            subtitle["size"] = size_var.get()
            subtitle["color"] = color_value
            self.update_subtitles_listbox()
            self.update_preview()
            edit_window.destroy()
            
        tk.Button(button_frame, text="Salvar", command=save_changes, 
                 bg="green", fg="white", width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancelar", command=edit_window.destroy, 
                 bg="red", fg="white", width=10).pack(side=tk.LEFT, padx=5)
        
        # Foca no campo de texto
        text_entry.focus_set()
        text_entry.select_range(0, tk.END)

    def move_subtitle_up(self):
        """Move a legenda selecionada para cima na lista"""
        if self.selected_subtitle_idx is None or self.selected_subtitle_idx == 0:
            return
            
        idx = self.selected_subtitle_idx
        self.subtitles[idx], self.subtitles[idx-1] = self.subtitles[idx-1], self.subtitles[idx]
        self.selected_subtitle_idx = idx - 1
        self.update_subtitles_listbox()
        self.subtitles_listbox.selection_set(self.selected_subtitle_idx)

    def move_subtitle_down(self):
        """Move a legenda selecionada para baixo na lista"""
        if self.selected_subtitle_idx is None or self.selected_subtitle_idx >= len(self.subtitles) - 1:
            return
            
        idx = self.selected_subtitle_idx
        self.subtitles[idx], self.subtitles[idx+1] = self.subtitles[idx+1], self.subtitles[idx]
        self.selected_subtitle_idx = idx + 1
        self.update_subtitles_listbox()
        self.subtitles_listbox.selection_set(self.selected_subtitle_idx)

    def select_subtitle_in_preview(self):
        """Seleciona a legenda no preview"""
        if self.selected_subtitle_idx is not None:
            # Centraliza a legenda selecionada
            self.center_selected_subtitle()

    def center_selected_subtitle(self):
        """Centraliza a legenda selecionada no preview"""
        if self.selected_subtitle_idx is not None and 0 <= self.selected_subtitle_idx < len(self.subtitles):
            self.subtitles[self.selected_subtitle_idx]["x"] = 135
            self.subtitles[self.selected_subtitle_idx]["y"] = 240
            self.update_preview()

    def center_subtitle_in_border(self):
        """Centraliza a legenda selecionada na área da borda"""
        if self.selected_subtitle_idx is not None and 0 <= self.selected_subtitle_idx < len(self.subtitles):
            if self.video_border_enabled.get():
                border_size = self.video_border_size.get()
                # Centraliza na área da borda (parte superior)
                self.subtitles[self.selected_subtitle_idx]["x"] = 135
                self.subtitles[self.selected_subtitle_idx]["y"] = border_size // 2
                self.update_preview()
            else:
                messagebox.showinfo("Info", "Ative a borda primeiro para usar esta função!")

    def clear_all_subtitles(self):
        """Limpa todas as legendas"""
        if not self.subtitles:
            return
            
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja remover todas as legendas?"):
            self.subtitles.clear()
            self.selected_subtitle_idx = None
            self.update_subtitles_listbox()
            self.update_preview()

    def update_preview(self):
        """Atualiza o preview com as legendas"""
        if self.video_clip is None:
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(135, 240, text="Selecione um vídeo", 
                fill="white", font=("Arial", 16))
            return
            
        try:
            # Pega o primeiro frame do vídeo
            frame_array = self.video_clip.get_frame(0)
            
            # Redimensiona para 9:16 (270x480)
            frame_array = np.array(frame_array)
            image = Image.fromarray(frame_array)
            image = image.resize((270, 480), Image.Resampling.LANCZOS)
            
            # Aplica borda ao vídeo se habilitada (proporcional para preview)
            if self.video_border_enabled.get():
                # Calcula dimensões do vídeo interno proporcionalmente
                border_size = self.video_border_size.get()
                preview_border_size = max(1, border_size // 4)  # Proporção 1:4 para preview
                
                # Calcula dimensões do vídeo interno no preview (mantendo proporção 9:16)
                available_width = 270 - (preview_border_size * 2)
                available_height = 480 - (preview_border_size * 2)
                
                # Calcula proporção 9:16
                aspect_ratio = 9 / 16
                
                # Calcula dimensões baseadas na largura disponível
                video_width = available_width
                video_height = int(video_width / aspect_ratio)
                
                # Se a altura calculada for maior que a disponível, ajusta pela altura
                if video_height > available_height:
                    video_height = available_height
                    video_width = int(video_height * aspect_ratio)
                
                # Redimensiona o vídeo para as dimensões internas (proporcional)
                video_image = image.resize((video_width, video_height), Image.Resampling.LANCZOS)
                
                # Aplica a borda
                image = self.apply_video_border(video_image, 270, 480)
            else:
                # Sem borda, mantém o vídeo original
                pass
                
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível ler o frame do vídeo: {e}")
            return

        # Mantém o canvas do preview sempre no mesmo tamanho (270x480)
        canvas_width = 270
        canvas_height = 480
        
        # Atualiza o tamanho do canvas se necessário
        if (self.preview_canvas.winfo_width() != canvas_width or 
            self.preview_canvas.winfo_height() != canvas_height):
            self.preview_canvas.config(width=canvas_width, height=canvas_height)

        # Desenha as legendas no frame
        draw = ImageDraw.Draw(image)
        self._subtitle_bbox_cache = []
        
        for idx, subtitle in enumerate(self.subtitles):
            try:
                # Usa a fonte selecionada pelo usuário (adaptado para Linux)
                font_family = subtitle["font"]
                if font_family == "Arial Black":
                    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", subtitle["size"])
                elif font_family == "Arial":
                    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", subtitle["size"])
                elif font_family == "Helvetica":
                    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", subtitle["size"])
                elif font_family == "Times":
                    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf", subtitle["size"])
                elif font_family == "Courier":
                    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf", subtitle["size"])
                elif font_family == "Verdana":
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", subtitle["size"])
                elif font_family == "Impact":
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", subtitle["size"])
                elif font_family == "Comic Sans MS":
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", subtitle["size"])
                else:
                    # Fallback para fonte padrão do Linux
                    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", subtitle["size"])
            except:
                # Fallback para fonte padrão se não conseguir carregar a fonte específica
                font = ImageFont.load_default()
                
            text = subtitle["text"]
            x = subtitle["x"]
            y = subtitle["y"]
            color = subtitle["color"] if subtitle["color"] else "#FFFFFF"
            border = subtitle["border"] if subtitle["border"] else "#000000"
            bg = subtitle["bg"] if subtitle["bg"] else "#000000"

            # Ajusta posição das legendas se houver borda
            if self.video_border_enabled.get():
                border_size = self.video_border_size.get()
                x += border_size
                y += border_size

            # Calcula bounding box para detecção de clique
            bbox = draw.textbbox((0, 0), text, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            
            # Bounding box expandido para facilitar clique
            bbox = (x - w//2 - 10, y - h//2 - 8, x + w//2 + 10, y + h//2 + 8)
            self._subtitle_bbox_cache.append(bbox)

            # Desenha fundo se houver
            if bg and bg != "#000000":
                draw.rectangle([x - w//2 - 5, y - h//2 - 2, x + w//2 + 5, y + h//2 + 2], fill=bg)
                
            # Desenha borda se houver com espessura configurável (ajustada para preview)
            if border and border != "#000000":
                # Ajusta a espessura da borda para o preview (escala 1:4)
                preview_scale = 270 / 1080  # Fator de escala do preview
                border_thickness = max(1, int(self.subtitle_border_thickness.get() * preview_scale))
                for dx in range(-border_thickness, border_thickness + 1):
                    for dy in range(-border_thickness, border_thickness + 1):
                        if dx != 0 or dy != 0:
                            draw.text((x+dx, y+dy), text, font=font, fill=border, anchor="mm")
                            
            # Processa texto com emojis no preview
            self.draw_text_with_emojis_preview(draw, text, x, y, font, color, border, bg)
            
            # Destaca legenda selecionada
            if idx == self.selected_subtitle_idx:
                draw.rectangle(bbox, outline="yellow", width=2)

        self.preview_image = ImageTk.PhotoImage(image)
        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=self.preview_image)

        # Desenha retângulo de seleção se estiver arrastando
        if self.dragging_subtitle_idx is not None and 0 <= self.dragging_subtitle_idx < len(self._subtitle_bbox_cache):
            bbox = self._subtitle_bbox_cache[self.dragging_subtitle_idx]
            self.preview_canvas.create_rectangle(bbox, outline="red", width=3)
        
        # Atualiza informações da borda
        self.update_border_info()

    def update_border_info(self):
        """Atualiza as informações da borda no preview"""
        if self.video_border_enabled.get():
            border_size = self.video_border_size.get()
            border_color = self.video_border_color.get()
            border_style = self.video_border_style.get()
            
            # Dimensões finais (SEMPRE 1080x1920)
            final_width = 1080
            final_height = 1920
            
            # Calcula área do vídeo interno mantendo proporção 9:16
            scale_factor = 1080 / 270  # Fator de escala de 270 para 1080
            scaled_border_size = int(border_size * scale_factor)
            
            # Calcula dimensões internas mantendo proporção 9:16
            available_width = final_width - (scaled_border_size * 2)
            available_height = final_height - (scaled_border_size * 2)
            
            # Calcula proporção 9:16
            aspect_ratio = 9 / 16
            
            # Calcula dimensões baseadas na largura disponível
            video_width = available_width
            video_height = int(video_width / aspect_ratio)
            
            # Se a altura calculada for maior que a disponível, ajusta pela altura
            if video_height > available_height:
                video_height = available_height
                video_width = int(video_height * aspect_ratio)
            
            # Preview dimensions (sempre fixo)
            preview_width = 270
            preview_height = 480
            
            info_text = f"🖼️ Borda: {border_size}px | 🎨 {border_color} | 🎭 {border_style} | 📏 Preview: {preview_width}x{preview_height} | 🎬 Final: {final_width}x{final_height} | 🎥 Vídeo: {video_width}x{video_height} | 📝 Legenda: {self.subtitle_border_thickness.get()}px"
            self.border_info_label.config(text=info_text)
        else:
            self.border_info_label.config(text=f"📏 Preview: 270x480 | 🎬 Renderização: 1080x1920 | 📝 Legenda: {self.subtitle_border_thickness.get()}px")

    def on_preview_click(self, event):
        """Callback para clique no preview"""
        if not hasattr(self, "_subtitle_bbox_cache"):
            return
            
        x, y = event.x, event.y
        
        # Verifica se clicou em alguma legenda
        for idx, bbox in enumerate(self._subtitle_bbox_cache):
            x1, y1, x2, y2 = bbox
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.dragging_subtitle_idx = idx
                self.selected_subtitle_idx = idx
                
                # Atualiza seleção na lista
                self.subtitles_listbox.selection_clear(0, tk.END)
                self.subtitles_listbox.selection_set(idx)
                self.subtitles_listbox.see(idx)
                
                # Calcula offset do clique considerando a borda
                if self.video_border_enabled.get():
                    border_size = self.video_border_size.get()
                    sx = self.subtitles[idx]["x"] + border_size
                    sy = self.subtitles[idx]["y"] + border_size
                else:
                    sx = self.subtitles[idx]["x"]
                    sy = self.subtitles[idx]["y"]
                
                self.drag_offset_x = x - sx
                self.drag_offset_y = y - sy
                
                self.update_preview()
                return
                
        # Se não clicou em legenda, limpa seleção
        self.dragging_subtitle_idx = None
        self.selected_subtitle_idx = None
        self.subtitles_listbox.selection_clear(0, tk.END)
        self.update_preview()

    def on_preview_drag(self, event):
        """Callback para arrastar no preview"""
        if self.dragging_subtitle_idx is not None:
            idx = self.dragging_subtitle_idx
            new_x = event.x - self.drag_offset_x
            new_y = event.y - self.drag_offset_y
            
            # Ajusta posição considerando a borda
            if self.video_border_enabled.get():
                border_size = self.video_border_size.get()
                # Remove o offset da borda para salvar a posição original
                original_x = new_x - border_size
                original_y = new_y - border_size
                
                # Permite posicionar em qualquer lugar, incluindo na borda
                # Sem limitações para permitir posicionamento livre
                self.subtitles[idx]["x"] = original_x
                self.subtitles[idx]["y"] = original_y
            else:
                # Permite posicionar em qualquer lugar do canvas
                self.subtitles[idx]["x"] = new_x
                self.subtitles[idx]["y"] = new_y
            
            # Atualiza a lista
            self.update_subtitles_listbox()
            self.update_preview()

    def on_preview_release(self, event):
        """Callback para soltar o mouse no preview"""
        if self.dragging_subtitle_idx is not None:
            self.dragging_subtitle_idx = None
            self.update_preview()

    def on_preview_double_click(self, event):
        """Callback para duplo clique no preview"""
        if self.selected_subtitle_idx is not None:
            self.edit_selected_subtitle()

    def choose_output_path(self):
        """Escolhe o caminho de saída"""
        folder = filedialog.askdirectory(
            title="Escolha a pasta de saída",
            initialdir=self.output_path.get()
        )
        if folder:
            self.output_path.set(folder)

    def choose_font_color(self):
        """Escolhe a cor da fonte"""
        color = colorchooser.askcolor(title="Escolha a cor da fonte", initialcolor=self.font_color.get())
        if color and color[1]:
            self.font_color.set(color[1])
            self.font_color_label.config(bg=color[1])

    def choose_border_color(self):
        """Escolhe a cor da borda"""
        color = colorchooser.askcolor(title="Escolha a cor da borda (deixe Cancelar para sem borda)", 
                                    initialcolor=self.border_color.get())
        if color and color[1]:
            self.border_color.set(color[1])
            self.border_color_label.config(bg=color[1])
        elif color and color[1] is None:
            self.border_color.set("")
            self.border_color_label.config(bg=self.main_app.root.cget("bg"))

    def choose_bg_color(self):
        """Escolhe a cor do fundo"""
        color = colorchooser.askcolor(title="Escolha a cor do fundo (deixe Cancelar para sem fundo)", 
                                    initialcolor=self.bg_color.get())
        if color and color[1]:
            self.bg_color.set(color[1])
            self.bg_color_label.config(bg=color[1])
        elif color and color[1] is None:
            self.bg_color.set("")
            self.bg_color_label.config(bg=self.main_app.root.cget("bg"))

    def choose_video_border_color(self):
        """Escolhe a cor da borda do vídeo"""
        color = colorchooser.askcolor(title="Escolha a cor da borda do vídeo", 
                                    initialcolor=self.video_border_color.get())
        if color and color[1]:
            self.video_border_color.set(color[1])
            self.video_border_color_label.config(bg=color[1])

        
    def test_preview_render_consistency(self):
        """Testa a consistência entre preview e renderização"""
        if not self.video_path.get():
            messagebox.showinfo("Info", "Selecione um vídeo primeiro!")
            return
        
        if not self.subtitles:
            messagebox.showinfo("Info", "Adicione pelo menos uma legenda!")
            return
        
        try:
            # Cria uma imagem de teste com as mesmas dimensões da renderização
            test_width = 1080
            test_height = 1920
            scale_factor = 1080 / 270
            
            # Cria imagem de teste
            test_image = Image.new('RGB', (test_width, test_height), (0, 0, 0))
            
            # Aplica borda se habilitada
            if self.video_border_enabled.get():
                border_size = self.video_border_size.get()
                scaled_border_size = int(border_size * scale_factor)
                test_image = self.apply_video_border_render(test_image, test_width, test_height, scaled_border_size)
            
            draw = ImageDraw.Draw(test_image)
            
            # Desenha as legendas com as mesmas regras da renderização
            for subtitle in self.subtitles:
                try:
                    scaled_font_size = int(subtitle["size"] * scale_factor)
                    font_family = subtitle["font"]
                    if font_family == "Arial Black":
                        font = ImageFont.truetype("arialbd.ttf", scaled_font_size)
                    elif font_family == "Arial":
                        font = ImageFont.truetype("arial.ttf", scaled_font_size)
                    else:
                        font = ImageFont.truetype("arial.ttf", scaled_font_size)
                except:
                    font = ImageFont.load_default()
                
                # Calcula posições como na renderização
                x = subtitle["x"] * scale_factor
                y = subtitle["y"] * scale_factor
                
                # Ajusta posição se houver borda
                if self.video_border_enabled.get():
                    border_size = self.video_border_size.get()
                    scaled_border_size = int(border_size * scale_factor)
                    x += scaled_border_size
                    y += scaled_border_size
                
                # Desenha borda se houver com espessura configurável
                if subtitle["border"] and subtitle["border"] != "#000000":
                    border_thickness = int(self.subtitle_border_thickness.get() * scale_factor)
                    for dx in range(-border_thickness, border_thickness + 1):
                        for dy in range(-border_thickness, border_thickness + 1):
                            if dx != 0 or dy != 0:
                                draw.text((x+dx, y+dy), subtitle["text"], font=font, fill=subtitle["border"], anchor="mm")
                
                # Desenha texto de teste
                draw.text((x, y), subtitle["text"], font=font, fill=subtitle["color"], anchor="mm")
            
            # Redimensiona para mostrar no preview
            preview_width = 400
            preview_height = int(preview_width * (test_image.height / test_image.width))
            preview_image = test_image.resize((preview_width, preview_height), Image.Resampling.LANCZOS)
            
            # Mostra janela de comparação
            self.show_consistency_test(preview_image, test_width, test_height)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro no teste de consistência: {e}")

    def show_consistency_test(self, test_image, original_width, original_height):
        """Mostra janela de teste de consistência"""
        test_window = tk.Toplevel(self.main_app.root)
        test_window.title("🔍 Teste de Consistência - Preview vs Renderização")
        test_window.geometry("600x800")
        test_window.transient(self.main_app.root)
        
        # Frame principal
        main_frame = ttk.Frame(test_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        ttk.Label(main_frame, text="🔍 Teste de Consistência", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Informações
        info_text = f"📏 Dimensões originais: {original_width}x{original_height}\n"
        info_text += f"🖼️ Borda: {'Ativada' if self.video_border_enabled.get() else 'Desativada'}\n"
        if self.video_border_enabled.get():
            info_text += f"📐 Tamanho da borda: {self.video_border_size.get()}px\n"
            info_text += f"🎨 Cor: {self.video_border_color.get()}\n"
        info_text += f"📝 Legendas: {len(self.subtitles)}"
        
        ttk.Label(main_frame, text=info_text, font=("Arial", 10)).pack(pady=(0, 10))
        
        # Canvas para mostrar a imagem de teste
        canvas = tk.Canvas(main_frame, bg="white", relief=tk.SUNKEN, bd=2)
        canvas.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Converte para PhotoImage
        photo = ImageTk.PhotoImage(test_image)
        canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        canvas.image = photo
        
        # Instruções
        ttk.Label(main_frame, text="💡 Esta imagem mostra como as legendas aparecerão na renderização final.", 
                 font=("Arial", 9), foreground="blue").pack(pady=5)
        ttk.Label(main_frame, text="Compare com o preview principal para verificar se as posições estão corretas.", 
                 font=("Arial", 9), foreground="blue").pack(pady=5)
        
        # Botão fechar
        ttk.Button(main_frame, text="✅ Fechar", command=test_window.destroy).pack(pady=10)


    def apply_video_border(self, image, target_width, target_height):
        """Aplica borda ao vídeo (proporcional para preview)"""
        if not self.video_border_enabled.get():
            return image
        
        border_size = self.video_border_size.get()
        border_color = self.video_border_color.get()
        border_style = self.video_border_style.get()
        
        # Para preview: usa borda proporcional (1:4) para caber em 270x480
        # Para render: usa borda real (1:1) para 1080x1920
        if target_width == 270:  # Preview
            preview_border_size = max(1, border_size // 4)  # Proporção 1:4
        else:  # Render
            preview_border_size = border_size
        
        # Cria nova imagem com borda (sempre 270x480 para preview)
        if target_width == 270:  # Preview
            bordered_image = Image.new('RGB', (270, 480), border_color)
        else:  # Render
            bordered_image = Image.new('RGB', (target_width + (preview_border_size * 2), 
                                            target_height + (preview_border_size * 2)), border_color)
        
        # Cola a imagem original no centro
        if target_width == 270:  # Preview
            paste_x = preview_border_size
            paste_y = preview_border_size
        else:  # Render
            paste_x = preview_border_size
            paste_y = preview_border_size
            
        bordered_image.paste(image, (paste_x, paste_y))
        
        return bordered_image

    def apply_video_border_render(self, image, target_width, target_height, border_size):
        """Aplica borda ao vídeo durante a renderização"""
        border_color = self.video_border_color.get()
        border_style = self.video_border_style.get()
        
        # Calcula as novas dimensões com borda
        new_width = target_width + (border_size * 2)
        new_height = target_height + (border_size * 2)
        
        # Cria nova imagem com borda
        if border_style == "uniforme":
            bordered_image = Image.new('RGB', (new_width, new_height), border_color)
        elif border_style == "arredondada":
            bordered_image = Image.new('RGB', (new_width, new_height), border_color)
            # Aqui você pode adicionar lógica para bordas arredondadas
        elif border_style == "degradê":
            bordered_image = self.create_gradient_border_render(new_width, new_height, border_color)
        else:
            bordered_image = Image.new('RGB', (new_width, new_height), border_color)
        
        # Cola a imagem original no centro
        paste_x = border_size
        paste_y = border_size
        bordered_image.paste(image, (paste_x, paste_y))
        
        return bordered_image

    def create_bordered_frame(self, video_image, output_width, output_height, border_size):
        """Cria um frame com borda interna centralizando o vídeo"""
        border_color = self.video_border_color.get()
        border_style = self.video_border_style.get()
        
        # Cria imagem de fundo com a cor da borda
        if border_style == "uniforme":
            bordered_image = Image.new('RGB', (output_width, output_height), border_color)
        elif border_style == "arredondada":
            bordered_image = Image.new('RGB', (output_width, output_height), border_color)
        elif border_style == "degradê":
            bordered_image = self.create_gradient_border_render(output_width, output_height, border_color)
        else:
            bordered_image = Image.new('RGB', (output_width, output_height), border_color)
        
        # Calcula dimensões do vídeo interno (descontando a borda)
        available_width = output_width - (border_size * 2)
        available_height = output_height - (border_size * 2)
        
        # Calcula proporção 9:16
        aspect_ratio = 9 / 16
        
        # Calcula dimensões baseadas na largura disponível
        video_width = available_width
        video_height = int(video_width / aspect_ratio)
        
        # Se a altura calculada for maior que a disponível, ajusta pela altura
        if video_height > available_height:
            video_height = available_height
            video_width = int(video_height * aspect_ratio)
        
        # Redimensiona o vídeo para as dimensões internas
        resized_video = video_image.resize((video_width, video_height), Image.Resampling.LANCZOS)
        
        # Calcula posição para centralizar o vídeo
        paste_x = border_size + (available_width - video_width) // 2
        paste_y = border_size + (available_height - video_height) // 2
        
        # Cola o vídeo centralizado na moldura
        bordered_image.paste(resized_video, (paste_x, paste_y))
        
        return bordered_image

    def create_gradient_border_render(self, width, height, base_color):
        """Cria uma borda com degradê para renderização"""
        # Converte cor hex para RGB
        color = base_color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        
        # Cria degradê simples
        image = Image.new('RGB', (width, height))
        pixels = image.load()
        
        for x in range(width):
            for y in range(height):
                # Calcula intensidade baseada na distância das bordas
                dist_x = min(x, width - x - 1)
                dist_y = min(y, height - y - 1)
                min_dist = min(dist_x, dist_y)
                
                if min_dist < 50:  # Área de degradê
                    intensity = min_dist / 50.0
                    pixels[x, y] = (int(r * intensity), int(g * intensity), int(b * intensity))
                else:
                    pixels[x, y] = (r, g, b)
        
        return image

    def create_gradient_border(self, width, height, base_color):
        """Cria uma borda com degradê"""
        # Converte cor hex para RGB
        color = base_color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        
        # Cria degradê simples
        image = Image.new('RGB', (width, height))
        pixels = image.load()
        
        for x in range(width):
            for y in range(height):
                # Calcula intensidade baseada na distância das bordas
                dist_x = min(x, width - x - 1)
                dist_y = min(y, height - y - 1)
                min_dist = min(dist_x, dist_y)
                
                if min_dist < 50:  # Área de degradê
                    intensity = min_dist / 50.0
                    pixels[x, y] = (int(r * intensity), int(g * intensity), int(b * intensity))
                else:
                    pixels[x, y] = (r, g, b)
        
        return image





    def draw_subtitles_on_image(self, draw, image_width, image_height):
        """Desenha as legendas diretamente na imagem"""
        for subtitle in self.subtitles:
            try:
                # Escala o tamanho da fonte
                scale_factor = image_width / 270  # Fator de escala
                scaled_font_size = int(subtitle["size"] * scale_factor)
                
                # Usa a fonte selecionada pelo usuário (adaptado para Linux)
                font_family = subtitle["font"]
                if font_family == "Arial Black":
                    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", scaled_font_size)
                elif font_family == "Arial":
                    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", scaled_font_size)
                elif font_family == "Helvetica":
                    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", scaled_font_size)
                elif font_family == "Times":
                    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf", scaled_font_size)
                elif font_family == "Courier":
                    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf", scaled_font_size)
                elif font_family == "Verdana":
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", scaled_font_size)
                elif font_family == "Impact":
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", scaled_font_size)
                elif font_family == "Comic Sans MS":
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", scaled_font_size)
                else:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", scaled_font_size)
            except:
                font = ImageFont.load_default()
            
            # Escala as posições
            x = subtitle["x"] * scale_factor
            y = subtitle["y"] * scale_factor
            
            # Ajusta posição se houver borda
            if self.video_border_enabled.get():
                border_size = self.video_border_size.get()
                scaled_border_size = int(border_size * scale_factor)
                x += scaled_border_size
                y += scaled_border_size
            
            text = subtitle["text"]
            color = subtitle["color"]
            border = subtitle["border"]
            bg = subtitle["bg"]
            
            # Desenha fundo se houver
            if bg and bg != "#000000":
                bbox = draw.textbbox((0, 0), text, font=font)
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                draw.rectangle([x - w//2 - 5, y - h//2 - 2, x + w//2 + 5, y + h//2 + 2], fill=bg)
            
            # Desenha borda se houver com espessura configurável (escala para renderização)
            if border and border != "#000000":
                # Escala a espessura da borda para a renderização final (escala 1:1)
                scale_factor = 1080 / 270  # Fator de escala de 270 para 1080
                border_thickness = int(self.subtitle_border_thickness.get() * scale_factor)
                for dx in range(-border_thickness, border_thickness + 1):
                    for dy in range(-border_thickness, border_thickness + 1):
                        if dx != 0 or dy != 0:
                            draw.text((x+dx, y+dy), text, font=font, fill=border, anchor="mm")
            
            # Desenha texto principal
            draw.text((x, y), text, font=font, fill=color, anchor="mm")






    def select_emoji_folder(self):
        """Seleciona a pasta com imagens de emojis"""
        folder_path = filedialog.askdirectory(title="Selecione a pasta com imagens de emojis")
        if folder_path:
            self.emoji_folder.set(folder_path)
            self.load_emoji_images()

    def load_emoji_images(self):
        """Carrega as imagens de emojis da pasta selecionada"""
        folder_path = self.emoji_folder.get()
        if not folder_path or not os.path.exists(folder_path):
            return
        
        # Limpa o frame de emojis
        for widget in self.emoji_inner_frame.winfo_children():
            widget.destroy()
        
        self.emoji_images.clear()
        
        # Extensões de imagem suportadas
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        
        # Lista arquivos de imagem
        image_files = []
        for file in os.listdir(folder_path):
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_files.append(file)
        
        if not image_files:
            messagebox.showwarning("Aviso", "Nenhuma imagem encontrada na pasta selecionada!")
            return
        
        # Carrega e exibe as imagens
        for i, filename in enumerate(image_files):
            try:
                file_path = os.path.join(folder_path, filename)
                # Carrega a imagem
                image = Image.open(file_path)
                # Redimensiona para exibição (32x32 pixels)
                image = image.resize((32, 32), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                # Armazena a imagem original e a versão redimensionada
                self.emoji_images[filename] = {
                    'original_path': file_path,
                    'display_image': photo,
                    'original_image': Image.open(file_path)
                }
                
                # Cria botão para o emoji
                emoji_btn = tk.Button(self.emoji_inner_frame, image=photo, 
                                    command=lambda f=filename: self.select_emoji(f),
                                    relief=tk.FLAT, bd=1)
                emoji_btn.pack(side=tk.LEFT, padx=2, pady=2)
                
            except Exception as e:
                print(f"Erro ao carregar emoji {filename}: {e}")
        
        messagebox.showinfo("Sucesso", f"Carregados {len(self.emoji_images)} emojis!")

    def select_emoji(self, filename):
        """Seleciona um emoji"""
        self.selected_emoji = filename
        # Destaca o emoji selecionado
        for widget in self.emoji_inner_frame.winfo_children():
            if hasattr(widget, 'emoji_filename') and widget.emoji_filename == filename:
                widget.config(relief=tk.RAISED, bd=2)
            else:
                widget.config(relief=tk.FLAT, bd=1)

    def add_emoji_to_text(self):
        """Adiciona o emoji selecionado ao texto da legenda"""
        if not self.selected_emoji:
            messagebox.showwarning("Aviso", "Selecione um emoji primeiro!")
            return
        
        current_text = self.text_widget.get("1.0", tk.END).strip()
        # Adiciona o emoji ao texto (usando o nome do arquivo como placeholder)
        emoji_placeholder = f"[EMOJI:{self.selected_emoji}]"
        new_text = current_text + emoji_placeholder
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", new_text)

    def start_rendering(self):
        """Inicia a renderização do vídeo com legendas"""
        if not self.video_path.get():
            messagebox.showerror("Erro", "Selecione um vídeo primeiro!")
            return
            
        if not self.subtitles:
            messagebox.showerror("Erro", "Adicione pelo menos uma legenda!")
            return
            
        # Verifica se a pasta de saída existe
        output_dir = self.output_path.get()
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível criar a pasta de saída: {e}")
                return
        
        # Inicia a renderização em thread separada
        import threading
        self.render_thread = threading.Thread(target=self.render_video)
        self.render_thread.daemon = True
        self.render_thread.start()

    def render_video(self):
        """Renderiza o vídeo com as legendas usando MoviePy"""
        try:
            # Atualiza interface
            self.render_btn.config(state="disabled")
            self.status_label.config(text="Renderizando...")
            self.progress_var.set(0)
            
            # Carrega o vídeo
            video_clip = VideoFileClip(self.video_path.get())
            if video_clip is None:
                messagebox.showerror("Erro", "Não foi possível abrir o vídeo!")
                return
                
            # Define dimensões finais (SEMPRE 1080x1920 - nunca passa disso)
            output_width = 1080
            output_height = 1920
            
            # Calcula área do vídeo interno (descontando a borda)
            if self.video_border_enabled.get():
                border_size = self.video_border_size.get()
                scale_factor = 1080 / 270  # Fator de escala de 270 para 1080
                scaled_border_size = int(border_size * scale_factor)
                
                # Calcula dimensões internas mantendo proporção 9:16
                # Pega o menor lado para manter proporção
                available_width = output_width - (scaled_border_size * 2)
                available_height = output_height - (scaled_border_size * 2)
                
                # Calcula proporção 9:16
                aspect_ratio = 9 / 16
                
                # Calcula dimensões baseadas na largura disponível
                video_width = available_width
                video_height = int(video_width / aspect_ratio)
                
                # Se a altura calculada for maior que a disponível, ajusta pela altura
                if video_height > available_height:
                    video_height = available_height
                    video_width = int(video_height * aspect_ratio)
            else:
                video_width = output_width
                video_height = output_height
            
            # Redimensiona o vídeo para a área interna (mantém proporção 9:16)
            video_resized = video_clip.resize((video_width, video_height))
            
            # Cria o arquivo de saída com sufixo da aba
            base_name = os.path.splitext(os.path.basename(self.video_path.get()))[0]
            output_filename = os.path.join(
                self.output_path.get(),
                f"{base_name}_aba{self.tab_index + 1}.mp4"
            )
            
            # Cria função para renderizar frame com legendas e bordas
            def make_frame_with_subtitles(t):
                # Pega o frame do vídeo no tempo t
                frame = video_resized.get_frame(t)
                
                # Converte para PIL
                video_image = Image.fromarray(frame.astype(np.uint8))
                
                # Cria a imagem final com as dimensões de saída
                if self.video_border_enabled.get():
                    border_size = self.video_border_size.get()
                    scale_factor = output_width / 270  # Fator de escala dinâmico
                    scaled_border_size = int(border_size * scale_factor)
                    
                    # Cria imagem com borda
                    image = self.create_bordered_frame(video_image, output_width, output_height, scaled_border_size)
                else:
                    # Sem borda, redimensiona o vídeo para as dimensões finais
                    image = video_image.resize((output_width, output_height), Image.Resampling.LANCZOS)
                
                # Só cria o draw se houver legendas
                if self.subtitles:
                    draw = ImageDraw.Draw(image)
                    
                    # Adiciona as legendas
                    for subtitle in self.subtitles:
                        try:
                            # Escala o tamanho da fonte baseado na qualidade
                            scale_factor = output_width / 270  # Fator de escala dinâmico
                            scaled_font_size = int(subtitle["size"] * scale_factor)
                            
                            # Usa a fonte selecionada pelo usuário (adaptado para Linux)
                            font_family = subtitle["font"]
                            if font_family == "Arial Black":
                                font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", scaled_font_size)
                            elif font_family == "Arial":
                                font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", scaled_font_size)
                            elif font_family == "Helvetica":
                                font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", scaled_font_size)
                            elif font_family == "Times":
                                font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf", scaled_font_size)
                            elif font_family == "Courier":
                                font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf", scaled_font_size)
                            elif font_family == "Verdana":
                                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", scaled_font_size)
                            elif font_family == "Impact":
                                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", scaled_font_size)
                            elif font_family == "Comic Sans MS":
                                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", scaled_font_size)
                            else:
                                # Fallback para fonte padrão do Linux
                                font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", scaled_font_size)
                        except:
                            # Fallback para fonte padrão se não conseguir carregar a fonte específica
                            font = ImageFont.load_default()
                        
                        text = subtitle["text"]
                        # Escala as posições baseado na qualidade
                        scale_factor = output_width / 270  # Fator de escala dinâmico
                        x = subtitle["x"] * scale_factor
                        y = subtitle["y"] * scale_factor
                        color = subtitle["color"]
                        border = subtitle["border"]
                        bg = subtitle["bg"]
                        
                        # Ajusta posição das legendas se houver borda
                        if self.video_border_enabled.get():
                            border_size = self.video_border_size.get()
                            scaled_border_size = int(border_size * scale_factor)
                            x += scaled_border_size
                            y += scaled_border_size
                        
                        # Processa texto com emojis
                        self.draw_text_with_emojis(draw, text, x, y, font, color, border, bg, scale_factor)
                
                # Converte de volta para array numpy
                return np.array(image)
            
            # Função de callback para progresso
            def progress_callback(t, total_duration):
                progress = (t / total_duration) * 100
                self.progress_var.set(progress)
                self.status_label.config(text=f"Renderizando... {t:.1f}s/{total_duration:.1f}s")
                self.main_app.root.update_idletasks()
            
            # Cria o clip final com legendas usando make_frame
            from moviepy.video.VideoClip import VideoClip
            
            # Corrige FPS se for None (problema comum no Linux)
            fps_value = video_clip.fps
            if fps_value is None or fps_value <= 0:
                fps_value = 30.0  # FPS padrão
                print(f"⚠️ FPS não detectado, usando padrão: {fps_value}")
            
            final_clip = VideoClip(make_frame=make_frame_with_subtitles, duration=video_clip.duration)
            final_clip = final_clip.set_fps(fps_value)
            
            # Adiciona o áudio original
            if video_clip.audio is not None:
                final_clip = final_clip.set_audio(video_clip.audio)
            
            # Cria diretório temporário se não existir
            temp_dir = os.getenv("MOVIEPY_TEMP_DIR", tempfile.gettempdir())
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            # Corrige FPS se for None (problema comum no Linux)
            fps_value = video_clip.fps
            if fps_value is None or fps_value <= 0:
                fps_value = 30.0  # FPS padrão
                print(f"⚠️ FPS não detectado, usando padrão: {fps_value}")
            
            # Renderiza o vídeo final usando configurações otimizadas
            print(f"🎬 Iniciando renderização com FPS: {fps_value}")
            print(f"⚡ Usando {self.cpu_threads.get()} threads da CPU")
            
            # Força FPS no clip antes de renderizar (workaround para Linux)
            final_clip = final_clip.set_fps(fps_value)
            
            # Configura parâmetros de renderização otimizados
            render_params = {
                'codec': os.getenv("MOVIEPY_VIDEO_CODEC", 'libx264'),
                'audio_codec': os.getenv("MOVIEPY_AUDIO_CODEC", 'aac') if video_clip.audio is not None else None,
                'temp_audiofile': os.path.join(temp_dir, 'temp-audio.m4a') if video_clip.audio is not None else None,
                'remove_temp': True,
                'verbose': True,
                'logger': 'bar',
                'preset': 'medium',
                'threads': self.cpu_threads.get()  # Usa o número de threads configurado
            }
            
            # Renderiza o vídeo com configurações otimizadas
            final_clip.write_videofile(output_filename, **render_params)
            
            # Limpa recursos
            video_clip.close()
            video_resized.close()
            final_clip.close()
            
            # Atualiza interface
            self.progress_var.set(100)
            self.status_label.config(text="Renderização concluída!")
            self.render_btn.config(state="normal")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro durante a renderização: {e}")
            self.render_btn.config(state="normal")
            self.status_label.config(text="Erro na renderização")

    def draw_text_with_emojis(self, draw, text, x, y, font, color, border, bg, scale_factor):
        """Desenha texto com emojis integrados e quebra de linha com alinhamento à esquerda"""
        import re
        
        # Padrão para encontrar emojis no texto
        emoji_pattern = r'\[EMOJI:([^\]]+)\]'
        
        # Divide o texto em linhas
        lines = text.split('\n')
        line_height = font.size + 1  # Espaçamento entre linhas
        
        # Calcula altura total para centralizar verticalmente
        total_height = len(lines) * line_height
        start_y = y - total_height // 2
        
        # Calcula a largura máxima entre todas as linhas para centralizar o bloco
        max_line_width = 0
        line_widths = []
        
        for line in lines:
            parts = re.split(emoji_pattern, line)
            line_width = 0
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Texto normal
                    if part.strip():
                        bbox = draw.textbbox((0, 0), part, font=font)
                        line_width += bbox[2] - bbox[0]
                else:  # Emoji
                    emoji_filename = part
                    if emoji_filename in self.emoji_images:
                        emoji_size = int(font.size * self.emoji_scale.get())
                        line_width += emoji_size
            line_widths.append(line_width)
            max_line_width = max(max_line_width, line_width)
        
        # Calcula a posição inicial do bloco de texto (centralizado)
        block_start_x = x - max_line_width // 2
        
        # Desenha cada linha
        for line_idx, line in enumerate(lines):
            line_y = start_y + line_idx * line_height
            
            # Divide a linha em partes (texto e emojis)
            parts = re.split(emoji_pattern, line)
            
            # Posição inicial da linha (alinhada à esquerda dentro do bloco centralizado)
            current_x = block_start_x
            
            # Desenha fundo da linha se houver
            if bg and bg != "#000000":
                line_width = line_widths[line_idx]
                draw.rectangle([block_start_x - 5, line_y - font.size//2 - 2, 
                              block_start_x + line_width + 5, line_y + font.size//2 + 2], fill=bg)
            
            # Desenha cada parte da linha
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Texto normal
                    if part.strip():
                        # Desenha borda se houver com espessura configurável (escala para renderização)
                        if border and border != "#000000":
                            # Escala a espessura da borda para a renderização final
                            border_thickness = int(self.subtitle_border_thickness.get() * scale_factor)
                            for dx in range(-border_thickness, border_thickness + 1):
                                for dy in range(-border_thickness, border_thickness + 1):
                                    if dx != 0 or dy != 0:
                                        draw.text((current_x+dx, line_y+dy), part, font=font, fill=border, anchor="lm")
                        
                        # Desenha texto principal
                        draw.text((current_x, line_y), part, font=font, fill=color, anchor="lm")
                        
                        # Atualiza posição
                        bbox = draw.textbbox((0, 0), part, font=font)
                        current_x += bbox[2] - bbox[0]
                else:  # Emoji
                    emoji_filename = part
                    if emoji_filename in self.emoji_images:
                        emoji_size = int(font.size * self.emoji_scale.get())
                        
                        # Redimensiona a imagem do emoji
                        emoji_image = self.emoji_images[emoji_filename]['original_image'].copy()
                        emoji_image = emoji_image.resize((emoji_size, emoji_size), Image.Resampling.LANCZOS)
                        
                        # Converte para RGBA se necessário
                        if emoji_image.mode != 'RGBA':
                            emoji_image = emoji_image.convert('RGBA')
                        
                        # Cola o emoji na imagem principal
                        paste_x = int(current_x)
                        paste_y = int(line_y - emoji_size // 2)
                        
                        # Cria uma máscara para transparência
                        if emoji_image.mode == 'RGBA':
                            mask = emoji_image.split()[-1]
                            draw._image.paste(emoji_image, (paste_x, paste_y), mask)
                        else:
                            draw._image.paste(emoji_image, (paste_x, paste_y))
                        
                        # Atualiza posição
                        current_x += emoji_size

    def draw_text_with_emojis_preview(self, draw, text, x, y, font, color, border, bg):
        """Desenha texto com emojis integrados no preview com quebra de linha"""
        import re
        
        # Padrão para encontrar emojis no texto
        emoji_pattern = r'\[EMOJI:([^\]]+)\]'
        
        # Divide o texto em linhas
        lines = text.split('\n')
        line_height = font.size + 2  # Espaçamento entre linhas
        
        # Calcula altura total para centralizar verticalmente
        total_height = len(lines) * line_height
        start_y = y - total_height // 2
        
        # Calcula a largura máxima entre todas as linhas para centralizar o bloco
        max_line_width = 0
        line_widths = []
        
        for line in lines:
            parts = re.split(emoji_pattern, line)
            line_width = 0
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Texto normal
                    if part.strip():
                        bbox = draw.textbbox((0, 0), part, font=font)
                        line_width += bbox[2] - bbox[0]
                else:  # Emoji
                    emoji_filename = part
                    if emoji_filename in self.emoji_images:
                        emoji_size = int(font.size * self.emoji_scale.get())
                        line_width += emoji_size
            line_widths.append(line_width)
            max_line_width = max(max_line_width, line_width)
        
        # Calcula a posição inicial do bloco de texto (centralizado)
        block_start_x = x - max_line_width // 2
        
        # Desenha cada linha
        for line_idx, line in enumerate(lines):
            line_y = start_y + line_idx * line_height
            
            # Divide a linha em partes (texto e emojis)
            parts = re.split(emoji_pattern, line)
            
            # Posição inicial da linha (alinhada à esquerda dentro do bloco centralizado)
            current_x = block_start_x
            
            # Desenha fundo da linha se houver
            if bg and bg != "#000000":
                line_width = line_widths[line_idx]
                draw.rectangle([block_start_x - 5, line_y - font.size//2 - 2, 
                              block_start_x + line_width + 5, line_y + font.size//2 + 2], fill=bg)
            
            # Desenha cada parte da linha
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Texto normal
                    if part.strip():
                        # Desenha borda se houver com espessura configurável (ajustada para preview)
                        if border and border != "#000000":
                            # Ajusta a espessura da borda para o preview (escala 1:4)
                            preview_scale = 270 / 1080  # Fator de escala do preview
                            border_thickness = max(1, int(self.subtitle_border_thickness.get() * preview_scale))
                            for dx in range(-border_thickness, border_thickness + 1):
                                for dy in range(-border_thickness, border_thickness + 1):
                                    if dx != 0 or dy != 0:
                                        draw.text((current_x+dx, line_y+dy), part, font=font, fill=border, anchor="lm")
                        
                        # Desenha texto principal
                        draw.text((current_x, line_y), part, font=font, fill=color, anchor="lm")
                        
                        # Atualiza posição
                        bbox = draw.textbbox((0, 0), part, font=font)
                        current_x += bbox[2] - bbox[0]
                else:  # Emoji
                    emoji_filename = part
                    if emoji_filename in self.emoji_images:
                        emoji_size = int(font.size * self.emoji_scale.get())
                        
                        # Redimensiona a imagem do emoji
                        emoji_image = self.emoji_images[emoji_filename]['original_image'].copy()
                        emoji_image = emoji_image.resize((emoji_size, emoji_size), Image.Resampling.LANCZOS)
                        
                        # Converte para RGBA se necessário
                        if emoji_image.mode != 'RGBA':
                            emoji_image = emoji_image.convert('RGBA')
                        
                        # Cola o emoji na imagem principal
                        paste_x = int(current_x)
                        paste_y = int(line_y - emoji_size // 2)
                        
                        # Cria uma máscara para transparência
                        if emoji_image.mode == 'RGBA':
                            mask = emoji_image.split()[-1]
                            draw._image.paste(emoji_image, (paste_x, paste_y), mask)
                        else:
                            draw._image.paste(emoji_image, (paste_x, paste_y))
                        
                        # Atualiza posição
                        current_x += emoji_size

if __name__ == "__main__":
    root = tk.Tk()
    app = ProfessionalVideoEditorUI(root)
    root.geometry("500x900")
    root.mainloop()