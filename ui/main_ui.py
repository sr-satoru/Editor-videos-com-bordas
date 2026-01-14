# ui/main_ui.py
import tkinter as tk
from tkinter import ttk
from ui.preview import Preview
from ui.video_controls import VideoControls
from ui.borders import VideoBorders
from ui.subtitles import Subtitles
from ui.audio import AudioSettings
from ui.output import OutputVideo
from ui.footer import Footer
from ui.marca_da_agua import WatermarkUI
import json
from tkinter import filedialog, messagebox

from modules.subiitels.gerenciador_legendas import GerenciadorLegendas
from modules.subiitels.gerenciador_emojis import GerenciadorEmojis

class EditorUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Editor Profissional de Vídeo 9:16")
        self.geometry("900x800")
        self.processar_pasta_var = tk.BooleanVar()
        self.tabs_data = []

        self.build_ui()

    def build_ui(self):
        # ---------- NOTEBOOK ----------
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # ---------- CRIAR ABA INICIAL ----------
        self.add_new_tab("Aba 1")

        # ---------- FOOTER ----------
        Footer(self, 
               add_tab_callback=self.add_new_tab_with_auto_name,
               remove_tab_callback=self.remove_current_tab,
               render_all_callback=self.render_all_tabs,
               save_callback=self.save_project,
               load_callback=self.load_project,
               change_all_output_callback=self.change_all_output_path,
               change_all_audio_callback=self.change_all_audio_folder,
               load_video_all_callback=self.load_video_all_tabs)

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
        """Carrega o mesmo vídeo em todas as abas"""
        filepath = filedialog.askopenfilename(
            filetypes=[("Vídeos", "*.mp4 *.mov *.avi *.mkv")],
            title="Selecionar Vídeo para Todas as Abas"
        )
        if filepath:
            for tab in self.tabs_data:
                tab['video_controls'].video_selector.load_video(filepath)
                # Forçar atualização do preview se necessário
                tab['subtitles'].update_preview()
            messagebox.showinfo("Sucesso", f"Vídeo carregado em {len(self.tabs_data)} abas.")

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

    def render_all_tabs(self):
        """Chama o render de todas as abas abertas"""
        for idx, tab in enumerate(self.tabs_data, start=1):
            tab['output'].start_rendering(tab_number=idx)

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

        project_state = []
        for tab in self.tabs_data:
            tab_state = {
                "name": self.notebook.tab(tab['frame'], "text"),
                "video_controls": tab['video_controls'].get_state(),
                "borders": tab['borders'].get_state(),
                "subtitles": tab['subtitles'].get_state(),
                "watermark": tab['watermark'].get_state(),
                "audio": tab['audio'].get_state(),
                "output": tab['output'].get_state()
            }
            project_state.append(tab_state)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project_state, f, indent=4, ensure_ascii=False)
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

        # Recriar abas
        tabs_to_load = project_state.get("tabs", []) if isinstance(project_state, dict) else project_state
        
        for tab_state in tabs_to_load:
            if not isinstance(tab_state, dict): continue
            
            self.add_new_tab(tab_state.get("name", "Aba"))
            current_tab = self.tabs_data[-1]
            
            # Aplicar estados
            current_tab['video_controls'].set_state(tab_state.get("video_controls", {}))
            current_tab['borders'].set_state(tab_state.get("borders", {}))
            current_tab['subtitles'].set_state(tab_state.get("subtitles", {}))
            current_tab['watermark'].set_state(tab_state.get("watermark", {}))
            current_tab['audio'].set_state(tab_state.get("audio", {}))
            current_tab['output'].set_state(tab_state.get("output", {}))

        messagebox.showinfo("Sucesso", "Projeto importado com sucesso!")

    def add_new_tab(self, tab_name):
        """Adiciona uma nova aba e popula com os módulos"""
        new_tab = ttk.Frame(self.notebook)
        self.notebook.add(new_tab, text=tab_name)

        # ================== SCROLL DA ABA ==================
        canvas = tk.Canvas(new_tab, highlightthickness=0)
        scrollbar = ttk.Scrollbar(new_tab, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
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
        preview = Preview(scroll_frame)  # Apenas o canvas do preview
        video_controls = VideoControls(scroll_frame, self.processar_pasta_var, preview.canvas)  # Botão seleciona vídeo
        video_borders = VideoBorders(scroll_frame, video_controls, subtitle_manager, emoji_manager)
        
        subtitles_ui = Subtitles(scroll_frame, subtitle_manager, emoji_manager, video_controls, video_borders)
        
        watermark_ui = WatermarkUI(scroll_frame, video_controls, subtitle_manager, emoji_manager, video_borders)
        watermark_ui.subtitles_ui = subtitles_ui  # Referência para disparar preview
        subtitles_ui.watermark_ui = watermark_ui  # Referência para ler dados da marca d'água
        
        audio_settings = AudioSettings(scroll_frame)
        output_video = OutputVideo(scroll_frame, video_controls, video_borders, subtitle_manager, emoji_manager, audio_settings, watermark_ui, processar_pasta_var=self.processar_pasta_var)
        
        self.tabs_data.append({
            'frame': new_tab,
            'video_controls': video_controls,
            'borders': video_borders,
            'subtitles': subtitles_ui,
            'watermark': watermark_ui,
            'audio': audio_settings,
            'output': output_video
        })


if __name__ == "__main__":
    EditorUI().mainloop()
