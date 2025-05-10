"""
Testes unitários para o módulo de sistema de arquivos.

Este módulo contém testes para a classe FileSystemService, que implementa
a interface IFileSystemService para operações no sistema de arquivos.
"""

import os
import shutil
import tempfile
import time
from pathlib import Path
from unittest import mock

import pytest

from fotix.infrastructure.file_system import FileSystemService


class TestFileSystemService:
    """Testes para a classe FileSystemService."""

    @pytest.fixture
    def fs_service(self):
        """Fixture que retorna uma instância de FileSystemService."""
        return FileSystemService()

    @pytest.fixture
    def temp_dir(self):
        """Fixture que cria um diretório temporário para testes."""
        # Criar diretório temporário
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        # Limpar após o teste
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    @pytest.fixture
    def temp_file(self, temp_dir):
        """Fixture que cria um arquivo temporário para testes."""
        # Criar arquivo temporário com conteúdo
        file_path = temp_dir / "test_file.txt"
        with open(file_path, 'wb') as f:
            f.write("Conteúdo de teste".encode('utf-8'))
        yield file_path
        # Limpeza é feita pela fixture temp_dir

    def test_get_file_size_existing_file(self, fs_service, temp_file):
        """Testa get_file_size com um arquivo existente."""
        # Arrange
        expected_size = len("Conteúdo de teste".encode('utf-8'))

        # Act
        size = fs_service.get_file_size(temp_file)

        # Assert
        assert size == expected_size

    def test_get_file_size_permission_error(self, fs_service, temp_file):
        """Testa get_file_size com erro de permissão."""
        # Arrange
        with mock.patch('pathlib.Path.is_file', return_value=True):
            with mock.patch('pathlib.Path.stat', side_effect=PermissionError("Sem permissão")):
                # Act
                size = fs_service.get_file_size(temp_file)

                # Assert
                assert size is None

    def test_get_file_size_generic_error(self, fs_service, temp_file):
        """Testa get_file_size com um erro genérico."""
        # Arrange
        with mock.patch('pathlib.Path.is_file', return_value=True):
            with mock.patch('pathlib.Path.stat', side_effect=Exception("Erro genérico")):
                # Act
                size = fs_service.get_file_size(temp_file)

                # Assert
                assert size is None

    def test_get_file_size_nonexistent_file(self, fs_service, temp_dir):
        """Testa get_file_size com um arquivo inexistente."""
        # Arrange
        nonexistent_file = temp_dir / "nonexistent.txt"

        # Act
        size = fs_service.get_file_size(nonexistent_file)

        # Assert
        assert size is None

    def test_get_file_size_file_not_found_error(self, fs_service, temp_file):
        """Testa get_file_size com FileNotFoundError durante stat()."""
        # Arrange
        with mock.patch('pathlib.Path.is_file', return_value=True):
            with mock.patch('pathlib.Path.stat', side_effect=FileNotFoundError("Arquivo não encontrado")):
                # Act
                size = fs_service.get_file_size(temp_file)

                # Assert
                assert size is None

    def test_get_file_size_directory(self, fs_service, temp_dir):
        """Testa get_file_size com um diretório."""
        # Act
        size = fs_service.get_file_size(temp_dir)

        # Assert
        assert size is None

    def test_stream_file_content(self, fs_service, temp_file):
        """Testa stream_file_content com um arquivo existente."""
        # Arrange
        expected_content = "Conteúdo de teste".encode('utf-8')

        # Act
        chunks = list(fs_service.stream_file_content(temp_file))
        content = b''.join(chunks)

        # Assert
        assert content == expected_content

    def test_stream_file_content_generic_error(self, fs_service, temp_file):
        """Testa stream_file_content com um erro genérico."""
        # Arrange
        with mock.patch('builtins.open', side_effect=Exception("Erro genérico")):
            # Act & Assert
            with pytest.raises(Exception):
                list(fs_service.stream_file_content(temp_file))

    def test_stream_file_content_permission_error(self, fs_service, temp_file):
        """Testa stream_file_content com erro de permissão."""
        # Arrange
        with mock.patch('builtins.open', side_effect=PermissionError("Sem permissão")):
            # Act & Assert
            with pytest.raises(PermissionError):
                list(fs_service.stream_file_content(temp_file))

    def test_stream_file_content_nonexistent_file(self, fs_service, temp_dir):
        """Testa stream_file_content com um arquivo inexistente."""
        # Arrange
        nonexistent_file = temp_dir / "nonexistent.txt"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            list(fs_service.stream_file_content(nonexistent_file))

    def test_stream_file_content_directory(self, fs_service, temp_dir):
        """Testa stream_file_content com um diretório."""
        # Act & Assert
        # Forçar IsADirectoryError para garantir cobertura dessa exceção específica
        with mock.patch('builtins.open', side_effect=IsADirectoryError("É um diretório")):
            with pytest.raises(IsADirectoryError):
                list(fs_service.stream_file_content(temp_dir))

    def test_list_directory_contents_non_recursive(self, fs_service, temp_dir):
        """Testa list_directory_contents sem recursão."""
        # Arrange
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.jpg"
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        file3 = subdir / "file3.txt"

        file1.touch()
        file2.touch()
        file3.touch()

        # Act
        files = list(fs_service.list_directory_contents(temp_dir, recursive=False))

        # Assert
        assert len(files) == 2
        assert file1 in files
        assert file2 in files
        assert file3 not in files

    def test_list_directory_contents_recursive(self, fs_service, temp_dir):
        """Testa list_directory_contents com recursão."""
        # Arrange
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.jpg"
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        file3 = subdir / "file3.txt"

        file1.touch()
        file2.touch()
        file3.touch()

        # Act
        files = list(fs_service.list_directory_contents(temp_dir, recursive=True))

        # Assert
        assert len(files) == 3
        assert file1 in files
        assert file2 in files
        assert file3 in files

    def test_list_directory_contents_with_extensions(self, fs_service, temp_dir):
        """Testa list_directory_contents com filtro de extensões."""
        # Arrange
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.jpg"
        file3 = temp_dir / "file3.png"

        file1.touch()
        file2.touch()
        file3.touch()

        # Act
        files = list(fs_service.list_directory_contents(temp_dir, file_extensions=['.jpg', '.png']))

        # Assert
        assert len(files) == 2
        assert file1 not in files
        assert file2 in files
        assert file3 in files

    def test_list_directory_contents_nonexistent_directory(self, fs_service, temp_dir):
        """Testa list_directory_contents com um diretório inexistente."""
        # Arrange
        nonexistent_dir = temp_dir / "nonexistent"

        # Act & Assert
        # Forçar FileNotFoundError para garantir cobertura dessa exceção específica
        with mock.patch('pathlib.Path.is_dir', side_effect=FileNotFoundError("Diretório não encontrado")):
            with pytest.raises(FileNotFoundError):
                list(fs_service.list_directory_contents(nonexistent_dir))

    def test_list_directory_contents_permission_error(self, fs_service, temp_dir):
        """Testa list_directory_contents com erro de permissão."""
        # Arrange
        with mock.patch('pathlib.Path.is_dir', return_value=True):
            with mock.patch('pathlib.Path.rglob', side_effect=PermissionError("Sem permissão")):
                # Act & Assert
                with pytest.raises(PermissionError):
                    list(fs_service.list_directory_contents(temp_dir))

    def test_list_directory_contents_generic_error(self, fs_service, temp_dir):
        """Testa list_directory_contents com um erro genérico."""
        # Arrange
        with mock.patch('pathlib.Path.is_dir', return_value=True):
            with mock.patch('pathlib.Path.rglob', side_effect=Exception("Erro genérico")):
                # Act & Assert
                with pytest.raises(Exception):
                    list(fs_service.list_directory_contents(temp_dir))

    def test_list_directory_contents_file(self, fs_service, temp_file):
        """Testa list_directory_contents com um arquivo em vez de diretório."""
        # Act & Assert
        with pytest.raises(NotADirectoryError):
            list(fs_service.list_directory_contents(temp_file))

    def test_move_to_trash(self, fs_service, temp_file):
        """Testa move_to_trash com um arquivo existente."""
        # Arrange
        with mock.patch('send2trash.send2trash') as mock_send2trash:
            # Act
            fs_service.move_to_trash(temp_file)

            # Assert
            mock_send2trash.assert_called_once_with(str(temp_file))

    def test_move_to_trash_generic_error(self, fs_service, temp_file):
        """Testa move_to_trash com um erro genérico."""
        # Arrange
        with mock.patch('pathlib.Path.exists', return_value=True):
            with mock.patch('send2trash.send2trash', side_effect=Exception("Erro genérico")):
                # Act & Assert
                with pytest.raises(Exception):
                    fs_service.move_to_trash(temp_file)

    def test_move_to_trash_nonexistent_file(self, fs_service, temp_dir):
        """Testa move_to_trash com um arquivo inexistente."""
        # Arrange
        nonexistent_file = temp_dir / "nonexistent.txt"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            fs_service.move_to_trash(nonexistent_file)

    def test_move_to_trash_permission_error(self, fs_service, temp_file):
        """Testa move_to_trash com erro de permissão."""
        # Arrange
        with mock.patch('pathlib.Path.exists', return_value=True):
            with mock.patch('send2trash.send2trash', side_effect=PermissionError("Sem permissão")):
                # Act & Assert
                with pytest.raises(PermissionError):
                    fs_service.move_to_trash(temp_file)

    def test_copy_file(self, fs_service, temp_file, temp_dir):
        """Testa copy_file com um arquivo existente."""
        # Arrange
        destination = temp_dir / "copy.txt"

        # Act
        fs_service.copy_file(temp_file, destination)

        # Assert
        assert destination.exists()
        with open(destination, 'rb') as f:
            content = f.read()
        assert content == "Conteúdo de teste".encode('utf-8')

    def test_copy_file_generic_error(self, fs_service, temp_file, temp_dir):
        """Testa copy_file com um erro genérico."""
        # Arrange
        destination = temp_dir / "copy.txt"
        with mock.patch('pathlib.Path.is_file', return_value=True):
            with mock.patch('shutil.copy2', side_effect=Exception("Erro genérico")):
                # Act & Assert
                with pytest.raises(Exception):
                    fs_service.copy_file(temp_file, destination)

    def test_copy_file_nonexistent_source(self, fs_service, temp_dir):
        """Testa copy_file com um arquivo de origem inexistente."""
        # Arrange
        nonexistent_file = temp_dir / "nonexistent.txt"
        destination = temp_dir / "copy.txt"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            fs_service.copy_file(nonexistent_file, destination)

    def test_copy_file_permission_error(self, fs_service, temp_file, temp_dir):
        """Testa copy_file com erro de permissão."""
        # Arrange
        destination = temp_dir / "copy.txt"
        with mock.patch('pathlib.Path.is_file', return_value=True):
            with mock.patch('shutil.copy2', side_effect=PermissionError("Sem permissão")):
                # Act & Assert
                with pytest.raises(PermissionError):
                    fs_service.copy_file(temp_file, destination)

    def test_copy_file_directory_source(self, fs_service, temp_dir):
        """Testa copy_file com um diretório como origem."""
        # Arrange
        destination = temp_dir / "copy"

        # Act & Assert
        with pytest.raises(IsADirectoryError):
            fs_service.copy_file(temp_dir, destination)

    def test_create_directory(self, fs_service, temp_dir):
        """Testa create_directory com um caminho válido."""
        # Arrange
        new_dir = temp_dir / "new_dir" / "subdir"

        # Act
        fs_service.create_directory(new_dir)

        # Assert
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_create_directory_existing(self, fs_service, temp_dir):
        """Testa create_directory com um diretório existente e exist_ok=True."""
        # Arrange
        # Primeiro, criar o diretório
        fs_service.create_directory(temp_dir)

        # Act - Não deve levantar exceção
        fs_service.create_directory(temp_dir, exist_ok=True)

    def test_create_directory_existing_not_ok(self, fs_service, temp_dir):
        """Testa create_directory com um diretório existente e exist_ok=False."""
        # Act & Assert
        with pytest.raises(FileExistsError):
            fs_service.create_directory(temp_dir, exist_ok=False)

    def test_create_directory_permission_error(self, fs_service, temp_dir):
        """Testa create_directory com erro de permissão."""
        # Arrange
        new_dir = temp_dir / "new_dir"
        with mock.patch('pathlib.Path.mkdir', side_effect=PermissionError("Sem permissão")):
            # Act & Assert
            with pytest.raises(PermissionError):
                fs_service.create_directory(new_dir)

    def test_create_directory_generic_error(self, fs_service, temp_dir):
        """Testa create_directory com um erro genérico."""
        # Arrange
        new_dir = temp_dir / "new_dir"
        with mock.patch('pathlib.Path.mkdir', side_effect=Exception("Erro genérico")):
            # Act & Assert
            with pytest.raises(Exception):
                fs_service.create_directory(new_dir)

    def test_path_exists(self, fs_service, temp_file, temp_dir):
        """Testa path_exists com caminhos existentes e inexistentes."""
        # Arrange
        nonexistent_file = temp_dir / "nonexistent.txt"

        # Act & Assert
        assert fs_service.path_exists(temp_file) is True
        assert fs_service.path_exists(temp_dir) is True
        assert fs_service.path_exists(nonexistent_file) is False

    def test_get_creation_time(self, fs_service, temp_file):
        """Testa get_creation_time com um arquivo existente."""
        # Act
        creation_time = fs_service.get_creation_time(temp_file)

        # Assert
        assert creation_time is not None
        assert isinstance(creation_time, float)
        # O timestamp deve ser recente (nos últimos 60 segundos)
        assert time.time() - creation_time < 60

    def test_get_creation_time_nonexistent_file(self, fs_service, temp_dir):
        """Testa get_creation_time com um arquivo inexistente."""
        # Arrange
        nonexistent_file = temp_dir / "nonexistent.txt"

        # Act
        creation_time = fs_service.get_creation_time(nonexistent_file)

        # Assert
        assert creation_time is None

    def test_get_modification_time(self, fs_service, temp_file):
        """Testa get_modification_time com um arquivo existente."""
        # Act
        modification_time = fs_service.get_modification_time(temp_file)

        # Assert
        assert modification_time is not None
        assert isinstance(modification_time, float)
        # O timestamp deve ser recente (nos últimos 60 segundos)
        assert time.time() - modification_time < 60

    def test_get_modification_time_nonexistent_file(self, fs_service, temp_dir):
        """Testa get_modification_time com um arquivo inexistente."""
        # Arrange
        nonexistent_file = temp_dir / "nonexistent.txt"

        # Act
        modification_time = fs_service.get_modification_time(nonexistent_file)

        # Assert
        assert modification_time is None

    def test_get_modification_time_error(self, fs_service, temp_file):
        """Testa get_modification_time com um erro genérico."""
        # Arrange
        with mock.patch('pathlib.Path.exists', return_value=True):
            with mock.patch('pathlib.Path.stat', side_effect=Exception("Erro genérico")):
                # Act
                modification_time = fs_service.get_modification_time(temp_file)

                # Assert
                assert modification_time is None

    def test_get_creation_time_error(self, fs_service, temp_file):
        """Testa get_creation_time com um erro genérico."""
        # Arrange
        with mock.patch('pathlib.Path.exists', return_value=True):
            with mock.patch('pathlib.Path.stat', side_effect=Exception("Erro genérico")):
                # Act
                creation_time = fs_service.get_creation_time(temp_file)

                # Assert
                assert creation_time is None
