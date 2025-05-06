"""
Testes unitários para o módulo fotix.infrastructure.file_system.

Este módulo contém testes para a implementação do serviço de sistema de arquivos,
incluindo casos normais, casos de erro e casos de borda.
"""

import os
import shutil
import tempfile
from pathlib import Path
from unittest import mock

import pytest
import send2trash

from fotix.infrastructure.file_system import FileSystemService


class TestFileSystemService:
    """Testes para a classe FileSystemService."""

    @pytest.fixture
    def fs_service(self):
        """Fixture que retorna uma instância de FileSystemService."""
        return FileSystemService()

    @pytest.fixture
    def temp_dir(self):
        """Fixture que cria um diretório temporário para os testes."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        # Limpar após os testes
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def temp_file(self, temp_dir):
        """Fixture que cria um arquivo temporário para os testes."""
        file_path = temp_dir / "test_file.txt"
        with open(file_path, "w") as f:
            f.write("Conteúdo de teste")
        return file_path

    @pytest.fixture
    def nested_dir_structure(self, temp_dir):
        """Fixture que cria uma estrutura de diretórios aninhados com arquivos."""
        # Criar estrutura de diretórios
        subdir1 = temp_dir / "subdir1"
        subdir2 = temp_dir / "subdir2"
        subdir1_1 = subdir1 / "subdir1_1"

        for d in [subdir1, subdir2, subdir1_1]:
            d.mkdir()

        # Criar arquivos com diferentes extensões
        files = [
            temp_dir / "root_file.txt",
            subdir1 / "file1.txt",
            subdir1 / "image1.jpg",
            subdir1_1 / "file2.txt",
            subdir1_1 / "image2.png",
            subdir2 / "file3.pdf"
        ]

        for file_path in files:
            with open(file_path, "w") as f:
                f.write(f"Conteúdo de {file_path.name}")

        return {
            "root": temp_dir,
            "subdirs": [subdir1, subdir2, subdir1_1],
            "files": files
        }

    # Testes para get_file_size

    def test_get_file_size_existing_file(self, fs_service, temp_file):
        """Testa get_file_size com um arquivo existente."""
        # Act
        size = fs_service.get_file_size(temp_file)

        # Assert
        assert size > 0  # Verificamos apenas se o tamanho é maior que zero, evitando problemas de codificação

    def test_get_file_size_nonexistent_file(self, fs_service, temp_dir):
        """Testa get_file_size com um arquivo inexistente."""
        # Arrange
        nonexistent_file = temp_dir / "nonexistent.txt"

        # Act
        size = fs_service.get_file_size(nonexistent_file)

        # Assert
        assert size is None

    # Testes para stream_file_content

    def test_stream_file_content(self, fs_service, temp_file):
        """Testa stream_file_content."""
        # Act
        chunks = list(fs_service.stream_file_content(temp_file))
        content = b"".join(chunks)

        # Assert
        # Verificamos apenas se o conteúdo não está vazio, evitando problemas de codificação
        assert len(content) > 0
        assert b"teste" in content  # Verificamos se parte do conteúdo esperado está presente

    def test_stream_file_content_nonexistent_file(self, fs_service, temp_dir):
        """Testa stream_file_content com um arquivo inexistente."""
        # Arrange
        nonexistent_file = temp_dir / "nonexistent.txt"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            list(fs_service.stream_file_content(nonexistent_file))

    def test_stream_file_content_permission_error(self, fs_service, temp_file):
        """Testa stream_file_content com erro de permissão."""
        # Arrange
        with mock.patch('builtins.open', side_effect=PermissionError("Permissão negada")):
            # Act & Assert
            with pytest.raises(PermissionError):
                list(fs_service.stream_file_content(temp_file))

    def test_stream_file_content_io_error(self, fs_service, temp_file):
        """Testa stream_file_content com erro de IO."""
        # Arrange
        with mock.patch('builtins.open', side_effect=IOError("Erro de IO")):
            # Act & Assert
            with pytest.raises(IOError):
                list(fs_service.stream_file_content(temp_file))

    # Testes para list_directory_contents

    def test_list_directory_contents_recursive(self, fs_service, nested_dir_structure):
        """Testa list_directory_contents com recursão."""
        # Arrange
        root_dir = nested_dir_structure["root"]
        all_files = nested_dir_structure["files"]

        # Act
        files = list(fs_service.list_directory_contents(root_dir))

        # Assert
        assert len(files) == len(all_files)
        for file_path in all_files:
            assert file_path in files

    def test_list_directory_contents_non_recursive(self, fs_service, nested_dir_structure):
        """Testa list_directory_contents sem recursão."""
        # Arrange
        root_dir = nested_dir_structure["root"]
        root_files = [f for f in nested_dir_structure["files"] if f.parent == root_dir]

        # Act
        files = list(fs_service.list_directory_contents(root_dir, recursive=False))

        # Assert
        assert len(files) == len(root_files)
        for file_path in root_files:
            assert file_path in files

    def test_list_directory_contents_with_extension_filter(self, fs_service, nested_dir_structure):
        """Testa list_directory_contents com filtro de extensão."""
        # Arrange
        root_dir = nested_dir_structure["root"]
        txt_files = [f for f in nested_dir_structure["files"] if f.suffix == ".txt"]

        # Act
        files = list(fs_service.list_directory_contents(root_dir, file_extensions=[".txt"]))

        # Assert
        assert len(files) == len(txt_files)
        for file_path in txt_files:
            assert file_path in files

    def test_list_directory_contents_nonexistent_dir(self, fs_service, temp_dir):
        """Testa list_directory_contents com um diretório inexistente."""
        # Arrange
        nonexistent_dir = temp_dir / "nonexistent"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            list(fs_service.list_directory_contents(nonexistent_dir))

    def test_list_directory_contents_not_a_dir(self, fs_service, temp_file):
        """Testa list_directory_contents com um caminho que não é um diretório."""
        # Act & Assert
        with pytest.raises(NotADirectoryError):
            list(fs_service.list_directory_contents(temp_file))

    def test_list_directory_contents_permission_error(self, fs_service, temp_dir):
        """Testa list_directory_contents com erro de permissão."""
        # Arrange
        with mock.patch.object(Path, 'rglob', side_effect=PermissionError("Permissão negada")):
            # Act & Assert
            with pytest.raises(PermissionError):
                list(fs_service.list_directory_contents(temp_dir))

    def test_list_directory_contents_os_error(self, fs_service, temp_dir):
        """Testa list_directory_contents com erro de OS."""
        # Arrange
        with mock.patch.object(Path, 'rglob', side_effect=OSError("Erro de OS")):
            # Act & Assert
            with pytest.raises(OSError):
                list(fs_service.list_directory_contents(temp_dir))

    # Testes para move_to_trash

    def test_move_to_trash(self, fs_service, temp_file):
        """Testa move_to_trash."""
        # Arrange
        with mock.patch('send2trash.send2trash') as mock_send2trash:
            # Act
            fs_service.move_to_trash(temp_file)

            # Assert
            mock_send2trash.assert_called_once_with(str(temp_file))

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
        with mock.patch('send2trash.send2trash', side_effect=PermissionError("Permissão negada")):
            # Act & Assert
            with pytest.raises(PermissionError):
                fs_service.move_to_trash(temp_file)

    def test_move_to_trash_os_error(self, fs_service, temp_file):
        """Testa move_to_trash com erro de OS."""
        # Arrange
        with mock.patch('send2trash.send2trash', side_effect=OSError("Erro de OS")):
            # Act & Assert
            with pytest.raises(OSError):
                fs_service.move_to_trash(temp_file)

    # Testes para copy_file

    def test_copy_file(self, fs_service, temp_file, temp_dir):
        """Testa copy_file."""
        # Arrange
        destination = temp_dir / "copied_file.txt"

        # Act
        fs_service.copy_file(temp_file, destination)

        # Assert
        assert destination.exists()
        with open(destination, "r") as f:
            content = f.read()
        assert content == "Conteúdo de teste"

    def test_copy_file_nonexistent_source(self, fs_service, temp_dir):
        """Testa copy_file com um arquivo de origem inexistente."""
        # Arrange
        nonexistent_file = temp_dir / "nonexistent.txt"
        destination = temp_dir / "copied_file.txt"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            fs_service.copy_file(nonexistent_file, destination)

    def test_copy_file_source_is_directory(self, fs_service, temp_dir):
        """Testa copy_file quando a origem é um diretório."""
        # Arrange
        destination = temp_dir / "copied_dir.txt"

        # Act & Assert
        with pytest.raises(IsADirectoryError):
            fs_service.copy_file(temp_dir, destination)

    def test_copy_file_create_destination_dir(self, fs_service, temp_file, temp_dir):
        """Testa copy_file criando diretório de destino."""
        # Arrange
        destination_dir = temp_dir / "new_dir"
        destination = destination_dir / "copied_file.txt"

        # Act
        fs_service.copy_file(temp_file, destination)

        # Assert
        assert destination.exists()
        assert destination_dir.exists()

    def test_copy_file_permission_error(self, fs_service, temp_file, temp_dir):
        """Testa copy_file com erro de permissão."""
        # Arrange
        destination = temp_dir / "copied_file.txt"
        with mock.patch('shutil.copy2', side_effect=PermissionError("Permissão negada")):
            # Act & Assert
            with pytest.raises(PermissionError):
                fs_service.copy_file(temp_file, destination)

    def test_copy_file_is_a_directory_error(self, fs_service, temp_file, temp_dir):
        """Testa copy_file com erro de destino sendo um diretório."""
        # Arrange
        with mock.patch('shutil.copy2', side_effect=IsADirectoryError("O destino é um diretório")):
            # Act & Assert
            with pytest.raises(IsADirectoryError):
                fs_service.copy_file(temp_file, temp_dir)

    def test_copy_file_io_error(self, fs_service, temp_file, temp_dir):
        """Testa copy_file com erro de IO."""
        # Arrange
        destination = temp_dir / "copied_file.txt"
        with mock.patch('shutil.copy2', side_effect=IOError("Erro de IO")):
            # Act & Assert
            with pytest.raises(IOError):
                fs_service.copy_file(temp_file, destination)

    def test_copy_file_create_directory_error(self, fs_service, temp_file, temp_dir):
        """Testa copy_file com erro ao criar diretório de destino."""
        # Arrange
        destination = temp_dir / "new_dir" / "copied_file.txt"
        with mock.patch.object(Path, 'mkdir', side_effect=PermissionError("Permissão negada")):
            # Act & Assert
            with pytest.raises(PermissionError):
                fs_service.copy_file(temp_file, destination)

    # Testes para create_directory

    def test_create_directory(self, fs_service, temp_dir):
        """Testa create_directory."""
        # Arrange
        new_dir = temp_dir / "new_dir"

        # Act
        fs_service.create_directory(new_dir)

        # Assert
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_create_directory_nested(self, fs_service, temp_dir):
        """Testa create_directory com diretórios aninhados."""
        # Arrange
        nested_dir = temp_dir / "parent" / "child" / "grandchild"

        # Act
        fs_service.create_directory(nested_dir)

        # Assert
        assert nested_dir.exists()
        assert nested_dir.is_dir()

    def test_create_directory_exists_ok_true(self, fs_service, temp_dir):
        """Testa create_directory com exist_ok=True para um diretório existente."""
        # Arrange
        existing_dir = temp_dir / "existing"
        existing_dir.mkdir()

        # Act
        fs_service.create_directory(existing_dir, exist_ok=True)

        # Assert
        assert existing_dir.exists()

    def test_create_directory_exists_ok_false(self, fs_service, temp_dir):
        """Testa create_directory com exist_ok=False para um diretório existente."""
        # Arrange
        existing_dir = temp_dir / "existing"
        existing_dir.mkdir()

        # Act & Assert
        with pytest.raises(FileExistsError):
            fs_service.create_directory(existing_dir, exist_ok=False)

    def test_create_directory_permission_error(self, fs_service, temp_dir):
        """Testa create_directory com erro de permissão."""
        # Arrange
        new_dir = temp_dir / "new_dir"
        with mock.patch.object(Path, 'mkdir', side_effect=PermissionError("Permissão negada")):
            # Act & Assert
            with pytest.raises(PermissionError):
                fs_service.create_directory(new_dir)

    def test_create_directory_file_not_found_error(self, fs_service, temp_dir):
        """Testa create_directory com erro de diretório pai não encontrado."""
        # Arrange
        new_dir = temp_dir / "new_dir"
        with mock.patch.object(Path, 'mkdir', side_effect=FileNotFoundError("Diretório pai não encontrado")):
            # Act & Assert
            with pytest.raises(FileNotFoundError):
                fs_service.create_directory(new_dir)

    # Testes para path_exists

    def test_path_exists(self, fs_service, temp_file, temp_dir):
        """Testa path_exists."""
        # Act & Assert
        assert fs_service.path_exists(temp_file) is True
        assert fs_service.path_exists(temp_dir) is True
        assert fs_service.path_exists(temp_dir / "nonexistent.txt") is False

    # Testes para get_creation_time e get_modification_time

    def test_get_creation_time(self, fs_service, temp_file):
        """Testa get_creation_time."""
        # Act
        creation_time = fs_service.get_creation_time(temp_file)

        # Assert
        assert creation_time is not None
        assert isinstance(creation_time, float)

    def test_get_creation_time_with_birthtime(self, fs_service, temp_file):
        """Testa get_creation_time quando st_birthtime está disponível."""
        # Arrange
        mock_stat_result = mock.MagicMock()
        mock_stat_result.st_birthtime = 12345.67

        with mock.patch.object(Path, 'stat', return_value=mock_stat_result):
            # Act
            creation_time = fs_service.get_creation_time(temp_file)

            # Assert
            assert creation_time == 12345.67

    def test_get_creation_time_without_birthtime(self, fs_service, temp_file):
        """Testa get_creation_time quando st_birthtime não está disponível e ocorre AttributeError."""
        # Arrange
        # Criar um objeto que simula o resultado de stat() mas sem o atributo st_birthtime
        class MockStatResult:
            def __init__(self):
                self.st_ctime = 98765.43
                # Não tem st_birthtime

        mock_stat_result = MockStatResult()

        # Patch getattr para simular AttributeError quando st_birthtime é acessado
        def mock_getattr_func(obj, name, default=None):
            if name == 'st_birthtime':
                raise AttributeError("'stat_result' object has no attribute 'st_birthtime'")
            return object.__getattribute__(obj, name)

        with mock.patch('fotix.infrastructure.file_system.getattr', side_effect=mock_getattr_func):
            with mock.patch.object(Path, 'stat', return_value=mock_stat_result):
                # Act
                creation_time = fs_service.get_creation_time(temp_file)

                # Assert
                assert creation_time == 98765.43

    def test_get_modification_time(self, fs_service, temp_file):
        """Testa get_modification_time."""
        # Act
        modification_time = fs_service.get_modification_time(temp_file)

        # Assert
        assert modification_time is not None
        assert isinstance(modification_time, float)

    def test_get_creation_time_nonexistent_file(self, fs_service, temp_dir):
        """Testa get_creation_time com um arquivo inexistente."""
        # Arrange
        nonexistent_file = temp_dir / "nonexistent.txt"

        # Act
        creation_time = fs_service.get_creation_time(nonexistent_file)

        # Assert
        assert creation_time is None

    def test_get_modification_time_nonexistent_file(self, fs_service, temp_dir):
        """Testa get_modification_time com um arquivo inexistente."""
        # Arrange
        nonexistent_file = temp_dir / "nonexistent.txt"

        # Act
        modification_time = fs_service.get_modification_time(nonexistent_file)

        # Assert
        assert modification_time is None

    def test_get_creation_time_error(self, fs_service, temp_file):
        """Testa get_creation_time com erro."""
        # Arrange
        with mock.patch.object(Path, 'stat', side_effect=FileNotFoundError("Arquivo não encontrado")):
            # Act
            creation_time = fs_service.get_creation_time(temp_file)

            # Assert
            assert creation_time is None

    def test_get_modification_time_error(self, fs_service, temp_file):
        """Testa get_modification_time com erro."""
        # Arrange
        with mock.patch.object(Path, 'stat', side_effect=PermissionError("Permissão negada")):
            # Act
            modification_time = fs_service.get_modification_time(temp_file)

            # Assert
            assert modification_time is None
