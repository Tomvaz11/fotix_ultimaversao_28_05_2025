"""
Interfaces para os serviços da camada de infraestrutura.
"""
from pathlib import Path
from typing import Any, Callable, Iterable, Protocol

# Import FileInfo aqui se/quando for definido e necessário por alguma interface de infra.
# from fotix.core.models import FileInfo


class IFileSystemService(Protocol):
    """
    Abstrai operações no sistema de arquivos.
    """

    def get_file_size(self, path: Path) -> int | None:
        """Retorna o tamanho do arquivo em bytes ou None se não existir/acessível."""
        ...

    def stream_file_content(
        self, path: Path, chunk_size: int = 65536
    ) -> Iterable[bytes]:
        """
        Retorna um iterador/gerador para ler o conteúdo do arquivo em blocos.
        Lança exceções apropriadas (ex: FileNotFoundError, PermissionError).
        """
        ...

    def list_directory_contents(
        self,
        path: Path,
        recursive: bool = True,
        file_extensions: list[str] | None = None,
    ) -> Iterable[Path]:
        """
        Retorna um iterador/gerador para os caminhos de arquivos
        (e opcionalmente diretórios, dependendo da implementação)
        dentro de um diretório, com filtros opcionais.
        """
        ...

    def move_to_trash(self, path: Path) -> None:
        """
        Move o arquivo/diretório para a lixeira do sistema.
        Lança exceção em caso de falha.
        """
        ...

    def copy_file(self, source: Path, destination: Path) -> None:
        """Copia um arquivo. Preserva metadados se possível."""
        ...

    def create_directory(self, path: Path, exist_ok: bool = True) -> None:
        """Cria um diretório."""
        ...

    def path_exists(self, path: Path) -> bool:
        """Verifica se um caminho existe."""
        ...

    def get_creation_time(self, path: Path) -> float | None:
        """Retorna o timestamp de criação (Unix epoch)."""
        ...

    def get_modification_time(self, path: Path) -> float | None:
        """Retorna o timestamp de modificação (Unix epoch)."""
        ...

    def delete_file(self, path: Path) -> None:
        """
        Exclui um arquivo permanentemente.
        Lança exceção em caso de falha.
        Atenção: Esta operação é destrutiva e não usa a lixeira.
        """
        ...

    def delete_directory(self, path: Path, recursive: bool = False) -> None:
        """
        Exclui um diretório permanentemente.
        Se recursive=False, o diretório deve estar vazio.
        Se recursive=True, remove o diretório e todo o seu conteúdo.
        Lança exceção em caso de falha.
        Atenção: Esta operação é destrutiva e não usa a lixeira.
        """
        ...

    def get_file_info(self, path: Path) -> dict[str, Any] | None:
        """
        Retorna um dicionário com informações do arquivo:
        'name', 'path', 'size', 'creation_time', 'modification_time', 'is_dir'.
        Retorna None se o caminho não existir.
        """
        ...

# Outras interfaces de infraestrutura podem ser adicionadas aqui, como:
# class IZipHandlerService(Protocol): ...
# class IConcurrencyService(Protocol): ...
# class IBackupService(Protocol): ...

# class ILoggingConfigService(Protocol): # Se quisermos abstrair a configuração do logging
#     def setup_logging(self) -> None:
#         ... 