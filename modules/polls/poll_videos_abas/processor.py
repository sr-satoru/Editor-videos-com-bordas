from typing import Any
from modules.polls.utils.selectors import Selector

class AbasProcessor:
    """
    Sistema de processamento de pools para as abas do Editor.
    """
    def __init__(self, editor_ui: Any):
        self.editor_ui = editor_ui

    def distribute_global_pool(self):
        """
        Distribui o pool global entre as abas abertas.
        Seguindo a regra: [Vídeo da Aba] + [Vídeos Secundários do Pool].
        """
        if not self.editor_ui or not hasattr(self.editor_ui, 'global_tab_pool'):
            return

        pool_mgr = self.editor_ui.global_tab_pool
        if not pool_mgr.enabled:
            return

        print(f"[AbasProcessor] Distribuindo pool global entre {len(self.editor_ui.tabs_data)} abas...")
        
        # Obter lista de secundários (o primário é a própria aba)
        secondary_pool = pool_mgr.secondary_videos
        
        for i, tab in enumerate(self.editor_ui.tabs_data):
            # Para a primeira aba (i=0), mantemos o vídeo carregado nela?
            # O usuário disse: "o primmario e oque ta ma aba"
            # Então para i=0 -> Vídeo da aba.
            # Para i > 0 -> Secundários do pool.
            
            if i == 0:
                # Primeira aba mantém seu vídeo original como "âncora"
                continue
            
            # Para as demais abas, pegamos do pool de secundários
            if secondary_pool:
                # i-1 para ajustar o índice já que a aba 0 é a âncora
                video_path = Selector.get_sequential(secondary_pool, i - 1)
                if video_path:
                    tab['video_controls'].video_selector.load_video(video_path)
                    if 'subtitles' in tab:
                        tab['subtitles'].update_preview()
