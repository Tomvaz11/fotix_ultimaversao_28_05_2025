"""
Testes unitários para a classe DuplicateFinder.

Este módulo contém testes para verificar o comportamento da classe DuplicateFinder
em diferentes cenários, incluindo casos de sucesso e casos de erro.
"""

import logging
from pathlib import Path
from typing import Iterator, List
from unittest.mock import Mock, patch

import pytest

from fotix.core.duplicate_finder import DuplicateFinder
from fotix.domain import FileMetadata, DuplicateGroup


class TestDuplicateFinder:
    """Testes para a classe DuplicateFinder."""

    def setup_method(self):
        """Configuração executada antes de cada teste."""
        self.finder = DuplicateFinder()

        # Cria alguns objetos FileMetadata para usar nos testes
        self.file1 = FileMetadata(
            path=Path("/path/to/file1.jpg"),
            size=1000,
            creation_time=1600000000.0
        )
        self.file2 = FileMetadata(
            path=Path("/path/to/file2.jpg"),
            size=1000,
            creation_time=1600001000.0
        )
        self.file3 = FileMetadata(
            path=Path("/path/to/file3.jpg"),
            size=1000,
            creation_time=1600002000.0
        )
        self.file4 = FileMetadata(
            path=Path("/path/to/file4.jpg"),
            size=2000,
            creation_time=1600003000.0
        )
        self.file5 = FileMetadata(
            path=Path("/path/to/file5.jpg"),
            size=2000,
            creation_time=1600004000.0
        )
        self.file6 = FileMetadata(
            path=Path("/path/to/file6.jpg"),
            size=3000,
            creation_time=1600005000.0
        )
        self.file7 = FileMetadata(
            path=Path("/path/to/empty1.txt"),
            size=0,
            creation_time=1600006000.0
        )
        self.file8 = FileMetadata(
            path=Path("/path/to/empty2.txt"),
            size=0,
            creation_time=1600007000.0
        )

    def test_empty_iterator(self):
        """Testa o comportamento com um iterador vazio."""
        # Cria um iterador vazio
        file_iterator = iter([])
        hash_function = Mock()

        # Executa o método find_duplicates
        result = self.finder.find_duplicates(file_iterator, hash_function)

        # Verifica se o resultado é uma lista vazia
        assert result == []
        # Verifica se a hash_function não foi chamada
        hash_function.assert_not_called()

    def test_no_duplicates_by_size(self):
        """Testa o comportamento quando não há arquivos com o mesmo tamanho."""
        # Cria um iterador com arquivos de tamanhos diferentes
        file_iterator = iter([self.file1, self.file4, self.file6])
        hash_function = Mock()

        # Executa o método find_duplicates
        result = self.finder.find_duplicates(file_iterator, hash_function)

        # Verifica se o resultado é uma lista vazia
        assert result == []
        # Verifica se a hash_function não foi chamada
        hash_function.assert_not_called()

    def test_duplicates_by_size_but_different_hash(self):
        """Testa o comportamento quando há arquivos com o mesmo tamanho, mas hashes diferentes."""
        # Cria um iterador com arquivos do mesmo tamanho
        file_iterator = iter([self.file1, self.file2, self.file3])

        # Configura a hash_function para retornar hashes diferentes
        hash_function = Mock(side_effect=["hash1", "hash2", "hash3"])

        # Executa o método find_duplicates
        result = self.finder.find_duplicates(file_iterator, hash_function)

        # Verifica se o resultado é uma lista vazia
        assert result == []
        # Verifica se a hash_function foi chamada para cada arquivo
        assert hash_function.call_count == 3

    def test_one_duplicate_group(self):
        """Testa o comportamento quando há um grupo de arquivos duplicados."""
        # Cria um iterador com alguns arquivos duplicados
        file_iterator = iter([self.file1, self.file2, self.file3, self.file4, self.file6])

        # Configura a hash_function para retornar o mesmo hash para os 3 primeiros arquivos
        def mock_hash(file_meta: FileMetadata) -> str:
            if file_meta.size == 1000:
                return "same_hash"
            return f"hash_{file_meta.size}"

        hash_function = Mock(side_effect=mock_hash)

        # Executa o método find_duplicates
        result = self.finder.find_duplicates(file_iterator, hash_function)

        # Verifica se o resultado contém um grupo de duplicatas
        assert len(result) == 1
        assert isinstance(result[0], DuplicateGroup)
        assert result[0].hash_value == "same_hash"
        assert len(result[0].files) == 3
        assert self.file1 in result[0].files
        assert self.file2 in result[0].files
        assert self.file3 in result[0].files
        assert result[0].file_to_keep is None

        # Verifica se a hash_function foi chamada para os arquivos com tamanho 1000
        # (a implementação otimiza e não chama a função para arquivos sem duplicatas por tamanho)
        assert hash_function.call_count == 3

    def test_multiple_duplicate_groups(self):
        """Testa o comportamento quando há múltiplos grupos de arquivos duplicados."""
        # Cria um iterador com múltiplos grupos de duplicatas
        file_iterator = iter([
            self.file1, self.file2, self.file3,  # Grupo 1 (tamanho 1000)
            self.file4, self.file5,              # Grupo 2 (tamanho 2000)
            self.file6,                          # Sem duplicatas
            self.file7, self.file8               # Grupo 3 (tamanho 0)
        ])

        # Configura a hash_function para retornar hashes apropriados
        def mock_hash(file_meta: FileMetadata) -> str:
            if file_meta.size == 1000:
                return "hash_1000"
            elif file_meta.size == 2000:
                return "hash_2000"
            elif file_meta.size == 0:
                return "hash_0"
            return f"hash_{file_meta.size}"

        hash_function = Mock(side_effect=mock_hash)

        # Executa o método find_duplicates
        result = self.finder.find_duplicates(file_iterator, hash_function)

        # Verifica se o resultado contém três grupos de duplicatas
        assert len(result) == 3

        # Verifica o primeiro grupo (tamanho 1000)
        group_1000 = next(g for g in result if g.hash_value == "hash_1000")
        assert len(group_1000.files) == 3
        assert self.file1 in group_1000.files
        assert self.file2 in group_1000.files
        assert self.file3 in group_1000.files

        # Verifica o segundo grupo (tamanho 2000)
        group_2000 = next(g for g in result if g.hash_value == "hash_2000")
        assert len(group_2000.files) == 2
        assert self.file4 in group_2000.files
        assert self.file5 in group_2000.files

        # Verifica o terceiro grupo (tamanho 0)
        group_0 = next(g for g in result if g.hash_value == "hash_0")
        assert len(group_0.files) == 2
        assert self.file7 in group_0.files
        assert self.file8 in group_0.files

        # Verifica se a hash_function foi chamada para os arquivos em grupos com duplicatas por tamanho
        # (a implementação otimiza e não chama a função para arquivos sem duplicatas por tamanho)
        assert hash_function.call_count == 7

    def test_hash_function_error(self):
        """Testa o comportamento quando a hash_function levanta uma exceção."""
        # Cria um iterador com arquivos do mesmo tamanho
        file_iterator = iter([self.file1, self.file2, self.file3])

        # Configura a hash_function para levantar uma exceção para o segundo arquivo
        def mock_hash_with_error(file_meta: FileMetadata) -> str:
            if file_meta.path == self.file2.path:
                raise OSError("Erro ao ler o arquivo")
            return "hash_value"

        hash_function = Mock(side_effect=mock_hash_with_error)

        # Captura os logs para verificar se o aviso foi registrado
        with patch.object(logging, 'warning') as mock_warning:
            # Executa o método find_duplicates
            result = self.finder.find_duplicates(file_iterator, hash_function)

            # Verifica se o aviso foi registrado
            mock_warning.assert_called_once()
            assert "Falha ao calcular hash para o arquivo" in mock_warning.call_args[0][0]
            assert "Erro ao ler o arquivo" in mock_warning.call_args[0][0]

        # Verifica se o resultado contém um grupo de duplicatas com os arquivos 1 e 3
        assert len(result) == 1
        assert len(result[0].files) == 2
        assert self.file1 in result[0].files
        assert self.file3 in result[0].files
        assert self.file2 not in result[0].files

        # Verifica se a hash_function foi chamada para cada arquivo
        assert hash_function.call_count == 3

    def test_all_files_identical(self):
        """Testa o comportamento quando todos os arquivos são idênticos."""
        # Cria um iterador com vários arquivos do mesmo tamanho
        file_iterator = iter([self.file1, self.file2, self.file3])

        # Configura a hash_function para retornar o mesmo hash para todos os arquivos
        hash_function = Mock(return_value="same_hash_for_all")

        # Executa o método find_duplicates
        result = self.finder.find_duplicates(file_iterator, hash_function)

        # Verifica se o resultado contém um único grupo com todos os arquivos
        assert len(result) == 1
        assert len(result[0].files) == 3
        assert self.file1 in result[0].files
        assert self.file2 in result[0].files
        assert self.file3 in result[0].files
        assert result[0].hash_value == "same_hash_for_all"

        # Verifica se a hash_function foi chamada para cada arquivo
        assert hash_function.call_count == 3
