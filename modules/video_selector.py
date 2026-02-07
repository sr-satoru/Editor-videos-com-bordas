import tkinter as tk
from tkinter import filedialog
from moviepy.editor import VideoFileClip, vfx
from PIL import Image, ImageTk

class VideoSelector:
    def __init__(self, parent, preview_canvas):
        """
        parent: frame onde o botão será adicionado
        preview_canvas: canvas onde o preview do vídeo vai aparecer
        """
        self.preview_canvas = preview_canvas

        # Botão de selecionar vídeo
        self.btn = tk.Button(parent, text="Selecionar Vídeo", command=self.select_video)
        self.btn.is_accent = True
        self.btn.pack(side="left", padx=10, pady=10)

        # Variável para armazenar a imagem do preview
        self.preview_image = None
        self.current_video_path = None

    def select_video(self):
        # Abre diálogo para escolher vídeo
        filepath = filedialog.askopenfilename(
            filetypes=[("Vídeos", "*.mp4 *.mov *.avi *.mkv")]
        )
        if filepath:
            self.load_video(filepath)

    def load_video(self, filepath):
        # Carrega o vídeo usando moviepy
        self.current_video_path = filepath
        clip = VideoFileClip(filepath)

        # Pega o primeiro frame como preview
        frame = clip.get_frame(0)  # frame inicial
        img = Image.fromarray(frame)
        img = img.resize((360, 640))  # ajusta ao tamanho do canvas
        self.preview_image = ImageTk.PhotoImage(img)

        # Exibe no canvas
        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(0, 0, anchor="nw", image=self.preview_image)
