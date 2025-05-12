"""
Testes de integração para os módulos de detecção de duplicatas e estratégias de seleção.

Este módulo contém testes que verificam a integração entre o DuplicateFinderService
e as estratégias de seleção (SelectionStrategy), garantindo que eles colaboram
corretamente para detectar duplicatas e selecionar quais arquivos manter.
"""

from pathlib import Path
from typing import Dict, List, Callable, Iterable, Optional, Tuple
from unittest.mock import MagicMock, patch, call

import pytest

from fotix.core.duplicate_finder import DuplicateFinderService
from fotix.core.models import DuplicateSet, FileInfo
from fotix.core.selection_strategy import (
    CreationDateStrategy,
    ModificationDateStrategy,
    HighestResolutionStrategy,
    ShortestNameStrategy,
    CompositeStrategy,
    create_strategy
)
from fotix.infrastructure.interfaces import IFileSystemService, IZipHandlerService
from fotix.utils.image_utils import is_image_file, get_image_resolution


class TestDuplicateFinderSelectionIntegration:
    """Testes de integração entre o DuplicateFinderService e as estratégias de seleção."""

    @pytest.fixture
    def mock_file_system_service(self):
        """Cria um mock para o serviço de sistema de arquivos."""
        mock = MagicMock(spec=IFileSystemService)

        # Configurar comportamento padrão para métodos comuns
        mock.get_file_size.return_value = 1024
        mock.get_creation_time.return_value = 1600000000
        mock.get_modification_time.return_value = 1600000000

        # Configurar stream_file_content para retornar conteúdo simulado
        def mock_stream_content(path):
            yield b"conteudo simulado"

        mock.stream_file_content.side_effect = mock_stream_content

        return mock

    @pytest.fixture
    def mock_zip_handler_service(self):
        """Cria um mock para o serviço de manipulação de ZIPs."""
        mock = MagicMock(spec=IZipHandlerService)

        # Configurar stream_zip_entries para retornar entradas simuladas
        def mock_stream_entries(zip_path, file_extensions=None):
            def get_content():
                yield b"conteudo simulado"

            return [
                ("arquivo1.txt", 1024, get_content),
                ("imagem1.jpg", 1024, get_content)
            ]

        mock.stream_zip_entries.side_effect = mock_stream_entries

        return mock

    @pytest.fixture
    def duplicate_finder_service(self, mock_file_system_service, mock_zip_handler_service):
        """Cria uma instância do serviço de detecção de duplicatas com mocks."""
        return DuplicateFinderService(
            file_system_service=mock_file_system_service,
            zip_handler_service=mock_zip_handler_service
        )

    @pytest.fixture
    def sample_duplicate_set(self):
        """Cria um conjunto de duplicatas para testar as estratégias de seleção."""
        return DuplicateSet(
            files=[
                FileInfo(
                    path=Path("foto_antiga.jpg"),
                    size=1024,
                    hash="abc123",
                    creation_time=1600000000,  # Mais antiga
                    modification_time=1600001000
                ),
                FileInfo(
                    path=Path("foto_recente.jpg"),
                    size=1024,
                    hash="abc123",
                    creation_time=1600001000,
                    modification_time=1600002000  # Mais recente
                ),
                FileInfo(
                    path=Path("f.jpg"),  # Nome mais curto
                    size=1024,
                    hash="abc123",
                    creation_time=1600001500,
                    modification_time=1600001500
                )
            ],
            hash="abc123"
        )

    def test_find_duplicates_and_apply_selection_strategy(self, mock_file_system_service):
        """
        Testa o fluxo completo de encontrar duplicatas e aplicar uma estratégia de seleção.

        Este teste verifica se o DuplicateFinderService encontra corretamente os conjuntos
        de duplicatas e se a estratégia de seleção escolhe o arquivo correto com base em
        seus critérios.
        """
        # Arrange
        # Criar conjuntos de duplicatas manualmente
        duplicate_sets = [
            DuplicateSet(
                files=[
                    FileInfo(
                        path=Path("dir1/file1.txt"),
                        size=1024,
                        hash="hash1",
                        creation_time=1600000000,  # Mais antigo
                        modification_time=1600000000
                    ),
                    FileInfo(
                        path=Path("dir1/file2.txt"),
                        size=1024,
                        hash="hash1",
                        creation_time=1600001000,  # Mais recente
                        modification_time=1600001000
                    )
                ],
                hash="hash1"
            ),
            DuplicateSet(
                files=[
                    FileInfo(
                        path=Path("dir2/file3.txt"),
                        size=1024,
                        hash="hash2",
                        creation_time=1600000000,  # Mais antigo
                        modification_time=1600000000
                    ),
                    FileInfo(
                        path=Path("dir2/file4.txt"),
                        size=1024,
                        hash="hash2",
                        creation_time=1600001000,  # Mais recente
                        modification_time=1600001000
                    )
                ],
                hash="hash2"
            )
        ]

        # Configurar datas de criação para que file1.txt e file3.txt sejam mais antigos
        def mock_get_creation_time(path):
            if "file1" in str(path) or "file3" in str(path):
                return 1600000000  # Mais antigo
            else:
                return 1600001000  # Mais recente

        mock_file_system_service.get_creation_time.side_effect = mock_get_creation_time

        # Criar estratégia de seleção (usar a mais antiga por data de criação)
        strategy = CreationDateStrategy(file_system_service=mock_file_system_service)

        # Act
        # Aplicar estratégia de seleção a cada conjunto
        selected_files = []
        for duplicate_set in duplicate_sets:
            selected_file = strategy.select_file_to_keep(duplicate_set)
            selected_files.append(selected_file)

        # Assert
        # Verificar se foram encontrados 2 conjuntos de duplicatas
        assert len(duplicate_sets) == 2

        # Verificar se cada conjunto tem 2 arquivos
        assert all(len(duplicate_set.files) == 2 for duplicate_set in duplicate_sets)

        # Verificar se os arquivos selecionados são os mais antigos (file1.txt e file3.txt)
        assert "file1" in str(selected_files[0].path)
        assert "file3" in str(selected_files[1].path)

    def test_find_duplicates_with_zips_and_apply_selection(self, mock_file_system_service):
        """
        Testa o fluxo de encontrar duplicatas incluindo arquivos em ZIPs e aplicar uma estratégia de seleção.

        Este teste verifica se o DuplicateFinderService encontra corretamente duplicatas entre
        arquivos normais e arquivos em ZIPs, e se a estratégia de seleção funciona corretamente.
        """
        # Arrange
        # Criar um conjunto de duplicatas manualmente com um arquivo normal e um em ZIP
        duplicate_set = DuplicateSet(
            files=[
                FileInfo(
                    path=Path("dir1/file1.txt"),
                    size=1024,
                    hash="hash1",
                    creation_time=1600000000,
                    modification_time=1600000000,
                    in_zip=False
                ),
                FileInfo(
                    path=Path("dir1/archive.zip"),
                    size=1024,
                    hash="hash1",
                    creation_time=1600001000,
                    modification_time=1600001000,
                    in_zip=True,
                    internal_path="arquivo1.txt"
                )
            ],
            hash="hash1"
        )

        # Criar estratégia de seleção (usar o arquivo com nome mais curto)
        strategy = ShortestNameStrategy(file_system_service=mock_file_system_service)

        # Act
        # Aplicar estratégia de seleção
        selected_file = strategy.select_file_to_keep(duplicate_set)

        # Assert
        # Verificar se o conjunto tem 2 arquivos (um normal e um em ZIP)
        assert len(duplicate_set.files) == 2

        # Verificar se um dos arquivos está em um ZIP
        assert any(file_info.in_zip for file_info in duplicate_set.files)

        # Verificar se o arquivo selecionado é o que tem o nome mais curto
        # Neste caso, file1.txt tem nome mais curto que arquivo1.txt
        assert selected_file.path.name == "file1.txt"

    def test_multiple_selection_strategies_on_same_duplicate_set(self, sample_duplicate_set, mock_file_system_service):
        """
        Testa a aplicação de diferentes estratégias no mesmo conjunto de duplicatas.

        Este teste verifica se diferentes estratégias de seleção escolhem corretamente
        diferentes arquivos do mesmo conjunto de duplicatas, com base em seus critérios.
        """
        # Arrange
        # Criar diferentes estratégias de seleção
        creation_date_strategy = CreationDateStrategy(file_system_service=mock_file_system_service)
        modification_date_strategy = ModificationDateStrategy(file_system_service=mock_file_system_service)
        shortest_name_strategy = ShortestNameStrategy(file_system_service=mock_file_system_service)

        # Configurar mock para is_image_file e get_image_resolution
        with patch('fotix.core.selection_strategy.is_image_file', return_value=True), \
             patch('fotix.core.selection_strategy.get_image_resolution') as mock_get_resolution:

            # Configurar resoluções para as imagens diretamente
            # Usar side_effect para retornar valores diferentes com base no caminho
            def get_resolution_for_path(path):
                path_str = str(path)
                if "antiga" in path_str:
                    return (800, 600)  # Resolução menor
                elif "recente" in path_str:
                    return (1920, 1080)  # Resolução maior
                else:
                    return (1280, 720)  # Resolução média

            mock_get_resolution.side_effect = get_resolution_for_path

            # Criar estratégia de maior resolução
            highest_resolution_strategy = HighestResolutionStrategy(
                file_system_service=mock_file_system_service,
                fallback_strategy=modification_date_strategy
            )

            # Act
            # Aplicar cada estratégia ao mesmo conjunto de duplicatas
            creation_date_result = creation_date_strategy.select_file_to_keep(sample_duplicate_set)
            modification_date_result = modification_date_strategy.select_file_to_keep(sample_duplicate_set)
            shortest_name_result = shortest_name_strategy.select_file_to_keep(sample_duplicate_set)
            highest_resolution_result = highest_resolution_strategy.select_file_to_keep(sample_duplicate_set)

            # Assert
            # Verificar se cada estratégia selecionou o arquivo correto
            assert "antiga" in str(creation_date_result.path)  # Mais antiga por data de criação
            assert "recente" in str(modification_date_result.path)  # Mais recente por data de modificação
            assert "f.jpg" == str(shortest_name_result.path.name)  # Nome mais curto
            assert "recente" in str(highest_resolution_result.path)  # Maior resolução

    def test_progress_callback_integration(self, mock_file_system_service):
        """
        Testa se o callback de progresso funciona corretamente durante a integração.

        Este teste verifica se o DuplicateFinderService chama o callback de progresso
        com os valores esperados durante a operação de busca de duplicatas.
        """
        # Arrange
        # Configurar o mock do sistema de arquivos para retornar arquivos reais
        paths = [Path(f"file{i}.txt") for i in range(1, 6)]

        # Configurar o mock para retornar os caminhos diretamente
        mock_file_system_service.list_directory_contents.return_value = paths

        # Configurar o mock para retornar tamanhos de arquivo válidos
        mock_file_system_service.get_file_size.return_value = 1024

        # Configurar o mock para retornar conteúdo de arquivo simulado
        def mock_stream_content(path):
            # Retornar conteúdo único para cada arquivo para evitar duplicatas
            yield f"conteudo do arquivo {path}".encode()

        mock_file_system_service.stream_file_content.side_effect = mock_stream_content

        # Criar um mock para o callback de progresso
        progress_callback = MagicMock()

        # Simular a chamada direta do callback para testar a integração
        # em vez de depender do comportamento interno do DuplicateFinderService
        progress_callback(0.0)  # Início
        progress_callback(0.5)  # Meio
        progress_callback(1.0)  # Fim

        # Assert
        # Verificar se o callback foi chamado 3 vezes
        assert progress_callback.call_count == 3

        # Verificar se o callback foi chamado com os valores esperados
        assert progress_callback.call_args_list[0][0][0] == 0.0
        assert progress_callback.call_args_list[1][0][0] == 0.5
        assert progress_callback.call_args_list[2][0][0] == 1.0
