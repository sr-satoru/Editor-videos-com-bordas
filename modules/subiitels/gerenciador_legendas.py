import json
import os

class GerenciadorLegendas:
    def __init__(self):
        self.subtitles = []
        self.counter = 0

    def add_subtitle(self, text, font="Arial Black", size=18, color="#FFFFFF", border_color="#000000", bg_color="", x=135, y=400, border_thickness=2):
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
        """direction: -1 para cima, 1 para baixo"""
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
