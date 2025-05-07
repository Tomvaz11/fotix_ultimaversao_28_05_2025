"""
Interfaces para os serviços da camada de infraestrutura do Fotix.

Este módulo define as interfaces (contratos) para os serviços da camada de infraestrutura,
como sistema de arquivos, concorrência, backup e manipulação de arquivos ZIP.
"""

from pathlib import Path
from typing import Callable, Iterable, List, Optional, Protocol, Tuple, TypeVar, Union

# Definição de tipos genéricos para uso nas interfaces
T = TypeVar('T')
R = TypeVar('R')


class IFileSystemService(Protocol):
    """
    Interface para operações no sistema de arquivos.

    Esta interface abstrai operações comuns no sistema de arquivos, como listar diretórios,
    obter tamanho de arquivo, ler conteúdo, mover para a lixeira, copiar arquivos, etc.
    """

    def get_file_size(self, path: Path) -> Optional[int]:
        """
        Retorna o tamanho do arquivo em bytes.

        Args:
            path: Caminho para o arquivo.

        Returns:
            int: Tamanho do arquivo em bytes, ou None se o arquivo não existir ou não for acessível.

        Note:
            Esta função não lança exceções para arquivos inexistentes ou inacessíveis,
            apenas retorna None nesses casos.
        """
        ...

    def stream_file_content(self, path: Path, chunk_size: int = 65536) -> Iterable[bytes]:
        """
        Retorna um iterador/gerador para ler o conteúdo do arquivo em blocos.

        Args:
            path: Caminho para o arquivo.
            chunk_size: Tamanho de cada bloco em bytes. O padrão é 65536 (64KB).

        Returns:
            Iterable[bytes]: Iterador/gerador que produz blocos do conteúdo do arquivo.

        Raises:
            FileNotFoundError: Se o arquivo não existir.
            PermissionError: Se não houver permissão para ler o arquivo.
            IOError: Para outros erros de IO.
        """
        ...

    def list_directory_contents(
        self,
        path: Path,
        recursive: bool = True,
        file_extensions: Optional[List[str]] = None
    ) -> Iterable[Path]:
        """
        Retorna um iterador/gerador para os caminhos de arquivos dentro de um diretório.

        Args:
            path: Caminho para o diretório.
            recursive: Se True, lista também os arquivos em subdiretórios. O padrão é True.
            file_extensions: Lista opcional de extensões de arquivo para filtrar (ex: ['.jpg', '.png']).
                            Se None, não aplica filtro de extensão.

        Returns:
            Iterable[Path]: Iterador/gerador que produz caminhos de arquivos.

        Raises:
            FileNotFoundError: Se o diretório não existir.
            NotADirectoryError: Se o caminho não for um diretório.
            PermissionError: Se não houver permissão para acessar o diretório.
        """
        ...

    def move_to_trash(self, path: Path) -> None:
        """
        Move o arquivo ou diretório para a lixeira do sistema.

        Args:
            path: Caminho para o arquivo ou diretório.

        Raises:
            FileNotFoundError: Se o arquivo ou diretório não existir.
            PermissionError: Se não houver permissão para mover o arquivo ou diretório.
            OSError: Para outros erros do sistema operacional.
        """
        ...

    def copy_file(self, source: Path, destination: Path) -> None:
        """
        Copia um arquivo de origem para destino.

        Args:
            source: Caminho para o arquivo de origem.
            destination: Caminho para o arquivo de destino.

        Raises:
            FileNotFoundError: Se o arquivo de origem não existir.
            PermissionError: Se não houver permissão para ler o arquivo de origem ou escrever no destino.
            IsADirectoryError: Se o destino for um diretório.
            IOError: Para outros erros de IO.
        """
        ...

    def create_directory(self, path: Path, exist_ok: bool = True) -> None:
        """
        Cria um diretório.

        Args:
            path: Caminho para o diretório a ser criado.
            exist_ok: Se True, não lança erro se o diretório já existir. O padrão é True.

        Raises:
            FileExistsError: Se o diretório já existir e exist_ok for False.
            PermissionError: Se não houver permissão para criar o diretório.
            FileNotFoundError: Se o diretório pai não existir.
        """
        ...

    def path_exists(self, path: Path) -> bool:
        """
        Verifica se um caminho existe.

        Args:
            path: Caminho para verificar.

        Returns:
            bool: True se o caminho existir, False caso contrário.
        """
        ...

    def get_creation_time(self, path: Path) -> Optional[float]:
        """
        Retorna o timestamp de criação do arquivo ou diretório.

        Args:
            path: Caminho para o arquivo ou diretório.

        Returns:
            float: Timestamp de criação (segundos desde a época), ou None se não for possível obter.

        Note:
            Em alguns sistemas de arquivos, o timestamp de criação pode não estar disponível.
            Nesse caso, pode retornar o timestamp de modificação ou None.
        """
        ...

    def get_modification_time(self, path: Path) -> Optional[float]:
        """
        Retorna o timestamp de modificação do arquivo ou diretório.

        Args:
            path: Caminho para o arquivo ou diretório.

        Returns:
            float: Timestamp de modificação (segundos desde a época), ou None se não for possível obter.
        """
        ...


class IZipHandlerService(Protocol):
    """
    Interface para operações em arquivos ZIP.

    Esta interface abstrai a leitura de arquivos dentro de arquivos ZIP,
    permitindo o processamento streaming sem extrair tudo para o disco.
    """

    def stream_zip_entries(
        self,
        zip_path: Path,
        file_extensions: Optional[List[str]] = None
    ) -> Iterable[Tuple[str, Optional[int], Callable[[], Iterable[bytes]]]]:
        """
        Retorna um iterador/gerador para os arquivos dentro de um ZIP.

        Args:
            zip_path: Caminho para o arquivo ZIP.
            file_extensions: Lista opcional de extensões de arquivo para filtrar (ex: ['.jpg', '.png']).
                            Se None, não aplica filtro de extensão.

        Returns:
            Iterable[Tuple[str, Optional[int], Callable[[], Iterable[bytes]]]]:
                Iterador/gerador que produz tuplas contendo:
                - Nome do arquivo dentro do ZIP
                - Tamanho do arquivo em bytes (pode ser None se não disponível)
                - Uma função lazy que retorna um iterador/gerador para o conteúdo do arquivo em blocos

        Raises:
            FileNotFoundError: Se o arquivo ZIP não existir.
            PermissionError: Se não houver permissão para ler o arquivo ZIP.
            zipfile.BadZipFile: Se o arquivo não for um ZIP válido ou estiver corrompido.
            IOError: Para outros erros de IO.
        """
        ...
