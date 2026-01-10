# ui/main_ui.py
import tkinter as tk
from tkinter import ttk
from ui.preview import Preview
from ui.video_controls import VideoControls
from ui.borders import VideoBorders
from ui.subtitles import Subtitles
from ui.audio import AudioSettings
from ui.output import OutputVideo
from ui.footer import Footer

from modules.subtitle_manager import SubtitleManager, EmojiManager

class EditorUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Editor Profissional de Vídeo 9:16")
        self.geometry("900x800")
        self.processar_pasta_var = tk.BooleanVar()

        self.build_ui()

    def build_ui(self):
        # ---------- NOTEBOOK ----------
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # ---------- CRIAR ABA INICIAL ----------
        self.add_new_tab("Aba 1")

        # ---------- FOOTER ----------
        Footer(self, add_tab_callback=lambda: self.add_new_tab(f"Aba {len(self.notebook.tabs())+1}"))

    def add_new_tab(self, tab_name):
        """Adiciona uma nova aba e popula com os módulos"""
        new_tab = ttk.Frame(self.notebook)
        self.notebook.add(new_tab, text=tab_name)

        # ================== SCROLL DA ABA ==================
        canvas = tk.Canvas(new_tab, highlightthickness=0)
        scrollbar = ttk.Scrollbar(new_tab, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ===== SCROLL COM MOUSE =====
        def _on_mousewheel(event):
            if event.num == 4:           # Linux scroll up
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:         # Linux scroll down
                canvas.yview_scroll(1, "units")
            else:                        # Windows / macOS
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<Enter>", lambda e: (
            canvas.bind_all("<MouseWheel>", _on_mousewheel),
            canvas.bind_all("<Button-4>", _on_mousewheel),
            canvas.bind_all("<Button-5>", _on_mousewheel)
        ))
        canvas.bind("<Leave>", lambda e: (
            canvas.unbind_all("<MouseWheel>"),
            canvas.unbind_all("<Button-4>"),
            canvas.unbind_all("<Button-5>")
        ))

        # ================== MANAGERS ==================
        subtitle_manager = SubtitleManager()
        emoji_manager = EmojiManager()

        # ================== MÓDULOS ==================
        preview = Preview(scroll_frame)  # Apenas o canvas do preview
        video_controls = VideoControls(scroll_frame, self.processar_pasta_var, preview.canvas)  # Botão seleciona vídeo
        video_borders = VideoBorders(scroll_frame, video_controls, subtitle_manager, emoji_manager)
        
        subtitles_ui = Subtitles(scroll_frame, subtitle_manager, emoji_manager, video_controls, video_borders)
        
        AudioSettings(scroll_frame)
        OutputVideo(scroll_frame, video_controls, video_borders, subtitle_manager, emoji_manager)


if __name__ == "__main__":
    EditorUI().mainloop()
