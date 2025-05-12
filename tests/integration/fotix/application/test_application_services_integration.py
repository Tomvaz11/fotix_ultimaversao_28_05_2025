"""
Testes de integração para os serviços da camada de aplicação do Fotix.

Este módulo contém testes que verificam a integração entre os serviços:
- fotix.application.services.scan_service
- fotix.application.services.duplicate_management_service
- fotix.application.services.backup_restore_service

Cenários testados:
1. Fluxo Completo de Scan e Identificação
2. Fluxo de Gerenciamento de Duplicata (Seleção e Remoção com Backup)
3. Fluxo de Restauração de Backup
4. Interação entre Scan e Management Services
"""

import os
import tempfile
import time
from pathlib import Path
from unittest import mock

import pytest

from fotix.application.services.scan_service import ScanService
from fotix.application.services.duplicate_management_service import DuplicateManagementService
from fotix.application.services.backup_restore_service import BackupRestoreService
from fotix.core.duplicate_finder import DuplicateFinderService
from fotix.core.selection_strategy import (
    CreationDateStrategy,
    ModificationDateStrategy,
    HighestResolutionStrategy,
    ShortestNameStrategy,
    CompositeStrategy,
    create_strategy
)
from fotix.core.models import DuplicateSet, FileInfo
from fotix.infrastructure.file_system import FileSystemService
from fotix.infrastructure.zip_handler import ZipHandlerService
from fotix.infrastructure.concurrency import ConcurrencyService
from fotix.infrastructure.backup import BackupService
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
def zip_service():
    """Fixture que cria uma instância do ZipHandlerService."""
    return ZipHandlerService()


@pytest.fixture
def concurrency_service():
    """Fixture que cria uma instância do ConcurrencyService."""
    return ConcurrencyService()


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
def duplicate_finder_service(fs_service, zip_service):
    """Fixture que cria uma instância do DuplicateFinderService."""
    return DuplicateFinderService(
        file_system_service=fs_service,
        zip_handler_service=zip_service
    )


@pytest.fixture
def selection_strategy(fs_service):
    """Fixture que cria uma estratégia de seleção composta."""
    return CompositeStrategy([
        ModificationDateStrategy(file_system_service=fs_service),
        CreationDateStrategy(file_system_service=fs_service),
        ShortestNameStrategy(file_system_service=fs_service)
    ])


@pytest.fixture
def scan_service(duplicate_finder_service, fs_service, zip_service, concurrency_service):
    """Fixture que cria uma instância do ScanService."""
    return ScanService(
        duplicate_finder_service=duplicate_finder_service,
        file_system_service=fs_service,
        zip_handler_service=zip_service,
        concurrency_service=concurrency_service
    )


@pytest.fixture
def duplicate_management_service(selection_strategy, fs_service, backup_service):
    """Fixture que cria uma instância do DuplicateManagementService."""
    return DuplicateManagementService(
        selection_strategy=selection_strategy,
        file_system_service=fs_service,
        backup_service=backup_service
    )


@pytest.fixture
def backup_restore_service(backup_service, fs_service):
    """Fixture que cria uma instância do BackupRestoreService."""
    return BackupRestoreService(
        backup_service=backup_service,
        file_system_service=fs_service
    )


@pytest.fixture
def create_test_files(temp_dir, fs_service):
    """
    Fixture que cria arquivos de teste com conteúdo duplicado e não duplicado.

    Retorna um dicionário com informações sobre os arquivos criados.
    """
    # Criar diretórios
    dir1 = temp_dir / "dir1"
    dir2 = temp_dir / "dir2"
    fs_service.create_directory(dir1)
    fs_service.create_directory(dir2)

    # Conteúdos para os arquivos
    content1 = b"Conteudo duplicado para teste 1"
    content2 = b"Conteudo duplicado para teste 2"
    content3 = b"Conteudo unico para teste"

    # Criar arquivos com conteúdo duplicado em diferentes diretórios
    file1_path = dir1 / "file1.txt"
    file2_path = dir2 / "file2.txt"
    file3_path = dir1 / "file3.txt"
    file4_path = dir2 / "file4.txt"
    file5_path = dir1 / "unique.txt"

    with open(file1_path, 'wb') as f:
        f.write(content1)

    with open(file2_path, 'wb') as f:
        f.write(content1)  # Mesmo conteúdo que file1

    with open(file3_path, 'wb') as f:
        f.write(content2)

    with open(file4_path, 'wb') as f:
        f.write(content2)  # Mesmo conteúdo que file3

    with open(file5_path, 'wb') as f:
        f.write(content3)  # Conteúdo único

    # Garantir que os arquivos sejam grandes o suficiente para serem considerados pelo DuplicateFinderService
    min_size = 1024  # 1KB
    for file_path in [file1_path, file2_path, file3_path, file4_path, file5_path]:
        with open(file_path, 'ab') as f:
            # Adicionar bytes extras para atingir o tamanho mínimo
            current_size = os.path.getsize(file_path)
            if current_size < min_size:
                f.write(b'0' * (min_size - current_size))

    # Adicionar um pequeno atraso para garantir timestamps diferentes
    time.sleep(0.1)

    return {
        "dir1": dir1,
        "dir2": dir2,
        "duplicate_set1": [file1_path, file2_path],
        "duplicate_set2": [file3_path, file4_path],
        "unique_file": file5_path
    }


