"""
Testes unitários para o serviço de backup e restauração.

Este módulo contém testes para o BackupRestoreService, verificando
a funcionalidade de listagem, restauração e exclusão de backups.
"""

import pytest
from pathlib import Path
from unittest import mock

from fotix.application.services.backup_restore_service import BackupRestoreService
from fotix.infrastructure.interfaces import IBackupService, IFileSystemService


class TestBackupRestoreService:
    """Testes para o BackupRestoreService."""

    @pytest.fixture
    def mock_backup_service(self):
        """Cria um mock do serviço de backup."""
        mock_service = mock.MagicMock(spec=IBackupService)

        # Configurar comportamento padrão
        mock_service.list_backups.return_value = [
            {
                "id": "backup1",
                "date": "2023-01-01T12:00:00",
                "file_count": 3,
                "total_size": 1024,
                "files": [
                    {"original_path": "/path/to/file1.jpg", "size": 500},
                    {"original_path": "/path/to/file2.jpg", "size": 300},
                    {"original_path": "/path/to/file3.jpg", "size": 224}
                ]
            },
            {
                "id": "backup2",
                "date": "2023-01-02T14:30:00",
                "file_count": 2,
                "total_size": 2048,
                "files": [
                    {"original_path": "/path/to/file4.jpg", "size": 1024},
                    {"original_path": "/path/to/file5.jpg", "size": 1024}
                ]
            }
        ]

        return mock_service

    @pytest.fixture
    def mock_file_system_service(self):
        """Cria um mock do serviço de sistema de arquivos."""
        mock_service = mock.MagicMock(spec=IFileSystemService)

        # Configurar comportamento padrão
        mock_service.path_exists.return_value = True

        return mock_service

    @pytest.fixture
    def backup_restore_service(self, mock_backup_service, mock_file_system_service):
        """Cria uma instância do serviço de backup e restauração com mocks."""
        return BackupRestoreService(
            backup_service=mock_backup_service,
            file_system_service=mock_file_system_service
        )

    def test_list_backups_success(self, backup_restore_service, mock_backup_service):
        """Testa a listagem de backups com sucesso."""
        # Arrange
        expected_backups = mock_backup_service.list_backups.return_value

        # Act
        result = backup_restore_service.list_backups()

        # Assert
        assert result == expected_backups
        mock_backup_service.list_backups.assert_called_once()

    def test_list_backups_error(self, backup_restore_service, mock_backup_service):
        """Testa a listagem de backups com erro."""
        # Arrange
        mock_backup_service.list_backups.side_effect = Exception("Erro ao listar backups")

        # Act & Assert
        with pytest.raises(IOError) as excinfo:
            backup_restore_service.list_backups()

        assert "Erro ao listar backups" in str(excinfo.value)
        mock_backup_service.list_backups.assert_called_once()

    def test_get_backup_details_success(self, backup_restore_service, mock_backup_service):
        """Testa a obtenção de detalhes de um backup com sucesso."""
        # Arrange
        backup_id = "backup1"
        expected_backup = mock_backup_service.list_backups.return_value[0]

        # Act
        result = backup_restore_service.get_backup_details(backup_id)

        # Assert
        assert result == expected_backup
        mock_backup_service.list_backups.assert_called_once()

    def test_get_backup_details_not_found(self, backup_restore_service):
        """Testa a obtenção de detalhes de um backup inexistente."""
        # Arrange
        backup_id = "nonexistent"

        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            backup_restore_service.get_backup_details(backup_id)

        assert "Backup não encontrado" in str(excinfo.value)

    def test_get_backup_details_error(self, backup_restore_service, mock_backup_service):
        """Testa a obtenção de detalhes de um backup com erro genérico."""
        # Arrange
        backup_id = "backup1"
        mock_backup_service.list_backups.side_effect = Exception("Erro inesperado")

        # Act & Assert
        with pytest.raises(IOError) as excinfo:
            backup_restore_service.get_backup_details(backup_id)

        assert "Erro ao obter detalhes do backup" in str(excinfo.value)

    def test_restore_backup_success(self, backup_restore_service, mock_backup_service):
        """Testa a restauração de um backup com sucesso."""
        # Arrange
        backup_id = "backup1"
        target_directory = Path("/path/to/restore")

        # Act
        result = backup_restore_service.restore_backup(backup_id, target_directory)

        # Assert
        assert result["status"] == "success"
        assert result["backup_info"]["id"] == backup_id
        assert result["target_directory"] == str(target_directory)
        mock_backup_service.restore_backup.assert_called_once_with(backup_id, target_directory)

    def test_restore_backup_to_original_locations(self, backup_restore_service, mock_backup_service):
        """Testa a restauração de um backup para locais originais."""
        # Arrange
        backup_id = "backup1"

        # Act
        result = backup_restore_service.restore_backup(backup_id)

        # Assert
        assert result["status"] == "success"
        assert result["backup_info"]["id"] == backup_id
        assert result["target_directory"] == "locais originais"
        mock_backup_service.restore_backup.assert_called_once_with(backup_id, None)

    def test_restore_backup_create_target_directory(
        self, backup_restore_service, mock_file_system_service, mock_backup_service
    ):
        """Testa a restauração de um backup com criação de diretório alvo."""
        # Arrange
        backup_id = "backup1"
        target_directory = Path("/path/to/restore")
        mock_file_system_service.path_exists.return_value = False

        # Act
        result = backup_restore_service.restore_backup(backup_id, target_directory)

        # Assert
        assert result["status"] == "success"
        mock_file_system_service.path_exists.assert_called_once_with(target_directory)
        mock_file_system_service.create_directory.assert_called_once_with(target_directory)
        mock_backup_service.restore_backup.assert_called_once_with(backup_id, target_directory)

    def test_restore_backup_create_target_directory_error(
        self, backup_restore_service, mock_file_system_service, mock_backup_service
    ):
        """Testa a restauração de um backup com erro ao criar diretório alvo."""
        # Arrange
        backup_id = "backup1"
        target_directory = Path("/path/to/restore")
        mock_file_system_service.path_exists.return_value = False
        mock_file_system_service.create_directory.side_effect = Exception("Erro ao criar diretório")

        # Act & Assert
        with pytest.raises(IOError) as excinfo:
            backup_restore_service.restore_backup(backup_id, target_directory)

        assert "Erro ao criar diretório alvo" in str(excinfo.value)
        mock_file_system_service.path_exists.assert_called_once_with(target_directory)
        mock_file_system_service.create_directory.assert_called_once_with(target_directory)
        mock_backup_service.restore_backup.assert_not_called()

    def test_restore_backup_not_found(self, backup_restore_service, mock_backup_service):
        """Testa a restauração de um backup inexistente."""
        # Arrange
        backup_id = "nonexistent"
        mock_backup_service.restore_backup.side_effect = ValueError(f"Backup não encontrado: {backup_id}")

        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            backup_restore_service.restore_backup(backup_id)

        assert "Backup não encontrado" in str(excinfo.value)

    def test_restore_backup_error(self, backup_restore_service, mock_backup_service):
        """Testa a restauração de um backup com erro."""
        # Arrange
        backup_id = "backup1"
        mock_backup_service.restore_backup.side_effect = Exception("Erro ao restaurar")

        # Act & Assert
        with pytest.raises(IOError) as excinfo:
            backup_restore_service.restore_backup(backup_id)

        assert "Erro ao restaurar backup" in str(excinfo.value)

    def test_delete_backup_success(self, backup_restore_service, mock_backup_service):
        """Testa a remoção de um backup com sucesso."""
        # Arrange
        backup_id = "backup1"

        # Act
        result = backup_restore_service.delete_backup(backup_id)

        # Assert
        assert result["status"] == "success"
        assert result["backup_info"]["id"] == backup_id
        mock_backup_service.delete_backup.assert_called_once_with(backup_id)

    def test_delete_backup_not_found(self, backup_restore_service):
        """Testa a remoção de um backup inexistente."""
        # Arrange
        backup_id = "nonexistent"

        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            backup_restore_service.delete_backup(backup_id)

        assert "Backup não encontrado" in str(excinfo.value)

    def test_delete_backup_error(self, backup_restore_service, mock_backup_service):
        """Testa a remoção de um backup com erro."""
        # Arrange
        backup_id = "backup1"
        mock_backup_service.delete_backup.side_effect = Exception("Erro ao remover")

        # Act & Assert
        with pytest.raises(IOError) as excinfo:
            backup_restore_service.delete_backup(backup_id)

        assert "Erro ao remover backup" in str(excinfo.value)
