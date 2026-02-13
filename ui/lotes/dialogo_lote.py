import tkinter as tk
from tkinter import ttk, messagebox
import os
from .utilitarios import selecionar_arquivo, selecionar_pasta
from .pool_lotes import PoolLotesUI

class DialogoLote(tk.Toplevel):
    """Diálogo profissional para Adicionar ou Editar um Lote de vídeos"""
    def __init__(self, pai, gerenciador_lotes, editor_ui, lote_para_editar=None):
        super().__init__(pai)
        self.gerenciador_lotes = gerenciador_lotes
        self.editor_ui = editor_ui
        self.lote_para_editar = lote_para_editar
        self.eh_edicao = lote_para_editar is not None
        
        # Configuração da janela - layout mais largo
        self.title("✏️ Editar Lote" if self.eh_edicao else "➕ Adicionar Novo Lote")
        self.geometry("1200x650")
        self.transient(pai.winfo_toplevel())
        self.grab_set()
        self.configure(bg="#f5f6fa")
        
        # Centralizar a janela
        self.update_idletasks()
        largura = 1200
        altura = 650
        x = (self.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.winfo_screenheight() // 2) - (altura // 2)
        self.geometry(f"{largura}x{altura}+{x}+{y}")
        
        self._configurar_interface()

    def _configurar_interface(self):
        # Container principal com padding
        container_principal = ttk.Frame(self, padding=25)
        container_principal.pack(fill="both", expand=True)
        
        # Cabeçalho com título e descrição
        self._criar_cabecalho(container_principal)
        
        # Container de duas colunas
        frame_colunas = ttk.Frame(container_principal)
        frame_colunas.pack(fill="both", expand=True, pady=(0, 15))
        
        # Coluna Esquerda: Configurações do Lote
        coluna_esquerda = ttk.Frame(frame_colunas)
        coluna_esquerda.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Coluna Direita: Pool de Mídias
        coluna_direita = ttk.Frame(frame_colunas)
        coluna_direita.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Preencher colunas
        self._criar_coluna_configuracoes(coluna_esquerda)
        self._criar_coluna_pool(coluna_direita)
        
        # Rodapé com botões de ação
        self._criar_rodape(container_principal)

    def _criar_cabecalho(self, pai):
        frame_cabecalho = ttk.Frame(pai)
        frame_cabecalho.pack(fill="x", pady=(0, 20))
        
        icone = "✏️" if self.eh_edicao else "➕"
        titulo = "Editar Lote Existente" if self.eh_edicao else "Criar Novo Lote"
        
        ttk.Label(
            frame_cabecalho, 
            text=f"{icone} {titulo}",
            font=("Segoe UI", 16, "bold"),
            foreground="#2c3e50"
        ).pack(anchor="w")
        
        descricao = "Modifique as configurações do lote" if self.eh_edicao else "Configure um novo lote para processamento em fila"
        ttk.Label(
            frame_cabecalho,
            text=descricao,
            font=("Segoe UI", 9),
            foreground="#7f8c8d"
        ).pack(anchor="w", pady=(5, 0))

    def _criar_coluna_configuracoes(self, pai):
        """Coluna esquerda: Informações básicas, caminhos e áudio"""
        
        # Seção 1: Informações Básicas
        frame_basico = ttk.LabelFrame(pai, text=" 📝 Informações Básicas ", padding=15)
        frame_basico.pack(fill="x", pady=(0, 15))
        
        ttk.Label(
            frame_basico, 
            text="Nome do Lote:",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.var_nome = tk.StringVar(value=self.lote_para_editar.name if self.eh_edicao else "")
        entry_nome = ttk.Entry(frame_basico, textvariable=self.var_nome, font=("Segoe UI", 10))
        entry_nome.pack(fill="x", ipady=5)
        
        ttk.Label(
            frame_basico,
            text="Um nome descritivo para identificar este lote",
            font=("Segoe UI", 8),
            foreground="#95a5a6"
        ).pack(anchor="w", pady=(3, 0))
        
        # Seção 2: Caminhos
        frame_caminhos = ttk.LabelFrame(pai, text=" 📂 Caminhos de Entrada e Saída ", padding=15)
        frame_caminhos.pack(fill="x", pady=(0, 15))
        
        # Entrada
        ttk.Label(
            frame_caminhos,
            text="Vídeo ou Pasta de Entrada: *",
            font=("Segoe UI", 10, "bold"),
            foreground="#e74c3c"
        ).pack(anchor="w", pady=(0, 5))
        
        self.var_entrada = tk.StringVar(value=self.lote_para_editar.input_path if self.eh_edicao else "")
        
        frame_entrada = ttk.Frame(frame_caminhos)
        frame_entrada.pack(fill="x", pady=(0, 15))
        
        entry_entrada = ttk.Entry(frame_entrada, textvariable=self.var_entrada, font=("Segoe UI", 9))
        entry_entrada.pack(side="left", fill="x", expand=True, ipady=4)
        
        ttk.Button(
            frame_entrada,
            text="📄 Arquivo",
            command=lambda: selecionar_arquivo(self.var_entrada, self),
            width=12
        ).pack(side="left", padx=(5, 0))
        
        ttk.Button(
            frame_entrada,
            text="📁 Pasta",
            command=lambda: selecionar_pasta(self.var_entrada, self),
            width=12
        ).pack(side="left", padx=(5, 0))
        
        # Saída
        ttk.Label(
            frame_caminhos,
            text="Pasta de Saída: *",
            font=("Segoe UI", 10, "bold"),
            foreground="#e74c3c"
        ).pack(anchor="w", pady=(0, 5))
        
        self.var_saida = tk.StringVar(value=self.lote_para_editar.output_folder if self.eh_edicao else "")
        
        frame_saida = ttk.Frame(frame_caminhos)
        frame_saida.pack(fill="x")
        
        entry_saida = ttk.Entry(frame_saida, textvariable=self.var_saida, font=("Segoe UI", 9))
        entry_saida.pack(side="left", fill="x", expand=True, ipady=4)
        
        ttk.Button(
            frame_saida,
            text="📁 Selecionar",
            command=lambda: selecionar_pasta(self.var_saida, self),
            width=15
        ).pack(side="left", padx=(5, 0))
        
        # Seção 3: Áudio
        frame_audio = ttk.LabelFrame(pai, text=" 🎵 Áudio Personalizado (Opcional) ", padding=15)
        frame_audio.pack(fill="x", pady=(0, 15))
        
        audio_inicial = self.lote_para_editar.audio_folder if self.eh_edicao else None
        self.var_usar_audio = tk.BooleanVar(value=audio_inicial is not None)
        self.var_audio = tk.StringVar(value=audio_inicial if audio_inicial else "")
        
        check_audio = ttk.Checkbutton(
            frame_audio,
            text="Usar pasta de áudio personalizada",
            variable=self.var_usar_audio,
            command=self._toggle_audio
        )
        check_audio.pack(anchor="w", pady=(0, 10))
        
        self.frame_audio_selecao = ttk.Frame(frame_audio)
        self.frame_audio_selecao.pack(fill="x")
        
        self.entry_audio = ttk.Entry(
            self.frame_audio_selecao,
            textvariable=self.var_audio,
            font=("Segoe UI", 9),
            state="normal" if self.var_usar_audio.get() else "disabled"
        )
        self.entry_audio.pack(side="left", fill="x", expand=True, ipady=4)
        
        self.btn_audio = ttk.Button(
            self.frame_audio_selecao,
            text="📁 Selecionar",
            command=lambda: selecionar_pasta(self.var_audio, self),
            width=15,
            state="normal" if self.var_usar_audio.get() else "disabled"
        )
        self.btn_audio.pack(side="left", padx=(5, 0))

    def _criar_coluna_pool(self, pai):
        """Coluna direita: Pool de Mídias"""
        
        frame_pool = ttk.LabelFrame(pai, text=" 🎬 Pool de Mídias Secundárias ", padding=15)
        frame_pool.pack(fill="both", expand=True)
        
        ttk.Label(
            frame_pool,
            text="Adicione vídeos ou imagens extras para uso durante o processamento",
            font=("Segoe UI", 9),
            foreground="#7f8c8d",
            wraplength=450
        ).pack(anchor="w", pady=(0, 10))
        
        pool_inicial = None
        if self.eh_edicao:
            pool_inicial = self.lote_para_editar.media_pool_data
        else:
            try:
                indice_aba_ativa = self.editor_ui.notebook.index("current")
                pool_aba = self.editor_ui.tabs_data[indice_aba_ativa]['video_controls'].video_selector.pool_manager
                if pool_aba.enabled:
                    pool_inicial = pool_aba.to_dict()
            except Exception:
                pass
        
        self.ui_pool_lotes = PoolLotesUI(frame_pool, initial_pool_data=pool_inicial)
        self.ui_pool_lotes.pack(fill="both", expand=True)

    def _toggle_audio(self):
        """Ativa/desativa os campos de áudio"""
        estado = "normal" if self.var_usar_audio.get() else "disabled"
        self.entry_audio.config(state=estado)
        self.btn_audio.config(state=estado)

    def _criar_rodape(self, pai):
        frame_rodape = ttk.Frame(pai)
        frame_rodape.pack(fill="x", pady=(10, 0))
        
        # Separador visual
        ttk.Separator(frame_rodape, orient="horizontal").pack(fill="x", pady=(0, 15))
        
        # Container de botões
        frame_botoes = ttk.Frame(frame_rodape)
        frame_botoes.pack(fill="x")
        
        # Nota sobre campos obrigatórios (esquerda)
        ttk.Label(
            frame_botoes,
            text="* Campos obrigatórios",
            font=("Segoe UI", 8),
            foreground="#e74c3c"
        ).pack(side="left")
        
        # Botão Cancelar (direita)
        ttk.Button(
            frame_botoes,
            text="✖ Cancelar",
            command=self.destroy,
            width=15
        ).pack(side="right", padx=(5, 0))
        
        # Botão Salvar/Adicionar (direita)
        texto_btn = "💾 Salvar Alterações" if self.eh_edicao else "➕ Adicionar Lote"
        ttk.Button(
            frame_botoes,
            text=texto_btn,
            command=self._acao_salvar,
            style="Accent.TButton",
            width=20
        ).pack(side="right")

    def _acao_salvar(self):
        caminho_entrada = self.var_entrada.get().strip()
        caminho_saida = self.var_saida.get().strip()
        
        if not caminho_entrada or not caminho_saida:
            messagebox.showwarning(
                "Campos Obrigatórios",
                "Por favor, preencha todos os campos marcados com * (asterisco)."
            )
            return
        
        nome = self.var_nome.get().strip() or f"Lote {len(self.gerenciador_lotes.batches) + 1}"
        pasta_audio = self.var_audio.get().strip() if self.var_usar_audio.get() else None
        dados_pool = self.ui_pool_lotes.get_pool_data() if self.ui_pool_lotes.pool_manager.enabled else None
        
        if self.eh_edicao:
            self.gerenciador_lotes.update_batch(
                self.lote_para_editar.id,
                name=nome,
                input_path=caminho_entrada,
                output_folder=caminho_saida,
                audio_folder=pasta_audio,
                media_pool_data=dados_pool
            )
            messagebox.showinfo("✓ Sucesso", "Lote atualizado com sucesso!")
        else:
            self.gerenciador_lotes.add_batch(nome, caminho_entrada, caminho_saida, pasta_audio, dados_pool)
            messagebox.showinfo("✓ Sucesso", "Novo lote adicionado à fila!")
        
        self.destroy()
