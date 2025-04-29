"""
Módulo que define as estruturas de dados principais do domínio do Fotix.

Este módulo contém as classes de dados (dataclasses) que representam as entidades
principais do domínio da aplicação, como metadados de arquivos e grupos de duplicatas.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass(frozen=True)
class FileMetadata:
    """
    Representa os metadados de um arquivo.
    
    Esta classe é imutável (frozen=True) e contém informações básicas sobre um arquivo,
    como seu caminho, tamanho e data de criação.
    
    Attributes:
        path: Caminho absoluto para o arquivo
        size: Tamanho do arquivo em bytes
        creation_time: Timestamp UTC da criação do arquivo
    """
    path: Path
    size: int
    creation_time: float  # Timestamp UTC


@dataclass
class DuplicateGroup:
    """
    Representa um grupo de arquivos duplicados.
    
    Um grupo de duplicatas contém dois ou mais arquivos que são idênticos
    (mesmo tamanho e mesmo hash).
    
    Attributes:
        files: Lista de metadados dos arquivos duplicados
        hash_value: O hash BLAKE3 comum a todos os arquivos no grupo
        file_to_keep: Arquivo que deve ser mantido (os outros podem ser removidos)
    """
    files: List[FileMetadata]
    hash_value: str
    file_to_keep: Optional[FileMetadata] = None
