import moviepy.editor as mp
import cv2
import numpy as np

class VideoEditor:
    def __init__(self):
        self.width = 1080
        self.height = 1920
        self.video_width_ratio = 0.78
        self.video_height_ratio = 0.70
        self.border_size = 14
        self.blur_intensity = 25

    def apply_blur_opencv(self, get_frame, t):
        frame = get_frame(t)
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        blurred = cv2.GaussianBlur(
            frame_bgr,
            (self.blur_intensity * 2 + 1, self.blur_intensity * 2 + 1),
            0
        )
        return cv2.cvtColor(blurred, cv2.COLOR_BGR2RGB)

    def create_composition(self, video_clip, style, border_color_name="white"):
        """
        Cria a composição do vídeo baseada no estilo selecionado.
        Retorna um CompositeVideoClip.
        """
        # Garantir tipos padrão do Python
        style = str(style)
        border_color_name = str(border_color_name)
        
        # 0. Garantir que o vídeo de entrada seja RGB
        # Se for grayscale, MoviePy pode carregar como 2D ou 3D com canais iguais.
        # Vamos forçar uma verificação inicial.
        def ensure_rgb(get_frame, t):
            frame = get_frame(t)
            if len(frame.shape) == 2:
                return np.dstack([frame, frame, frame])
            return frame
            
        # Aplicar filtro de conversão se necessário, mas fl() é custoso se não precisar.
        # Vamos verificar o primeiro frame.
        try:
            first_frame = video_clip.get_frame(0)
            if len(first_frame.shape) == 2:
                print("DEBUG: Input video is grayscale. Converting to RGB.")
                video_clip = video_clip.fl(ensure_rgb)
        except Exception as e:
            print(f"DEBUG: Error checking input video: {e}")

        # Dimensões calculadas
        video_width = int(self.width * self.video_width_ratio)
        video_height = int(self.height * self.video_height_ratio)
        
        frame_width = video_width + self.border_size * 2
        frame_height = video_height + self.border_size * 2
        
        x_pos = (self.width - frame_width) // 2
        y_pos = (self.height - frame_height) // 2

        # 1. Preparar o Background
        if "Blur" in style:
            # Fundo Desfocado
            background = (
                video_clip
                .resize((self.width, self.height))
                .fl(self.apply_blur_opencv)
            )
        elif "black" in style or "Black" in style:
            # Fundo Preto
            background = mp.ColorClip(
                size=(self.width, self.height),
                color=(0, 0, 0),
                duration=video_clip.duration
            )
        elif "White" in style:
             # Fundo Branco (supondo)
            background = mp.ColorClip(
                size=(self.width, self.height),
                color=(255, 255, 255),
                duration=video_clip.duration
            )
        else:
            # Default
            background = mp.ColorClip(
                size=(self.width, self.height),
                color=(0, 0, 0),
                duration=video_clip.duration
            )

        # 2. Preparar o Vídeo Central
        main_video = video_clip.resize((video_width, video_height))
        
        # 3. Preparar a Moldura (se houver)
        layers = [background]
        
        if "Moldura" in style:
            # Converter nome da cor para RGB se necessário
            # MoviePy aceita strings, mas para garantir compatibilidade com old/black.py (que usa tupla)
            # e evitar erros de parsing, vamos converter hex para tupla.
            c_color = border_color_name
            if isinstance(c_color, str) and c_color.startswith("#"):
                try:
                    # Remove # e converte para tuple (R, G, B)
                    h = c_color.lstrip('#')
                    c_color = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
                except:
                    pass # Mantém como string se falhar
            
            frame = mp.ColorClip(
                size=(frame_width, frame_height),
                color=c_color,
                duration=video_clip.duration
            )
            
            # DEBUG: Verificar shape da moldura
            try:
                f_frame = frame.get_frame(0)
                if len(f_frame.shape) == 2:
                    print(f"DEBUG: Frame (border) is 2D {f_frame.shape}. Converting to RGB.")
                    # ColorClip deve ser RGB, mas se der erro...
                    frame = frame.fl(ensure_rgb)
            except:
                pass

            layers.append(frame.set_position((x_pos, y_pos)))
            
            # Vídeo centralizado na moldura
            layers.append(main_video.set_position((x_pos + self.border_size, y_pos + self.border_size)))
        else:
            # Sem moldura
            center_x = (self.width - video_width) // 2
            center_y = (self.height - video_height) // 2
            layers.append(main_video.set_position((center_x, center_y)))

        # 4. Composição Final
        final = mp.CompositeVideoClip(
            layers,
            size=(self.width, self.height)
        ).set_duration(video_clip.duration)
        
        if video_clip.audio:
            final = final.set_audio(video_clip.audio)
            
        return final

    def generate_preview_image(self, video_path, style, border_color="white"):
        """
        Gera uma imagem de preview (frame 0) com o estilo aplicado.
        Retorna um objeto PIL Image ou numpy array.
        """
        try:
            # Carregar apenas um frame ou clip curto para preview
            clip = mp.VideoFileClip(video_path)
            # Cortar para 1 frame para processamento rápido? 
            # Mas CompositeVideoClip precisa de duração.
            # Vamos pegar um subclip de 0.1s
            subclip = clip.subclip(0, 0.1)
            
            final_clip = self.create_composition(subclip, style, border_color)
            
            # Pegar o frame 0
            frame = final_clip.get_frame(0)
            
            # Fechar clips
            clip.close()
            final_clip.close()
            
            return frame
        except Exception as e:
            print(f"Erro ao gerar preview: {e}")
            return None

    def render_video(self, input_path, output_path, style, border_color="white"):
        """
        Renderiza o vídeo final com os efeitos aplicados.
        """
        try:
            clip = mp.VideoFileClip(input_path)
            final_clip = self.create_composition(clip, style, border_color)
            
            # Definir nome do arquivo de saída
            # Se output_path for diretório, criar nome. Se for arquivo, usar nome.
            # Assumindo que output_path vem do OutputVideo e é uma pasta (baseado no código atual)
            import os
            filename = os.path.basename(input_path)
            name, ext = os.path.splitext(filename)
            output_file = os.path.join(output_path, f"{name}_edited{ext}")
            
            # Escrever arquivo
            final_clip.write_videofile(
                output_file,
                codec="libx264",
                audio_codec="aac",
                fps=30,
                preset="medium", # Bom balanço entre velocidade e qualidade
                threads=4
            )
            
            clip.close()
            final_clip.close()
            return True, output_file
        except Exception as e:
            print(f"Erro ao renderizar: {e}")
            return False, str(e)
