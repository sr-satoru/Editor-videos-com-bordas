from typing import Optional, Dict, Any
from modules.polls.utils.selectors import Selector

class LotesBackend:
    """
    Sistema de gerenciamento de pools para Lotes (Batches).
    Garante isolamento entre o pool do lote e o pool global das abas.
    """
    def __init__(self, editor_ui: Any):
        self.editor_ui = editor_ui
        self._original_pools = {} # Armazena estado original para restauração

    def apply_batch_pool(self, batch_pool_data: Optional[Dict]):
        """
        Salva o pool global atual e aplica o pool do lote.
        """
        if not self.editor_ui:
            return

        # 1. Salvar pool global atual das abas
        if hasattr(self.editor_ui, 'global_tab_pool'):
            self._original_pools['global'] = self.editor_ui.global_tab_pool.to_dict()

        # 2. Desabilitar pool global durante o lote para evitar conflitos
        if batch_pool_data and batch_pool_data.get("enabled"):
            print(f"[LotesBackend] Aplicando Pool do Lote. Pool Global temporariamente desativado.")
            self.editor_ui.global_tab_pool.enabled = False
            
            # 3. Distribuir mídias secundárias do lote entre as abas (mantendo a aba 0 como o vídeo base)
            secondary_videos = batch_pool_data.get("secondary_videos", [])
            if secondary_videos:
                print(f"[LotesBackend] Distribuindo {len(secondary_videos)} mídias secundárias do lote...")
                for i, tab in enumerate(self.editor_ui.tabs_data):
                    # Pular a primeira aba (i=0), que mantém o vídeo carregado pelo BatchQueue (input_path)
                    if i == 0:
                        continue
                        
                    # Obter vídeo sequencial do pool de secundários
                    video_path = Selector.get_sequential(secondary_videos, i - 1)
                    if video_path:
                        tab['video_controls'].video_selector.load_video(video_path)
                        if 'subtitles' in tab:
                            tab['subtitles'].update_preview()
        else:
            print(f"[LotesBackend] Lote sem pool específico.")

    def restore_pools(self):
        """
        Restaura o pool global das abas após o lote.
        """
        if not self.editor_ui or 'global' not in self._original_pools:
            return

        print(f"[LotesBackend] Restaurando pool global das abas...")
        pool_data = self._original_pools['global']
        
        # Como o MediaPoolManager é a estrutura de dados, 
        # precisamos garantir que ele seja importado corretamente.
        from modules.polls.manager import MediaPoolManager
        self.editor_ui.global_tab_pool = MediaPoolManager.from_dict(pool_data)
        
        self._original_pools.clear()
