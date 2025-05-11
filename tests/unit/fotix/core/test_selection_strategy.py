"""
Testes unitários para o módulo de estratégias de seleção.

Este módulo contém testes para verificar o funcionamento correto das
estratégias de seleção de arquivos duplicados definidas em fotix.core.selection_strategy.
"""

from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from fotix.core.models import DuplicateSet, FileInfo
from fotix.core.selection_strategy import (
    BaseSelectionStrategy,
    CreationDateStrategy,
    ModificationDateStrategy,
    HighestResolutionStrategy,
    ShortestNameStrategy,
    CompositeStrategy,
    create_strategy
)
from fotix.utils.image_utils import is_image_file, get_image_resolution


# Classe de teste concreta para BaseSelectionStrategy
class TestSelectionStrategy(BaseSelectionStrategy):
    """Implementação concreta de BaseSelectionStrategy para testes."""
    
    def _select_file(self, duplicate_set):
        """Implementação simples que retorna o primeiro arquivo."""
        return duplicate_set.files[0]


class TestBaseSelectionStrategy:
    """Testes para a classe base BaseSelectionStrategy."""

    def test_select_file_to_keep_empty_set(self):
        """Testa se a função levanta ValueError para um conjunto vazio."""
        # Arrange
        strategy = TestSelectionStrategy()
        duplicate_set = DuplicateSet(files=[], hash="abc123")
        
        # Act & Assert
        with pytest.raises(ValueError, match="O conjunto de duplicatas está vazio"):
            strategy.select_file_to_keep(duplicate_set)

    def test_select_file_to_keep_single_file(self):
        """Testa se a função retorna o único arquivo quando há apenas um."""
        # Arrange
        strategy = TestSelectionStrategy()
        file_info = FileInfo(path=Path("file.txt"), size=100)
        duplicate_set = DuplicateSet(files=[file_info], hash="abc123")
        
        # Act
        result = strategy.select_file_to_keep(duplicate_set)
        
        # Assert
        assert result == file_info

    def test_select_file_to_keep_calls_select_file(self):
        """Testa se select_file_to_keep chama o método _select_file."""
        # Arrange
        strategy = TestSelectionStrategy()
        file1 = FileInfo(path=Path("file1.txt"), size=100)
        file2 = FileInfo(path=Path("file2.txt"), size=100)
        duplicate_set = DuplicateSet(files=[file1, file2], hash="abc123")
        
        # Mock o método _select_file
        strategy._select_file = MagicMock(return_value=file1)
        
        # Act
        result = strategy.select_file_to_keep(duplicate_set)
        
        # Assert
        strategy._select_file.assert_called_once_with(duplicate_set)
        assert result == file1


class TestCreationDateStrategy:
    """Testes para a estratégia CreationDateStrategy."""

    def test_select_oldest_file(self):
        """Testa se a estratégia seleciona o arquivo mais antigo."""
        # Arrange
        strategy = CreationDateStrategy()
        
        # Criar arquivos com diferentes datas de criação
        file1 = FileInfo(path=Path("file1.txt"), size=100, creation_time=1600000000)  # Mais antigo
        file2 = FileInfo(path=Path("file2.txt"), size=100, creation_time=1600001000)
        file3 = FileInfo(path=Path("file3.txt"), size=100, creation_time=1600002000)
        
        duplicate_set = DuplicateSet(files=[file1, file2, file3], hash="abc123")
        
        # Act
        result = strategy.select_file_to_keep(duplicate_set)
        
        # Assert
        assert result == file1

    def test_select_with_missing_creation_dates(self):
        """Testa o comportamento quando alguns arquivos não têm data de criação."""
        # Arrange
        strategy = CreationDateStrategy()
        
        # Criar arquivos, alguns sem data de criação
        file1 = FileInfo(path=Path("file1.txt"), size=100, creation_time=None)
        file2 = FileInfo(path=Path("file2.txt"), size=100, creation_time=1600001000)  # Mais antigo com data
        file3 = FileInfo(path=Path("file3.txt"), size=100, creation_time=1600002000)
        
        duplicate_set = DuplicateSet(files=[file1, file2, file3], hash="abc123")
        
        # Act
        result = strategy.select_file_to_keep(duplicate_set)
        
        # Assert
        assert result == file2

    def test_select_all_missing_creation_dates(self):
        """Testa o comportamento quando nenhum arquivo tem data de criação."""
        # Arrange
        strategy = CreationDateStrategy()
        
        # Criar arquivos sem data de criação
        file1 = FileInfo(path=Path("file1.txt"), size=100, creation_time=None)
        file2 = FileInfo(path=Path("file2.txt"), size=100, creation_time=None)
        
        duplicate_set = DuplicateSet(files=[file1, file2], hash="abc123")
        
        # Act
        result = strategy.select_file_to_keep(duplicate_set)
        
        # Assert
        assert result == file1  # Deve retornar o primeiro arquivo


