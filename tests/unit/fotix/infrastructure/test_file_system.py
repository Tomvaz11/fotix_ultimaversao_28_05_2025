"""
Testes unitários para o módulo file_system.py.

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
from send2trash import TrashPermissionError

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
        temp_dir = tempfile.mkdtemp(prefix="fotix_test_")
        yield Path(temp_dir)
        # Limpeza após o teste
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def temp_file(self, temp_dir):
        """Fixture que cria um arquivo temporário para testes."""
        temp_file = temp_dir / "test_file.txt"
        with open(temp_file, "w") as f:
            f.write("Test content")
        yield temp_file
    
    @pytest.fixture
    def nested_dir_structure(self, temp_dir):
        """Fixture que cria uma estrutura de diretórios aninhados com arquivos."""
        # Cria subdiretórios
        subdir1 = temp_dir / "subdir1"
        subdir2 = temp_dir / "subdir2"
        subdir3 = subdir1 / "subdir3"
        
        for d in [subdir1, subdir2, subdir3]:
            d.mkdir()
        
        # Cria arquivos em cada diretório
        files = [
            temp_dir / "root_file.txt",
            subdir1 / "file1.txt",
            subdir1 / "image.jpg",
            subdir2 / "file2.txt",
            subdir3 / "file3.txt",
            subdir3 / "document.pdf"
        ]
        
        for i, file in enumerate(files):
            with open(file, "w") as f:
                f.write(f"Content of file {i}")
        
        return {
            "root": temp_dir,
            "subdirs": [subdir1, subdir2, subdir3],
            "files": files
        }
    
    def test_get_file_size_existing_file(self, fs_service, temp_file):
        """Testa get_file_size com um arquivo existente."""
        size = fs_service.get_file_size(temp_file)
        assert size == len("Test content")
    
    def test_get_file_size_nonexistent_file(self, fs_service, temp_dir):
        """Testa get_file_size com um arquivo inexistente."""
        nonexistent_file = temp_dir / "nonexistent.txt"
        size = fs_service.get_file_size(nonexistent_file)
        assert size is None
    
    def test_get_file_size_directory(self, fs_service, temp_dir):
        """Testa get_file_size com um diretório."""
        size = fs_service.get_file_size(temp_dir)
        assert size is None
    
    def test_stream_file_content(self, fs_service, temp_file):
        """Testa stream_file_content."""
        content = b"".join(fs_service.stream_file_content(temp_file))
        assert content == b"Test content"
    
    def test_stream_file_content_nonexistent_file(self, fs_service, temp_dir):
        """Testa stream_file_content com um arquivo inexistente."""
        nonexistent_file = temp_dir / "nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            list(fs_service.stream_file_content(nonexistent_file))
    
    def test_stream_file_content_directory(self, fs_service, temp_dir):
        """Testa stream_file_content com um diretório."""
        with pytest.raises(IsADirectoryError):
            list(fs_service.stream_file_content(temp_dir))
    
    def test_list_directory_contents_recursive(self, fs_service, nested_dir_structure):
        """Testa list_directory_contents com recursão."""
        files = list(fs_service.list_directory_contents(nested_dir_structure["root"], recursive=True))
        assert len(files) == len(nested_dir_structure["files"])
        for file in nested_dir_structure["files"]:
            assert file in files
    
    def test_list_directory_contents_non_recursive(self, fs_service, nested_dir_structure):
        """Testa list_directory_contents sem recursão."""
        files = list(fs_service.list_directory_contents(nested_dir_structure["root"], recursive=False))
        # Apenas arquivos na raiz
        root_files = [f for f in nested_dir_structure["files"] if f.parent == nested_dir_structure["root"]]
        assert len(files) == len(root_files)
        for file in root_files:
            assert file in files
    
    def test_list_directory_contents_with_extensions(self, fs_service, nested_dir_structure):
        """Testa list_directory_contents com filtro de extensões."""
        # Filtra apenas arquivos .jpg
        files = list(fs_service.list_directory_contents(
            nested_dir_structure["root"], 
            recursive=True,
            file_extensions=[".jpg"]
        ))
        jpg_files = [f for f in nested_dir_structure["files"] if f.suffix == ".jpg"]
        assert len(files) == len(jpg_files)
        for file in jpg_files:
            assert file in files
    
    def test_list_directory_contents_nonexistent_directory(self, fs_service, temp_dir):
        """Testa list_directory_contents com um diretório inexistente."""
        nonexistent_dir = temp_dir / "nonexistent"
        with pytest.raises(FileNotFoundError):
            list(fs_service.list_directory_contents(nonexistent_dir))
    
    def test_list_directory_contents_file(self, fs_service, temp_file):
        """Testa list_directory_contents com um arquivo."""
        with pytest.raises(NotADirectoryError):
            list(fs_service.list_directory_contents(temp_file))
    
    def test_move_to_trash(self, fs_service, temp_file):
        """Testa move_to_trash."""
        with mock.patch("fotix.infrastructure.file_system.send2trash") as mock_send2trash:
            fs_service.move_to_trash(temp_file)
            mock_send2trash.assert_called_once_with(str(temp_file))
    
    def test_move_to_trash_nonexistent_file(self, fs_service, temp_dir):
        """Testa move_to_trash com um arquivo inexistente."""
        nonexistent_file = temp_dir / "nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            fs_service.move_to_trash(nonexistent_file)
    
    def test_move_to_trash_disabled(self, fs_service, temp_file):
        """Testa move_to_trash com trash_enabled=False."""
        with mock.patch("fotix.infrastructure.file_system.get_config", return_value=False):
            fs_service.move_to_trash(temp_file)
            assert not temp_file.exists()
    
    def test_move_to_trash_permission_error(self, fs_service, temp_file):
        """Testa move_to_trash com erro de permissão."""
        with mock.patch("fotix.infrastructure.file_system.send2trash", side_effect=TrashPermissionError("Permission denied")):
            with pytest.raises(TrashPermissionError):
                fs_service.move_to_trash(temp_file)
    
    def test_copy_file(self, fs_service, temp_file, temp_dir):
        """Testa copy_file."""
        destination = temp_dir / "copy.txt"
        fs_service.copy_file(temp_file, destination)
        assert destination.exists()
        with open(destination, "r") as f:
            assert f.read() == "Test content"
    
    def test_copy_file_nonexistent_source(self, fs_service, temp_dir):
        """Testa copy_file com um arquivo de origem inexistente."""
        source = temp_dir / "nonexistent.txt"
        destination = temp_dir / "copy.txt"
        with pytest.raises(FileNotFoundError):
            fs_service.copy_file(source, destination)
    
    def test_copy_file_directory_source(self, fs_service, temp_dir):
        """Testa copy_file com um diretório como origem."""
        destination = temp_dir / "copy"
        with pytest.raises(IsADirectoryError):
            fs_service.copy_file(temp_dir, destination)
    
    def test_create_directory(self, fs_service, temp_dir):
        """Testa create_directory."""
        new_dir = temp_dir / "new_dir"
        fs_service.create_directory(new_dir)
        assert new_dir.exists() and new_dir.is_dir()
    
    def test_create_directory_nested(self, fs_service, temp_dir):
        """Testa create_directory com diretórios aninhados."""
        nested_dir = temp_dir / "parent" / "child" / "grandchild"
        fs_service.create_directory(nested_dir)
        assert nested_dir.exists() and nested_dir.is_dir()
    
    def test_create_directory_existing(self, fs_service, temp_dir):
        """Testa create_directory com um diretório existente e exist_ok=True."""
        fs_service.create_directory(temp_dir, exist_ok=True)
        assert temp_dir.exists() and temp_dir.is_dir()
    
    def test_create_directory_existing_error(self, fs_service, temp_dir):
        """Testa create_directory com um diretório existente e exist_ok=False."""
        with pytest.raises(FileExistsError):
            fs_service.create_directory(temp_dir, exist_ok=False)
    
    def test_path_exists(self, fs_service, temp_file, temp_dir):
        """Testa path_exists."""
        assert fs_service.path_exists(temp_file) is True
        assert fs_service.path_exists(temp_dir) is True
        nonexistent = temp_dir / "nonexistent.txt"
        assert fs_service.path_exists(nonexistent) is False
    
    def test_get_creation_time(self, fs_service, temp_file):
        """Testa get_creation_time."""
        creation_time = fs_service.get_creation_time(temp_file)
        assert creation_time is not None
        assert isinstance(creation_time, float)
        # O timestamp deve ser recente (nos últimos 10 segundos)
        assert time.time() - creation_time < 10
    
    def test_get_creation_time_nonexistent_file(self, fs_service, temp_dir):
        """Testa get_creation_time com um arquivo inexistente."""
        nonexistent_file = temp_dir / "nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            fs_service.get_creation_time(nonexistent_file)
    
    def test_get_modification_time(self, fs_service, temp_file):
        """Testa get_modification_time."""
        modification_time = fs_service.get_modification_time(temp_file)
        assert modification_time is not None
        assert isinstance(modification_time, float)
        # O timestamp deve ser recente (nos últimos 10 segundos)
        assert time.time() - modification_time < 10
    
    def test_get_modification_time_nonexistent_file(self, fs_service, temp_dir):
        """Testa get_modification_time com um arquivo inexistente."""
        nonexistent_file = temp_dir / "nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            fs_service.get_modification_time(nonexistent_file)
    
    def test_get_modification_time_after_update(self, fs_service, temp_file):
        """Testa get_modification_time após atualizar o arquivo."""
        initial_time = fs_service.get_modification_time(temp_file)
        
        # Espera um pouco para garantir que o timestamp será diferente
        time.sleep(0.1)
        
        # Atualiza o arquivo
        with open(temp_file, "w") as f:
            f.write("Updated content")
        
        updated_time = fs_service.get_modification_time(temp_file)
        assert updated_time > initial_time
