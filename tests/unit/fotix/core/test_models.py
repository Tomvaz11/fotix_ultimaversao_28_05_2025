"""
Testes unitários para os modelos de dados do Fotix.

Este módulo contém testes para as classes FileInfo e DuplicateSet,
verificando a criação, validação e propriedades dessas classes.
"""

import os
from datetime import datetime
from pathlib import Path
import pytest

from fotix.core.models import FileInfo, DuplicateSet


class TestFileInfo:
    """Testes para a classe FileInfo."""

    def test_create_file_info(self):
        """Testa a criação básica de um FileInfo."""
        # Arrange & Act
        file_info = FileInfo(
            path=Path("/test/file.txt"),
            size=1024
        )

        # Assert
        assert file_info.path == Path("/test/file.txt")
        assert file_info.size == 1024
        assert file_info.hash is None
        assert file_info.creation_time is None
        assert file_info.modification_time is None
        assert file_info.in_zip is False
        assert file_info.zip_path is None
        assert file_info.original_path is None

    def test_create_file_info_with_all_fields(self):
        """Testa a criação de um FileInfo com todos os campos."""
        # Arrange
        now = datetime.now().timestamp()

        # Act
        file_info = FileInfo(
            path=Path("/test/file.txt"),
            size=1024,
            hash="abc123",
            creation_time=now,
            modification_time=now,
            in_zip=True,
            zip_path=Path("/test/archive.zip"),
            original_path=Path("/original/file.txt")
        )

        # Assert
        assert file_info.path == Path("/test/file.txt")
        assert file_info.size == 1024
        assert file_info.hash == "abc123"
        assert file_info.creation_time == now
        assert file_info.modification_time == now
        assert file_info.in_zip is True
        assert file_info.zip_path == Path("/test/archive.zip")
        assert file_info.original_path == Path("/original/file.txt")

    def test_post_init_conversion(self):
        """Testa a conversão de strings para Path no __post_init__."""
        # Act
        file_info = FileInfo(
            path="/test/file.txt",  # String em vez de Path
            size=1024,
            zip_path="/test/archive.zip",  # String em vez de Path
            original_path="/original/file.txt"  # String em vez de Path
        )

        # Assert
        assert isinstance(file_info.path, Path)
        assert file_info.path == Path("/test/file.txt")
        assert isinstance(file_info.zip_path, Path)
        assert file_info.zip_path == Path("/test/archive.zip")
        assert isinstance(file_info.original_path, Path)
        assert file_info.original_path == Path("/original/file.txt")

    def test_filename_property(self):
        """Testa a propriedade filename."""
        # Arrange
        file_info = FileInfo(
            path=Path("/test/file.txt"),
            size=1024
        )

        # Act & Assert
        assert file_info.filename == "file.txt"

    def test_extension_property(self):
        """Testa a propriedade extension."""
        # Arrange
        file_info = FileInfo(
            path=Path("/test/file.txt"),
            size=1024
        )

        # Act & Assert
        assert file_info.extension == ".txt"

    def test_creation_datetime_property(self):
        """Testa a propriedade creation_datetime."""
        # Arrange
        now = datetime.now().timestamp()
        file_info = FileInfo(
            path=Path("/test/file.txt"),
            size=1024,
            creation_time=now
        )

        # Act
        dt = file_info.creation_datetime

        # Assert
        assert isinstance(dt, datetime)
        assert dt.timestamp() == pytest.approx(now)

    def test_creation_datetime_property_none(self):
        """Testa a propriedade creation_datetime quando creation_time é None."""
        # Arrange
        file_info = FileInfo(
            path=Path("/test/file.txt"),
            size=1024,
            creation_time=None
        )

        # Act & Assert
        assert file_info.creation_datetime is None

    def test_modification_datetime_property(self):
        """Testa a propriedade modification_datetime."""
        # Arrange
        now = datetime.now().timestamp()
        file_info = FileInfo(
            path=Path("/test/file.txt"),
            size=1024,
            modification_time=now
        )

        # Act
        dt = file_info.modification_datetime

        # Assert
        assert isinstance(dt, datetime)
        assert dt.timestamp() == pytest.approx(now)

    def test_modification_datetime_property_none(self):
        """Testa a propriedade modification_datetime quando modification_time é None."""
        # Arrange
        file_info = FileInfo(
            path=Path("/test/file.txt"),
            size=1024,
            modification_time=None
        )

        # Act & Assert
        assert file_info.modification_datetime is None


class TestDuplicateSet:
    """Testes para a classe DuplicateSet."""

    def test_create_duplicate_set(self):
        """Testa a criação básica de um DuplicateSet."""
        # Arrange & Act
        duplicate_set = DuplicateSet()

        # Assert
        assert duplicate_set.files == []
        assert duplicate_set.hash is None
        assert duplicate_set.selected_file is None

    def test_size_property_empty(self):
        """Testa a propriedade size quando o conjunto está vazio."""
        # Arrange
        duplicate_set = DuplicateSet()

        # Act & Assert
        assert duplicate_set.size == 0

    def test_size_property(self):
        """Testa a propriedade size quando o conjunto tem arquivos."""
        # Arrange
        file_info = FileInfo(
            path=Path("/test/file.txt"),
            size=1024
        )
        duplicate_set = DuplicateSet(files=[file_info])

        # Act & Assert
        assert duplicate_set.size == 1024

    def test_count_property(self):
        """Testa a propriedade count."""
        # Arrange
        file_info1 = FileInfo(
            path=Path("/test/file1.txt"),
            size=1024
        )
        file_info2 = FileInfo(
            path=Path("/test/file2.txt"),
            size=1024
        )
        duplicate_set = DuplicateSet(files=[file_info1, file_info2])

        # Act & Assert
        assert duplicate_set.count == 2

    def test_add_file_first(self):
        """Testa a adição do primeiro arquivo ao conjunto."""
        # Arrange
        duplicate_set = DuplicateSet()
        file_info = FileInfo(
            path=Path("/test/file.txt"),
            size=1024,
            hash="abc123"
        )

        # Act
        duplicate_set.add_file(file_info)

        # Assert
        assert len(duplicate_set.files) == 1
        assert duplicate_set.files[0] == file_info
        assert duplicate_set.hash == "abc123"

    def test_add_file_matching_hash(self):
        """Testa a adição de um arquivo com hash correspondente."""
        # Arrange
        file_info1 = FileInfo(
            path=Path("/test/file1.txt"),
            size=1024,
            hash="abc123"
        )
        duplicate_set = DuplicateSet(files=[file_info1], hash="abc123")

        file_info2 = FileInfo(
            path=Path("/test/file2.txt"),
            size=1024,
            hash="abc123"
        )

        # Act
        duplicate_set.add_file(file_info2)

        # Assert
        assert len(duplicate_set.files) == 2
        assert duplicate_set.files[1] == file_info2

    def test_add_file_different_hash(self):
        """Testa a adição de um arquivo com hash diferente (deve lançar ValueError)."""
        # Arrange
        file_info1 = FileInfo(
            path=Path("/test/file1.txt"),
            size=1024,
            hash="abc123"
        )
        duplicate_set = DuplicateSet(files=[file_info1], hash="abc123")

        file_info2 = FileInfo(
            path=Path("/test/file2.txt"),
            size=1024,
            hash="def456"  # Hash diferente
        )

        # Act & Assert
        with pytest.raises(ValueError):
            duplicate_set.add_file(file_info2)
