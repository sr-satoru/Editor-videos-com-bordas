import moviepy.editor as mp

class TextWatermark:
    def __init__(self, text, font="Arial", font_size=30, color="white", opacity=100):
        self.text = text
        self.font = font
        self.font_size = font_size
        self.color = color
        self.opacity = opacity / 100.0

    def apply(self, video_clip):
        """
        Aplica a marca d'água de texto ao clip de vídeo.
        """
        if not self.text:
            return video_clip

        # Criar o clip de texto
        txt_clip = mp.TextClip(
            self.text,
            fontsize=self.font_size,
            color=self.color,
            font=self.font,
            method='label'
        ).set_opacity(self.opacity).set_duration(video_clip.duration)

        # Posicionar a marca d'água (ex: canto inferior direito com margem)
        # Por enquanto, vamos deixar no centro ou permitir customização futura
        txt_clip = txt_clip.set_position(('right', 'bottom')).margin(right=20, bottom=20, opacity=0)

        return mp.CompositeVideoClip([video_clip, txt_clip])
