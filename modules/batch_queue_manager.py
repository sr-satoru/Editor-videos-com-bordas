import json
import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Callable
from dataclasses import dataclass, asdict
from modules.render_orchestrator import render_orchestrator
from modules.queue_file_manager import queue_file_manager


@dataclass
class Batch:
    """Representa um lote de processamento"""
    id: str
    name: str
    input_path: str
    output_folder: str
    audio_folder: Optional[str] = None
    status: str = "pending"  # pending, processing, completed, error
    error_message: Optional[str] = None
    media_pool_data: Optional[Dict] = None # Dados do pool de mídias
    created_at: str = None
    completed_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


class BatchQueueManager:
    """Gerenciador singleton da fila de lotes"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BatchQueueManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.batches: List[Batch] = []
        self.current_batch_index: int = 0
        self.is_paused: bool = False
        self.is_active: bool = False  # Nunca persistir como True no JSON
        
        # Callbacks
        self.on_status_change: Optional[Callable] = None
        self.on_queue_complete: Optional[Callable] = None
        self.on_queue_switch: Optional[Callable] = None  # Callback para quando fila trocar
        
        # Referência ao EditorUI
        self.editor_ui = None
        self.pool_backend = None # Inicializado em set_editor_ui
        
        self._initialized = True
        self.load_from_file()
    
    @property
    def _STATE_FILE(self) -> str:
        """Retorna caminho do arquivo de fila ativo (dinâmico)"""
        return queue_file_manager.get_current_file_path()
    
    def get_current_queue_name(self) -> str:
        """Retorna nome da fila atualmente ativa"""
        return queue_file_manager.get_current_queue_name()
    
    def switch_to_global(self) -> bool:
        """Volta para fila global"""
        self.save_to_file()  # Salvar fila atual
        queue_file_manager.switch_to_global()
        self.load_from_file()  # Carregar global
        self._notify_status_change()
        if self.on_queue_switch:
            self.on_queue_switch()
        return True
    
    def switch_to_custom(self, queue_name: str) -> bool:
        """Troca para fila personalizada"""
        self.save_to_file()  # Salvar fila atual
        if not queue_file_manager.switch_to_custom(queue_name):
            return False
        self.load_from_file()  # Carregar nova fila
        self._notify_status_change()
        if self.on_queue_switch:
            self.on_queue_switch()
        return True
    
    def switch_from_file_path(self, file_path: str) -> bool:
        """Troca para fila a partir de caminho de arquivo"""
        self.save_to_file()  # Salvar fila atual
        if not queue_file_manager.switch_from_file_path(file_path):
            return False
        self.load_from_file()  # Carregar nova fila
        self._notify_status_change()
        if self.on_queue_switch:
            self.on_queue_switch()
        return True
    
    def create_and_switch_to_queue(self, queue_name: str) -> bool:
        """Cria nova fila e automaticamente troca para ela"""
        if not queue_file_manager.create_queue(queue_name):
            return False
        return self.switch_to_custom(queue_name)
    
    def set_editor_ui(self, editor_ui):
        """Define referência ao EditorUI para poder chamar render_all_tabs()"""
        self.editor_ui = editor_ui
        from modules.polls.poll_lotes.backend import LotesBackend
        self.pool_backend = LotesBackend(editor_ui)
    
    def add_batch(self, name: str, input_path: str, output_folder: str, 
                  audio_folder: Optional[str] = None, 
                  media_pool_data: Optional[Dict] = None) -> Batch:
        """Adiciona um novo lote à fila"""
        batch = Batch(
            id=str(uuid.uuid4()),
            name=name if name else f"Lote {len(self.batches) + 1}",
            input_path=input_path,
            output_folder=output_folder,
            audio_folder=audio_folder,
            media_pool_data=media_pool_data
        )
        self.batches.append(batch)
        self.save_to_file()
        self._notify_status_change()
        return batch
    
    def remove_batch(self, batch_id: str) -> bool:
        """Remove um lote da fila"""
        for i, batch in enumerate(self.batches):
            if batch.id == batch_id:
                self.batches.pop(i)
                self.save_to_file()
                self._notify_status_change()
                return True
        return False

    def update_batch(self, batch_id: str, **kwargs) -> bool:
        """Atualiza campos de um lote existente"""
        for batch in self.batches:
            if batch.id == batch_id:
                for key, value in kwargs.items():
                    if hasattr(batch, key):
                        setattr(batch, key, value)
                self.save_to_file()
                self._notify_status_change()
                return True
        return False
    
    def move_batch(self, batch_id: str, direction: str) -> bool:
        """Move um lote para cima ou para baixo na fila"""
        for i, batch in enumerate(self.batches):
            if batch.id == batch_id:
                if direction == "up" and i > 0:
                    self.batches[i], self.batches[i-1] = self.batches[i-1], self.batches[i]
                    self.save_to_file()
                    self._notify_status_change()
                    return True
                elif direction == "down" and i < len(self.batches) - 1:
                    self.batches[i], self.batches[i+1] = self.batches[i+1], self.batches[i]
                    self.save_to_file()
                    self._notify_status_change()
                    return True
        return False
    
    def clear_queue(self):
        """Limpa todos os lotes da fila"""
        self.batches = []
        self.current_batch_index = 0
        self.is_active = False
        self.is_paused = False
        self.save_to_file()
        self._notify_status_change()
    
    def start_queue(self):
        """Inicia o processamento da fila"""
        if not self.batches:
            print("[BatchQueue] Nenhum lote na fila para processar")
            return False
        
        # Se já está ativa, não faz nada mas também não bloqueia se for um restart limpo
        if self.is_active:
            print("[BatchQueue] Fila já está ativa, reiniciando fluxo...")
            self.is_active = False
            
        self.is_active = True
        self.is_paused = False
        self.current_batch_index = 0
        
        # Sincronizar com orquestrador
        render_orchestrator.set_busy(True)
        
        # Processar primeiro lote
        self._process_current_batch()
        return True
    
    def pause_queue(self):
        """Pausa a fila após o lote atual terminar"""
        self.is_paused = True
        self.save_to_file()
        self._notify_status_change()
        print("[BatchQueue] Fila será pausada após o lote atual")
    
    def resume_queue(self):
        """Retoma o processamento da fila"""
        if not self.is_active:
            print("[BatchQueue] Fila não está ativa")
            return False
        
        self.is_paused = False
        self.save_to_file()
        self._notify_status_change()
        
        # Se tinha pausado, continuar do próximo lote
        if self.current_batch_index < len(self.batches):
            self._process_current_batch()
        
        return True
    
    def stop_queue(self):
        """Para completamente a fila"""
        self.is_active = False
        self.is_paused = False
        
        # Marcar lote atual como pending se estava processing
        if self.current_batch_index < len(self.batches):
            current = self.batches[self.current_batch_index]
            if current.status == "processing":
                current.status = "pending"
        
        self.save_to_file()
        self._notify_status_change()
        
        # Sincronizar com orquestrador
        render_orchestrator.set_busy(False)
        
        # Restaurar pools das abas
        if self.pool_backend:
            self.pool_backend.restore_pools()
            
        print("[BatchQueue] Fila parada")
    
    def on_batch_complete(self, success: bool, error_message: Optional[str] = None):
        """Callback chamado quando todas as abas de um lote terminarem"""
        if not self.is_active or self.current_batch_index >= len(self.batches):
            return
        
        current_batch = self.batches[self.current_batch_index]
        
        # Marcar lote atual como concluído
        if success:
            current_batch.status = "completed"
            current_batch.completed_at = datetime.now().isoformat()
            print(f"[BatchQueue] ✅ Lote '{current_batch.name}' concluído!")
        else:
            current_batch.status = "error"
            current_batch.error_message = error_message
            print(f"[BatchQueue] ❌ Lote '{current_batch.name}' falhou: {error_message}")
        
        self.save_to_file()
        self._notify_status_change()
        
        # Verificar se deve pausar
        if self.is_paused:
            print("[BatchQueue] Fila pausada")
            return
        
        # Avançar para próximo lote
        self.current_batch_index += 1
        
        # Verificar se terminou todos os lotes
        if self.current_batch_index >= len(self.batches):
            print("[BatchQueue] 🎉 Todos os lotes foram processados!")
            
            # Sincronizar com orquestrador
            render_orchestrator.set_busy(False)
            
            self.save_to_file()
            self._notify_status_change()
            
            if self.on_queue_complete:
                # Fila concluída!
                self.stop_queue()
            
            # Enviar notificação
            from modules.notifier import Notifier
            completed = sum(1 for b in self.batches if b.status == "completed")
            errors = sum(1 for b in self.batches if b.status == "error")
            Notifier.notify(
                "Fila de Lotes Concluída",
                f"{completed} lotes processados com sucesso. {errors} erros."
            )
            return
        
        # Processar próximo lote
        self._process_current_batch()
    
    def _process_current_batch(self):
        """Processa o lote atual"""
        if self.current_batch_index >= len(self.batches):
            return
        
        current_batch = self.batches[self.current_batch_index]
        current_batch.status = "processing"
        self.save_to_file()
        self._notify_status_change()
        
        print(f"[BatchQueue] ▶️ Iniciando Lote {self.current_batch_index + 1}/{len(self.batches)}: '{current_batch.name}'")
        
        # Enviar notificação
        from modules.notifier import Notifier
        Notifier.notify(
            f"Lote {self.current_batch_index + 1}/{len(self.batches)}",
            f"Iniciando processamento: {current_batch.name}"
        )
        
        # Aplicar lote em todas as abas e iniciar renderização
        self.apply_batch_to_all_tabs(current_batch)
    
    def apply_batch_to_all_tabs(self, batch: Batch):
        """Aplica vídeo/saída/áudio do lote em todas as abas e inicia renderização"""
        if not self.editor_ui:
            print("[BatchQueue] ERRO: EditorUI não configurado!")
            self.on_batch_complete(False, "EditorUI não configurado")
            return
        
        try:
            # 1. Carregar vídeo base em todas as abas (âncora inicial)
            print(f"[BatchQueue] Carregando vídeo base: {batch.input_path}")
            self.editor_ui.load_video_all_tabs_from_path(batch.input_path)

            # 2. Aplicar Pool do Lote (E salvar originais)
            # O backend vai sobrescrever as abas necessárias (1, 2, 3...) com o pool
            if self.pool_backend:
                self.pool_backend.apply_batch_pool(batch.media_pool_data)
            
            # 2. Mudar pasta de saída em todas as abas
            print(f"[BatchQueue] Mudando pasta de saída: {batch.output_folder}")
            self.editor_ui.change_all_output_path_direct(batch.output_folder)
            
            # 3. Mudar pasta de áudio se especificada
            if batch.audio_folder:
                print(f"[BatchQueue] Mudando pasta de áudio: {batch.audio_folder}")
                self.editor_ui.change_all_audio_folder_direct(batch.audio_folder)
            
            # 4. Iniciar renderização de todas as abas (SEM perguntar sobre lotes novamente)
            print(f"[BatchQueue] Iniciando renderização de todas as abas...")
            self.editor_ui.render_all_tabs_core()
            
        except Exception as e:
            print(f"[BatchQueue] ERRO ao aplicar lote: {e}")
            self.on_batch_complete(False, str(e))
    
    def get_current_batch(self) -> Optional[Batch]:
        """Retorna o lote sendo processado atualmente"""
        if 0 <= self.current_batch_index < len(self.batches):
            return self.batches[self.current_batch_index]
        return None
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas da fila"""
        total = len(self.batches)
        pending = sum(1 for b in self.batches if b.status == "pending")
        processing = sum(1 for b in self.batches if b.status == "processing")
        completed = sum(1 for b in self.batches if b.status == "completed")
        errors = sum(1 for b in self.batches if b.status == "error")
        
        return {
            "total": total,
            "pending": pending,
            "processing": processing,
            "completed": completed,
            "errors": errors,
            "is_active": self.is_active,
            "is_paused": self.is_paused,
            "current_index": self.current_batch_index
        }
    
    def save_to_file(self):
        """Salva estado da fila em arquivo JSON"""
        try:
            state = {
                "batches": [batch.to_dict() for batch in self.batches],
                "current_batch_index": self.current_batch_index,
                "is_paused": self.is_paused,
                "is_active": False  # Sempre salvar como inativo
            }
            
            with open(self._STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            print(f"[BatchQueue] Erro ao salvar estado: {e}")
    
    def load_from_file(self):
        """Carrega estado da fila do arquivo JSON"""
        if not os.path.exists(self._STATE_FILE):
            return
        
        try:
            with open(self._STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            self.batches = [Batch.from_dict(b) for b in state.get("batches", [])]
            self.current_batch_index = state.get("current_batch_index", 0)
            self.is_paused = state.get("is_paused", False)
            self.is_active = state.get("is_active", False)
            
            print(f"[BatchQueue] Estado carregado: {len(self.batches)} lotes")
            
        except Exception as e:
            print(f"[BatchQueue] Erro ao carregar estado: {e}")
    
    def _notify_status_change(self):
        """Notifica mudança de status"""
        if self.on_status_change:
            self.on_status_change()


# Instância singleton global
batch_queue_manager = BatchQueueManager()
