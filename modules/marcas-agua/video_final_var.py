import moviepy.editor as mp
import os

class FinalVideo:
    def __init__(self, video_path):
        self.video_path = video_path

    def apply(self, main_video_clip):
        """
        Concatena o vídeo final ao clip de vídeo principal.
        """
        if not self.video_path or not os.path.exists(self.video_path):
            return main_video_clip

        try:
            final_clip = mp.VideoFileClip(self.video_path)
            
            # Garantir que o vídeo final tenha as mesmas dimensões do vídeo principal
            # para evitar problemas na concatenação.
            final_clip_resized = final_clip.resize(newsize=(main_video_clip.w, main_video_clip.h))
            
            # Concatenar clips
            combined = mp.concatenate_videoclips([main_video_clip, final_clip_resized])
            return combined
        except Exception as e:
            print(f"Erro ao adicionar vídeo final: {e}")
            return main_video_clip
