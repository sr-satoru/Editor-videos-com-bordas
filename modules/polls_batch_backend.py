from typing import Dict, Optional
from modules.media_pool_manager import MediaPoolManager

class BatchPoolBackend:
    """
    Gerenciador de backend para os Pools de Mídias em Lotes.
    Cuida da isolação entre os pools configurados nas abas e os pools dos lotes.
    """
    def __init__(self, editor_ui):
        self.editor_ui = editor_ui
        self._original_pools = {} # Armazena pools originais para restauração

    def apply_batch_pool(self, media_pool_data: Optional[Dict]):
        """Aplica o pool de um lote às abas do editor, salvando o estado original antes."""
        if not self.editor_ui:
            return

        # 1. Salvar pool global atual das abas
        self._original_pools['global'] = self.editor_ui.global_tab_pool.to_dict()

        # 2. Aplicar novo pool (se existir)
        # Nota: Lotes aplicam o pool diretamente nas abas para o render_all_tabs_core
        # Mas como agora o render_all_tabs_core pula o pool global se for lote,
        # o BatchQueueManager aplicará os vídeos carregando-os explicitamente.
        if media_pool_data and media_pool_data.get("enabled"):
            print(f"[BatchPoolBackend] Aplicando Pool do Lote às abas (via carregamento explícito)...")
            # O BatchQueueManager já faz o carregamento dos vídeos adequados via apply_batch_to_all_tabs
            # Aqui podemos apenas desabilitar temporariamente o pool global das abas para evitar conflitos
            self.editor_ui.global_tab_pool.enabled = False
        else:
            print(f"[BatchPoolBackend] Lote não possui Pool.")

    def restore_original_pools(self):
        """Restaura o pool global das abas após o processamento do lote."""
        if not self.editor_ui or 'global' not in self._original_pools:
            return

        print(f"[BatchPoolBackend] Restaurando pool global das abas...")
        pool_data = self._original_pools['global']
        from modules.media_pool_manager import MediaPoolManager
        self.editor_ui.global_tab_pool = MediaPoolManager.from_dict(pool_data)
        
        self._original_pools.clear()
