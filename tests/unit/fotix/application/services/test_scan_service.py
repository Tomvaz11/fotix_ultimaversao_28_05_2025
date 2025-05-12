"""
Testes unitários para o serviço de varredura do Fotix.

Este módulo contém testes para verificar o funcionamento do ScanService,
responsável por orquestrar o processo de varredura de diretórios e arquivos.
"""

from pathlib import Path
from unittest.mock import Mock, patch
import pytest

from fotix.application.services.scan_service import ScanService
from fotix.core.models import DuplicateSet, FileInfo


@pytest.fixture
def mock_duplicate_finder():
    """Fixture que cria um mock do serviço de detecção de duplicatas."""
    mock = Mock()
    mock.find_duplicates.return_value = []
    return mock


@pytest.fixture
def mock_file_system():
    """Fixture que cria um mock do serviço de sistema de arquivos."""
    mock = Mock()
    mock.path_exists.return_value = True
    return mock


@pytest.fixture
def mock_zip_handler():
    """Fixture que cria um mock do serviço de manipulação de ZIPs."""
    return Mock()


@pytest.fixture
def mock_concurrency():
    """Fixture que cria um mock do serviço de concorrência."""
    return Mock()


@pytest.fixture
def scan_service(mock_duplicate_finder, mock_file_system, mock_zip_handler, mock_concurrency):
    """Fixture que cria uma instância do ScanService com dependências mockadas."""
    return ScanService(
        duplicate_finder_service=mock_duplicate_finder,
        file_system_service=mock_file_system,
        zip_handler_service=mock_zip_handler,
        concurrency_service=mock_concurrency
    )


class TestScanService:
    """Testes para o ScanService."""

    def test_initialization(self, scan_service, mock_duplicate_finder, mock_file_system,
                           mock_zip_handler, mock_concurrency):
        """Testa se o serviço é inicializado corretamente com suas dependências."""
        assert scan_service.duplicate_finder_service == mock_duplicate_finder
        assert scan_service.file_system_service == mock_file_system
        assert scan_service.zip_handler_service == mock_zip_handler
        assert scan_service.concurrency_service == mock_concurrency

    def test_scan_directories_calls_duplicate_finder(self, scan_service, mock_duplicate_finder):
        """Testa se o método scan_directories chama corretamente o serviço de detecção de duplicatas."""
        # Arrange
        directories = [Path("/test/dir1"), Path("/test/dir2")]
        include_zips = True
        progress_callback = lambda _: None

        # Configurar mock para simular que os diretórios são válidos
        with patch.object(Path, "is_dir", return_value=True):
            # Act
            result = scan_service.scan_directories(
                directories=directories,
                include_zips=include_zips,
                progress_callback=progress_callback
            )

            # Assert
            mock_duplicate_finder.find_duplicates.assert_called_once_with(
                scan_paths=directories,
                include_zips=include_zips,
                progress_callback=progress_callback
            )
            assert result == []

    def test_validate_directories_with_valid_dirs(self, scan_service, mock_file_system):
        """Testa a validação de diretórios quando todos são válidos."""
        # Arrange
        directories = [Path("/test/dir1"), Path("/test/dir2")]
        mock_file_system.path_exists.return_value = True

        # Configurar mock para simular que os diretórios são válidos
        with patch.object(Path, "is_dir", return_value=True):
            # Act & Assert - não deve lançar exceção
            scan_service._validate_directories(directories)

            # Verificar se path_exists foi chamado para cada diretório
            assert mock_file_system.path_exists.call_count == len(directories)

    def test_validate_directories_with_nonexistent_dir(self, scan_service, mock_file_system):
        """Testa a validação de diretórios quando um não existe."""
        # Arrange
        directories = [Path("/test/dir1"), Path("/test/nonexistent")]

        # Configurar mock para simular que o segundo diretório não existe
        mock_file_system.path_exists.side_effect = lambda p: p != Path("/test/nonexistent")

        # Configurar mock para simular que o primeiro diretório é um diretório válido
        with patch.object(Path, "is_dir", return_value=True):
            # Act & Assert
            with pytest.raises(ValueError) as excinfo:
                scan_service._validate_directories(directories)

            # Verificar mensagem de erro
            assert "'\\test\\nonexistent' não existe" in str(excinfo.value)

    def test_validate_directories_with_non_directory(self, scan_service, mock_file_system):
        """Testa a validação de diretórios quando um não é um diretório."""
        # Arrange
        directories = [Path("/test/dir1"), Path("/test/file.txt")]
        mock_file_system.path_exists.return_value = True

        # Configurar mock para simular que o segundo caminho não é um diretório
        with patch.object(Path, "is_dir", return_value=False):
            # Act & Assert
            with pytest.raises(ValueError) as excinfo:
                scan_service._validate_directories(directories)

            # Verificar mensagem de erro
            assert "não é um diretório" in str(excinfo.value)

    def test_filter_nested_directories(self, scan_service):
        """Testa a filtragem de diretórios aninhados."""
        # Arrange
        parent_dir = Path("/test/parent")
        child_dir = Path("/test/parent/child")
        other_dir = Path("/test/other")

        directories = [parent_dir, child_dir, other_dir]

        # Act
        result = scan_service._filter_nested_directories(directories)

        # Assert
        assert len(result) == 2
        assert parent_dir in result
        assert other_dir in result
        assert child_dir not in result

    def test_prepare_scan_paths(self, scan_service):
        """Testa a preparação de caminhos para varredura."""
        # Arrange
        directories = [Path("/test/dir1"), Path("/test/dir2")]

        # Act
        result = scan_service._prepare_scan_paths(directories)

        # Assert
        assert result == directories

    def test_scan_directories_with_duplicate_sets(self, scan_service, mock_duplicate_finder):
        """Testa o retorno de conjuntos de duplicatas."""
        # Arrange
        directories = [Path("/test/dir1")]

        # Criar alguns conjuntos de duplicatas para o mock retornar
        file_info1 = FileInfo(path=Path("/test/dir1/file1.jpg"), size=1024)
        file_info2 = FileInfo(path=Path("/test/dir1/file2.jpg"), size=1024)
        duplicate_set = DuplicateSet(files=[file_info1, file_info2], hash="abc123")

        mock_duplicate_finder.find_duplicates.return_value = [duplicate_set]

        # Configurar mock para simular que os diretórios são válidos
        with patch.object(Path, "is_dir", return_value=True):
            # Act
            result = scan_service.scan_directories(directories=directories)

            # Assert
            assert len(result) == 1
            assert result[0].hash == "abc123"
            assert len(result[0].files) == 2

    def test_scan_directories_with_nested_directories(self, scan_service, mock_duplicate_finder):
        """Testa a varredura com diretórios aninhados."""
        # Arrange
        parent_dir = Path("/test/parent")
        child_dir = Path("/test/parent/child")
        directories = [parent_dir, child_dir]

        # Configurar mock para simular que os diretórios são válidos
        with patch.object(Path, "is_dir", return_value=True):
            # Configurar mock para simular a detecção de subdiretórios
            with patch.object(Path, "relative_to", side_effect=lambda p: None if str(p) in str(child_dir) else ValueError()):
                # Act
                scan_service.scan_directories(directories=directories)

                # Assert
                # Verificar se o duplicate_finder foi chamado apenas com o diretório pai
                mock_duplicate_finder.find_duplicates.assert_called_once()
                call_args = mock_duplicate_finder.find_duplicates.call_args[1]
                assert len(call_args["scan_paths"]) == 1
                assert call_args["scan_paths"][0] == parent_dir
