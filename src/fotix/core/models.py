"""
Modelos de dados centrais do domínio do Fotix.

Este módulo define as estruturas de dados principais utilizadas pelo sistema,
como FileInfo e DuplicateSet, usando dataclasses para garantir tipagem forte
e validação de dados.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Callable, Iterable


@dataclass
class FileInfo:
    """
    Representa informações sobre um arquivo no sistema.

    Esta classe armazena metadados sobre um arquivo, como caminho, tamanho,
    hash, data de criação e modificação. É utilizada para representar tanto
    arquivos normais quanto arquivos dentro de ZIPs.

    Attributes:
        path: Caminho completo para o arquivo.
        size: Tamanho do arquivo em bytes.
        hash: Hash do conteúdo do arquivo (BLAKE3), usado para identificar duplicatas.
        creation_time: Timestamp de criação do arquivo (segundos desde a época).
        modification_time: Timestamp de última modificação do arquivo.
        in_zip: Indica se o arquivo está dentro de um arquivo ZIP.
        zip_path: Se in_zip=True, este é o caminho para o arquivo ZIP que contém este arquivo.
        internal_path: Se in_zip=True, este é o caminho do arquivo dentro do ZIP.
        content_provider: Se in_zip=True, esta é uma função que retorna um iterador para o conteúdo do arquivo.
        original_path: Caminho original do arquivo, usado para restauração de backups.
    """

    path: Path
    size: int
    hash: Optional[str] = None
    creation_time: Optional[float] = None
    modification_time: Optional[float] = None
    in_zip: bool = False
    zip_path: Optional[Path] = None
    internal_path: Optional[str] = None
    content_provider: Optional[Callable[[], Iterable[bytes]]] = None
    original_path: Optional[Path] = None

    def __post_init__(self):
        """
        Validação e processamento após a inicialização.

        Converte strings para Path se necessário e garante que os tipos estão corretos.
        """
        # Converter strings para Path se necessário
        if isinstance(self.path, str):
            self.path = Path(self.path)

        if self.zip_path is not None and isinstance(self.zip_path, str):
            self.zip_path = Path(self.zip_path)

        if self.original_path is not None and isinstance(self.original_path, str):
            self.original_path = Path(self.original_path)

    @property
    def filename(self) -> str:
        """
        Retorna apenas o nome do arquivo, sem o caminho.

        Returns:
            str: Nome do arquivo.
        """
        return self.path.name

    @property
    def extension(self) -> str:
        """
        Retorna a extensão do arquivo.

        Returns:
            str: Extensão do arquivo (com o ponto), ou string vazia se não tiver extensão.
        """
        return self.path.suffix

    @property
    def creation_datetime(self) -> Optional[datetime]:
        """
        Retorna a data/hora de criação como objeto datetime.

        Returns:
            datetime: Data e hora de criação, ou None se não disponível.
        """
        if self.creation_time is not None:
            return datetime.fromtimestamp(self.creation_time)
        return None

    @property
    def modification_datetime(self) -> Optional[datetime]:
        """
        Retorna a data/hora de modificação como objeto datetime.

        Returns:
            datetime: Data e hora de modificação, ou None se não disponível.
        """
        if self.modification_time is not None:
            return datetime.fromtimestamp(self.modification_time)
        return None


@dataclass
class DuplicateSet:
    """
    Representa um conjunto de arquivos duplicados.

    Esta classe armazena informações sobre um grupo de arquivos que são
    considerados duplicatas uns dos outros, com base em seu conteúdo (hash).

    Attributes:
        files: Lista de FileInfo representando os arquivos duplicados.
        hash: Hash comum a todos os arquivos no conjunto.
        selected_file: Arquivo selecionado para ser mantido (os outros seriam removidos).
    """

    files: List[FileInfo] = field(default_factory=list)
    hash: Optional[str] = None
    selected_file: Optional[FileInfo] = None

    @property
    def size(self) -> int:
        """
        Retorna o tamanho dos arquivos no conjunto.

        Como todos os arquivos são duplicatas, todos têm o mesmo tamanho.

        Returns:
            int: Tamanho em bytes, ou 0 se o conjunto estiver vazio.
        """
        if not self.files:
            return 0
        return self.files[0].size

    @property
    def count(self) -> int:
        """
        Retorna o número de arquivos no conjunto.

        Returns:
            int: Número de arquivos duplicados.
        """
        return len(self.files)

    def add_file(self, file: FileInfo) -> None:
        """
        Adiciona um arquivo ao conjunto de duplicatas.

        Args:
            file: FileInfo do arquivo a ser adicionado.

        Raises:
            ValueError: Se o arquivo tiver um hash diferente dos outros no conjunto.
        """
        if self.hash is None:
            self.hash = file.hash
        elif file.hash != self.hash:
            raise ValueError(f"Arquivo com hash diferente: {file.hash} != {self.hash}")

        self.files.append(file)
