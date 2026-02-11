#!/usr/bin/env python3
"""
Módulo para converter imagens em vídeos.
Permite transformar pastas de imagens em vídeos prontos para processamento com legendas.
"""

import os
from pathlib import Path
from typing import Optional, List, Tuple
import cv2
from moviepy.editor import ImageClip
from modules.config_global import global_config


# Extensões de imagem suportadas
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tiff', '.tif'}


def is_image_file(filepath: str) -> bool:
    """
    Verifica se um arquivo é uma imagem suportada.
    
    Args:
        filepath: Caminho do arquivo a verificar
        
    Returns:
        True se for imagem, False caso contrário
    """
    ext = Path(filepath).suffix.lower()
    return ext in IMAGE_EXTENSIONS


def get_image_dimensions(image_path: str) -> Tuple[int, int]:
    """
    Obtém as dimensões de uma imagem.
    
    Args:
        image_path: Caminho da imagem
        
    Returns:
        Tupla (largura, altura)
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Não foi possível carregar a imagem: {image_path}")
    height, width = img.shape[:2]
    return width, height


def convert_image_to_video(
    image_path: str,
    duration: Optional[float] = None,
    output_path: Optional[str] = None,
    fps: int = 30
) -> str:
    """
    Converte uma imagem em vídeo com duração especificada.
    
    Args:
        image_path: Caminho da imagem de entrada
        duration: Duração do vídeo em segundos (None usa config global)
        output_path: Caminho do vídeo de saída (None gera automaticamente)
        fps: Frames por segundo do vídeo
        
    Returns:
        Caminho do vídeo criado
        
    Raises:
        ValueError: Se a imagem não puder ser carregada
        FileNotFoundError: Se o arquivo de imagem não existir
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Imagem não encontrada: {image_path}")
    
    if not is_image_file(image_path):
        raise ValueError(f"Arquivo não é uma imagem suportada: {image_path}")
    
    # Usar duração da configuração global se não especificada
    if duration is None:
        duration = global_config.get("image_to_video_duration")
    
    # Gerar caminho de saída se não especificado
    if output_path is None:
        input_path = Path(image_path)
        output_path = str(input_path.parent / f"{input_path.stem}_video.mp4")
    
    print(f"Convertendo imagem → vídeo: {image_path}")
    print(f"  Duração: {duration}s | FPS: {fps}")
    
    try:
        # Criar clip de imagem com duração
        clip = ImageClip(image_path, duration=duration)
        
        # Escrever vídeo
        clip.write_videofile(
            output_path,
            fps=fps,
            codec='libx264',
            audio=False,
            verbose=False,
            logger=None
        )
        
        clip.close()
        
        print(f"✓ Vídeo criado: {output_path}")
        return output_path
        
    except Exception as e:
        raise RuntimeError(f"Erro ao converter imagem em vídeo: {e}")


def convert_images_folder(
    folder_path: str,
    duration: Optional[float] = None,
    output_folder: Optional[str] = None,
    recursive: bool = False
) -> List[str]:
    """
    Converte todas as imagens de uma pasta em vídeos.
    
    Args:
        folder_path: Pasta contendo imagens
        duration: Duração de cada vídeo em segundos (None usa config global)
        output_folder: Pasta para salvar vídeos (None usa mesma pasta)
        recursive: Se True, processa subpastas recursivamente
        
    Returns:
        Lista de caminhos dos vídeos criados
    """
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"Pasta não encontrada: {folder_path}")
    
    folder_path = Path(folder_path)
    
    # Definir pasta de saída
    if output_folder is None:
        output_folder = folder_path / "videos_convertidos"
    else:
        output_folder = Path(output_folder)
    
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Encontrar todas as imagens
    if recursive:
        image_files = [
            f for f in folder_path.rglob('*')
            if f.is_file() and is_image_file(str(f))
        ]
    else:
        image_files = [
            f for f in folder_path.iterdir()
            if f.is_file() and is_image_file(str(f))
        ]
    
    if not image_files:
        print(f"⚠ Nenhuma imagem encontrada em: {folder_path}")
        return []
    
    print(f"\n{'='*60}")
    print(f"📸 Conversão em Lote: {len(image_files)} imagens")
    print(f"{'='*60}\n")
    
    converted_videos = []
    
    for idx, image_file in enumerate(image_files, 1):
        try:
            # Gerar nome do vídeo de saída
            output_name = f"{image_file.stem}.mp4"
            output_path = output_folder / output_name
            
            print(f"[{idx}/{len(image_files)}] {image_file.name}")
            
            video_path = convert_image_to_video(
                str(image_file),
                duration=duration,
                output_path=str(output_path)
            )
            
            converted_videos.append(video_path)
            
        except Exception as e:
            print(f"✗ Erro ao processar {image_file.name}: {e}")
            continue
    
    print(f"\n{'='*60}")
    print(f"✓ Conversão concluída: {len(converted_videos)}/{len(image_files)} vídeos")
    print(f"📁 Pasta de saída: {output_folder}")
    print(f"{'='*60}\n")
    
    return converted_videos


def auto_convert_if_image(input_path: str) -> str:
    """
    Converte automaticamente para vídeo se o input for uma imagem.
    Caso contrário, retorna o caminho original.
    
    Args:
        input_path: Caminho do arquivo de entrada
        
    Returns:
        Caminho do vídeo (convertido ou original)
    """
    if is_image_file(input_path):
        print(f"🔄 Imagem detectada, convertendo para vídeo...")
        return convert_image_to_video(input_path)
    return input_path


if __name__ == "__main__":
    # Exemplo de uso
    import sys
    
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python process_image.py <imagem.png>")
        print("  python process_image.py <pasta_imagens>")
        sys.exit(1)
    
    target = sys.argv[1]
    
    if os.path.isfile(target):
        # Converter imagem única
        output = convert_image_to_video(target)
        print(f"\n✓ Vídeo salvo em: {output}")
    elif os.path.isdir(target):
        # Converter pasta
        videos = convert_images_folder(target)
        print(f"\n✓ {len(videos)} vídeos criados")
    else:
        print(f"✗ Arquivo ou pasta não encontrado: {target}")
        sys.exit(1)
