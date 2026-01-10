import json
import os
import re
from PIL import Image, ImageDraw, ImageFont

class SubtitleManager:
    def __init__(self):
        self.subtitles = []
        self.counter = 0

    def add_subtitle(self, text, font="Arial Black", size=40, color="#FFFFFF", border_color="#000000", bg_color="", x=540, y=1600, border_thickness=2):
        self.counter += 1
        subtitle = {
            "id": self.counter,
            "text": text,
            "font": font,
            "size": size,
            "color": color,
            "border": border_color,
            "bg": bg_color,
            "border_thickness": border_thickness,
            "x": x,
            "y": y
        }
        self.subtitles.append(subtitle)
        return subtitle

    def get_subtitles(self):
        return self.subtitles

    def remove_subtitle(self, index):
        if 0 <= index < len(self.subtitles):
            return self.subtitles.pop(index)
        return None

    def update_subtitle(self, index, **kwargs):
        if 0 <= index < len(self.subtitles):
            self.subtitles[index].update(kwargs)
            return self.subtitles[index]
        return None

    def move_subtitle(self, index, direction):
        """direction: -1 for up, 1 for down"""
        new_index = index + direction
        if 0 <= new_index < len(self.subtitles):
            self.subtitles[index], self.subtitles[new_index] = self.subtitles[new_index], self.subtitles[index]
            return True
        return False

    def clear(self):
        self.subtitles = []
        self.counter = 0

    def save_to_file(self, filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.subtitles, f, indent=4)

    def load_from_file(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                self.subtitles = json.load(f)
                if self.subtitles:
                    self.counter = max(s['id'] for s in self.subtitles)
                else:
                    self.counter = 0

class EmojiManager:
    def __init__(self):
        self.emojis = {}
        self.folder = None

    def load_emojis(self, folder):
        self.folder = folder
        self.emojis = {}
        if not os.path.exists(folder): return
        for f in os.listdir(folder):
            if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                try:
                    img = Image.open(os.path.join(folder, f))
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    self.emojis[f] = img
                except: pass

    def get_emoji(self, name):
        return self.emojis.get(name)

    def get_emoji_list(self):
        return sorted(list(self.emojis.keys()))

class SubtitleRenderer:
    def __init__(self, emoji_manager):
        self.emoji_manager = emoji_manager

    def draw_subtitle(self, draw, sub, scale_factor=1.0, emoji_scale=1.0):
        text = sub["text"]
        x = sub["x"] * scale_factor
        y = sub["y"] * scale_factor
        color = sub["color"]
        border = sub["border"]
        bg = sub["bg"]
        border_thickness = sub.get("border_thickness", 2)
        
        # Fonte
        try:
            # Tentar carregar fonte do sistema
            font_path = "arial.ttf" 
            font = ImageFont.truetype(font_path, int(sub["size"] * scale_factor))
        except:
            font = ImageFont.load_default()

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
                    if self.emoji_manager.get_emoji(part):
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
                        if border and border != "":
                            t = max(1, int(border_thickness * scale_factor))
                            for dx in range(-t, t+1):
                                for dy in range(-t, t+1):
                                    if dx!=0 or dy!=0: draw.text((curr_x+dx, curr_y+dy), part, font=font, fill=border, anchor="lm")
                        draw.text((curr_x, curr_y), part, font=font, fill=color, anchor="lm")
                        bbox = draw.textbbox((0, 0), part, font=font)
                        curr_x += bbox[2] - bbox[0]
                else:
                    emoji_img = self.emoji_manager.get_emoji(part)
                    if emoji_img:
                        e_size = int(font.size * emoji_scale)
                        e_img = emoji_img.resize((e_size, e_size), Image.Resampling.LANCZOS)
                        draw._image.paste(e_img, (int(curr_x), int(curr_y - e_size//2)), e_img if e_img.mode == 'RGBA' else None)
                        curr_x += e_size

    def get_subtitle_bbox(self, sub, scale_factor=1.0, emoji_scale=1.0):
        text = sub["text"]
        x = sub["x"] * scale_factor
        y = sub["y"] * scale_factor
        
        try:
            font = ImageFont.truetype("arial.ttf", int(sub["size"] * scale_factor))
        except:
            font = ImageFont.load_default()
            
        emoji_pattern = r'\[EMOJI:([^\]]+)\]'
        lines = text.split('\n')
        line_height = font.size + int(5 * scale_factor)
        max_w = 0
        for line in lines:
            parts = re.split(emoji_pattern, line)
            w = 0
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    if part:
                        dummy = Image.new("RGB", (1, 1))
                        d = ImageDraw.Draw(dummy)
                        bbox = d.textbbox((0, 0), part, font=font)
                        w += bbox[2] - bbox[0]
                else:
                    if self.emoji_manager.get_emoji(part):
                        w += int(font.size * emoji_scale)
            max_w = max(max_w, w)
            
        h = len(lines) * line_height
        return (x - max_w//2, y - h//2, x + max_w//2, y + h//2)
