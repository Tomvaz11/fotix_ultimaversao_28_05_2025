"""
Testes unitários para as interfaces da infraestrutura do Fotix.

Este módulo contém testes para verificar se as interfaces da infraestrutura
estão definidas corretamente e podem ser usadas para tipagem.
"""

from pathlib import Path
from typing import List, Dict, Any, Iterable, Tuple, Callable, Optional
from concurrent.futures import Future
import pytest

from fotix.core.models import FileInfo
from fotix.infrastructure.interfaces import (
    IConcurrencyService,
    IFileSystemService,
    IZipHandlerService,
    IBackupService
)


class MockConcurrencyService:
    """Implementação mock de IConcurrencyService para testes."""

    def run_parallel(self, tasks: Iterable[Callable[[], Any]]) -> Iterable[Any]:
        """Executa tarefas em paralelo (simulado)."""
        return [task() for task in tasks]

    def submit_background_task(self, task: Callable[..., Any], *args, **kwargs) -> Future:
        """Submete uma tarefa para execução em background (simulado)."""
        future = Future()
        try:
            result = task(*args, **kwargs)
            future.set_result(result)
        except Exception as e:
            future.set_exception(e)
        return future


class MockFileSystemService:
    """Implementação mock de IFileSystemService para testes."""

    def get_file_size(self, path: Path) -> Optional[int]:
        """Retorna o tamanho do arquivo (simulado)."""
        return 1024 if path.name != "nonexistent.txt" else None

    def stream_file_content(self, path: Path, chunk_size: int = 65536) -> Iterable[bytes]:
        """Retorna o conteúdo do arquivo em blocos (simulado)."""
        if path.name == "nonexistent.txt":
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")
        return [b"conteudo simulado"]

    def list_directory_contents(self, path: Path, recursive: bool = True,
                               file_extensions: Optional[List[str]] = None) -> Iterable[Path]:
        """Lista os conteúdos de um diretório (simulado)."""
        if path.name == "nonexistent":
            raise FileNotFoundError(f"Diretório não encontrado: {path}")
        return [path / "file1.txt", path / "file2.txt"]

    def move_to_trash(self, path: Path) -> None:
        """Move um arquivo para a lixeira (simulado)."""
        if path.name == "nonexistent.txt":
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    def copy_file(self, source: Path, destination: Path) -> None:
        """Copia um arquivo (simulado)."""
        if source.name == "nonexistent.txt":
            raise FileNotFoundError(f"Arquivo não encontrado: {source}")

    def create_directory(self, path: Path, exist_ok: bool = True) -> None:
        """Cria um diretório (simulado)."""
        pass

    def path_exists(self, path: Path) -> bool:
        """Verifica se um caminho existe (simulado)."""
        return path.name != "nonexistent.txt"

    def get_creation_time(self, path: Path) -> Optional[float]:
        """Retorna o timestamp de criação (simulado)."""
        if path.name == "nonexistent.txt":
            return None
        return 1620000000.0

    def get_modification_time(self, path: Path) -> Optional[float]:
        """Retorna o timestamp de modificação (simulado)."""
        if path.name == "nonexistent.txt":
            return None
        return 1620000000.0


class MockZipHandlerService:
    """Implementação mock de IZipHandlerService para testes."""

    def stream_zip_entries(self, zip_path: Path,
                          file_extensions: Optional[List[str]] = None) -> Iterable[Tuple[str, int, Callable[[], Iterable[bytes]]]]:
        """Retorna um iterador para os arquivos dentro de um ZIP (simulado)."""
        if zip_path.name == "nonexistent.zip":
            raise FileNotFoundError(f"Arquivo ZIP não encontrado: {zip_path}")

        def get_content() -> Iterable[bytes]:
            yield b"conteudo simulado"

        return [
            ("file1.txt", 1024, get_content),
            ("file2.txt", 2048, get_content)
        ]


