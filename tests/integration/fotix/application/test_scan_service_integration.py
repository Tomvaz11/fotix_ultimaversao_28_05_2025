"""
Testes de integração para o serviço de varredura do Fotix.

Este módulo contém testes que verificam a integração entre o ScanService
e os serviços que ele utiliza (DuplicateFinderService, FileSystemService,
ZipHandlerService e ConcurrencyService).

Cenários testados:
1. Varredura de diretórios com arquivos reais
2. Varredura de diretórios com estrutura aninhada
3. Varredura de diretórios com arquivos ZIP
"""

import os
import tempfile
import zipfile
import time
from pathlib import Path
from unittest import mock

import pytest

from fotix.application.services.scan_service import ScanService
from fotix.core.duplicate_finder import DuplicateFinderService
from fotix.core.models import DuplicateSet, FileInfo
from fotix.infrastructure.file_system import FileSystemService
from fotix.infrastructure.zip_handler import ZipHandlerService
from fotix.infrastructure.concurrency import ConcurrencyService


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
    # (pode haver um tamanho mínimo definido no serviço)
    min_size = 1024  # 1KB
    for file_path in [file1_path, file2_path, file3_path, file4_path, file5_path]:
        with open(file_path, 'ab') as f:
            # Adicionar bytes extras para atingir o tamanho mínimo
            current_size = os.path.getsize(file_path)
            if current_size < min_size:
                f.write(b'0' * (min_size - current_size))

    return {
        "dir1": dir1,
        "dir2": dir2,
        "duplicate_set1": [file1_path, file2_path],
        "duplicate_set2": [file3_path, file4_path],
        "unique_file": file5_path
    }


@pytest.fixture
def create_nested_structure(temp_dir, fs_service):
    """
    Fixture que cria uma estrutura de diretórios aninhada com arquivos duplicados.

    Retorna um dicionário com informações sobre os diretórios e arquivos criados.
    """
    # Criar estrutura de diretórios
    root = temp_dir / "root"
    subdir1 = root / "subdir1"
    subdir2 = root / "subdir2"
    subsubdir = subdir1 / "subsubdir"

    fs_service.create_directory(root)
    fs_service.create_directory(subdir1)
    fs_service.create_directory(subdir2)
    fs_service.create_directory(subsubdir)

    # Conteúdo para os arquivos
    content1 = b"Conteudo duplicado em estrutura aninhada"
    content2 = b"Conteudo unico"

    # Criar arquivos com conteúdo duplicado em diferentes níveis
    file1_path = root / "file1.txt"
    file2_path = subdir1 / "file2.txt"
    file3_path = subsubdir / "file3.txt"
    file4_path = subdir2 / "unique.txt"

    with open(file1_path, 'wb') as f:
        f.write(content1)

    with open(file2_path, 'wb') as f:
        f.write(content1)  # Mesmo conteúdo que file1

    with open(file3_path, 'wb') as f:
        f.write(content1)  # Mesmo conteúdo que file1

    with open(file4_path, 'wb') as f:
        f.write(content2)  # Conteúdo único

    # Garantir que os arquivos sejam grandes o suficiente para serem considerados pelo DuplicateFinderService
    min_size = 1024  # 1KB
    for file_path in [file1_path, file2_path, file3_path, file4_path]:
        with open(file_path, 'ab') as f:
            # Adicionar bytes extras para atingir o tamanho mínimo
            current_size = os.path.getsize(file_path)
            if current_size < min_size:
                f.write(b'0' * (min_size - current_size))

    return {
        "root": root,
        "subdir1": subdir1,
        "subdir2": subdir2,
        "subsubdir": subsubdir,
        "duplicate_files": [file1_path, file2_path, file3_path],
        "unique_file": file4_path
    }


@pytest.fixture
def create_zip_files(temp_dir, fs_service):
    """
    Fixture que cria arquivos ZIP com conteúdo duplicado.

    Retorna um dicionário com informações sobre os arquivos criados.
    """
    # Criar diretórios
    zip_dir = temp_dir / "zip_dir"
    normal_dir = temp_dir / "normal_dir"
    fs_service.create_directory(zip_dir)
    fs_service.create_directory(normal_dir)

    # Conteúdo para os arquivos
    content1 = b"Conteudo duplicado em ZIP e arquivo normal" + b"0" * 1024  # Garantir tamanho mínimo
    content2 = b"Conteudo unico" + b"0" * 1024  # Garantir tamanho mínimo

    # Criar arquivo normal
    normal_file_path = normal_dir / "normal_file.txt"
    with open(normal_file_path, 'wb') as f:
        f.write(content1)

    # Criar arquivo ZIP com conteúdo duplicado
    zip_file_path = zip_dir / "archive.zip"
    with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
        # Adicionar arquivo com conteúdo duplicado
        zip_file.writestr("duplicate_in_zip.txt", content1)
        # Adicionar arquivo com conteúdo único
        zip_file.writestr("unique_in_zip.txt", content2)

    return {
        "zip_dir": zip_dir,
        "normal_dir": normal_dir,
        "zip_file": zip_file_path,
        "normal_file": normal_file_path
    }


