import os
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, VideoClip
import numpy as np
import tempfile
import re

class SimpleSubtitleEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Legendas Simples 9:16")
        self.root.geometry("1200x800")
        
        # Variáveis
        self.video_path = tk.StringVar()
        self.subtitle_text = tk.StringVar()
        self.font_family = tk.StringVar(value="Arial Black")
        self.font_size = tk.IntVar(value=40)
        self.font_color = tk.StringVar(value="#FFFFFF")
        self.border_color = tk.StringVar(value="#000000")
        self.bg_color = tk.StringVar(value="")
        self.subtitle_border_thickness = tk.IntVar(value=2)
        self.output_path = tk.StringVar(value=os.path.join(os.getcwd(), "output"))
        
        # Emojis
        self.emoji_folder = tk.StringVar()
        self.emoji_images = {}
        self.selected_emoji = None
        self.emoji_scale = tk.DoubleVar(value=1.0)
        
        # Legendas
        self.subtitles = []
        self.subtitle_counter = 0
        self.selected_subtitle_idx = None
        self.dragging_subtitle_idx = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        # Preview
        self.video_clip = None
        self.preview_image = None
        self._subtitle_bbox_cache = []
        
        # Configuração da UI
        self.setup_ui()
        
    def setup_ui(self):
        # Layout principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Coluna Esquerda (Preview)
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5)
        
        self.setup_preview_area(left_frame)
        
        # Coluna Direita (Controles)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Scroll para a coluna direita se necessário
        canvas = tk.Canvas(right_frame)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.setup_video_controls(scrollable_frame)
        self.setup_subtitle_editor(scrollable_frame)
        self.setup_subtitles_list(scrollable_frame)
        self.setup_output_controls(scrollable_frame)

    def setup_preview_area(self, parent):
        preview_frame = ttk.LabelFrame(parent, text="Preview 9:16")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas do preview (270x480 - proporção 9:16)
        self.preview_canvas = tk.Canvas(preview_frame, bg="black", width=270, height=480, relief=tk.RAISED, bd=2)
        self.preview_canvas.pack(padx=10, pady=10)
        
        # Bind eventos do mouse
        self.preview_canvas.bind("<Button-1>", self.on_preview_click)
        self.preview_canvas.bind("<B1-Motion>", self.on_preview_drag)
        self.preview_canvas.bind("<ButtonRelease-1>", self.on_preview_release)
        self.preview_canvas.bind("<Double-Button-1>", self.on_preview_double_click)
        
        # Botões de controle do preview
        controls_frame = ttk.Frame(preview_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="🔄 Atualizar", command=self.update_preview).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="🎯 Centralizar", command=self.center_selected_subtitle).pack(side=tk.LEFT, padx=2)

    def setup_video_controls(self, parent):
        frame = ttk.LabelFrame(parent, text="📹 Vídeo")
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(frame, text="📁 Selecionar Vídeo", command=self.select_video).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.video_path, width=40, state="readonly").pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    def setup_subtitle_editor(self, parent):
        """Configura o editor profissional de legendas"""
        subtitle_frame = ttk.LabelFrame(parent, text="✏️ Editor de Legendas")
        subtitle_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Grid para organizar os controles
        controls_frame = ttk.Frame(subtitle_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Primeira linha - Texto e Fonte
        ttk.Label(controls_frame, text="Texto:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        # Frame para o campo de texto com scroll
        text_frame = ttk.Frame(controls_frame)
        text_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # Text widget para múltiplas linhas
        self.text_widget = tk.Text(text_frame, width=40, height=3, wrap=tk.WORD)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar para o texto
        text_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.configure(yscrollcommand=text_scrollbar.set)
        
        ttk.Label(controls_frame, text="Fonte:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        font_options = ["Arial", "Arial Black", "Helvetica", "Times", "Courier", "Verdana", "Impact", "Comic Sans MS"]
        ttk.Combobox(controls_frame, textvariable=self.font_family, values=font_options, width=12).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(controls_frame, text="Tamanho:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        ttk.Spinbox(controls_frame, from_=8, to=200, textvariable=self.font_size, width=5).grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        
        # Segunda linha - Cores
        ttk.Label(controls_frame, text="Cor da Fonte:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        font_color_btn = ttk.Button(controls_frame, text="🎨 Escolher", command=lambda: self.choose_color(self.font_color))
        font_color_btn.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.font_color_label = tk.Label(controls_frame, bg=self.font_color.get(), width=3, relief=tk.RAISED)
        self.font_color_label.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(controls_frame, text="Cor da Borda:").grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
        border_color_btn = ttk.Button(controls_frame, text="🎨 Escolher", command=lambda: self.choose_color(self.border_color))
        border_color_btn.grid(row=1, column=4, padx=5, pady=5, sticky=tk.W)
        self.border_color_label = tk.Label(controls_frame, bg=self.border_color.get(), width=3, relief=tk.RAISED)
        self.border_color_label.grid(row=1, column=5, padx=5, pady=5, sticky=tk.W)
        
        # Terceira linha - Fundo e espessura da borda
        ttk.Label(controls_frame, text="Cor do Fundo:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        bg_color_btn = ttk.Button(controls_frame, text="🎨 Escolher", command=lambda: self.choose_color(self.bg_color, allow_none=True))
        bg_color_btn.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        self.bg_color_label = tk.Label(controls_frame, bg=self.bg_color.get() or self.root.cget("bg"), width=3, relief=tk.RAISED)
        self.bg_color_label.grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(controls_frame, text="Espessura Borda:").grid(row=2, column=3, padx=5, pady=5, sticky=tk.W)
        ttk.Spinbox(controls_frame, from_=1, to=10, textvariable=self.subtitle_border_thickness, width=5).grid(row=2, column=4, padx=5, pady=5, sticky=tk.W)
        
        # Quarta linha - Botão adicionar
        add_subtitle_btn = ttk.Button(controls_frame, text="➕ Adicionar Legenda", command=self.add_subtitle)
        add_subtitle_btn.grid(row=3, column=0, columnspan=6, padx=5, pady=10, sticky=tk.W+tk.E)
        
        # Sistema de emojis
        self.setup_emoji_system(subtitle_frame)

    def setup_emoji_system(self, parent):
        frame = ttk.LabelFrame(parent, text="😊 Emojis")
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        controls = ttk.Frame(frame)
        controls.pack(fill=tk.X, padx=5)
        
        ttk.Button(controls, text="📁 Pasta Emojis", command=self.select_emoji_folder).pack(side=tk.LEFT, padx=2)
        ttk.Entry(controls, textvariable=self.emoji_folder, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # Canvas de emojis
        self.emoji_canvas = tk.Canvas(frame, height=60, bg="white")
        self.emoji_canvas.pack(fill=tk.X, padx=5, pady=5)
        
        self.emoji_inner_frame = ttk.Frame(self.emoji_canvas)
        self.emoji_canvas.create_window((0, 0), window=self.emoji_inner_frame, anchor="nw")
        
        # Scrollbar emojis
        sb = ttk.Scrollbar(frame, orient="horizontal", command=self.emoji_canvas.xview)
        sb.pack(fill=tk.X)
        self.emoji_canvas.configure(xscrollcommand=sb.set)
        
        # Escala e Adicionar
        bottom = ttk.Frame(frame)
        bottom.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(bottom, text="Escala:").pack(side=tk.LEFT)
        ttk.Scale(bottom, from_=0.5, to=2.0, variable=self.emoji_scale, orient="horizontal").pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(bottom, text="Inserir Emoji", command=self.add_emoji_to_text).pack(side=tk.RIGHT)

    def setup_subtitles_list(self, parent):
        frame = ttk.LabelFrame(parent, text="📝 Lista de Legendas")
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.subtitles_listbox = tk.Listbox(frame, height=6)
        self.subtitles_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.subtitles_listbox.bind("<<ListboxSelect>>", self.on_subtitle_select)
        
        btns = ttk.Frame(frame)
        btns.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        ttk.Button(btns, text="🗑️", command=self.remove_selected_subtitle, width=3).pack(pady=2)
        ttk.Button(btns, text="✏️", command=self.edit_selected_subtitle, width=3).pack(pady=2)
        ttk.Button(btns, text="⬆️", command=self.move_subtitle_up, width=3).pack(pady=2)
        ttk.Button(btns, text="⬇️", command=self.move_subtitle_down, width=3).pack(pady=2)

    def setup_output_controls(self, parent):
        frame = ttk.LabelFrame(parent, text="💾 Exportar")
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Entry(frame, textvariable=self.output_path).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(frame, text="📁 Pasta Saída", command=self.choose_output_path).pack(fill=tk.X, padx=5)
        
        self.render_btn = ttk.Button(frame, text="🎬 Renderizar Vídeo", command=self.start_rendering)
        self.render_btn.pack(fill=tk.X, padx=5, pady=10)
        
        self.status_label = ttk.Label(frame, text="Aguardando...")
        self.status_label.pack(pady=5)

    # --- Lógica ---

    def select_video(self):
        path = filedialog.askopenfilename(filetypes=[("Vídeos", "*.mp4 *.avi *.mov *.mkv")])
        if path:
            self.video_path.set(path)
            self.open_video(path)

    def open_video(self, path):
        try:
            if self.video_clip:
                self.video_clip.close()
            self.video_clip = VideoFileClip(path)
            self.update_preview()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir vídeo: {e}")

    def choose_color(self, var, allow_none=False):
        color = colorchooser.askcolor(initialcolor=var.get())
        if color[1]:
            var.set(color[1])
            self.update_color_labels()
        elif allow_none:
            var.set("")
            self.update_color_labels()

    def update_color_labels(self):
        self.font_color_label.config(bg=self.font_color.get())
        self.border_color_label.config(bg=self.border_color.get())
        bg = self.bg_color.get()
        self.bg_color_label.config(bg=bg if bg else self.root.cget("bg"))

    def select_emoji_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.emoji_folder.set(folder)
            self.load_emoji_images()

    def load_emoji_images(self):
        folder = self.emoji_folder.get()
        if not os.path.exists(folder): return
        
        for widget in self.emoji_inner_frame.winfo_children():
            widget.destroy()
            
        self.emoji_images.clear()
        
        for f in os.listdir(folder):
            if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                path = os.path.join(folder, f)
                try:
                    orig_img = Image.open(path)
                    if orig_img.mode != 'RGBA':
                        orig_img = orig_img.convert('RGBA')
                    
                    # Thumbnail para a UI
                    thumb = orig_img.copy()
                    thumb.thumbnail((32, 32))
                    photo = ImageTk.PhotoImage(thumb)
                    
                    self.emoji_images[f] = {
                        'path': path, 
                        'photo': photo,
                        'original_image': orig_img
                    }
                    
                    btn = tk.Button(self.emoji_inner_frame, image=photo, command=lambda x=f: self.select_emoji(x))
                    btn.pack(side=tk.LEFT, padx=2)
                except: pass
        
        self.emoji_inner_frame.bind("<Configure>", lambda e: self.emoji_canvas.configure(scrollregion=self.emoji_canvas.bbox("all")))

    def select_emoji(self, filename):
        self.selected_emoji = filename
        messagebox.showinfo("Emoji", f"Selecionado: {filename}")

    def add_emoji_to_text(self):
        if self.selected_emoji:
            self.text_widget.insert(tk.INSERT, f"[EMOJI:{self.selected_emoji}]")

    def add_subtitle(self):
        text = self.text_widget.get("1.0", tk.END).strip()
        if not text: return
        
        self.subtitle_counter += 1
        sub = {
            "id": self.subtitle_counter,
            "text": text,
            "font": self.font_family.get(),
            "size": self.font_size.get(),
            "color": self.font_color.get(),
            "border": self.border_color.get(),
            "bg": self.bg_color.get(),
            "border_thickness": self.subtitle_border_thickness.get(),
            "x": 135, "y": 240 # Centro do preview 270x480
        }
        self.subtitles.append(sub)
        self.update_subtitles_listbox()
        self.update_preview()
        self.text_widget.delete("1.0", tk.END)

    def update_subtitles_listbox(self):
        self.subtitles_listbox.delete(0, tk.END)
        for sub in self.subtitles:
            self.subtitles_listbox.insert(tk.END, f"#{sub['id']}: {sub['text'][:30]}...")

    def on_subtitle_select(self, event):
        sel = self.subtitles_listbox.curselection()
        if sel:
            self.selected_subtitle_idx = sel[0]
            self.update_preview()

    def remove_selected_subtitle(self):
        if self.selected_subtitle_idx is not None:
            self.subtitles.pop(self.selected_subtitle_idx)
            self.selected_subtitle_idx = None
            self.update_subtitles_listbox()
            self.update_preview()

    def edit_selected_subtitle(self):
        """Edita a legenda selecionada"""
        if self.selected_subtitle_idx is None:
            messagebox.showwarning("Aviso", "Selecione uma legenda para editar.")
            return
            
        self.show_edit_subtitle_dialog()

    def show_edit_subtitle_dialog(self):
        """Mostra diálogo para editar legenda"""
        if self.selected_subtitle_idx is None:
            return
            
        subtitle = self.subtitles[self.selected_subtitle_idx]
        
        # Criar janela de edição
        edit_window = tk.Toplevel()
        edit_window.title(f"Editar Legenda #{subtitle['id']}")
        edit_window.geometry("500x450")
        edit_window.resizable(True, True)
        
        # Variáveis
        text_var = tk.StringVar(value=subtitle["text"])
        font_var = tk.StringVar(value=subtitle["font"])
        size_var = tk.IntVar(value=subtitle["size"])
        color_var = tk.StringVar(value=subtitle["color"])
        border_var = tk.StringVar(value=subtitle["border"])
        bg_var = tk.StringVar(value=subtitle["bg"])
        
        # Frame principal
        main_frame = tk.Frame(edit_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text=f"Editar Legenda #{subtitle['id']}", font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        fields_frame = tk.Frame(main_frame)
        fields_frame.pack(fill=tk.BOTH, expand=True)
        
        # Texto
        tk.Label(fields_frame, text="Texto:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        text_entry = tk.Entry(fields_frame, textvariable=text_var, font=("Arial", 10))
        text_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Fonte e Tamanho
        row2 = tk.Frame(fields_frame)
        row2.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(row2, text="Fonte:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        font_options = ["Arial", "Arial Black", "Helvetica", "Times", "Courier", "Verdana", "Impact", "Comic Sans MS"]
        ttk.Combobox(row2, textvariable=font_var, values=font_options, width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Label(row2, text="Tamanho:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(10, 0))
        tk.Spinbox(row2, from_=8, to=200, textvariable=size_var, width=5).pack(side=tk.LEFT, padx=5)
        
        # Cores
        def choose_color_dialog(var, label):
            color = colorchooser.askcolor(initialcolor=var.get() or "#FFFFFF")
            if color[1]:
                var.set(color[1])
                label.config(bg=color[1])
            elif var == bg_var:
                var.set("")
                label.config(bg=self.root.cget("bg"))

        # Cor Texto
        row3 = tk.Frame(fields_frame)
        row3.pack(fill=tk.X, pady=5)
        tk.Label(row3, text="Cor Texto:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        color_lbl = tk.Label(row3, bg=color_var.get(), width=3, relief=tk.RAISED)
        color_lbl.pack(side=tk.LEFT, padx=5)
        tk.Button(row3, text="🎨", command=lambda: choose_color_dialog(color_var, color_lbl)).pack(side=tk.LEFT)
        
        # Cor Borda
        row4 = tk.Frame(fields_frame)
        row4.pack(fill=tk.X, pady=5)
        tk.Label(row4, text="Cor Borda:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        border_lbl = tk.Label(row4, bg=border_var.get() or self.root.cget("bg"), width=3, relief=tk.RAISED)
        border_lbl.pack(side=tk.LEFT, padx=5)
        tk.Button(row4, text="🎨", command=lambda: choose_color_dialog(border_var, border_lbl)).pack(side=tk.LEFT)
        
        # Cor Fundo
        row5 = tk.Frame(fields_frame)
        row5.pack(fill=tk.X, pady=5)
        tk.Label(row5, text="Cor Fundo:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        bg_lbl = tk.Label(row5, bg=bg_var.get() or self.root.cget("bg"), width=3, relief=tk.RAISED)
        bg_lbl.pack(side=tk.LEFT, padx=5)
        tk.Button(row5, text="🎨", command=lambda: choose_color_dialog(bg_var, bg_lbl)).pack(side=tk.LEFT)
        
        # Botões
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        def save():
            subtitle["text"] = text_var.get()
            subtitle["font"] = font_var.get()
            subtitle["size"] = size_var.get()
            subtitle["color"] = color_var.get()
            subtitle["border"] = border_var.get()
            subtitle["bg"] = bg_var.get()
            self.update_subtitles_listbox()
            self.update_preview()
            edit_window.destroy()
            
        tk.Button(btn_frame, text="Salvar", command=save, bg="green", fg="white", width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancelar", command=edit_window.destroy, bg="red", fg="white", width=10).pack(side=tk.LEFT, padx=5)

    def move_subtitle_up(self):
        idx = self.selected_subtitle_idx
        if idx is not None and idx > 0:
            self.subtitles[idx], self.subtitles[idx-1] = self.subtitles[idx-1], self.subtitles[idx]
            self.selected_subtitle_idx -= 1
            self.update_subtitles_listbox()
            self.subtitles_listbox.selection_set(self.selected_subtitle_idx)
            self.update_preview()

    def move_subtitle_down(self):
        idx = self.selected_subtitle_idx
        if idx is not None and idx < len(self.subtitles) - 1:
            self.subtitles[idx], self.subtitles[idx+1] = self.subtitles[idx+1], self.subtitles[idx]
            self.selected_subtitle_idx += 1
            self.update_subtitles_listbox()
            self.subtitles_listbox.selection_set(self.selected_subtitle_idx)
            self.update_preview()

    def center_selected_subtitle(self):
        if self.selected_subtitle_idx is not None:
            self.subtitles[self.selected_subtitle_idx]["x"] = 135
            self.subtitles[self.selected_subtitle_idx]["y"] = 240
            self.update_preview()

    def update_preview(self):
        if not self.video_clip: return
        
        try:
            frame = self.video_clip.get_frame(0)
            img = Image.fromarray(frame).resize((270, 480))
            draw = ImageDraw.Draw(img)
            
            self._subtitle_bbox_cache = []
            
            for i, sub in enumerate(self.subtitles):
                # Fonte
                try:
                    font = ImageFont.truetype("arial.ttf", int(sub["size"] * 0.25)) # Escala para preview
                except:
                    font = ImageFont.load_default()
                
                # Desenha
                self.draw_text_with_emojis(draw, sub["text"], sub["x"], sub["y"], font, sub["color"], sub["border"], sub["bg"], 0.25, sub.get("border_thickness", self.subtitle_border_thickness.get()))
                
                # BBox para clique (aproximado)
                bbox = draw.textbbox((sub["x"], sub["y"]), sub["text"], font=font, anchor="mm")
                self._subtitle_bbox_cache.append(bbox)
                
                # Seleção
                if i == self.selected_subtitle_idx:
                    draw.rectangle(bbox, outline="yellow", width=2)
            
            self.preview_image = ImageTk.PhotoImage(img)
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(0, 0, anchor="nw", image=self.preview_image)
            
        except Exception as e:
            print(f"Erro preview: {e}")

    def draw_text_with_emojis(self, draw, text, x, y, font, color, border, bg, scale, border_thickness):
        """Desenha texto com emojis integrados e quebra de linha"""
        emoji_pattern = r'\[EMOJI:([^\]]+)\]'
        
        # Divide o texto em linhas
        lines = text.split('\n')
        line_height = font.size + int(2 * scale)
        
        # Calcula altura total para centralizar verticalmente
        total_height = len(lines) * line_height
        start_y = y - total_height // 2
        
        # Calcula a largura máxima entre todas as linhas para centralizar o bloco
        max_line_width = 0
        line_widths = []
        
        for line in lines:
            parts = re.split(emoji_pattern, line)
            line_width = 0
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Texto normal
                    if part:
                        bbox = draw.textbbox((0, 0), part, font=font)
                        line_width += bbox[2] - bbox[0]
                else:  # Emoji
                    emoji_filename = part
                    if emoji_filename in self.emoji_images:
                        emoji_size = int(font.size * self.emoji_scale.get())
                        line_width += emoji_size
            line_widths.append(line_width)
            max_line_width = max(max_line_width, line_width)
        
        # Calcula a posição inicial do bloco de texto (centralizado)
        block_start_x = x - max_line_width // 2
        
        # Desenha cada linha
        for line_idx, line in enumerate(lines):
            line_y = start_y + line_idx * line_height
            parts = re.split(emoji_pattern, line)
            
            # Posição inicial da linha (centralizada dentro do bloco)
            line_width = line_widths[line_idx]
            current_x = x - line_width // 2
            
            # Desenha fundo da linha se houver
            if bg:
                draw.rectangle([current_x - 5, line_y - font.size//2 - 2, 
                              current_x + line_width + 5, line_y + font.size//2 + 2], fill=bg)
            
            # Desenha cada parte da linha
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Texto normal
                    if part:
                        # Borda
                        if border:
                            thick = max(1, int(border_thickness * scale))
                            for dx in range(-thick, thick+1):
                                for dy in range(-thick, thick+1):
                                    if dx!=0 or dy!=0:
                                        draw.text((current_x+dx, line_y+dy), part, font=font, fill=border, anchor="lm")
                        
                        # Texto
                        draw.text((current_x, line_y), part, font=font, fill=color, anchor="lm")
                        
                        # Atualiza posição
                        bbox = draw.textbbox((0, 0), part, font=font)
                        current_x += bbox[2] - bbox[0]
                else:  # Emoji
                    emoji_filename = part
                    if emoji_filename in self.emoji_images:
                        emoji_size = int(font.size * self.emoji_scale.get())
                        
                        # Redimensiona a imagem do emoji
                        emoji_image = self.emoji_images[emoji_filename]['original_image'].copy()
                        emoji_image = emoji_image.resize((emoji_size, emoji_size), Image.Resampling.LANCZOS)
                        
                        # Cola o emoji na imagem principal
                        paste_x = int(current_x)
                        paste_y = int(line_y - emoji_size // 2)
                        
                        # Usa máscara para transparência
                        mask = emoji_image.split()[-1] if emoji_image.mode == 'RGBA' else None
                        draw._image.paste(emoji_image, (paste_x, paste_y), mask)
                        
                        # Atualiza posição
                        current_x += emoji_size

    # Eventos Mouse Preview
    def on_preview_click(self, event):
        x, y = event.x, event.y
        for i, bbox in enumerate(self._subtitle_bbox_cache):
            if bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
                self.dragging_subtitle_idx = i
                self.selected_subtitle_idx = i
                self.drag_offset_x = x - self.subtitles[i]["x"]
                self.drag_offset_y = y - self.subtitles[i]["y"]
                self.subtitles_listbox.selection_clear(0, tk.END)
                self.subtitles_listbox.selection_set(i)
                self.update_preview()
                return
        self.selected_subtitle_idx = None
        self.update_preview()

    def on_preview_drag(self, event):
        if self.dragging_subtitle_idx is not None:
            self.subtitles[self.dragging_subtitle_idx]["x"] = event.x - self.drag_offset_x
            self.subtitles[self.dragging_subtitle_idx]["y"] = event.y - self.drag_offset_y
            self.update_preview()

    def on_preview_release(self, event):
        self.dragging_subtitle_idx = None

    def on_preview_double_click(self, event):
        if self.selected_subtitle_idx is not None:
            self.edit_selected_subtitle()

    def choose_output_path(self):
        d = filedialog.askdirectory()
        if d: self.output_path.set(d)

    def start_rendering(self):
        if not self.video_path.get() or not self.subtitles:
            messagebox.showwarning("Aviso", "Vídeo ou legendas faltando!")
            return
            
        import threading
        threading.Thread(target=self.render_video, daemon=True).start()

    def render_video(self):
        try:
            self.status_label.config(text="Renderizando... Aguarde.")
            self.render_btn.config(state="disabled")
            
            clip = VideoFileClip(self.video_path.get())
            
            # Redimensiona para 1080x1920 (9:16)
            # Se for horizontal, corta ou preenche? Vamos assumir preenchimento/resize simples
            # Para manter proporção correta, ideal é crop. Aqui faremos resize direto para simplificar
            # ou melhor, resize mantendo aspect ratio e centralizando em fundo preto
            
            target_w, target_h = 1080, 1920
            
            def make_frame(t):
                frame = clip.get_frame(t)
                img = Image.fromarray(frame)
                
                # Resize mantendo aspect ratio
                ratio = min(target_w/img.width, target_h/img.height)
                new_w = int(img.width * ratio)
                new_h = int(img.height * ratio)
                img = img.resize((new_w, new_h))
                
                # Fundo preto
                final = Image.new("RGB", (target_w, target_h), "black")
                final.paste(img, ((target_w-new_w)//2, (target_h-new_h)//2))
                
                draw = ImageDraw.Draw(final)
                
                # Legendas
                scale = target_w / 270 # Escala do preview para final
                
                for sub in self.subtitles:
                    # Ajusta coordenadas
                    x = sub["x"] * scale
                    y = sub["y"] * scale
                    
                    # Fonte
                    try:
                        font = ImageFont.truetype("arial.ttf", int(sub["size"] * scale * 0.25)) # Ajuste empírico
                    except:
                        font = ImageFont.load_default()
                        
                    self.draw_text_with_emojis(draw, sub["text"], x, y, font, sub["color"], sub["border"], sub["bg"], scale * 0.25, sub.get("border_thickness", self.subtitle_border_thickness.get()))
                
                return np.array(final)
            
            final_clip = VideoClip(make_frame, duration=clip.duration)
            final_clip = final_clip.set_audio(clip.audio)
            final_clip = final_clip.set_fps(clip.fps)
            
            out_name = os.path.join(self.output_path.get(), f"video_legendado_{self.subtitle_counter}.mp4")
            final_clip.write_videofile(out_name, codec="libx264", audio_codec="aac")
            
            self.status_label.config(text="Concluído!")
            messagebox.showinfo("Sucesso", f"Vídeo salvo em:\n{out_name}")
            
        except Exception as e:
            self.status_label.config(text="Erro!")
            messagebox.showerror("Erro Render", str(e))
        finally:
            self.render_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleSubtitleEditor(root)
    root.mainloop()
