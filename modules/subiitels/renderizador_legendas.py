import re
import platform
import os
from PIL import Image, ImageDraw, ImageFont

class RenderizadorLegendas:
    def __init__(self, gerenciador_emojis):
        self.gerenciador_emojis = gerenciador_emojis

    def _get_font(self, font_family, size):
        """Carrega a fonte correta dependendo do Sistema Operacional"""
        system = platform.system()
        
        try:
            if system == "Windows":
                # Mapeamento para Windows
                font_map = {
                    "Arial Black": "ariblk.ttf",
                    "Arial": "arial.ttf",
                    "Helvetica": "arial.ttf",
                    "Times": "times.ttf",
                    "Courier": "cour.ttf",
                    "Verdana": "verdana.ttf",
                    "Impact": "impact.ttf",
                    "Comic Sans MS": "comic.ttf"
                }
                font_name = font_map.get(font_family, "arial.ttf")
                font_path = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', font_name)
            else:
                # Mapeamento para Linux (Liberation/DejaVu)
                font_map = {
                    "Arial Black": "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                    "Arial": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                    "Helvetica": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                    "Times": "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
                    "Courier": "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
                    "Verdana": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "Impact": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    "Comic Sans MS": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
                }
                font_path = font_map.get(font_family, "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf")
            
            return ImageFont.truetype(font_path, size)
        except:
            return ImageFont.load_default()

    def draw_subtitle(self, draw, sub, scale_factor=1.0, emoji_scale=1.0, offset_x=0, offset_y=0):
        text = sub["text"]
        x = sub["x"] * scale_factor + offset_x
        y = sub["y"] * scale_factor + offset_y
        color = sub["color"]
        border = sub["border"]
        bg = sub["bg"]
        border_thickness = sub.get("border_thickness", 2)
        
        # Fonte
        font = self._get_font(sub["font"], int(sub["size"] * scale_factor))

        emoji_pattern = r'\[EMOJI:([^\]]+)\]'
        lines = text.split('\n')
        line_height = font.size + int(5 * scale_factor)
        total_height = len(lines) * line_height
        start_y = y - total_height // 2
        
        line_widths = []
        for line in lines:
            parts = re.split(emoji_pattern, line)
            w = 0
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    if part:
                        bbox = draw.textbbox((0, 0), part, font=font)
                        w += bbox[2] - bbox[0]
                else:
                    if self.gerenciador_emojis.get_emoji(part):
                        w += int(font.size * emoji_scale)
            line_widths.append(w)

        for i, line in enumerate(lines):
            curr_y = start_y + i * line_height
            curr_x = x - line_widths[i] // 2
            
            if bg and bg != "":
                draw.rectangle([curr_x-5, curr_y-font.size//2, curr_x+line_widths[i]+5, curr_y+font.size//2], fill=bg)
            
            parts = re.split(emoji_pattern, line)
            for j, part in enumerate(parts):
                if j % 2 == 0:
                    if part:
                        if border and border != "" and border_thickness > 0:
                            t = max(1, int(border_thickness * scale_factor))
                            for dx in range(-t, t+1):
                                for dy in range(-t, t+1):
                                    if dx!=0 or dy!=0: draw.text((curr_x+dx, curr_y+dy), part, font=font, fill=border, anchor="lm")
                        draw.text((curr_x, curr_y), part, font=font, fill=color, anchor="lm")
                        bbox = draw.textbbox((0, 0), part, font=font)
                        curr_x += bbox[2] - bbox[0]
                else:
                    emoji_img = self.gerenciador_emojis.get_emoji(part)
                    if emoji_img:
                        e_size = int(font.size * emoji_scale)
                        e_img = emoji_img.resize((e_size, e_size), Image.Resampling.LANCZOS)
                        draw._image.paste(e_img, (int(curr_x), int(curr_y - e_size//2)), e_img if e_img.mode == 'RGBA' else None)
                        curr_x += e_size

    def get_subtitle_bbox(self, sub, scale_factor=1.0, emoji_scale=1.0, offset_x=0, offset_y=0):
        text = sub["text"]
        x = sub["x"] * scale_factor + offset_x
        y = sub["y"] * scale_factor + offset_y
        
        font = self._get_font(sub["font"], int(sub["size"] * scale_factor))
            
        emoji_pattern = r'\[EMOJI:([^\]]+)\]'
        lines = text.split('\n')
        line_height = font.size + int(5 * scale_factor)
        total_height = len(lines) * line_height
        start_y = y - total_height // 2
        
        max_w = 0
        min_y = float('inf')
        max_y = float('-inf')
        
        for i, line in enumerate(lines):
            curr_y = start_y + i * line_height
            parts = re.split(emoji_pattern, line)
            w = 0
            for j, part in enumerate(parts):
                if j % 2 == 0:
                    if part:
                        # Usar uma imagem temporária pequena para medir o texto
                        dummy = Image.new("RGB", (1, 1))
                        d = ImageDraw.Draw(dummy)
                        bbox = d.textbbox((0, 0), part, font=font)
                        w += bbox[2] - bbox[0]
                else:
                    if self.gerenciador_emojis.get_emoji(part):
                        w += int(font.size * emoji_scale)
            max_w = max(max_w, w)
            
            # Calcular limites verticais baseado no anchor "lm" (left-middle)
            # O texto é centralizado verticalmente em curr_y
            text_top = curr_y - font.size // 2
            text_bottom = curr_y + font.size // 2
            min_y = min(min_y, text_top)
            max_y = max(max_y, text_bottom)
            
        return (x - max_w//2, min_y, x + max_w//2, max_y)

