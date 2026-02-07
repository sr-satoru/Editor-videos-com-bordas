# ui/preview.py
import tkinter as tk
from modules.video_selector import VideoSelector

class Preview:
    def __init__(self, parent):
        preview_group = tk.LabelFrame(parent, text="Preview 9:16")
        preview_group.pack(fill="x", pady=10)

        self.canvas = tk.Canvas(preview_group, width=360, height=640, bg="black")
        self.canvas.ignore_theme = True
        self.canvas.pack(padx=10, pady=10)
