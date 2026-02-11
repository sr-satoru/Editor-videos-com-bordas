import os
import tkinter as tk
from tkinter import ttk, filedialog

from tkinter import messagebox
from modules.video_editor import VideoEditor
from modules.process_pasta_var import FolderProcessor
import threading
from modules.notifier import Notifier

class OutputVideo(ttk.LabelFrame):
    def __init__(self, parent, video_controls, video_borders, subtitle_manager, emoji_manager, audio_settings_ui, watermark_ui, mesclagem_ui, processar_pasta_var=None):
        super().__init__(parent, text="Salvar Vídeo Processado", padding=10) # Adicionado padding interno
        self.pack(fill="x", pady=10, padx=10)
        
        self.video_controls = video_controls
        self.video_borders = video_borders
        self.subtitle_manager = subtitle_manager
        self.emoji_manager = emoji_manager
        self.audio_settings_ui = audio_settings_ui
        self.watermark_ui = watermark_ui
        self.mesclagem_ui = mesclagem_ui
        self.processar_pasta_var = processar_pasta_var
        self.editor = VideoEditor()
        self.folder_processor = FolderProcessor(self.editor)

        self.output_path = tk.StringVar()

        path_frame = ttk.Frame(self)
        path_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(path_frame, text="Caminho de saída:").pack(side="left")

        ttk.Entry(path_frame, textvariable=self.output_path).pack(
            side="left", fill="x", expand=True, padx=5
        )

        ttk.Button(path_frame, text="Escolher Pasta", command=self.select_output_folder).pack(side="left", padx=5)
        
        # Botão de Renderizar
        self.render_btn = ttk.Button(self, text="Renderizar Vídeo", command=self.start_rendering, style="Accent.TButton")
        self.render_btn.pack(pady=10)
        
        self.status_label = ttk.Label(self, text="")
        self.status_label.pack(pady=5)

    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_path.set(folder)

    def start_rendering(self, tab_number=None):
        input_path = self.video_controls.video_selector.current_video_path
        output_folder = self.output_path.get()
        
        if not input_path:
            messagebox.showwarning("Aviso", "Selecione um vídeo primeiro.")
            return
            
        if not output_folder:
            messagebox.showwarning("Aviso", "Selecione uma pasta de saída.")
            return
            
        style = self.video_borders.get_effective_style()
        color = self.video_borders.get_border_color()
        subtitles = self.subtitle_manager.get_subtitles()
        
        # Pega as proporções dinâmicas atuais da moldura (vídeo interno)
        w_ratio = self.video_borders.video_w_ratio_var.get()
        h_ratio = self.video_borders.video_h_ratio_var.get()
        
        # Coletar configurações de áudio
        audio_settings = {
            'remove_audio': self.audio_settings_ui.remove_audio_var.get(),
            'use_folder_audio': self.audio_settings_ui.use_folder_audio_var.get() or self.audio_settings_ui.select_folder_audio_var.get(),
            'random_mode': self.audio_settings_ui.use_folder_audio_var.get(),
            'sync_duration': self.audio_settings_ui.sync_duration_var.get(),
            'audio_folder': self.audio_settings_ui.audio_folder_path.get()
        }
        
        watermark_data = self.watermark_ui.get_state() if self.watermark_ui else None
        mesclagem_data = self.mesclagem_ui.get_state() if self.mesclagem_ui else None
        
        # Obter configuração de enhancement
        enable_enhancement = self.video_controls.enable_enhancement.get()
        
        self.render_btn.config(state="disabled")
        
        if self.processar_pasta_var and self.processar_pasta_var.get():
            self.status_label.config(text="Iniciando processamento da pasta...")
            self.folder_processor.process_folder(
                input_path, 
                output_folder, 
                style, 
                color, 
                subtitles, 
                self.emoji_manager, 
                audio_settings,
                status_callback=lambda msg: self.status_label.config(text=msg),
                completion_callback=self.on_folder_process_complete,
                process_all_folder=True,
                watermark_data=watermark_data,
                mesclagem_data=mesclagem_data,
                tab_number=tab_number,
                enable_enhancement=enable_enhancement,
                video_width_ratio=w_ratio,
                video_height_ratio=h_ratio
            )
        else:
            self.status_label.config(text="Adicionado à fila de renderização...")
            # Usar a mesma lógica de fila para vídeo individual
            self.folder_processor.process_folder(
                input_path, 
                output_folder, 
                style, 
                color, 
                subtitles, 
                self.emoji_manager, 
                audio_settings,
                status_callback=lambda msg: self.status_label.config(text=msg),
                completion_callback=lambda s, t, e: self.on_single_render_complete(s, t, e, input_path),
                process_all_folder=False,
                watermark_data=watermark_data,
                mesclagem_data=mesclagem_data,
                tab_number=tab_number,
                enable_enhancement=enable_enhancement,
                video_width_ratio=w_ratio,
                video_height_ratio=h_ratio
            )
        
        # O botão volta ao normal via callback ou quando a fila termina
        # Para simplificar, vamos deixar o botão habilitado para permitir enfileirar mais
        self.render_btn.config(state="normal")

    def on_folder_process_complete(self, success_count, total, errors):
        self.render_btn.config(state="normal")
        if errors:
            error_msg = "\n".join(errors[:5])
            if len(errors) > 5:
                error_msg += f"\n... e mais {len(errors)-5} erros."
            messagebox.showwarning("Processamento Concluído", f"Processados {success_count} de {total} vídeos.\n\nErros:\n{error_msg}")
        else:
            messagebox.showinfo("Sucesso", f"Todos os {total} vídeos foram processados com sucesso!")
        
        # Enviar Notificação Push
        msg = f"Processados {success_count} de {total} vídeos."
        if errors:
            msg += f" ({len(errors)} erros)"
        Notifier.notify("Renderização em Lote Finalizada", msg)

    def on_single_render_complete(self, success_count, total, errors, input_path):
        self.render_btn.config(state="normal")
        video_name = os.path.basename(input_path)
        
        if success_count > 0:
            Notifier.notify("Renderização Finalizada", f"O vídeo '{video_name}' foi renderizado com sucesso!")
        elif errors:
            Notifier.notify("Erro na Renderização", f"Falha ao renderizar '{video_name}'.")

    def run_render(self, input_path, output_folder, style, color, subtitles, emoji_manager, audio_settings):
        success, result = self.editor.render_video(input_path, output_folder, style, color, subtitles, emoji_manager, audio_settings)
        
        if success:
            self.status_label.config(text=f"Concluído! Salvo em: {result}")
            messagebox.showinfo("Sucesso", f"Vídeo renderizado com sucesso!\nSalvo em: {result}")
        else:
            self.status_label.config(text=f"Erro: {result}")
            messagebox.showerror("Erro", f"Falha na renderização:\n{result}")
            
        self.render_btn.config(state="normal")
    def get_state(self):
        return {
            "output_path": self.output_path.get()
        }

    def set_state(self, state):
        self.output_path.set(state.get("output_path", ""))
