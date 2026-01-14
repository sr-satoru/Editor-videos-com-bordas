#!/usr/bin/env python3
"""
Executa o editor de vídeo forçando uso de GPU AMD (ROCm).
"""

import os
os.environ['FORCE_DEVICE'] = 'rocm'

from ui.main_ui import EditorUI

if __name__ == "__main__":
    print("=" * 60)
    print("🔴 Editor de Vídeo - Modo AMD GPU (ROCm)")
    print("=" * 60)
    print()
    
    app = EditorUI()
    app.mainloop()
