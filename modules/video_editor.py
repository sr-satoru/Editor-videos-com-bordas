import moviepy.editor as mp
import cv2
import numpy as np
from PIL import Image, ImageDraw
from modules.subiitels.renderizador_legendas import RenderizadorLegendas
from modules.subiitels.gerenciador_emojis import GerenciadorEmojis
from modules.editar_com_legendas import VideoRenderer

class VideoEditor:
    def __init__(self):
        self.width = 1080
        self.height = 1920
        self.video_width_ratio = 0.78
        self.video_height_ratio = 0.70
        self.border_size = 14
        self.blur_intensity = 25
        # O VideoRenderer será instanciado sob demanda ou no init se houver emoji_manager

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
        # Se for "Sem moldura" e não tiver outros estilos, usa tela cheia
        if style == "Sem moldura":
            video_width = self.width
            video_height = self.height
        else:
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

    def generate_base_preview(self, video_path, style, border_color="white", border_size_preview=14):
        """
        Gera o frame base do preview (sem legendas).
        """
        renderer = VideoRenderer(None)
        style_lower = style.lower()
        border_enabled = "moldura" in style_lower or "black" in style_lower or "white" in style_lower or "blur" in style_lower
        
        try:
            clip = mp.VideoFileClip(video_path)
            v_w, v_h, _ = renderer.calculate_video_dimensions(border_enabled, border_size_preview, is_preview=True)
            
            subclip = clip.subclip(0, 0.1)
            video_resized = subclip.resize((v_w, v_h))
            
            frame = renderer.render_frame(
                video_resized.get_frame(0),
                subtitles=[],
                border_enabled=border_enabled,
                border_size_preview=border_size_preview,
                border_color=border_color,
                border_style=style,
                is_preview=True
            )
            
            clip.close()
            video_resized.close()
            return frame
        except Exception as e:
            print(f"Erro ao gerar base preview: {e}")
            return None

    def generate_preview_image(self, video_path, style, border_color="white", subtitles=None, emoji_manager=None, base_frame=None, border_size_preview=14, watermark_data=None):
        """
        Gera uma imagem de preview.
        """
        renderer = VideoRenderer(emoji_manager)
        style_lower = style.lower()
        border_enabled = "moldura" in style_lower or "black" in style_lower or "white" in style_lower or "blur" in style_lower

        if base_frame is not None:
            # Se já temos o base_frame (que é 1080p), apenas desenhamos as legendas
            image = Image.fromarray(base_frame)
            draw = ImageDraw.Draw(image)
            
            # Precisamos do offset da borda para as legendas
            v_w, v_h, _ = renderer.calculate_video_dimensions(border_enabled, border_size_preview, is_preview=True)
            offset_x, offset_y = renderer.get_offsets(v_w, v_h)
            scale_factor = renderer.get_scale_factor()

            for sub in (subtitles or []):
                renderer.subtitle_renderer.draw_subtitle(
                    draw, 
                    sub,
                    scale_factor=scale_factor,
                    offset_x=offset_x,
                    offset_y=offset_y,
                    emoji_scale=1.0 # Padrão para preview do editor
                )
            
            # Desenhar marca d'água se houver
            if watermark_data and watermark_data.get("add_text_mark"):
                renderer._draw_watermark(draw, watermark_data, scale_factor, offset_x, offset_y)
            
            return np.array(image)
        else:
            # Gera do zero
            try:
                clip = mp.VideoFileClip(video_path)
                v_w, v_h, _ = renderer.calculate_video_dimensions(border_enabled, border_size_preview, is_preview=True)
                frame = clip.get_frame(0)
                video_resized = Image.fromarray(frame).resize((v_w, v_h), Image.Resampling.LANCZOS)
                
                # Se for blur, gerar o frame de fundo
                bg_frame = None
                if "blur" in (style or "").lower():
                    raw_bg = np.array(Image.fromarray(frame).resize((renderer.OUTPUT_WIDTH, renderer.OUTPUT_HEIGHT), Image.Resampling.LANCZOS))
                    bg_frame = renderer.apply_blur_opencv(raw_bg)

                final_frame = renderer.render_frame(
                    np.array(video_resized),
                    subtitles,
                    border_enabled,
                    border_size_preview,
                    border_color,
                    style,
                    background_frame=bg_frame,
                    is_preview=True,
                    watermark_data=watermark_data
                )
                clip.close()
                return final_frame
            except Exception as e:
                print(f"Erro ao gerar preview: {e}")
                return None

    def render_video(self, input_path, output_path, style, border_color="white", subtitles=None, emoji_manager=None, audio_settings=None, watermark_data=None, mesclagem_data=None, tab_number=None, enable_enhancement=False):
        """
        Renderiza o vídeo final usando o VideoRenderer.
        """
        renderer = VideoRenderer(emoji_manager)
        style_lower = style.lower()
        border_enabled = "moldura" in style_lower or "black" in style_lower or "white" in style_lower or "blur" in style_lower
        border_size_preview = 14 # Padrão
        
        success, result = renderer.render_video(
            input_path,
            output_path,
            border_enabled,
            border_size_preview,
            border_color,
            style,
            subtitles,
            audio_settings=audio_settings,
            watermark_data=watermark_data,
            mesclagem_data=mesclagem_data,
            tab_number=tab_number,
            enable_enhancement=enable_enhancement
        )
        return success, result
