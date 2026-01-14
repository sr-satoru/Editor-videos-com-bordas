#!/usr/bin/env python3
"""
Executa o editor de vídeo forçando uso de GPU NVIDIA (CUDA).
"""

import os
os.environ['FORCE_DEVICE'] = 'cuda'

from ui.main_ui import EditorUI

if __name__ == "__main__":
    print("=" * 60)
    print("🎮 Editor de Vídeo - Modo NVIDIA GPU (CUDA)")
    print("=" * 60)
    print()
    
    app = EditorUI()
    app.mainloop()
