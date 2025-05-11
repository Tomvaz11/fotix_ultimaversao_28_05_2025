"""
Testes unitários para o módulo de detecção de duplicatas.

Este módulo contém testes para verificar o funcionamento correto do serviço
de detecção de duplicatas (DuplicateFinderService).
"""

import os
from pathlib import Path
from typing import Dict, List, Callable, Iterable, Optional, Tuple
from unittest.mock import MagicMock, patch, call

import pytest

from fotix.core.duplicate_finder import DuplicateFinderService, MIN_FILE_SIZE
from fotix.core.models import DuplicateSet, FileInfo
from fotix.infrastructure.interfaces import IFileSystemService, IZipHandlerService


class TestDuplicateFinderService:
    """Testes para o serviço de detecção de duplicatas."""

    @pytest.fixture
    def mock_file_system_service(self):
        """Cria um mock para o serviço de sistema de arquivos."""
        mock = MagicMock(spec=IFileSystemService)
        return mock

    @pytest.fixture
    def mock_zip_handler_service(self):
        """Cria um mock para o serviço de manipulação de ZIPs."""
        mock = MagicMock(spec=IZipHandlerService)
        return mock

    @pytest.fixture
    def duplicate_finder_service(self, mock_file_system_service, mock_zip_handler_service):
        """Cria uma instância do serviço de detecção de duplicatas com mocks."""
        return DuplicateFinderService(
            file_system_service=mock_file_system_service,
            zip_handler_service=mock_zip_handler_service
        )

    def test_init(self, mock_file_system_service, mock_zip_handler_service):
        """Testa a inicialização do serviço."""
        # Act
        service = DuplicateFinderService(
            file_system_service=mock_file_system_service,
            zip_handler_service=mock_zip_handler_service
        )

        # Assert
        assert service.file_system_service == mock_file_system_service
        assert service.zip_handler_service == mock_zip_handler_service

    def test_find_duplicates_with_no_paths(self, duplicate_finder_service):
        """Testa a busca de duplicatas com uma lista vazia de caminhos."""
        # Arrange
        scan_paths = []

        # Act
        result = duplicate_finder_service.find_duplicates(scan_paths, include_zips=False)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 0

    def test_find_duplicates_with_individual_file(self, duplicate_finder_service, mock_file_system_service):
        """Testa a busca de duplicatas com um arquivo individual."""
        # Arrange
        file_path = Path("/test/file.txt")
        scan_paths = [file_path]

        # Configurar o mock para simular um arquivo
        # Nota: Usamos Path.is_dir e Path.is_file diretamente, não métodos do mock
        # Configurar o comportamento para o método stream_file_content
        def mock_stream_content(path, chunk_size=None):
            yield b"conteudo do arquivo"

        mock_file_system_service.stream_file_content.side_effect = mock_stream_content

        # Configurar tamanho do arquivo
        mock_file_system_service.get_file_size.return_value = 1024

        # Configurar timestamps
        mock_file_system_service.get_creation_time.return_value = 1600000000.0
        mock_file_system_service.get_modification_time.return_value = 1600000000.0

        # Patch os métodos is_dir e is_file da classe Path
        with patch.object(Path, 'is_dir', return_value=False), \
             patch.object(Path, 'is_file', return_value=True):

            # Act
            result = duplicate_finder_service.find_duplicates(scan_paths, include_zips=False)

            # Assert
            assert isinstance(result, list)
            assert len(result) == 0  # Um único arquivo não pode ser duplicata

    def test_find_duplicates_requires_zip_handler_when_include_zips_true(self, mock_file_system_service):
        """Testa que um erro é levantado quando include_zips=True mas zip_handler_service não foi fornecido."""
        # Arrange
        service = DuplicateFinderService(
            file_system_service=mock_file_system_service,
            zip_handler_service=None
        )
        scan_paths = [Path("/test")]

        # Act & Assert
        with pytest.raises(ValueError, match="zip_handler_service é necessário quando include_zips=True"):
            service.find_duplicates(scan_paths, include_zips=True)

    def test_find_duplicates_with_directory(self, duplicate_finder_service, mock_file_system_service):
        """Testa a busca de duplicatas em um diretório."""
        # Arrange
        scan_paths = [Path("/test")]

        # Configurar o mock para retornar uma lista de arquivos
        file_paths = [Path("/test/file1.txt"), Path("/test/file2.txt"), Path("/test/file3.txt")]
        mock_file_system_service.list_directory_contents.return_value = file_paths

        # Configurar tamanhos de arquivo (file1 e file2 têm o mesmo tamanho)
        mock_file_system_service.get_file_size.side_effect = lambda path: {
            Path("/test/file1.txt"): 1024,
            Path("/test/file2.txt"): 1024,
            Path("/test/file3.txt"): 2048
        }.get(path)

        # Configurar timestamps
        mock_file_system_service.get_creation_time.return_value = 1600000000.0
        mock_file_system_service.get_modification_time.return_value = 1600000000.0

        # Configurar conteúdo dos arquivos para cálculo de hash
        def mock_stream_content(path, chunk_size=None):
            content_map = {
                Path("/test/file1.txt"): b"conteudo igual",
                Path("/test/file2.txt"): b"conteudo igual",
                Path("/test/file3.txt"): b"conteudo diferente"
            }
            yield content_map.get(path, b"")

        mock_file_system_service.stream_file_content.side_effect = mock_stream_content

        # Act
        result = duplicate_finder_service.find_duplicates(scan_paths, include_zips=False)

        # Assert
        assert len(result) == 1  # Um conjunto de duplicatas (file1 e file2)
        assert len(result[0].files) == 2
        assert {file.path for file in result[0].files} == {Path("/test/file1.txt"), Path("/test/file2.txt")}
        assert result[0].hash is not None

    def test_find_duplicates_with_zip(self, duplicate_finder_service, mock_file_system_service, mock_zip_handler_service):
        """Testa a busca de duplicatas incluindo arquivos em ZIPs."""
        # Arrange
        scan_paths = [Path("/test")]

        # Configurar o mock para retornar uma lista de arquivos incluindo um ZIP
        file_paths = [Path("/test/file1.txt"), Path("/test/archive.zip")]
        mock_file_system_service.list_directory_contents.return_value = file_paths

        # Configurar tamanhos de arquivo
        mock_file_system_service.get_file_size.side_effect = lambda path: {
            Path("/test/file1.txt"): 1024,
            Path("/test/archive.zip"): 5000
        }.get(path)

        # Configurar timestamps
        mock_file_system_service.get_creation_time.return_value = 1600000000.0
        mock_file_system_service.get_modification_time.return_value = 1600000000.0

        # Configurar conteúdo do arquivo normal para cálculo de hash
        def mock_stream_content(path, chunk_size=None):
            content_map = {
                Path("/test/file1.txt"): b"conteudo igual"
            }
            yield content_map.get(path, b"")

        mock_file_system_service.stream_file_content.side_effect = mock_stream_content

        # Configurar conteúdo do arquivo ZIP
        def mock_zip_content():
            yield b"conteudo igual"

        # Configurar o mock para retornar arquivos dentro do ZIP
        mock_zip_handler_service.stream_zip_entries.return_value = [
            ("file_in_zip.txt", 1024, mock_zip_content)
        ]

        # Act
        result = duplicate_finder_service.find_duplicates(scan_paths, include_zips=True)

        # Assert
        assert len(result) == 1  # Um conjunto de duplicatas (file1 e file_in_zip)
        assert len(result[0].files) == 2
        assert any(not file.in_zip for file in result[0].files)  # Um arquivo normal
        assert any(file.in_zip for file in result[0].files)  # Um arquivo em ZIP
        assert result[0].hash is not None

    def test_find_duplicates_with_progress_callback(self, duplicate_finder_service, mock_file_system_service):
        """Testa que o callback de progresso é chamado durante a busca de duplicatas."""
        # Arrange
        scan_paths = [Path("/test")]
        mock_callback = MagicMock()

        # Configurar o mock para retornar uma lista vazia de arquivos
        mock_file_system_service.list_directory_contents.return_value = []

        # Act
        duplicate_finder_service.find_duplicates(scan_paths, include_zips=False, progress_callback=mock_callback)

        # Assert
        assert mock_callback.call_count > 0  # O callback deve ser chamado pelo menos uma vez

    def test_group_files_by_size(self, duplicate_finder_service):
        """Testa o agrupamento de arquivos por tamanho."""
        # Arrange
        files = [
            FileInfo(path=Path("/test/file1.txt"), size=1024, hash=None),
            FileInfo(path=Path("/test/file2.txt"), size=1024, hash=None),
            FileInfo(path=Path("/test/file3.txt"), size=2048, hash=None)
        ]

        # Act
        result = duplicate_finder_service._group_files_by_size(files)

        # Assert
        assert len(result) == 2  # Dois grupos de tamanho
        assert len(result[1024]) == 2  # Dois arquivos com 1024 bytes
        assert len(result[2048]) == 1  # Um arquivo com 2048 bytes

    def test_group_files_by_hash(self, duplicate_finder_service):
        """Testa o agrupamento de arquivos por hash."""
        # Arrange
        files = [
            FileInfo(path=Path("/test/file1.txt"), size=1024, hash="abc123"),
            FileInfo(path=Path("/test/file2.txt"), size=1024, hash="abc123"),
            FileInfo(path=Path("/test/file3.txt"), size=1024, hash="def456"),
            FileInfo(path=Path("/test/file4.txt"), size=1024, hash=None)  # Sem hash
        ]

        # Act
        result = duplicate_finder_service._group_files_by_hash(files)

        # Assert
        assert len(result) == 2  # Dois grupos de hash
        assert len(result["abc123"]) == 2  # Dois arquivos com hash abc123
        assert len(result["def456"]) == 1  # Um arquivo com hash def456
        assert None not in result  # Arquivos sem hash são ignorados

    def test_calculate_file_hash_normal_file(self, duplicate_finder_service, mock_file_system_service):
        """Testa o cálculo de hash para um arquivo normal."""
        # Arrange
        file_info = FileInfo(path=Path("/test/file.txt"), size=1024, hash=None, in_zip=False)

        # Configurar conteúdo do arquivo para cálculo de hash
        mock_file_system_service.stream_file_content.return_value = [b"conteudo do arquivo"]

        # Act
        with patch('blake3.blake3') as mock_blake3:
            mock_hasher = MagicMock()
            mock_hasher.hexdigest.return_value = "abc123"
            mock_blake3.return_value = mock_hasher

            result = duplicate_finder_service._calculate_file_hash(file_info)

        # Assert
        assert result == "abc123"
        mock_file_system_service.stream_file_content.assert_called_once_with(file_info.path, 65536)
        mock_hasher.update.assert_called_once_with(b"conteudo do arquivo")

    def test_calculate_file_hash_zip_file(self, duplicate_finder_service):
        """Testa o cálculo de hash para um arquivo dentro de um ZIP."""
        # Arrange
        def mock_content_provider():
            yield b"conteudo do arquivo no zip"

        file_info = FileInfo(
            path=Path("/test/archive.zip:file.txt"),
            size=1024,
            hash=None,
            in_zip=True,
            zip_path=Path("/test/archive.zip"),
            internal_path="file.txt",
            content_provider=mock_content_provider
        )

        # Act
        with patch('blake3.blake3') as mock_blake3:
            mock_hasher = MagicMock()
            mock_hasher.hexdigest.return_value = "def456"
            mock_blake3.return_value = mock_hasher

            result = duplicate_finder_service._calculate_file_hash(file_info)

        # Assert
        assert result == "def456"
        mock_hasher.update.assert_called_once_with(b"conteudo do arquivo no zip")

    def test_calculate_file_hash_zip_file_without_provider(self, duplicate_finder_service):
        """Testa que um erro é levantado ao calcular hash para um arquivo ZIP sem content_provider."""
        # Arrange
        file_info = FileInfo(
            path=Path("/test/archive.zip:file.txt"),
            size=1024,
            hash=None,
            in_zip=True,
            zip_path=Path("/test/archive.zip"),
            internal_path="file.txt"
            # Sem content_provider
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Arquivo ZIP sem content_provider"):
            duplicate_finder_service._calculate_file_hash(file_info)

    def test_process_directory(self, duplicate_finder_service, mock_file_system_service):
        """Testa o processamento de um diretório."""
        # Arrange
        directory = Path("/test")

        # Configurar o mock para retornar uma lista de arquivos
        file_paths = [Path("/test/file1.txt"), Path("/test/file2.txt")]
        mock_file_system_service.list_directory_contents.return_value = file_paths

        # Configurar tamanhos de arquivo
        mock_file_system_service.get_file_size.side_effect = lambda path: 1024

        # Configurar timestamps
        mock_file_system_service.get_creation_time.return_value = 1600000000.0
        mock_file_system_service.get_modification_time.return_value = 1600000000.0

        # Act
        result = duplicate_finder_service._process_directory(directory, include_zips=False)

        # Assert
        assert len(result) == 2
        assert all(isinstance(file, FileInfo) for file in result)
        assert {file.path for file in result} == set(file_paths)

    def test_process_directory_with_exception(self, duplicate_finder_service, mock_file_system_service):
        """Testa o processamento de um diretório quando ocorre uma exceção."""
        # Arrange
        directory = Path("/test")

        # Configurar o mock para lançar uma exceção
        mock_file_system_service.list_directory_contents.side_effect = Exception("Erro simulado")

        # Act
        result = duplicate_finder_service._process_directory(directory, include_zips=False)

        # Assert
        assert len(result) == 0  # Nenhum arquivo deve ser retornado quando ocorre um erro

    def test_process_directory_with_zip(self, duplicate_finder_service, mock_file_system_service, mock_zip_handler_service):
        """Testa o processamento de um diretório contendo um arquivo ZIP."""
        # Arrange
        directory = Path("/test")

        # Configurar o mock para retornar uma lista de arquivos incluindo um ZIP
        file_paths = [Path("/test/file1.txt"), Path("/test/archive.zip")]
        mock_file_system_service.list_directory_contents.return_value = file_paths

        # Configurar tamanhos de arquivo
        mock_file_system_service.get_file_size.side_effect = lambda path: 1024

        # Configurar timestamps
        mock_file_system_service.get_creation_time.return_value = 1600000000.0
        mock_file_system_service.get_modification_time.return_value = 1600000000.0

        # Configurar conteúdo do arquivo ZIP
        def mock_content_provider():
            yield b"conteudo do arquivo no zip"

        # Configurar o mock para retornar arquivos dentro do ZIP
        mock_zip_handler_service.stream_zip_entries.return_value = [
            ("file_in_zip.txt", 1024, mock_content_provider)
        ]

        # Act
        result = duplicate_finder_service._process_directory(directory, include_zips=True)

        # Assert
        assert len(result) == 3  # 1 arquivo normal + 1 arquivo ZIP + 1 arquivo dentro do ZIP
        assert sum(1 for file in result if file.in_zip) == 1  # 1 arquivo dentro do ZIP

    def test_process_zip(self, duplicate_finder_service, mock_file_system_service, mock_zip_handler_service):
        """Testa o processamento de um arquivo ZIP."""
        # Arrange
        zip_path = Path("/test/archive.zip")

        # Configurar timestamp do ZIP
        mock_file_system_service.get_modification_time.return_value = 1600000000.0

        # Configurar conteúdo do arquivo ZIP
        def mock_content_provider():
            yield b"conteudo do arquivo no zip"

        # Configurar o mock para retornar arquivos dentro do ZIP
        mock_zip_handler_service.stream_zip_entries.return_value = [
            ("file1.txt", 1024, mock_content_provider),
            ("file2.txt", 2048, mock_content_provider)
        ]

        # Act
        result = duplicate_finder_service._process_zip(zip_path)

        # Assert
        assert len(result) == 2
        assert all(isinstance(file, FileInfo) for file in result)
        assert all(file.in_zip for file in result)
        assert all(file.zip_path == zip_path for file in result)
        assert {file.internal_path for file in result} == {"file1.txt", "file2.txt"}

    def test_process_zip_with_exception(self, duplicate_finder_service, mock_file_system_service, mock_zip_handler_service):
        """Testa o processamento de um arquivo ZIP quando ocorre uma exceção."""
        # Arrange
        zip_path = Path("/test/archive.zip")

        # Configurar timestamp do ZIP
        mock_file_system_service.get_modification_time.return_value = 1600000000.0

        # Configurar o mock para lançar uma exceção
        mock_zip_handler_service.stream_zip_entries.side_effect = Exception("Erro simulado")

        # Act
        result = duplicate_finder_service._process_zip(zip_path)

        # Assert
        assert len(result) == 0  # Nenhum arquivo deve ser retornado quando ocorre um erro

    def test_process_zip_with_small_files(self, duplicate_finder_service, mock_file_system_service, mock_zip_handler_service):
        """Testa o processamento de um arquivo ZIP com arquivos muito pequenos (menores que MIN_FILE_SIZE)."""
        # Arrange
        zip_path = Path("/test/archive.zip")

        # Configurar timestamp do ZIP
        mock_file_system_service.get_modification_time.return_value = 1600000000.0

        # Configurar conteúdo do arquivo ZIP
        def mock_content_provider():
            yield b"pequeno"

        # Configurar o mock para retornar arquivos dentro do ZIP (um pequeno e um grande)
        mock_zip_handler_service.stream_zip_entries.return_value = [
            ("small.txt", 10, mock_content_provider),  # Menor que MIN_FILE_SIZE
            ("large.txt", 2048, mock_content_provider)  # Maior que MIN_FILE_SIZE
        ]

        # Act
        result = duplicate_finder_service._process_zip(zip_path)

        # Assert
        assert len(result) == 1  # Apenas o arquivo grande deve ser incluído
        assert result[0].internal_path == "large.txt"
