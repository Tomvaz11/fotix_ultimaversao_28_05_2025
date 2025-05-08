"""
Testes unitários para o módulo models.py.

Este módulo contém testes para as classes de modelo do domínio,
como FileInfo e DuplicateSet.
"""

from datetime import datetime
from pathlib import Path

import pytest

from fotix.core.models import DuplicateSet, FileInfo


class TestFileInfo:
    """Testes para a classe FileInfo."""
    
    def test_create_file_info(self):
        """Testa a criação de um FileInfo básico."""
        path = Path("/path/to/file.jpg")
        size = 1024
        file_info = FileInfo(path=path, size=size)
        
        assert file_info.path == path
        assert file_info.size == size
        assert file_info.creation_time is None
        assert file_info.modification_time is None
        assert file_info.hash_value is None
        assert file_info.in_zip is False
        assert file_info.zip_path is None
    
    def test_create_file_info_with_all_fields(self):
        """Testa a criação de um FileInfo com todos os campos."""
        path = Path("/path/to/file.jpg")
        size = 1024
        creation_time = 1620000000.0
        modification_time = 1630000000.0
        hash_value = "abc123"
        in_zip = True
        zip_path = Path("/path/to/archive.zip")
        
        file_info = FileInfo(
            path=path,
            size=size,
            creation_time=creation_time,
            modification_time=modification_time,
            hash_value=hash_value,
            in_zip=in_zip,
            zip_path=zip_path
        )
        
        assert file_info.path == path
        assert file_info.size == size
        assert file_info.creation_time == creation_time
        assert file_info.modification_time == modification_time
        assert file_info.hash_value == hash_value
        assert file_info.in_zip is True
        assert file_info.zip_path == zip_path
    
    def test_name_property(self):
        """Testa a propriedade name."""
        path = Path("/path/to/file.jpg")
        file_info = FileInfo(path=path, size=1024)
        assert file_info.name == "file.jpg"
    
    def test_extension_property(self):
        """Testa a propriedade extension."""
        path = Path("/path/to/file.JPG")  # Maiúsculas para testar normalização
        file_info = FileInfo(path=path, size=1024)
        assert file_info.extension == ".jpg"  # Deve estar em minúsculas
    
    def test_creation_datetime_property(self):
        """Testa a propriedade creation_datetime."""
        path = Path("/path/to/file.jpg")
        creation_time = 1620000000.0  # 2021-05-03 00:00:00 UTC
        file_info = FileInfo(path=path, size=1024, creation_time=creation_time)
        
        assert file_info.creation_datetime is not None
        assert isinstance(file_info.creation_datetime, datetime)
        assert file_info.creation_datetime == datetime.fromtimestamp(creation_time)
    
    def test_creation_datetime_property_none(self):
        """Testa a propriedade creation_datetime quando creation_time é None."""
        path = Path("/path/to/file.jpg")
        file_info = FileInfo(path=path, size=1024)  # creation_time é None por padrão
        
        assert file_info.creation_datetime is None
    
    def test_modification_datetime_property(self):
        """Testa a propriedade modification_datetime."""
        path = Path("/path/to/file.jpg")
        modification_time = 1630000000.0  # 2021-08-26 13:20:00 UTC
        file_info = FileInfo(path=path, size=1024, modification_time=modification_time)
        
        assert file_info.modification_datetime is not None
        assert isinstance(file_info.modification_datetime, datetime)
        assert file_info.modification_datetime == datetime.fromtimestamp(modification_time)
    
    def test_modification_datetime_property_none(self):
        """Testa a propriedade modification_datetime quando modification_time é None."""
        path = Path("/path/to/file.jpg")
        file_info = FileInfo(path=path, size=1024)  # modification_time é None por padrão
        
        assert file_info.modification_datetime is None
    
    def test_str_representation(self):
        """Testa a representação em string."""
        path = Path("/path/to/file.jpg")
        size = 1024
        file_info = FileInfo(path=path, size=size)
        
        assert str(file_info) == f"FileInfo(path='{path}', size={size} bytes)"


class TestDuplicateSet:
    """Testes para a classe DuplicateSet."""
    
    @pytest.fixture
    def sample_files(self):
        """Fixture que retorna uma lista de FileInfo para testes."""
        return [
            FileInfo(path=Path("/path/to/file1.jpg"), size=1024, hash_value="abc123"),
            FileInfo(path=Path("/path/to/file2.jpg"), size=1024, hash_value="abc123"),
            FileInfo(path=Path("/path/to/file3.jpg"), size=1024, hash_value="abc123")
        ]
    
    def test_create_duplicate_set(self, sample_files):
        """Testa a criação de um DuplicateSet."""
        duplicate_set = DuplicateSet(files=sample_files, hash_value="abc123")
        
        assert duplicate_set.files == sample_files
        assert duplicate_set.hash_value == "abc123"
    
    def test_size_property(self, sample_files):
        """Testa a propriedade size."""
        duplicate_set = DuplicateSet(files=sample_files, hash_value="abc123")
        assert duplicate_set.size == 1024  # Tamanho do primeiro arquivo
    
    def test_size_property_empty(self):
        """Testa a propriedade size com lista de arquivos vazia."""
        duplicate_set = DuplicateSet(files=[], hash_value="abc123")
        assert duplicate_set.size == 0
    
    def test_count_property(self, sample_files):
        """Testa a propriedade count."""
        duplicate_set = DuplicateSet(files=sample_files, hash_value="abc123")
        assert duplicate_set.count == 3
    
    def test_str_representation(self, sample_files):
        """Testa a representação em string."""
        duplicate_set = DuplicateSet(files=sample_files, hash_value="abc123")
        assert str(duplicate_set) == f"DuplicateSet(hash='abc123...', count=3, size=1024 bytes)"
