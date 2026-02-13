import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from modules.batch_queue_manager import batch_queue_manager
from modules.render_orchestrator import render_orchestrator


class LotesInVideos(ttk.Frame):
    """Aba de gerenciamento de lotes dentro das Configurações"""
    
    def __init__(self, parent, editor_ui):
        super().__init__(parent)
        self.editor_ui = editor_ui
        self.batch_manager = batch_queue_manager
        self.batch_manager.set_editor_ui(editor_ui)
        self.batch_manager.on_status_change = self.update_ui
        
        self._build_ui()
        self._update_queue_indicator()  # Atualizar indicador inicial
        self.update_ui()
    
    def _build_ui(self):
        """Constrói a interface da aba"""
        # Cabeçalho informativo
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        # Indicador de arquivo de fila ativo
        self.queue_file_label = ttk.Label(
            header_frame,
            text="",
            font=("Segoe UI", 9, "bold"),
            foreground="#3498db"
        )
        self.queue_file_label.pack(side="left", padx=(0, 15))
        
        warning_label = ttk.Label(
            header_frame,
            text="⚠️ Cada lote será aplicado em TODAS as abas",
            font=("Segoe UI", 10, "bold"),
            foreground="#FF6B00"
        )
        warning_label.pack(side="left")
        
        # Container principal: lista + botões
        main_container = ttk.Frame(self)
        main_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # ========== LISTA DE LOTES ==========
        list_frame = ttk.Frame(main_container)
        list_frame.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        
        # Treeview
        columns = ("status", "name", "input", "output", "audio")
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            height=10,
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)
        
        # Configurar colunas
        self.tree.heading("status", text="Status")
        self.tree.heading("name", text="Nome do Lote")
        self.tree.heading("input", text="Vídeo/Pasta")
        self.tree.heading("output", text="Saída")
        self.tree.heading("audio", text="Áudio")
        
        self.tree.column("status", width=80, anchor="center")
        self.tree.column("name", width=150)
        self.tree.column("input", width=200)
        self.tree.column("output", width=150)
        self.tree.column("audio", width=120)
        
        self.tree.pack(side="left", fill="both", expand=True)
        
        # ========== BOTÕES DE GERENCIAMENTO ==========
        buttons_frame = ttk.Frame(main_container)
        buttons_frame.pack(side="right", fill="y", padx=(10, 0))
        
        ttk.Button(
            buttons_frame,
            text="➕ Adicionar Lote",
            command=self.add_batch_dialog,
            width=18
        ).pack(pady=5)
        
        ttk.Button(
            buttons_frame,
            text="➖ Remover",
            command=self.remove_batch,
            width=18
        ).pack(pady=5)
        
        ttk.Button(
            buttons_frame,
            text="⬆️ Mover para Cima",
            command=lambda: self.move_batch("up"),
            width=18
        ).pack(pady=5)
        
        ttk.Button(
            buttons_frame,
            text="⬇️ Mover para Baixo",
            command=lambda: self.move_batch("down"),
            width=18
        ).pack(pady=5)
        
        ttk.Separator(buttons_frame, orient="horizontal").pack(fill="x", pady=10)
        
        ttk.Button(
            buttons_frame,
            text="🗑️ Limpar Tudo",
            command=self.clear_all,
            width=18
        ).pack(pady=5)
        
        # ========== CONTROLES DE EXECUÇÃO ==========
        control_frame = ttk.LabelFrame(self, text="Controles de Execução", padding=10)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Botões de controle
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill="x", pady=(0, 10))
        
        self.start_btn = ttk.Button(
            btn_frame,
            text="▶️ Iniciar Fila de Lotes",
            command=self.start_queue,
            style="Accent.TButton"
        )
        self.start_btn.pack(side="left", padx=5)
        
        self.pause_btn = ttk.Button(
            btn_frame,
            text="⏸️ Pausar",
            command=self.pause_queue,
            state="disabled"
        )
        self.pause_btn.pack(side="left", padx=5)
        
        self.stop_btn = ttk.Button(
            btn_frame,
            text="🛑 Parar",
            command=self.stop_queue,
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=5)
        
        # Status label
        self.status_label = ttk.Label(
            control_frame,
            text="📊 Aguardando...",
            font=("Segoe UI", 9)
        )
        self.status_label.pack(fill="x", pady=5)
        
        # Progress bars
        progress_frame = ttk.Frame(control_frame)
        progress_frame.pack(fill="x", pady=5)
        
        ttk.Label(progress_frame, text="Lote Atual:").grid(row=0, column=0, sticky="w")
        self.current_progress = ttk.Progressbar(
            progress_frame,
            mode="determinate",
            length=300
        )
        self.current_progress.grid(row=0, column=1, sticky="ew", padx=5)
        
        ttk.Label(progress_frame, text="Global:").grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.global_progress = ttk.Progressbar(
            progress_frame,
            mode="determinate",
            length=300
        )
        self.global_progress.grid(row=1, column=1, sticky="ew", padx=5, pady=(5, 0))
        
        progress_frame.columnconfigure(1, weight=1)
    
    def add_batch_dialog(self):
        """Abre diálogo para adicionar novo lote"""
        dialog = tk.Toplevel(self)
        dialog.title("Adicionar Lote")
        dialog.geometry("780x540")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (780 // 2)
        y = (dialog.winfo_screenheight() // 2) - (540 // 2)
        dialog.geometry(f"780x540+{x}+{y}")
        
        # Frame principal
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Nome do lote
        ttk.Label(main_frame, text="Nome do Lote (opcional):").grid(row=0, column=0, sticky="w", pady=5)
        name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=name_var, width=40).grid(row=0, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        # Vídeo/Pasta de entrada
        ttk.Label(main_frame, text="Vídeo/Pasta de Entrada:*", foreground="red").grid(row=1, column=0, sticky="w", pady=5)
        input_var = tk.StringVar()
        input_entry = ttk.Entry(main_frame, textvariable=input_var, width=40)
        input_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        btn_frame1 = ttk.Frame(main_frame)
        btn_frame1.grid(row=2, column=1, sticky="w", padx=(10, 0))
        ttk.Button(
            btn_frame1,
            text="Escolher Arquivo",
            command=lambda: self._browse_file(input_var, dialog),
            width=15
        ).pack(side="left", padx=(0, 5))
        ttk.Button(
            btn_frame1,
            text="Escolher Pasta",
            command=lambda: self._browse_folder(input_var, dialog),
            width=15
        ).pack(side="left")
        
        # Pasta de saída
        ttk.Label(main_frame, text="Pasta de Saída:*", foreground="red").grid(row=3, column=0, sticky="w", pady=(15, 5))
        output_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=output_var, width=40).grid(row=3, column=1, sticky="ew", pady=(15, 5), padx=(10, 0))
        ttk.Button(
            main_frame,
            text="Escolher Pasta",
            command=lambda: self._browse_folder(output_var, dialog),
            width=15
        ).grid(row=4, column=1, sticky="w", padx=(10, 0))
        
        # Pasta de áudio (opcional)
        use_audio_var = tk.BooleanVar(value=False)
        audio_var = tk.StringVar()
        
        audio_check = ttk.Checkbutton(
            main_frame,
            text="Usar pasta de áudio personalizada",
            variable=use_audio_var,
            command=lambda: audio_entry.config(state="normal" if use_audio_var.get() else "disabled")
        )
        audio_check.grid(row=5, column=0, columnspan=2, sticky="w", pady=(15, 5))
        
        audio_entry = ttk.Entry(main_frame, textvariable=audio_var, width=40, state="disabled")
        audio_entry.grid(row=6, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        ttk.Button(
            main_frame,
            text="Escolher Pasta",
            command=lambda: self._browse_folder(audio_var, dialog),
            width=15
        ).grid(row=7, column=1, sticky="w", padx=(10, 0))
        
        # Tooltip
        tooltip = ttk.Label(
            main_frame,
            text="💡 Se desmarcado, usa a pasta de áudio configurada em cada aba",
            font=("Segoe UI", 8),
            foreground="gray"
        )
        tooltip.grid(row=8, column=0, columnspan=2, sticky="w", pady=5)
        
        main_frame.columnconfigure(1, weight=1)
        
        # Botões de ação
        action_frame = ttk.Frame(dialog, padding=(20, 0, 20, 20))
        action_frame.pack(fill="x", side="bottom")
        
        def add_batch():
            input_path = input_var.get().strip()
            output_path = output_var.get().strip()
            
            if not input_path:
                messagebox.showwarning("Aviso", "Selecione um vídeo ou pasta de entrada")
                return
            
            if not output_path:
                messagebox.showwarning("Aviso", "Selecione uma pasta de saída")
                return
            
            name = name_var.get().strip()
            audio_folder = audio_var.get().strip() if use_audio_var.get() else None
            
            self.batch_manager.add_batch(name, input_path, output_path, audio_folder)
            messagebox.showinfo("Sucesso", f"Lote '{name or 'Lote ' + str(len(self.batch_manager.batches))}' adicionado!")
            dialog.destroy()
        
        ttk.Button(
            action_frame,
            text="Adicionar",
            command=add_batch,
            style="Accent.TButton",
            width=12
        ).pack(side="right", padx=5)
        
        ttk.Button(
            action_frame,
            text="Cancelar",
            command=dialog.destroy,
            width=12
        ).pack(side="right")
    
    def _browse_file(self, var, parent=None):
        """Abre diálogo para selecionar arquivo"""
        filepath = filedialog.askopenfilename(
            parent=parent,
            title="Selecionar Vídeo/Imagem",
            filetypes=[
                ("Vídeos e Imagens", "*.mp4 *.mov *.avi *.mkv *.jpg *.jpeg *.png"),
                ("Todos os arquivos", "*.*")
            ]
        )
        if filepath:
            var.set(filepath)
    
    def _browse_folder(self, var, parent=None):
        """Abre diálogo para selecionar pasta"""
        folder = filedialog.askdirectory(parent=parent, title="Selecionar Pasta")
        if folder:
            var.set(folder)
    
    def remove_batch(self):
        """Remove lote selecionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um lote para remover")
            return
        
        item = selection[0]
        index = self.tree.index(item)
        
        if index < len(self.batch_manager.batches):
            batch = self.batch_manager.batches[index]
            
            if messagebox.askyesno("Confirmar", f"Remover lote '{batch.name}'?"):
                self.batch_manager.remove_batch(batch.id)
    
    def move_batch(self, direction):
        """Move lote para cima ou para baixo"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um lote para mover")
            return
        
        item = selection[0]
        index = self.tree.index(item)
        
        if index < len(self.batch_manager.batches):
            batch = self.batch_manager.batches[index]
            self.batch_manager.move_batch(batch.id, direction)
    
    def clear_all(self):
        """Limpa todos os lotes"""
        if not self.batch_manager.batches:
            messagebox.showinfo("Info", "Nenhum lote na fila")
            return
        
        if messagebox.askyesno("Confirmar", f"Remover todos os {len(self.batch_manager.batches)} lotes?"):
            self.batch_manager.clear_queue()
            messagebox.showinfo("Sucesso", "Todos os lotes foram removidos")
    
    def start_queue(self):
        """Inicia processamento da fila"""
        if not self.batch_manager.batches:
            messagebox.showwarning("Aviso", "Nenhum lote na fila")
            return
        
        if self.batch_manager.start_queue():
            self.start_btn.config(state="disabled")
            self.pause_btn.config(state="normal")
            self.stop_btn.config(state="normal")
    
    def pause_queue(self):
        """Pausa a fila"""
        self.batch_manager.pause_queue()
        self.pause_btn.config(text="▶️ Retomar", command=self.resume_queue)
    
    def resume_queue(self):
        """Retoma a fila"""
        self.batch_manager.resume_queue()
        self.pause_btn.config(text="⏸️ Pausar", command=self.pause_queue)
    
    def stop_queue(self):
        """Para a fila"""
        if messagebox.askyesno("Confirmar", "Deseja parar o processamento da fila?"):
            self.batch_manager.stop_queue()
            self.start_btn.config(state="normal")
            self.pause_btn.config(state="disabled")
            self.stop_btn.config(state="disabled")
    
    def update_ui(self):
        """Atualiza a interface baseado no estado atual"""
        # Proteção: Verifica se o widget ainda existe (evita erro se diálogo fechado)
        if not self.winfo_exists():
            return

        # Garantir que a atualização ocorra na thread principal
        def _perform_update():
            if not self.winfo_exists():
                return
                
            # Limpar lista
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Preencher lista
            for batch in self.batch_manager.batches:
                status_icon = {
                    "pending": "⏳",
                    "processing": "▶️",
                    "completed": "✅",
                    "error": "❌"
                }.get(batch.status, "❓")
                
                import os
                input_display = os.path.basename(batch.input_path)
                output_display = os.path.basename(batch.output_folder) or batch.output_folder
                audio_display = os.path.basename(batch.audio_folder) if batch.audio_folder else "(padrão)"
                
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        status_icon,
                        batch.name,
                        input_display,
                        output_display,
                        audio_display
                    )
                )
            
            # Atualizar status e progress bars
            stats = self.batch_manager.get_statistics()
            
            if self.batch_manager.is_active or render_orchestrator.is_active:
                current_batch = self.batch_manager.get_current_batch()
                if current_batch and self.batch_manager.is_active:
                    self.status_label.config(
                        text=f"📊 Lote {self.batch_manager.current_batch_index + 1}/{stats['total']} - {current_batch.name}"
                    )
                elif render_orchestrator.is_active:
                    self.status_label.config(text="📊 Renderização manual em curso...")
                
                # Progress global (só se batch manager estiver ativo)
                if self.batch_manager.is_active and stats['total'] > 0:
                    progress_pct = (stats['completed'] / stats['total']) * 100
                    self.global_progress['value'] = progress_pct
                
                # Botões
                self.start_btn.config(state="disabled")
                self.pause_btn.config(state="normal" if self.batch_manager.is_active else "disabled")
                self.stop_btn.config(state="normal" if self.batch_manager.is_active else "disabled")
            else:
                self.status_label.config(
                    text=f"📊 {stats['completed']}/{stats['total']} concluídos | {stats['errors']} erros"
                )
                self.global_progress['value'] = 0
                self.current_progress['value'] = 0
                
                # Botões
                self.start_btn.config(state="normal")
                self.pause_btn.config(state="disabled")
                self.stop_btn.config(state="disabled")

        # Agendar execução na thread principal do Tkinter
        self.after(0, _perform_update)
    
    def refresh_from_manager(self):
        """Atualiza interface após troca de fila"""
        self.update_ui()
        self._update_queue_indicator()
    
    def _update_queue_indicator(self):
        """Atualiza label mostrando arquivo de fila ativo"""
        queue_name = self.batch_manager.get_current_queue_name()
        
        if queue_name == "global":
            self.queue_file_label.config(
                text="📂 Arquivo: global (batch_queue_state.json)",
                foreground="#2ecc71"  # Verde
            )
        else:
            self.queue_file_label.config(
                text=f"📂 Arquivo: {queue_name}.json",
                foreground="#3498db"  # Azul
            )

