"""
Interfaces para os serviços da camada de infraestrutura do Fotix.

Este módulo define os contratos (interfaces) para os serviços da camada de infraestrutura,
como acesso ao sistema de arquivos, manipulação de ZIPs, concorrência e backup.
"""

from pathlib import Path
from typing import Any, Callable, Iterable, Optional, Protocol, Union


class IFileSystemService(Protocol):
    """
    Interface para abstrair operações no sistema de arquivos.
    
    Esta interface define métodos para operações comuns no sistema de arquivos,
    como leitura, escrita, movimentação para lixeira e listagem de diretórios.
    """
    
    def get_file_size(self, path: Path) -> Optional[int]:
        """
        Retorna o tamanho do arquivo em bytes.
        
        Args:
            path: Caminho do arquivo.
            
        Returns:
            Tamanho do arquivo em bytes ou None se o arquivo não existir ou não for acessível.
            
        Raises:
            PermissionError: Se o arquivo existir mas não for acessível por permissões.
        """
        ...
    
    def stream_file_content(self, path: Path, chunk_size: int = 65536) -> Iterable[bytes]:
        """
        Retorna um iterador/gerador para ler o conteúdo do arquivo em blocos.
        
        Args:
            path: Caminho do arquivo.
            chunk_size: Tamanho do bloco em bytes para leitura.
            
        Returns:
            Um iterador/gerador que produz blocos de bytes do arquivo.
            
        Raises:
            FileNotFoundError: Se o arquivo não existir.
            PermissionError: Se o arquivo não for acessível por permissões.
            IsADirectoryError: Se o caminho apontar para um diretório.
        """
        ...
    
    def list_directory_contents(
        self, 
        path: Path, 
        recursive: bool = True, 
        file_extensions: Optional[list[str]] = None
    ) -> Iterable[Path]:
        """
        Retorna um iterador/gerador para os caminhos de arquivos dentro de um diretório.
        
        Args:
            path: Caminho do diretório.
            recursive: Se True, lista arquivos em subdiretórios recursivamente.
            file_extensions: Lista opcional de extensões de arquivo para filtrar (ex: ['.jpg', '.png']).
                            Se None, todos os arquivos são incluídos.
            
        Returns:
            Um iterador/gerador que produz objetos Path para cada arquivo encontrado.
            
        Raises:
            FileNotFoundError: Se o diretório não existir.
            NotADirectoryError: Se o caminho não apontar para um diretório.
            PermissionError: Se o diretório não for acessível por permissões.
        """
        ...
    
    def move_to_trash(self, path: Path) -> None:
        """
        Move o arquivo ou diretório para a lixeira do sistema.
        
        Args:
            path: Caminho do arquivo ou diretório a ser movido para a lixeira.
            
        Raises:
            FileNotFoundError: Se o arquivo ou diretório não existir.
            PermissionError: Se o arquivo ou diretório não puder ser movido por permissões.
        """
        ...
    
    def copy_file(self, source: Path, destination: Path) -> None:
        """
        Copia um arquivo de origem para destino.
        
        Args:
            source: Caminho do arquivo de origem.
            destination: Caminho do arquivo de destino.
            
        Raises:
            FileNotFoundError: Se o arquivo de origem não existir.
            IsADirectoryError: Se o caminho de origem apontar para um diretório.
            PermissionError: Se o arquivo não puder ser copiado por permissões.
        """
        ...
    
    def create_directory(self, path: Path, exist_ok: bool = True) -> None:
        """
        Cria um diretório no caminho especificado.
        
        Args:
            path: Caminho do diretório a ser criado.
            exist_ok: Se True, não levanta erro se o diretório já existir.
            
        Raises:
            FileExistsError: Se o diretório já existir e exist_ok=False.
            PermissionError: Se o diretório não puder ser criado por permissões.
        """
        ...
    
    def path_exists(self, path: Path) -> bool:
        """
        Verifica se um caminho existe.
        
        Args:
            path: Caminho a ser verificado.
            
        Returns:
            True se o caminho existir, False caso contrário.
        """
        ...
    
    def get_creation_time(self, path: Path) -> Optional[float]:
        """
        Retorna o timestamp de criação do arquivo ou diretório.
        
        Args:
            path: Caminho do arquivo ou diretório.
            
        Returns:
            Timestamp de criação como float (segundos desde a época) ou None se não disponível.
            
        Raises:
            FileNotFoundError: Se o arquivo ou diretório não existir.
            PermissionError: Se o arquivo ou diretório não for acessível por permissões.
        """
        ...
    
    def get_modification_time(self, path: Path) -> Optional[float]:
        """
        Retorna o timestamp de modificação do arquivo ou diretório.
        
        Args:
            path: Caminho do arquivo ou diretório.
            
        Returns:
            Timestamp de modificação como float (segundos desde a época) ou None se não disponível.
            
        Raises:
            FileNotFoundError: Se o arquivo ou diretório não existir.
            PermissionError: Se o arquivo ou diretório não for acessível por permissões.
        """
        ...


# Outras interfaces serão adicionadas conforme necessário
# (IZipHandlerService, IConcurrencyService, IBackupService)
