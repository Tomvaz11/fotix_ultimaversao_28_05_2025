"""
Testes unitários para o diálogo de configurações.

Este módulo contém testes para verificar o funcionamento correto do diálogo
de configurações da aplicação Fotix.
"""

import sys
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from PySide6.QtWidgets import QApplication, QDialog, QFileDialog
from PySide6.QtCore import Qt

from fotix.ui.widgets.settings_dialog import SettingsDialog


# Fixture para a aplicação Qt
@pytest.fixture
def app():
    """Fixture que cria uma instância da aplicação Qt."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


# Fixture para o diálogo de configurações
@pytest.fixture
def settings_dialog(app):
    """Fixture que cria uma instância do diálogo de configurações."""
    with patch('fotix.ui.widgets.settings_dialog.get_config') as mock_get_config:
        # Configurar mock para retornar configurações de teste
        mock_get_config.return_value = {
            "backup_dir": "/test/backup",
            "default_scan_dir": "/test/scan",
            "max_workers": 4,
            "log_level": "INFO",
            "log_file": "/test/logs/fotix.log"
        }
        
        dialog = SettingsDialog()
        yield dialog
        dialog.reject()


class TestSettingsDialog:
    """Testes para o diálogo de configurações."""

    def test_init(self, settings_dialog):
        """Testa a inicialização do diálogo."""
        # Verificar se o diálogo foi criado corretamente
        assert settings_dialog.windowTitle() == "Configurações"
        
        # Verificar se as configurações foram carregadas
        assert settings_dialog._config == {
            "backup_dir": "/test/backup",
            "default_scan_dir": "/test/scan",
            "max_workers": 4,
            "log_level": "INFO",
            "log_file": "/test/logs/fotix.log"
        }
        
        # Verificar se os widgets foram criados
        assert settings_dialog._tab_widget is not None
        assert settings_dialog._backup_dir_edit is not None
        assert settings_dialog._scan_dir_edit is not None
        assert settings_dialog._max_workers_spin is not None
        assert settings_dialog._log_level_combo is not None
        assert settings_dialog._log_file_edit is not None
    
    def test_load_settings(self, settings_dialog):
        """Testa o carregamento das configurações nos widgets."""
        # Verificar que os widgets foram preenchidos corretamente
        assert settings_dialog._backup_dir_edit.text() == "/test/backup"
        assert settings_dialog._scan_dir_edit.text() == "/test/scan"
        assert settings_dialog._max_workers_spin.value() == 4
        assert settings_dialog._log_level_combo.currentText() == "INFO"
        assert settings_dialog._log_file_edit.text() == "/test/logs/fotix.log"
    
    def test_save_settings(self, settings_dialog):
        """Testa o salvamento das configurações dos widgets."""
        # Modificar widgets
        settings_dialog._backup_dir_edit.setText("/new/backup")
        settings_dialog._scan_dir_edit.setText("/new/scan")
        settings_dialog._max_workers_spin.setValue(8)
        settings_dialog._log_level_combo.setCurrentText("DEBUG")
        settings_dialog._log_file_edit.setText("/new/logs/fotix.log")
        
        # Chamar método
        updated_config = settings_dialog._save_settings()
        
        # Verificar que as configurações foram atualizadas corretamente
        assert updated_config["backup_dir"] == "/new/backup"
        assert updated_config["default_scan_dir"] == "/new/scan"
        assert updated_config["max_workers"] == 8
        assert updated_config["log_level"] == "DEBUG"
        assert updated_config["log_file"] == "/new/logs/fotix.log"
    
    @patch('fotix.ui.widgets.settings_dialog.QFileDialog.getExistingDirectory')
    def test_on_backup_dir_browse_canceled(self, mock_get_directory, settings_dialog):
        """Testa o clique no botão de procurar diretório de backup quando o usuário cancela."""
        # Configurar mock para simular cancelamento
        mock_get_directory.return_value = ""
        
        # Chamar método
        settings_dialog._on_backup_dir_browse()
        
        # Verificar que o diálogo foi exibido
        mock_get_directory.assert_called_once()
        
        # Verificar que o campo não foi alterado
        assert settings_dialog._backup_dir_edit.text() == "/test/backup"
    
    @patch('fotix.ui.widgets.settings_dialog.QFileDialog.getExistingDirectory')
    def test_on_backup_dir_browse_selected(self, mock_get_directory, settings_dialog):
        """Testa o clique no botão de procurar diretório de backup quando o usuário seleciona um diretório."""
        # Configurar mock para simular seleção
        mock_get_directory.return_value = "/new/backup"
        
        # Chamar método
        settings_dialog._on_backup_dir_browse()
        
        # Verificar que o diálogo foi exibido
        mock_get_directory.assert_called_once()
        
        # Verificar que o campo foi atualizado
        assert settings_dialog._backup_dir_edit.text() == "/new/backup"
    
    @patch('fotix.ui.widgets.settings_dialog.QFileDialog.getExistingDirectory')
    def test_on_scan_dir_browse_selected(self, mock_get_directory, settings_dialog):
        """Testa o clique no botão de procurar diretório de varredura quando o usuário seleciona um diretório."""
        # Configurar mock para simular seleção
        mock_get_directory.return_value = "/new/scan"
        
        # Chamar método
        settings_dialog._on_scan_dir_browse()
        
        # Verificar que o diálogo foi exibido
        mock_get_directory.assert_called_once()
        
        # Verificar que o campo foi atualizado
        assert settings_dialog._scan_dir_edit.text() == "/new/scan"
    
    @patch('fotix.ui.widgets.settings_dialog.QFileDialog.getSaveFileName')
    def test_on_log_file_browse_selected(self, mock_get_file, settings_dialog):
        """Testa o clique no botão de procurar arquivo de log quando o usuário seleciona um arquivo."""
        # Configurar mock para simular seleção
        mock_get_file.return_value = ("/new/logs/fotix.log", "Arquivos de Log (*.log)")
        
        # Chamar método
        settings_dialog._on_log_file_browse()
        
        # Verificar que o diálogo foi exibido
        mock_get_file.assert_called_once()
        
        # Verificar que o campo foi atualizado
        assert settings_dialog._log_file_edit.text() == "/new/logs/fotix.log"
    
    @patch('fotix.ui.widgets.settings_dialog.update_config')
    def test_on_accept(self, mock_update_config, settings_dialog):
        """Testa o clique no botão OK."""
        # Configurar mocks
        settings_dialog._save_settings = MagicMock(return_value={
            "backup_dir": "/new/backup",
            "default_scan_dir": "/new/scan",
            "max_workers": 8,
            "log_level": "DEBUG",
            "log_file": "/new/logs/fotix.log"
        })
        settings_dialog.settings_changed = MagicMock()
        settings_dialog.accept = MagicMock()
        
        # Chamar método
        settings_dialog._on_accept()
        
        # Verificar que _save_settings foi chamado
        settings_dialog._save_settings.assert_called_once()
        
        # Verificar que update_config foi chamado para cada configuração
        assert mock_update_config.call_count == 5
        
        # Verificar que o sinal foi emitido
        settings_dialog.settings_changed.emit.assert_called_once()
        
        # Verificar que o diálogo foi aceito
        settings_dialog.accept.assert_called_once()
