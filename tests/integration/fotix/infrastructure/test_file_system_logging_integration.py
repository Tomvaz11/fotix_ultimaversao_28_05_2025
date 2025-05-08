"""
Testes de integração entre os módulos de sistema de arquivos e logging do Fotix.

Este módulo testa a integração entre fotix.infrastructure.file_system e
fotix.infrastructure.logging_config, verificando se as operações do sistema de arquivos
são logadas corretamente.
"""

import os
import sys
import logging
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from send2trash import TrashPermissionError

# Importa os módulos a serem testados
from fotix.config import get, set
from fotix.infrastructure.file_system import FileSystemService
from fotix.infrastructure.logging_config import configure_logging, get_logger


class TestFileSystemLoggingIntegration:
    """Testes de integração entre sistema de arquivos e logging."""

    @pytest.fixture
    def fs_service(self):
        """Fixture que retorna uma instância de FileSystemService."""
        return FileSystemService()

    def test_file_operations_are_logged(self, fs_service, test_files, temp_log_file, reset_logging, caplog):
        """
        Testa se as operações do sistema de arquivos são logadas.

        Este teste verifica se as operações básicas do FileSystemService
        geram entradas de log apropriadas.
        """
        # Configura o logging para usar o arquivo temporário e capturar logs
        configure_logging(log_level="DEBUG", log_file=temp_log_file)
        caplog.set_level(logging.DEBUG)

        # Realiza operações do sistema de arquivos
        root_dir = test_files["root"]
        test_file = test_files["files"][0]

        # Obtém tamanho do arquivo
        size = fs_service.get_file_size(test_file)
        assert size is not None

        # Lista conteúdo do diretório
        files = list(fs_service.list_directory_contents(root_dir, recursive=True))
        # Pode haver mais arquivos do que esperamos (como o arquivo de log)
        # Verificamos apenas se todos os arquivos de teste estão na lista
        for test_file in test_files["files"]:
            assert test_file in files

        # Cria um novo diretório
        new_dir = root_dir / "new_test_dir"
        fs_service.create_directory(new_dir)
        assert new_dir.exists()

        # Copia um arquivo
        copy_dest = root_dir / "copy_test.txt"
        fs_service.copy_file(test_file, copy_dest)
        assert copy_dest.exists()

        # Verifica se as operações foram logadas usando caplog
        log_text = caplog.text.lower()  # Converte para minúsculas para facilitar a comparação
        assert "tamanho do arquivo" in log_text
        assert "listando conteúdo do diretório" in log_text
        assert "criando diretório" in log_text
        assert "copiando arquivo" in log_text

    def test_trash_operations_are_logged(self, fs_service, test_files, temp_log_file, reset_logging, caplog):
        """
        Testa se as operações de lixeira são logadas.

        Este teste verifica se as operações de movimentação para a lixeira
        geram entradas de log apropriadas.
        """
        # Configura o logging para usar o arquivo temporário e capturar logs
        configure_logging(log_level="INFO", log_file=temp_log_file)
        caplog.set_level(logging.INFO)

        # Cria um arquivo temporário para mover para a lixeira
        test_file = test_files["files"][0]
        trash_test = test_files["root"] / "trash_test.txt"
        fs_service.copy_file(test_file, trash_test)

        # Limpa os logs capturados até agora
        caplog.clear()

        # Patch send2trash para evitar realmente mover para a lixeira
        with patch('fotix.infrastructure.file_system.send2trash') as mock_send2trash:
            # Move o arquivo para a lixeira
            fs_service.move_to_trash(trash_test)

            # Verifica se send2trash foi chamado
            mock_send2trash.assert_called_once_with(str(trash_test))

            # Verifica se a operação foi logada usando caplog
            assert "Movendo para a lixeira" in caplog.text

    def test_trash_disabled_is_logged(self, fs_service, test_files, temp_log_file, reset_logging, caplog):
        """
        Testa se a remoção permanente (trash_enabled=False) é logada.

        Este teste verifica se a remoção permanente de arquivos (quando a lixeira
        está desabilitada) gera entradas de log apropriadas.
        """
        # Configura o logging para usar o arquivo temporário e capturar logs
        configure_logging(log_level="INFO", log_file=temp_log_file)
        caplog.set_level(logging.WARNING)  # WARNING para capturar avisos

        # Cria um arquivo temporário para remover
        test_file = test_files["files"][0]
        remove_test = test_files["root"] / "remove_test.txt"
        fs_service.copy_file(test_file, remove_test)

        # Limpa os logs capturados até agora
        caplog.clear()

        # Patch get_config para desabilitar a lixeira
        with patch('fotix.infrastructure.file_system.get_config', return_value=False):
            # Remove o arquivo permanentemente
            fs_service.move_to_trash(remove_test)

            # Verifica se o arquivo foi removido
            assert not remove_test.exists()

            # Verifica se a operação foi logada com aviso usando caplog
            assert "Removendo permanentemente (trash_enabled=False)" in caplog.text

    def test_error_handling_and_logging(self, fs_service, test_files, temp_log_file, reset_logging, caplog):
        """
        Testa o tratamento de erros e logging de exceções.

        Este teste verifica se as exceções são tratadas corretamente e
        se os erros são logados apropriadamente.
        """
        # Configura o logging para usar o arquivo temporário e capturar logs
        configure_logging(log_level="ERROR", log_file=temp_log_file)
        caplog.set_level(logging.ERROR)

        # Cria um arquivo inexistente com um caminho que certamente não existe
        nonexistent_file = test_files["root"] / "definitivamente_nao_existe.txt"

        # Limpa os logs capturados até agora
        caplog.clear()

        # Tenta mover para a lixeira um arquivo inexistente
        # Isso deve gerar um erro que será logado
        try:
            fs_service.move_to_trash(nonexistent_file)
            pytest.fail("Deveria ter levantado FileNotFoundError")
        except FileNotFoundError:
            # Esperado
            pass

        # Verifica se os erros foram logados usando caplog
        log_text = caplog.text.lower()  # Converte para minúsculas para facilitar a comparação
        assert "erro" in log_text or "error" in log_text
        assert "não encontrado" in log_text or "não existe" in log_text

    def test_permission_error_logging(self, fs_service, test_files, temp_log_file, reset_logging, caplog):
        """
        Testa o logging de erros de permissão.

        Este teste verifica se os erros de permissão são logados corretamente.
        """
        # Configura o logging para usar o arquivo temporário e capturar logs
        configure_logging(log_level="ERROR", log_file=temp_log_file)
        caplog.set_level(logging.ERROR)

        # Cria um arquivo temporário para testar
        test_file = test_files["files"][0]

        # Limpa os logs capturados até agora
        caplog.clear()

        # Patch send2trash para simular um erro de permissão
        with patch('fotix.infrastructure.file_system.send2trash',
                  side_effect=TrashPermissionError("Permissão negada")):
            # Tenta mover para a lixeira
            with pytest.raises(TrashPermissionError):
                fs_service.move_to_trash(test_file)

            # Verifica se o erro foi logado usando caplog
            assert "Erro de permissão ao mover para a lixeira" in caplog.text
