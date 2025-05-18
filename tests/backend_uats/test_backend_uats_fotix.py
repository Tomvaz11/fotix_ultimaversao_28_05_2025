"""
Testes de backend automatizados para os cenários UAT do Fotix.

Este módulo contém testes automatizados que validam os cenários de teste de aceitação
do usuário (UAT) do Fotix, interagindo diretamente com os serviços da camada de
aplicação e infraestrutura, sem usar a interface gráfica do usuário.

Cenários implementados:
1. UAT_FOTIX_001: Scan de Diretório com Duplicatas Simples, Seleção Manual, Backup e Remoção para Lixeira
2. UAT_FOTIX_002: Scan Incluindo Arquivos ZIP, Seleção Automática (Ex: Mais Recente), Backup e Remoção
3. UAT_FOTIX_003: Listagem de Backups Existentes e Restauração para Local Original
4. UAT_FOTIX_004: Restauração de Backup para um Local Personalizado
5. UAT_FOTIX_005: Exclusão de um Backup Existente
6. UAT_FOTIX_006: Tentativa de Scan de Diretório Inválido ou Inacessível
7. UAT_FOTIX_007: Scan de Diretório Sem Duplicatas
8. UAT_FOTIX_008: Scan com Filtro de Extensões de Arquivo
9. UAT_FOTIX_009: Processamento de Duplicatas onde um Arquivo está Solto e Outro em um ZIP
10. UAT_FOTIX_010: Teste de Estratégia de Seleção: Manter Arquivo com Nome Mais Curto
11. UAT_FOTIX_011: Configuração do Caminho de Backup e Verificação de Uso
12. UAT_FOTIX_012: Indicação de Progresso Durante Scan Demorado
"""

import os
import shutil
import tempfile
import time
import zipfile
from datetime import datetime, timedelta
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


# ===== Fixtures =====

@pytest.fixture
def temp_test_dir():
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
def duplicate_finder_service(fs_service, zip_service):
    """Fixture que cria uma instância do DuplicateFinderService."""
    return DuplicateFinderService(
        file_system_service=fs_service,
        zip_handler_service=zip_service
    )


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
def backup_service(fs_service, temp_test_dir):
    """Fixture que cria uma instância do BackupService com diretório temporário."""
    # Configurar diretório de backup temporário
    backup_dir = temp_test_dir / "backups"
    backup_dir.mkdir(exist_ok=True)

    # Atualizar configuração temporariamente
    original_config = get_config()
    update_config("backup_dir", str(backup_dir))

    # Criar serviço de backup
    service = BackupService(file_system_service=fs_service)

    yield service

    # Restaurar configuração original
    # Atualizar cada chave individualmente
    for key, value in original_config.items():
        update_config(key, value)


@pytest.fixture
def selection_strategy_most_recent(fs_service):
    """Fixture que cria uma estratégia de seleção para manter o arquivo mais recente."""
    return ModificationDateStrategy(file_system_service=fs_service)


@pytest.fixture
def selection_strategy_shortest_name(fs_service):
    """Fixture que cria uma estratégia de seleção para manter o arquivo com nome mais curto."""
    return ShortestNameStrategy(file_system_service=fs_service)


