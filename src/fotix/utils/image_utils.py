"""
Utilitários para processamento de imagens no Fotix.

Este módulo contém funções para extrair informações de imagens,
como resolução, e verificar tipos de arquivo de imagem.
"""

import io
from pathlib import Path
from typing import Optional, Tuple, Callable, Iterable

from PIL import Image, UnidentifiedImageError

from fotix.infrastructure.logging_config import get_logger

# Obter logger para este módulo
logger = get_logger(__name__)

# Lista de extensões de arquivo de imagem comuns
IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp'
}


def is_image_file(file_path: Path) -> bool:
    """
    Verifica se um arquivo é uma imagem com base na extensão.
    
    Args:
        file_path: Caminho para o arquivo.
    
    Returns:
        bool: True se o arquivo tiver uma extensão de imagem conhecida, False caso contrário.
    """
    return file_path.suffix.lower() in IMAGE_EXTENSIONS


def get_image_resolution(file_path: Path) -> Optional[Tuple[int, int]]:
    """
    Obtém a resolução de uma imagem.
    
    Args:
        file_path: Caminho para o arquivo de imagem.
    
    Returns:
        Optional[Tuple[int, int]]: Tupla (largura, altura) ou None se não for possível obter a resolução.
    """
    if not is_image_file(file_path):
        logger.debug(f"Arquivo não é uma imagem: {file_path}")
        return None
    
    try:
        with Image.open(file_path) as img:
            resolution = img.size  # (width, height)
            logger.debug(f"Resolução da imagem {file_path}: {resolution}")
            return resolution
    except (UnidentifiedImageError, FileNotFoundError, PermissionError) as e:
        logger.warning(f"Não foi possível abrir a imagem {file_path}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Erro ao processar a imagem {file_path}: {str(e)}")
        return None


def get_image_resolution_from_bytes(content_provider: Callable[[], Iterable[bytes]]) -> Optional[Tuple[int, int]]:
    """
    Obtém a resolução de uma imagem a partir de um provedor de conteúdo em bytes.
    
    Útil para arquivos dentro de ZIPs ou outros contêineres.
    
    Args:
        content_provider: Função que retorna um iterador/gerador para o conteúdo do arquivo em blocos.
    
    Returns:
        Optional[Tuple[int, int]]: Tupla (largura, altura) ou None se não for possível obter a resolução.
    """
    try:
        # Consumir o conteúdo do provedor
        content_chunks = list(content_provider())
        content = b''.join(content_chunks)
        
        # Abrir a imagem a partir dos bytes
        with Image.open(io.BytesIO(content)) as img:
            resolution = img.size  # (width, height)
            logger.debug(f"Resolução da imagem (de bytes): {resolution}")
            return resolution
    except (UnidentifiedImageError, ValueError) as e:
        logger.warning(f"Não foi possível identificar a imagem a partir dos bytes: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Erro ao processar a imagem a partir dos bytes: {str(e)}")
        return None


def calculate_image_quality(resolution: Tuple[int, int]) -> int:
    """
    Calcula um valor de qualidade para uma imagem com base na resolução.
    
    Args:
        resolution: Tupla (largura, altura) representando a resolução da imagem.
    
    Returns:
        int: Valor de qualidade (largura * altura).
    """
    width, height = resolution
    return width * height