class TestModificationDateStrategy:
    """Testes para a estratégia ModificationDateStrategy."""

    def test_select_newest_file(self):
        """Testa se a estratégia seleciona o arquivo mais recente."""
        # Arrange
        strategy = ModificationDateStrategy()
        
        # Criar arquivos com diferentes datas de modificação
        file1 = FileInfo(path=Path("file1.txt"), size=100, modification_time=1600000000)
        file2 = FileInfo(path=Path("file2.txt"), size=100, modification_time=1600001000)
        file3 = FileInfo(path=Path("file3.txt"), size=100, modification_time=1600002000)  # Mais recente
        
        duplicate_set = DuplicateSet(files=[file1, file2, file3], hash="abc123")
        
        # Act
        result = strategy.select_file_to_keep(duplicate_set)
        
        # Assert
        assert result == file3

    def test_select_with_missing_modification_dates(self):
        """Testa o comportamento quando alguns arquivos não têm data de modificação."""
        # Arrange
        strategy = ModificationDateStrategy()
        
        # Criar arquivos, alguns sem data de modificação
        file1 = FileInfo(path=Path("file1.txt"), size=100, modification_time=None)
        file2 = FileInfo(path=Path("file2.txt"), size=100, modification_time=1600001000)
        file3 = FileInfo(path=Path("file3.txt"), size=100, modification_time=1600002000)  # Mais recente com data
        
        duplicate_set = DuplicateSet(files=[file1, file2, file3], hash="abc123")
        
        # Act
        result = strategy.select_file_to_keep(duplicate_set)
        
        # Assert
        assert result == file3

    def test_select_all_missing_modification_dates(self):
        """Testa o comportamento quando nenhum arquivo tem data de modificação."""
        # Arrange
        strategy = ModificationDateStrategy()
        
        # Criar arquivos sem data de modificação
        file1 = FileInfo(path=Path("file1.txt"), size=100, modification_time=None)
        file2 = FileInfo(path=Path("file2.txt"), size=100, modification_time=None)
        
        duplicate_set = DuplicateSet(files=[file1, file2], hash="abc123")
        
        # Act
        result = strategy.select_file_to_keep(duplicate_set)
        
        # Assert
        assert result == file1  # Deve retornar o primeiro arquivo


class TestHighestResolutionStrategy:
    """Testes para a estratégia HighestResolutionStrategy."""

    def test_select_highest_resolution_image(self):
        """Testa se a estratégia seleciona a imagem com maior resolução."""
        # Arrange
        mock_fs_service = MagicMock()
        strategy = HighestResolutionStrategy(file_system_service=mock_fs_service)
        
        # Criar arquivos de imagem
        file1 = FileInfo(path=Path("image1.jpg"), size=100)
        file2 = FileInfo(path=Path("image2.jpg"), size=100)
        file3 = FileInfo(path=Path("image3.jpg"), size=100)
        
        duplicate_set = DuplicateSet(files=[file1, file2, file3], hash="abc123")
        
        # Mock para is_image_file
        with patch('fotix.core.selection_strategy.is_image_file', return_value=True):
            # Mock para get_image_resolution
            with patch('fotix.core.selection_strategy.get_image_resolution') as mock_get_resolution:
                # Configurar resoluções diferentes
                mock_get_resolution.side_effect = lambda path: (
                    (800, 600) if path == file1.path else
                    (1920, 1080) if path == file2.path else  # Maior resolução
                    (1280, 720)
                )
                
                # Act
                result = strategy.select_file_to_keep(duplicate_set)
        
        # Assert
        assert result == file2

    def test_select_with_non_image_files(self):
        """Testa o comportamento quando não há arquivos de imagem."""
        # Arrange
        mock_fs_service = MagicMock()
        fallback_strategy = ModificationDateStrategy()
        strategy = HighestResolutionStrategy(
            file_system_service=mock_fs_service,
            fallback_strategy=fallback_strategy
        )
        
        # Criar arquivos que não são imagens
        file1 = FileInfo(path=Path("doc1.txt"), size=100, modification_time=1600000000)
        file2 = FileInfo(path=Path("doc2.txt"), size=100, modification_time=1600001000)  # Mais recente
        
        duplicate_set = DuplicateSet(files=[file1, file2], hash="abc123")
        
        # Mock para is_image_file
        with patch('fotix.core.selection_strategy.is_image_file', return_value=False):
            # Act
            result = strategy.select_file_to_keep(duplicate_set)
        
        # Assert
        assert result == file2  # Deve usar a estratégia de fallback (ModificationDateStrategy)

    def test_select_with_zip_image_files(self):
        """Testa o comportamento com imagens dentro de arquivos ZIP."""
        # Arrange
        mock_fs_service = MagicMock()
        strategy = HighestResolutionStrategy(file_system_service=mock_fs_service)
        
        # Criar função de conteúdo simulada
        def content_provider():
            yield b'fake_image_data'
        
        # Criar arquivos de imagem, um em ZIP
        file1 = FileInfo(path=Path("image1.jpg"), size=100)
        file2 = FileInfo(
            path=Path("archive.zip:image2.jpg"),
            size=100,
            in_zip=True,
            zip_path=Path("archive.zip"),
            internal_path="image2.jpg",
            content_provider=content_provider
        )
        
        duplicate_set = DuplicateSet(files=[file1, file2], hash="abc123")
        
        # Mock para is_image_file
        with patch('fotix.core.selection_strategy.is_image_file', return_value=True):
            # Mock para get_image_resolution
            with patch('fotix.core.selection_strategy.get_image_resolution') as mock_get_resolution:
                mock_get_resolution.return_value = (800, 600)
                
                # Mock para get_image_resolution_from_bytes
                with patch('fotix.core.selection_strategy.get_image_resolution_from_bytes') as mock_get_resolution_bytes:
                    mock_get_resolution_bytes.return_value = (1920, 1080)  # Maior resolução
                    
                    # Act
                    result = strategy.select_file_to_keep(duplicate_set)
        
        # Assert
        assert result == file2


