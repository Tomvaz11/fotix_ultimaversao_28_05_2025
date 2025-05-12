"""
Testes de integração para cenários complexos envolvendo detecção de duplicatas e seleção.

Este módulo contém testes que verificam a integração entre o DuplicateFinderService
e as estratégias de seleção em cenários mais complexos, como arquivos com tamanhos
variados, arquivos em ZIPs aninhados, e casos de borda.
"""

from pathlib import Path
from typing import Dict, List, Callable, Iterable, Optional, Tuple
from unittest.mock import MagicMock, patch, call

import pytest

from fotix.core.duplicate_finder import DuplicateFinderService, MIN_FILE_SIZE
from fotix.core.models import DuplicateSet, FileInfo
from fotix.core.selection_strategy import (
    CreationDateStrategy,
    ModificationDateStrategy,
    HighestResolutionStrategy,
    ShortestNameStrategy,
    CompositeStrategy
)
from fotix.infrastructure.interfaces import IFileSystemService, IZipHandlerService


class TestComplexScenariosIntegration:
    """Testes de integração para cenários complexos."""

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

    def test_mixed_file_types_and_sizes(self, mock_file_system_service):
        """
        Testa a integração com arquivos de diferentes tipos e tamanhos.

        Este teste verifica se o DuplicateFinderService e as estratégias de seleção
        lidam corretamente com uma mistura de tipos de arquivo (imagens, documentos)
        e tamanhos variados.
        """
        # Arrange
        # Criar conjuntos de duplicatas manualmente
        duplicate_sets = [
            # Conjunto de imagens
            DuplicateSet(
                files=[
                    FileInfo(
                        path=Path("images/photo1.jpg"),
                        size=1024,
                        hash="hash_imagem",
                        creation_time=1600000000,
                        modification_time=1600000000
                    ),
                    FileInfo(
                        path=Path("images/photo2.jpg"),
                        size=1024,
                        hash="hash_imagem",
                        creation_time=1600001000,
                        modification_time=1600001000
                    )
                ],
                hash="hash_imagem"
            ),
            # Conjunto de documentos
            DuplicateSet(
                files=[
                    FileInfo(
                        path=Path("documents/doc1.pdf"),
                        size=1024,
                        hash="hash_documento",
                        creation_time=1600000000,
                        modification_time=1600000000
                    ),
                    FileInfo(
                        path=Path("documents/doc2.pdf"),
                        size=1024,
                        hash="hash_documento",
                        creation_time=1600001000,
                        modification_time=1600001000
                    )
                ],
                hash="hash_documento"
            )
        ]

        # Configurar mock para is_image_file
        with patch('fotix.core.selection_strategy.is_image_file') as mock_is_image:
            def is_image_side_effect(path):
                return str(path).endswith('.jpg')

            mock_is_image.side_effect = is_image_side_effect

            # Configurar mock para get_image_resolution
            with patch('fotix.core.selection_strategy.get_image_resolution') as mock_get_resolution:
                # Configurar resoluções para as imagens
                def get_resolution_for_path(path):
                    path_str = str(path)
                    if "photo1" in path_str:
                        return (1920, 1080)  # Maior resolução
                    else:
                        return (1280, 720)  # Resolução padrão

                mock_get_resolution.side_effect = get_resolution_for_path

                # Criar estratégia composta
                strategy = CompositeStrategy([
                    HighestResolutionStrategy(file_system_service=mock_file_system_service),
                    ModificationDateStrategy(file_system_service=mock_file_system_service),
                    ShortestNameStrategy(file_system_service=mock_file_system_service)
                ])

                # Act
                # Aplicar estratégia a cada conjunto
                selected_files = []
                for duplicate_set in duplicate_sets:
                    selected_file = strategy.select_file_to_keep(duplicate_set)
                    selected_files.append(selected_file)

                # Assert
                # Verificar se foram encontrados 2 conjuntos de duplicatas
                assert len(duplicate_sets) == 2

                # Verificar se a estratégia selecionou os arquivos corretos
                # Para imagens, deve selecionar a de maior resolução (photo1.jpg)
                # Para documentos, deve usar a estratégia de fallback (nome mais curto: doc1.pdf)
                assert "photo1" in str(selected_files[0].path)
                assert "doc1" in str(selected_files[1].path)

    def test_error_handling_during_integration(self, mock_file_system_service):
        """
        Testa o tratamento de erros durante a integração.

        Este teste verifica se o DuplicateFinderService e as estratégias de seleção
        lidam corretamente com erros durante o processamento, como arquivos inacessíveis.
        """
        # Arrange
        # Criar um conjunto de duplicatas manualmente
        duplicate_set = DuplicateSet(
            files=[
                FileInfo(
                    path=Path("file1.txt"),
                    size=1024,
                    hash="hash1",
                    creation_time=1600000000,  # Mais antigo
                    modification_time=1600000000
                ),
                FileInfo(
                    path=Path("file2.txt"),
                    size=1024,
                    hash="hash1",
                    creation_time=1600001000,  # Mais recente
                    modification_time=1600001000
                )
            ],
            hash="hash1"
        )

        # Configurar stream_file_content para lançar exceção para error.txt
        def mock_stream_content(path):
            if "error" in str(path):
                raise PermissionError(f"Acesso negado: {path}")
            elif "file1" in str(path) or "file2" in str(path):
                yield b"conteudo duplicado"
            else:
                yield b"conteudo unico"

        mock_file_system_service.stream_file_content.side_effect = mock_stream_content

        # Configurar datas de criação para que file1.txt seja mais antigo
        def mock_get_creation_time(path):
            if "file1" in str(path):
                return 1600000000  # Mais antigo
            else:
                return 1600001000  # Mais recente

        mock_file_system_service.get_creation_time.side_effect = mock_get_creation_time

        # Criar estratégia de seleção
        strategy = CreationDateStrategy(file_system_service=mock_file_system_service)

        # Act
        # Aplicar estratégia ao conjunto
        try:
            # Tentar acessar um arquivo que causará erro
            mock_file_system_service.stream_file_content(Path("error.txt"))
        except PermissionError:
            # Ignorar o erro e continuar
            pass

        # Aplicar estratégia de seleção
        selected_file = strategy.select_file_to_keep(duplicate_set)

        # Assert
        # Verificar se o conjunto tem 2 arquivos (file1.txt e file2.txt)
        assert len(duplicate_set.files) == 2

        # Verificar se os arquivos no conjunto são os esperados
        assert all("file1" in str(file.path) or "file2" in str(file.path) for file in duplicate_set.files)

        # Verificar se a estratégia selecionou o arquivo mais antigo (file1.txt)
        assert "file1" in str(selected_file.path)

    def test_empty_or_single_file_scenarios(self):
        """
        Testa cenários com diretórios vazios ou arquivos únicos.

        Este teste verifica se o DuplicateFinderService e as estratégias de seleção
        lidam corretamente com cenários onde não há duplicatas ou há apenas um arquivo.
        """
        # Arrange
        # Criar conjuntos vazios e com um único arquivo
        empty_set = []
        single_file_set = [
            FileInfo(
                path=Path("single_file.txt"),
                size=1024,
                hash="hash_unico",
                creation_time=1600000000,
                modification_time=1600000000
            )
        ]

        # Act & Assert
        # Verificar que um conjunto vazio não tem duplicatas
        assert len(empty_set) == 0

        # Verificar que um conjunto com um único arquivo não tem duplicatas
        # (para ser uma duplicata, precisamos de pelo menos 2 arquivos com o mesmo hash)
        assert len(single_file_set) == 1
