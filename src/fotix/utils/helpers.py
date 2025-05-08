"""
Funções auxiliares genéricas para o Fotix.

Este módulo contém funções utilitárias que podem ser usadas em várias partes da aplicação.
"""

import os
from pathlib import Path
from typing import List, Optional, Set


def normalize_path(path: Path) -> Path:
    """
    Normaliza um caminho para garantir consistência.

    Args:
        path: O caminho a ser normalizado.

    Returns:
        O caminho normalizado como objeto Path.
    """
    return path.resolve()


def filter_by_extensions(path: Path, extensions: List[str]) -> bool:
    """
    Verifica se um arquivo tem uma das extensões especificadas.

    Args:
        path: Caminho do arquivo.
        extensions: Lista de extensões (com ponto, ex: ['.jpg', '.png']).

    Returns:
        True se o arquivo tiver uma das extensões, False caso contrário.
    """
    if not extensions:
        return True

    return path.suffix.lower() in [ext.lower() for ext in extensions]


def is_hidden_file(path: Path) -> bool:
    """
    Verifica se um arquivo ou diretório é oculto.

    Em sistemas Windows, verifica o atributo FILE_ATTRIBUTE_HIDDEN.
    Em sistemas Unix-like, verifica se o nome começa com ponto.

    Args:
        path: Caminho do arquivo ou diretório.

    Returns:
        True se o arquivo ou diretório for oculto, False caso contrário.
    """
    # Verificação baseada no nome (funciona em todos os sistemas)
    if path.name.startswith('.'):
        return True

    # Verificação adicional específica do Windows usando win32api
    if os.name == 'nt' and path.exists():  # Windows e o caminho existe
        try:
            import win32api
            import win32con
            attributes = win32api.GetFileAttributes(str(path))
            return bool(attributes & win32con.FILE_ATTRIBUTE_HIDDEN)
        except (ImportError, OSError):
            # Se win32api não estiver disponível ou ocorrer erro, já verificamos pelo nome acima
            pass

    # Se chegou aqui, não é oculto
    return False


def format_file_size(size_bytes: int) -> str:
    """
    Formata um tamanho em bytes para uma representação legível.

    Args:
        size_bytes: Tamanho em bytes.

    Returns:
        String formatada (ex: "1.23 MB").
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"

    size_kb = size_bytes / 1024
    if size_kb < 1024:
        return f"{size_kb:.2f} KB"

    size_mb = size_kb / 1024
    if size_mb < 1024:
        return f"{size_mb:.2f} MB"

    size_gb = size_mb / 1024
    return f"{size_gb:.2f} GB"


def get_common_parent_directory(paths: List[Path]) -> Optional[Path]:
    """
    Encontra o diretório pai comum mais específico para uma lista de caminhos.

    Args:
        paths: Lista de caminhos.

    Returns:
        O diretório pai comum ou None se a lista estiver vazia.
    """
    if not paths:
        return None

    # Normaliza todos os caminhos
    normalized_paths = [normalize_path(p) for p in paths]

    # Converte para strings para comparação
    path_strings = [str(p) for p in normalized_paths]

    # Encontra o prefixo comum
    common_prefix = os.path.commonprefix(path_strings)

    # Se o prefixo comum não terminar em um separador de diretório,
    # precisamos voltar para o último diretório completo
    if not common_prefix.endswith(os.path.sep):
        common_prefix = os.path.dirname(common_prefix)

    # Se o prefixo comum estiver vazio, não há diretório comum
    if not common_prefix:
        return None

    return Path(common_prefix)
