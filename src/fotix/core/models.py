"""
Modelos de dados centrais do domínio do Fotix.

Este módulo define as estruturas de dados principais utilizadas pelo Fotix,
como informações de arquivos e conjuntos de duplicatas.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class FileInfo:
    """
    Representa informações sobre um arquivo no sistema.
    
    Esta classe armazena metadados sobre um arquivo, como caminho, tamanho,
    datas de criação e modificação, e hash (quando calculado).
    """
    
    path: Path
    """Caminho completo para o arquivo."""
    
    size: int
    """Tamanho do arquivo em bytes."""
    
    creation_time: Optional[float] = None
    """Timestamp de criação do arquivo (segundos desde a época) ou None se não disponível."""
    
    modification_time: Optional[float] = None
    """Timestamp de modificação do arquivo (segundos desde a época) ou None se não disponível."""
    
    hash_value: Optional[str] = None
    """Hash do conteúdo do arquivo (quando calculado) ou None."""
    
    in_zip: bool = False
    """Indica se o arquivo está dentro de um arquivo ZIP."""
    
    zip_path: Optional[Path] = None
    """Caminho do arquivo ZIP que contém este arquivo, se aplicável."""
    
    @property
    def name(self) -> str:
        """Retorna o nome do arquivo sem o caminho."""
        return self.path.name
    
    @property
    def extension(self) -> str:
        """Retorna a extensão do arquivo (incluindo o ponto)."""
        return self.path.suffix.lower()
    
    @property
    def creation_datetime(self) -> Optional[datetime]:
        """Retorna a data/hora de criação como objeto datetime ou None."""
        if self.creation_time is not None:
            return datetime.fromtimestamp(self.creation_time)
        return None
    
    @property
    def modification_datetime(self) -> Optional[datetime]:
        """Retorna a data/hora de modificação como objeto datetime ou None."""
        if self.modification_time is not None:
            return datetime.fromtimestamp(self.modification_time)
        return None
    
    def __str__(self) -> str:
        """Representação em string do FileInfo."""
        return f"FileInfo(path='{self.path}', size={self.size} bytes)"


@dataclass
class DuplicateSet:
    """
    Representa um conjunto de arquivos duplicados.
    
    Esta classe armazena um conjunto de arquivos que foram identificados como
    duplicados com base em seu conteúdo (hash).
    """
    
    files: List[FileInfo]
    """Lista de arquivos duplicados."""
    
    hash_value: str
    """Valor de hash compartilhado por todos os arquivos no conjunto."""
    
    @property
    def size(self) -> int:
        """Retorna o tamanho dos arquivos no conjunto (todos têm o mesmo tamanho)."""
        if not self.files:
            return 0
        return self.files[0].size
    
    @property
    def count(self) -> int:
        """Retorna o número de arquivos no conjunto."""
        return len(self.files)
    
    def __str__(self) -> str:
        """Representação em string do DuplicateSet."""
        return f"DuplicateSet(hash='{self.hash_value[:8]}...', count={self.count}, size={self.size} bytes)"
