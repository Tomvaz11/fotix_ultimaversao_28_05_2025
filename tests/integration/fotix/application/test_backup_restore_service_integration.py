"""
Testes de integração para o serviço de backup e restauração do Fotix.

Este módulo contém testes que verificam a integração entre o BackupRestoreService
e os serviços de infraestrutura que ele utiliza (BackupService e FileSystemService).

Cenários testados:
1. Listagem de backups
2. Obtenção de detalhes de um backup específico
3. Restauração de backup para o local original
4. Restauração de backup para um novo local
5. Remoção de backup
"""

import os
import tempfile
import json
from pathlib import Path
from unittest import mock

import pytest

from fotix.application.services.backup_restore_service import BackupRestoreService
from fotix.core.models import FileInfo
from fotix.infrastructure.backup import BackupService
from fotix.infrastructure.file_system import FileSystemService
from fotix.config import get_config, update_config


@pytest.fixture
def temp_dir():
    """Fixture que cria um diretório temporário para testes."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def fs_service():
    """Fixture que cria uma instância do FileSystemService."""
    return FileSystemService()


@pytest.fixture
def backup_service(fs_service, temp_dir):
    """
    Fixture que cria uma instância de BackupService com diretório de backup temporário.
    """
    # Salvar configuração original
    original_backup_dir = get_config().get("backup_dir")

    # Configurar diretório de backup temporário
    backup_dir = temp_dir / "backups"
    update_config("backup_dir", str(backup_dir))

    # Criar serviço de backup
    service = BackupService(file_system_service=fs_service)

    yield service

    # Restaurar configuração original
    if original_backup_dir:
        update_config("backup_dir", original_backup_dir)


@pytest.fixture
def backup_restore_service(backup_service, fs_service):
    """Fixture que cria uma instância do BackupRestoreService."""
    return BackupRestoreService(
        backup_service=backup_service,
        file_system_service=fs_service
    )


@pytest.fixture
def create_test_backup(backup_service, temp_dir, fs_service):
    """
    Fixture que cria um backup de teste.
    
    Retorna um dicionário com informações sobre o backup criado.
    """
    # Criar diretório e arquivo para backup
    original_dir = temp_dir / "original"
    fs_service.create_directory(original_dir)
    
    file_path = original_dir / "test_file.txt"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("Conteúdo de teste para backup")
    
    # Criar FileInfo para o arquivo
    file_info = FileInfo(
        path=file_path,
        size=fs_service.get_file_size(file_path),
        hash="hash_teste",
        creation_time=fs_service.get_creation_time(file_path),
        modification_time=fs_service.get_modification_time(file_path)
    )
    
    # Criar backup
    backup_id = backup_service.create_backup([(file_path, file_info)])
    
    return {
        "backup_id": backup_id,
        "file_path": file_path,
        "file_info": file_info
    }


class TestBackupRestoreServiceIntegration:
    """Testes de integração para o BackupRestoreService."""

    def test_list_backups(self, backup_restore_service, create_test_backup):
        """
        Testa a listagem de backups.
        
        Cenário:
        1. Criar um backup de teste
        2. Listar backups com BackupRestoreService
        3. Verificar se o backup criado está na lista
        """
        # Arrange
        backup_info = create_test_backup
        
        # Act
        backups = backup_restore_service.list_backups()
        
        # Assert
        assert len(backups) == 1
        assert backups[0]["id"] == backup_info["backup_id"]
        assert "date" in backups[0]
        assert "file_count" in backups[0]
        assert backups[0]["file_count"] == 1

    def test_get_backup_details(self, backup_restore_service, create_test_backup):
        """
        Testa a obtenção de detalhes de um backup específico.
        
        Cenário:
        1. Criar um backup de teste
        2. Obter detalhes do backup com BackupRestoreService
        3. Verificar se os detalhes estão corretos
        """
        # Arrange
        backup_info = create_test_backup
        
        # Act
        details = backup_restore_service.get_backup_details(backup_info["backup_id"])
        
        # Assert
        assert details["id"] == backup_info["backup_id"]
        assert "date" in details
        assert "file_count" in details
        assert details["file_count"] == 1

    def test_restore_backup_to_original_location(self, backup_restore_service, create_test_backup, 
                                               fs_service, temp_dir):
        """
        Testa a restauração de um backup para o local original.
        
        Cenário:
        1. Criar um backup de teste
        2. Remover o arquivo original
        3. Restaurar o backup para o local original
        4. Verificar se o arquivo foi restaurado corretamente
        """
        # Arrange
        backup_info = create_test_backup
        original_file_path = backup_info["file_path"]
        
        # Remover o arquivo original
        fs_service.move_to_trash(original_file_path)
        assert not original_file_path.exists()
        
        # Act
        result = backup_restore_service.restore_backup(
            backup_id=backup_info["backup_id"],
            target_directory=None  # Restaurar para local original
        )
        
        # Assert
        assert result["status"] == "success"
        assert original_file_path.exists()
        
        # Verificar conteúdo do arquivo restaurado
        with open(original_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert content == "Conteúdo de teste para backup"

    def test_restore_backup_to_new_location(self, backup_restore_service, create_test_backup, 
                                          fs_service, temp_dir):
        """
        Testa a restauração de um backup para um novo local.
        
        Cenário:
        1. Criar um backup de teste
        2. Restaurar o backup para um novo local
        3. Verificar se o arquivo foi restaurado corretamente no novo local
        """
        # Arrange
        backup_info = create_test_backup
        new_location = temp_dir / "restored"
        
        # Act
        result = backup_restore_service.restore_backup(
            backup_id=backup_info["backup_id"],
            target_directory=new_location
        )
        
        # Assert
        assert result["status"] == "success"
        
        # Verificar se o diretório de destino foi criado
        assert new_location.exists()
        
        # Verificar se o arquivo foi restaurado
        restored_files = list(new_location.glob('**/*'))
        assert len(restored_files) >= 1
        
        # Verificar conteúdo do arquivo restaurado
        restored_file = restored_files[0]
        with open(restored_file, 'r', encoding='utf-8') as f:
            content = f.read()
        assert content == "Conteúdo de teste para backup"

    def test_delete_backup(self, backup_restore_service, create_test_backup, backup_service):
        """
        Testa a remoção de um backup.
        
        Cenário:
        1. Criar um backup de teste
        2. Remover o backup com BackupRestoreService
        3. Verificar se o backup foi removido corretamente
        """
        # Arrange
        backup_info = create_test_backup
        
        # Verificar que o backup existe
        backups_before = backup_restore_service.list_backups()
        assert len(backups_before) == 1
        
        # Act
        result = backup_restore_service.delete_backup(backup_info["backup_id"])
        
        # Assert
        assert result["status"] == "success"
        
        # Verificar que o backup foi removido
        backups_after = backup_restore_service.list_backups()
        assert len(backups_after) == 0
        
        # Verificar que o diretório do backup foi removido
        backup_dir = backup_service.files_dir / backup_info["backup_id"]
        assert not backup_dir.exists()
