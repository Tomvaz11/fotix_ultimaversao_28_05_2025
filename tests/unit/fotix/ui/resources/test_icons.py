"""
Testes unitários para o módulo de ícones.

Este módulo contém testes para verificar o funcionamento correto do módulo
de ícones da aplicação Fotix.
"""

import sys
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from PySide6.QtWidgets import QApplication, QStyle
from PySide6.QtGui import QIcon

from fotix.ui.resources.icons import get_icon, get_standard_icon, _icon_cache


# Fixture para a aplicação Qt
@pytest.fixture
def app():
    """Fixture que cria uma instância da aplicação Qt."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


# Fixture para limpar o cache de ícones
@pytest.fixture
def clear_icon_cache():
    """Fixture que limpa o cache de ícones."""
    _icon_cache.clear()
    yield
    _icon_cache.clear()


class TestIcons:
    """Testes para o módulo de ícones."""

    @patch('fotix.ui.resources.icons.Path.exists')
    @patch('fotix.ui.resources.icons.QIcon')
    def test_get_icon_from_file(self, mock_qicon, mock_exists, app, clear_icon_cache):
        """Testa a obtenção de um ícone a partir de um arquivo."""
        # Configurar mocks
        mock_exists.return_value = True
        mock_icon = MagicMock()
        mock_qicon.return_value = mock_icon

        # Chamar método
        icon = get_icon("test")

        # Verificar que o ícone foi criado a partir do arquivo
        mock_qicon.assert_called_once()
        assert icon == mock_icon

        # Verificar que o ícone foi armazenado em cache
        assert "test" in _icon_cache
        assert _icon_cache["test"] == mock_icon

    @patch('fotix.ui.resources.icons.Path.exists')
    @patch('fotix.ui.resources.icons.QIcon.fromTheme')
    def test_get_icon_from_theme(self, mock_from_theme, mock_exists, app, clear_icon_cache):
        """Testa a obtenção de um ícone a partir do tema."""
        # Configurar mocks
        mock_exists.return_value = False
        mock_icon = MagicMock()
        mock_from_theme.return_value = mock_icon

        # Chamar método
        icon = get_icon("test")

        # Verificar que o ícone foi criado a partir do tema
        mock_from_theme.assert_called_once_with("test")
        assert icon == mock_icon

        # Verificar que o ícone foi armazenado em cache
        assert "test" in _icon_cache
        assert _icon_cache["test"] == mock_icon

    def test_get_icon_from_cache(self, app, clear_icon_cache):
        """Testa a obtenção de um ícone a partir do cache."""
        # Adicionar ícone ao cache
        mock_icon = MagicMock()
        _icon_cache["test"] = mock_icon

        # Chamar método
        icon = get_icon("test")

        # Verificar que o ícone foi obtido do cache
        assert icon == mock_icon

    @patch('fotix.ui.resources.icons.QApplication.instance')
    def test_get_standard_icon(self, mock_instance, app):
        """Testa a obtenção de um ícone padrão."""
        # Configurar mock
        mock_app = MagicMock()
        mock_style = MagicMock()
        mock_icon = MagicMock()

        mock_instance.return_value = mock_app
        mock_app.style.return_value = mock_style
        mock_style.standardIcon.return_value = mock_icon

        # Chamar método
        icon = get_standard_icon(QStyle.SP_DirIcon)

        # Verificar que o ícone foi criado
        mock_style.standardIcon.assert_called_once_with(QStyle.SP_DirIcon)
        assert icon == mock_icon
