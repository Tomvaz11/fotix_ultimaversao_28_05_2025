"""
Testes unitários para a janela principal da aplicação Fotix.

Este módulo contém testes para verificar o funcionamento correto da janela
principal da aplicação Fotix.
"""

import sys
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QTimer

from fotix.ui.main_window import MainWindow
from fotix.core.models import DuplicateSet, FileInfo


# Fixture para a aplicação Qt
@pytest.fixture
def app():
    """Fixture que cria uma instância da aplicação Qt."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


# Fixture para a janela principal
@pytest.fixture
def main_window(app):
    """Fixture que cria uma instância da janela principal."""
    with patch('fotix.ui.main_window.ScanService'), \
         patch('fotix.ui.main_window.DuplicateManagementService'), \
         patch('fotix.ui.main_window.BackupRestoreService'), \
         patch('fotix.ui.main_window.FileSystemService'), \
         patch('fotix.ui.main_window.ZipHandlerService'), \
         patch('fotix.ui.main_window.ConcurrencyService'), \
         patch('fotix.ui.main_window.BackupService'), \
         patch('fotix.ui.main_window.DuplicateFinderService'), \
         patch('fotix.ui.main_window.create_strategy'):
        window = MainWindow()
        yield window
        window.close()


class TestMainWindow:
    """Testes para a janela principal."""

    def test_init(self, main_window):
        """Testa a inicialização da janela principal."""
        # Verificar se a janela foi criada corretamente
        assert main_window.windowTitle() == "Fotix - Gerenciador de Duplicatas"
        assert main_window.isVisible() is False

    def test_setup_services(self, main_window):
        """Testa a configuração dos serviços."""
        # Verificar se os serviços foram configurados
        assert main_window._file_system_service is not None
        assert main_window._zip_handler_service is not None
        assert main_window._concurrency_service is not None
        assert main_window._backup_service is not None
        assert main_window._duplicate_finder_service is not None
        assert main_window._selection_strategy is not None
        assert main_window._scan_service is not None
        assert main_window._duplicate_mgmt_service is not None
        assert main_window._backup_restore_service is not None

    def test_setup_ui(self, main_window):
        """Testa a configuração da interface do usuário."""
        # Verificar se os widgets foram criados
        assert main_window._duplicate_list_widget is not None
        assert main_window._status_bar is not None

        # Verificar se as ações foram criadas
        assert main_window._scan_action is not None
        assert main_window._settings_action is not None
        assert main_window._backup_action is not None
        assert main_window._restore_action is not None
        assert main_window._help_action is not None
        assert main_window._about_action is not None
        assert main_window._exit_action is not None

    @patch('fotix.ui.main_window.QFileDialog.getExistingDirectory')
    @patch('fotix.ui.main_window.ProgressDialog')
    def test_on_scan_action_canceled(self, mock_progress_dialog, mock_get_directory, main_window):
        """Testa a ação de escanear diretórios quando o usuário cancela a seleção."""
        # Configurar mock para simular cancelamento
        mock_get_directory.return_value = ""

        # Chamar método
        main_window._on_scan_action()

        # Verificar que o diálogo de progresso não foi criado
        mock_progress_dialog.assert_not_called()

    @patch('fotix.ui.main_window.QFileDialog.getExistingDirectory')
    @patch('fotix.ui.main_window.ProgressDialog')
    def test_on_scan_action_success(self, mock_progress_dialog, mock_get_directory, main_window):
        """Testa a ação de escanear diretórios com sucesso."""
        # Configurar mocks
        mock_get_directory.return_value = "/test/dir1"
        mock_dialog = MagicMock()
        mock_progress_dialog.return_value = mock_dialog
        mock_callback = MagicMock()
        mock_dialog.get_callback.return_value = mock_callback

        # Configurar mock do serviço de varredura
        main_window._scan_service.scan_directories.return_value = []

        # Chamar método
        main_window._on_scan_action()

        # Verificar que o diálogo de progresso foi criado e exibido
        mock_progress_dialog.assert_called_once()
        mock_dialog.show.assert_called_once()

        # Verificar que o serviço de varredura foi chamado com os parâmetros corretos
        main_window._scan_service.scan_directories.assert_called_once()
        args, kwargs = main_window._scan_service.scan_directories.call_args
        assert len(kwargs['directories']) == 1
        assert kwargs['include_zips'] is True
        assert kwargs['progress_callback'] == mock_callback

    @patch('fotix.ui.main_window.QFileDialog.getExistingDirectory')
    @patch('fotix.ui.main_window.ProgressDialog')
    @patch('fotix.ui.main_window.QMessageBox.critical')
    def test_on_scan_action_error(self, mock_message_box, mock_progress_dialog, mock_get_directory, main_window):
        """Testa a ação de escanear diretórios com erro."""
        # Configurar mocks
        mock_get_directory.return_value = "/test/dir1"
        mock_dialog = MagicMock()
        mock_progress_dialog.return_value = mock_dialog

        # Configurar mock do serviço de varredura para lançar exceção
        main_window._scan_service.scan_directories.side_effect = Exception("Erro de teste")

        # Chamar método
        main_window._on_scan_action()

        # Verificar que o diálogo de progresso foi criado e rejeitado
        mock_progress_dialog.assert_called_once()
        mock_dialog.reject.assert_called_once()

        # Verificar que a mensagem de erro foi exibida
        mock_message_box.assert_called_once()

    @patch('fotix.ui.main_window.SettingsDialog')
    def test_on_settings_action(self, mock_settings_dialog, main_window):
        """Testa a ação de configurações."""
        # Configurar mock
        mock_dialog = MagicMock()
        mock_settings_dialog.return_value = mock_dialog

        # Chamar método
        main_window._on_settings_action()

        # Verificar que o diálogo de configurações foi criado e exibido
        mock_settings_dialog.assert_called_once()
        mock_dialog.exec.assert_called_once()

    def test_on_settings_changed(self, main_window):
        """Testa a alteração de configurações."""
        # Configurar mock
        main_window._concurrency_service = MagicMock()

        # Chamar método
        main_window._on_settings_changed({"max_workers": 8})

        # Verificar que o serviço de concorrência foi atualizado
        main_window._concurrency_service.set_max_workers.assert_called_once_with(8)

    @patch('fotix.ui.main_window.QMessageBox.information')
    def test_on_backup_action_no_backups(self, mock_message_box, main_window):
        """Testa a ação de gerenciar backups quando não há backups."""
        # Configurar mock
        main_window._backup_restore_service.list_backups.return_value = []

        # Chamar método
        main_window._on_backup_action()

        # Verificar que a mensagem foi exibida
        mock_message_box.assert_called_once()

    @patch('fotix.ui.main_window.QMessageBox.information')
    def test_on_backup_action_with_backups(self, mock_message_box, main_window):
        """Testa a ação de gerenciar backups quando há backups."""
        # Configurar mock
        main_window._backup_restore_service.list_backups.return_value = [
            {"id": "backup1", "date": "2023-01-01", "file_count": 5},
            {"id": "backup2", "date": "2023-01-02", "file_count": 3}
        ]

        # Chamar método
        main_window._on_backup_action()

        # Verificar que a mensagem foi exibida
        mock_message_box.assert_called_once()

    @patch('fotix.ui.main_window.QMessageBox.question')
    def test_close_event_yes(self, mock_message_box, main_window):
        """Testa o evento de fechamento da janela quando o usuário confirma."""
        # Configurar mock
        mock_message_box.return_value = QMessageBox.StandardButton.Yes
        mock_event = MagicMock()

        # Chamar método
        main_window.closeEvent(mock_event)

        # Verificar que o evento foi aceito
        mock_event.accept.assert_called_once()

    @patch('fotix.ui.main_window.QMessageBox.question')
    def test_close_event_no(self, mock_message_box, main_window):
        """Testa o evento de fechamento da janela quando o usuário cancela."""
        # Configurar mock
        mock_message_box.return_value = QMessageBox.StandardButton.No
        mock_event = MagicMock()

        # Chamar método
        main_window.closeEvent(mock_event)

        # Verificar que o evento foi ignorado
        mock_event.ignore.assert_called_once()

    @patch('fotix.ui.main_window.QMessageBox.information')
    def test_on_restore_action_no_backups(self, mock_message_box, main_window):
        """Testa a ação de restaurar backup quando não há backups."""
        # Configurar mock
        main_window._backup_restore_service.list_backups.return_value = []

        # Chamar método
        main_window._on_restore_action()

        # Verificar que a mensagem foi exibida
        mock_message_box.assert_called_once()

    @patch('fotix.ui.main_window.QMessageBox.information')
    def test_on_restore_action_with_backups(self, mock_message_box, main_window):
        """Testa a ação de restaurar backup quando há backups."""
        # Configurar mock
        main_window._backup_restore_service.list_backups.return_value = [
            {"id": "backup1", "date": "2023-01-01", "file_count": 5},
            {"id": "backup2", "date": "2023-01-02", "file_count": 3}
        ]

        # Chamar método
        main_window._on_restore_action()

        # Verificar que a mensagem foi exibida
        mock_message_box.assert_called_once()

    @patch('fotix.ui.main_window.ProgressDialog')
    @patch('fotix.ui.main_window.QMessageBox.information')
    def test_on_process_duplicate_success(self, mock_message_box, mock_progress_dialog, main_window):
        """Testa o processamento de duplicatas com sucesso."""
        # Configurar mocks
        mock_dialog = MagicMock()
        mock_progress_dialog.return_value = mock_dialog

        # Criar objetos de teste
        duplicate_set = MagicMock()
        file_to_keep = MagicMock()
        file_to_keep.path.name = "test.jpg"

        # Configurar mock do serviço
        main_window._duplicate_mgmt_service.process_duplicate_set.return_value = {
            "error": None,
            "kept_file": file_to_keep,
            "removed_files": [MagicMock(), MagicMock()],
            "backup_id": "backup123"
        }

        # Adicionar o conjunto de duplicatas à lista
        main_window._duplicate_sets = [duplicate_set]

        # Chamar método
        main_window._on_process_duplicate(duplicate_set, file_to_keep)

        # Verificar que o diálogo de progresso foi criado e exibido
        mock_progress_dialog.assert_called_once()
        mock_dialog.show.assert_called_once()

        # Verificar que o serviço foi chamado
        main_window._duplicate_mgmt_service.process_duplicate_set.assert_called_once()

        # Verificar que a mensagem de sucesso foi exibida
        mock_message_box.assert_called_once()

        # Verificar que o diálogo foi fechado
        mock_dialog.accept.assert_called_once()

    @patch('fotix.ui.main_window.ProgressDialog')
    @patch('fotix.ui.main_window.QMessageBox.critical')
    def test_on_process_duplicate_error_result(self, mock_message_box, mock_progress_dialog, main_window):
        """Testa o processamento de duplicatas com erro no resultado."""
        # Configurar mocks
        mock_dialog = MagicMock()
        mock_progress_dialog.return_value = mock_dialog

        # Criar objetos de teste
        duplicate_set = MagicMock()
        file_to_keep = MagicMock()

        # Configurar mock do serviço
        main_window._duplicate_mgmt_service.process_duplicate_set.return_value = {
            "error": "Erro de teste",
            "kept_file": None,
            "removed_files": [],
            "backup_id": None
        }

        # Chamar método
        main_window._on_process_duplicate(duplicate_set, file_to_keep)

        # Verificar que o diálogo de progresso foi criado e exibido
        mock_progress_dialog.assert_called_once()
        mock_dialog.show.assert_called_once()

        # Verificar que o serviço foi chamado
        main_window._duplicate_mgmt_service.process_duplicate_set.assert_called_once()

        # Verificar que a mensagem de erro foi exibida
        mock_message_box.assert_called_once()

        # Verificar que o diálogo foi fechado
        mock_dialog.accept.assert_called_once()

    @patch('fotix.ui.main_window.ProgressDialog')
    @patch('fotix.ui.main_window.QMessageBox.critical')
    def test_on_process_duplicate_exception(self, mock_message_box, mock_progress_dialog, main_window):
        """Testa o processamento de duplicatas com exceção."""
        # Configurar mocks
        mock_dialog = MagicMock()
        mock_progress_dialog.return_value = mock_dialog

        # Criar objetos de teste
        duplicate_set = MagicMock()
        file_to_keep = MagicMock()

        # Configurar mock do serviço para lançar exceção
        main_window._duplicate_mgmt_service.process_duplicate_set.side_effect = Exception("Erro de teste")

        # Chamar método
        main_window._on_process_duplicate(duplicate_set, file_to_keep)

        # Verificar que o diálogo de progresso foi criado e rejeitado
        mock_progress_dialog.assert_called_once()
        mock_dialog.reject.assert_called_once()

        # Verificar que a mensagem de erro foi exibida
        mock_message_box.assert_called_once()

    @patch('fotix.ui.main_window.QMessageBox.information')
    def test_on_help_action(self, mock_message_box, main_window):
        """Testa a ação de ajuda."""
        # Chamar método
        main_window._on_help_action()

        # Verificar que a mensagem foi exibida
        mock_message_box.assert_called_once()

    @patch('fotix.ui.main_window.QMessageBox.about')
    def test_on_about_action(self, mock_message_box, main_window):
        """Testa a ação de sobre."""
        # Chamar método
        main_window._on_about_action()

        # Verificar que a mensagem foi exibida
        mock_message_box.assert_called_once()

    def test_on_scan_canceled(self, main_window):
        """Testa o cancelamento da varredura."""
        # Configurar mock
        main_window._status_bar = MagicMock()

        # Chamar método
        main_window._on_scan_canceled()

        # Verificar que a mensagem foi exibida na barra de status
        main_window._status_bar.showMessage.assert_called_once_with("Varredura cancelada pelo usuário.")