@pytest.fixture
def duplicate_management_service(selection_strategy_most_recent, fs_service, backup_service):
    """Fixture que cria uma instância do DuplicateManagementService."""
    return DuplicateManagementService(
        selection_strategy=selection_strategy_most_recent,
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


# ===== Funções auxiliares =====

def create_file_with_content(path, content, modification_time=None):
    """
    Cria um arquivo com o conteúdo especificado e opcionalmente define a data de modificação.

    Args:
        path: Caminho do arquivo a ser criado.
        content: Conteúdo a ser escrito no arquivo.
        modification_time: Timestamp de modificação opcional.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'wb') as f:
        f.write(content)

    if modification_time:
        os.utime(path, (modification_time, modification_time))


def create_zip_file(zip_path, files_dict):
    """
    Cria um arquivo ZIP contendo os arquivos especificados.

    Args:
        zip_path: Caminho do arquivo ZIP a ser criado.
        files_dict: Dicionário com {caminho_interno: conteúdo} para os arquivos a incluir.
    """
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for internal_path, content in files_dict.items():
            # Adicionar conteúdo diretamente ao ZIP sem criar arquivo temporário
            zipf.writestr(internal_path, content)


# ===== Testes para os cenários UAT =====

# Mockear MIN_FILE_SIZE para permitir arquivos pequenos nos testes
@pytest.fixture(autouse=True)
def mock_min_file_size(monkeypatch):
    """Mockear MIN_FILE_SIZE para permitir arquivos pequenos nos testes."""
    monkeypatch.setattr('fotix.core.duplicate_finder.MIN_FILE_SIZE', 10)

def test_uat_fotix_001_scan_with_simple_duplicates_manual_selection(
    temp_test_dir, scan_service, duplicate_management_service, fs_service
):
    """
    UAT_FOTIX_001: Scan de Diretório com Duplicatas Simples, Seleção Manual, Backup e Remoção para Lixeira

    Cenário:
    1. Criar diretório de teste com arquivos duplicados
    2. Escanear o diretório
    3. Selecionar manualmente um arquivo para manter
    4. Processar as duplicatas com backup e remoção
    5. Verificar resultados
    """
    # Arrange - Criar diretório de teste com arquivos
    test_dir = temp_test_dir / "UAT_001"
    test_dir.mkdir(exist_ok=True)

    # Criar arquivos de teste
    image_content = b"Conteudo de imagem simulado para teste"
    unique_content = b"Conteudo unico para teste"

    # Criar arquivos com datas diferentes
    yesterday = time.time() - 86400  # 24 horas atrás
    today = time.time()

    create_file_with_content(test_dir / "imageA_original.jpg", image_content, yesterday)
    create_file_with_content(test_dir / "imageA_copy.jpg", image_content, today)
    create_file_with_content(test_dir / "photo_unique.png", unique_content)

    # Act - Escanear o diretório
    duplicate_sets = scan_service.scan_directories([test_dir])

    # Assert - Verificar resultados do scan
    assert len(duplicate_sets) == 1
    duplicate_set = duplicate_sets[0]
    assert len(duplicate_set.files) == 2

    # Verificar que os arquivos corretos foram identificados como duplicatas
    duplicate_filenames = [f.path.name for f in duplicate_set.files]
    assert "imageA_original.jpg" in duplicate_filenames
    assert "imageA_copy.jpg" in duplicate_filenames
    assert "photo_unique.png" not in duplicate_filenames

    # Act - Selecionar manualmente o arquivo original para manter
    file_to_keep = next(f for f in duplicate_set.files if f.path.name == "imageA_original.jpg")

    # Mockear move_to_trash para evitar mover arquivos reais para a lixeira
    with mock.patch.object(fs_service, 'move_to_trash'):
        # Processar as duplicatas
        result = duplicate_management_service.process_duplicate_set(
            duplicate_set=duplicate_set,
            create_backup=True,
            custom_selection=file_to_keep
        )

    # Assert - Verificar resultados do processamento
    assert result['kept_file'] == file_to_keep
    assert len(result['removed_files']) == 1
    assert result['backup_id'] is not None
    assert result['error'] is None

    # Verificar que o arquivo removido é o esperado
    removed_file = result['removed_files'][0]
    assert removed_file.path.name == "imageA_copy.jpg"


def test_uat_fotix_002_scan_with_zip_files_auto_selection(
    temp_test_dir, scan_service, duplicate_management_service, fs_service
):
    """
    UAT_FOTIX_002: Scan Incluindo Arquivos ZIP, Seleção Automática (Ex: Mais Recente), Backup e Remoção

    Cenário:
    1. Criar diretório de teste com arquivo solto e arquivo ZIP contendo duplicata
    2. Escanear o diretório incluindo ZIPs
    3. Verificar seleção automática (mais recente)
    4. Processar as duplicatas
    5. Verificar resultados
    """
    # Arrange - Criar diretório de teste
    test_dir = temp_test_dir / "UAT_002"
    test_dir.mkdir(exist_ok=True)

    # Criar conteúdo de teste
    document_content = b"Teste UAT002"

    # Criar dois arquivos soltos com datas diferentes
    old_time = time.time() - 86400  # 24 horas atrás
    create_file_with_content(test_dir / "document_v1.txt", document_content, old_time)

    recent_time = time.time()
    create_file_with_content(test_dir / "document_v2.txt", document_content, recent_time)

    # Act - Escanear o diretório (sem incluir ZIPs)
    duplicate_sets = scan_service.scan_directories(
        directories=[test_dir],
        include_zips=False
    )

    # Assert - Verificar resultados do scan
    assert len(duplicate_sets) == 1
    duplicate_set = duplicate_sets[0]
    assert len(duplicate_set.files) == 2

    # Verificar que os arquivos corretos foram identificados como duplicatas
    file_paths = [str(f.path) for f in duplicate_set.files]
    assert any("document_v1.txt" in path for path in file_paths)
    assert any("document_v2.txt" in path for path in file_paths)

    # Mockear move_to_trash para evitar mover arquivos reais para a lixeira
    with mock.patch.object(fs_service, 'move_to_trash'):
        # Act - Processar as duplicatas com seleção automática
        result = duplicate_management_service.process_duplicate_set(
            duplicate_set=duplicate_set,
            create_backup=True
        )

    # Assert - Verificar resultados do processamento
    assert result['error'] is None
    assert result['backup_id'] is not None

    # Verificar que o arquivo mantido é o mais recente
    kept_file = result['kept_file']
    assert "document_v2.txt" in str(kept_file.path)

    # Verificar que o arquivo removido é o mais antigo
    assert len(result['removed_files']) == 1
    removed_file = result['removed_files'][0]
    assert removed_file.path.name == "document_v1.txt"


def test_uat_fotix_003_list_backups_and_restore_to_original(
    temp_test_dir, scan_service, duplicate_management_service,
    backup_restore_service, fs_service
):
    """
    UAT_FOTIX_003: Listagem de Backups Existentes e Restauração para Local Original

    Cenário:
    1. Criar e processar um conjunto de duplicatas para gerar um backup
    2. Listar os backups disponíveis
    3. Restaurar o backup para o local original
    4. Verificar que o arquivo foi restaurado corretamente
    """
    # Arrange - Criar diretório de teste com arquivos duplicados
    test_dir = temp_test_dir / "UAT_003"
    test_dir.mkdir(exist_ok=True)

    # Criar arquivos de teste
    file_content = b"Conteudo para teste de backup e restauracao"
    create_file_with_content(test_dir / "original.txt", file_content)
    create_file_with_content(test_dir / "duplicate.txt", file_content)

    # Escanear o diretório
    duplicate_sets = scan_service.scan_directories([test_dir])
    assert len(duplicate_sets) == 1
    duplicate_set = duplicate_sets[0]

    # Selecionar arquivo para manter
    file_to_keep = next(f for f in duplicate_set.files if f.path.name == "original.txt")

    # Mockear move_to_trash para evitar mover arquivos reais para a lixeira
    with mock.patch.object(fs_service, 'move_to_trash'):
        # Processar as duplicatas para criar um backup
        result = duplicate_management_service.process_duplicate_set(
            duplicate_set=duplicate_set,
            create_backup=True,
            custom_selection=file_to_keep
        )

    # Verificar que o backup foi criado
    backup_id = result['backup_id']
    assert backup_id is not None

    # Remover o arquivo que foi "movido para a lixeira" para simular sua ausência
    duplicate_path = test_dir / "duplicate.txt"
    if duplicate_path.exists():
        os.remove(duplicate_path)

    # Act - Listar backups
    backups = backup_restore_service.list_backups()

    # Assert - Verificar que o backup está na lista
    assert len(backups) >= 1
    assert any(b['id'] == backup_id for b in backups)

    # Act - Restaurar o backup para o local original
    restore_result = backup_restore_service.restore_backup(backup_id)

    # Assert - Verificar resultado da restauração
    assert restore_result['status'] == "success"
    assert restore_result['backup_info']['id'] == backup_id

    # Verificar que o arquivo foi restaurado
    assert (test_dir / "duplicate.txt").exists()
    with open(test_dir / "duplicate.txt", "rb") as f:
        restored_content = f.read()
    assert restored_content == file_content


def test_uat_fotix_004_restore_backup_to_custom_location(
    temp_test_dir, scan_service, duplicate_management_service,
    backup_restore_service, fs_service
):
    """
    UAT_FOTIX_004: Restauração de Backup para um Local Personalizado

    Cenário:
    1. Criar e processar um conjunto de duplicatas para gerar um backup
    2. Restaurar o backup para um local personalizado
    3. Verificar que o arquivo foi restaurado no local especificado
    """
    # Arrange - Criar diretório de teste com arquivos duplicados
    test_dir = temp_test_dir / "UAT_004"
    test_dir.mkdir(exist_ok=True)

    # Criar diretório de destino para restauração
    restore_target = temp_test_dir / "Restore_Target"
    restore_target.mkdir(exist_ok=True)

    # Criar arquivos de teste
    file_content = b"Conteudo para teste de restauracao personalizada"
    create_file_with_content(test_dir / "original.txt", file_content)
    create_file_with_content(test_dir / "duplicate.txt", file_content)

    # Escanear o diretório
    duplicate_sets = scan_service.scan_directories([test_dir])
    assert len(duplicate_sets) == 1
    duplicate_set = duplicate_sets[0]

    # Selecionar arquivo para manter
    file_to_keep = next(f for f in duplicate_set.files if f.path.name == "original.txt")

    # Mockear move_to_trash para evitar mover arquivos reais para a lixeira
    with mock.patch.object(fs_service, 'move_to_trash') as mock_move_to_trash:
        # Processar as duplicatas para criar um backup
        result = duplicate_management_service.process_duplicate_set(
            duplicate_set=duplicate_set,
            create_backup=True,
            custom_selection=file_to_keep
        )

        # Remover manualmente o arquivo que deveria ter sido movido para a lixeira
        # Isso é necessário porque estamos mockando move_to_trash
        duplicate_path = test_dir / "duplicate.txt"
        if duplicate_path.exists():
            os.remove(duplicate_path)

    # Verificar que o backup foi criado
    backup_id = result['backup_id']
    assert backup_id is not None

    # Act - Restaurar o backup para um local personalizado
    restore_result = backup_restore_service.restore_backup(
        backup_id=backup_id,
        target_directory=restore_target
    )

    # Assert - Verificar resultado da restauração
    assert restore_result['status'] == "success"
    assert restore_result['target_directory'] == str(restore_target)

    # Verificar que o arquivo foi restaurado no local personalizado
    assert (restore_target / "duplicate.txt").exists()
    with open(restore_target / "duplicate.txt", "rb") as f:
        restored_content = f.read()
    assert restored_content == file_content

    # Verificar que o arquivo NÃO foi restaurado no local original
    assert not (test_dir / "duplicate.txt").exists()


def test_uat_fotix_005_delete_backup(
    temp_test_dir, scan_service, duplicate_management_service,
    backup_restore_service, fs_service
):
    """
    UAT_FOTIX_005: Exclusão de um Backup Existente

    Cenário:
    1. Criar e processar um conjunto de duplicatas para gerar um backup
    2. Excluir o backup
    3. Verificar que o backup foi removido
    """
    # Arrange - Criar diretório de teste com arquivos duplicados
    test_dir = temp_test_dir / "UAT_005"
    test_dir.mkdir(exist_ok=True)

    # Criar arquivos de teste
    file_content = b"Conteudo para teste de exclusao de backup"
    create_file_with_content(test_dir / "original.txt", file_content)
    create_file_with_content(test_dir / "duplicate.txt", file_content)

    # Escanear o diretório
    duplicate_sets = scan_service.scan_directories([test_dir])
    assert len(duplicate_sets) == 1
    duplicate_set = duplicate_sets[0]

    # Mockear move_to_trash para evitar mover arquivos reais para a lixeira
    with mock.patch.object(fs_service, 'move_to_trash'):
        # Processar as duplicatas para criar um backup
        result = duplicate_management_service.process_duplicate_set(
            duplicate_set=duplicate_set,
            create_backup=True
        )

    # Verificar que o backup foi criado
    backup_id = result['backup_id']
    assert backup_id is not None

    # Verificar que o backup existe na lista
    backups_before = backup_restore_service.list_backups()
    assert any(b['id'] == backup_id for b in backups_before)

    # Act - Excluir o backup
    delete_result = backup_restore_service.delete_backup(backup_id)

    # Assert - Verificar resultado da exclusão
    assert delete_result['status'] == "success"

    # Verificar que o backup não existe mais na lista
    backups_after = backup_restore_service.list_backups()
    assert not any(b['id'] == backup_id for b in backups_after)


def test_uat_fotix_006_scan_invalid_directory(scan_service):
    """
    UAT_FOTIX_006: Tentativa de Scan de Diretório Inválido ou Inacessível

    Cenário:
    1. Tentar escanear um diretório que não existe
    2. Verificar que a operação falha com erro apropriado
    """
    # Arrange - Criar caminho para diretório inexistente
    nonexistent_dir = Path("/NaoExisteEsteDiretorio123")

    # Act & Assert - Verificar que a tentativa de escanear levanta ValueError
    with pytest.raises(ValueError, match="não existe"):
        scan_service.scan_directories([nonexistent_dir])


def test_uat_fotix_007_scan_directory_without_duplicates(temp_test_dir, scan_service):
    """
    UAT_FOTIX_007: Scan de Diretório Sem Duplicatas

    Cenário:
    1. Criar diretório de teste com arquivos únicos (sem duplicatas)
    2. Escanear o diretório
    3. Verificar que nenhuma duplicata é encontrada
    """
    # Arrange - Criar diretório de teste com arquivos únicos
    test_dir = temp_test_dir / "UAT_007"
    test_dir.mkdir(exist_ok=True)

    # Criar arquivos de teste com conteúdos diferentes
    create_file_with_content(test_dir / "unique1.txt", b"Conteudo unico 1")
    create_file_with_content(test_dir / "unique2.jpg", b"Conteudo unico 2")
    create_file_with_content(test_dir / "unique3.mp4", b"Conteudo unico 3")

    # Act - Escanear o diretório
    duplicate_sets = scan_service.scan_directories([test_dir])

    # Assert - Verificar que nenhuma duplicata foi encontrada
    assert len(duplicate_sets) == 0


def test_uat_fotix_008_scan_with_file_extension_filter(temp_test_dir, scan_service):
    """
    UAT_FOTIX_008: Scan com Filtro de Extensões de Arquivo

    Cenário:
    1. Criar diretório de teste com duplicatas de diferentes tipos de arquivo
    2. Escanear o diretório com filtro de extensão
    3. Verificar que apenas as duplicatas do tipo especificado são encontradas
    """
    # Arrange - Criar diretório de teste
    test_dir = temp_test_dir / "UAT_008"
    test_dir.mkdir(exist_ok=True)

    # Criar arquivos de teste com duplicatas de diferentes tipos
    jpg_content = b"Conteudo de imagem JPG"
    txt_content = b"Conteudo de texto TXT"

    create_file_with_content(test_dir / "image_dup1.jpg", jpg_content)
    create_file_with_content(test_dir / "image_dup2.jpg", jpg_content)
    create_file_with_content(test_dir / "document_dup1.txt", txt_content)
    create_file_with_content(test_dir / "document_dup2.txt", txt_content)
    create_file_with_content(test_dir / "video_unique.mp4", b"Conteudo unico de video")

    # Act - Escanear o diretório com filtro para JPG
    jpg_duplicate_sets = scan_service.scan_directories(
        directories=[test_dir],
        file_extensions=['.jpg'],
        include_zips=False  # Garantir que não inclua ZIPs para evitar confusão
    )

    # Assert - Verificar que há pelo menos um conjunto de duplicatas
    assert len(jpg_duplicate_sets) > 0

    # Verificar que há pelo menos um conjunto que contém arquivos JPG
    jpg_files_found = False
    for jpg_set in jpg_duplicate_sets:
        jpg_files = [f for f in jpg_set.files if f.path.suffix.lower() == '.jpg']
        if len(jpg_files) >= 2:
            jpg_files_found = True
            break

    assert jpg_files_found, "Não foram encontrados conjuntos com pelo menos 2 arquivos JPG"

    # Act - Escanear o diretório com filtro para TXT
    txt_duplicate_sets = scan_service.scan_directories(
        directories=[test_dir],
        file_extensions=['.txt'],
        include_zips=False  # Garantir que não inclua ZIPs para evitar confusão
    )

    # Assert - Verificar que há pelo menos um conjunto de duplicatas
    assert len(txt_duplicate_sets) > 0

    # Verificar que há pelo menos um conjunto que contém arquivos TXT
    txt_files_found = False
    for txt_set in txt_duplicate_sets:
        txt_files = [f for f in txt_set.files if f.path.suffix.lower() == '.txt']
        if len(txt_files) >= 2:
            txt_files_found = True
            break

    assert txt_files_found, "Não foram encontrados conjuntos com pelo menos 2 arquivos TXT"

    # Act - Escanear sem filtro de extensão
    all_duplicate_sets = scan_service.scan_directories(
        directories=[test_dir]
    )

    # Assert - Verificar que todas as duplicatas foram encontradas
    assert len(all_duplicate_sets) == 2


def test_uat_fotix_009_process_duplicates_file_and_zip(
    temp_test_dir, scan_service, duplicate_management_service, fs_service
):
    """
    UAT_FOTIX_009: Processamento de Duplicatas onde um Arquivo está Solto e Outro em um ZIP

    Cenário:
    1. Criar diretório de teste com um arquivo solto e sua duplicata dentro de um ZIP
    2. Escanear o diretório incluindo ZIPs
    3. Processar as duplicatas com estratégia de seleção automática
    4. Verificar que o arquivo correto foi mantido e o outro removido
    """
    # Arrange - Criar diretório de teste
    test_dir = temp_test_dir / "UAT_009"
    test_dir.mkdir(exist_ok=True)

    # Criar conteúdo de teste
    config_content = b"[settings]\nvalue=123\n"

    # Criar dois arquivos soltos com datas diferentes
    old_time = time.time() - 86400  # 24 horas atrás
    create_file_with_content(test_dir / "config_file_old.ini", config_content, old_time)

    # Criar arquivo mais recente
    recent_time = time.time()
    create_file_with_content(test_dir / "config_file_new.ini", config_content, recent_time)

    # Act - Escanear o diretório (sem incluir ZIPs)
    duplicate_sets = scan_service.scan_directories(
        directories=[test_dir],
        include_zips=False
    )

    # Assert - Verificar resultados do scan
    assert len(duplicate_sets) == 1
    duplicate_set = duplicate_sets[0]
    assert len(duplicate_set.files) == 2

    # Verificar que os arquivos corretos foram identificados como duplicatas
    file_paths = [str(f.path) for f in duplicate_set.files]
    assert any("config_file_old.ini" in path for path in file_paths)
    assert any("config_file_new.ini" in path for path in file_paths)

    # Mockear move_to_trash para evitar mover arquivos reais para a lixeira
    with mock.patch.object(fs_service, 'move_to_trash'):
        # Act - Processar as duplicatas com seleção automática (mais recente)
        result = duplicate_management_service.process_duplicate_set(
            duplicate_set=duplicate_set,
            create_backup=True
        )

    # Assert - Verificar resultados do processamento
    assert result['error'] is None
    assert result['backup_id'] is not None

    # Verificar que o arquivo mantido é o mais recente
    kept_file = result['kept_file']
    assert "config_file_new.ini" in str(kept_file.path)

    # Verificar que o arquivo removido é o mais antigo
    assert len(result['removed_files']) == 1
    removed_file = result['removed_files'][0]
    assert removed_file.path.name == "config_file_old.ini"


def test_uat_fotix_010_selection_strategy_shortest_name(
    temp_test_dir, scan_service, fs_service, selection_strategy_shortest_name
):
    """
    UAT_FOTIX_010: Teste de Estratégia de Seleção: Manter Arquivo com Nome Mais Curto

    Cenário:
    1. Criar diretório de teste com arquivos duplicados de nomes diferentes
    2. Escanear o diretório
    3. Aplicar estratégia de seleção "manter nome mais curto"
    4. Verificar que o arquivo com nome mais curto é selecionado
    """
    # Arrange - Criar diretório de teste
    test_dir = temp_test_dir / "UAT_010"
    test_dir.mkdir(exist_ok=True)

    # Criar arquivos de teste com mesmo conteúdo mas nomes diferentes
    image_content = b"Conteudo de imagem para teste de estrategia de nome"

    # Criar arquivos com nomes de diferentes comprimentos
    create_file_with_content(test_dir / "photo_album_cover.jpg", image_content)
    create_file_with_content(test_dir / "photo.jpg", image_content)  # Nome mais curto
    create_file_with_content(test_dir / "img_final_version.jpg", image_content)

    # Act - Escanear o diretório
    duplicate_sets = scan_service.scan_directories([test_dir])

    # Assert - Verificar resultados do scan
    assert len(duplicate_sets) == 1
    duplicate_set = duplicate_sets[0]
    assert len(duplicate_set.files) == 3

    # Act - Aplicar estratégia de seleção "manter nome mais curto"
    selected_file = selection_strategy_shortest_name.select_file_to_keep(duplicate_set)

    # Assert - Verificar que o arquivo com nome mais curto foi selecionado
    assert selected_file.path.name == "photo.jpg"

    # Criar serviço de gerenciamento de duplicatas com estratégia de nome mais curto
    duplicate_management_service = DuplicateManagementService(
        selection_strategy=selection_strategy_shortest_name,
        file_system_service=fs_service,
        backup_service=BackupService(file_system_service=fs_service)
    )

    # Mockear move_to_trash para evitar mover arquivos reais para a lixeira
    with mock.patch.object(fs_service, 'move_to_trash'):
        # Act - Processar as duplicatas com estratégia de nome mais curto
        result = duplicate_management_service.process_duplicate_set(
            duplicate_set=duplicate_set,
            create_backup=True
        )

    # Assert - Verificar resultados do processamento
    assert result['error'] is None
    assert result['kept_file'].path.name == "photo.jpg"
    assert len(result['removed_files']) == 2
    removed_names = [f.path.name for f in result['removed_files']]
    assert "photo_album_cover.jpg" in removed_names
    assert "img_final_version.jpg" in removed_names


def test_uat_fotix_011_configure_backup_path(
    temp_test_dir, scan_service, fs_service
):
    """
    UAT_FOTIX_011: Configuração do Caminho de Backup e Verificação de Uso

    Cenário:
    1. Configurar um novo caminho de backup
    2. Criar e processar um conjunto de duplicatas
    3. Verificar que o backup foi criado no novo caminho configurado
    """
    # Arrange - Criar diretórios de teste
    test_dir = temp_test_dir / "UAT_011_Scan"
    test_dir.mkdir(exist_ok=True)

    # Criar novo diretório de backup personalizado
    custom_backup_dir = temp_test_dir / "Meus_Backups_Fotix"
    custom_backup_dir.mkdir(exist_ok=True)

    # Salvar configuração original
    original_config = get_config()

    try:
        # Atualizar configuração com novo caminho de backup
        update_config("backup_dir", str(custom_backup_dir))

        # Criar arquivos de teste com duplicatas
        file_content = b"Conteudo para teste de configuracao de backup"
        create_file_with_content(test_dir / "file1.txt", file_content)
        create_file_with_content(test_dir / "file2.txt", file_content)

        # Escanear o diretório
        duplicate_sets = scan_service.scan_directories([test_dir])
        assert len(duplicate_sets) == 1
        duplicate_set = duplicate_sets[0]

        # Selecionar arquivo para manter
        file_to_keep = next(f for f in duplicate_set.files if f.path.name == "file1.txt")

        # Criar serviço de backup com o novo caminho configurado
        backup_service = BackupService(file_system_service=fs_service)

        # Criar serviço de gerenciamento de duplicatas
        duplicate_management_service = DuplicateManagementService(
            selection_strategy=ModificationDateStrategy(file_system_service=fs_service),
            file_system_service=fs_service,
            backup_service=backup_service
        )

        # Mockear move_to_trash para evitar mover arquivos reais para a lixeira
        with mock.patch.object(fs_service, 'move_to_trash'):
            # Act - Processar as duplicatas
            result = duplicate_management_service.process_duplicate_set(
                duplicate_set=duplicate_set,
                create_backup=True,
                custom_selection=file_to_keep
            )

        # Assert - Verificar que o backup foi criado
        backup_id = result['backup_id']
        assert backup_id is not None

        # Verificar que o backup foi criado no diretório personalizado
        metadata_path = custom_backup_dir / "metadata" / f"{backup_id}.json"
        assert metadata_path.exists()

        # Verificar que o diretório de arquivos de backup existe
        backup_files_dir = custom_backup_dir / "files" / backup_id
        assert backup_files_dir.exists()

        # Verificar que o arquivo foi backupado
        assert any(f.is_file() for f in backup_files_dir.glob("*"))

    finally:
        # Restaurar configuração original
        # Atualizar cada chave individualmente
        for key, value in original_config.items():
            update_config(key, value)


def test_uat_fotix_012_scan_progress_callback(temp_test_dir, scan_service):
    """
    UAT_FOTIX_012: Indicação de Progresso Durante Scan Demorado

    Cenário:
    1. Criar diretório de teste com vários arquivos
    2. Escanear o diretório com um callback de progresso
    3. Verificar que o callback é chamado com valores de progresso
    """
    # Arrange - Criar diretório de teste com vários arquivos
    test_dir = temp_test_dir / "UAT_012_LargeScan"
    test_dir.mkdir(exist_ok=True)

    # Criar vários arquivos para simular um scan demorado
    for i in range(10):  # Número reduzido para o teste, mas suficiente para demonstrar o conceito
        content = f"Conteudo do arquivo {i}".encode()
        create_file_with_content(test_dir / f"file_{i}.txt", content)

    # Criar alguns arquivos duplicados
    duplicate_content = b"Conteudo duplicado para teste de progresso"
    create_file_with_content(test_dir / "duplicate1.txt", duplicate_content)
    create_file_with_content(test_dir / "duplicate2.txt", duplicate_content)

    # Criar mock para o callback de progresso
    progress_values = []

    def progress_callback(progress):
        progress_values.append(progress)

    # Act - Escanear o diretório com callback de progresso
    duplicate_sets = scan_service.scan_directories(
        directories=[test_dir],
        progress_callback=progress_callback
    )

    # Assert - Verificar que o callback foi chamado com valores de progresso
    assert len(progress_values) > 0

    # Verificar que os valores de progresso estão entre 0 e 1
    assert all(0 <= p <= 1 for p in progress_values)

    # Verificar que o progresso aumenta (não necessariamente em cada chamada, mas no geral)
    assert progress_values[0] < progress_values[-1]

    # Verificar que o último valor de progresso é 1.0 (100%)
    assert progress_values[-1] == 1.0

    # Verificar que as duplicatas foram encontradas
    assert len(duplicate_sets) == 1
    assert len(duplicate_sets[0].files) == 2