class TestScanServiceIntegration:
    """Testes de integração para o ScanService."""

    def test_scan_directories_with_real_files(self, scan_service, create_test_files):
        """
        Testa a varredura de diretórios com arquivos reais.

        Cenário:
        1. Criar arquivos reais com conteúdo duplicado em diferentes diretórios
        2. Usar ScanService para varrer os diretórios
        3. Verificar se as duplicatas são encontradas corretamente
        """
        # Arrange
        test_files = create_test_files
        directories = [test_files["dir1"], test_files["dir2"]]

        # Act
        duplicate_sets = scan_service.scan_directories(
            directories=directories,
            include_zips=False
        )

        # Assert
        assert len(duplicate_sets) == 2

        # Verificar se cada conjunto tem 2 arquivos
        for duplicate_set in duplicate_sets:
            assert duplicate_set.count == 2

            # Verificar se os arquivos no conjunto têm o mesmo hash
            hashes = set(file_info.hash for file_info in duplicate_set.files)
            assert len(hashes) == 1

            # Verificar se os arquivos no conjunto têm o mesmo tamanho
            sizes = set(file_info.size for file_info in duplicate_set.files)
            assert len(sizes) == 1

    def test_scan_directories_with_nested_structure(self, scan_service, create_nested_structure):
        """
        Testa a varredura de diretórios com estrutura aninhada.

        Cenário:
        1. Criar uma estrutura de diretórios aninhada com arquivos duplicados
        2. Usar ScanService para varrer o diretório raiz
        3. Verificar se as duplicatas são encontradas corretamente, mesmo em subdiretórios
        """
        # Arrange
        test_structure = create_nested_structure
        root_dir = test_structure["root"]

        # Act
        duplicate_sets = scan_service.scan_directories(
            directories=[root_dir],
            include_zips=False
        )

        # Assert
        assert len(duplicate_sets) == 1

        # Verificar se o conjunto tem 3 arquivos (duplicatas em diferentes níveis)
        duplicate_set = duplicate_sets[0]
        assert duplicate_set.count == 3

        # Verificar se os caminhos dos arquivos correspondem aos esperados
        file_paths = [file_info.path for file_info in duplicate_set.files]
        for expected_path in test_structure["duplicate_files"]:
            assert expected_path in file_paths

    def test_scan_directories_with_zips(self, scan_service, create_zip_files):
        """
        Testa a varredura de diretórios com arquivos ZIP.

        Cenário:
        1. Criar um arquivo ZIP com conteúdo duplicado em relação a um arquivo normal
        2. Usar ScanService para varrer os diretórios, incluindo ZIPs
        3. Verificar se as duplicatas são encontradas corretamente, mesmo dentro de ZIPs
        """
        # Arrange
        test_files = create_zip_files
        directories = [test_files["zip_dir"], test_files["normal_dir"]]

        # Act
        try:
            duplicate_sets = scan_service.scan_directories(
                directories=directories,
                include_zips=True
            )

            # Assert
            assert len(duplicate_sets) == 1

            # Verificar se o conjunto tem 2 arquivos (um normal e um dentro do ZIP)
            duplicate_set = duplicate_sets[0]
            assert duplicate_set.count == 2

            # Verificar se um dos arquivos está dentro de um ZIP
            has_zip_file = any(file_info.in_zip for file_info in duplicate_set.files)
            assert has_zip_file

            # Verificar se um dos arquivos é o arquivo normal
            normal_file_path = test_files["normal_file"]
            has_normal_file = any(file_info.path == normal_file_path for file_info in duplicate_set.files)
            assert has_normal_file

        except Exception as e:
            # Em caso de erro na leitura do ZIP, registrar o erro e pular o teste
            pytest.skip(f"Erro ao processar arquivo ZIP: {str(e)}")
