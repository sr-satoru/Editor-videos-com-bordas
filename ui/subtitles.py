import os
import tkinter as tk
from tkinter import ttk, messagebox

from PIL import Image, ImageTk, ImageDraw

# Módulos de Backend
from modules.subiitels.renderizador_legendas import RenderizadorLegendas
from modules.subiitels.calculo_posicao import canvas_para_video
from modules.video_editor import VideoEditor

# Componentes de UI
from ui.dialogo_edicao import DialogoEdicaoLegenda
from ui.componente_emojis import ComponenteEmojis
from ui.componente_lista_legendas import ComponenteListaLegendas
from ui.componente_estilo_legenda import ComponenteEstiloLegenda

class Subtitles(ttk.Frame):
    def __init__(self, parent, subtitle_manager, emoji_manager, video_controls, video_borders):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        
        self.subtitle_manager = subtitle_manager
        self.emoji_manager = emoji_manager
        self.video_controls = video_controls
        self.video_borders = video_borders
        
        self.renderer = RenderizadorLegendas(emoji_manager)
        self.editor = VideoEditor()
        
        # Estado de Drag-and-Drop
        self.selected_subtitle_idx = None
        self.dragging_subtitle_idx = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.subtitle_bbox_cache = []
        
        # Estado de Drag-and-Drop para Marca d'Água
        self.dragging_watermark = False
        self.selected_watermark = False
        self.watermark_bbox_cache = None
        
        self.last_preview_params = None
        self.cached_preview_base = None
        
        self.setup_ui()
        self.setup_preview_bindings()

    def setup_ui(self):
        # 1. Editor de Texto e Estilo
        editor_container = ttk.Frame(self)
        editor_container.pack(fill="x", padx=10, pady=5)
        
        # Campo de Texto
        text_frame = ttk.LabelFrame(editor_container, text="✏️ Texto da Legenda")
        text_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.text_widget = tk.Text(text_frame, width=30, height=5, wrap="word")
        self.text_widget.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        text_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_widget.yview)
        text_scrollbar.pack(side="right", fill="y")
        self.text_widget.configure(yscrollcommand=text_scrollbar.set)
        
        # Componente de Estilo
        self.comp_estilo = ComponenteEstiloLegenda(editor_container, callbacks={'on_change': self.update_preview})
        self.comp_estilo.pack(side="right", fill="y")
        
        # Botões de Ação Rápida
        btn_row = ttk.Frame(self)
        btn_row.pack(fill="x", padx=10, pady=5)
        ttk.Button(btn_row, text="➕ Adicionar Legenda", command=self.add_subtitle).pack(side="left", fill="x", expand=True)

        # 2. Componente de Emojis
        self.comp_emojis = ComponenteEmojis(self, self.emoji_manager, callback_inserir=self.inserir_tag_emoji)
        self.comp_emojis.pack(fill="x", padx=10, pady=5)

        # 3. Componente de Lista
        self.comp_lista = ComponenteListaLegendas(self, self.subtitle_manager, callbacks={
            'on_select': self.on_list_select,
            'on_remove': self.remove_subtitle,
            'on_edit': self.edit_subtitle,
            'on_move': self.move_subtitle
        })
        self.comp_lista.pack(fill="x", padx=10, pady=5)

    def setup_preview_bindings(self):
        canvas = self.video_controls.video_selector.preview_canvas
        canvas.bind("<Button-1>", self.on_preview_click)
        canvas.bind("<B1-Motion>", self.on_preview_drag)
        canvas.bind("<ButtonRelease-1>", self.on_preview_release)
        canvas.bind("<Double-Button-1>", self.on_preview_double_click)

    def inserir_tag_emoji(self, tag):
        self.text_widget.insert(tk.INSERT, tag)

    def add_subtitle(self):
        text = self.text_widget.get("1.0", "end-1c").strip()
        if not text: return
        
        estilo = self.comp_estilo.get_estilo()
        self.subtitle_manager.add_subtitle(
            text=text,
            font=estilo['font'],
            size=estilo['size'],
            color=estilo['color'],
            border_color=estilo['border'],
            bg_color=estilo['bg'],
            border_thickness=estilo['border_thickness'],
            x=135, y=400
        )
        self.text_widget.delete("1.0", "end")
        self.comp_lista.refresh()
        self.update_preview()

    def on_list_select(self, event):
        self.selected_subtitle_idx = self.comp_lista.get_selection()
        self.update_preview()

    def remove_subtitle(self):
        idx = self.comp_lista.get_selection()
        if idx is not None:
            self.subtitle_manager.remove_subtitle(idx)
            self.selected_subtitle_idx = None
            self.comp_lista.refresh()
            self.update_preview()

    def edit_subtitle(self):
        idx = self.comp_lista.get_selection()
        if idx is None:
            messagebox.showwarning("Aviso", "Selecione uma legenda para editar.")
            return
        DialogoEdicaoLegenda(self, idx, self.subtitle_manager, self.on_dialog_save)

    def on_dialog_save(self):
        self.comp_lista.refresh()
        self.update_preview()

    def move_subtitle(self, direction):
        idx = self.comp_lista.get_selection()
        if idx is not None:
            if self.subtitle_manager.move_subtitle(idx, direction):
                new_idx = idx + direction
                self.comp_lista.refresh()
                self.comp_lista.set_selection(new_idx)
                self.selected_subtitle_idx = new_idx
                self.update_preview()

    def on_preview_double_click(self, event):
        if self.selected_subtitle_idx is not None:
            self.edit_subtitle()

    # --- Lógica de Preview e Drag (Mantida aqui por ser o orquestrador do Canvas) ---
    def update_preview(self):
        video_path = self.video_controls.video_selector.current_video_path
        if not video_path: return

        style = self.video_borders.get_effective_style()
        border_color = self.video_borders.border_color
        subtitles = self.subtitle_manager.get_subtitles()
        border_size_preview = self.video_borders.border_size_var.get()
        
        # Invalida o cache se o estilo ou cor mudar
        current_params = (video_path, style, border_color, border_size_preview)
        
        canvas = self.video_controls.video_selector.preview_canvas
        preview_w, preview_h = canvas.winfo_width(), canvas.winfo_height()
        if preview_w < 10: preview_w, preview_h = 360, 640

        if not self.cached_preview_base or self.last_preview_params != current_params:
            base_frame = self.editor.generate_base_preview(video_path, style, border_color, border_size_preview=border_size_preview)
            if base_frame is not None:
                img = Image.fromarray(base_frame)
                img.thumbnail((preview_w, preview_h), Image.Resampling.LANCZOS)
                self.cached_preview_base = img
                self.last_preview_params = current_params
                
                img_w, img_h = img.size
                img_x, img_y = (preview_w - img_w) // 2, (preview_h - img_h) // 2
                self.preview_img_geometry = (img_x, img_y, img_w, img_h)
                
                # CORREÇÃO CRÍTICA: Quando não há bordas, o vídeo final é renderizado em 1080x1920
                # e usa scale_factor = 1080/360 = 3.0. O preview DEVE usar o mesmo scale_factor
                # para que as posições coincidam!
                style_lower = style.lower()
                border_enabled_check = "moldura" in style_lower or "black" in style_lower or "white" in style_lower or "blur" in style_lower
                
                if border_enabled_check:
                    # Com bordas: usa a largura da imagem do preview
                    self.preview_scale_factor = img_w / 360.0
                else:
                    # Sem bordas: usa o mesmo scale_factor do vídeo final (1080/360 = 3.0)
                    # ajustado para o tamanho do preview (img_w/1080 * 3.0 = img_w/360)
                    # que é exatamente img_w / 360.0, MAS precisamos garantir que seja
                    # proporcional ao output final
                    self.preview_scale_factor = 3.0 * (img_w / 1080.0)
            else: return

        if self.cached_preview_base:
            img = self.cached_preview_base.copy()
            draw = ImageDraw.Draw(img)
            self.subtitle_bbox_cache = []
            img_x, img_y, _, _ = self.preview_img_geometry
            scale = self.preview_scale_factor
            
            style_lower = style.lower()
            border_enabled = "moldura" in style_lower or "black" in style_lower or "white" in style_lower or "blur" in style_lower
            
            if border_enabled:
                # Usar as mesmas proporções do VideoRenderer
                # VIDEO_WIDTH_RATIO = 0.78, VIDEO_HEIGHT_RATIO = 0.70
                # No preview, a base é 360.0
                v_w_preview = 360.0 * 0.78
                v_h_preview = 640.0 * 0.70
                
                off_x_preview = (360.0 - v_w_preview) / 2
                off_y_preview = (640.0 - v_h_preview) / 2
                
                offset_x = off_x_preview * scale
                offset_y = off_y_preview * scale
            else:
                offset_x = 0
                offset_y = 0
            
            for idx, sub in enumerate(subtitles):
                self.renderer.draw_subtitle(draw, sub, scale_factor=scale, emoji_scale=self.comp_emojis.emoji_scale.get(), offset_x=offset_x, offset_y=offset_y)
                bbox = self.renderer.get_subtitle_bbox(sub, scale_factor=scale, emoji_scale=self.comp_emojis.emoji_scale.get(), offset_x=offset_x, offset_y=offset_y)
                
                if idx == self.selected_subtitle_idx or idx == self.dragging_subtitle_idx:
                    draw.rectangle(bbox, outline="yellow", width=2)
                
                canvas_bbox = (bbox[0] + img_x, bbox[1] + img_y, bbox[2] + img_x, bbox[3] + img_y)
                self.subtitle_bbox_cache.append(canvas_bbox)

            # --- Desenhar Marca d'Água em Texto ---
            self.watermark_bbox_cache = None
            if hasattr(self, 'watermark_ui') and self.watermark_ui:
                watermark_data = self.watermark_ui.get_state()
                if watermark_data.get("add_text_mark"):
                    from modules.editar_com_legendas import VideoRenderer
                    v_renderer = VideoRenderer(self.emoji_manager)
                    v_renderer._draw_watermark(draw, watermark_data, scale, offset_x, offset_y)
                    
                    # Cache do BBox para interação
                    bbox = v_renderer.get_watermark_bbox(watermark_data, scale, offset_x, offset_y)
                    if bbox:
                        if self.selected_watermark or self.dragging_watermark:
                            draw.rectangle(bbox, outline="cyan", width=2)
                        
                        # Ajustar para coordenadas do Canvas
                        self.watermark_bbox_cache = (bbox[0] + img_x, bbox[1] + img_y, bbox[2] + img_x, bbox[3] + img_y)

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
                sub = self.subtitle_manager.get_subtitles()[i]
                scale = self.preview_scale_factor
                style = self.video_borders.get_effective_style()
                style_lower = style.lower()
                border_enabled = "moldura" in style_lower or "black" in style_lower or "white" in style_lower or "blur" in style_lower
                
                if border_enabled:
                    v_w_preview = 360.0 * 0.78
                    v_h_preview = 640.0 * 0.70
                    border_offset_x = (360.0 - v_w_preview) / 2
                    border_offset_y = (640.0 - v_h_preview) / 2
                else:
                    border_offset_x = 0
                    border_offset_y = 0
                
                click_video_x, click_video_y = canvas_para_video(x, y, self.preview_img_geometry, scale)
                self.drag_offset_x = click_video_x - (sub["x"] + border_offset_x)
                self.drag_offset_y = click_video_y - (sub["y"] + border_offset_y)
                
                self.comp_lista.set_selection(i)
                self.selected_watermark = False
                self.update_preview()
                return
        
        # Se não clicou em legenda, verificar marca d'água
        if self.watermark_bbox_cache:
            bbox = self.watermark_bbox_cache
            if bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
                self.dragging_watermark = True
                self.selected_watermark = True
                self.selected_subtitle_idx = None
                
                watermark_data = self.watermark_ui.get_state()
                scale = self.preview_scale_factor
                style = self.video_borders.get_effective_style()
                style_lower = style.lower()
                border_enabled = "moldura" in style_lower or "black" in style_lower or "white" in style_lower or "blur" in style_lower
                
                if border_enabled:
                    v_w_preview = 360.0 * 0.78
                    v_h_preview = 640.0 * 0.70
                    border_offset_x = (360.0 - v_w_preview) / 2
                    border_offset_y = (640.0 - v_h_preview) / 2
                else:
                    border_offset_x = 0
                    border_offset_y = 0
                
                click_video_x, click_video_y = canvas_para_video(x, y, self.preview_img_geometry, scale)
                self.drag_offset_x = click_video_x - (watermark_data["x"] + border_offset_x)
                self.drag_offset_y = click_video_y - (watermark_data["y"] + border_offset_y)
                
                self.update_preview()
                return

        self.selected_subtitle_idx = None
        self.selected_watermark = False
        self.update_preview()

    def on_preview_drag(self, event):
        if self.dragging_subtitle_idx is not None:
            scale = self.preview_scale_factor
            style = self.video_borders.get_effective_style()
            style_lower = style.lower()
            border_enabled = "moldura" in style_lower or "black" in style_lower or "white" in style_lower or "blur" in style_lower
            
            if border_enabled:
                v_w_preview = 360.0 * 0.78
                v_h_preview = 640.0 * 0.70
                border_offset_x = (360.0 - v_w_preview) / 2
                border_offset_y = (640.0 - v_h_preview) / 2
            else:
                border_offset_x = 0
                border_offset_y = 0
            
            new_render_x, new_render_y = canvas_para_video(event.x, event.y, self.preview_img_geometry, scale)
            new_video_x = new_render_x - self.drag_offset_x - border_offset_x
            new_video_y = new_render_y - self.drag_offset_y - border_offset_y
            
            self.subtitle_manager.update_subtitle(self.dragging_subtitle_idx, x=int(new_video_x), y=int(new_video_y))
            self.update_preview()
        elif self.dragging_watermark:
            scale = self.preview_scale_factor
            style = self.video_borders.get_effective_style()
            style_lower = style.lower()
            border_enabled = "moldura" in style_lower or "black" in style_lower or "white" in style_lower or "blur" in style_lower
            
            if border_enabled:
                v_w_preview = 360.0 * 0.78
                v_h_preview = 640.0 * 0.70
                border_offset_x = (360.0 - v_w_preview) / 2
                border_offset_y = (640.0 - v_h_preview) / 2
            else:
                border_offset_x = 0
                border_offset_y = 0
            
            new_render_x, new_render_y = canvas_para_video(event.x, event.y, self.preview_img_geometry, scale)
            new_video_x = new_render_x - self.drag_offset_x - border_offset_x
            new_video_y = new_render_y - self.drag_offset_y - border_offset_y
            
            self.watermark_ui.update_position(int(new_video_x), int(new_video_y))

    def on_preview_release(self, event):
        self.dragging_subtitle_idx = None
        self.dragging_watermark = False
        self.update_preview()
    def get_state(self):
        return {
            "subtitles": self.subtitle_manager.get_subtitles(),
            "emojis": self.comp_emojis.get_state(),
            "estilo": self.comp_estilo.get_state()
        }

    def set_state(self, state):
        # Limpar legendas atuais
        self.subtitle_manager.clear()
        
        # Carregar novas legendas
        for sub in state.get("subtitles", []):
            self.subtitle_manager.add_subtitle(
                text=sub['text'],
                font=sub['font'],
                size=sub['size'],
                color=sub['color'],
                border_color=sub['border'],
                bg_color=sub['bg'],
                border_thickness=sub['border_thickness'],
                x=sub['x'],
                y=sub['y']
            )
        
        self.comp_emojis.set_state(state.get("emojis", {}))
        self.comp_estilo.set_state(state.get("estilo", {}))
        
        self.comp_lista.refresh()
        self.update_preview()
