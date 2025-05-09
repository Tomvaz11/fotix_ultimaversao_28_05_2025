"""
Pacote para os serviços de infraestrutura da aplicação Fotix.

Este pacote contém implementações e interfaces para interações com o sistema operacional
e serviços externos, como sistema de arquivos, logging, concorrência, etc.
"""

from .file_system import FileSystemService
from .interfaces import IFileSystemService

__all__ = ["IFileSystemService", "FileSystemService"] 