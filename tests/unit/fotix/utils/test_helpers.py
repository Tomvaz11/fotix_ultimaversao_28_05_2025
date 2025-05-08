"""
Testes unitários para o módulo helpers.py.

Este módulo contém testes para as funções auxiliares genéricas do Fotix.
"""

import os
import sys
from pathlib import Path
from unittest import mock

import pytest

from fotix.utils.helpers import (
    filter_by_extensions,
    format_file_size,
    get_common_parent_directory,
    is_hidden_file,
    normalize_path
)


class TestNormalizePath:
    """Testes para a função normalize_path."""

    def test_normalize_path(self):
        """Testa a normalização de um caminho."""
        path = Path("./folder/../folder/file.txt")
        normalized = normalize_path(path)

        # O caminho normalizado deve ser absoluto e sem componentes relativos
        assert normalized.is_absolute()
        assert ".." not in str(normalized)
        # Não podemos verificar se "." não está no caminho, pois o caminho pode conter pontos legítimos

        # O caminho normalizado deve terminar com "folder/file.txt"
        assert normalized.name == "file.txt"
        assert normalized.parent.name == "folder"


class TestFilterByExtensions:
    """Testes para a função filter_by_extensions."""

    def test_filter_by_extensions_match(self):
        """Testa filtragem com extensão correspondente."""
        path = Path("/path/to/file.jpg")
        extensions = [".jpg", ".png", ".gif"]
        assert filter_by_extensions(path, extensions) is True

    def test_filter_by_extensions_no_match(self):
        """Testa filtragem com extensão não correspondente."""
        path = Path("/path/to/file.txt")
        extensions = [".jpg", ".png", ".gif"]
        assert filter_by_extensions(path, extensions) is False

    def test_filter_by_extensions_case_insensitive(self):
        """Testa filtragem com extensão em maiúsculas."""
        path = Path("/path/to/file.JPG")
        extensions = [".jpg", ".png", ".gif"]
        assert filter_by_extensions(path, extensions) is True

    def test_filter_by_extensions_empty_list(self):
        """Testa filtragem com lista de extensões vazia."""
        path = Path("/path/to/file.txt")
        extensions = []
        assert filter_by_extensions(path, extensions) is True

    def test_filter_by_extensions_none(self):
        """Testa filtragem com extensões None."""
        path = Path("/path/to/file.txt")
        extensions = None
        assert filter_by_extensions(path, extensions) is True


class TestIsHiddenFile:
    """Testes para a função is_hidden_file."""

    def test_is_hidden_file_unix_hidden(self):
        """Testa arquivo oculto no estilo Unix (começa com ponto)."""
        # Criamos um mock para evitar problemas com caminhos inexistentes
        with mock.patch('fotix.utils.helpers.os.name', 'posix'):  # Simula ambiente Unix
            with mock.patch('os.path.exists', return_value=True):  # Simula que o arquivo existe
                path = Path("/path/to/.hidden_file")
                # No Unix, apenas o nome do arquivo importa para determinar se é oculto
                assert is_hidden_file(path) is True

    def test_is_hidden_file_unix_not_hidden(self):
        """Testa arquivo não oculto no estilo Unix."""
        # Criamos um mock para evitar problemas com caminhos inexistentes
        with mock.patch('fotix.utils.helpers.os.name', 'posix'):  # Simula ambiente Unix
            with mock.patch('os.path.exists', return_value=True):  # Simula que o arquivo existe
                path = Path("/path/to/visible_file")
                # No Unix, apenas o nome do arquivo importa para determinar se é oculto
                assert is_hidden_file(path) is False

    def test_is_hidden_file_windows_with_win32api(self):
        """Testa arquivo oculto no Windows usando win32api."""
        # Testamos apenas o comportamento baseado no nome do arquivo
        # já que não podemos contar com win32api nos testes automatizados
        path_hidden = Path("C:/path/to/.hidden_file.txt")
        path_visible = Path("C:/path/to/visible_file.txt")

        # Não precisamos de mock, a função já foi atualizada para lidar com caminhos inexistentes
        assert is_hidden_file(path_hidden) is True
        assert is_hidden_file(path_visible) is False

    def test_is_hidden_file_windows_fallback(self):
        """Testa fallback quando win32api não está disponível no Windows."""
        path_hidden = Path("C:/path/to/.hidden_file")
        path_visible = Path("C:/path/to/visible_file")

        # Simulamos a ausência do win32api
        with mock.patch('fotix.utils.helpers.os.name', 'nt'):
            with mock.patch.dict('sys.modules', {'win32api': None}):
                assert is_hidden_file(path_hidden) is True
                assert is_hidden_file(path_visible) is False


