"""
Testes de integração para o módulo principal (main) do Fotix.

Este módulo contém testes que verificam a integração entre o ponto de entrada da aplicação
(fotix.main) e os outros componentes do sistema, como a UI e os serviços de aplicação.

Cenários testados:
1. Inicialização da aplicação: Verifica se a aplicação é inicializada corretamente,
   incluindo a configuração de logging, a criação da janela principal e o início do
   loop de eventos.
2. Fluxo completo da aplicação: Simula o fluxo completo da aplicação, desde a
   inicialização até o encerramento.
"""

import sys
import tempfile
import json
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest
from PySide6.QtWidgets import QApplication

from fotix.main import main, setup_application
from fotix.ui.main_window import MainWindow
from fotix.config import get_config, update_config


@pytest.fixture
def temp_config_file():
    """
    Fixture que cria um arquivo de configuração temporário para testes.

    Returns:
        Path: Caminho para o arquivo de configuração temporário.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "fotix_test_config.json"

        # Criar configuração de teste
        test_config = {
            "backup_dir": str(Path(temp_dir) / "backups"),
            "log_level": "DEBUG",
            "log_file": str(Path(temp_dir) / "logs" / "fotix_test.log"),
            "max_workers": 2,
            "default_scan_dir": str(Path(temp_dir) / "scan"),
        }

        # Salvar configuração em arquivo
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(test_config, f, indent=4)

        yield config_path


@pytest.fixture
def setup_and_teardown_logging():
    """
    Fixture que configura o logging antes dos testes e restaura a configuração original depois.
    """
    # Salvar os handlers originais e o nível
    import logging
    original_handlers = logging.getLogger().handlers.copy()
    original_level = logging.getLogger().level

    yield

    # Restaurar os handlers originais e o nível
    root_logger = logging.getLogger()
    root_logger.setLevel(original_level)
    for handler in root_logger.handlers[:]:
        handler.close()  # Importante fechar os handlers para liberar arquivos
        root_logger.removeHandler(handler)
    for handler in original_handlers:
        root_logger.addHandler(handler)


class TestMainIntegration:
    """Testes de integração para o módulo principal (main) do Fotix."""

    def test_setup_application(self):
        """
        Testa a função setup_application.

        Verifica se a função setup_application cria e configura corretamente
        uma instância de QApplication.
        """
        # Garantir que não há instância de QApplication
        app = QApplication.instance()
        if app is not None:
            app.quit()
            app = None

        # Chamar a função setup_application
        app = setup_application()

        # Verificar se a instância foi criada
        assert app is not None
        assert isinstance(app, QApplication)

        # Verificar se as propriedades foram configuradas
        assert app.organizationName() == "Fotix"
        assert app.applicationName() == "Fotix - Gerenciador de Duplicatas"
        # O nome do estilo pode ser "Fusion" ou "fusion" dependendo da implementação
        assert app.style().objectName().lower() == "fusion"

        # Limpar
        app.quit()

    def test_main_initialization(self, temp_config_file, setup_and_teardown_logging):
        """
        Testa a inicialização da aplicação através da função main.

        Verifica se a função main configura corretamente o logging, cria a janela
        principal e inicia o loop de eventos.
        """
        # Configurar mocks
        with patch('fotix.main.get_config') as mock_get_config, \
             patch('fotix.main.get_log_level') as mock_get_log_level, \
             patch('fotix.main.setup_logging') as mock_setup_logging, \
             patch('fotix.main.setup_application') as mock_setup_application, \
             patch('fotix.main.MainWindow') as mock_main_window:

            # Configurar retornos dos mocks
            mock_get_log_level.return_value = "DEBUG"
            mock_get_config.return_value = {"key": "value"}

            mock_app = MagicMock()
            mock_app.exec.return_value = 0
            mock_setup_application.return_value = mock_app

            mock_window = MagicMock()
            mock_main_window.return_value = mock_window

            # Chamar a função main
            result = main()

            # Verificar se as funções foram chamadas na ordem correta
            assert mock_get_log_level.call_count == 1
            assert mock_setup_logging.call_count == 1
            assert mock_get_config.call_count == 1
            assert mock_setup_application.call_count == 1
            assert mock_main_window.call_count == 1

            # Verificar se a janela principal foi exibida
            assert mock_window.show.call_count == 1

            # Verificar se o loop de eventos foi iniciado
            assert mock_app.exec.call_count == 1

            # Verificar o código de saída
            assert result == 0

    def test_main_full_flow(self, temp_config_file, setup_and_teardown_logging):
        """
        Testa o fluxo completo da aplicação.

        Simula o fluxo completo da aplicação, desde a inicialização até o encerramento,
        incluindo a interação com a UI e os serviços de aplicação.
        """
        # Configurar mocks para os serviços
        with patch('fotix.ui.main_window.ScanService') as mock_scan_service, \
             patch('fotix.ui.main_window.DuplicateManagementService') as mock_duplicate_mgmt_service, \
             patch('fotix.ui.main_window.BackupRestoreService') as mock_backup_restore_service, \
             patch('fotix.ui.main_window.FileSystemService') as mock_file_system_service, \
             patch('fotix.ui.main_window.ZipHandlerService') as mock_zip_handler_service, \
             patch('fotix.ui.main_window.ConcurrencyService') as mock_concurrency_service, \
             patch('fotix.ui.main_window.BackupService') as mock_backup_service, \
             patch('fotix.ui.main_window.DuplicateFinderService') as mock_duplicate_finder_service, \
             patch('fotix.ui.main_window.create_strategy') as mock_create_strategy, \
             patch('fotix.main.QApplication') as mock_qapplication:

            # Configurar retornos dos mocks
            mock_app = MagicMock()
            mock_app.exec.return_value = 0
            mock_qapplication.instance.return_value = None
            mock_qapplication.return_value = mock_app

            # Chamar a função main
            result = main()

            # Verificar se a aplicação Qt foi inicializada
            assert mock_qapplication.call_count == 1

            # Verificar se a janela principal foi criada
            assert mock_scan_service.call_count == 1
            assert mock_duplicate_mgmt_service.call_count == 1
            assert mock_backup_restore_service.call_count == 1
            assert mock_file_system_service.call_count == 1
            assert mock_zip_handler_service.call_count == 1
            assert mock_concurrency_service.call_count == 1
            assert mock_backup_service.call_count == 1
            assert mock_duplicate_finder_service.call_count == 1
            assert mock_create_strategy.call_count == 1

            # Verificar se o loop de eventos foi iniciado
            assert mock_app.exec.call_count == 1

            # Verificar o código de saída
            assert result == 0
