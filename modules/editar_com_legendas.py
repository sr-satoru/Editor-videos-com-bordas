import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import moviepy.editor as mp
from moviepy.video.VideoClip import VideoClip
from modules.subiitels.renderizador_legendas import RenderizadorLegendas
from modules.audio.gerenciador_audio import GerenciadorAudio
from modules import video_enhancement
from modules import mesclagem_back

class VideoRenderer:
    """
    Centraliza todos os cálculos, proporções e lógica de renderização final do vídeo,
    espelhando o comportamento do simples.py.
    """
    OUTPUT_WIDTH = 1080
    OUTPUT_HEIGHT = 1920
    BASE_WIDTH = 360.0  # Base usada no preview para cálculos de escala (360x640)
    ASPECT_RATIO = 9 / 16
    
    # Proporções do vídeo interno (baseado no old/black.py)
    VIDEO_WIDTH_RATIO = 0.78
    VIDEO_HEIGHT_RATIO = 0.70

    def __init__(self, emoji_manager):
        self.emoji_manager = emoji_manager
        self.subtitle_renderer = RenderizadorLegendas(emoji_manager)
        self.audio_manager = GerenciadorAudio()
        self.blur_intensity = 25
        self.enhancement_enabled = False

    def apply_blur_opencv(self, frame):
        """Aplica blur em um frame usando OpenCV"""
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        blurred = cv2.GaussianBlur(
            frame_bgr,
            (self.blur_intensity * 2 + 1, self.blur_intensity * 2 + 1),
            0
        )
        return cv2.cvtColor(blurred, cv2.COLOR_BGR2RGB)

    def get_scale_factor(self):
        """Retorna o fator de escala entre o preview (270p) e o output (1080p)"""
        return self.OUTPUT_WIDTH / self.BASE_WIDTH

    def calculate_video_dimensions(self, border_enabled, border_size_preview, is_preview=False):
        """
        Calcula as dimensões do vídeo interno baseado na borda e proporções.
        border_size_preview: tamanho da borda definido na UI (base 360p)
        """
        if not border_enabled:
            return self.OUTPUT_WIDTH, self.OUTPUT_HEIGHT, 0

        # Se houver borda, usamos as proporções fixas do old/black.py
        video_width = int(self.OUTPUT_WIDTH * self.VIDEO_WIDTH_RATIO)
        video_height = int(self.OUTPUT_HEIGHT * self.VIDEO_HEIGHT_RATIO)
        
        if is_preview:
            # No preview, deixamos 30% maior para melhor visibilidade na interface
            scaled_border_size = int(border_size_preview * 1.3)
        else:
            # No vídeo final, usamos o valor original do spinbox
            scaled_border_size = int(border_size_preview)
            
        return video_width, video_height, scaled_border_size

    def get_offsets(self, v_w, v_h):
        """Retorna os offsets X e Y para centralizar o vídeo no fundo 1080x1920"""
        offset_x = (self.OUTPUT_WIDTH - v_w) // 2
        offset_y = (self.OUTPUT_HEIGHT - v_h) // 2
        return offset_x, offset_y

    def create_background(self, style, border_color, duration, background_frame=None):
        """Cria o frame de fundo baseado no estilo"""
        if background_frame is not None and "blur" in (style or "").lower():
            return Image.fromarray(background_frame)
            
        bg_color = (0, 0, 0) # Default black
        
        if style:
            style_lower = style.lower()
            if "white" in style_lower:
                bg_color = (255, 255, 255)
            elif "black" in style_lower:
                bg_color = (0, 0, 0)
            # Removido fallback que usava border_color como fundo

        if "degradê" in (style or "").lower():
            return self.create_gradient_background(border_color)
        
        return Image.new('RGB', (self.OUTPUT_WIDTH, self.OUTPUT_HEIGHT), bg_color)

    def create_gradient_background(self, base_color):
        """Cria um fundo com degradê nas bordas"""
        color = base_color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        
        image = Image.new('RGB', (self.OUTPUT_WIDTH, self.OUTPUT_HEIGHT))
        pixels = image.load()
        
        gradient_area = 50  # Pixels de degradê
        
        for x in range(self.OUTPUT_WIDTH):
            for y in range(self.OUTPUT_HEIGHT):
                dist_x = min(x, self.OUTPUT_WIDTH - x - 1)
                dist_y = min(y, self.OUTPUT_HEIGHT - y - 1)
                min_dist = min(dist_x, dist_y)
                
                if min_dist < gradient_area:
                    intensity = min_dist / float(gradient_area)
                    pixels[x, y] = (int(r * intensity), int(g * intensity), int(b * intensity))
                else:
                    pixels[x, y] = (r, g, b)
        return image

    def render_frame(self, video_frame, subtitles, border_enabled, border_size_preview, border_color, border_style, emoji_scale=1.0, background_frame=None, is_preview=False, watermark_data=None):
        """
        Renderiza um único frame com bordas, legendas e marca d'água.
        video_frame: numpy array do frame do vídeo (já redimensionado para a área interna)
        background_frame: numpy array do frame de fundo (opcional, usado para blur)
        watermark_data: dicionário com as configurações da marca d'água
        """
        video_image = Image.fromarray(video_frame.astype(np.uint8))
        
        # Se o estilo for "Sem moldura", forçamos border_enabled para False para garantir
        if border_style == "Sem moldura":
            border_enabled = False

        if border_enabled:
            # Com bordas: usa o scale_factor padrão baseado em BASE_WIDTH (360)
            scale_factor = self.get_scale_factor()
            
            # 1. Calcular dimensões
            v_w, v_h, scaled_border = self.calculate_video_dimensions(border_enabled, border_size_preview, is_preview=is_preview)
            
            # Fundo (Background)
            final_image = self.create_background(border_style, border_color, 0, background_frame=background_frame)
            
            # Centralizar vídeo no fundo (ou na moldura)
            paste_x, paste_y = self.get_offsets(v_w, v_h)

            if border_style and "Moldura" in border_style:
                # O tamanho da moldura é o tamanho do vídeo + border_size em cada lado
                frame_width = v_w + (scaled_border * 2)
                frame_height = v_h + (scaled_border * 2)
                
                # Cor da moldura: usa a cor selecionada na UI
                if isinstance(border_color, str) and border_color.startswith("#"):
                    h = border_color.lstrip('#')
                    frame_color = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
                else:
                    frame_color = border_color

                frame_image = Image.new('RGB', (frame_width, frame_height), frame_color)
                
                # Centralizar moldura no fundo
                frame_x = (self.OUTPUT_WIDTH - frame_width) // 2
                frame_y = (self.OUTPUT_HEIGHT - frame_height) // 2
                final_image.paste(frame_image, (frame_x, frame_y))
                
                # O vídeo já está centralizado via paste_x, paste_y
                final_image.paste(video_image, (paste_x, paste_y))
            else:
                # Sem moldura, apenas centraliza o vídeo no fundo
                final_image.paste(video_image, (paste_x, paste_y))
            
            # O offset para as legendas deve ser relativo ao canto superior esquerdo da imagem final
            offset_x = paste_x
            offset_y = paste_y
        else:
            # Sem borda: o vídeo preenche toda a tela 1080x1920
            # O scale_factor deve ser calculado como OUTPUT_WIDTH / BASE_WIDTH (1080 / 360 = 3.0)
            # mas as legendas devem ser posicionadas diretamente na imagem final sem offset
            scale_factor = self.get_scale_factor()
            final_image = video_image.resize((self.OUTPUT_WIDTH, self.OUTPUT_HEIGHT), Image.Resampling.LANCZOS)
            # USER REQUEST: Aplica o mesmo offset que seria usado na moldura
            # Simula as dimensões com borda para calcular o offset correto
            v_w_dummy, v_h_dummy, _ = self.calculate_video_dimensions(True, border_size_preview, is_preview=is_preview)
            offset_x, offset_y = self.get_offsets(v_w_dummy, v_h_dummy)

        # 2. Desenhar legendas
        if subtitles:
            draw = ImageDraw.Draw(final_image)
            for sub in subtitles:
                self.subtitle_renderer.draw_subtitle(
                    draw, 
                    sub, 
                    scale_factor=scale_factor,
                    emoji_scale=emoji_scale,
                    offset_x=offset_x,
                    offset_y=offset_y
                )
                
        # 3. Desenhar marca d'água em texto
        if watermark_data and watermark_data.get("add_text_mark"):
            draw = ImageDraw.Draw(final_image)
            self._draw_watermark(draw, watermark_data, scale_factor, offset_x, offset_y)
            
        # 4. Desenhar Logo (Imagem)
        if watermark_data and watermark_data.get("logo_path"):
            draw = ImageDraw.Draw(final_image)
            self._draw_logo(final_image, watermark_data, scale_factor, offset_x, offset_y)
                
        return np.array(final_image)

    def _draw_logo(self, final_image, data, scale_factor, offset_x, offset_y):
        """Desenha a logo (imagem) sobre o frame final"""
        logo_path = data.get("logo_path")
        if not logo_path or not os.path.exists(logo_path):
            return

        try:
            # Carregar logo
            logo = Image.open(logo_path).convert("RGBA")
            
            # Calcular tamanho final
            base_scale = data.get("logo_scale", 0.2)
            
            # A escala deve ser relativa ao tamanho do vídeo de saída (1080p)
            # Se scale_factor for diferente (ex: preview), ajustamos
            # Mas o "scale" do usuário é relativo ao tamanho original da imagem ou ao vídeo?
            # Vamos assumir que scale=1.0 significa tamanho original da imagem
            
            # Aplicar escala do usuário e escala do renderizador (preview vs final)
            final_scale = base_scale * scale_factor
            
            new_w = int(logo.width * final_scale)
            new_h = int(logo.height * final_scale)
            
            if new_w < 1 or new_h < 1:
                return
                
            logo = logo.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Calcular posição
            # As coordenadas x, y vêm do usuário (baseado no vídeo interno)
            # Precisamos somar o offset da borda
            user_x = data.get("logo_x", 50)
            user_y = data.get("logo_y", 50)
            
            # Ajustar coordenadas para a escala atual (se x,y forem absolutos em 1080p)
            # Se x,y forem relativos ao vídeo interno (sem borda), precisamos escalar
            # Vamos assumir que x,y são coordenadas no espaço do vídeo (antes do resize final)
            # Mas o sistema de legendas usa coordenadas fixas baseadas em 360p? Não, usa coordenadas do vídeo.
            
            # O sistema de legendas recebe offset_x e offset_y que já consideram a escala e a borda.
            # E as coordenadas da legenda são multiplicadas pelo scale_factor.
            
            final_x = int((user_x * scale_factor) + offset_x)
            final_y = int((user_y * scale_factor) + offset_y)
            
            # Colar logo (com transparência)
            # Se final_image for RGB, precisamos usar mask
            final_image.paste(logo, (final_x, final_y), logo)
            
        except Exception as e:
            print(f"Erro ao desenhar logo: {e}")

    def get_logo_bbox(self, data, scale_factor, offset_x, offset_y):
        """Calcula o bounding box da logo para interação no preview"""
        logo_path = data.get("logo_path")
        if not logo_path or not os.path.exists(logo_path):
            return None

        try:
            logo = Image.open(logo_path)
            base_scale = data.get("logo_scale", 0.2)
            final_scale = base_scale * scale_factor
            
            new_w = int(logo.width * final_scale)
            new_h = int(logo.height * final_scale)
            
            user_x = data.get("logo_x", 50)
            user_y = data.get("logo_y", 50)
            
            final_x = int((user_x * scale_factor) + offset_x)
            final_y = int((user_y * scale_factor) + offset_y)
            
            return (final_x, final_y, final_x + new_w, final_y + new_h)
        except:
            return None

    def _draw_watermark(self, draw, data, scale_factor, offset_x, offset_y):
        """Desenha a marca d'água de texto usando o mesmo renderer das legendas"""
        text = data.get("text_mark", "")
        if not text:
            return

        # Converter dados da marca d'água para o formato de legenda esperado pelo renderer
        hex_color = data.get("text_color", "#FFFFFF")
        opacity = data.get("opacity", 100) / 100.0
        
        # Converter hex para RGB e adicionar alpha
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        rgba_color = (*rgb, int(255 * opacity))

        sub_format = {
            "text": text,
            "x": data.get("x", 135),
            "y": data.get("y", 400),
            "font": data.get("font", "Arial"),
            "size": data.get("font_size", 30),
            "color": rgba_color,
            "border": None,
            "bg": None,
            "border_thickness": 0
        }

        self.subtitle_renderer.draw_subtitle(
            draw, 
            sub_format, 
            scale_factor=scale_factor, 
            offset_x=offset_x, 
            offset_y=offset_y
        )

    def get_watermark_bbox(self, data, scale_factor, offset_x, offset_y):
        """Calcula o bounding box da marca d'água usando o mesmo renderer das legendas"""
        text = data.get("text_mark", "")
        if not text:
            return None

        sub_format = {
            "text": text,
            "x": data.get("x", 135),
            "y": data.get("y", 400),
            "font": data.get("font", "Arial"),
            "size": data.get("font_size", 30)
        }

        return self.subtitle_renderer.get_subtitle_bbox(
            sub_format, 
            scale_factor=scale_factor, 
            offset_x=offset_x, 
            offset_y=offset_y
        )

    def render_video(self, input_path, output_folder, border_enabled, border_size_preview, border_color, border_style, subtitles, emoji_scale=1.0, threads=4, audio_settings=None, watermark_data=None, mesclagem_data=None, tab_number=None, enable_enhancement=False):
        """Renderiza o vídeo completo"""
        try:
            # 0. Opção de Ocultar Legendas no Vídeo Principal
            actual_subtitles = subtitles
            if mesclagem_data and mesclagem_data.get("hide_subtitles"):
                actual_subtitles = []

            clip = mp.VideoFileClip(input_path)
            
            # 1. Lógica de Áudio
            final_audio = clip.audio
            if audio_settings:
                remove_audio = audio_settings.get('remove_audio', False)
                use_folder_audio = audio_settings.get('use_folder_audio', False)
                random_mode = audio_settings.get('random_mode', False)
                audio_folder = audio_settings.get('audio_folder', "")
                sync_duration = audio_settings.get('sync_duration', False)

                if use_folder_audio and audio_folder:
                    audio_path = self.audio_manager.get_next_audio(audio_folder, random_mode=random_mode)
                    if audio_path:
                        new_audio = mp.AudioFileClip(audio_path)
                        
                        if sync_duration:
                            # Sincronizar duração: corta o vídeo para o tamanho do áudio (se menor)
                            target_duration = min(clip.duration, new_audio.duration)
                            clip = clip.subclip(0, target_duration)
                            final_audio = new_audio.subclip(0, target_duration)
                        else:
                            # Ajustar duração do áudio se necessário (loop ou corte)
                            if new_audio.duration < clip.duration:
                                final_audio = mp.afx.audio_loop(new_audio, duration=clip.duration)
                            else:
                                final_audio = new_audio.set_duration(clip.duration)
                    elif remove_audio:
                        final_audio = None
                elif remove_audio:
                    final_audio = None

            # 2. Dimensões do vídeo interno
            v_w, v_h, _ = self.calculate_video_dimensions(border_enabled, border_size_preview)
            video_resized = clip.resize((v_w, v_h))
            
            # Preparar fundo se for blur
            background_clip = None
            if "blur" in (border_style or "").lower():
                background_clip = clip.resize((self.OUTPUT_WIDTH, self.OUTPUT_HEIGHT))

            def make_frame(t):
                frame = video_resized.get_frame(t)
                
                # Aplicar enhancement se ativado
                if enable_enhancement:
                    # Converter RGB para BGR (OpenCV format)
                    frame_bgr = cv2.cvtColor(frame.astype(np.uint8), cv2.COLOR_RGB2BGR)
                    # Aplicar GFPGAN
                    enhanced_bgr = video_enhancement.enhance_frame(frame_bgr)
                    # Converter de volta para RGB
                    frame = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)
                
                bg_frame = None
                if background_clip:
                    raw_bg = background_clip.get_frame(t)
                    bg_frame = self.apply_blur_opencv(raw_bg)
                
                return self.render_frame(
                    frame, 
                    actual_subtitles, 
                    border_enabled, 
                    border_size_preview, 
                    border_color, 
                    border_style,
                    emoji_scale,
                    background_frame=bg_frame,
                    watermark_data=watermark_data
                )
            
            fps = clip.fps if clip.fps else 30.0
            final_clip = VideoClip(make_frame=make_frame, duration=clip.duration)
            final_clip = final_clip.set_fps(fps)
            
            if final_audio:
                final_clip = final_clip.set_audio(final_audio)

            # 3. Adicionar Vídeos Sequenciais (Mesclagem e CTA)
            sequence = [final_clip]
            
            # 3.1 Vídeo de Mesclagem (Logo após o principal)
            if mesclagem_data and mesclagem_data.get("use_merge"):
                merge_path = mesclagem_data.get("merge_path")
                if merge_path and os.path.exists(merge_path):
                    merge_clip = mesclagem_back.preparar_video_extra(merge_path)
                    if merge_clip:
                        sequence.append(merge_clip)

            # 3.2 Vídeo de CTA (Final)
            if mesclagem_data and mesclagem_data.get("use_cta"):
                cta_path = mesclagem_data.get("cta_path")
                if cta_path and os.path.exists(cta_path):
                    cta_video_clip = mesclagem_back.preparar_video_extra(cta_path)
                    if cta_video_clip:
                        sequence.append(cta_video_clip)
            
            # Se houver mais de um vídeo, concatenar
            if len(sequence) > 1:
                final_clip = mp.concatenate_videoclips(sequence, method="compose") # compose ajuda com disparidade de FPS/Size
            
            # Garantir que o diretório de saída exista
            os.makedirs(output_folder, exist_ok=True)
            
            # Criar pasta temp física dentro da pasta de saída
            temp_dir = os.path.join(output_folder, "temp")
            os.makedirs(temp_dir, exist_ok=True)
            
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            
            # Gerar nome do arquivo com número da aba se fornecido
            if tab_number is not None:
                output_path = os.path.join(output_folder, f"{base_name}_aba{tab_number}.mp4")
            else:
                output_path = os.path.join(output_folder, f"{base_name}_render.mp4")
            
            final_clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                fps=fps,
                threads=threads,
                preset="medium",
                temp_audiofile=os.path.join(temp_dir, f"{base_name}_temp_audio.m4a"),
                remove_temp=True
            )
            
            clip.close()
            video_resized.close()
            if background_clip:
                background_clip.close()

            final_clip.close()

            # Tentar remover a pasta temp se estiver vazia
            try:
                if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                    os.rmdir(temp_dir)
            except:
                pass
            
            return True, output_path
        except Exception as e:
            return False, str(e)
