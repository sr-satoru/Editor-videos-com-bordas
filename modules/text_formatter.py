"""
Módulo para formatação de texto em legendas.
Gerencia alinhamento (esquerda, centro, direita) e estilo itálico.
"""

import platform
import os
from PIL import ImageFont


class TextFormatter:
    """Gerenciador de formatação de texto para legendas"""
    
    # Constantes para alinhamento
    ALIGN_LEFT = 'left'
    ALIGN_CENTER = 'center'
    ALIGN_RIGHT = 'right'
    
    # Mapeamento de fontes itálicas para Windows
    ITALIC_FONTS_WINDOWS = {
        "Arial Black": "ariblk.ttf",  # Arial Black não tem itálico, usa bold
        "Arial": "ariali.ttf",
        "Helvetica": "ariali.ttf",
        "Times": "timesi.ttf",
        "Courier": "couri.ttf",
        "Verdana": "verdanai.ttf",
        "Impact": "impact.ttf",  # Impact não tem itálico
        "Comic Sans MS": "comici.ttf"
    }
    
    # Mapeamento de fontes itálicas para Linux
    ITALIC_FONTS_LINUX = {
        "Arial Black": "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf",
        "Arial": "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
        "Helvetica": "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
        "Times": "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
        "Courier": "/usr/share/fonts/truetype/liberation/LiberationMono-Italic.ttf",
        "Verdana": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        "Impact": "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
        "Comic Sans MS": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"
    }
    
    # Mapeamento de fontes normais para Windows
    NORMAL_FONTS_WINDOWS = {
        "Arial Black": "ariblk.ttf",
        "Arial": "arial.ttf",
        "Helvetica": "arial.ttf",
        "Times": "times.ttf",
        "Courier": "cour.ttf",
        "Verdana": "verdana.ttf",
        "Impact": "impact.ttf",
        "Comic Sans MS": "comic.ttf"
    }
    
    # Mapeamento de fontes normais para Linux
    NORMAL_FONTS_LINUX = {
        "Arial Black": "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "Arial": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "Helvetica": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "Times": "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "Courier": "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "Verdana": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "Impact": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "Comic Sans MS": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    }
    
    @staticmethod
    def get_font(font_family, size, italic=False):
        """
        Carrega a fonte correta baseada no sistema operacional e estilo.
        
        Args:
            font_family: Nome da família da fonte
            size: Tamanho da fonte
            italic: Se True, carrega versão itálica
            
        Returns:
            ImageFont: Objeto de fonte PIL
        """
        system = platform.system()
        
        try:
            if system == "Windows":
                if italic:
                    font_name = TextFormatter.ITALIC_FONTS_WINDOWS.get(font_family, "ariali.ttf")
                else:
                    font_name = TextFormatter.NORMAL_FONTS_WINDOWS.get(font_family, "arial.ttf")
                font_path = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', font_name)
            else:  # Linux
                if italic:
                    font_path = TextFormatter.ITALIC_FONTS_LINUX.get(
                        font_family, 
                        "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"
                    )
                else:
                    font_path = TextFormatter.NORMAL_FONTS_LINUX.get(
                        font_family, 
                        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
                    )
            
            return ImageFont.truetype(font_path, size)
        except Exception as e:
            print(f"Erro ao carregar fonte {font_family} (italic={italic}): {e}")
            return ImageFont.load_default()
    
    @staticmethod
    def calculate_text_position(x, width, align):
        """
        Calcula a posição inicial X do texto baseado no alinhamento.
        
        Args:
            x: Posição X central de referência
            width: Largura do texto
            align: Tipo de alinhamento ('left', 'center', 'right')
            
        Returns:
            int: Posição X ajustada
        """
        if align == TextFormatter.ALIGN_LEFT:
            # Texto começa no ponto X (alinhado à esquerda)
            return x
        elif align == TextFormatter.ALIGN_RIGHT:
            # Texto termina no ponto X (alinhado à direita)
            return x - width
        else:  # ALIGN_CENTER (padrão)
            # Texto centralizado no ponto X
            return x - width // 2
    
    @staticmethod
    def get_anchor_mode(align):
        """
        Retorna o modo de ancoragem PIL baseado no alinhamento.
        
        Args:
            align: Tipo de alinhamento ('left', 'center', 'right')
            
        Returns:
            str: Código de ancoragem PIL ('lm', 'mm', 'rm')
        """
        if align == TextFormatter.ALIGN_LEFT:
            return 'lm'  # left-middle
        elif align == TextFormatter.ALIGN_RIGHT:
            return 'rm'  # right-middle
        else:  # ALIGN_CENTER
            return 'mm'  # middle-middle
    
    @staticmethod
    def validate_alignment(align):
        """
        Valida se o alinhamento é válido.
        
        Args:
            align: Alinhamento a validar
            
        Returns:
            str: Alinhamento válido (retorna 'center' se inválido)
        """
        valid_alignments = [TextFormatter.ALIGN_LEFT, TextFormatter.ALIGN_CENTER, TextFormatter.ALIGN_RIGHT]
        return align if align in valid_alignments else TextFormatter.ALIGN_CENTER
