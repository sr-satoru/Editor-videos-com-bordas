#!/usr/bin/env python3
"""
Executa o editor de vídeo com detecção automática de dispositivo.
Use argumentos para forçar um dispositivo específico:
  python run.py --cpu      # Forçar CPU
  python run.py --nvidia   # Forçar GPU NVIDIA (CUDA)
  python run.py --amd      # Forçar GPU AMD (ROCm)
"""

import os
import sys
import argparse

from ui.main_ui import EditorUI

if __name__ == "__main__":
    # Parser de argumentos
    parser = argparse.ArgumentParser(description='Editor Profissional de Vídeo 9:16')
    parser.add_argument('--cpu', action='store_true', help='Forçar uso de CPU')
    parser.add_argument('--nvidia', action='store_true', help='Forçar uso de GPU NVIDIA (CUDA)')
    parser.add_argument('--amd', action='store_true', help='Forçar uso de GPU AMD (ROCm)')
    
    args = parser.parse_args()
    
    # Configurar dispositivo baseado nos argumentos
    device_name = "Detecção automática"
    if args.cpu:
        os.environ['FORCE_DEVICE'] = 'cpu'
        device_name = "CPU"
    elif args.nvidia:
        os.environ['FORCE_DEVICE'] = 'cuda'
        device_name = "NVIDIA GPU (CUDA)"
    elif args.amd:
        os.environ['FORCE_DEVICE'] = 'rocm'
        device_name = "AMD GPU (ROCm)"
    
    print("=" * 60)
    print("🎬 Editor Profissional de Vídeo 9:16")
    print(f"   Modo: {device_name}")
    print("=" * 60)
    print()
    
    app = EditorUI()
    app.mainloop()
