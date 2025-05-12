"""
Testes unitários para as interfaces da infraestrutura do Fotix.

Este módulo contém testes para verificar se as interfaces da infraestrutura
estão definidas corretamente e podem ser usadas para tipagem.
"""

from pathlib import Path
from typing import List, Dict, Any, Iterable, Tuple, Callable, Optional
from concurrent.futures import Future, CancelledError
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

    def test_run_parallel_with_exceptions(self):
        """Testa o comportamento de run_parallel quando uma tarefa lança exceção."""
        # Arrange
        service = MockConcurrencyService()

        def task_with_exception():
            raise ValueError("Erro simulado")

        # Act & Assert
        with pytest.raises(ValueError, match="Erro simulado"):
            list(service.run_parallel([lambda: 1, task_with_exception, lambda: 3]))

    def test_submit_background_task_with_exception(self):
        """Testa o comportamento de submit_background_task quando a tarefa lança exceção."""
        # Arrange
        service = MockConcurrencyService()

        def task_with_exception(x):
            raise ValueError(f"Erro simulado: {x}")

        # Act
        future = service.submit_background_task(task_with_exception, "teste")

        # Assert
        assert future.done()
        with pytest.raises(ValueError, match="Erro simulado: teste"):
            future.result()

    def test_submit_background_task_cancel(self):
        """Testa o cancelamento de uma tarefa em background."""
        # Arrange
        service = MockConcurrencyService()

        # Criar uma tarefa que pode ser cancelada
        def long_running_task():
            import time
            time.sleep(10)  # Esta tarefa nunca será executada completamente no teste
            return "resultado"

        # Sobrescrever o método submit_background_task para simular cancelamento
        original_submit = service.submit_background_task

        def mock_submit_cancellable(task, *args, **kwargs):
            future = Future()
            future.cancel()  # Cancelar imediatamente
            return future

        service.submit_background_task = mock_submit_cancellable

        try:
            # Act
            future = service.submit_background_task(long_running_task)

            # Assert
            assert future.cancelled()
            with pytest.raises(CancelledError):
                future.result()
        finally:
            # Restaurar o método original
            service.submit_background_task = original_submit


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

    def test_move_to_trash_operation(self):
        """Testa a operação move_to_trash."""
        # Arrange
        service = MockFileSystemService()

        # Act & Assert - operação normal
        service.move_to_trash(Path("/test/file.txt"))  # Não deve lançar exceção

        # Act & Assert - arquivo não existente
        with pytest.raises(FileNotFoundError):
            service.move_to_trash(Path("/test/nonexistent.txt"))

        # Sobrescrever o método move_to_trash para testar outros erros
        original_move_to_trash = service.move_to_trash

        def mock_move_to_trash_errors(path):
            if path.name == "no_permission.txt":
                raise PermissionError("Sem permissão para mover o arquivo")
            elif path.name == "os_error.txt":
                raise OSError("Erro do sistema operacional")
            return original_move_to_trash(path)

        service.move_to_trash = mock_move_to_trash_errors

        try:
            # Act & Assert - sem permissão
            with pytest.raises(PermissionError, match="Sem permissão para mover o arquivo"):
                service.move_to_trash(Path("/test/no_permission.txt"))

            # Act & Assert - erro do sistema operacional
            with pytest.raises(OSError, match="Erro do sistema operacional"):
                service.move_to_trash(Path("/test/os_error.txt"))
        finally:
            # Restaurar o método original
            service.move_to_trash = original_move_to_trash

    def test_copy_file_operation(self):
        """Testa a operação copy_file."""
        # Arrange
        service = MockFileSystemService()

        # Act & Assert - operação normal
        service.copy_file(Path("/test/file.txt"), Path("/test/file_copy.txt"))  # Não deve lançar exceção

        # Act & Assert - arquivo de origem não existente
        with pytest.raises(FileNotFoundError):
            service.copy_file(Path("/test/nonexistent.txt"), Path("/test/copy.txt"))

        # Sobrescrever o método copy_file para testar outros erros
        original_copy_file = service.copy_file

        def mock_copy_file_errors(source, destination):
            if source.name == "directory.txt":
                raise IsADirectoryError("A origem é um diretório")
            elif source.name == "no_permission.txt":
                raise PermissionError("Sem permissão para ler/escrever")
            elif source.name == "io_error.txt":
                raise OSError("Erro de IO genérico")
            return original_copy_file(source, destination)

        service.copy_file = mock_copy_file_errors

        try:
            # Act & Assert - origem é um diretório
            with pytest.raises(IsADirectoryError, match="A origem é um diretório"):
                service.copy_file(Path("/test/directory.txt"), Path("/test/copy.txt"))

            # Act & Assert - sem permissão
            with pytest.raises(PermissionError, match="Sem permissão para ler/escrever"):
                service.copy_file(Path("/test/no_permission.txt"), Path("/test/copy.txt"))

            # Act & Assert - erro de IO genérico
            with pytest.raises(OSError, match="Erro de IO genérico"):
                service.copy_file(Path("/test/io_error.txt"), Path("/test/copy.txt"))
        finally:
            # Restaurar o método original
            service.copy_file = original_copy_file

    def test_create_directory_operation(self):
        """Testa a operação create_directory."""
        # Arrange
        service = MockFileSystemService()

        # Act & Assert
        service.create_directory(Path("/test/new_dir"))  # Não deve lançar exceção
        service.create_directory(Path("/test/new_dir"), exist_ok=True)  # Não deve lançar exceção

    def test_create_directory_file_exists_error(self):
        """Testa o comportamento quando o diretório já existe e exist_ok é False."""
        # Arrange
        service = MockFileSystemService()

        # Sobrescrever o método create_directory para lançar FileExistsError
        original_create_directory = service.create_directory

        def mock_create_directory_exists(path, exist_ok=True):
            if path.name == "existing_dir" and not exist_ok:
                raise FileExistsError("O diretório já existe")
            return original_create_directory(path, exist_ok)

        service.create_directory = mock_create_directory_exists

        try:
            # Act & Assert - diretório já existe e exist_ok=False
            with pytest.raises(FileExistsError, match="O diretório já existe"):
                service.create_directory(Path("/test/existing_dir"), exist_ok=False)

            # Act & Assert - diretório já existe mas exist_ok=True
            service.create_directory(Path("/test/existing_dir"), exist_ok=True)  # Não deve lançar exceção
        finally:
            # Restaurar o método original
            service.create_directory = original_create_directory

    def test_create_directory_permission_error(self):
        """Testa o comportamento quando não há permissão para criar o diretório."""
        # Arrange
        service = MockFileSystemService()

        # Sobrescrever o método create_directory para lançar PermissionError
        original_create_directory = service.create_directory

        def mock_create_directory_permission(path, exist_ok=True):
            if path.name == "no_permission_dir":
                raise PermissionError("Sem permissão para criar o diretório")
            return original_create_directory(path, exist_ok)

        service.create_directory = mock_create_directory_permission

        try:
            # Act & Assert
            with pytest.raises(PermissionError, match="Sem permissão para criar o diretório"):
                service.create_directory(Path("/test/no_permission_dir"))
        finally:
            # Restaurar o método original
            service.create_directory = original_create_directory

    def test_list_directory_with_extensions(self):
        """Testa a operação list_directory_contents com filtro de extensões."""
        # Arrange
        service = MockFileSystemService()

        # Act
        files = list(service.list_directory_contents(
            Path("/test"),
            recursive=False,
            file_extensions=[".txt", ".jpg"]
        ))

        # Assert
        assert len(files) == 2

        # Act & Assert - diretório não existente
        with pytest.raises(FileNotFoundError):
            list(service.list_directory_contents(Path("/test/nonexistent")))

    def test_list_directory_with_permission_error(self):
        """Testa o comportamento quando não há permissão para acessar o diretório."""
        # Arrange
        service = MockFileSystemService()

        # Sobrescrever o método list_directory_contents para lançar PermissionError
        original_list_directory_contents = service.list_directory_contents

        def mock_list_directory_contents_permission(path, recursive=True, file_extensions=None):
            if path.name == "no_permission":
                raise PermissionError("Sem permissão para acessar o diretório")
            return original_list_directory_contents(path, recursive, file_extensions)

        service.list_directory_contents = mock_list_directory_contents_permission

        try:
            # Act & Assert
            with pytest.raises(PermissionError, match="Sem permissão para acessar o diretório"):
                list(service.list_directory_contents(Path("/test/no_permission")))
        finally:
            # Restaurar o método original
            service.list_directory_contents = original_list_directory_contents

    def test_list_directory_not_a_directory(self):
        """Testa o comportamento quando o caminho não é um diretório."""
        # Arrange
        service = MockFileSystemService()

        # Sobrescrever o método list_directory_contents para lançar NotADirectoryError
        original_list_directory_contents = service.list_directory_contents

        def mock_list_directory_contents_not_dir(path, recursive=True, file_extensions=None):
            if path.name == "file.txt":
                raise NotADirectoryError("O caminho não é um diretório")
            return original_list_directory_contents(path, recursive, file_extensions)

        service.list_directory_contents = mock_list_directory_contents_not_dir

        try:
            # Act & Assert
            with pytest.raises(NotADirectoryError, match="O caminho não é um diretório"):
                list(service.list_directory_contents(Path("/test/file.txt")))
        finally:
            # Restaurar o método original
            service.list_directory_contents = original_list_directory_contents


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

    def test_stream_zip_entries_with_extensions(self):
        """Testa stream_zip_entries com filtro de extensões."""
        # Arrange
        service = MockZipHandlerService()

        # Act
        entries = list(service.stream_zip_entries(
            Path("/test/archive.zip"),
            file_extensions=[".txt"]
        ))

        # Assert
        assert len(entries) == 2

        # Verificar o segundo arquivo
        filename, size, content_func = entries[1]
        assert filename == "file2.txt"
        assert size == 2048
        assert list(content_func()) == [b"conteudo simulado"]

    def test_stream_zip_entries_with_invalid_format(self):
        """Testa o comportamento quando o arquivo ZIP tem formato inválido."""
        # Arrange
        service = MockZipHandlerService()

        # Sobrescrever o método stream_zip_entries para lançar ValueError
        original_stream_zip_entries = service.stream_zip_entries

        def mock_stream_zip_entries_invalid(zip_path, file_extensions=None):
            if zip_path.name == "invalid.zip":
                raise ValueError("Formato de arquivo ZIP inválido")
            return original_stream_zip_entries(zip_path, file_extensions)

        service.stream_zip_entries = mock_stream_zip_entries_invalid

        try:
            # Act & Assert
            with pytest.raises(ValueError, match="Formato de arquivo ZIP inválido"):
                list(service.stream_zip_entries(Path("/test/invalid.zip")))
        finally:
            # Restaurar o método original
            service.stream_zip_entries = original_stream_zip_entries

    def test_stream_zip_entries_with_permission_error(self):
        """Testa o comportamento quando não há permissão para ler o arquivo ZIP."""
        # Arrange
        service = MockZipHandlerService()

        # Sobrescrever o método stream_zip_entries para lançar PermissionError
        original_stream_zip_entries = service.stream_zip_entries

        def mock_stream_zip_entries_permission(zip_path, file_extensions=None):
            if zip_path.name == "no_permission.zip":
                raise PermissionError("Sem permissão para ler o arquivo ZIP")
            return original_stream_zip_entries(zip_path, file_extensions)

        service.stream_zip_entries = mock_stream_zip_entries_permission

        try:
            # Act & Assert
            with pytest.raises(PermissionError, match="Sem permissão para ler o arquivo ZIP"):
                list(service.stream_zip_entries(Path("/test/no_permission.zip")))
        finally:
            # Restaurar o método original
            service.stream_zip_entries = original_stream_zip_entries


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

    def test_create_backup_with_multiple_files(self):
        """Testa a criação de backup com múltiplos arquivos."""
        # Arrange
        service = MockBackupService()
        file_info1 = FileInfo(path=Path("/test/file1.txt"), size=1024)
        file_info2 = FileInfo(path=Path("/test/file2.txt"), size=2048)

        # Act
        backup_id = service.create_backup([
            (Path("/test/file1.txt"), file_info1),
            (Path("/test/file2.txt"), file_info2)
        ])

        # Assert
        assert backup_id == "backup_id_123"

    def test_restore_backup_to_original_location(self):
        """Testa a restauração de backup para o local original."""
        # Arrange
        service = MockBackupService()

        # Act & Assert
        service.restore_backup("backup_id_123")  # Sem especificar diretório alvo

    def test_list_backups_empty(self):
        """Testa o comportamento de list_backups quando não há backups."""
        # Arrange
        service = MockBackupService()

        # Sobrescrever o método list_backups para retornar uma lista vazia
        original_list_backups = service.list_backups
        service.list_backups = lambda: []

        try:
            # Act
            backups = service.list_backups()

            # Assert
            assert len(backups) == 0
        finally:
            # Restaurar o método original
            service.list_backups = original_list_backups
