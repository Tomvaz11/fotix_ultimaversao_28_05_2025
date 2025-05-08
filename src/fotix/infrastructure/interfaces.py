"""
Interfaces para os componentes da camada de infraestrutura do Fotix.

Este módulo define os contratos (interfaces) para os serviços da camada
de infraestrutura, como acesso ao sistema de arquivos, concorrência,
manipulação de backups e arquivos ZIP.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Optional, List


class IFileSystemService(ABC):
    """
    Interface para abstrair operações no sistema de arquivos.
    
    Define o contrato para serviços que lidam com operações de arquivo,
    como leitura, escrita, movimentação para lixeira e listagem de diretórios.
    """
    
    @abstractmethod
    def get_file_size(self, path: Path) -> Optional[int]:
        """
        Retorna o tamanho do arquivo em bytes.
        
        Args:
            path: Caminho do arquivo.
            
        Returns:
            O tamanho do arquivo em bytes ou None se o arquivo não existir ou não for acessível.
        """
        pass
    
    @abstractmethod
    def stream_file_content(self, path: Path, chunk_size: int = 65536) -> Iterable[bytes]:
        """
        Retorna um iterador/gerador para ler o conteúdo do arquivo em blocos.
        
        Args:
            path: Caminho do arquivo.
            chunk_size: Tamanho de cada bloco em bytes.
            
        Returns:
            Um iterador que produz blocos de bytes do arquivo.
            
        Raises:
            FileNotFoundError: Se o arquivo não for encontrado.
            PermissionError: Se não houver permissão para acessar o arquivo.
            OSError: Para outros erros de IO.
        """
        pass
    
    @abstractmethod
    def list_directory_contents(
        self, path: Path, recursive: bool = True, file_extensions: Optional[List[str]] = None
    ) -> Iterable[Path]:
        """
        Retorna um iterador para os caminhos de arquivos dentro de um diretório.
        
        Args:
            path: Caminho do diretório.
            recursive: Se True, inclui arquivos em subdiretórios.
            file_extensions: Lista de extensões para filtrar os arquivos (ex: ['.jpg', '.png']).
                            Se None, todos os arquivos são incluídos.
            
        Returns:
            Um iterador que produz caminhos de arquivos (Path).
            
        Raises:
            FileNotFoundError: Se o diretório não for encontrado.
            PermissionError: Se não houver permissão para acessar o diretório.
            NotADirectoryError: Se o caminho não apontar para um diretório.
        """
        pass
    
    @abstractmethod
    def move_to_trash(self, path: Path) -> None:
        """
        Move o arquivo ou diretório para a lixeira do sistema.
        
        Args:
            path: Caminho do arquivo ou diretório.
            
        Raises:
            FileNotFoundError: Se o arquivo/diretório não for encontrado.
            PermissionError: Se não houver permissão para mover o arquivo/diretório.
            OSError: Para outros erros de IO.
        """
        pass
    
    @abstractmethod
    def copy_file(self, source: Path, destination: Path) -> None:
        """
        Copia um arquivo de origem para destino.
        
        Args:
            source: Caminho do arquivo de origem.
            destination: Caminho do arquivo de destino.
            
        Raises:
            FileNotFoundError: Se o arquivo de origem não for encontrado.
            PermissionError: Se não houver permissão para copiar o arquivo.
            OSError: Para outros erros de IO.
        """
        pass
    
    @abstractmethod
    def create_directory(self, path: Path, exist_ok: bool = True) -> None:
        """
        Cria um diretório.
        
        Args:
            path: Caminho do diretório a ser criado.
            exist_ok: Se True, não levanta exceção se o diretório já existir.
            
        Raises:
            FileExistsError: Se o diretório já existir e exist_ok for False.
            PermissionError: Se não houver permissão para criar o diretório.
            OSError: Para outros erros de IO.
        """
        pass
    
    @abstractmethod
    def path_exists(self, path: Path) -> bool:
        """
        Verifica se um caminho existe.
        
        Args:
            path: Caminho a ser verificado.
            
        Returns:
            True se o caminho existir, False caso contrário.
        """
        pass
    
    @abstractmethod
    def get_creation_time(self, path: Path) -> Optional[float]:
        """
        Retorna o timestamp de criação do arquivo.
        
        Args:
            path: Caminho do arquivo.
            
        Returns:
            Timestamp de criação como float (segundos desde a época) ou None se não disponível.
        """
        pass
    
    @abstractmethod
    def get_modification_time(self, path: Path) -> Optional[float]:
        """
        Retorna o timestamp de modificação do arquivo.
        
        Args:
            path: Caminho do arquivo.
            
        Returns:
            Timestamp de modificação como float (segundos desde a época) ou None se não disponível.
        """
        pass 