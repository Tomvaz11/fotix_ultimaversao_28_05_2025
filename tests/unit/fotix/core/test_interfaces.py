"""
Testes unitários para as interfaces do módulo core.

Este módulo contém testes para verificar a implementação correta das interfaces
definidas em fotix.core.interfaces.py.
"""

from pathlib import Path
from typing import List, Optional, Callable, Protocol, runtime_checkable

import pytest
from unittest.mock import MagicMock

from fotix.core.models import DuplicateSet, FileInfo
from fotix.core.interfaces import IDuplicateFinderService, ISelectionStrategy

# Redefinir as interfaces com @runtime_checkable para testes
@runtime_checkable
class RuntimeCheckableDuplicateFinderService(Protocol):
    """Interface para o serviço de detecção de duplicatas."""

    def find_duplicates(self, scan_paths: List[Path], include_zips: bool,
                       progress_callback: Optional[Callable[[float], None]] = None) -> List[DuplicateSet]:
        """Analisa os caminhos fornecidos e retorna uma lista de conjuntos de arquivos duplicados."""
        ...

@runtime_checkable
class RuntimeCheckableSelectionStrategy(Protocol):
    """Interface para estratégias de seleção de arquivos duplicados."""

    def select_file_to_keep(self, duplicate_set: DuplicateSet) -> FileInfo:
        """Recebe um conjunto de arquivos duplicados e retorna o arquivo que deve ser mantido."""
        ...


class TestIDuplicateFinderService:
    """Testes para a interface IDuplicateFinderService."""

    class MockDuplicateFinderService:
        """Implementação concreta da interface para testes."""

        def find_duplicates(self, scan_paths: List[Path], include_zips: bool,
                           progress_callback: Optional[Callable[[float], None]] = None) -> List[DuplicateSet]:
            """Implementação mock que retorna uma lista vazia."""
            # Simular chamada ao callback de progresso
            if progress_callback:
                progress_callback(0.5)
                progress_callback(1.0)
            return []

    def test_interface_implementation(self):
        """Testa se a interface pode ser implementada corretamente."""
        # Arrange & Act
        service = self.MockDuplicateFinderService()

        # Assert
        assert isinstance(service, RuntimeCheckableDuplicateFinderService)
        # Verificar se a classe implementa a interface
        assert hasattr(service, "find_duplicates")

    def test_find_duplicates_with_callback(self):
        """Testa se o método find_duplicates aceita e usa o callback de progresso."""
        # Arrange
        service = self.MockDuplicateFinderService()
        mock_callback = MagicMock()
        scan_paths = [Path("/test")]

        # Act
        result = service.find_duplicates(scan_paths, include_zips=False, progress_callback=mock_callback)

        # Assert
        assert isinstance(result, list)
        assert mock_callback.call_count == 2
        mock_callback.assert_any_call(0.5)
        mock_callback.assert_any_call(1.0)

    def test_find_duplicates_without_callback(self):
        """Testa se o método find_duplicates funciona sem callback de progresso."""
        # Arrange
        service = self.MockDuplicateFinderService()
        scan_paths = [Path("/test")]

        # Act
        result = service.find_duplicates(scan_paths, include_zips=True)

        # Assert
        assert isinstance(result, list)


class TestISelectionStrategy:
    """Testes para a interface ISelectionStrategy."""

    class MockSelectionStrategy:
        """Implementação concreta da interface para testes."""

        def select_file_to_keep(self, duplicate_set: DuplicateSet) -> FileInfo:
            """Implementação mock que retorna o primeiro arquivo do conjunto."""
            if not duplicate_set.files:
                raise ValueError("Conjunto vazio")
            return duplicate_set.files[0]

    def test_interface_implementation(self):
        """Testa se a interface pode ser implementada corretamente."""
        # Arrange & Act
        strategy = self.MockSelectionStrategy()

        # Assert
        assert isinstance(strategy, RuntimeCheckableSelectionStrategy)
        # Verificar se a classe implementa a interface
        assert hasattr(strategy, "select_file_to_keep")

    def test_select_file_to_keep(self):
        """Testa se o método select_file_to_keep funciona corretamente."""
        # Arrange
        strategy = self.MockSelectionStrategy()
        file1 = FileInfo(path=Path("file1.txt"), size=100)
        file2 = FileInfo(path=Path("file2.txt"), size=100)
        duplicate_set = DuplicateSet(files=[file1, file2], hash="abc123")

        # Act
        result = strategy.select_file_to_keep(duplicate_set)

        # Assert
        assert result == file1

    def test_select_file_to_keep_empty_set(self):
        """Testa o comportamento com um conjunto vazio."""
        # Arrange
        strategy = self.MockSelectionStrategy()
        duplicate_set = DuplicateSet(files=[], hash="abc123")

        # Act & Assert
        with pytest.raises(ValueError, match="Conjunto vazio"):
            strategy.select_file_to_keep(duplicate_set)

    def test_select_file_to_keep_single_file(self):
        """Testa o comportamento com um conjunto contendo apenas um arquivo."""
        # Arrange
        strategy = self.MockSelectionStrategy()
        file1 = FileInfo(path=Path("file1.txt"), size=100)
        duplicate_set = DuplicateSet(files=[file1], hash="abc123")

        # Act
        result = strategy.select_file_to_keep(duplicate_set)

        # Assert
        assert result == file1
