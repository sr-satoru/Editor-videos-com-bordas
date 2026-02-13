import os
from typing import List, Optional

class MediaPoolManager:
    """
    Gerencia um pool de mídias (vídeos/imagens) para serem distribuídos
    entre diferentes abas ou processos de forma sequencial.
    """
    def __init__(self):
        self.primary_video: Optional[str] = None
        self.secondary_videos: List[str] = []
        self.enabled: bool = False

    def add_primary(self, path: str):
        """Define o vídeo principal do pool"""
        if path and os.path.exists(path):
            self.primary_video = path
            self.enabled = True

    def add_secondary(self, path: str):
        """Adiciona um vídeo secundário ao pool"""
        if path and os.path.exists(path) and path not in self.secondary_videos:
            if path != self.primary_video:
                self.secondary_videos.append(path)
                self.enabled = True

    def remove_secondary(self, path: str):
        """Remove um vídeo secundário do pool"""
        if path in self.secondary_videos:
            self.secondary_videos.remove(path)
        
        if not self.primary_video and not self.secondary_videos:
            self.enabled = False

    def clear(self):
        """Limpa todo o pool"""
        self.primary_video = None
        self.secondary_videos = []
        self.enabled = False

    def get_full_pool(self) -> List[str]:
        """Retorna a lista completa de vídeos (Principal + Secundários)"""
        pool = []
        if self.primary_video:
            pool.append(self.primary_video)
        pool.extend(self.secondary_videos)
        return pool

    def get_video_for_index(self, index: int) -> Optional[str]:
        """
        Retorna um vídeo do pool baseado no índice informado.
        A distribuição é sequencial usando o operador módulo.
        """
        pool = self.get_full_pool()
        if not pool:
            return None
        
        # Algoritmo Sequencial: index % tamanho_do_pool
        target_index = index % len(pool)
        return pool[target_index]

    def to_dict(self) -> dict:
        """Serializa o estado para JSON"""
        return {
            "enabled": self.enabled,
            "primary_video": self.primary_video,
            "secondary_videos": self.secondary_videos
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Cria uma instância a partir de um dicionário"""
        instance = cls()
        instance.enabled = data.get("enabled", False)
        instance.primary_video = data.get("primary_video")
        instance.secondary_videos = data.get("secondary_videos", [])
        return instance
