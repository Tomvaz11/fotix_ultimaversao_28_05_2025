"""
Testes unitários para o módulo de utilitários de imagem.

Este módulo contém testes para verificar o funcionamento correto das funções
de processamento de imagem definidas em fotix.utils.image_utils.
"""

import io
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

import pytest
from PIL import Image, UnidentifiedImageError

from fotix.utils.image_utils import (
    is_image_file,
    get_image_resolution,
    get_image_resolution_from_bytes,
    calculate_image_quality
)


class TestIsImageFile:
    """Testes para a função is_image_file."""

    @pytest.mark.parametrize("file_path,expected", [
        (Path("image.jpg"), True),
        (Path("image.jpeg"), True),
        (Path("image.png"), True),
        (Path("image.gif"), True),
        (Path("image.bmp"), True),
        (Path("image.tiff"), True),
        (Path("image.webp"), True),
        (Path("image.JPG"), True),  # Teste de case-insensitive
        (Path("document.pdf"), False),
        (Path("document.txt"), False),
        (Path("image"), False),
        (Path("image.unknown"), False),
    ])
    def test_is_image_file(self, file_path, expected):
        """Testa se a função identifica corretamente arquivos de imagem."""
        # Act
        result = is_image_file(file_path)
        
        # Assert
        assert result == expected


class TestGetImageResolution:
    """Testes para a função get_image_resolution."""

    def test_get_resolution_valid_image(self):
        """Testa se a função retorna a resolução correta para uma imagem válida."""
        # Arrange
        test_path = Path("test_image.jpg")
        mock_img = MagicMock()
        mock_img.size = (800, 600)
        
        # Act
        with patch("PIL.Image.open") as mock_open:
            mock_open.return_value.__enter__.return_value = mock_img
            resolution = get_image_resolution(test_path)
        
        # Assert
        assert resolution == (800, 600)
        mock_open.assert_called_once_with(test_path)

    def test_get_resolution_non_image_file(self):
        """Testa se a função retorna None para arquivos que não são imagens."""
        # Arrange
        test_path = Path("document.pdf")
        
        # Act
        resolution = get_image_resolution(test_path)
        
        # Assert
        assert resolution is None

    def test_get_resolution_file_not_found(self):
        """Testa se a função trata corretamente o caso de arquivo não encontrado."""
        # Arrange
        test_path = Path("nonexistent.jpg")
        
        # Act
        with patch("PIL.Image.open", side_effect=FileNotFoundError("File not found")):
            resolution = get_image_resolution(test_path)
        
        # Assert
        assert resolution is None

    def test_get_resolution_permission_error(self):
        """Testa se a função trata corretamente o caso de erro de permissão."""
        # Arrange
        test_path = Path("protected.jpg")
        
        # Act
        with patch("PIL.Image.open", side_effect=PermissionError("Permission denied")):
            resolution = get_image_resolution(test_path)
        
        # Assert
        assert resolution is None

    def test_get_resolution_unidentified_image(self):
        """Testa se a função trata corretamente o caso de imagem não identificada."""
        # Arrange
        test_path = Path("corrupt.jpg")
        
        # Act
        with patch("PIL.Image.open", side_effect=UnidentifiedImageError("Cannot identify image")):
            resolution = get_image_resolution(test_path)
        
        # Assert
        assert resolution is None

    def test_get_resolution_general_exception(self):
        """Testa se a função trata corretamente exceções genéricas."""
        # Arrange
        test_path = Path("problematic.jpg")
        
        # Act
        with patch("PIL.Image.open", side_effect=Exception("Unknown error")):
            resolution = get_image_resolution(test_path)
        
        # Assert
        assert resolution is None


class TestGetImageResolutionFromBytes:
    """Testes para a função get_image_resolution_from_bytes."""

    def test_get_resolution_from_bytes_valid_image(self):
        """Testa se a função retorna a resolução correta para bytes de imagem válidos."""
        # Arrange
        mock_img = MagicMock()
        mock_img.size = (1024, 768)
        
        # Criar um provedor de conteúdo simulado
        def content_provider():
            yield b'fake_image_data'
        
        # Act
        with patch("PIL.Image.open") as mock_open:
            mock_open.return_value.__enter__.return_value = mock_img
            resolution = get_image_resolution_from_bytes(content_provider)
        
        # Assert
        assert resolution == (1024, 768)

    def test_get_resolution_from_bytes_invalid_image(self):
        """Testa se a função retorna None para bytes que não representam uma imagem válida."""
        # Arrange
        def content_provider():
            yield b'not_an_image'
        
        # Act
        with patch("PIL.Image.open", side_effect=UnidentifiedImageError("Cannot identify image")):
            resolution = get_image_resolution_from_bytes(content_provider)
        
        # Assert
        assert resolution is None

    def test_get_resolution_from_bytes_exception(self):
        """Testa se a função trata corretamente exceções genéricas."""
        # Arrange
        def content_provider():
            yield b'problematic_data'
        
        # Act
        with patch("PIL.Image.open", side_effect=Exception("Unknown error")):
            resolution = get_image_resolution_from_bytes(content_provider)
        
        # Assert
        assert resolution is None


class TestCalculateImageQuality:
    """Testes para a função calculate_image_quality."""

    @pytest.mark.parametrize("resolution,expected", [
        ((800, 600), 480000),
        ((1920, 1080), 2073600),
        ((640, 480), 307200),
        ((0, 0), 0),
        ((1, 1), 1),
    ])
    def test_calculate_image_quality(self, resolution, expected):
        """Testa se a função calcula corretamente a qualidade da imagem."""
        # Act
        quality = calculate_image_quality(resolution)
        
        # Assert
        assert quality == expected
