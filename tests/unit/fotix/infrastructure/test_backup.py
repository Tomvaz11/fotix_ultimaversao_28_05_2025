"""
Testes unitários para o módulo de backup.

Este módulo contém testes para a implementação do serviço de backup,
verificando a criação, listagem, restauração e exclusão de backups.
"""

import json
import os
import shutil
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from unittest import mock

import pytest

from fotix.core.models import FileInfo
from fotix.infrastructure.backup import BackupService


@pytest.fixture
def temp_dir():
    """
    Fixture que cria um diretório temporário para os testes.

    Returns:
        Path: Caminho para o diretório temporário.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_config(temp_dir, monkeypatch):
    """
    Fixture que configura um diretório de backup temporário.

    Args:
        temp_dir: Diretório temporário para os testes.
        monkeypatch: Fixture do pytest para modificar objetos.

    Returns:
        Path: Caminho para o diretório de backup temporário.
    """
    backup_dir = temp_dir / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Mock da função get_backup_dir
    def mock_get_backup_dir():
        return backup_dir

    monkeypatch.setattr("fotix.infrastructure.backup.get_backup_dir", mock_get_backup_dir)

    return backup_dir


@pytest.fixture
def test_files(temp_dir):
    """
    Fixture que cria arquivos de teste.

    Args:
        temp_dir: Diretório temporário para os testes.

    Returns:
        list: Lista de tuplas (Path, FileInfo) para os arquivos de teste.
    """
    # Criar diretório de arquivos de teste
    files_dir = temp_dir / "test_files"
    files_dir.mkdir(parents=True, exist_ok=True)

    # Criar alguns arquivos de teste
    files = []
    for i in range(3):
        file_path = files_dir / f"test_file_{i}.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"Conteúdo do arquivo de teste {i}")

        # Criar FileInfo para o arquivo
        file_info = FileInfo(
            path=file_path,
            size=os.path.getsize(file_path),
            hash=f"hash_{i}",  # Hash simulado
            creation_time=os.path.getctime(file_path),
            modification_time=os.path.getmtime(file_path)
        )

        files.append((file_path, file_info))

    return files


@pytest.fixture
def backup_service(mock_config):
    """
    Fixture que cria uma instância do serviço de backup.

    Args:
        mock_config: Configuração mockada.

    Returns:
        BackupService: Instância do serviço de backup.
    """
    return BackupService()


@pytest.fixture
def existing_backup(backup_service, test_files):
    """
    Fixture que cria um backup existente para testes.

    Args:
        backup_service: Instância do serviço de backup.
        test_files: Arquivos de teste.

    Returns:
        str: ID do backup criado.
    """
    return backup_service.create_backup(test_files)


def test_create_backup(backup_service, test_files):
    """
    Testa a criação de um backup.

    Args:
        backup_service: Instância do serviço de backup.
        test_files: Arquivos de teste.
    """
    # Criar backup
    backup_id = backup_service.create_backup(test_files)

    # Verificar se o ID foi gerado
    assert backup_id is not None
    assert isinstance(backup_id, str)

    # Verificar se os diretórios foram criados
    metadata_path = backup_service.metadata_dir / f"{backup_id}.json"
    backup_files_dir = backup_service.files_dir / backup_id

    assert metadata_path.exists()
    assert backup_files_dir.exists()

    # Verificar o conteúdo do arquivo de metadados
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    assert metadata["id"] == backup_id
    assert "date" in metadata
    assert len(metadata["files"]) == len(test_files)
    assert metadata["file_count"] == len(test_files)

    # Verificar se os arquivos foram copiados
    for file_metadata in metadata["files"]:
        backup_filename = file_metadata["backup_filename"]
        backup_file_path = backup_files_dir / backup_filename
        assert backup_file_path.exists()


def test_create_backup_with_missing_file(backup_service, test_files, temp_dir):
    """
    Testa a criação de um backup com um arquivo inexistente.

    Args:
        backup_service: Instância do serviço de backup.
        test_files: Arquivos de teste.
        temp_dir: Diretório temporário.
    """
    # Criar um arquivo que não existe
    non_existent_path = temp_dir / "non_existent.txt"
    non_existent_info = FileInfo(
        path=non_existent_path,
        size=0,
        hash="non_existent_hash"
    )

    # Adicionar o arquivo inexistente à lista
    files_with_missing = test_files + [(non_existent_path, non_existent_info)]

    # Criar backup (deve ignorar o arquivo inexistente)
    backup_id = backup_service.create_backup(files_with_missing)

    # Verificar se o backup foi criado com os arquivos existentes
    metadata_path = backup_service.metadata_dir / f"{backup_id}.json"
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    # Deve ter apenas os arquivos existentes
    assert len(metadata["files"]) == len(test_files)


def test_list_backups(backup_service, existing_backup):
    """
    Testa a listagem de backups.

    Args:
        backup_service: Instância do serviço de backup.
        existing_backup: ID de um backup existente.
    """
    # Listar backups
    backups = backup_service.list_backups()

    # Verificar se o backup existente está na lista
    assert len(backups) >= 1

    # Verificar se o backup tem as informações corretas
    backup = next((b for b in backups if b["id"] == existing_backup), None)
    assert backup is not None
    assert "date" in backup
    assert "file_count" in backup
    assert "total_size" in backup


def test_restore_backup(backup_service, existing_backup, test_files, temp_dir):
    """
    Testa a restauração de um backup para um diretório específico.

    Args:
        backup_service: Instância do serviço de backup.
        existing_backup: ID de um backup existente.
        test_files: Arquivos de teste originais.
        temp_dir: Diretório temporário.
    """
    # Criar diretório de restauração
    restore_dir = temp_dir / "restore"
    restore_dir.mkdir(parents=True, exist_ok=True)

    # Restaurar backup
    backup_service.restore_backup(existing_backup, restore_dir)

    # Verificar se os arquivos foram restaurados
    for file_path, _ in test_files:
        restored_path = restore_dir / file_path.name
        assert restored_path.exists()

        # Verificar conteúdo
        with open(file_path, 'r', encoding='utf-8') as original_file:
            original_content = original_file.read()

        with open(restored_path, 'r', encoding='utf-8') as restored_file:
            restored_content = restored_file.read()

        assert restored_content == original_content


def test_restore_backup_to_original_location(backup_service, existing_backup, test_files, temp_dir):
    """
    Testa a restauração de um backup para os locais originais.

    Args:
        backup_service: Instância do serviço de backup.
        existing_backup: ID de um backup existente.
        test_files: Arquivos de teste originais.
        temp_dir: Diretório temporário.
    """
    # Remover os arquivos originais
    for file_path, _ in test_files:
        file_path.unlink()
        assert not file_path.exists()

    # Restaurar backup para os locais originais
    backup_service.restore_backup(existing_backup)

    # Verificar se os arquivos foram restaurados nos locais originais
    for file_path, _ in test_files:
        assert file_path.exists()


def test_restore_nonexistent_backup(backup_service):
    """
    Testa a restauração de um backup inexistente.

    Args:
        backup_service: Instância do serviço de backup.
    """
    with pytest.raises(ValueError):
        backup_service.restore_backup("nonexistent_id")


def test_delete_backup(backup_service, existing_backup):
    """
    Testa a exclusão de um backup.

    Args:
        backup_service: Instância do serviço de backup.
        existing_backup: ID de um backup existente.
    """
    # Verificar que o backup existe
    metadata_path = backup_service.metadata_dir / f"{existing_backup}.json"
    backup_files_dir = backup_service.files_dir / existing_backup

    assert metadata_path.exists()
    assert backup_files_dir.exists()

    # Excluir o backup
    backup_service.delete_backup(existing_backup)

    # Verificar que o backup foi removido
    assert not metadata_path.exists()
    assert not backup_files_dir.exists()

    # Verificar que o backup não aparece mais na listagem
    backups = backup_service.list_backups()
    assert not any(b["id"] == existing_backup for b in backups)


def test_delete_nonexistent_backup(backup_service):
    """
    Testa a exclusão de um backup inexistente.

    Args:
        backup_service: Instância do serviço de backup.
    """
    with pytest.raises(ValueError):
        backup_service.delete_backup("nonexistent_id")


def test_backup_with_file_system_service(mock_config, test_files):
    """
    Testa o backup usando um serviço de sistema de arquivos mockado.

    Args:
        mock_config: Configuração mockada.
        test_files: Arquivos de teste.
    """
    # Criar mock para o FileSystemService
    mock_fs = mock.MagicMock()

    # Criar serviço de backup com o mock
    backup_service = BackupService(file_system_service=mock_fs)

    # Criar backup
    backup_id = backup_service.create_backup(test_files)

    # Verificar se o método copy_file do FileSystemService foi chamado
    assert mock_fs.copy_file.call_count == len(test_files)

    # Verificar se o backup foi criado corretamente
    metadata_path = backup_service.metadata_dir / f"{backup_id}.json"
    assert metadata_path.exists()


def test_create_backup_error_handling(mock_config, test_files):
    """
    Testa o tratamento de erros durante a criação de backup.

    Args:
        mock_config: Configuração mockada.
        test_files: Arquivos de teste.
    """
    # Criar mock para o FileSystemService que lança exceção
    mock_fs = mock.MagicMock()
    mock_fs.copy_file.side_effect = PermissionError("Sem permissão para copiar")

    # Criar serviço de backup com o mock
    backup_service = BackupService(file_system_service=mock_fs)

    # Tentar criar backup (deve lançar exceção)
    with pytest.raises(PermissionError):
        backup_service.create_backup(test_files)


def test_list_backups_error_handling(mock_config):
    """
    Testa o tratamento de erros durante a listagem de backups.

    Args:
        mock_config: Configuração mockada.
    """
    # Criar serviço de backup
    backup_service = BackupService()

    # Criar um arquivo de metadados inválido (JSON mal-formado)
    metadata_dir = backup_service.metadata_dir
    invalid_metadata_path = metadata_dir / "invalid.json"
    with open(invalid_metadata_path, 'w', encoding='utf-8') as f:
        f.write("{ invalid json")

    # Listar backups (deve ignorar o arquivo inválido)
    backups = backup_service.list_backups()

    # Verificar que a função não falhou, mesmo com um arquivo inválido
    assert isinstance(backups, list)


def test_restore_backup_with_file_system_service(backup_service, existing_backup, temp_dir):
    """
    Testa a restauração de backup usando um serviço de sistema de arquivos mockado.

    Args:
        backup_service: Instância do serviço de backup.
        existing_backup: ID de um backup existente.
        temp_dir: Diretório temporário.
    """
    # Substituir o file_system_service por um mock
    mock_fs = mock.MagicMock()
    backup_service.file_system_service = mock_fs

    # Restaurar backup
    restore_dir = temp_dir / "restore_mock"
    backup_service.restore_backup(existing_backup, restore_dir)

    # Verificar se o método copy_file do FileSystemService foi chamado
    assert mock_fs.copy_file.call_count > 0


def test_restore_backup_error_handling(backup_service, existing_backup, temp_dir):
    """
    Testa o tratamento de erros durante a restauração de backup.

    Args:
        backup_service: Instância do serviço de backup.
        existing_backup: ID de um backup existente.
        temp_dir: Diretório temporário.
    """
    # Substituir o file_system_service por um mock que lança exceção
    mock_fs = mock.MagicMock()
    mock_fs.copy_file.side_effect = FileExistsError("Arquivo já existe")
    backup_service.file_system_service = mock_fs

    # Tentar restaurar backup (deve lançar exceção)
    with pytest.raises(FileExistsError):
        backup_service.restore_backup(existing_backup, temp_dir / "restore_error")


def test_delete_backup_error_handling(backup_service, existing_backup):
    """
    Testa o tratamento de erros durante a exclusão de backup.

    Args:
        backup_service: Instância do serviço de backup.
        existing_backup: ID de um backup existente.
    """
    # Criar um cenário onde o arquivo de metadados existe mas o diretório de arquivos não
    backup_files_dir = backup_service.files_dir / existing_backup
    shutil.rmtree(backup_files_dir)

    # Excluir o backup (deve funcionar mesmo sem o diretório de arquivos)
    backup_service.delete_backup(existing_backup)

    # Verificar que o arquivo de metadados foi removido
    metadata_path = backup_service.metadata_dir / f"{existing_backup}.json"
    assert not metadata_path.exists()


def test_create_backup_metadata_error(mock_config, test_files, monkeypatch):
    """
    Testa o tratamento de erros ao salvar metadados durante a criação de backup.

    Args:
        mock_config: Configuração mockada.
        test_files: Arquivos de teste.
        monkeypatch: Fixture do pytest para modificar objetos.
    """
    # Criar serviço de backup
    backup_service = BackupService()

    # Mock da função open para lançar exceção ao tentar salvar metadados
    original_open = open

    def mock_open(*args, **kwargs):
        if args[0].name.endswith('.json') and 'w' in args[1]:
            raise PermissionError("Sem permissão para escrever metadados")
        return original_open(*args, **kwargs)

    # Aplicar o mock
    monkeypatch.setattr("builtins.open", mock_open)

    # Tentar criar backup (deve lançar IOError)
    with pytest.raises(IOError):
        backup_service.create_backup(test_files)


def test_restore_backup_metadata_error(mock_config, monkeypatch):
    """
    Testa o tratamento de erros ao ler metadados durante a restauração de backup.

    Args:
        mock_config: Configuração mockada.
        monkeypatch: Fixture do pytest para modificar objetos.
    """
    # Criar serviço de backup
    backup_service = BackupService()

    # Criar um ID de backup que existe, mas com metadados corrompidos
    backup_id = "corrupted_metadata"
    metadata_path = backup_service.metadata_dir / f"{backup_id}.json"
    backup_files_dir = backup_service.files_dir / backup_id

    # Criar diretório de backup
    backup_files_dir.mkdir(parents=True, exist_ok=True)

    # Criar arquivo de metadados corrompido
    with open(metadata_path, 'w', encoding='utf-8') as f:
        f.write("{ corrupted json")

    # Tentar restaurar backup (deve lançar IOError)
    with pytest.raises(IOError):
        backup_service.restore_backup(backup_id)


def test_create_backup_with_empty_list(mock_config):
    """
    Testa a criação de backup com uma lista vazia de arquivos.

    Args:
        mock_config: Configuração mockada.
    """
    # Criar serviço de backup
    backup_service = BackupService()

    # Criar backup com lista vazia
    backup_id = backup_service.create_backup([])

    # Verificar se o backup foi criado
    assert backup_id is not None

    # Verificar metadados
    metadata_path = backup_service.metadata_dir / f"{backup_id}.json"
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    # Verificar que não há arquivos no backup
    assert len(metadata["files"]) == 0
    assert metadata["file_count"] == 0


def test_create_backup_copy_error(mock_config, test_files, monkeypatch):
    """
    Testa o tratamento de erros ao copiar arquivos durante a criação de backup.

    Args:
        mock_config: Configuração mockada.
        test_files: Arquivos de teste.
        monkeypatch: Fixture do pytest para modificar objetos.
    """
    # Criar serviço de backup
    backup_service = BackupService()

    # Mock da função shutil.copy2 para lançar exceção
    def mock_copy2(*args, **kwargs):
        raise IOError("Erro ao copiar arquivo")

    # Aplicar o mock
    monkeypatch.setattr("shutil.copy2", mock_copy2)

    # Tentar criar backup (deve lançar IOError)
    with pytest.raises(IOError):
        backup_service.create_backup(test_files)


def test_restore_backup_with_missing_metadata(mock_config):
    """
    Testa a restauração de um backup com metadados incompletos.

    Args:
        mock_config: Configuração mockada.
    """
    # Criar serviço de backup
    backup_service = BackupService()

    # Criar um ID de backup com metadados incompletos
    backup_id = "incomplete_metadata"
    metadata_path = backup_service.metadata_dir / f"{backup_id}.json"
    backup_files_dir = backup_service.files_dir / backup_id

    # Criar diretório de backup
    backup_files_dir.mkdir(parents=True, exist_ok=True)

    # Criar arquivo de metadados incompleto (sem informações de arquivo)
    metadata = {
        "id": backup_id,
        "date": datetime.now().isoformat(),
        "files": [
            {
                # Sem original_path
                "backup_filename": "test.txt",
                "size": 100
            }
        ]
    }

    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f)

    # Criar um arquivo de teste no diretório de backup
    test_file = backup_files_dir / "test.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("Conteúdo de teste")

    # Restaurar backup (deve pular o arquivo com metadados incompletos)
    restore_dir = backup_service.backup_dir / "restore_incomplete"
    backup_service.restore_backup(backup_id, restore_dir)

    # Verificar que o diretório de restauração foi criado
    assert restore_dir.exists()


def test_delete_backup_metadata_error(backup_service, existing_backup, monkeypatch):
    """
    Testa o tratamento de erros ao excluir metadados durante a exclusão de backup.

    Args:
        backup_service: Instância do serviço de backup.
        existing_backup: ID de um backup existente.
        monkeypatch: Fixture do pytest para modificar objetos.
    """
    # Mock da função Path.unlink para lançar exceção
    original_unlink = Path.unlink

    def mock_unlink(self, *args, **kwargs):
        if self.name.endswith('.json'):
            raise PermissionError("Sem permissão para excluir metadados")
        return original_unlink(self, *args, **kwargs)

    # Aplicar o mock
    monkeypatch.setattr(Path, "unlink", mock_unlink)

    # Tentar excluir backup (deve lançar IOError)
    with pytest.raises(IOError):
        backup_service.delete_backup(existing_backup)
