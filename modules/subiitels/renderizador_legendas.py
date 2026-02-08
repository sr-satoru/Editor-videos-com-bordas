import re
import platform
import os
from PIL import Image, ImageDraw, ImageFont

class RenderizadorLegendas:
    def __init__(self, gerenciador_emojis):
        self.gerenciador_emojis = gerenciador_emojis
        self.cache = {}

    def clear_cache(self):
        self.cache = {}

    def _get_cache_key(self, sub, scale_factor, emoji_scale):
        return (
            sub.get("text"), sub.get("font"), sub.get("size"),
            sub.get("color"), sub.get("border"), sub.get("bg"),
            sub.get("border_thickness"), scale_factor, emoji_scale
        )

    def _render_to_cache(self, sub, scale_factor, emoji_scale):
        key = self._get_cache_key(sub, scale_factor, emoji_scale)
        if key in self.cache:
            return self.cache[key]

        # Calcular dimensões necessárias para a imagem da legenda
        font = self._get_font(sub["font"], int(sub["size"] * scale_factor))
        text = sub["text"]
        emoji_pattern = r'\[EMOJI:([^\]]+)\]'
        lines = text.split('\n')
        line_height = font.size + int(1 * scale_factor)
        
        # Primeiro passo: Medir tudo para saber o tamanho da imagem temporária
        max_w = 0
        for line in lines:
            parts = re.split(emoji_pattern, line)
            w = 0
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    if part:
                        dummy = Image.new("RGBA", (1, 1))
                        d = ImageDraw.Draw(dummy)
                        bbox = d.textbbox((0, 0), part, font=font)
                        w += bbox[2] - bbox[0]
                else:
                    if self.gerenciador_emojis.get_emoji(part):
                        w += int(font.size * emoji_scale)
            max_w = max(max_w, w)

        total_height = len(lines) * line_height
        
        # Adicionar margem para bordas
        border_thickness = sub.get("border_thickness", 2)
        margin = int(border_thickness * scale_factor) + 5
        canvas_w = max_w + margin * 2
        canvas_h = total_height + margin * 2
        
        # Criar a imagem transparente
        sub_img = Image.new("RGBA", (int(canvas_w), int(canvas_h)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(sub_img)
        
        # Renderizar na imagem transparente
        curr_y = margin + line_height // 2
        for i, line in enumerate(lines):
            line_w = 0
            # Primeiro calcula largura da linha para centralizar no canvas se quiser, 
            # mas vamos manter alinhado à esquerda no 'nosso' canvas por simplicidade
            # e o draw_subtitle cuida do offset.
            
            # Aqui vamos centralizar a linha dentro do canvas_w para facilitar o paste centralizado
            # mas o original alinha à esquerda dentro do bloco. Vamos seguir o original.
            curr_x = margin
            
            if sub.get("bg"):
                # Medir linha para o fundo
                parts = re.split(emoji_pattern, line)
                lw = 0
                for k, p in enumerate(parts):
                    if k % 2 == 0:
                        if p:
                            bbox = draw.textbbox((0, 0), p, font=font)
                            lw += bbox[2] - bbox[0]
                    else:
                        if self.gerenciador_emojis.get_emoji(p): lw += int(font.size * emoji_scale)
                draw.rectangle([curr_x-5, curr_y-font.size//2, curr_x+lw+5, curr_y+font.size//2], fill=sub["bg"])

            parts = re.split(emoji_pattern, line)
            for j, part in enumerate(parts):
                if j % 2 == 0:
                    if part:
                        border = sub.get("border")
                        if border and border != "" and border_thickness > 0:
                            t = max(1, int(border_thickness * scale_factor))
                            for dx in range(-t, t+1):
                                for dy in range(-t, t+1):
                                    if dx!=0 or dy!=0: draw.text((curr_x+dx, curr_y+dy), part, font=font, fill=border, anchor="lm")
                        draw.text((curr_x, curr_y), part, font=font, fill=sub["color"], anchor="lm")
                        bbox = draw.textbbox((0, 0), part, font=font)
                        curr_x += bbox[2] - bbox[0]
                else:
                    emoji_img = self.gerenciador_emojis.get_emoji(part)
                    if emoji_img:
                        e_size = int(font.size * emoji_scale)
                        e_img = emoji_img.resize((e_size, e_size), Image.Resampling.LANCZOS)
                        sub_img.paste(e_img, (int(curr_x), int(curr_y - e_size//2)), e_img if e_img.mode == 'RGBA' else None)
                        curr_x += e_size
            curr_y += line_height

        self.cache[key] = (sub_img, margin, max_w, total_height)
        return self.cache[key]

    def draw_subtitle(self, draw, sub, scale_factor=1.0, emoji_scale=1.0, offset_x=0, offset_y=0):
        # Usar o cachê para obter a imagem da legenda
        sub_img, margin, max_w, total_height = self._render_to_cache(sub, scale_factor, emoji_scale)
        
        # Calcular posição de colagem (centralizado conforme sub["x"], sub["y"])
        # Originalmente: block_start_x = x - max_line_width // 2
        # start_y = y - total_height // 2
        
        x = sub["x"] * scale_factor + offset_x
        y = sub["y"] * scale_factor + offset_y
        
        paste_x = int(x - max_w // 2 - margin)
        paste_y = int(y - total_height // 2 - margin)
        
        # Colar na imagem principal (o draw._image é a referência para o PIL.Image original)
        draw._image.paste(sub_img, (paste_x, paste_y), sub_img)

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

    def get_subtitle_bbox(self, sub, scale_factor=1.0, emoji_scale=1.0, offset_x=0, offset_y=0):
        # Usar o cachê para obter as dimensões rapidamente
        _, _, max_w, total_height = self._render_to_cache(sub, scale_factor, emoji_scale)
        
        x = sub["x"] * scale_factor + offset_x
        y = sub["y"] * scale_factor + offset_y
        
        return (x - max_w//2, y - total_height//2, x + max_w//2, y + total_height//2)