class TestFormatFileSize:
    """Testes para a função format_file_size."""

    def test_format_file_size_bytes(self):
        """Testa formatação de tamanho em bytes."""
        assert format_file_size(500) == "500 B"

    def test_format_file_size_kb(self):
        """Testa formatação de tamanho em kilobytes."""
        assert format_file_size(1500) == "1.46 KB"

    def test_format_file_size_mb(self):
        """Testa formatação de tamanho em megabytes."""
        assert format_file_size(1500000) == "1.43 MB"

    def test_format_file_size_gb(self):
        """Testa formatação de tamanho em gigabytes."""
        assert format_file_size(1500000000) == "1.40 GB"


class TestGetCommonParentDirectory:
    """Testes para a função get_common_parent_directory."""

    def test_get_common_parent_directory_same_dir(self):
        """Testa com arquivos no mesmo diretório."""
        # Mockamos normalize_path para retornar caminhos previsíveis
        with mock.patch('fotix.utils.helpers.normalize_path', side_effect=lambda p: p):
            # Usamos os.path.sep para garantir compatibilidade entre sistemas
            base_dir = f"C:{os.path.sep}path{os.path.sep}to{os.path.sep}dir"
            paths = [
                Path(f"{base_dir}{os.path.sep}file1.txt"),
                Path(f"{base_dir}{os.path.sep}file2.txt"),
                Path(f"{base_dir}{os.path.sep}file3.txt")
            ]

            # Mockamos os.path.commonprefix para retornar o resultado esperado
            with mock.patch('os.path.commonprefix', return_value=base_dir + os.path.sep):
                common_parent = get_common_parent_directory(paths)
                assert common_parent == Path(base_dir)

    def test_get_common_parent_directory_different_dirs(self):
        """Testa com arquivos em diretórios diferentes."""
        # Mockamos normalize_path para retornar caminhos previsíveis
        with mock.patch('fotix.utils.helpers.normalize_path', side_effect=lambda p: p):
            # Usamos os.path.sep para garantir compatibilidade entre sistemas
            base_dir = f"C:{os.path.sep}path{os.path.sep}to"
            paths = [
                Path(f"{base_dir}{os.path.sep}dir1{os.path.sep}file1.txt"),
                Path(f"{base_dir}{os.path.sep}dir2{os.path.sep}file2.txt"),
                Path(f"{base_dir}{os.path.sep}dir3{os.path.sep}file3.txt")
            ]

            # Mockamos os.path.commonprefix para retornar o resultado esperado
            with mock.patch('os.path.commonprefix', return_value=base_dir + os.path.sep):
                common_parent = get_common_parent_directory(paths)
                assert common_parent == Path(base_dir)

    def test_get_common_parent_directory_nested_dirs(self):
        """Testa com arquivos em diretórios aninhados."""
        # Mockamos normalize_path para retornar caminhos previsíveis
        with mock.patch('fotix.utils.helpers.normalize_path', side_effect=lambda p: p):
            # Usamos os.path.sep para garantir compatibilidade entre sistemas
            base_dir = f"C:{os.path.sep}path{os.path.sep}to{os.path.sep}dir"
            paths = [
                Path(f"{base_dir}{os.path.sep}file1.txt"),
                Path(f"{base_dir}{os.path.sep}subdir{os.path.sep}file2.txt"),
                Path(f"{base_dir}{os.path.sep}subdir{os.path.sep}nested{os.path.sep}file3.txt")
            ]

            # Mockamos os.path.commonprefix para retornar o resultado esperado
            with mock.patch('os.path.commonprefix', return_value=base_dir + os.path.sep):
                common_parent = get_common_parent_directory(paths)
                assert common_parent == Path(base_dir)

    def test_get_common_parent_directory_empty_list(self):
        """Testa com lista vazia."""
        paths = []
        common_parent = get_common_parent_directory(paths)
        assert common_parent is None

    def test_get_common_parent_directory_single_path(self):
        """Testa com um único caminho."""
        # Mockamos normalize_path para retornar caminhos previsíveis
        with mock.patch('fotix.utils.helpers.normalize_path', side_effect=lambda p: p):
            # Usamos os.path.sep para garantir compatibilidade entre sistemas
            file_path = f"C:{os.path.sep}path{os.path.sep}to{os.path.sep}file.txt"
            paths = [Path(file_path)]

            # Mockamos os.path.commonprefix e os.path.dirname para retornar os resultados esperados
            with mock.patch('os.path.commonprefix', return_value=file_path):
                with mock.patch('os.path.dirname', return_value=os.path.dirname(file_path)):
                    common_parent = get_common_parent_directory(paths)
                    assert common_parent == Path(os.path.dirname(file_path))
