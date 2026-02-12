"""
Executor Global Compartilhado para Renderização Paralela

Este módulo centraliza o pool de workers para garantir que múltiplas abas
possam processar seus vídeos simultaneamente, respeitando o limite de parallel_jobs.
"""
import threading
from concurrent.futures import ThreadPoolExecutor
from modules.config_global import global_config


class GlobalRenderExecutor:
    """
    Singleton que gerencia um ThreadPoolExecutor compartilhado por toda a aplicação.
    
    Isso permite que múltiplas abas submetam seus vídeos para renderização simultânea,
    respeitando o limite global de parallel_jobs configurado pelo usuário.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._executor = None
        self._executor_lock = threading.Lock()
        self._initialized = True
    
    def get_executor(self) -> ThreadPoolExecutor:
        """
        Retorna o executor global, criando-o se necessário.
        O número de workers é definido por parallel_jobs do global_config.
        """
        if self._executor is None:
            with self._executor_lock:
                if self._executor is None:
                    max_workers = global_config.get("parallel_jobs")
                    print(f"[GlobalExecutor] Criando pool com {max_workers} workers")
                    self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="RenderWorker")
        
        return self._executor
    
    def reset_executor(self):
        """
        Reseta o executor, forçando a criação de um novo pool na próxima renderização.
        Útil quando o usuário muda parallel_jobs nas configurações.
        """
        if self._executor is not None:
            with self._executor_lock:
                if self._executor is not None:
                    print("[GlobalExecutor] Resetando pool para aplicar novas configurações")
                    self._executor.shutdown(wait=False)  # Não espera jobs pendentes terminarem
                    self._executor = None
    
    def shutdown(self, wait=True):
        """Encerra o executor global"""
        if self._executor is not None:
            with self._executor_lock:
                if self._executor is not None:
                    print("[GlobalExecutor] Encerrando pool de workers")
                    self._executor.shutdown(wait=wait)
                    self._executor = None


# Instância singleton global
global_executor = GlobalRenderExecutor()
