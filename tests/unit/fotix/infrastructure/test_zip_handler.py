"""
Testes unitários para o módulo de manipulação de arquivos ZIP.

Este módulo contém testes para a classe ZipHandlerService, que implementa
a interface IZipHandlerService para acessar o conteúdo de arquivos ZIP.
"""

import os
import tempfile
import zipfile
from pathlib import Path
from unittest import mock

import pytest
from stream_unzip import NotStreamUnzippable, UnzipError

from fotix.infrastructure.zip_handler import ZipHandlerService


class TestZipHandlerService:
    """Testes para a classe ZipHandlerService."""

    @pytest.fixture
    def zip_service(self):
        """Fixture que retorna uma instância de ZipHandlerService."""
        return ZipHandlerService()

    @pytest.fixture
    def temp_dir(self):
        """Fixture que cria um diretório temporário para testes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def test_zip_file(self, temp_dir):
        """
        Fixture que cria um arquivo ZIP temporário com alguns arquivos dentro.

        O ZIP contém:
        - test.txt: Um arquivo de texto simples
        - image.jpg: Um arquivo simulando uma imagem
        - document.pdf: Um arquivo simulando um PDF
        - subdir/nested.txt: Um arquivo em um subdiretório

        Returns:
            Path: Caminho para o arquivo ZIP criado.
        """
        zip_path = temp_dir / "test.zip"

        # Criar arquivos temporários para adicionar ao ZIP
        files_to_add = [
            ("test.txt", b"Este e um arquivo de teste"),
            ("image.jpg", b"Conteudo simulando uma imagem JPEG"),
            ("document.pdf", b"Conteudo simulando um arquivo PDF"),
            ("subdir/nested.txt", b"Arquivo em um subdiretorio")
        ]

        # Criar o arquivo ZIP
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            for file_name, content in files_to_add:
                # Garantir que o diretório exista para arquivos em subdiretórios
                if '/' in file_name:
                    dir_name = os.path.dirname(file_name)
                    if not os.path.exists(temp_dir / dir_name):
                        os.makedirs(temp_dir / dir_name)

                # Criar o arquivo temporário
                temp_file = temp_dir / file_name
                os.makedirs(os.path.dirname(temp_file), exist_ok=True)
                with open(temp_file, 'wb') as f:
                    f.write(content)

                # Adicionar ao ZIP
                zip_file.write(temp_file, file_name)

        return zip_path

    def test_stream_zip_entries_nonexistent_file(self, zip_service):
        """Testa stream_zip_entries com um arquivo inexistente."""
        # Arrange
        nonexistent_path = Path("/caminho/inexistente/arquivo.zip")

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            list(zip_service.stream_zip_entries(nonexistent_path))

    def test_stream_zip_entries_not_a_file(self, zip_service, temp_dir):
        """Testa stream_zip_entries com um caminho que não é um arquivo."""
        # Act & Assert
        with pytest.raises(ValueError):
            list(zip_service.stream_zip_entries(temp_dir))

    def test_stream_zip_entries_all_files(self, zip_service, test_zip_file):
        """Testa stream_zip_entries para listar todos os arquivos em um ZIP."""
        # Arrange
        expected_files = ["test.txt", "image.jpg", "document.pdf", "subdir/nested.txt"]

        # Act - Consumir o iterador completamente e fechar o arquivo
        entries = []
        for file_name, file_size, content_fn in zip_service.stream_zip_entries(test_zip_file):
            # Consumir o conteúdo para garantir que o arquivo seja processado completamente
            content = list(content_fn())
            entries.append((file_name, file_size, content))

        # Assert
        assert len(entries) == 4

        # Verificar se todos os arquivos esperados estão presentes
        file_names = [entry[0] for entry in entries]
        for expected_file in expected_files:
            assert expected_file in file_names

        # Verificar se os tamanhos são corretos
        for file_name, file_size, _ in entries:
            if file_name == "test.txt":
                assert file_size == len(b"Este e um arquivo de teste")
            elif file_name == "image.jpg":
                assert file_size == len(b"Conteudo simulando uma imagem JPEG")
            elif file_name == "document.pdf":
                assert file_size == len(b"Conteudo simulando um arquivo PDF")
            elif file_name == "subdir/nested.txt":
                assert file_size == len(b"Arquivo em um subdiretorio")

    def test_stream_zip_entries_with_extension_filter(self, zip_service, test_zip_file):
        """Testa stream_zip_entries com filtro de extensão."""
        # Act - Consumir o iterador completamente e fechar o arquivo
        entries = []
        for file_name, file_size, content_fn in zip_service.stream_zip_entries(test_zip_file, file_extensions=['.jpg', '.pdf']):
            # Consumir o conteúdo para garantir que o arquivo seja processado completamente
            content = list(content_fn())
            entries.append((file_name, file_size, content))

        # Assert
        assert len(entries) == 2

        # Verificar se apenas os arquivos com as extensões especificadas estão presentes
        file_names = [entry[0] for entry in entries]
        assert "image.jpg" in file_names
        assert "document.pdf" in file_names
        assert "test.txt" not in file_names
        assert "subdir/nested.txt" not in file_names

    def test_stream_zip_entries_with_extension_filter_case_insensitive(self, zip_service, test_zip_file):
        """Testa stream_zip_entries com filtro de extensão case-insensitive."""
        # Act - Consumir o iterador completamente e fechar o arquivo
        entries = []
        for file_name, file_size, content_fn in zip_service.stream_zip_entries(test_zip_file, file_extensions=['.JPG', '.PDF']):
            # Consumir o conteúdo para garantir que o arquivo seja processado completamente
            content = list(content_fn())
            entries.append((file_name, file_size, content))

        # Assert
        assert len(entries) == 2

        # Verificar se apenas os arquivos com as extensões especificadas estão presentes
        file_names = [entry[0] for entry in entries]
        assert "image.jpg" in file_names
        assert "document.pdf" in file_names

    def test_stream_zip_entries_with_extension_filter_without_dot(self, zip_service, test_zip_file):
        """Testa stream_zip_entries com filtro de extensão sem ponto."""
        # Act - Consumir o iterador completamente e fechar o arquivo
        entries = []
        for file_name, file_size, content_fn in zip_service.stream_zip_entries(test_zip_file, file_extensions=['jpg', 'pdf']):
            # Consumir o conteúdo para garantir que o arquivo seja processado completamente
            content = list(content_fn())
            entries.append((file_name, file_size, content))

        # Assert
        assert len(entries) == 2

        # Verificar se apenas os arquivos com as extensões especificadas estão presentes
        file_names = [entry[0] for entry in entries]
        assert "image.jpg" in file_names
        assert "document.pdf" in file_names

    def test_stream_zip_content(self, zip_service, test_zip_file):
        """Testa se o conteúdo dos arquivos no ZIP pode ser acessado corretamente."""
        # Arrange
        expected_content = {
            "test.txt": b"Este e um arquivo de teste",
            "image.jpg": b"Conteudo simulando uma imagem JPEG",
            "document.pdf": b"Conteudo simulando um arquivo PDF",
            "subdir/nested.txt": b"Arquivo em um subdiretorio"
        }

        # Act - Consumir o iterador completamente e fechar o arquivo
        entries = []
        for file_name, _, content_fn in zip_service.stream_zip_entries(test_zip_file):
            # Obter o conteúdo do arquivo
            content_chunks = list(content_fn())
            content = b''.join(content_chunks)
            entries.append((file_name, content))

        # Assert
        for file_name, content in entries:
            assert content == expected_content[file_name]

    @mock.patch('fotix.infrastructure.zip_handler.stream_unzip')
    def test_not_stream_unzippable_error(self, mock_stream_unzip, zip_service, test_zip_file):
        """Testa o comportamento quando o arquivo ZIP não pode ser processado em streaming."""
        # Arrange
        mock_stream_unzip.side_effect = NotStreamUnzippable("Arquivo não pode ser processado em streaming")

        # Act & Assert
        with pytest.raises(NotStreamUnzippable):
            list(zip_service.stream_zip_entries(test_zip_file))

    @mock.patch('fotix.infrastructure.zip_handler.stream_unzip')
    def test_unzip_error(self, mock_stream_unzip, zip_service, test_zip_file):
        """Testa o comportamento quando ocorre um erro genérico de descompressão."""
        # Arrange
        mock_stream_unzip.side_effect = UnzipError("Erro genérico de descompressão")

        # Act & Assert
        with pytest.raises(ValueError):
            list(zip_service.stream_zip_entries(test_zip_file))

    @mock.patch('fotix.infrastructure.zip_handler.stream_unzip')
    def test_permission_error(self, mock_stream_unzip, zip_service, test_zip_file):
        """Testa o comportamento quando ocorre um erro de permissão."""
        # Arrange
        mock_stream_unzip.side_effect = PermissionError("Sem permissão para ler o arquivo")

        # Act & Assert
        with pytest.raises(PermissionError):
            list(zip_service.stream_zip_entries(test_zip_file))

    @mock.patch('fotix.infrastructure.zip_handler.stream_unzip')
    def test_unexpected_error(self, mock_stream_unzip, zip_service, test_zip_file):
        """Testa o comportamento quando ocorre um erro inesperado."""
        # Arrange
        mock_stream_unzip.side_effect = Exception("Erro inesperado")

        # Act & Assert
        with pytest.raises(Exception):
            list(zip_service.stream_zip_entries(test_zip_file))
