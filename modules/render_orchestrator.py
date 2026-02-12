import tkinter as tk
from tkinter import messagebox
from typing import Optional

class RenderOrchestrator:
    """
    Orquestrador de fluxo de renderização.
    Gere o ciclo de vida desde o clique no botão até o processamento dos lotes.
    """
    _instance: Optional['RenderOrchestrator'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RenderOrchestrator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.is_active = False  # Indica se há renderização técnica em curso (abas ou lotes)
        self.pending_batch_start = False  # Indica se a fila de lotes deve iniciar após as abas atuais
        self._initialized = True

    def start_render_flow(self, editor_ui):
        """
        Gatilho acionado pelo botão 'Renderizar Tudo'.
        Gerencia o estado ocupado e pergunta sobre lotes.
        """
        if self.is_active:
            messagebox.showwarning(
                "Sistema Ocupado",
                "Já existe uma renderização ou processamento de lotes em curso.\n"
                "Aguarde a conclusão antes de iniciar um novo serviço."
            )
            return

        from modules.batch_queue_manager import batch_queue_manager
        
        # Resetar flags de controle
        self.pending_batch_start = False
        
        # 1. Verificar se há lotes configurados
        if batch_queue_manager.batches:
            resposta = messagebox.askyesno(
                "Processar com Lotes?",
                f"Você tem {len(batch_queue_manager.batches)} lote(s) configurado(s).\n\n"
                f"Deseja processar com os lotes automaticamente após as abas atuais?\n\n"
                f"• SIM: Renderiza abas atuais e DEPOIS inicia a fila de lotes\n"
                f"• NÃO: Renderiza apenas as abas atuais"
            )
            
            if resposta:
                self.pending_batch_start = True
                print("[Orchestrator] Fila de lotes agendada para após renderização atual.")

        # 2. Iniciar renderização das abas atuais
        self.is_active = True
        print("[Orchestrator] Iniciando renderização das abas atuais.")
        editor_ui.render_all_tabs_core()

    def on_all_tabs_finished(self, editor_ui):
        """
        Callback chamado quando TODAS as abas atuais terminam de renderizar.
        """
        print("[Orchestrator] Todas as abas atuais foram processadas.")
        
        from modules.batch_queue_manager import batch_queue_manager

        # Caso 1: Havíamos agendado o início dos lotes
        if self.pending_batch_start:
            print("[Orchestrator] Iniciando Processamento de Lote 1 (fluxo automático)...")
            self.pending_batch_start = False
            
            # Chama o início oficial da fila. O manager cuidará de resetar seu próprio estado.
            if not batch_queue_manager.start_queue():
                print("[Orchestrator] Erro ao iniciar fila de lotes.")
                self.is_active = False
            return

        # Caso 2: Já estávamos em uma fila de lotes ativa
        if batch_queue_manager.is_active:
            print("[Orchestrator] Notificando conclusão de ciclo ao BatchQueueManager.")
            batch_queue_manager.on_batch_complete(success=True)
            return
            
        # Caso 3: Renderização manual simples terminou
        self.is_active = False
        print("[Orchestrator] Renderização manual concluída. Sistema livre.")

    def set_busy(self, busy: bool):
        """Define explicitamente se o sistema está ocupado (usado pelo BatchQueueManager)"""
        self.is_active = busy
        if not busy:
            print("[Orchestrator] Sistema liberado.")

render_orchestrator = RenderOrchestrator()
