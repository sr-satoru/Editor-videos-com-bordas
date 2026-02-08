import os
import moviepy.editor as mp

def redimensionar_para_9_16(clip, width=1080, height=1920):
    """
    Redimensiona um clipe para 1080x1920, mantendo o aspecto preenchido (crop) ou com faixas pretas.
    Para vídeos de CTA/Mesclagem, o ideal é preencher a tela.
    """
    # Calcula proporções
    target_aspect = width / height
    clip_aspect = clip.w / clip.h
    
    if clip_aspect > target_aspect:
        # Vídeo é mais largo que 9:16 (ex: horizontal) -> Corta as laterais
        new_w = int(clip.h * target_aspect)
        x_center = clip.w / 2
        clip_resized = clip.crop(x1=x_center - new_w/2, y1=0, x2=x_center + new_w/2, y2=clip.h)
    else:
        # Vídeo é mais alto que 9:16 -> Corta topo/baixo
        new_h = int(clip.w / target_aspect)
        y_center = clip.h / 2
        clip_resized = clip.crop(x1=0, y1=y_center - new_h/2, x2=clip.w, y2=y_center + new_h/2)
        
    return clip_resized.resize(newsize=(width, height))

def preparar_video_extra(path, width=1080, height=1920):
    """Carrega e redimensiona um vídeo extra (mesclagem ou CTA)"""
    if not path or not os.path.exists(path):
        return None
        
    try:
        clip = mp.VideoFileClip(path)
        # Se já estiver no tamanho certo, retorna
        if clip.w == width and clip.h == height:
            return clip
            
        return redimensionar_para_9_16(clip, width, height)
    except Exception as e:
        print(f"Erro ao carregar vídeo extra {path}: {e}")
        return None