class MockBackupService:
    """Implementação mock de IBackupService para testes."""

    def create_backup(self, files_to_backup: Iterable[Tuple[Path, FileInfo]]) -> str:
        """Cria um backup (simulado)."""
        return "backup_id_123"

    def list_backups(self) -> List[Dict[str, Any]]:
        """Lista backups (simulado)."""
        return [
            {
                "id": "backup_id_123",
                "date": "2023-01-01T12:00:00",
                "file_count": 2,
                "total_size": 3072
            }
        ]

    def restore_backup(self, backup_id: str, target_directory: Optional[Path] = None) -> None:
        """Restaura um backup (simulado)."""
        if backup_id == "nonexistent":
            raise ValueError(f"Backup não encontrado: {backup_id}")

    def delete_backup(self, backup_id: str) -> None:
        """Remove um backup (simulado)."""
        if backup_id == "nonexistent":
            raise ValueError(f"Backup não encontrado: {backup_id}")


class TestConcurrencyServiceInterface:
    """Testes para a interface IConcurrencyService."""

    def test_concurrency_service_implementation(self):
        """Testa se a implementação mock satisfaz a interface IConcurrencyService."""
        # Arrange
        service: IConcurrencyService = MockConcurrencyService()

        # Act & Assert - se não lançar exceção, o teste passa
        results = service.run_parallel([lambda: 1, lambda: 2, lambda: 3])
        assert list(results) == [1, 2, 3]

        future = service.submit_background_task(lambda x: x * 2, 5)
        assert future.result() == 10


class TestFileSystemServiceInterface:
    """Testes para a interface IFileSystemService."""

    def test_file_system_service_implementation(self):
        """Testa se a implementação mock satisfaz a interface IFileSystemService."""
        # Arrange
        service: IFileSystemService = MockFileSystemService()

        # Act & Assert - se não lançar exceção, o teste passa
        assert service.get_file_size(Path("/test/file.txt")) == 1024
        assert service.get_file_size(Path("/test/nonexistent.txt")) is None

        content = list(service.stream_file_content(Path("/test/file.txt")))
        assert content == [b"conteudo simulado"]

        with pytest.raises(FileNotFoundError):
            list(service.stream_file_content(Path("/test/nonexistent.txt")))

        files = list(service.list_directory_contents(Path("/test")))
        assert len(files) == 2

        assert service.path_exists(Path("/test/file.txt")) is True
        assert service.path_exists(Path("/test/nonexistent.txt")) is False

        assert service.get_creation_time(Path("/test/file.txt")) == 1620000000.0
        assert service.get_creation_time(Path("/test/nonexistent.txt")) is None

        assert service.get_modification_time(Path("/test/file.txt")) == 1620000000.0
        assert service.get_modification_time(Path("/test/nonexistent.txt")) is None


class TestZipHandlerServiceInterface:
    """Testes para a interface IZipHandlerService."""

    def test_zip_handler_service_implementation(self):
        """Testa se a implementação mock satisfaz a interface IZipHandlerService."""
        # Arrange
        service: IZipHandlerService = MockZipHandlerService()

        # Act & Assert - se não lançar exceção, o teste passa
        entries = list(service.stream_zip_entries(Path("/test/archive.zip")))
        assert len(entries) == 2

        filename, size, content_func = entries[0]
        assert filename == "file1.txt"
        assert size == 1024
        assert list(content_func()) == [b"conteudo simulado"]

        with pytest.raises(FileNotFoundError):
            list(service.stream_zip_entries(Path("/test/nonexistent.zip")))


class TestBackupServiceInterface:
    """Testes para a interface IBackupService."""

    def test_backup_service_implementation(self):
        """Testa se a implementação mock satisfaz a interface IBackupService."""
        # Arrange
        service: IBackupService = MockBackupService()
        file_info = FileInfo(path=Path("/test/file.txt"), size=1024)

        # Act & Assert - se não lançar exceção, o teste passa
        backup_id = service.create_backup([(Path("/test/file.txt"), file_info)])
        assert backup_id == "backup_id_123"

        backups = service.list_backups()
        assert len(backups) == 1
        assert backups[0]["id"] == "backup_id_123"

        service.restore_backup("backup_id_123", Path("/test/restore"))
        with pytest.raises(ValueError):
            service.restore_backup("nonexistent")

        service.delete_backup("backup_id_123")
        with pytest.raises(ValueError):
            service.delete_backup("nonexistent")
