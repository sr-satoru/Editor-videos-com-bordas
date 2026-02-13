"""
Módulo para gerenciamento de múltiplas filas de lotes.

Sistema:
- Global: batch_queue_state.json (na raiz)
- Personalizadas: batch_queues/{nome}.json
"""

import os
import json
from typing import List


class QueueFileManager:
    """Gerenciador simples de arquivos de fila"""
    
    QUEUES_DIR = "batch_queues"
    GLOBAL_FILE = "batch_queue_state.json"  # Arquivo global na raiz
    
    def __init__(self):
        self._current_file_path: str = self.GLOBAL_FILE
        self._ensure_structure()
    
    def _ensure_structure(self):
        """Garante que a pasta batch_queues/ existe"""
        os.makedirs(self.QUEUES_DIR, exist_ok=True)
    
    def _create_empty_queue_file(self, file_path: str):
        """Cria um arquivo de fila vazio"""
        empty_state = {
            "batches": [],
            "current_batch_index": 0,
            "is_paused": False,
            "is_active": False
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(empty_state, f, indent=2, ensure_ascii=False)
    
    def get_current_file_path(self) -> str:
        """Retorna caminho do arquivo de fila ativo"""
        return self._current_file_path
    
    def get_current_queue_name(self) -> str:
        """Retorna nome amigável da fila ativa"""
        if self._current_file_path == self.GLOBAL_FILE:
            return "global"
        
        # Extrair nome do arquivo
        filename = os.path.basename(self._current_file_path)
        return filename.replace('.json', '')
    
    def list_custom_queues(self) -> List[str]:
        """Lista apenas as filas personalizadas (em batch_queues/)"""
        if not os.path.exists(self.QUEUES_DIR):
            return []
        
        queues = []
        for filename in os.listdir(self.QUEUES_DIR):
            if filename.endswith('.json') and not filename.startswith('.'):
                queue_name = filename[:-5]  # Remove .json
                queues.append(queue_name)
        
        return sorted(queues)
    
    def create_queue(self, queue_name: str) -> bool:
        """
        Cria nova fila personalizada
        
        Returns:
            True se criado com sucesso
        """
        # Sanitizar nome
        queue_name = self._sanitize_name(queue_name)
        
        file_path = os.path.join(self.QUEUES_DIR, f"{queue_name}.json")
        
        # Verificar se já existe
        if os.path.exists(file_path):
            print(f"[QueueFileManager] ⚠️ Fila '{queue_name}' já existe")
            return False
        
        # Criar arquivo vazio
        try:
            self._create_empty_queue_file(file_path)
            print(f"[QueueFileManager] ✅ Fila '{queue_name}' criada: {file_path}")
            return True
        except Exception as e:
            print(f"[QueueFileManager] ❌ Erro ao criar fila: {e}")
            return False
    
    def switch_to_global(self) -> bool:
        """Volta para a fila global"""
        self._current_file_path = self.GLOBAL_FILE
        print(f"[QueueFileManager] 🔄 Fila trocada para: global")
        return True
    
    def switch_to_custom(self, queue_name: str) -> bool:
        """
        Troca para fila personalizada
        
        Args:
            queue_name: Nome da fila (sem .json)
        """
        file_path = os.path.join(self.QUEUES_DIR, f"{queue_name}.json")
        
        if not os.path.exists(file_path):
            print(f"[QueueFileManager] ❌ Fila '{queue_name}' não encontrada")
            return False
        
        self._current_file_path = file_path
        print(f"[QueueFileManager] 🔄 Fila trocada para: {queue_name}")
        return True
    
    def switch_from_file_path(self, file_path: str) -> bool:
        """
        Troca para fila a partir de um caminho completo
        
        Args:
            file_path: Caminho completo do .json
        """
        if not os.path.exists(file_path):
            print(f"[QueueFileManager] ❌ Arquivo não encontrado: {file_path}")
            return False
        
        if not file_path.endswith('.json'):
            print(f"[QueueFileManager] ❌ Arquivo inválido (não é .json)")
            return False
        
        self._current_file_path = file_path
        queue_name = self.get_current_queue_name()
        print(f"[QueueFileManager] 🔄 Fila trocada para: {queue_name}")
        return True
    
    def _sanitize_name(self, name: str) -> str:
        """Remove caracteres inválidos do nome"""
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_\-]', '_', name)
        return sanitized.lower()


# Instância singleton global
queue_file_manager = QueueFileManager()
