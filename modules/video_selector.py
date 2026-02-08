import tkinter as tk
import time
import os
import tempfile
import pygame
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
        self.clip = None
        self.is_playing = False
        self.current_time = 0.0
        self.update_job = None
        
        # Áudio
        self.temp_audio_path = None
        self.loop_enabled = False
        pygame.mixer.init()
        
        # Callbacks
        self.on_duration_changed = None
        self.on_time_changed = None
        self.on_playback_status_changed = None
        self.last_update_time = 0

    def select_video(self):
        # Abre diálogo para escolher vídeo
        filepath = filedialog.askopenfilename(
            filetypes=[("Vídeos", "*.mp4 *.mov *.avi *.mkv")]
        )
        if filepath:
            self.load_video(filepath)

    def load_video(self, filepath):
        # Parar vídeo anterior se estiver tocando
        self.pause_video()
        
        # Limpar áudio anterior
        if self.temp_audio_path and os.path.exists(self.temp_audio_path):
            try:
                pygame.mixer.music.unload()
                os.remove(self.temp_audio_path)
            except: pass

        # Carrega o vídeo usando moviepy
        self.current_video_path = filepath
        if self.clip:
            self.clip.close()
            
        self.clip = VideoFileClip(filepath)
        self.current_time = 0.0
        
        # Extrair áudio para preview
        if self.clip.audio:
            fd, self.temp_audio_path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)
            print(f"Extraindo áudio para: {self.temp_audio_path}")
            self.clip.audio.write_audiofile(self.temp_audio_path, logger=None)
            pygame.mixer.music.load(self.temp_audio_path)

        if self.on_duration_changed:
            self.on_duration_changed(self.clip.duration)

        # Mostra frame inicial
        self.show_frame(0)

    def show_frame(self, t):
        if not self.clip: return
        
        try:
            # Pega o frame no tempo t
            frame = self.clip.get_frame(t)
            img = Image.fromarray(frame)
            img = img.resize((360, 640))  # ajusta ao tamanho do canvas
            self.preview_image = ImageTk.PhotoImage(img)

            # Exibe no canvas
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(0, 0, anchor="nw", image=self.preview_image)
        except Exception as e:
            print(f"Erro ao exibir frame: {e}")

    def toggle_play(self):
        if self.is_playing:
            self.pause_video()
        else:
            self.play_video()

    def play_video(self):
        if not self.clip: return
        self.is_playing = True
        self.last_update_time = time.time()
        
        # Iniciar áudio
        if self.temp_audio_path:
            pygame.mixer.music.play(start=self.current_time)
            
        self._update_loop()
        if self.on_playback_status_changed:
            self.on_playback_status_changed(True)

    def pause_video(self):
        self.is_playing = False
        
        # Pausar áudio
        try:
            if pygame and pygame.mixer and pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except (AttributeError, pygame.error): 
            pass
        
        if self.update_job:
            try:
                self.preview_canvas.after_cancel(self.update_job)
            except: pass
            self.update_job = None
        if self.on_playback_status_changed:
            self.on_playback_status_changed(False)

    def seek(self, t):
        if not self.clip: return
        self.current_time = max(0, min(t, self.clip.duration))
        self.show_frame(self.current_time)
        
        # Sincronizar áudio se estiver tocando
        if self.is_playing and self.temp_audio_path:
            pygame.mixer.music.play(start=self.current_time)

    def _update_loop(self):
        if not self.is_playing or not self.clip:
            return

        now = time.time()
        dt = now - self.last_update_time
        self.last_update_time = now
        
        # Avança tempo baseado no tempo real decorrido
        self.current_time += dt
        
        if self.current_time >= self.clip.duration:
            self.current_time = 0
            # Resetar áudio no loop para manter sincronia
            if self.temp_audio_path:
                try:
                    pygame.mixer.music.play(0)
                except: pass
            
            if not getattr(self, 'loop_enabled', True):
                self.pause_video()
                return

        self.show_frame(self.current_time)
        
        if self.on_time_changed:
            self.on_time_changed(self.current_time)

        # Agenda próximo ciclo (target ~30fps)
        self.update_job = self.preview_canvas.after(30, self._update_loop)

    def close(self):
        try:
            self.pause_video()
        except: pass
        
        if self.clip:
            try:
                self.clip.close()
            except: pass
            self.clip = None
            
        if self.temp_audio_path and os.path.exists(self.temp_audio_path):
            try:
                if pygame and pygame.mixer and pygame.mixer.get_init():
                    pygame.mixer.music.unload()
                os.remove(self.temp_audio_path)
                self.temp_audio_path = None
            except: pass

    def __del__(self):
        self.close()
