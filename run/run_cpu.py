#!/usr/bin/env python3
"""
Executa o editor de vídeo forçando uso de CPU.
"""

import os
os.environ['FORCE_DEVICE'] = 'cpu'

from ui.main_ui import EditorUI

if __name__ == "__main__":
    print("=" * 60)
    print("🖥️  Editor de Vídeo - Modo CPU")
    print("=" * 60)
    print()
    
    app = EditorUI()
    app.mainloop()
