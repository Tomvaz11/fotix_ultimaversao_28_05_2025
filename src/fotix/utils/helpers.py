"""
Funções auxiliares genéricas para o Fotix.

Este módulo contém funções auxiliares que podem ser usadas em múltiplas
camadas da aplicação.
"""

import os
from pathlib import Path
from typing import List, Optional


def filter_by_extensions(file_path: str, extensions: Optional[List[str]] = None) -> bool:
    """
    Verifica se um caminho de arquivo tem uma das extensões especificadas.
    
    Args:
        file_path: Caminho do arquivo a ser verificado.
        extensions: Lista de extensões para filtrar (ex: ['.jpg', '.png']).
                   Se None, retorna True para qualquer arquivo.
    
    Returns:
        bool: True se o arquivo tiver uma das extensões especificadas ou se
              extensions for None, False caso contrário.
    """
    if extensions is None:
        return True
    
    # Normalizar extensões para minúsculas e garantir que começam com ponto
    normalized_extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in extensions]
    
    # Obter a extensão do arquivo (em minúsculas)
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    return ext in normalized_extensions


def is_path_valid(path: Path) -> bool:
    """
    Verifica se um caminho é válido e seguro.
    
    Args:
        path: Caminho a ser verificado.
    
    Returns:
        bool: True se o caminho for válido e seguro, False caso contrário.
    """
    try:
        # Verificar se o caminho é absoluto
        if not path.is_absolute():
            return False
        
        # Verificar se o caminho existe
        if not path.exists():
            return False
        
        # Verificar se temos permissão para acessar o caminho
        if not os.access(path, os.R_OK):
            return False
        
        return True
    except (OSError, ValueError):
        return False