class TestShortestNameStrategy:
    """Testes para a estratégia ShortestNameStrategy."""

    def test_select_shortest_name(self):
        """Testa se a estratégia seleciona o arquivo com o nome mais curto."""
        # Arrange
        strategy = ShortestNameStrategy()
        
        # Criar arquivos com nomes de diferentes comprimentos
        file1 = FileInfo(path=Path("file1.txt"), size=100)
        file2 = FileInfo(path=Path("f2.txt"), size=100)  # Nome mais curto
        file3 = FileInfo(path=Path("file_with_long_name.txt"), size=100)
        
        duplicate_set = DuplicateSet(files=[file1, file2, file3], hash="abc123")
        
        # Act
        result = strategy.select_file_to_keep(duplicate_set)
        
        # Assert
        assert result == file2


class TestCompositeStrategy:
    """Testes para a estratégia CompositeStrategy."""

    def test_empty_strategies_list(self):
        """Testa se a inicialização falha com uma lista vazia de estratégias."""
        # Act & Assert
        with pytest.raises(ValueError, match="A lista de estratégias não pode estar vazia"):
            CompositeStrategy([])

    def test_apply_multiple_strategies(self):
        """Testa se a estratégia composta aplica várias estratégias em sequência."""
        # Arrange
        # Criar estratégias mock
        strategy1 = MagicMock()
        strategy1.name = "Strategy1"
        strategy1._select_file.return_value = FileInfo(path=Path("file1.txt"), size=100)
        
        strategy2 = MagicMock()
        strategy2.name = "Strategy2"
        
        composite = CompositeStrategy([strategy1, strategy2])
        
        # Criar conjunto de duplicatas
        file1 = FileInfo(path=Path("file1.txt"), size=100)
        file2 = FileInfo(path=Path("file2.txt"), size=100)
        duplicate_set = DuplicateSet(files=[file1, file2], hash="abc123")
        
        # Act
        result = composite._select_file(duplicate_set)
        
        # Assert
        strategy1._select_file.assert_called_once()
        strategy2._select_file.assert_not_called()  # Não deve ser chamada porque strategy1 já reduziu para um arquivo
        assert result == file1


class TestCreateStrategy:
    """Testes para a função create_strategy."""

    def test_create_creation_date_strategy(self):
        """Testa a criação de uma estratégia CreationDateStrategy."""
        # Act
        strategy = create_strategy('creation_date')
        
        # Assert
        assert isinstance(strategy, CreationDateStrategy)

    def test_create_modification_date_strategy(self):
        """Testa a criação de uma estratégia ModificationDateStrategy."""
        # Act
        strategy = create_strategy('modification_date')
        
        # Assert
        assert isinstance(strategy, ModificationDateStrategy)

    def test_create_highest_resolution_strategy(self):
        """Testa a criação de uma estratégia HighestResolutionStrategy."""
        # Act
        strategy = create_strategy('highest_resolution')
        
        # Assert
        assert isinstance(strategy, HighestResolutionStrategy)
        assert isinstance(strategy.fallback_strategy, ModificationDateStrategy)

    def test_create_shortest_name_strategy(self):
        """Testa a criação de uma estratégia ShortestNameStrategy."""
        # Act
        strategy = create_strategy('shortest_name')
        
        # Assert
        assert isinstance(strategy, ShortestNameStrategy)

    def test_create_composite_strategy(self):
        """Testa a criação de uma estratégia CompositeStrategy."""
        # Act
        strategy = create_strategy('composite')
        
        # Assert
        assert isinstance(strategy, CompositeStrategy)
        assert len(strategy.strategies) == 3
        assert isinstance(strategy.strategies[0], HighestResolutionStrategy)
        assert isinstance(strategy.strategies[1], ModificationDateStrategy)
        assert isinstance(strategy.strategies[2], ShortestNameStrategy)

    def test_create_unknown_strategy(self):
        """Testa se a função levanta ValueError para um tipo desconhecido."""
        # Act & Assert
        with pytest.raises(ValueError, match="Tipo de estratégia desconhecido"):
            create_strategy('unknown_strategy')
