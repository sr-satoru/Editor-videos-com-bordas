# ui/main_ui.py
import tkinter as tk
from tkinter import ttk
from ui.preview import Preview
from ui.video_controls import VideoControls
from ui.borders import VideoBorders
from ui.subtitles import Subtitles
from ui.audio import AudioSettings
from ui.output import OutputVideo
from modules.config_global import global_config
from ui.footer import Footer
from ui.marca_da_agua import WatermarkUI
from ui.mesclagem_front import MesclagemFront
from ui.theme import ThemeManager, LIGHT_THEME, DARK_THEME
import json
from tkinter import filedialog, messagebox

from modules.subiitels.gerenciador_legendas import GerenciadorLegendas
from modules.subiitels.gerenciador_emojis import GerenciadorEmojis
from modules.media_pool_manager import MediaPoolManager

class EditorUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Editor Profissional de Vídeo 9:16")
        self.geometry("900x880")
        self.processar_pasta_var = tk.BooleanVar()
        self.tabs_data = []

        self.theme_manager = ThemeManager(self)
        self.global_tab_pool = MediaPoolManager() # Pool global para processamento de abas
        self.create_header()
        self.build_ui()

    def create_header(self):
        colors = LIGHT_THEME if self.theme_manager.current_theme == "light" else DARK_THEME
        header_bg = colors["surface"]
        
        self.header_frame = tk.Frame(self, bg=header_bg, highlightthickness=1, highlightbackground=colors["border"])
        self.header_frame.pack(fill="x", side="top")
        
        # Título / Logo (Mais elegante)
        self.header_title_label = tk.Label(
            self.header_frame, 
            text="🎬 Editor 9:16", 
            font=("Segoe UI", 12, "bold"),
            bg=header_bg,
            fg=colors["select_bg"]
        )
        self.header_title_label.pack(side="left", padx=15, pady=8)
        
        # Botão Toggle Theme (Menor e mais limpo)
        self.theme_btn = tk.Button(
            self.header_frame, 
            text="☀️", 
            font=("Segoe UI Emoji", 11), 
            bd=0,
            bg=header_bg,
            activebackground=header_bg,
            cursor="hand2",
            command=self.toggle_theme_action
        )
        self.theme_btn.pack(side="right", padx=15, pady=8)

        # Botão de Configurações
        self.settings_btn = tk.Button(
            self.header_frame, 
            text="⚙️", 
            font=("Segoe UI Emoji", 11), 
            bd=0,
            bg=header_bg,
            activebackground=header_bg,
            cursor="hand2",
            command=self.open_settings
        )
        self.settings_btn.pack(side="right", padx=0, pady=8)
        self.theme_btn.ignore_theme = True
        
        # Atualiza o botão com o estado inicial
        self.update_theme_button()

    def toggle_theme_action(self):
        self.theme_manager.toggle_theme()
        self.update_theme_button()

    def update_theme_button(self):
        is_light = self.theme_manager.current_theme == "light"
        colors = LIGHT_THEME if is_light else DARK_THEME
        text = "🌙" if is_light else "☀️" 
        
        header_bg = colors["surface"]
        fg_color = colors["fg"]
        
        self.theme_btn.config(text=text, bg=header_bg, fg=fg_color, activebackground=header_bg, activeforeground=fg_color)
        self.settings_btn.config(bg=header_bg, fg=fg_color, activebackground=header_bg, activeforeground=fg_color)
        self.header_frame.config(bg=header_bg, highlightbackground=colors["border"])
        self.header_title_label.config(bg=header_bg, fg=colors["select_bg"])

    def open_settings(self):
        from ui.dialogo_configuracoes import DialogoConfiguracoes
        DialogoConfiguracoes(self)

    def build_ui(self):
        # ---------- FOOTER (Primeiro para garantir espaço embaixo) ----------
        from modules.render_orchestrator import render_orchestrator
        Footer(self, 
               add_tab_callback=self.add_new_tab_with_auto_name,
               remove_tab_callback=self.remove_current_tab,
               render_all_callback=lambda: render_orchestrator.start_render_flow(self),
               save_callback=self.save_project,
               load_callback=self.load_project,
               change_all_output_callback=self.change_all_output_path,
               change_all_audio_callback=self.change_all_audio_folder,
               load_video_all_callback=self.load_video_all_tabs)

        # ---------- NOTEBOOK (Expandido para preencher o que sobra) ----------
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # ---------- CRIAR ABA INICIAL ----------
        self.add_new_tab("Aba 1")

    def change_all_output_path(self):
        """Altera a pasta de saída de todas as abas"""
        folder = filedialog.askdirectory(title="Selecionar Pasta de Saída para Todas as Abas")
        if folder:
            for tab in self.tabs_data:
                tab['output'].output_path.set(folder)
            messagebox.showinfo("Sucesso", f"Pasta de saída alterada em {len(self.tabs_data)} abas.")

    def change_all_audio_folder(self):
        """Altera a pasta de áudio de todas as abas"""
        folder = filedialog.askdirectory(title="Selecionar Pasta de Áudio para Todas as Abas")
        if folder:
            for tab in self.tabs_data:
                tab['audio'].audio_folder_path.set(folder)
            messagebox.showinfo("Sucesso", f"Pasta de áudio alterada em {len(self.tabs_data)} abas.")

    def load_video_all_tabs(self):
        """Carrega o mesmo vídeo ou imagem em todas as abas"""
        filepath = filedialog.askopenfilename(
            filetypes=[
                ("Vídeos e Imagens", "*.mp4 *.mov *.avi *.mkv *.jpg *.jpeg *.png"),
                ("Vídeos", "*.mp4 *.mov *.avi *.mkv"),
                ("Imagens", "*.jpg *.jpeg *.png")
            ],
            title="Selecionar Vídeo/Imagem para Todas as Abas"
        )
        if filepath:
            self.load_video_all_tabs_from_path(filepath)
            messagebox.showinfo("Sucesso", f"Vídeo carregado em {len(self.tabs_data)} abas.")
    
    def load_video_all_tabs_from_path(self, filepath: str):
        """Carrega vídeo em todas as abas sem diálogo (usado pelo BatchQueueManager)"""
        for tab in self.tabs_data:
            tab['video_controls'].video_selector.load_video(filepath)
            # Forçar atualização do preview se necessário
            tab['subtitles'].update_preview()
    
    def change_all_output_path_direct(self, folder: str):
        """Altera pasta de saída sem diálogo (usado pelo BatchQueueManager)"""
        for tab in self.tabs_data:
            tab['output'].output_path.set(folder)
    
    def change_all_audio_folder_direct(self, folder: str):
        """Altera pasta de áudio sem diálogo (usado pelo BatchQueueManager)"""
        for tab in self.tabs_data:
            tab['audio'].audio_folder_path.set(folder)

    def remove_current_tab(self):
        """Remove a aba atualmente selecionada"""
        if len(self.tabs_data) <= 1:
            messagebox.showwarning("Aviso", "Não é possível remover a última aba.")
            return

        current_idx = self.notebook.index("current")
        tab_to_remove = self.tabs_data[current_idx]
        
        if messagebox.askyesno("Confirmar", f"Deseja remover a aba '{self.notebook.tab(current_idx, 'text')}'?"):
            self.notebook.forget(current_idx)
            self.tabs_data.pop(current_idx)
            self.update_tab_names()

    def update_tab_names(self):
        """Renomeia todas as abas sequencialmente"""
        for i in range(self.notebook.index("end")):
            self.notebook.tab(i, text=f"Aba {i + 1}")

    def add_new_tab_with_auto_name(self):
        """Helper para adicionar nova aba com o próximo nome disponível"""
        next_idx = self.notebook.index("end") + 1
        self.add_new_tab(f"Aba {next_idx}")

    def render_all_tabs_core(self):
        """Execução técnica da renderização de todas as abas (sem prompts)"""
        # Resetar contador de abas concluídas
        self.tabs_rendered_count = 0
        self.total_tabs_to_render = len(self.tabs_data)
        
        # --- LÓGICA DE POOL DE MÍDIAS (DISTRIBUIÇÃO SEQUENCIAL) ---
        # AQUI usamos o POOL GLOBAL das abas, mas APENAS se não estivermos rodando um Lote (Batch)
        from modules.batch_queue_manager import batch_queue_manager
        
        if not batch_queue_manager.is_active and self.global_tab_pool.enabled:
            print(f"[MainUI] Pool Global de Abas ativo. Distribuindo entre {self.total_tabs_to_render} abas...")
            try:
                for i, tab in enumerate(self.tabs_data):
                    video_path = self.global_tab_pool.get_video_for_index(i)
                    if video_path:
                        # Carrega o vídeo na aba de forma silenciosa e atualiza o preview
                        tab['video_controls'].video_selector.load_video(video_path)
                        tab['subtitles'].update_preview()
            except Exception as e:
                print(f"[MainUI] Erro ao aplicar pool global: {e}")
        # ---------------------------------------------------------

        for idx, tab in enumerate(self.tabs_data, start=1):
            tab['output'].start_rendering(tab_number=idx)
    
    def on_tab_render_complete(self):
        """Callback chamado quando uma aba termina de renderizar (Thread-Safe)"""
        def _safe_finish_logic():
            # Apenas um incremento atômico na thread principal evita condições de corrida
            self.tabs_rendered_count += 1
            print(f"[MainUI] Aba {self.tabs_rendered_count}/{self.total_tabs_to_render} concluída")
            
            # Verificar se todas as abas terminaram (usamos == para garantir disparo único)
            if hasattr(self, 'total_tabs_to_render') and self.tabs_rendered_count == self.total_tabs_to_render:
                print("[MainUI] Todas as abas foram renderizadas!")
                # Resetar total para evitar re-execução se ABA for reportada duas vezes por erro técnico
                self.total_tabs_to_render = -1 
                
                from modules.render_orchestrator import render_orchestrator
                render_orchestrator.on_all_tabs_finished(self)
        
        # Agendar para rodar na thread principal
        self.after(0, _safe_finish_logic)

    def save_project(self):
        """Salva o estado de todas as abas em um JSON"""
        if not self.tabs_data:
            messagebox.showwarning("Aviso", "Não há abas para salvar.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Salvar Projeto"
        )
        if not file_path:
            return

        project_data = {
            "global_tab_pool": self.global_tab_pool.to_dict(),
            "tabs": []
        }
        
        for tab in self.tabs_data:
            tab_state = {
                "name": self.notebook.tab(tab['frame'], "text"),
                "video_controls": tab['video_controls'].get_state(),
                "borders": tab['borders'].get_state(),
                "subtitles": tab['subtitles'].get_state(),
                "watermark": tab['watermark'].get_state(),
                "audio": tab['audio'].get_state(),
                "output": tab['output'].get_state(),
                "mesclagem": tab['mesclagem'].get_state()  # Novo: vídeos de mesclagem/CTA
            }
            project_state.append(tab_state)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Sucesso", "Projeto salvo com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar projeto: {e}")

    def load_project(self):
        """Carrega o estado de um JSON e recria as abas"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            title="Importar Projeto"
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                project_state = json.load(f)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar arquivo: {e}")
            return

        # Limpar abas atuais
        for tab in self.tabs_data:
            self.notebook.forget(tab['frame'])
        self.tabs_data = []

        # Carregar pool global se existir
        if isinstance(project_state, dict) and "global_tab_pool" in project_state:
            self.global_tab_pool = MediaPoolManager.from_dict(project_state["global_tab_pool"])

        # Recriar abas
        tabs_to_load = project_state.get("tabs", []) if isinstance(project_state, dict) else project_state
        
        errors = []  # Lista para coletar erros de vídeos não encontrados
        
        for idx, tab_state in enumerate(tabs_to_load, start=1):
            if not isinstance(tab_state, dict): 
                continue
            
            tab_name = tab_state.get("name", f"Aba {idx}")
            self.add_new_tab(tab_name)
            current_tab = self.tabs_data[-1]
            
            # Aplicar estados com fallback para compatibilidade com JSONs antigos
            # Video Controls - captura erro se vídeo não for encontrado
            video_result = current_tab['video_controls'].set_state(tab_state.get("video_controls", {}))
            if video_result and not video_result.get("success", True):
                errors.append({
                    "tab": idx,
                    "tab_name": tab_name,
                    "error": video_result.get("error"),
                    "path": video_result.get("video_path")
                })
            
            # Outros componentes (com fallback para JSONs antigos)
            current_tab['borders'].set_state(tab_state.get("borders", {}))
            current_tab['subtitles'].set_state(tab_state.get("subtitles", {}))
            current_tab['watermark'].set_state(tab_state.get("watermark", {}))
            current_tab['audio'].set_state(tab_state.get("audio", {}))
            current_tab['output'].set_state(tab_state.get("output", {}))
            current_tab['mesclagem'].set_state(tab_state.get("mesclagem", {}))  # Novo campo com fallback

        # Mostrar avisos ou sucesso
        if errors:
            self.show_import_warnings(errors)
        else:
            messagebox.showinfo("Sucesso", "Projeto importado com sucesso!")

    def show_import_warnings(self, errors):
        """Mostra avisos de vídeos não encontrados durante importação"""
        if not errors:
            return
        
        message = "⚠️ Projeto importado com avisos:\n\n"
        
        for error in errors:
            message += f"• {error['tab_name']}: {error['error']}\n"
            message += f"  Caminho: {error['path']}\n\n"
        
        message += "As abas foram criadas, mas você precisa recarregar os vídeos manualmente."
        
        messagebox.showwarning("Avisos de Importação", message)

    def add_new_tab(self, tab_name):
        """Adiciona uma nova aba e popula com os módulos"""
        new_tab = ttk.Frame(self.notebook)
        self.notebook.add(new_tab, text=tab_name)

        # ================== CONTAINER PRINCIPAL (DUAS COLUNAS) ==================
        main_container = ttk.Frame(new_tab)
        main_container.pack(fill="both", expand=True)

        # Coluna da Esquerda (Preview Fixo)
        left_column = ttk.Frame(main_container, padding=(10, 0))
        left_column.pack(side="left", fill="y", padx=5, pady=10)

        # Coluna da Direita (Configurações Roláveis)
        right_column = ttk.Frame(main_container, padding=(0, 0))
        right_column.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

        # ================== SCROLL DA COLUNA DIREITA ==================
        canvas = tk.Canvas(right_column, highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_column, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        
        # Ajustar largura do scroll_frame para acompanhar o canvas
        def _on_canvas_configure(event):
            canvas.itemconfig(canvas.find_withtag("all")[0], width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ===== SCROLL COM MOUSE =====
        def _on_mousewheel(event):
            if event.num == 4:           # Linux scroll up
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:         # Linux scroll down
                canvas.yview_scroll(1, "units")
            else:                        # Windows / macOS
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

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

        # ================== MANAGERS ==================
        subtitle_manager = GerenciadorLegendas()
        emoji_manager = GerenciadorEmojis()

        # ================== MÓDULOS ==================
        preview = Preview(left_column)  # Preview na ESQUERDA
        video_controls = VideoControls(left_column, self.processar_pasta_var, preview.canvas) # Controles na ESQUERDA abaixo do preview
        
        video_borders = VideoBorders(scroll_frame, video_controls, subtitle_manager, emoji_manager)
        
        subtitles_ui = Subtitles(scroll_frame, subtitle_manager, emoji_manager, video_controls, video_borders)
        
        watermark_ui = WatermarkUI(scroll_frame, video_controls, subtitle_manager, emoji_manager, video_borders)
        watermark_ui.subtitles_ui = subtitles_ui  # Referência para disparar preview
        subtitles_ui.watermark_ui = watermark_ui  # Referência para ler dados da marca d'água
        
        audio_settings = AudioSettings(scroll_frame)
        
        mesclagem_ui = MesclagemFront(scroll_frame, video_controls) # Novo Módulo de Finalizadores
        
        output_video = OutputVideo(scroll_frame, video_controls, video_borders, subtitle_manager, emoji_manager, audio_settings, watermark_ui, mesclagem_ui, processar_pasta_var=self.processar_pasta_var, editor_ui_ref=self)
        
        self.tabs_data.append({
            'frame': new_tab,
            'video_controls': video_controls,
            'borders': video_borders,
            'subtitles': subtitles_ui,
            'watermark': watermark_ui,
            'mesclagem': mesclagem_ui,
            'audio': audio_settings,
            'output': output_video
        })
        
        # Aplicar tema à nova aba
        if hasattr(self, 'theme_manager'):
            self.theme_manager.apply_to_widget(new_tab)


if __name__ == "__main__":
    EditorUI().mainloop()
