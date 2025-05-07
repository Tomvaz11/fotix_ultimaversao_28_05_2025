"""
Testes unitários para o módulo fotix.infrastructure.zip_handler.

Este módulo contém testes para a implementação do serviço de manipulação de arquivos ZIP,
incluindo casos normais, casos de erro e casos de borda.
"""

import io
import os
import tempfile
import zipfile
from pathlib import Path
from unittest import mock

import pytest
from stream_unzip import UnfinishedIterationError

from fotix.infrastructure.zip_handler import ZipHandlerService


class TestZipHandlerService:
    """Testes para a classe ZipHandlerService."""

    @pytest.fixture
    def zip_service(self):
        """Fixture que retorna uma instância de ZipHandlerService."""
        return ZipHandlerService()

    @pytest.fixture
    def temp_dir(self):
        """Fixture que cria um diretório temporário para os testes."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        # Limpar após os testes
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def temp_zip_file(self, temp_dir):
        """Fixture que cria um arquivo ZIP temporário com alguns arquivos dentro."""
        zip_path = temp_dir / "test.zip"

        # Criar arquivos para adicionar ao ZIP
        files_data = {
            "file1.txt": b"Conteudo do arquivo 1",
            "file2.txt": b"Conteudo do arquivo 2",
            "image.jpg": b"Dados binarios simulados de uma imagem",
            "document.pdf": b"Dados binarios simulados de um PDF",
            "subdir/file3.txt": b"Arquivo em subdiretorio"
        }

        # Criar o arquivo ZIP
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            for file_name, content in files_data.items():
                # Garantir que os diretórios existam
                if '/' in file_name:
                    dir_name = file_name.rsplit('/', 1)[0]
                    try:
                        zip_file.getinfo(f"{dir_name}/")
                    except KeyError:
                        zip_file.writestr(f"{dir_name}/", b"")

                zip_file.writestr(file_name, content)

        return zip_path

    # Testes para stream_zip_entries

    def test_stream_zip_entries_all_files(self, zip_service, temp_zip_file):
        """Testa stream_zip_entries para obter todos os arquivos do ZIP."""
        # Act
        entries = list(zip_service.stream_zip_entries(temp_zip_file))

        # Assert
        # Verificar se temos o número correto de arquivos (excluindo diretórios vazios)
        assert len(entries) == 5  # 5 arquivos no ZIP (excluindo o diretório vazio 'subdir/')

        # Verificar se todos os arquivos esperados estão presentes
        file_names = [entry[0] for entry in entries]
        assert "file1.txt" in file_names
        assert "file2.txt" in file_names
        assert "image.jpg" in file_names
        assert "document.pdf" in file_names
        assert "subdir/file3.txt" in file_names

        # Verificar se os tamanhos são corretos
        for file_name, file_size, _ in entries:
            if file_name == "file1.txt":
                assert file_size == len(b"Conteudo do arquivo 1")
            elif file_name == "image.jpg":
                assert file_size == len(b"Dados binarios simulados de uma imagem")

        # Verificar se o conteúdo pode ser lido corretamente
        for file_name, _, content_fn in entries:
            content = b"".join(content_fn())
            if file_name == "file1.txt":
                assert content == b"Conteudo do arquivo 1"
            elif file_name == "image.jpg":
                assert content == b"Dados binarios simulados de uma imagem"

    def test_stream_zip_entries_with_extension_filter(self, zip_service, temp_zip_file):
        """Testa stream_zip_entries com filtro de extensão."""
        # Act
        entries = list(zip_service.stream_zip_entries(temp_zip_file, file_extensions=[".txt"]))

        # Assert
        assert len(entries) == 3  # 3 arquivos .txt no ZIP

        # Verificar se apenas os arquivos .txt estão presentes
        file_names = [entry[0] for entry in entries]
        assert "file1.txt" in file_names
        assert "file2.txt" in file_names
        assert "subdir/file3.txt" in file_names
        assert "image.jpg" not in file_names
        assert "document.pdf" not in file_names

    def test_stream_zip_entries_nonexistent_file(self, zip_service, temp_dir):
        """Testa stream_zip_entries com um arquivo ZIP inexistente."""
        # Arrange
        nonexistent_zip = temp_dir / "nonexistent.zip"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            list(zip_service.stream_zip_entries(nonexistent_zip))

    def test_stream_zip_entries_permission_error(self, zip_service, temp_zip_file):
        """Testa stream_zip_entries com erro de permissão."""
        # Arrange
        with mock.patch('builtins.open', side_effect=PermissionError("Permissão negada")):
            # Act & Assert
            with pytest.raises(PermissionError):
                list(zip_service.stream_zip_entries(temp_zip_file))

    def test_stream_zip_entries_invalid_zip(self, zip_service, temp_dir):
        """Testa stream_zip_entries com um arquivo que não é um ZIP válido."""
        # Arrange
        invalid_zip = temp_dir / "invalid.zip"
        with open(invalid_zip, 'wb') as f:
            f.write(b"Este nao e um arquivo ZIP valido")

        # Act & Assert
        with pytest.raises(Exception):  # Pode ser zipfile.BadZipFile ou outra exceção da stream_unzip
            list(zip_service.stream_zip_entries(invalid_zip))

    def test_stream_zip_entries_empty_zip(self, zip_service, temp_dir):
        """Testa stream_zip_entries com um arquivo ZIP vazio."""
        # Arrange
        empty_zip = temp_dir / "empty.zip"
        with zipfile.ZipFile(empty_zip, 'w'):
            pass  # Criar um ZIP vazio

        # Act
        entries = list(zip_service.stream_zip_entries(empty_zip))

        # Assert
        assert len(entries) == 0

    def test_stream_zip_entries_with_mock_stream_unzip(self, zip_service, temp_zip_file):
        """Testa stream_zip_entries usando um mock para stream_unzip."""
        # Arrange
        mock_entries = [
            ("mock_file1.txt", 100, lambda: [b"Conteudo mockado 1"]),
            ("mock_file2.jpg", 200, lambda: [b"Conteudo mockado 2"])
        ]

        with mock.patch('fotix.infrastructure.zip_handler.stream_unzip', return_value=mock_entries):
            # Act
            entries = list(zip_service.stream_zip_entries(temp_zip_file))

            # Assert
            assert len(entries) == 2
            assert entries[0][0] == "mock_file1.txt"
            assert entries[0][1] == 100
            assert b"".join(entries[0][2]()) == b"Conteudo mockado 1"
            assert entries[1][0] == "mock_file2.jpg"
            assert entries[1][1] == 200
            assert b"".join(entries[1][2]()) == b"Conteudo mockado 2"

    def test_stream_zip_entries_filter_consumes_unwanted_entries(self, zip_service, temp_zip_file):
        """Testa se stream_zip_entries consome corretamente os iteradores de entradas filtradas."""
        # Arrange
        # Criar um mock para o iterador de chunks que verifica se foi consumido
        consumed = {"image.jpg": False, "document.pdf": False}

        def mock_unzipped_chunks_fn(file_name):
            def chunks_generator():
                yield b"Conteudo de teste"
                consumed[file_name] = True
            return chunks_generator

        mock_entries = [
            ("file1.txt", 100, lambda: [b"Conteudo de teste"]),
            ("image.jpg", 200, lambda: mock_unzipped_chunks_fn("image.jpg")()),
            ("document.pdf", 300, lambda: mock_unzipped_chunks_fn("document.pdf")())
        ]

        with mock.patch('fotix.infrastructure.zip_handler.stream_unzip', return_value=mock_entries):
            # Act
            entries = list(zip_service.stream_zip_entries(temp_zip_file, file_extensions=[".txt"]))

            # Assert
            assert len(entries) == 1
            assert entries[0][0] == "file1.txt"
            # Verificar se os iteradores de entradas filtradas foram consumidos
            assert consumed["image.jpg"] is True
            assert consumed["document.pdf"] is True
