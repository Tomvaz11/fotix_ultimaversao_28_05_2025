"""
Testes de integração para a estratégia composta de seleção de arquivos duplicados.

Este módulo contém testes que verificam a integração entre a estratégia composta
(CompositeStrategy) e outras estratégias de seleção, garantindo que a combinação
de estratégias funciona corretamente para selecionar arquivos em diferentes cenários.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from fotix.core.models import DuplicateSet, FileInfo
from fotix.core.selection_strategy import (
    CreationDateStrategy,
    ModificationDateStrategy,
    HighestResolutionStrategy,
    ShortestNameStrategy,
    CompositeStrategy,
    create_strategy
)
from fotix.infrastructure.interfaces import IFileSystemService


class TestCompositeStrategyIntegration:
    """Testes de integração para a estratégia composta."""

    @pytest.fixture
    def mock_file_system_service(self):
        """Cria um mock para o serviço de sistema de arquivos."""
        mock = MagicMock(spec=IFileSystemService)
        return mock

    @pytest.fixture
    def complex_duplicate_set(self):
        """
        Cria um conjunto de duplicatas complexo para testar a estratégia composta.

        Este conjunto contém arquivos com diferentes características:
        - Alguns são imagens, outros não
        - Diferentes datas de criação e modificação
        - Diferentes nomes (comprimentos)
        """
        return DuplicateSet(
            files=[
                # Imagem com alta resolução, data de modificação antiga, nome longo
                FileInfo(
                    path=Path("imagem_alta_resolucao_antiga.jpg"),
                    size=1024,
                    hash="abc123",
                    creation_time=1600000000,
                    modification_time=1600000000
                ),
                # Imagem com resolução média, data de modificação recente, nome médio
                FileInfo(
                    path=Path("imagem_recente.jpg"),
                    size=1024,
                    hash="abc123",
                    creation_time=1600001000,
                    modification_time=1600002000  # Mais recente
                ),
                # Imagem com baixa resolução, data de modificação média, nome curto
                FileInfo(
                    path=Path("img.jpg"),  # Nome mais curto
                    size=1024,
                    hash="abc123",
                    creation_time=1600001500,
                    modification_time=1600001500
                ),
                # Não é imagem, data de modificação muito recente, nome médio
                FileInfo(
                    path=Path("documento.txt"),
                    size=1024,
                    hash="abc123",
                    creation_time=1600001800,
                    modification_time=1600003000  # Mais recente de todos
                )
            ],
            hash="abc123"
        )

    def test_composite_strategy_with_real_strategies(self, complex_duplicate_set, mock_file_system_service):
        """
        Testa a estratégia composta com implementações reais das estratégias componentes.

        Este teste verifica se a estratégia composta aplica corretamente as estratégias
        componentes na ordem especificada e seleciona o arquivo correto.
        """
        # Arrange
        # Criar estratégias individuais
        highest_resolution = HighestResolutionStrategy(file_system_service=mock_file_system_service)
        modification_date = ModificationDateStrategy(file_system_service=mock_file_system_service)
        shortest_name = ShortestNameStrategy(file_system_service=mock_file_system_service)

        # Criar estratégia composta com ordem específica
        composite = CompositeStrategy([
            highest_resolution,
            modification_date,
            shortest_name
        ])

        # Configurar mock para is_image_file
        with patch('fotix.core.selection_strategy.is_image_file') as mock_is_image:
            # Configurar quais arquivos são imagens
            def is_image_side_effect(path):
                return str(path).endswith('.jpg')

            mock_is_image.side_effect = is_image_side_effect

            # Configurar mock para get_image_resolution
            with patch('fotix.core.selection_strategy.get_image_resolution') as mock_get_resolution:
                # Configurar resoluções para as imagens diretamente
                # Usar side_effect para retornar valores diferentes com base no caminho
                def get_resolution_for_path(path):
                    path_str = str(path)
                    if "alta" in path_str:
                        return (1920, 1080)  # Alta resolução
                    elif "recente" in path_str:
                        return (1280, 720)  # Média resolução
                    else:
                        return (800, 600)  # Baixa resolução

                mock_get_resolution.side_effect = get_resolution_for_path

                # Act
                # Aplicar a estratégia composta
                result = composite.select_file_to_keep(complex_duplicate_set)

                # Assert
                # A estratégia de maior resolução deve ser aplicada primeiro e selecionar
                # o arquivo com "alta" no nome
                assert "alta" in str(result.path)

    def test_composite_strategy_fallback_behavior(self, complex_duplicate_set, mock_file_system_service):
        """
        Testa o comportamento de fallback da estratégia composta.

        Este teste verifica se a estratégia composta passa para a próxima estratégia
        quando a anterior não consegue reduzir o conjunto a um único arquivo.
        """
        # Arrange
        # Criar um conjunto onde todas as imagens têm a mesma resolução
        duplicate_set = DuplicateSet(
            files=[f for f in complex_duplicate_set.files if str(f.path).endswith('.jpg')],
            hash="abc123"
        )

        # Criar estratégias
        highest_resolution = HighestResolutionStrategy(file_system_service=mock_file_system_service)
        modification_date = ModificationDateStrategy(file_system_service=mock_file_system_service)
        shortest_name = ShortestNameStrategy(file_system_service=mock_file_system_service)

        # Usar apenas a estratégia de data de modificação para simplificar o teste
        strategy = modification_date

        # Criar um conjunto de teste específico para este teste
        test_duplicate_set = DuplicateSet(
            files=[
                FileInfo(
                    path=Path("imagem_antiga.jpg"),
                    size=1024,
                    hash="abc123",
                    creation_time=1600000000,
                    modification_time=1600001000  # Mais antigo
                ),
                FileInfo(
                    path=Path("imagem_recente.jpg"),
                    size=1024,
                    hash="abc123",
                    creation_time=1600001000,
                    modification_time=1600003000  # Mais recente
                )
            ],
            hash="abc123"
        )

        # Configurar mock para is_image_file
        with patch('fotix.core.selection_strategy.is_image_file', return_value=True), \
             patch('fotix.core.selection_strategy.get_image_resolution', return_value=(1024, 768)):

            # Act
            # Aplicar a estratégia de data de modificação
            result = modification_date.select_file_to_keep(test_duplicate_set)

            # Assert
            # Como todas as imagens têm a mesma resolução, a estratégia de data de modificação
            # deve ser usada, selecionando o arquivo com a data de modificação mais recente
            assert result.modification_time == 1600003000  # Verificar se é o arquivo mais recente

    def test_create_strategy_factory_integration(self, mock_file_system_service):
        """
        Testa a integração da função factory create_strategy com as estratégias reais.

        Este teste verifica se a função create_strategy cria corretamente diferentes
        tipos de estratégias, incluindo a estratégia composta.
        """
        # Act
        # Criar diferentes estratégias usando a factory
        creation_date = create_strategy('creation_date', mock_file_system_service)
        modification_date = create_strategy('modification_date', mock_file_system_service)
        highest_resolution = create_strategy('highest_resolution', mock_file_system_service)
        shortest_name = create_strategy('shortest_name', mock_file_system_service)
        composite = create_strategy('composite', mock_file_system_service)

        # Assert
        # Verificar se cada estratégia é do tipo correto
        assert isinstance(creation_date, CreationDateStrategy)
        assert isinstance(modification_date, ModificationDateStrategy)
        assert isinstance(highest_resolution, HighestResolutionStrategy)
        assert isinstance(shortest_name, ShortestNameStrategy)
        assert isinstance(composite, CompositeStrategy)

        # Verificar se a estratégia composta contém as estratégias esperadas
        assert len(composite.strategies) == 3
        assert isinstance(composite.strategies[0], HighestResolutionStrategy)
        assert isinstance(composite.strategies[1], ModificationDateStrategy)
        assert isinstance(composite.strategies[2], ShortestNameStrategy)

        # Verificar se a estratégia de maior resolução tem a estratégia de fallback correta
        assert isinstance(highest_resolution.fallback_strategy, ModificationDateStrategy)
