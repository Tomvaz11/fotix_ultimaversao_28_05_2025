"""
Interfaces para os serviços da camada de infraestrutura do Fotix.

Este módulo define os contratos (interfaces) para os serviços desta camada,
permitindo que as camadas superiores dependam de abstrações e não de implementações.
"""

from pathlib import Path
from typing import Protocol, runtime_checkable, Iterable, Optional, List

# Nota: Atualmente não há interfaces específicas para configuração de logging
# pois o módulo logging_config configura o sistema de logging padrão do Python
# sem precisar expor uma interface específica para isso.

@runtime_checkable
class IFileSystemService(Protocol):
    """
    Interface para abstrair operações no sistema de arquivos.
    
    Esta interface define o contrato para operações como leitura, escrita,
    movimentação para lixeira e listagem de diretórios, isolando
    o código de aplicação e domínio das implementações concretas de IO.
    """
    
    def get_file_size(self, path: Path) -> Optional[int]:
        """
        Retorna o tamanho do arquivo em bytes.
        
        Args:
            path: Caminho do arquivo.
            
        Returns:
            Tamanho do arquivo em bytes ou None se o arquivo não existir/for inacessível.
        """
        ...
    
    def stream_file_content(self, path: Path, chunk_size: int = 65536) -> Iterable[bytes]:
        """
        Retorna um iterador/gerador para ler o conteúdo do arquivo em blocos.
        
        Args:
            path: Caminho do arquivo.
            chunk_size: Tamanho de cada bloco de leitura em bytes.
            
        Returns:
            Iterador/gerador que produz blocos de bytes do arquivo.
            
        Raises:
            FileNotFoundError: Se o arquivo não existir.
            PermissionError: Se não houver permissão para ler o arquivo.
            IOError: Para outros erros de IO.
        """
        ...
    
    def list_directory_contents(self, path: Path, recursive: bool = True, 
                              file_extensions: Optional[List[str]] = None) -> Iterable[Path]:
        """
        Lista os arquivos (e diretórios) em um diretório, com filtros opcionais.
        
        Args:
            path: Caminho do diretório.
            recursive: Se True, inclui arquivos em subdiretórios recursivamente.
            file_extensions: Lista opcional de extensões de arquivo para filtrar
                           (ex: ['.jpg', '.png']). Se None, inclui todos os arquivos.
                           
        Returns:
            Iterador/gerador que produz caminhos de arquivos/diretórios.
            
        Raises:
            FileNotFoundError: Se o diretório não existir.
            PermissionError: Se não houver permissão para acessar o diretório.
            NotADirectoryError: Se o caminho não for um diretório.
        """
        ...
    
    def move_to_trash(self, path: Path) -> None:
        """
        Move o arquivo ou diretório para a lixeira do sistema.
        
        Args:
            path: Caminho do arquivo ou diretório a ser movido para a lixeira.
            
        Raises:
            FileNotFoundError: Se o arquivo/diretório não existir.
            PermissionError: Se não houver permissão para movê-lo.
            OSError: Para outros erros do sistema operacional durante a operação.
        """
        ...
    
    def copy_file(self, source: Path, destination: Path) -> None:
        """
        Copia um arquivo de origem para o destino.
        
        Args:
            source: Caminho do arquivo de origem.
            destination: Caminho de destino para o arquivo.
            
        Raises:
            FileNotFoundError: Se o arquivo de origem não existir.
            PermissionError: Se não houver permissão para ler a origem ou escrever no destino.
            IsADirectoryError: Se a origem for um diretório e não um arquivo.
            OSError: Para outros erros do sistema operacional durante a operação.
        """
        ...
    
    def create_directory(self, path: Path, exist_ok: bool = True) -> None:
        """
        Cria um diretório.
        
        Args:
            path: Caminho do diretório a ser criado.
            exist_ok: Se True, não gera erro se o diretório já existir.
            
        Raises:
            FileExistsError: Se o diretório já existir e exist_ok for False.
            PermissionError: Se não houver permissão para criar o diretório.
            OSError: Para outros erros do sistema operacional durante a operação.
        """
        ...
    
    def path_exists(self, path: Path) -> bool:
        """
        Verifica se um caminho (arquivo ou diretório) existe.
        
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
            Timestamp de criação como float (segundos desde epoch) ou
            None se o arquivo não existir ou a informação não estiver disponível.
        """
        ...
    
    def get_modification_time(self, path: Path) -> Optional[float]:
        """
        Retorna o timestamp de modificação do arquivo ou diretório.
        
        Args:
            path: Caminho do arquivo ou diretório.
            
        Returns:
            Timestamp de modificação como float (segundos desde epoch) ou
            None se o arquivo não existir ou a informação não estiver disponível.
        """
        ...

# As interfaces como IConcurrencyService, IBackupService, IZipHandlerService
# serão definidas neste arquivo conforme forem implementadas nos próximos módulos. 