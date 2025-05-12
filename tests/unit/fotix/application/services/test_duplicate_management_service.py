"""
Testes unitários para o serviço de gerenciamento de duplicatas.

Este módulo contém testes para verificar o funcionamento correto do serviço
de gerenciamento de duplicatas (DuplicateManagementService).
"""

from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

from fotix.application.services.duplicate_management_service import DuplicateManagementService
from fotix.core.models import DuplicateSet, FileInfo


class TestDuplicateManagementService:
    """Testes para o DuplicateManagementService."""

    @pytest.fixture
    def mock_selection_strategy(self):
        """Fixture para criar um mock da estratégia de seleção."""
        strategy = MagicMock()
        return strategy

    @pytest.fixture
    def mock_file_system_service(self):
        """Fixture para criar um mock do serviço de sistema de arquivos."""
        service = MagicMock()
        return service

    @pytest.fixture
    def mock_backup_service(self):
        """Fixture para criar um mock do serviço de backup."""
        service = MagicMock()
        service.create_backup.return_value = "backup_id_123"
        return service

    @pytest.fixture
    def service(self, mock_selection_strategy, mock_file_system_service, mock_backup_service):
        """Fixture para criar uma instância do serviço com mocks."""
        return DuplicateManagementService(
            selection_strategy=mock_selection_strategy,
            file_system_service=mock_file_system_service,
            backup_service=mock_backup_service
        )

    @pytest.fixture
    def sample_duplicate_set(self):
        """Fixture para criar um conjunto de duplicatas de exemplo."""
        return DuplicateSet(
            files=[
                FileInfo(path=Path("/path/to/file1.jpg"), size=1024, hash="abc123"),
                FileInfo(path=Path("/path/to/file2.jpg"), size=1024, hash="abc123"),
                FileInfo(path=Path("/path/to/file3.jpg"), size=1024, hash="abc123")
            ],
            hash="abc123"
        )

    def test_init(self, mock_selection_strategy, mock_file_system_service, mock_backup_service):
        """Testa se o serviço é inicializado corretamente."""
        # Act
        service = DuplicateManagementService(
            selection_strategy=mock_selection_strategy,
            file_system_service=mock_file_system_service,
            backup_service=mock_backup_service
        )

        # Assert
        assert service.selection_strategy == mock_selection_strategy
        assert service.file_system_service == mock_file_system_service
        assert service.backup_service == mock_backup_service

    def test_process_duplicate_set_with_strategy(self, service, sample_duplicate_set, 
                                               mock_selection_strategy, mock_file_system_service, 
                                               mock_backup_service):
        """Testa o processamento de um conjunto de duplicatas usando a estratégia de seleção."""
        # Arrange
        file_to_keep = sample_duplicate_set.files[0]
        mock_selection_strategy.select_file_to_keep.return_value = file_to_keep

        # Act
        result = service.process_duplicate_set(sample_duplicate_set)

        # Assert
        assert result['kept_file'] == file_to_keep
        assert len(result['removed_files']) == 2
        assert result['backup_id'] == "backup_id_123"
        assert result['error'] is None

        # Verificar se os métodos corretos foram chamados
        mock_selection_strategy.select_file_to_keep.assert_called_once_with(sample_duplicate_set)
        assert mock_backup_service.create_backup.call_count == 1
        assert mock_file_system_service.move_to_trash.call_count == 2

    def test_process_duplicate_set_with_custom_selection(self, service, sample_duplicate_set,
                                                      mock_selection_strategy, mock_file_system_service,
                                                      mock_backup_service):
        """Testa o processamento de um conjunto de duplicatas usando uma seleção personalizada."""
        # Arrange
        custom_selection = sample_duplicate_set.files[1]

        # Act
        result = service.process_duplicate_set(
            duplicate_set=sample_duplicate_set,
            custom_selection=custom_selection
        )

        # Assert
        assert result['kept_file'] == custom_selection
        assert len(result['removed_files']) == 2
        assert sample_duplicate_set.files[0] in result['removed_files']
        assert sample_duplicate_set.files[2] in result['removed_files']
        assert result['backup_id'] == "backup_id_123"
        assert result['error'] is None

        # Verificar se os métodos corretos foram chamados
        mock_selection_strategy.select_file_to_keep.assert_not_called()
        assert mock_backup_service.create_backup.call_count == 1
        assert mock_file_system_service.move_to_trash.call_count == 2

    def test_process_duplicate_set_without_backup(self, service, sample_duplicate_set,
                                               mock_selection_strategy, mock_file_system_service,
                                               mock_backup_service):
        """Testa o processamento de um conjunto de duplicatas sem criar backup."""
        # Arrange
        file_to_keep = sample_duplicate_set.files[0]
        mock_selection_strategy.select_file_to_keep.return_value = file_to_keep

        # Act
        result = service.process_duplicate_set(
            duplicate_set=sample_duplicate_set,
            create_backup=False
        )

        # Assert
        assert result['kept_file'] == file_to_keep
        assert len(result['removed_files']) == 2
        assert result['backup_id'] is None
        assert result['error'] is None

        # Verificar se os métodos corretos foram chamados
        mock_selection_strategy.select_file_to_keep.assert_called_once_with(sample_duplicate_set)
        mock_backup_service.create_backup.assert_not_called()
        assert mock_file_system_service.move_to_trash.call_count == 2

    def test_process_empty_duplicate_set(self, service):
        """Testa se o processamento de um conjunto vazio levanta ValueError."""
        # Arrange
        empty_set = DuplicateSet(files=[], hash="empty")

        # Act & Assert
        with pytest.raises(ValueError, match="O conjunto de duplicatas está vazio"):
            service.process_duplicate_set(empty_set)

    def test_process_duplicate_set_with_invalid_custom_selection(self, service, sample_duplicate_set):
        """Testa se o processamento com uma seleção personalizada inválida retorna erro."""
        # Arrange
        invalid_selection = FileInfo(path=Path("/path/to/nonexistent.jpg"), size=1024, hash="xyz789")

        # Act
        result = service.process_duplicate_set(
            duplicate_set=sample_duplicate_set,
            custom_selection=invalid_selection
        )

        # Assert
        assert result['kept_file'] is None
        assert len(result['removed_files']) == 0
        assert result['backup_id'] is None
        assert result['error'] is not None
        assert "não está no conjunto de duplicatas" in result['error']

    def test_backup_files(self, service, mock_backup_service):
        """Testa a criação de backup de arquivos."""
        # Arrange
        files = [
            FileInfo(path=Path("/path/to/file1.jpg"), size=1024, hash="abc123"),
            FileInfo(path=Path("/path/to/file2.jpg"), size=1024, hash="abc123")
        ]

        # Act
        backup_id = service._backup_files(files)

        # Assert
        assert backup_id == "backup_id_123"
        mock_backup_service.create_backup.assert_called_once()
        # Verificar se os argumentos corretos foram passados
        args = mock_backup_service.create_backup.call_args[0][0]
        assert len(args) == 2
        assert args[0][0] == Path("/path/to/file1.jpg")
        assert args[1][0] == Path("/path/to/file2.jpg")

    def test_backup_files_with_zip_files(self, service, mock_backup_service):
        """Testa a criação de backup ignorando arquivos dentro de ZIPs."""
        # Arrange
        files = [
            FileInfo(path=Path("/path/to/file1.jpg"), size=1024, hash="abc123"),
            FileInfo(
                path=Path("internal/path/file2.jpg"), 
                size=1024, 
                hash="abc123", 
                in_zip=True,
                zip_path=Path("/path/to/archive.zip")
            )
        ]

        # Act
        backup_id = service._backup_files(files)

        # Assert
        assert backup_id == "backup_id_123"
        mock_backup_service.create_backup.assert_called_once()
        # Verificar se apenas o arquivo normal foi incluído no backup
        args = mock_backup_service.create_backup.call_args[0][0]
        assert len(args) == 1
        assert args[0][0] == Path("/path/to/file1.jpg")

    def test_backup_files_empty_list(self, service, mock_backup_service):
        """Testa a criação de backup com uma lista vazia."""
        # Act
        backup_id = service._backup_files([])

        # Assert
        assert backup_id == "no_backup_needed"
        mock_backup_service.create_backup.assert_not_called()

    def test_backup_files_only_zip_files(self, service, mock_backup_service):
        """Testa a criação de backup com apenas arquivos dentro de ZIPs."""
        # Arrange
        files = [
            FileInfo(
                path=Path("internal/path/file.jpg"), 
                size=1024, 
                hash="abc123", 
                in_zip=True,
                zip_path=Path("/path/to/archive.zip")
            )
        ]

        # Act
        backup_id = service._backup_files(files)

        # Assert
        assert backup_id == "no_backup_needed"
        mock_backup_service.create_backup.assert_not_called()

    def test_remove_file(self, service, mock_file_system_service):
        """Testa a remoção de um arquivo."""
        # Arrange
        file_info = FileInfo(path=Path("/path/to/file.jpg"), size=1024, hash="abc123")

        # Act
        service._remove_file(file_info)

        # Assert
        mock_file_system_service.move_to_trash.assert_called_once_with(Path("/path/to/file.jpg"))

    def test_remove_file_in_zip(self, service, mock_file_system_service):
        """Testa a tentativa de remoção de um arquivo dentro de ZIP."""
        # Arrange
        file_info = FileInfo(
            path=Path("internal/path/file.jpg"), 
            size=1024, 
            hash="abc123", 
            in_zip=True,
            zip_path=Path("/path/to/archive.zip")
        )

        # Act
        service._remove_file(file_info)

        # Assert
        mock_file_system_service.move_to_trash.assert_not_called()

    def test_process_duplicate_set_with_backup_error(self, service, sample_duplicate_set,
                                                  mock_selection_strategy, mock_backup_service):
        """Testa o processamento quando ocorre um erro no backup."""
        # Arrange
        file_to_keep = sample_duplicate_set.files[0]
        mock_selection_strategy.select_file_to_keep.return_value = file_to_keep
        mock_backup_service.create_backup.side_effect = Exception("Erro de backup")

        # Act
        result = service.process_duplicate_set(sample_duplicate_set)

        # Assert
        assert result['kept_file'] is None
        assert len(result['removed_files']) == 0
        assert result['backup_id'] is None
        assert result['error'] is not None
        assert "Erro de backup" in result['error']

    def test_process_duplicate_set_with_remove_error(self, service, sample_duplicate_set,
                                                  mock_selection_strategy, mock_file_system_service):
        """Testa o processamento quando ocorre um erro na remoção."""
        # Arrange
        file_to_keep = sample_duplicate_set.files[0]
        mock_selection_strategy.select_file_to_keep.return_value = file_to_keep
        mock_file_system_service.move_to_trash.side_effect = Exception("Erro ao mover para lixeira")

        # Act
        result = service.process_duplicate_set(sample_duplicate_set)

        # Assert
        assert result['kept_file'] is None
        assert len(result['removed_files']) == 0
        assert result['backup_id'] is not None  # O backup deve ter sido criado
        assert result['error'] is not None
        assert "Erro ao mover para lixeira" in result['error']
