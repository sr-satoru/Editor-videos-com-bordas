"""
Módulo para extração e validação de estilos de legendas.
Centraliza a lógica de captura de cores e configurações do UI.
"""

def extrair_estilo_legenda(componente_estilo):
    """
    Extrai o estilo completo do componente de UI.
    
    Args:
        componente_estilo: Instância de ComponenteEstiloLegenda
        
    Returns:
        dict: Dicionário com todas as configurações de estilo
    """
    estilo = componente_estilo.get_estilo()
    
    # Validar e normalizar valores
    border_thickness = estilo.get('border_thickness', 2)
    border_color = estilo.get('border', '#000000')
    
    # Se espessura é 0, não aplicar borda
    if border_thickness == 0:
        border_color = None
    
    return {
        'font': estilo.get('font', 'Arial Black'),
        'size': estilo.get('size', 18),
        'color': estilo.get('color', '#FFFFFF'),
        'border': border_color,
        'bg': estilo.get('bg', ''),
        'border_thickness': border_thickness
    }


def validar_cor(cor):
    """
    Valida se uma cor está no formato correto.
    
    Args:
        cor: String com a cor em formato hexadecimal
        
    Returns:
        bool: True se a cor é válida
    """
    if not cor:
        return False
    
    if not isinstance(cor, str):
        return False
    
    # Verificar formato hexadecimal
    if cor.startswith('#'):
        cor = cor[1:]
    
    if len(cor) not in [3, 6]:
        return False
    
    try:
        int(cor, 16)
        return True
    except ValueError:
        return False


def aplicar_estilo_legenda(subtitle_data, estilo):
    """
    Aplica um estilo a um dicionário de legenda.
    
    Args:
        subtitle_data: Dicionário com dados da legenda
        estilo: Dicionário com configurações de estilo
        
    Returns:
        dict: Legenda atualizada com o estilo aplicado
    """
    subtitle_data.update({
        'font': estilo.get('font', subtitle_data.get('font', 'Arial Black')),
        'size': estilo.get('size', subtitle_data.get('size', 18)),
        'color': estilo.get('color', subtitle_data.get('color', '#FFFFFF')),
        'border': estilo.get('border', subtitle_data.get('border', '#000000')),
        'bg': estilo.get('bg', subtitle_data.get('bg', '')),
        'border_thickness': estilo.get('border_thickness', subtitle_data.get('border_thickness', 2))
    })
    
    return subtitle_data
