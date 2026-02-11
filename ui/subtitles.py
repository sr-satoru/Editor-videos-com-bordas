import os
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np

from PIL import Image, ImageTk, ImageDraw

# Módulos de Backend
from modules.subiitels.renderizador_legendas import RenderizadorLegendas
from modules.subiitels.calculo_posicao import canvas_para_video
from modules.video_editor import VideoEditor

# Componentes de UI
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
        
        from modules.editar_com_legendas import VideoRenderer
        self.v_renderer = VideoRenderer(self.emoji_manager)
        
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
        
        # Estado de Drag-and-Drop para Logo
        self.dragging_logo = False
        self.resizing_logo = False
        self.selected_logo = False
        self.logo_bbox_cache = None
        self.logo_resize_handle_bbox = None
        self.initial_logo_scale = 1.0
        self.initial_mouse_y = 0
        
        self.last_preview_params = None
        self.cached_preview_base = None
        
        # Estado para Redimensionamento da Moldura de Vídeo (Estilo Canva)
        self.resizing_moldura = False
        self.selected_moldura = False
        self.moldura_handles = {} # {id_canto: bbox}
        self.active_handle = None 
        
        # Estado para Modo de Edição vs. Criação
        self.editing_mode = False
        self.temporary_subtitle = None  # Legenda temporária para preview em tempo real
        
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
        self.comp_estilo = ComponenteEstiloLegenda(editor_container, callbacks={
            'on_change': self.on_style_change,
            'get_current_time': lambda: self.video_controls.video_selector.current_time
        })
        self.comp_estilo.pack(side="right", fill="y")
        
        # Evento de digitação em tempo real
        self.text_widget.bind("<KeyRelease>", self.on_text_typing)
        
        # Botões de Ação Rápida
        btn_row = ttk.Frame(self)
        btn_row.pack(fill="x", padx=10, pady=5)
        self.add_btn = ttk.Button(btn_row, text="➞ Adicionar Legenda", command=self.add_subtitle)
        self.add_btn.pack(side="left", fill="x", expand=True)

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
        
        # Registrar callback de renderização ao vivo
        self.video_controls.video_selector.post_process_callback = self.render_live_preview

    def on_style_change(self):
        """Atualiza os metadados da legenda selecionada em tempo real (fonte, cor, tempo)"""
        # Verificar se comp_estilo já foi inicializado (evita erro durante setup_ui)
        if not hasattr(self, 'comp_estilo'):
            return
            
        estilo = self.comp_estilo.get_estilo()
        
        if self.editing_mode and self.selected_subtitle_idx is not None:
            # Modo de edição: atualiza a legenda existente
            self.subtitle_manager.update_subtitle(self.selected_subtitle_idx, **estilo)
            self.comp_lista.refresh()
            self.update_preview()
        elif self.temporary_subtitle:
            # Modo de criação: atualiza o preview temporário
            self.temporary_subtitle.update({
                'font': estilo['font'],
                'size': estilo['size'],
                'color': estilo['color'],
                'border': estilo['border'],
                'bg': estilo['bg'],
                'border_thickness': estilo['border_thickness'],
                'start_time': estilo.get('start_time', 0.0),
                'end_time': estilo.get('end_time', 10.0)
            })
            self.update_preview()
        else:
            # Se nada selecionado, apenas atualiza o preview (ex: preview sem vídeo)
            self.update_preview()

    def on_text_typing(self, event):
        """Atualiza o texto da legenda selecionada em tempo real (se em modo de edição) ou cria preview temporário"""
        new_text = self.text_widget.get("1.0", "end-1c")
        
        if self.editing_mode and self.selected_subtitle_idx is not None:
            # Modo de edição: atualiza a legenda existente
            self.subtitle_manager.update_subtitle(self.selected_subtitle_idx, text=new_text)
            self.comp_lista.refresh()
            self.update_preview()
        else:
            # Modo de criação: cria preview temporário
            if new_text.strip():
                estilo = self.comp_estilo.get_estilo()
                self.temporary_subtitle = {
                    "text": new_text,
                    "font": estilo['font'],
                    "size": estilo['size'],
                    "color": estilo['color'],
                    "border": estilo['border'],
                    "bg": estilo['bg'],
                    "border_thickness": estilo['border_thickness'],
                    "x": 135,
                    "y": 400,
                    "start_time": estilo.get('start_time', 0.0),
                    "end_time": estilo.get('end_time', 10.0)
                }
            else:
                self.temporary_subtitle = None
            self.update_preview()

    def inserir_tag_emoji(self, tag):
        self.text_widget.insert(tk.INSERT, tag)
    
    def update_button_text(self):
        """Atualiza o texto do botão com base no modo de edição"""
        if self.editing_mode and self.selected_subtitle_idx is not None:
            self.add_btn.config(text="✔️ Salvar Alterações")
        else:
            self.add_btn.config(text="➞ Adicionar Legenda")


    def add_subtitle(self):
        text = self.text_widget.get("1.0", "end-1c").strip()
        if not text: return
        
        estilo = self.comp_estilo.get_estilo()
        
        if self.editing_mode and self.selected_subtitle_idx is not None:
            # Modo de edição: salvar alterações na legenda existente
            self.subtitle_manager.update_subtitle(
                self.selected_subtitle_idx,
                text=text,
                font=estilo['font'],
                size=estilo['size'],
                color=estilo['color'],
                border=estilo['border'],
                bg=estilo['bg'],
                border_thickness=estilo['border_thickness'],
                start_time=estilo.get('start_time', 0.0),
                end_time=estilo.get('end_time', 10.0)
            )
        else:
            # Modo de criação: adicionar nova legenda
            self.subtitle_manager.add_subtitle(
                text=text,
                font=estilo['font'],
                size=estilo['size'],
                color=estilo['color'],
                border_color=estilo['border'],
                bg_color=estilo['bg'],
                border_thickness=estilo['border_thickness'],
                x=135, y=400,
                start_time=estilo.get('start_time', 0.0),
                end_time=estilo.get('end_time', 10.0)
            )
        
        # Limpar e resetar estado
        self.text_widget.delete("1.0", "end")
        self.temporary_subtitle = None
        self.editing_mode = False
        self.selected_subtitle_idx = None
        self.comp_lista.set_selection(None)
        self.comp_lista.refresh()
        self.update_button_text()
        self.update_preview()

    def on_list_select(self, event):
        idx = self.comp_lista.get_selection()
        if idx is not None:
            self.selected_subtitle_idx = idx
            sub = self.subtitle_manager.get_subtitles()[idx]
            # Sincronizar UI de estilo com a legenda selecionada
            self.comp_estilo.set_state({
                'font': sub['font'],
                'size': sub['size'],
                'color': sub['color'],
                'border': sub['border'],
                'bg': sub['bg'],
                'border_thickness': sub['border_thickness'],
                'start_time': sub.get('start_time', 0.0),
                'end_time': sub.get('end_time', 10.0)
            })
            # NÃO carregar texto no widget para evitar edição acidental
            # O texto só será carregado ao dar duplo clique ou clicar em editar
            self.editing_mode = False
            self.temporary_subtitle = None
            
        self.update_preview()
    
    def clear_selection(self):
        """Limpa a seleção e reseta o modo de edição"""
        self.selected_subtitle_idx = None
        self.editing_mode = False
        self.temporary_subtitle = None
        self.comp_lista.set_selection(None)
        self.text_widget.delete("1.0", "end")
        self.update_button_text()
        self.update_preview()


    def remove_subtitle(self):
        idx = self.comp_lista.get_selection()
        if idx is not None:
            self.subtitle_manager.remove_subtitle(idx)
            self.selected_subtitle_idx = None
            self.editing_mode = False
            self.temporary_subtitle = None
            # Limpar seleção da listbox
            self.comp_lista.set_selection(None)
            # Limpar campo de texto
            self.text_widget.delete("1.0", "end")
            self.comp_lista.refresh()
            self.update_button_text()
            self.update_preview()

    def edit_subtitle(self):
        idx = self.comp_lista.get_selection()
        if idx is None:
            messagebox.showwarning("Aviso", "Selecione uma legenda para editar.")
            return
        
        # Carregar texto da legenda no editor
        sub = self.subtitle_manager.get_subtitles()[idx]
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", sub["text"])
        
        # Ativar modo de edição quando usuário explicitamente edita
        self.editing_mode = True
        self.temporary_subtitle = None
        self.update_button_text()
        self.update_preview()

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
            # Carregar texto da legenda no editor
            sub = self.subtitle_manager.get_subtitles()[self.selected_subtitle_idx]
            self.text_widget.delete("1.0", "end")
            self.text_widget.insert("1.0", sub["text"])
            
            # Duplo clique ativa modo de edição
            self.editing_mode = True
            self.temporary_subtitle = None
            # Não chamar edit_subtitle() pois já carregamos o texto e ativamos edição
            self.update_button_text()
            self.update_preview()

    def render_live_preview(self, frame):
        """
        Callback usado pelo VideoSelector para renderizar decorações (legendas, bordas)
        sobre o frame do vídeo original em tempo real.
        """
        style = self.video_borders.get_effective_style()
        border_color = self.video_borders.border_color
        subtitles = self.subtitle_manager.get_subtitles()
        border_size_preview = self.video_borders.border_size_var.get()
        watermark_data = self.watermark_ui.get_state() if hasattr(self, 'watermark_ui') else None
        
        style_lower = style.lower()
        border_enabled = "moldura" in style_lower or "black" in style_lower or "white" in style_lower or "blur" in style_lower
        
        # 1. Redimensionar frame original para a área interna
        # Usamos BILINEAR no preview para ser mais rápido que LANCZOS
        v_w, v_h, _ = self.v_renderer.calculate_video_dimensions(border_enabled, border_size_preview, is_preview=True)
        video_resized = np.array(Image.fromarray(frame).resize((v_w, v_h), Image.Resampling.BILINEAR))
        
        # 2. Preparar fundo de blur se necessário
        bg_frame = None
        if "blur" in style_lower:
            # Resize rápido para o fundo
            bg_frame_raw = np.array(Image.fromarray(frame).resize((1080, 1920), Image.Resampling.NEAREST))
            bg_frame = self.v_renderer.apply_blur_opencv(bg_frame_raw)
            
        # 3. Renderizar composição final (usando o cachê de legendas e logos)
        # Obter duração do vídeo para end_time dinâmico
        video_duration = None
        if hasattr(self.video_controls.video_selector, 'current_video_clip') and self.video_controls.video_selector.current_video_clip:
            video_duration = self.video_controls.video_selector.current_video_clip.duration
        
        return self.v_renderer.render_frame(
            video_resized,
            subtitles,
            border_enabled,
            border_size_preview,
            border_color,
            style,
            background_frame=bg_frame,
            watermark_data=watermark_data,
            is_preview=True,
            emoji_scale=self.comp_emojis.emoji_scale.get(),
            current_time=self.video_controls.video_selector.current_time,
            video_duration=video_duration
        )

    # --- Lógica de Preview e Drag (Mantida aqui por ser o orquestrador do Canvas) ---
    def update_preview(self):
        video_path = self.video_controls.video_selector.current_video_path
        if not video_path: return

        style = self.video_borders.get_effective_style()
        border_color = self.video_borders.border_color
        subtitles = self.subtitle_manager.get_subtitles()
        border_size_preview = self.video_borders.border_size_var.get()
        
        # Invalida o cache se o estilo, cor ou PROPORÇÕES mudarem
        w_ratio = self.video_borders.video_w_ratio_var.get()
        h_ratio = self.video_borders.video_h_ratio_var.get()
        current_params = (video_path, style, border_color, border_size_preview, w_ratio, h_ratio)
        
        canvas = self.video_controls.video_selector.preview_canvas
        preview_w, preview_h = canvas.winfo_width(), canvas.winfo_height()
        if preview_w < 10: preview_w, preview_h = 360, 640

        if not self.cached_preview_base or self.last_preview_params != current_params:
            base_frame = self.editor.generate_base_preview(
                video_path, style, border_color, 
                border_size_preview=border_size_preview,
                video_width_ratio=w_ratio,
                video_height_ratio=h_ratio
            )
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
                # Usar proporções dinâmicas da UI
                w_ratio = self.video_borders.video_w_ratio_var.get()
                h_ratio = self.video_borders.video_h_ratio_var.get()
                
                v_w_preview = 360.0 * w_ratio
                v_h_preview = 640.0 * h_ratio
                
                off_x_preview = (360.0 - v_w_preview) / 2
                off_y_preview = (640.0 - v_h_preview) / 2
                
                offset_x = off_x_preview * scale
                offset_y = off_y_preview * scale
            else:
                offset_x = 0
                offset_y = 0
            
            current_time = self.video_controls.video_selector.current_time
            
            for idx, sub in enumerate(subtitles):
                is_selected = (idx == self.selected_subtitle_idx or idx == self.dragging_subtitle_idx)
                
                # SÓ desenha se estiver no tempo OU se for a selecionada (facilitando edição)
                start = sub.get("start_time", 0.0)
                end = sub.get("end_time", 1000.0)
                
                if not is_selected and not (start <= current_time <= end):
                    # Placeholder para o bbox cache se não for renderizado?
                    # Na verdade, precisamos do bbox cache para detecção de clique.
                    # Vamos adicionar apenas se renderizar.
                    continue

                self.renderer.draw_subtitle(draw, sub, scale_factor=scale, emoji_scale=self.comp_emojis.emoji_scale.get(), offset_x=offset_x, offset_y=offset_y)
                bbox = self.renderer.get_subtitle_bbox(sub, scale_factor=scale, emoji_scale=self.comp_emojis.emoji_scale.get(), offset_x=offset_x, offset_y=offset_y)
                
                if is_selected:
                    draw.rectangle(bbox, outline="yellow", width=2)
                
                canvas_bbox = (bbox[0] + img_x, bbox[1] + img_y, bbox[2] + img_x, bbox[3] + img_y)
                self.subtitle_bbox_cache.append(canvas_bbox)
            
            # Renderizar legenda temporária (preview em tempo real)
            if self.temporary_subtitle and not self.editing_mode:
                self.renderer.draw_subtitle(draw, self.temporary_subtitle, scale_factor=scale, emoji_scale=self.comp_emojis.emoji_scale.get(), offset_x=offset_x, offset_y=offset_y)
                bbox = self.renderer.get_subtitle_bbox(self.temporary_subtitle, scale_factor=scale, emoji_scale=self.comp_emojis.emoji_scale.get(), offset_x=offset_x, offset_y=offset_y)
                # Desenhar com borda verde para indicar que é temporária
                draw.rectangle(bbox, outline="lime", width=2)


            # --- Desenhar Marca d'Água em Texto ---
            self.watermark_bbox_cache = None
            if hasattr(self, 'watermark_ui') and self.watermark_ui:
                watermark_data = self.watermark_ui.get_state()
                if watermark_data.get("add_text_mark"):
                    self.v_renderer._draw_watermark(draw, watermark_data, scale, offset_x, offset_y)
                    
                    # Cache do BBox para interação
                    bbox = self.v_renderer.get_watermark_bbox(watermark_data, scale, offset_x, offset_y)
                    if bbox:
                        if self.selected_watermark or self.dragging_watermark:
                            draw.rectangle(bbox, outline="cyan", width=2)
                        
                        # Ajustar para coordenadas do Canvas
                        self.watermark_bbox_cache = (bbox[0] + img_x, bbox[1] + img_y, bbox[2] + img_x, bbox[3] + img_y)

            # --- Desenhar Logo (Imagem) ---
            self.logo_bbox_cache = None
            self.logo_resize_handle_bbox = None
            
            if hasattr(self, 'watermark_ui') and self.watermark_ui:
                watermark_data = self.watermark_ui.get_state()
                if watermark_data.get("logo_path"):
                    # Desenhar logo
                    self.v_renderer._draw_logo(img, watermark_data, scale, offset_x, offset_y)
                    
                    # BBox para interação
                    bbox = self.v_renderer.get_logo_bbox(watermark_data, scale, offset_x, offset_y)
                    if bbox:
                        canvas_bbox = (bbox[0] + img_x, bbox[1] + img_y, bbox[2] + img_x, bbox[3] + img_y)
                        self.logo_bbox_cache = canvas_bbox
                        
                        if self.selected_logo or self.dragging_logo or self.resizing_logo:
                            draw = ImageDraw.Draw(img)
                            draw.rectangle(bbox, outline="magenta", width=2)
                            
                            # Desenhar alça de redimensionamento (canto inferior direito)
                            handle_size = 10
                            handle_x1 = bbox[2] - handle_size
                            handle_y1 = bbox[3] - handle_size
                            handle_x2 = bbox[2]
                            handle_y2 = bbox[3]
                            
                            draw.rectangle((handle_x1, handle_y1, handle_x2, handle_y2), fill="magenta")
                            
                            # Cache da alça (coordenadas do canvas)
                            self.logo_resize_handle_bbox = (
                                handle_x1 + img_x, 
                                handle_y1 + img_y, 
                                handle_x2 + img_x, 
                                handle_y2 + img_y
                            )

            # --- Sistema de Redimensionamento Estilo Canva (8 Pontos) ---
            self.moldura_handles = {}
            w_ratio = self.video_borders.video_w_ratio_var.get()
            h_ratio = self.video_borders.video_h_ratio_var.get()
            
            v_w_p = 360.0 * w_ratio
            v_h_p = 640.0 * h_ratio
            off_x_p = (360.0 - v_w_p) / 2
            off_y_p = (640.0 - v_h_p) / 2
            
            # SÓ desenha o sistema de seleção se estiver selecionado ou redimensionando
            if self.selected_moldura or self.resizing_moldura:
                # BBox da Moldura na imagem do preview
                m_x1, m_y1 = off_x_p * scale, off_y_p * scale
                m_x2, m_y2 = (off_x_p + v_w_p) * scale, (off_y_p + v_h_p) * scale
                m_cx, m_cy = (m_x1 + m_x2) / 2, (m_y1 + m_y2) / 2
                
                # Desenhar Contorno de Seleção (Azul Canva)
                draw.rectangle((m_x1, m_y1, m_x2, m_y2), outline="#00C4CC", width=2)
                
                # Definir Posições das 8 Alças
                handles_pos = {
                    "tl": (m_x1, m_y1), "tr": (m_x2, m_y1),
                    "bl": (m_x1, m_y2), "br": (m_x2, m_y2),
                    "top": (m_cx, m_y1), "bottom": (m_cx, m_y2),
                    "left": (m_x1, m_cy), "right": (m_x2, m_cy)
                }
                
                h_radius = 6
                for h_id, (hx, hy) in handles_pos.items():
                    # Desenhar Círculo da Alça
                    draw.ellipse((hx - h_radius, hy - h_radius, hx + h_radius, hy + h_radius), 
                                 fill="white", outline="#00C4CC", width=2)
                    
                    # Cache para o Canvas
                    self.moldura_handles[h_id] = (
                        hx - h_radius + img_x, 
                        hy - h_radius + img_y, 
                        hx + h_radius + img_x, 
                        hy + h_radius + img_y
                    )

            self.preview_image_tk = ImageTk.PhotoImage(img)
            canvas.delete("all")
            canvas.create_image(preview_w//2, preview_h//2, image=self.preview_image_tk, anchor="center")
            canvas.image = self.preview_image_tk

    def on_preview_click(self, event):
        x, y = event.x, event.y
        
        # Parâmetros base do preview
        if not hasattr(self, 'preview_img_geometry'): return
        img_x, img_y, img_w, img_h = self.preview_img_geometry
        scale = self.preview_scale_factor
        
        # Parâmetros de Estilo
        style = self.video_borders.get_effective_style()
        style_lower = style.lower()
        border_enabled = any(k in style_lower for k in ["moldura", "black", "white", "blur"])

        # 1. Verificar Alças da Moldura de Vídeo (Estilo Canva)
        for h_id, bbox in self.moldura_handles.items():
            if bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
                self.resizing_moldura = True
                self.active_handle = h_id
                self.selected_moldura = True
                self.selected_subtitle_idx = None
                self.selected_logo = False
                self.selected_watermark = False
                self.update_preview()
                return

        # 2. Verificar Legendas
        for i in range(len(self.subtitle_bbox_cache)-1, -1, -1):
            bbox = self.subtitle_bbox_cache[i]
            if bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
                # Cálculo de offset dinâmico
                v_w_p = 360.0 * self.video_borders.video_w_ratio_var.get()
                v_h_p = 640.0 * self.video_borders.video_h_ratio_var.get()
                off_x_v = (360.0 - v_w_p) / 2
                off_y_v = (640.0 - v_h_p) / 2

                self.dragging_subtitle_idx = i
                self.selected_subtitle_idx = i
                self.selected_moldura = False
                self.selected_watermark = False
                self.comp_lista.set_selection(i)
                
                click_v_x, click_v_y = canvas_para_video(x, y, self.preview_img_geometry, scale)
                sub = self.subtitle_manager.get_subtitles()[i]
                self.drag_offset_x = click_v_x - (sub["x"] + off_x_v)
                self.drag_offset_y = click_v_y - (sub["y"] + off_y_v)
                
                self.update_preview()
                return
        
        # 3. Verificar Marca d'Água e Logo
        v_w_p = 360.0 * self.video_borders.video_w_ratio_var.get()
        v_h_p = 640.0 * self.video_borders.video_h_ratio_var.get()
        off_x_v = (360.0 - v_w_p) / 2
        off_y_v = (640.0 - v_h_p) / 2

        if self.watermark_bbox_cache:
            bbox = self.watermark_bbox_cache
            if bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
                self.dragging_watermark = True
                self.selected_watermark = True
                self.selected_moldura = False
                self.selected_subtitle_idx = None
                
                click_v_x, click_v_y = canvas_para_video(x, y, self.preview_img_geometry, scale)
                water_data = self.watermark_ui.get_state()
                self.drag_offset_x = click_v_x - (water_data["x"] + off_x_v)
                self.drag_offset_y = click_v_y - (water_data["y"] + off_y_v)
                
                self.update_preview()
                return

        if self.logo_bbox_cache:
            # Alça de redimensionamento da Logo
            if self.logo_resize_handle_bbox:
                hbox = self.logo_resize_handle_bbox
                if hbox[0] <= x <= hbox[2] and hbox[1] <= y <= hbox[3]:
                    self.resizing_logo = True
                    self.selected_logo = True
                    self.selected_moldura = False
                    self.initial_logo_scale = self.watermark_ui.get_state().get("logo_scale", 0.2)
                    self.initial_mouse_y = y
                    self.update_preview()
                    return

            # Corpo da Logo
            lbox = self.logo_bbox_cache
            if lbox[0] <= x <= lbox[2] and lbox[1] <= y <= lbox[3]:
                self.dragging_logo = True
                self.selected_logo = True
                self.selected_moldura = False
                self.selected_subtitle_idx = None
                
                click_v_x, click_v_y = canvas_para_video(x, y, self.preview_img_geometry, scale)
                water_data = self.watermark_ui.get_state()
                self.drag_offset_x = click_v_x - (water_data.get("logo_x", 0) + off_x_v)
                self.drag_offset_y = click_v_y - (water_data.get("logo_y", 0) + off_y_v)
                
                self.update_preview()
                return

        # 4. Verificar Clique na Área do Vídeo (Sempre permitir seleção se clicar na moldura)
        w_ratio = self.video_borders.video_w_ratio_var.get()
        h_ratio = self.video_borders.video_h_ratio_var.get()
        
        v_w_p = 360.0 * w_ratio
        v_h_p = 640.0 * h_ratio
        off_x_p = (360.0 - v_w_p) / 2
        off_y_p = (640.0 - v_h_p) / 2
        
        # BBox no Canvas
        v_x1 = (off_x_p * scale) + img_x
        v_y1 = (off_y_p * scale) + img_y
        v_x2 = v_x1 + (v_w_p * scale)
        v_y2 = v_y1 + (v_h_p * scale)
        
        if v_x1 <= x <= v_x2 and v_y1 <= y <= v_y2:
            self.selected_moldura = True
            self.selected_subtitle_idx = None
            self.selected_watermark = False
            self.selected_logo = False
            self.update_preview()
            return

        # Deselecionar tudo se clicar no vazio
        self.selected_subtitle_idx = None
        self.selected_watermark = False
        self.selected_logo = False
        self.selected_moldura = False
        self.update_preview()

    def on_preview_drag(self, event):
        if self.resizing_moldura:
            img_x, img_y, img_w, img_h = self.preview_img_geometry
            scale = self.preview_scale_factor
            
            # Coordenadas relativas à base 360x640
            x_rel = (event.x - img_x) / scale
            y_rel = (event.y - img_y) / scale
            
            # Redimensionamento Simétrico por Eixo (Estilo Canva)
            # Se for alça lateral, só altera largura. Se for topo/fundo, só altera altura.
            change_w = self.active_handle in ["tl", "tr", "bl", "br", "left", "right"]
            change_h = self.active_handle in ["tl", "tr", "bl", "br", "top", "bottom"]
            
            if change_w:
                new_w_ratio = (abs(x_rel - 180.0) * 2.0) / 360.0
                new_w_ratio = max(0.1, min(1.0, new_w_ratio))
                self.video_borders.video_w_ratio_var.set(round(new_w_ratio, 3))
                self.v_renderer.video_width_ratio = new_w_ratio
                
            if change_h:
                new_h_ratio = (abs(y_rel - 320.0) * 2.0) / 640.0
                new_h_ratio = max(0.1, min(1.0, new_h_ratio))
                self.video_borders.video_h_ratio_var.set(round(new_h_ratio, 3))
                self.v_renderer.video_height_ratio = new_h_ratio
            
            self.update_preview()
            
        elif self.dragging_subtitle_idx is not None:
            scale = self.preview_scale_factor
            
            # Cálculo de offset dinâmico baseado na moldura atual
            v_w_p = 360.0 * self.video_borders.video_w_ratio_var.get()
            v_h_p = 640.0 * self.video_borders.video_h_ratio_var.get()
            border_offset_x = (360.0 - v_w_p) / 2
            border_offset_y = (640.0 - v_h_p) / 2
            
            new_render_x, new_render_y = canvas_para_video(event.x, event.y, self.preview_img_geometry, scale)
            new_video_x = new_render_x - self.drag_offset_x - border_offset_x
            new_video_y = new_render_y - self.drag_offset_y - border_offset_y
            
            self.subtitle_manager.update_subtitle(self.dragging_subtitle_idx, x=int(new_video_x), y=int(new_video_y))
            self.update_preview()
            
        elif self.dragging_watermark:
            scale = self.preview_scale_factor
            
            v_w_p = 360.0 * self.video_borders.video_w_ratio_var.get()
            v_h_p = 640.0 * self.video_borders.video_h_ratio_var.get()
            border_offset_x = (360.0 - v_w_p) / 2
            border_offset_y = (640.0 - v_h_p) / 2
            
            new_render_x, new_render_y = canvas_para_video(event.x, event.y, self.preview_img_geometry, scale)
            new_x = new_render_x - self.drag_offset_x - border_offset_x
            new_y = new_render_y - self.drag_offset_y - border_offset_y
            
            self.watermark_ui.update_position(int(new_x), int(new_y))
            self.update_preview()
        
        elif self.dragging_logo:
            scale = self.preview_scale_factor
            
            v_w_p = 360.0 * self.video_borders.video_w_ratio_var.get()
            v_h_p = 640.0 * self.video_borders.video_h_ratio_var.get()
            border_offset_x = (360.0 - v_w_p) / 2
            border_offset_y = (640.0 - v_h_p) / 2
            
            new_render_x, new_render_y = canvas_para_video(event.x, event.y, self.preview_img_geometry, scale)
            new_video_x = new_render_x - self.drag_offset_x - border_offset_x
            new_video_y = new_render_y - self.drag_offset_y - border_offset_y
            
            self.watermark_ui.update_logo_position(int(new_video_x), int(new_video_y))
            self.update_preview()

        elif self.resizing_logo:
            # Lógica simples de redimensionamento baseada no movimento vertical do mouse
            dy = event.y - self.initial_mouse_y
            # Sensibilidade: 100px de movimento = 0.1 de escala
            scale_delta = dy / 500.0
            new_scale = self.initial_logo_scale + scale_delta
            
            self.watermark_ui.update_logo_scale(new_scale)

    def on_preview_release(self, event):
        self.dragging_subtitle_idx = None
        self.dragging_watermark = False
        self.dragging_logo = False
        self.resizing_logo = False
        self.resizing_moldura = False
        self.active_handle = None
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