class TestApplicationServicesIntegration:
    """Testes de integração para os serviços da camada de aplicação."""

    def test_scan_and_process_duplicates(self, scan_service, duplicate_management_service,
                                        create_test_files, temp_dir):
        """
        Testa o fluxo de varredura e processamento de duplicatas.

        Cenário:
        1. Criar arquivos de teste com duplicatas
        2. Usar ScanService para encontrar duplicatas
        3. Usar DuplicateManagementService para processar um conjunto de duplicatas
        4. Verificar se o arquivo selecionado foi mantido e os outros foram movidos para a lixeira
        """
        # Arrange
        test_files = create_test_files
        directories = [test_files["dir1"], test_files["dir2"]]

        # Act - Scan
        duplicate_sets = scan_service.scan_directories(
            directories=directories,
            include_zips=False
        )

        # Assert - Scan
        assert len(duplicate_sets) == 2

        # Encontrar o primeiro conjunto de duplicatas
        duplicate_set = duplicate_sets[0]
        assert duplicate_set.count == 2

        # Act - Process
        with mock.patch.object(scan_service.file_system_service, 'move_to_trash') as mock_move_to_trash:
            result = duplicate_management_service.process_duplicate_set(
                duplicate_set=duplicate_set,
                create_backup=True
            )

        # Assert - Process
        assert result['kept_file'] is not None
        assert len(result['removed_files']) == 1
        assert result['backup_id'] is not None
        assert mock_move_to_trash.call_count == 1

    def test_process_and_restore_backup(self, duplicate_management_service, backup_restore_service,
                                       create_test_files, temp_dir, fs_service):
        """
        Testa o fluxo de processamento de duplicatas e restauração de backup.

        Cenário:
        1. Criar um conjunto de duplicatas manualmente
        2. Processar o conjunto com DuplicateManagementService
        3. Listar backups com BackupRestoreService
        4. Restaurar o backup para um novo local
        5. Verificar se os arquivos foram restaurados corretamente
        """
        # Arrange
        test_files = create_test_files
        file1_path, file2_path = test_files["duplicate_set1"]

        # Criar um conjunto de duplicatas manualmente
        duplicate_set = DuplicateSet(
            files=[
                FileInfo(
                    path=file1_path,
                    size=fs_service.get_file_size(file1_path),
                    hash="hash_teste",
                    creation_time=fs_service.get_creation_time(file1_path),
                    modification_time=fs_service.get_modification_time(file1_path)
                ),
                FileInfo(
                    path=file2_path,
                    size=fs_service.get_file_size(file2_path),
                    hash="hash_teste",
                    creation_time=fs_service.get_creation_time(file2_path),
                    modification_time=fs_service.get_modification_time(file2_path)
                )
            ],
            hash="hash_teste"
        )

        # Act - Process
        with mock.patch.object(fs_service, 'move_to_trash'):
            result = duplicate_management_service.process_duplicate_set(
                duplicate_set=duplicate_set,
                create_backup=True
            )

        # Assert - Process
        assert result['backup_id'] is not None
        backup_id = result['backup_id']

        # Act - List Backups
        backups = backup_restore_service.list_backups()

        # Assert - List Backups
        assert len(backups) == 1
        assert backups[0]['id'] == backup_id

        # Act - Restore Backup
        restore_dir = temp_dir / "restored"
        restore_result = backup_restore_service.restore_backup(
            backup_id=backup_id,
            target_directory=restore_dir
        )

        # Assert - Restore
        assert restore_result['status'] == "success"
        assert os.path.exists(restore_dir)
        # Verificar se pelo menos um arquivo foi restaurado
        assert any(restore_dir.glob('**/*'))

    def test_full_workflow_with_multiple_directories(self, scan_service, duplicate_management_service,
                                                   backup_restore_service, create_test_files, temp_dir):
        """
        Testa o fluxo completo de trabalho com múltiplos diretórios.

        Cenário:
        1. Criar arquivos de teste com duplicatas em múltiplos diretórios
        2. Usar ScanService para encontrar duplicatas
        3. Usar DuplicateManagementService para processar todos os conjuntos de duplicatas
        4. Listar backups com BackupRestoreService
        5. Restaurar um backup para um novo local
        6. Verificar se os arquivos foram restaurados corretamente
        """
        # Arrange
        test_files = create_test_files
        directories = [test_files["dir1"], test_files["dir2"]]

        # Act - Scan
        duplicate_sets = scan_service.scan_directories(
            directories=directories,
            include_zips=False
        )

        # Assert - Scan
        assert len(duplicate_sets) == 2

        # Act - Process all duplicate sets
        backup_ids = []
        with mock.patch.object(scan_service.file_system_service, 'move_to_trash'):
            for duplicate_set in duplicate_sets:
                result = duplicate_management_service.process_duplicate_set(
                    duplicate_set=duplicate_set,
                    create_backup=True
                )
                backup_ids.append(result['backup_id'])

        # Assert - Process
        assert len(backup_ids) == 2

        # Act - List Backups
        backups = backup_restore_service.list_backups()

        # Assert - List Backups
        assert len(backups) == 2

        # Act - Restore one backup
        restore_dir = temp_dir / "restored_full"
        restore_result = backup_restore_service.restore_backup(
            backup_id=backup_ids[0],
            target_directory=restore_dir
        )

        # Assert - Restore
        assert restore_result['status'] == "success"
        assert os.path.exists(restore_dir)
        # Verificar se pelo menos um arquivo foi restaurado
        assert any(restore_dir.glob('**/*'))
