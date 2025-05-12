"""
Testes unitários para o widget de informações de arquivo.

Este módulo contém testes para verificar o funcionamento correto do widget
de informações de arquivo da aplicação Fotix.
"""

import sys
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import QApplication

from fotix.ui.widgets.file_info_widget import FileInfoWidget
from fotix.core.models import FileInfo


# Fixture para a aplicação Qt
@pytest.fixture
def app():
    """Fixture que cria uma instância da aplicação Qt."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


# Fixture para o widget de informações de arquivo
@pytest.fixture
def file_info_widget(app):
    """Fixture que cria uma instância do widget de informações de arquivo."""
    widget = FileInfoWidget()
    yield widget
    widget.deleteLater()


# Fixture para criar um arquivo de teste
@pytest.fixture
def file_info():
    """Fixture que cria um arquivo de teste."""
    return FileInfo(
        path=Path("/test/file.jpg"),
        size=1024,
        hash="abc123",
        creation_time=1609459200.0,  # 2021-01-01
        modification_time=1609459200.0
    )


# Fixture para criar um arquivo em ZIP de teste
@pytest.fixture
def zip_file_info():
    """Fixture que cria um arquivo em ZIP de teste."""
    return FileInfo(
        path=Path("/test/archive.zip:file.jpg"),
        size=1024,
        hash="abc123",
        creation_time=1609459200.0,
        modification_time=1609459200.0,
        in_zip=True,
        zip_path=Path("/test/archive.zip"),
        internal_path="file.jpg",
        content_provider=lambda: [b"test content"]
    )


class TestFileInfoWidget:
    """Testes para o widget de informações de arquivo."""

    def test_init(self, file_info_widget):
        """Testa a inicialização do widget."""
        # Verificar se o widget foi criado corretamente
        assert file_info_widget._title_label is not None
        assert file_info_widget._name_label is not None
        assert file_info_widget._path_label is not None
        assert file_info_widget._size_label is not None
        assert file_info_widget._hash_label is not None
        assert file_info_widget._creation_time_label is not None
        assert file_info_widget._modification_time_label is not None
        assert file_info_widget._in_zip_label is not None
        assert file_info_widget._zip_path_label is not None
        assert file_info_widget._resolution_label is not None

    def test_clear(self, file_info_widget):
        """Testa a limpeza das informações."""
        # Chamar método
        file_info_widget.clear()

        # Verificar que os campos foram limpos
        assert file_info_widget._name_label.text() == "N/A"
        assert file_info_widget._path_label.text() == "N/A"
        assert file_info_widget._size_label.text() == "N/A"
        assert file_info_widget._hash_label.text() == "N/A"
        assert file_info_widget._creation_time_label.text() == "N/A"
        assert file_info_widget._modification_time_label.text() == "N/A"
        assert file_info_widget._in_zip_label.text() == "N/A"
        assert file_info_widget._zip_path_label.text() == "N/A"
        assert file_info_widget._resolution_label.text() == "N/A"

    def test_format_size(self, file_info_widget):
        """Testa a formatação de tamanho em bytes."""
        # Testar diferentes tamanhos
        assert file_info_widget._format_size(500) == "500 B"
        assert file_info_widget._format_size(1500) == "1.5 KB"
        assert file_info_widget._format_size(1500000) == "1.4 MB"
        assert file_info_widget._format_size(1500000000) == "1.4 GB"

    def test_set_file_info_normal(self, file_info_widget, file_info):
        """Testa a definição de informações para um arquivo normal."""
        # Configurar mock para get_image_resolution
        with patch('fotix.ui.widgets.file_info_widget.get_image_resolution') as mock_get_resolution:
            mock_get_resolution.return_value = (800, 600)

            # Chamar método
            file_info_widget.set_file_info(file_info)

            # Verificar que os campos foram preenchidos corretamente
            assert file_info_widget._name_label.text() == "file.jpg"
            # No Windows, os caminhos usam barras invertidas
            assert file_info_widget._path_label.text() == str(file_info.path)
            assert file_info_widget._size_label.text() == "1.0 KB"
            assert file_info_widget._hash_label.text() == "abc123"
            # Não verificamos a data exata, pois pode variar com o fuso horário
            assert file_info_widget._creation_time_label.text() != "N/A"
            assert file_info_widget._modification_time_label.text() != "N/A"
            assert file_info_widget._in_zip_label.text() == "Não"
            assert file_info_widget._zip_path_label.text() == "N/A"
            assert file_info_widget._resolution_label.text() == "800 x 600"

            # Verificar que get_image_resolution foi chamado
            mock_get_resolution.assert_called_once_with(file_info.path)

    def test_set_file_info_zip(self, file_info_widget, zip_file_info):
        """Testa a definição de informações para um arquivo em ZIP."""
        # Configurar mock para get_image_resolution_from_bytes
        with patch('fotix.ui.widgets.file_info_widget.get_image_resolution_from_bytes') as mock_get_resolution:
            mock_get_resolution.return_value = (800, 600)

            # Chamar método
            file_info_widget.set_file_info(zip_file_info)

            # Verificar que os campos foram preenchidos corretamente
            # O nome pode incluir o caminho do ZIP
            assert "file.jpg" in file_info_widget._name_label.text()
            # No Windows, os caminhos usam barras invertidas
            assert file_info_widget._path_label.text() == str(zip_file_info.path)
            assert file_info_widget._size_label.text() == "1.0 KB"
            assert file_info_widget._hash_label.text() == "abc123"
            # Não verificamos a data exata, pois pode variar com o fuso horário
            assert file_info_widget._creation_time_label.text() != "N/A"
            assert file_info_widget._modification_time_label.text() != "N/A"
            assert file_info_widget._in_zip_label.text() == "Sim"
            # No Windows, os caminhos usam barras invertidas
            assert str(zip_file_info.zip_path) in file_info_widget._zip_path_label.text()
            assert "-> file.jpg" in file_info_widget._zip_path_label.text()
            assert file_info_widget._resolution_label.text() == "800 x 600"

            # Verificar que get_image_resolution_from_bytes foi chamado
            mock_get_resolution.assert_called_once_with(zip_file_info.content_provider)

    def test_set_file_info_no_hash(self, file_info_widget, file_info):
        """Testa a definição de informações para um arquivo sem hash."""
        # Modificar arquivo para remover hash
        file_info.hash = None

        # Configurar mock para get_image_resolution
        with patch('fotix.ui.widgets.file_info_widget.get_image_resolution') as mock_get_resolution:
            mock_get_resolution.return_value = None

            # Chamar método
            file_info_widget.set_file_info(file_info)

            # Verificar que os campos foram preenchidos corretamente
            assert file_info_widget._hash_label.text() == "N/A"
            assert file_info_widget._resolution_label.text() == "N/A"

    def test_set_file_info_no_dates(self, file_info_widget, file_info):
        """Testa a definição de informações para um arquivo sem datas."""
        # Modificar arquivo para remover datas
        file_info.creation_time = None
        file_info.modification_time = None

        # Chamar método
        file_info_widget.set_file_info(file_info)

        # Verificar que os campos foram preenchidos corretamente
        assert file_info_widget._creation_time_label.text() == "N/A"
        assert file_info_widget._modification_time_label.text() == "N/A"

    @patch('fotix.ui.widgets.file_info_widget.Image.open')
    def test_get_image_resolution_from_bytes_success(self, mock_image_open):
        """Testa a obtenção da resolução de uma imagem a partir de bytes com sucesso."""
        from fotix.ui.widgets.file_info_widget import get_image_resolution_from_bytes

        # Configurar mock para Image.open
        mock_img = MagicMock()
        mock_img.size = (800, 600)
        mock_image_open.return_value.__enter__.return_value = mock_img

        # Criar função de provider de conteúdo
        content_provider = lambda: [b"test content"]

        # Chamar função
        resolution = get_image_resolution_from_bytes(content_provider)

        # Verificar resultado
        assert resolution == (800, 600)

        # Verificar que Image.open foi chamado
        mock_image_open.assert_called_once()

    @patch('fotix.ui.widgets.file_info_widget.Image.open')
    def test_get_image_resolution_from_bytes_empty_content(self, mock_image_open):
        """Testa a obtenção da resolução de uma imagem a partir de bytes vazios."""
        from fotix.ui.widgets.file_info_widget import get_image_resolution_from_bytes

        # Criar função de provider de conteúdo vazio
        content_provider = lambda: []

        # Chamar função
        resolution = get_image_resolution_from_bytes(content_provider)

        # Verificar resultado
        assert resolution is None

        # Verificar que Image.open não foi chamado
        mock_image_open.assert_not_called()

    @patch('fotix.ui.widgets.file_info_widget.Image.open')
    def test_get_image_resolution_from_bytes_exception(self, mock_image_open):
        """Testa a obtenção da resolução de uma imagem a partir de bytes com exceção."""
        from fotix.ui.widgets.file_info_widget import get_image_resolution_from_bytes

        # Configurar mock para Image.open para lançar exceção
        mock_image_open.side_effect = Exception("Erro de teste")

        # Criar função de provider de conteúdo
        content_provider = lambda: [b"test content"]

        # Chamar função
        resolution = get_image_resolution_from_bytes(content_provider)

        # Verificar resultado
        assert resolution is None

        # Verificar que Image.open foi chamado
        mock_image_open.assert_called_once()
