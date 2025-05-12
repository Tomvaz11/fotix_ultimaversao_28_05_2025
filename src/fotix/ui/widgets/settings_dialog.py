"""
Diálogo de configurações da aplicação.

Este módulo implementa um diálogo para exibir e modificar as configurações
da aplicação, como diretório de backup, nível de log, etc.
"""

from typing import Optional, Dict, Any
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QPushButton, QLineEdit, QSpinBox, QComboBox, QFileDialog,
    QDialogButtonBox, QTabWidget, QWidget, QGroupBox
)
from PySide6.QtCore import Qt, Signal, Slot

from fotix.config import get_config, update_config, save_config


class SettingsDialog(QDialog):
    """
    Diálogo de configurações da aplicação.
    
    Este diálogo permite ao usuário visualizar e modificar as configurações
    da aplicação, como diretório de backup, nível de log, etc.
    
    Signals:
        settings_changed: Emitido quando as configurações são alteradas.
    """
    
    # Sinais
    settings_changed = Signal(dict)
    
    def __init__(self, parent: Optional[QDialog] = None):
        """
        Inicializa o diálogo de configurações.
        
        Args:
            parent: Widget pai opcional.
        """
        super().__init__(parent)
        
        self.setWindowTitle("Configurações")
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        
        self._config = get_config().copy()
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Configura a interface do usuário."""
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Abas
        self._tab_widget = QTabWidget()
        
        # Aba de configurações gerais
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # Grupo de diretórios
        directories_group = QGroupBox("Diretórios")
        directories_layout = QFormLayout(directories_group)
        
        # Diretório de backup
        backup_layout = QHBoxLayout()
        self._backup_dir_edit = QLineEdit()
        self._backup_dir_edit.setReadOnly(True)
        backup_browse_button = QPushButton("Procurar...")
        backup_browse_button.clicked.connect(self._on_backup_dir_browse)
        backup_layout.addWidget(self._backup_dir_edit)
        backup_layout.addWidget(backup_browse_button)
        directories_layout.addRow("Diretório de Backup:", backup_layout)
        
        # Diretório de varredura padrão
        scan_layout = QHBoxLayout()
        self._scan_dir_edit = QLineEdit()
        self._scan_dir_edit.setReadOnly(True)
        scan_browse_button = QPushButton("Procurar...")
        scan_browse_button.clicked.connect(self._on_scan_dir_browse)
        scan_layout.addWidget(self._scan_dir_edit)
        scan_layout.addWidget(scan_browse_button)
        directories_layout.addRow("Diretório de Varredura Padrão:", scan_layout)
        
        general_layout.addWidget(directories_group)
        
        # Grupo de desempenho
        performance_group = QGroupBox("Desempenho")
        performance_layout = QFormLayout(performance_group)
        
        # Número máximo de workers
        self._max_workers_spin = QSpinBox()
        self._max_workers_spin.setRange(1, 16)
        performance_layout.addRow("Número Máximo de Workers:", self._max_workers_spin)
        
        general_layout.addWidget(performance_group)
        
        # Aba de configurações de log
        log_tab = QWidget()
        log_layout = QFormLayout(log_tab)
        
        # Nível de log
        self._log_level_combo = QComboBox()
        self._log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        log_layout.addRow("Nível de Log:", self._log_level_combo)
        
        # Arquivo de log
        log_file_layout = QHBoxLayout()
        self._log_file_edit = QLineEdit()
        self._log_file_edit.setReadOnly(True)
        log_file_browse_button = QPushButton("Procurar...")
        log_file_browse_button.clicked.connect(self._on_log_file_browse)
        log_file_layout.addWidget(self._log_file_edit)
        log_file_layout.addWidget(log_file_browse_button)
        log_layout.addRow("Arquivo de Log:", log_file_layout)
        
        # Adicionar abas
        self._tab_widget.addTab(general_tab, "Geral")
        self._tab_widget.addTab(log_tab, "Log")
        
        layout.addWidget(self._tab_widget)
        
        # Botões
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
    
    def _load_settings(self):
        """Carrega as configurações atuais nos widgets."""
        # Diretório de backup
        self._backup_dir_edit.setText(str(self._config.get("backup_dir", "")))
        
        # Diretório de varredura padrão
        self._scan_dir_edit.setText(str(self._config.get("default_scan_dir", "")))
        
        # Número máximo de workers
        self._max_workers_spin.setValue(self._config.get("max_workers", 4))
        
        # Nível de log
        log_level = self._config.get("log_level", "INFO")
        index = self._log_level_combo.findText(log_level)
        if index >= 0:
            self._log_level_combo.setCurrentIndex(index)
        
        # Arquivo de log
        self._log_file_edit.setText(str(self._config.get("log_file", "")))
    
    def _save_settings(self) -> Dict[str, Any]:
        """
        Salva as configurações dos widgets.
        
        Returns:
            Dict[str, Any]: Configurações atualizadas.
        """
        # Criar uma cópia das configurações atuais
        updated_config = self._config.copy()
        
        # Atualizar com os valores dos widgets
        updated_config["backup_dir"] = self._backup_dir_edit.text()
        updated_config["default_scan_dir"] = self._scan_dir_edit.text()
        updated_config["max_workers"] = self._max_workers_spin.value()
        updated_config["log_level"] = self._log_level_combo.currentText()
        updated_config["log_file"] = self._log_file_edit.text()
        
        return updated_config
    
    @Slot()
    def _on_backup_dir_browse(self):
        """Manipula o clique no botão de procurar diretório de backup."""
        current_dir = self._backup_dir_edit.text()
        directory = QFileDialog.getExistingDirectory(
            self,
            "Selecionar Diretório de Backup",
            current_dir
        )
        
        if directory:
            self._backup_dir_edit.setText(directory)
    
    @Slot()
    def _on_scan_dir_browse(self):
        """Manipula o clique no botão de procurar diretório de varredura padrão."""
        current_dir = self._scan_dir_edit.text()
        directory = QFileDialog.getExistingDirectory(
            self,
            "Selecionar Diretório de Varredura Padrão",
            current_dir
        )
        
        if directory:
            self._scan_dir_edit.setText(directory)
    
    @Slot()
    def _on_log_file_browse(self):
        """Manipula o clique no botão de procurar arquivo de log."""
        current_file = self._log_file_edit.text()
        file, _ = QFileDialog.getSaveFileName(
            self,
            "Selecionar Arquivo de Log",
            current_file,
            "Arquivos de Log (*.log);;Todos os Arquivos (*)"
        )
        
        if file:
            self._log_file_edit.setText(file)
    
    @Slot()
    def _on_accept(self):
        """Manipula o clique no botão OK."""
        # Salvar configurações
        updated_config = self._save_settings()
        
        # Atualizar configurações globais
        for key, value in updated_config.items():
            update_config(key, value)
        
        # Emitir sinal de configurações alteradas
        self.settings_changed.emit(updated_config)
        
        # Fechar diálogo
        self.accept()
