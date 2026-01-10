import os
import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import re
from modules.subtitle_manager import SubtitleRenderer
from modules.video_editor import VideoEditor

class Subtitles(ttk.Frame):
    def __init__(self, parent, subtitle_manager, emoji_manager, video_controls, video_borders):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        
        self.subtitle_manager = subtitle_manager
        self.emoji_manager = emoji_manager
        self.video_controls = video_controls
        self.video_borders = video_borders
        self.renderer = SubtitleRenderer(emoji_manager)
        self.editor = VideoEditor()
        
        # Variáveis de estado
        self.font_family = tk.StringVar(value="Arial Black")
        self.font_size = tk.IntVar(value=40)
        self.font_color = tk.StringVar(value="#FFFFFF")
        self.border_color = tk.StringVar(value="#000000")
        self.bg_color = tk.StringVar(value="")
        self.border_thickness = tk.IntVar(value=2)
        self.emoji_scale = tk.DoubleVar(value=1.0)
        
        self.selected_subtitle_idx = None
        self.dragging_subtitle_idx = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.subtitle_bbox_cache = []
        self.last_preview_params = None
        self.cached_preview_base = None
        
        self.setup_ui()
        self.setup_preview_bindings()

    def setup_ui(self):
        # 1. Editor de Legendas
        editor_frame = ttk.LabelFrame(self, text="✏️ Editor de Legendas")
        editor_frame.pack(fill="x", padx=10, pady=5)
        
        controls_frame = ttk.Frame(editor_frame)
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        # Row 0: Texto, Fonte, Tamanho
        ttk.Label(controls_frame, text="Texto:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        text_frame = ttk.Frame(controls_frame)
        text_frame.grid(row=0, column=1, padx=5, pady=5, sticky="we")
        self.text_widget = tk.Text(text_frame, width=40, height=3, wrap="word")
        self.text_widget.pack(side="left", fill="both", expand=True)
        text_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_widget.yview)
        text_scrollbar.pack(side="right", fill="y")
        self.text_widget.configure(yscrollcommand=text_scrollbar.set)
        
        ttk.Label(controls_frame, text="Fonte:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        font_options = ["Arial", "Arial Black", "Helvetica", "Impact", "Verdana", "Impact", "Comic Sans MS"]
        self.font_combo = ttk.Combobox(controls_frame, textvariable=self.font_family, values=font_options, width=15)
        self.font_combo.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        ttk.Label(controls_frame, text="Tamanho:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        ttk.Spinbox(controls_frame, from_=10, to=200, textvariable=self.font_size, width=5).grid(row=0, column=5, padx=5, pady=5, sticky="w")
        
        # Row 1: Cor Fonte, Cor Borda
        ttk.Label(controls_frame, text="Cor da Fonte:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.font_color_btn = ttk.Button(controls_frame, text="🎨 Escolher", command=self.choose_font_color)
        self.font_color_btn.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.font_color_indicator = tk.Label(controls_frame, width=3, bg=self.font_color.get(), relief="raised")
        self.font_color_indicator.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        
        ttk.Label(controls_frame, text="Cor da Borda:").grid(row=1, column=3, padx=5, pady=5, sticky="w")
        self.border_color_btn = ttk.Button(controls_frame, text="🎨 Escolher", command=self.choose_border_color)
        self.border_color_btn.grid(row=1, column=4, padx=5, pady=5, sticky="w")
        self.border_color_indicator = tk.Label(controls_frame, width=3, bg=self.border_color.get(), relief="raised")
        self.border_color_indicator.grid(row=1, column=5, padx=5, pady=5, sticky="w")
        
        # Row 2: Cor Fundo, Espessura Borda
        ttk.Label(controls_frame, text="Cor do Fundo:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.bg_color_btn = ttk.Button(controls_frame, text="🎨 Escolher", command=self.choose_bg_color)
        self.bg_color_btn.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.bg_color_indicator = tk.Label(controls_frame, width=3, bg=self.bg_color.get() or "#f0f0f0", relief="raised")
        self.bg_color_indicator.grid(row=2, column=2, padx=5, pady=5, sticky="w")
        
        ttk.Label(controls_frame, text="Espessura Borda:").grid(row=2, column=3, padx=5, pady=5, sticky="w")
        ttk.Spinbox(controls_frame, from_=0, to=10, textvariable=self.border_thickness, width=5).grid(row=2, column=4, padx=5, pady=5, sticky="w")
        
        # Row 3: Botões Adicionar e Centralizar
        btn_row = ttk.Frame(controls_frame)
        btn_row.grid(row=3, column=0, columnspan=6, padx=5, pady=10, sticky="we")
        ttk.Button(btn_row, text="➕ Adicionar Legenda", command=self.add_subtitle).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(btn_row, text="🎯 Centralizar", command=self.center_selected_subtitle).pack(side="left", fill="x", expand=True)

        # 2. Emojis
        self.setup_emoji_system(editor_frame)

        # 3. Lista de Legendas
        self.setup_subtitles_list(self)

    def setup_emoji_system(self, parent):
        frame = ttk.LabelFrame(parent, text="😊 Emojis")
        frame.pack(fill="x", padx=10, pady=5)
        
        emoji_top = ttk.Frame(frame)
        emoji_top.pack(fill="x", padx=10, pady=5)
        ttk.Button(emoji_top, text="📁 Pasta Emojis", command=self.select_emoji_folder).pack(side="left")
        self.emoji_folder_label = ttk.Label(emoji_top, text="Nenhuma pasta selecionada", width=40)
        self.emoji_folder_label.pack(side="left", padx=5)
        
        # Barra de Emojis
        self.emoji_canvas = tk.Canvas(frame, height=60, bg="white")
        self.emoji_canvas.pack(fill="x", padx=10, pady=5)
        self.emoji_inner_frame = ttk.Frame(self.emoji_canvas)
        self.emoji_canvas.create_window((0, 0), window=self.emoji_inner_frame, anchor="nw")
        
        emoji_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.emoji_canvas.xview)
        emoji_scroll.pack(fill="x", padx=10)
        self.emoji_canvas.configure(xscrollcommand=emoji_scroll.set)
        
        emoji_bottom = ttk.Frame(frame)
        emoji_bottom.pack(fill="x", padx=10, pady=5)
        ttk.Label(emoji_bottom, text="Escala:").pack(side="left")
        ttk.Scale(emoji_bottom, from_=0.5, to=2.0, variable=self.emoji_scale, orient="horizontal").pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(emoji_bottom, text="Inserir Emoji", command=self.insert_emoji_tag).pack(side="right")

    def setup_subtitles_list(self, parent):
        list_frame = ttk.LabelFrame(parent, text="📝 Lista de Legendas")
        list_frame.pack(fill="x", padx=10, pady=5)
        
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill="x", padx=10, pady=5)
        
        self.subtitles_listbox = tk.Listbox(list_container, height=6)
        self.subtitles_listbox.pack(side="left", fill="x", expand=True)
        self.subtitles_listbox.bind("<<ListboxSelect>>", self.on_list_select)
        
        btn_list_frame = ttk.Frame(list_container)
        btn_list_frame.pack(side="right", padx=5)
        
        ttk.Button(btn_list_frame, text="🗑️", width=3, command=self.remove_subtitle).pack(pady=2)
        ttk.Button(btn_list_frame, text="✏️", width=3, command=self.edit_subtitle).pack(pady=2)
        ttk.Button(btn_list_frame, text="⬆️", width=3, command=lambda: self.move_subtitle(-1)).pack(pady=2)
        ttk.Button(btn_list_frame, text="⬇️", width=3, command=lambda: self.move_subtitle(1)).pack(pady=2)

    def setup_preview_bindings(self):
        canvas = self.video_controls.video_selector.preview_canvas
        canvas.bind("<Button-1>", self.on_preview_click)
        canvas.bind("<B1-Motion>", self.on_preview_drag)
        canvas.bind("<ButtonRelease-1>", self.on_preview_release)
        canvas.bind("<Double-Button-1>", self.on_preview_double_click)

    def on_preview_double_click(self, event):
        if self.selected_subtitle_idx is not None:
            self.edit_subtitle()

    def center_selected_subtitle(self):
        if self.selected_subtitle_idx is not None:
            self.subtitle_manager.update_subtitle(self.selected_subtitle_idx, x=540, y=960)
            self.update_preview()

    # --- Lógica de Cores ---
    def choose_font_color(self):
        color = colorchooser.askcolor(initialcolor=self.font_color.get())[1]
        if color:
            self.font_color.set(color)
            self.font_color_indicator.config(bg=color)

    def choose_border_color(self):
        color = colorchooser.askcolor(initialcolor=self.border_color.get())[1]
        if color:
            self.border_color.set(color)
            self.border_color_indicator.config(bg=color)

    def choose_bg_color(self):
        color = colorchooser.askcolor(initialcolor=self.bg_color.get() or "#ffffff")[1]
        if color:
            self.bg_color.set(color)
            self.bg_color_indicator.config(bg=color)
        else:
            self.bg_color.set("")
            self.bg_color_indicator.config(bg="#f0f0f0")

    # --- Lógica de Emojis ---
    def select_emoji_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.emoji_folder_label.config(text=os.path.basename(folder))
            self.load_emojis(folder)

    def load_emojis(self, folder):
        for widget in self.emoji_inner_frame.winfo_children():
            widget.destroy()
        
        self.emoji_manager.load_emojis(folder)
        emojis = self.emoji_manager.get_emoji_list()
        
        for emoji_name in emojis:
            img_data = self.emoji_manager.get_emoji(emoji_name)
            if img_data:
                thumb = img_data.copy()
                thumb.thumbnail((32, 32))
                photo = ImageTk.PhotoImage(thumb)
                
                btn = tk.Button(self.emoji_inner_frame, image=photo, command=lambda n=emoji_name: self.set_selected_emoji(n))
                btn.image = photo # Referência
                btn.pack(side="left", padx=2)
        
        self.emoji_inner_frame.update_idletasks()
        self.emoji_canvas.configure(scrollregion=self.emoji_canvas.bbox("all"))

    def set_selected_emoji(self, name):
        self.selected_emoji_name = name

    def insert_emoji_tag(self):
        if hasattr(self, 'selected_emoji_name'):
            self.text_widget.insert(tk.INSERT, f"[EMOJI:{self.selected_emoji_name}]")

    # --- Lógica de Legendas ---
    def add_subtitle(self):
        text = self.text_widget.get("1.0", "end-1c").strip()
        if not text: return
        
        self.subtitle_manager.add_subtitle(
            text=text,
            font=self.font_family.get(),
            size=self.font_size.get(),
            color=self.font_color.get(),
            border_color=self.border_color.get(),
            bg_color=self.bg_color.get(),
            border_thickness=self.border_thickness.get(),
            x=540, y=1600 # Centro inferior padrão (1080p)
        )
        self.text_widget.delete("1.0", "end")
        self.refresh_list()
        self.update_preview()

    def refresh_list(self):
        self.subtitles_listbox.delete(0, tk.END)
        for sub in self.subtitle_manager.get_subtitles():
            self.subtitles_listbox.insert(tk.END, f"#{sub['id']}: {sub['text'][:30]}...")

    def on_list_select(self, event):
        sel = self.subtitles_listbox.curselection()
        if sel:
            self.selected_subtitle_idx = sel[0]
            self.update_preview()

    def remove_subtitle(self):
        if self.selected_subtitle_idx is not None:
            self.subtitle_manager.remove_subtitle(self.selected_subtitle_idx)
            self.selected_subtitle_idx = None
            self.refresh_list()
            self.update_preview()

    def edit_subtitle(self):
        if self.selected_subtitle_idx is None:
            messagebox.showwarning("Aviso", "Selecione uma legenda para editar.")
            return
        self.show_edit_subtitle_dialog()

    def show_edit_subtitle_dialog(self):
        if self.selected_subtitle_idx is None: return
        sub = self.subtitle_manager.get_subtitles()[self.selected_subtitle_idx]
        
        edit_window = tk.Toplevel(self)
        edit_window.title(f"Editar Legenda #{sub['id']}")
        edit_window.geometry("500x450")
        
        # Variáveis locais para o diálogo
        text_var = tk.StringVar(value=sub["text"])
        font_var = tk.StringVar(value=sub["font"])
        size_var = tk.IntVar(value=sub["size"])
        color_var = tk.StringVar(value=sub["color"])
        border_var = tk.StringVar(value=sub["border"])
        bg_var = tk.StringVar(value=sub["bg"])
        thick_var = tk.IntVar(value=sub["border_thickness"])
        
        main_frame = tk.Frame(edit_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text=f"Editar Legenda #{sub['id']}", font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        fields_frame = tk.Frame(main_frame)
        fields_frame.pack(fill="both", expand=True)
        
        # Texto
        tk.Label(fields_frame, text="Texto:", font=("Arial", 10, "bold")).pack(anchor="w")
        text_entry = tk.Entry(fields_frame, textvariable=text_var, font=("Arial", 10))
        text_entry.pack(fill="x", pady=(0, 10))
        
        # Fonte e Tamanho
        row2 = tk.Frame(fields_frame)
        row2.pack(fill="x", pady=(0, 10))
        tk.Label(row2, text="Fonte:", font=("Arial", 10, "bold")).pack(side="left")
        font_options = ["Arial", "Arial Black", "Helvetica", "Impact", "Verdana", "Comic Sans MS"]
        ttk.Combobox(row2, textvariable=font_var, values=font_options, width=15).pack(side="left", padx=5)
        tk.Label(row2, text="Tamanho:", font=("Arial", 10, "bold")).pack(side="left", padx=(10, 0))
        tk.Spinbox(row2, from_=10, to=200, textvariable=size_var, width=5).pack(side="left", padx=5)
        
        def choose_color_dialog(var, label, allow_none=False):
            color = colorchooser.askcolor(initialcolor=var.get() or "#FFFFFF")[1]
            if color:
                var.set(color)
                label.config(bg=color)
            elif allow_none:
                var.set("")
                label.config(bg="#f0f0f0")

        # Cores
        row3 = tk.Frame(fields_frame)
        row3.pack(fill="x", pady=5)
        tk.Label(row3, text="Cor Texto:", font=("Arial", 10, "bold")).pack(side="left")
        color_lbl = tk.Label(row3, bg=color_var.get(), width=3, relief="raised")
        color_lbl.pack(side="left", padx=5)
        tk.Button(row3, text="🎨", command=lambda: choose_color_dialog(color_var, color_lbl)).pack(side="left")
        
        row4 = tk.Frame(fields_frame)
        row4.pack(fill="x", pady=5)
        tk.Label(row4, text="Cor Borda:", font=("Arial", 10, "bold")).pack(side="left")
        border_lbl = tk.Label(row4, bg=border_var.get() or "#000000", width=3, relief="raised")
        border_lbl.pack(side="left", padx=5)
        tk.Button(row4, text="🎨", command=lambda: choose_color_dialog(border_var, border_lbl)).pack(side="left")
        
        row5 = tk.Frame(fields_frame)
        row5.pack(fill="x", pady=5)
        tk.Label(row5, text="Cor Fundo:", font=("Arial", 10, "bold")).pack(side="left")
        bg_lbl = tk.Label(row5, bg=bg_var.get() or "#f0f0f0", width=3, relief="raised")
        bg_lbl.pack(side="left", padx=5)
        tk.Button(row5, text="🎨", command=lambda: choose_color_dialog(bg_var, bg_lbl, True)).pack(side="left")

        row6 = tk.Frame(fields_frame)
        row6.pack(fill="x", pady=5)
        tk.Label(row6, text="Espessura Borda:", font=("Arial", 10, "bold")).pack(side="left")
        tk.Spinbox(row6, from_=0, to=10, textvariable=thick_var, width=5).pack(side="left", padx=5)
        
        def save():
            self.subtitle_manager.update_subtitle(
                self.selected_subtitle_idx,
                text=text_var.get(),
                font=font_var.get(),
                size=size_var.get(),
                color=color_var.get(),
                border_color=border_var.get(),
                bg_color=bg_var.get(),
                border_thickness=thick_var.get()
            )
            self.refresh_list()
            self.update_preview()
            edit_window.destroy()
            
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(20, 0))
        tk.Button(btn_frame, text="Salvar", command=save, bg="green", fg="white", width=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancelar", command=edit_window.destroy, bg="red", fg="white", width=10).pack(side="left", padx=5)

    def move_subtitle(self, direction):
        if self.selected_subtitle_idx is not None:
            if self.subtitle_manager.move_subtitle(self.selected_subtitle_idx, direction):
                self.selected_subtitle_idx += direction
                self.refresh_list()
                self.subtitles_listbox.selection_set(self.selected_subtitle_idx)
                self.update_preview()

    # --- Lógica de Preview e Drag ---
    def update_preview(self):
        video_path = self.video_controls.video_selector.current_video_path
        if not video_path: return

        style = self.video_borders.get_effective_style()
        border_color = self.video_borders.border_color
        subtitles = self.subtitle_manager.get_subtitles()
        current_params = (video_path, style, border_color)
        
        canvas = self.video_controls.video_selector.preview_canvas
        preview_w = canvas.winfo_width()
        preview_h = canvas.winfo_height()
        if preview_w < 10: preview_w, preview_h = 360, 640

        if not self.cached_preview_base or self.last_preview_params != current_params:
            base_frame = self.editor.generate_base_preview(video_path, style, border_color)
            if base_frame is not None:
                img = Image.fromarray(base_frame)
                img.thumbnail((preview_w, preview_h), Image.Resampling.LANCZOS)
                self.cached_preview_base = img
                self.last_preview_params = current_params
                
                # Geometria
                img_w, img_h = img.size
                img_x = (preview_w - img_w) // 2
                img_y = (preview_h - img_h) // 2
                self.preview_img_geometry = (img_x, img_y, img_w, img_h)
                self.preview_scale_factor = img_w / 1080.0
            else: return

        if self.cached_preview_base:
            img = self.cached_preview_base.copy()
            draw = ImageDraw.Draw(img)
            
            self.subtitle_bbox_cache = []
            img_x, img_y, img_w, img_h = self.preview_img_geometry
            scale = self.preview_scale_factor
            
            for idx, sub in enumerate(subtitles):
                # Desenhar usando o renderer do módulo
                self.renderer.draw_subtitle(draw, sub, scale_factor=scale, emoji_scale=self.emoji_scale.get())
                
                # BBox para hit detection usando o renderer do módulo
                bbox = self.renderer.get_subtitle_bbox(sub, scale_factor=scale, emoji_scale=self.emoji_scale.get())
                
                # Desenhar retângulo de seleção no PIL se selecionado
                if idx == self.selected_subtitle_idx or idx == self.dragging_subtitle_idx:
                    draw.rectangle(bbox, outline="yellow", width=2)
                
                # Cache da BBox relativa ao CANVAS para clique
                canvas_bbox = (
                    bbox[0] + img_x, bbox[1] + img_y,
                    bbox[2] + img_x, bbox[3] + img_y
                )
                self.subtitle_bbox_cache.append(canvas_bbox)

            self.preview_image_tk = ImageTk.PhotoImage(img)
            canvas.delete("all")
            canvas.create_image(preview_w//2, preview_h//2, image=self.preview_image_tk, anchor="center")
            canvas.image = self.preview_image_tk

    def on_preview_click(self, event):
        x, y = event.x, event.y
        for i in range(len(self.subtitle_bbox_cache)-1, -1, -1):
            bbox = self.subtitle_bbox_cache[i]
            if bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
                self.dragging_subtitle_idx = i
                self.selected_subtitle_idx = i
                
                # Offset relativo à posição X,Y da legenda (em coordenadas 1080p)
                sub = self.subtitle_manager.get_subtitles()[i]
                img_x, img_y, _, _ = self.preview_img_geometry
                scale = self.preview_scale_factor
                
                # Converter clique do canvas para coordenadas 1080p
                click_video_x = (x - img_x) / scale
                click_video_y = (y - img_y) / scale
                
                self.drag_offset_x = click_video_x - sub["x"]
                self.drag_offset_y = click_video_y - sub["y"]
                
                self.subtitles_listbox.selection_clear(0, tk.END)
                self.subtitles_listbox.selection_set(i)
                self.update_preview()
                return
        self.selected_subtitle_idx = None
        self.update_preview()

    def on_preview_drag(self, event):
        if self.dragging_subtitle_idx is not None:
            img_x, img_y, _, _ = self.preview_img_geometry
            scale = self.preview_scale_factor
            
            # Nova posição no vídeo = (Posição no canvas - offset) convertida para escala
            new_video_x = (event.x - img_x) / scale - self.drag_offset_x
            new_video_y = (event.y - img_y) / scale - self.drag_offset_y
            
            self.subtitle_manager.update_subtitle(self.dragging_subtitle_idx, x=int(new_video_x), y=int(new_video_y))
            self.update_preview()

    def on_preview_release(self, event):
        self.dragging_subtitle_idx = None
        self.update_preview()
