import tkinter as tk
from tkinter import ttk, filedialog

from tkinter import messagebox
from modules.video_editor import VideoEditor
import threading

class OutputVideo(ttk.LabelFrame):
    def __init__(self, parent, video_controls, video_borders):
        super().__init__(parent, text="Salvar Vídeo Processado")
        self.pack(fill="x", pady=10)
        
        self.video_controls = video_controls
        self.video_borders = video_borders
        self.editor = VideoEditor()

        self.output_path = tk.StringVar()

        path_frame = ttk.Frame(self)
        path_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(path_frame, text="Caminho de saída:").pack(side="left")

        ttk.Entry(path_frame, textvariable=self.output_path).pack(
            side="left", fill="x", expand=True, padx=5
        )

        ttk.Button(path_frame, text="Escolher Pasta", command=self.select_output_folder).pack(side="left", padx=5)
        
        # Botão de Renderizar
        self.render_btn = ttk.Button(self, text="Renderizar Vídeo", command=self.start_rendering)
        self.render_btn.pack(pady=10)
        
        self.status_label = ttk.Label(self, text="")
        self.status_label.pack(pady=5)

    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_path.set(folder)

    def start_rendering(self):
        input_path = self.video_controls.video_selector.current_video_path
        output_folder = self.output_path.get()
        
        if not input_path:
            messagebox.showwarning("Aviso", "Selecione um vídeo primeiro.")
            return
            
        if not output_folder:
            messagebox.showwarning("Aviso", "Selecione uma pasta de saída.")
            return
            
        style = self.video_borders.get_style()
        color = self.video_borders.get_border_color()
        
        self.render_btn.config(state="disabled")
        self.status_label.config(text="Renderizando... Aguarde.")
        
        # Rodar em thread para não travar a UI
        threading.Thread(target=self.run_render, args=(input_path, output_folder, style, color)).start()

    def run_render(self, input_path, output_folder, style, color):
        success, result = self.editor.render_video(input_path, output_folder, style, color)
        
        if success:
            self.status_label.config(text=f"Concluído! Salvo em: {result}")
            messagebox.showinfo("Sucesso", f"Vídeo renderizado com sucesso!\nSalvo em: {result}")
        else:
            self.status_label.config(text=f"Erro: {result}")
            messagebox.showerror("Erro", f"Falha na renderização:\n{result}")
            
        self.render_btn.config(state="normal")
