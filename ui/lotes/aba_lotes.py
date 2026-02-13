import tkinter as tk
from tkinter import ttk, messagebox
import os
from modules.batch_queue_manager import batch_queue_manager
from modules.render_orchestrator import render_orchestrator
from ui.lotes.dialogo_lote import DialogoLote

class AbaLotes(ttk.Frame):
    """Componente de interface (aba) para gerenciamento de lotes"""
    
    def __init__(self, pai, editor_ui):
        super().__init__(pai)
        self.editor_ui = editor_ui
        self.gerenciador_lotes = batch_queue_manager
        self.gerenciador_lotes.set_editor_ui(editor_ui)
        self.gerenciador_lotes.on_status_change = self.atualizar_interface
        
        self._construir_interface()
        self._atualizar_indicador_fila()
        self.atualizar_interface()
    
    def _construir_interface(self):
        """Constrói os elementos visuais da aba"""
        # Cabeçalho
        frame_cabecalho = ttk.Frame(self)
        frame_cabecalho.pack(fill="x", padx=10, pady=10)
        
        self.label_arquivo_fila = ttk.Label(
            frame_cabecalho,
            text="",
            font=("Segoe UI", 9, "bold"),
            foreground="#3498db"
        )
        self.label_arquivo_fila.pack(side="left", padx=(0, 15))
        
        label_aviso = ttk.Label(
            frame_cabecalho,
            text="⚠️ Cada lote será aplicado em TODAS as abas",
            font=("Segoe UI", 10, "bold"),
            foreground="#FF6B00"
        )
        label_aviso.pack(side="left")
        
        # Container principal
        container_principal = ttk.Frame(self)
        container_principal.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Lista de Lotes (Treeview)
        frame_lista = ttk.Frame(container_principal)
        frame_lista.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        
        colunas = ("status", "nome", "entrada", "saida", "audio")
        self.arvore = ttk.Treeview(
            frame_lista,
            columns=colunas,
            show="headings",
            height=10,
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.arvore.yview)
        
        self.arvore.heading("status", text="Status")
        self.arvore.heading("nome", text="Nome do Lote")
        self.arvore.heading("entrada", text="Vídeo/Pasta")
        self.arvore.heading("saida", text="Saída")
        self.arvore.heading("audio", text="Áudio")
        
        self.arvore.column("status", width=80, anchor="center")
        self.arvore.column("nome", width=150)
        self.arvore.column("entrada", width=200)
        self.arvore.column("saida", width=150)
        self.arvore.column("audio", width=120)
        
        self.arvore.pack(side="left", fill="both", expand=True)
        
        # Botões de Gerenciamento Lateral
        frame_botoes = ttk.Frame(container_principal)
        frame_botoes.pack(side="right", fill="y", padx=(10, 0))
        
        ttk.Button(frame_botoes, text="➕ Adicionar Lote", command=self.abrir_dialogo_adicionar, width=20).pack(pady=5)
        ttk.Button(frame_botoes, text="✏️ Editar Lote", command=self.abrir_dialogo_editar, width=20).pack(pady=5)
        ttk.Button(frame_botoes, text="➖ Remover", command=self.remover_lote, width=20).pack(pady=5)
        
        ttk.Button(frame_botoes, text="⬆️ Mover para Cima", command=lambda: self.mover_lote("up"), width=20).pack(pady=5)
        ttk.Button(frame_botoes, text="⬇️ Mover para Baixo", command=lambda: self.mover_lote("down"), width=20).pack(pady=5)
        
        ttk.Separator(frame_botoes, orient="horizontal").pack(fill="x", pady=10)
        ttk.Button(frame_botoes, text="🗑️ Limpar Tudo", command=self.limpar_tudo, width=20).pack(pady=5)
        
        # Controles de Execução
        frame_controles = ttk.LabelFrame(self, text="Controles de Execução", padding=10)
        frame_controles.pack(fill="x", padx=10, pady=10)
        
        frame_btns_exec = ttk.Frame(frame_controles)
        frame_btns_exec.pack(fill="x", pady=(0, 10))
        
        self.btn_iniciar = ttk.Button(frame_btns_exec, text="▶️ Iniciar Fila", command=self.iniciar_fila, style="Accent.TButton")
        self.btn_iniciar.pack(side="left", padx=5)
        
        self.btn_pausar = ttk.Button(frame_btns_exec, text="⏸️ Pausar", command=self.pausar_fila, state="disabled")
        self.btn_pausar.pack(side="left", padx=5)
        
        self.btn_parar = ttk.Button(frame_btns_exec, text="🛑 Parar", command=self.parar_fila, state="disabled")
        self.btn_parar.pack(side="left", padx=5)
        
        self.label_status = ttk.Label(frame_controles, text="📊 Aguardando...", font=("Segoe UI", 9))
        self.label_status.pack(fill="x", pady=5)
        
        # Barras de Progresso
        frame_progresso = ttk.Frame(frame_controles)
        frame_progresso.pack(fill="x", pady=5)
        
        ttk.Label(frame_progresso, text="Lote Atual:").grid(row=0, column=0, sticky="w")
        self.progresso_atual = ttk.Progressbar(frame_progresso, mode="determinate")
        self.progresso_atual.grid(row=0, column=1, sticky="ew", padx=5)
        
        ttk.Label(frame_progresso, text="Global:").grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.progresso_global = ttk.Progressbar(frame_progresso, mode="determinate")
        self.progresso_global.grid(row=1, column=1, sticky="ew", padx=5, pady=(5, 0))
        
        frame_progresso.columnconfigure(1, weight=1)

    def abrir_dialogo_editar(self):
        selecao = self.arvore.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um lote para editar")
            return
            
        indice = self.arvore.index(selecao[0])
        if indice < len(self.gerenciador_lotes.batches):
            lote = self.gerenciador_lotes.batches[indice]
            DialogoLote(self, self.gerenciador_lotes, self.editor_ui, lote_para_editar=lote)

    def abrir_dialogo_adicionar(self):
        DialogoLote(self, self.gerenciador_lotes, self.editor_ui)

    def remover_lote(self):
        selecao = self.arvore.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um lote para remover")
            return
        
        indice = self.arvore.index(selecao[0])
        if indice < len(self.gerenciador_lotes.batches):
            lote = self.gerenciador_lotes.batches[indice]
            if messagebox.askyesno("Confirmar", f"Remover lote '{lote.name}'?"):
                self.gerenciador_lotes.remove_batch(lote.id)
    
    def mover_lote(self, direcao):
        selecao = self.arvore.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um lote para mover")
            return
        
        indice = self.arvore.index(selecao[0])
        if indice < len(self.gerenciador_lotes.batches):
            lote = self.gerenciador_lotes.batches[indice]
            self.gerenciador_lotes.move_batch(lote.id, direcao)
    
    def limpar_tudo(self):
        if not self.gerenciador_lotes.batches:
            return
        if messagebox.askyesno("Confirmar", f"Remover todos os {len(self.gerenciador_lotes.batches)} lotes?"):
            self.gerenciador_lotes.clear_queue()

    def iniciar_fila(self):
        if not self.gerenciador_lotes.batches:
            messagebox.showwarning("Aviso", "Nenhum lote na fila")
            return
        if self.gerenciador_lotes.start_queue():
            self._atualizar_botoes_ativo(True)
    
    def pausar_fila(self):
        self.gerenciador_lotes.pause_queue()
        self.btn_pausar.config(text="▶️ Retomar", command=self.retomar_fila)
    
    def retomar_fila(self):
        self.gerenciador_lotes.resume_queue()
        self.btn_pausar.config(text="⏸️ Pausar", command=self.pausar_fila)
    
    def parar_fila(self):
        if messagebox.askyesno("Confirmar", "Deseja parar o processamento da fila?"):
            self.gerenciador_lotes.stop_queue()
            self._atualizar_botoes_ativo(False)

    def _atualizar_botoes_ativo(self, ativo):
        self.btn_iniciar.config(state="disabled" if ativo else "normal")
        self.btn_pausar.config(state="normal" if ativo else "disabled")
        self.btn_parar.config(state="normal" if ativo else "disabled")

    def atualizar_interface(self):
        if not self.winfo_exists():
            return

        def _executar_atualizacao():
            if not self.winfo_exists():
                return
                
            for item in self.arvore.get_children():
                self.arvore.delete(item)
            
            for lote in self.gerenciador_lotes.batches:
                icone_status = {
                    "pending": "⏳",
                    "processing": "▶️",
                    "completed": "✅",
                    "error": "❌"
                }.get(lote.status, "❓")
                
                entrada = os.path.basename(lote.input_path)
                saida = os.path.basename(lote.output_folder) or lote.output_folder
                audio = os.path.basename(lote.audio_folder) if lote.audio_folder else "(padrão)"
                
                self.arvore.insert("", "end", values=(icone_status, lote.name, entrada, saida, audio))
            
            estatisticas = self.gerenciador_lotes.get_statistics()
            ativo = self.gerenciador_lotes.is_active or render_orchestrator.is_active
            
            if ativo:
                lote_atual = self.gerenciador_lotes.get_current_batch()
                if lote_atual and self.gerenciador_lotes.is_active:
                    self.label_status.config(text=f"📊 Lote {self.gerenciador_lotes.current_batch_index + 1}/{estatisticas['total']} - {lote_atual.name}")
                elif render_orchestrator.is_active:
                    self.label_status.config(text="📊 Renderização manual em curso...")
                
                if self.gerenciador_lotes.is_active and estatisticas['total'] > 0:
                    progresso = (estatisticas['completed'] / estatisticas['total']) * 100
                    self.progresso_global['value'] = progresso
                
                self._atualizar_botoes_ativo(True)
            else:
                self.label_status.config(text=f"📊 {estatisticas['completed']}/{estatisticas['total']} concluídos | {estatisticas['errors']} erros")
                self.progresso_global['value'] = 0
                self.progresso_atual['value'] = 0
                self._atualizar_botoes_ativo(False)

        self.after(0, _executar_atualizacao)
    
    def refresh_from_manager(self):
        self.atualizar_interface()
        self._atualizar_indicador_fila()
    
    def _atualizar_indicador_fila(self):
        nome_fila = self.gerenciador_lotes.get_current_queue_name()
        if nome_fila == "global":
            self.label_arquivo_fila.config(text="📂 Arquivo: global (batch_queue_state.json)", foreground="#2ecc71")
        else:
            self.label_arquivo_fila.config(text=f"📂 Arquivo: {nome_fila}.json", foreground="#3498db")
