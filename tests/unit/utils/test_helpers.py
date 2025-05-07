"""
Testes unitários para o módulo fotix.utils.helpers.

Este módulo contém testes para as funções auxiliares genéricas do Fotix.
"""

import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from fotix.utils.helpers import filter_by_extensions, is_path_valid


class TestFilterByExtensions:
    """Testes para a função filter_by_extensions."""

    def test_filter_by_extensions_with_matching_extension(self):
        """Testa filter_by_extensions com uma extensão que corresponde."""
        # Arrange
        file_path = "imagem.jpg"
        extensions = [".jpg", ".png", ".gif"]
        
        # Act
        result = filter_by_extensions(file_path, extensions)
        
        # Assert
        assert result is True

    def test_filter_by_extensions_with_non_matching_extension(self):
        """Testa filter_by_extensions com uma extensão que não corresponde."""
        # Arrange
        file_path = "documento.pdf"
        extensions = [".jpg", ".png", ".gif"]
        
        # Act
        result = filter_by_extensions(file_path, extensions)
        
        # Assert
        assert result is False

    def test_filter_by_extensions_with_no_extension(self):
        """Testa filter_by_extensions com um arquivo sem extensão."""
        # Arrange
        file_path = "arquivo_sem_extensao"
        extensions = [".jpg", ".png", ".gif"]
        
        # Act
        result = filter_by_extensions(file_path, extensions)
        
        # Assert
        assert result is False

    def test_filter_by_extensions_with_none_extensions(self):
        """Testa filter_by_extensions com extensions=None."""
        # Arrange
        file_path = "qualquer_arquivo.txt"
        
        # Act
        result = filter_by_extensions(file_path, None)
        
        # Assert
        assert result is True

    def test_filter_by_extensions_case_insensitive(self):
        """Testa filter_by_extensions com correspondência case-insensitive."""
        # Arrange
        file_path = "imagem.JPG"
        extensions = [".jpg", ".png", ".gif"]
        
        # Act
        result = filter_by_extensions(file_path, extensions)
        
        # Assert
        assert result is True

    def test_filter_by_extensions_with_dot_in_filename(self):
        """Testa filter_by_extensions com um nome de arquivo que contém pontos."""
        # Arrange
        file_path = "arquivo.com.multiplos.pontos.txt"
        extensions = [".txt"]
        
        # Act
        result = filter_by_extensions(file_path, extensions)
        
        # Assert
        assert result is True

    def test_filter_by_extensions_with_extensions_without_dot(self):
        """Testa filter_by_extensions com extensões sem ponto."""
        # Arrange
        file_path = "imagem.jpg"
        extensions = ["jpg", "png", "gif"]  # Sem ponto
        
        # Act
        result = filter_by_extensions(file_path, extensions)
        
        # Assert
        assert result is True


class TestIsPathValid:
    """Testes para a função is_path_valid."""

    @pytest.fixture
    def temp_dir(self):
        """Fixture que cria um diretório temporário para os testes."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        # Limpar após os testes
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def temp_file(self, temp_dir):
        """Fixture que cria um arquivo temporário para os testes."""
        file_path = temp_dir / "test_file.txt"
        with open(file_path, "w") as f:
            f.write("Conteúdo de teste")
        return file_path

    def test_is_path_valid_with_valid_file(self, temp_file):
        """Testa is_path_valid com um arquivo válido."""
        # Act
        result = is_path_valid(temp_file)
        
        # Assert
        assert result is True

    def test_is_path_valid_with_valid_directory(self, temp_dir):
        """Testa is_path_valid com um diretório válido."""
        # Act
        result = is_path_valid(temp_dir)
        
        # Assert
        assert result is True

    def test_is_path_valid_with_nonexistent_path(self, temp_dir):
        """Testa is_path_valid com um caminho inexistente."""
        # Arrange
        nonexistent_path = temp_dir / "nonexistent.txt"
        
        # Act
        result = is_path_valid(nonexistent_path)
        
        # Assert
        assert result is False

    def test_is_path_valid_with_relative_path(self):
        """Testa is_path_valid com um caminho relativo."""
        # Arrange
        relative_path = Path("relative/path.txt")
        
        # Act
        result = is_path_valid(relative_path)
        
        # Assert
        assert result is False

    def test_is_path_valid_with_permission_error(self, temp_file):
        """Testa is_path_valid com erro de permissão."""
        # Arrange
        with mock.patch('os.access', return_value=False):
            # Act
            result = is_path_valid(temp_file)
            
            # Assert
            assert result is False

    def test_is_path_valid_with_os_error(self, temp_file):
        """Testa is_path_valid com erro de OS."""
        # Arrange
        with mock.patch('os.access', side_effect=OSError("Erro de OS")):
            # Act
            result = is_path_valid(temp_file)
            
            # Assert
            assert result is False

    def test_is_path_valid_with_value_error(self):
        """Testa is_path_valid com ValueError."""
        # Arrange
        with mock.patch.object(Path, 'exists', side_effect=ValueError("Erro de valor")):
            # Act
            result = is_path_valid(Path("/valid/path.txt"))
            
            # Assert
            assert result is False
