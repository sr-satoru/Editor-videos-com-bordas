import random
from typing import List, Optional

class Selector:
    """
    Utilitários para seleção de mídias em um pool.
    """
    
    @staticmethod
    def get_sequential(pool: List[str], index: int) -> Optional[str]:
        """
        Retorna um item de forma sequencial usando o operador módulo.
        """
        if not pool:
            return None
        return pool[index % len(pool)]

    @staticmethod
    def get_random(pool: List[str]) -> Optional[str]:
        """
        Retorna um item aleatório da lista.
        """
        if not pool:
            return None
        return random.choice(pool)
