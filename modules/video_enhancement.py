# modules/video_enhancement.py
"""
Módulo de melhoramento de vídeo usando GFPGAN.
Adaptado do face_enhancer.py do projeto Deep-Live-Cam.
"""

from typing import Optional
import cv2
import threading
import os
import platform
import numpy as np

# Variável global para o enhancer
FACE_ENHANCER = None
THREAD_SEMAPHORE = threading.Semaphore()
THREAD_LOCK = threading.Lock()
NAME = "VIDEO-ENHANCEMENT"

# Caminhos
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(SCRIPT_DIR, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "GFPGANv1.4.pth")


def is_available() -> bool:
    """
    Verifica se o GFPGAN está disponível (modelo existe e dependências instaladas).
    """
    try:
        import torch
        import gfpgan
        
        # Verificar se o modelo existe
        if not os.path.exists(MODEL_PATH):
            print(f"{NAME}: Modelo GFPGAN não encontrado em {MODEL_PATH}")
            print(f"{NAME}: Execute 'python setup_gfpgan.py' para baixar o modelo.")
            return False
        
        return True
    except ImportError as e:
        print(f"{NAME}: Dependências não instaladas: {e}")
        print(f"{NAME}: Execute 'pip install -r requirements.txt'")
        return False


def get_device_type() -> str:
    """
    Detecta o tipo de dispositivo disponível.
    Retorna: 'cuda', 'rocm', 'mps', ou 'cpu'
    """
    # Verificar variável de ambiente forçada
    forced_device = os.environ.get('FORCE_DEVICE', '').lower()
    if forced_device in ['cuda', 'rocm', 'mps', 'cpu']:
        print(f"{NAME}: Dispositivo forçado via FORCE_DEVICE: {forced_device}")
        return forced_device
    
    try:
        import torch
        
        # Priority 1: CUDA (NVIDIA)
        if torch.cuda.is_available():
            return 'cuda'
        
        # Priority 2: ROCm (AMD) - verificar se torch foi compilado com ROCm
        if hasattr(torch.version, 'hip') and torch.version.hip is not None:
            return 'rocm'
        
        # Priority 3: MPS (Mac Silicon)
        if platform.system() == "Darwin" and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return 'mps'
        
        # Priority 4: CPU
        return 'cpu'
    
    except ImportError:
        return 'cpu'


def get_enhancer(device_type: str = 'auto') -> Optional[any]:
    """
    Inicializa e retorna a instância do GFPGAN.
    
    Args:
        device_type: 'auto', 'cuda', 'rocm', 'mps', ou 'cpu'
    
    Returns:
        Instância do GFPGANer ou None se falhar
    """
    global FACE_ENHANCER
    
    with THREAD_LOCK:
        if FACE_ENHANCER is None:
            # Verificar disponibilidade
            if not is_available():
                return None
            
            try:
                import torch
                import gfpgan
                
                # Determinar dispositivo
                if device_type == 'auto':
                    device_type = get_device_type()
                
                # Criar dispositivo torch
                if device_type == 'cuda':
                    device = torch.device('cuda')
                    print(f"{NAME}: Usando GPU NVIDIA (CUDA)")
                elif device_type == 'rocm':
                    device = torch.device('cuda')  # ROCm usa 'cuda' como device
                    print(f"{NAME}: Usando GPU AMD (ROCm)")
                elif device_type == 'mps':
                    device = torch.device('mps')
                    print(f"{NAME}: Usando GPU Apple Silicon (MPS)")
                else:
                    device = torch.device('cpu')
                    print(f"{NAME}: Usando CPU")
                
                # Inicializar GFPGAN
                FACE_ENHANCER = gfpgan.GFPGANer(
                    model_path=MODEL_PATH,
                    upscale=1,  # Apenas enhancement, sem upscale
                    arch='clean',
                    channel_multiplier=2,
                    bg_upsampler=None,
                    device=device
                )
                
                print(f"{NAME}: GFPGANer inicializado com sucesso em {device}")
                
            except Exception as e:
                print(f"{NAME}: Erro ao inicializar GFPGANer: {e}")
                
                # Fallback para CPU se falhar com GPU
                if device_type != 'cpu':
                    print(f"{NAME}: Tentando fallback para CPU...")
                    try:
                        import torch
                        import gfpgan
                        
                        device = torch.device('cpu')
                        FACE_ENHANCER = gfpgan.GFPGANer(
                            model_path=MODEL_PATH,
                            upscale=1,
                            arch='clean',
                            channel_multiplier=2,
                            bg_upsampler=None,
                            device=device
                        )
                        print(f"{NAME}: GFPGANer inicializado em CPU após fallback")
                    except Exception as fallback_e:
                        print(f"{NAME}: FATAL: Falha no fallback para CPU: {fallback_e}")
                        FACE_ENHANCER = None
                else:
                    FACE_ENHANCER = None
    
    return FACE_ENHANCER


def enhance_frame(frame: np.ndarray) -> np.ndarray:
    """
    Melhora a qualidade de um frame usando GFPGAN.
    
    Args:
        frame: Frame numpy array (BGR)
    
    Returns:
        Frame melhorado ou original se falhar
    """
    # Obter enhancer
    enhancer = get_enhancer()
    
    if enhancer is None:
        # Se não disponível, retornar frame original
        return frame
    
    try:
        with THREAD_SEMAPHORE:
            # GFPGAN enhance retorna: (_, restored_faces, restored_img)
            _, _, restored_img = enhancer.enhance(
                frame,
                has_aligned=False,      # Faces não estão pré-alinhadas
                only_center_face=False, # Melhorar todas as faces detectadas
                paste_back=True         # Colar faces melhoradas de volta
            )
        
        # Se retornar None, usar frame original
        if restored_img is None:
            return frame
        
        return restored_img
    
    except Exception as e:
        print(f"{NAME}: Erro durante enhancement: {e}")
        return frame


def reset_enhancer():
    """
    Reseta o enhancer global (útil para trocar de dispositivo).
    """
    global FACE_ENHANCER
    with THREAD_LOCK:
        FACE_ENHANCER = None
    print(f"{NAME}: Enhancer resetado")
