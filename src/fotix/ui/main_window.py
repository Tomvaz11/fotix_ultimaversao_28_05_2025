"""
Janela principal da aplicação Fotix.

Este módulo implementa a janela principal da aplicação Fotix, que contém
a interface gráfica para interação com o usuário.
"""

import sys
from typing import List, Optional, Dict, Any
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolBar,
    QStatusBar, QFileDialog, QMessageBox, QTabWidget,
    QSplitter, QMenu, QApplication
)
from PySide6.QtGui import QAction, QIcon, QCloseEvent
from PySide6.QtCore import Qt, Signal, Slot, QSize

from fotix.core.models import DuplicateSet, FileInfo
from fotix.application.services.scan_service import ScanService
from fotix.application.services.duplicate_management_service import DuplicateManagementService
from fotix.application.services.backup_restore_service import BackupRestoreService
from fotix.infrastructure.file_system import FileSystemService
from fotix.infrastructure.zip_handler import ZipHandlerService
from fotix.infrastructure.concurrency import ConcurrencyService
from fotix.infrastructure.backup import BackupService
from fotix.core.duplicate_finder import DuplicateFinderService
from fotix.core.selection_strategy import create_strategy
from fotix.config import get_config

from fotix.ui.widgets.duplicate_list_widget import DuplicateListWidget
from fotix.ui.widgets.progress_dialog import ProgressDialog
from fotix.ui.widgets.settings_dialog import SettingsDialog
from fotix.ui.resources.icons import (
    ICON_APP, ICON_FOLDER, ICON_SCAN, ICON_DUPLICATE,
    ICON_SETTINGS, ICON_BACKUP, ICON_RESTORE, ICON_DELETE,
    ICON_HELP, ICON_EXIT
)


class MainWindow(QMainWindow):
    """
    Janela principal da aplicação Fotix.

    Esta classe implementa a janela principal da aplicação Fotix, que contém
    a interface gráfica para interação com o usuário.
    """

    def __init__(self):
        """Inicializa a janela principal."""
        super().__init__()

        self.setWindowTitle("Fotix - Gerenciador de Duplicatas")
        self.setWindowIcon(ICON_APP)
        self.resize(1024, 768)

        self._duplicate_sets: List[DuplicateSet] = []

        self._setup_services()
        self._setup_ui()

    def _setup_services(self):
        """Configura os serviços da aplicação."""
        # Serviços de infraestrutura
        self._file_system_service = FileSystemService()
        self._zip_handler_service = ZipHandlerService()
        self._concurrency_service = ConcurrencyService()
        self._backup_service = BackupService(self._file_system_service)

        # Serviços de domínio
        self._duplicate_finder_service = DuplicateFinderService(
            file_system_service=self._file_system_service,
            zip_handler_service=self._zip_handler_service
        )

        # Estratégia de seleção
        self._selection_strategy = create_strategy('highest_resolution', self._file_system_service)

        # Serviços de aplicação
        self._scan_service = ScanService(
            duplicate_finder_service=self._duplicate_finder_service,
            file_system_service=self._file_system_service,
            zip_handler_service=self._zip_handler_service,
            concurrency_service=self._concurrency_service
        )

        self._duplicate_mgmt_service = DuplicateManagementService(
            selection_strategy=self._selection_strategy,
            file_system_service=self._file_system_service,
            backup_service=self._backup_service
        )

        self._backup_restore_service = BackupRestoreService(
            backup_service=self._backup_service,
            file_system_service=self._file_system_service
        )

    def _setup_ui(self):
        """Configura a interface do usuário."""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Widget de lista de duplicatas
        self._duplicate_list_widget = DuplicateListWidget()
        self._duplicate_list_widget.process_duplicate.connect(self._on_process_duplicate)

        # Adicionar widget ao layout principal
        main_layout.addWidget(self._duplicate_list_widget)

        # Barra de status
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("Pronto")

        # Criar ações
        self._create_actions()

        # Criar menus
        self._create_menus()

        # Criar barra de ferramentas
        self._create_toolbar()

    def _create_actions(self):
        """Cria as ações da aplicação."""
        # Ação para escanear diretórios
        self._scan_action = QAction(ICON_SCAN, "Escanear Diretórios", self)
        self._scan_action.setStatusTip("Escanear diretórios em busca de duplicatas")
        self._scan_action.triggered.connect(self._on_scan_action)

        # Ação para configurações
        self._settings_action = QAction(ICON_SETTINGS, "Configurações", self)
        self._settings_action.setStatusTip("Configurar a aplicação")
        self._settings_action.triggered.connect(self._on_settings_action)

        # Ação para gerenciar backups
        self._backup_action = QAction(ICON_BACKUP, "Gerenciar Backups", self)
        self._backup_action.setStatusTip("Gerenciar backups de arquivos")
        self._backup_action.triggered.connect(self._on_backup_action)

        # Ação para restaurar backup
        self._restore_action = QAction(ICON_RESTORE, "Restaurar Backup", self)
        self._restore_action.setStatusTip("Restaurar arquivos de um backup")
        self._restore_action.triggered.connect(self._on_restore_action)

        # Ação para ajuda
        self._help_action = QAction(ICON_HELP, "Ajuda", self)
        self._help_action.setStatusTip("Exibir ajuda")
        self._help_action.triggered.connect(self._on_help_action)

        # Ação para sobre
        self._about_action = QAction("Sobre", self)
        self._about_action.setStatusTip("Exibir informações sobre a aplicação")
        self._about_action.triggered.connect(self._on_about_action)

        # Ação para sair
        self._exit_action = QAction(ICON_EXIT, "Sair", self)
        self._exit_action.setStatusTip("Sair da aplicação")
        self._exit_action.triggered.connect(self.close)

    def _create_menus(self):
        """Cria os menus da aplicação."""
        # Menu Arquivo
        file_menu = self.menuBar().addMenu("&Arquivo")
        file_menu.addAction(self._scan_action)
        file_menu.addSeparator()
        file_menu.addAction(self._settings_action)
        file_menu.addSeparator()
        file_menu.addAction(self._exit_action)

        # Menu Backup
        backup_menu = self.menuBar().addMenu("&Backup")
        backup_menu.addAction(self._backup_action)
        backup_menu.addAction(self._restore_action)

        # Menu Ajuda
        help_menu = self.menuBar().addMenu("A&juda")
        help_menu.addAction(self._help_action)
        help_menu.addAction(self._about_action)

    def _create_toolbar(self):
        """Cria a barra de ferramentas da aplicação."""
        # Barra de ferramentas principal
        toolbar = QToolBar("Barra de Ferramentas Principal")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addToolBar(toolbar)

        # Adicionar ações à barra de ferramentas
        toolbar.addAction(self._scan_action)
        toolbar.addSeparator()
        toolbar.addAction(self._backup_action)
        toolbar.addAction(self._restore_action)
        toolbar.addSeparator()
        toolbar.addAction(self._settings_action)
        toolbar.addSeparator()
        toolbar.addAction(self._help_action)

    @Slot()
    def _on_scan_action(self):
        """Manipula a ação de escanear diretórios."""
        # Obter diretório padrão das configurações
        config = get_config()
        default_dir = config.get("default_scan_dir", str(Path.home()))

        # Abrir diálogo para selecionar diretório
        directory = QFileDialog.getExistingDirectory(
            self,
            "Selecionar Diretório para Escanear",
            default_dir,
            QFileDialog.Option.ShowDirsOnly
        )

        if not directory:
            return

        # Converter para Path
        dir_paths = [Path(directory)]

        # Criar diálogo de progresso
        progress_dialog = ProgressDialog(
            "Escaneando Diretórios",
            f"Escaneando {len(dir_paths)} diretórios em busca de duplicatas...",
            self
        )

        # Conectar sinal de cancelamento
        progress_dialog.canceled.connect(self._on_scan_canceled)

        # Exibir diálogo
        progress_dialog.show()

        # Iniciar varredura em segundo plano
        try:
            # Obter callback de progresso
            progress_callback = progress_dialog.get_callback()

            # Iniciar varredura
            self._duplicate_sets = self._scan_service.scan_directories(
                directories=dir_paths,
                include_zips=True,
                progress_callback=progress_callback
            )

            # Atualizar widget de lista de duplicatas
            self._duplicate_list_widget.set_duplicate_sets(self._duplicate_sets)

            # Atualizar barra de status
            self._status_bar.showMessage(
                f"Varredura concluída. Encontrados {len(self._duplicate_sets)} conjuntos de duplicatas."
            )

        except Exception as e:
            # Fechar diálogo de progresso
            progress_dialog.reject()

            # Exibir mensagem de erro
            QMessageBox.critical(
                self,
                "Erro ao Escanear Diretórios",
                f"Ocorreu um erro ao escanear os diretórios: {str(e)}"
            )

            # Atualizar barra de status
            self._status_bar.showMessage("Erro ao escanear diretórios.")

    @Slot()
    def _on_scan_canceled(self):
        """Manipula o cancelamento da varredura."""
        self._status_bar.showMessage("Varredura cancelada pelo usuário.")

    @Slot()
    def _on_settings_action(self):
        """Manipula a ação de configurações."""
        # Criar diálogo de configurações
        settings_dialog = SettingsDialog(self)

        # Conectar sinal de configurações alteradas
        settings_dialog.settings_changed.connect(self._on_settings_changed)

        # Exibir diálogo
        settings_dialog.exec()

    @Slot(dict)
    def _on_settings_changed(self, settings: Dict[str, Any]):
        """
        Manipula a alteração de configurações.

        Args:
            settings: Configurações alteradas.
        """
        # Atualizar serviços com as novas configurações
        max_workers = settings.get("max_workers", 4)
        self._concurrency_service.set_max_workers(max_workers)

        # Atualizar barra de status
        self._status_bar.showMessage("Configurações atualizadas.")

    @Slot()
    def _on_backup_action(self):
        """Manipula a ação de gerenciar backups."""
        # Obter lista de backups
        backups = self._backup_restore_service.list_backups()

        # Exibir mensagem se não houver backups
        if not backups:
            QMessageBox.information(
                self,
                "Gerenciar Backups",
                "Não há backups disponíveis."
            )
            return

        # TODO: Implementar diálogo de gerenciamento de backups
        # Por enquanto, apenas exibir uma mensagem
        backup_info = "\n".join([
            f"ID: {backup['id']}, Data: {backup['date']}, Arquivos: {backup['file_count']}"
            for backup in backups
        ])

        QMessageBox.information(
            self,
            "Gerenciar Backups",
            f"Backups disponíveis:\n\n{backup_info}"
        )

    @Slot()
    def _on_restore_action(self):
        """Manipula a ação de restaurar backup."""
        # Obter lista de backups
        backups = self._backup_restore_service.list_backups()

        # Exibir mensagem se não houver backups
        if not backups:
            QMessageBox.information(
                self,
                "Restaurar Backup",
                "Não há backups disponíveis para restauração."
            )
            return

        # TODO: Implementar diálogo de seleção de backup e restauração
        # Por enquanto, apenas exibir uma mensagem
        QMessageBox.information(
            self,
            "Restaurar Backup",
            f"Há {len(backups)} backups disponíveis para restauração."
        )

    @Slot(DuplicateSet, FileInfo)
    def _on_process_duplicate(self, duplicate_set: DuplicateSet, file_to_keep: FileInfo):
        """
        Manipula o processamento de um conjunto de duplicatas.

        Args:
            duplicate_set: Conjunto de duplicatas a ser processado.
            file_to_keep: Arquivo a ser mantido.
        """
        # Criar diálogo de progresso
        progress_dialog = ProgressDialog(
            "Processando Duplicatas",
            f"Processando conjunto de duplicatas...",
            self
        )

        # Exibir diálogo
        progress_dialog.show()

        try:
            # Processar conjunto de duplicatas
            result = self._duplicate_mgmt_service.process_duplicate_set(
                duplicate_set=duplicate_set,
                create_backup=True,
                custom_selection=file_to_keep
            )

            # Verificar resultado
            if result['error'] is None:
                # Atualizar widget de lista de duplicatas
                self._duplicate_sets.remove(duplicate_set)
                self._duplicate_list_widget.set_duplicate_sets(self._duplicate_sets)

                # Exibir mensagem de sucesso
                QMessageBox.information(
                    self,
                    "Processamento Concluído",
                    f"Arquivo mantido: {result['kept_file'].path.name}\n"
                    f"Arquivos removidos: {len(result['removed_files'])}\n"
                    f"ID do backup: {result['backup_id']}"
                )

                # Atualizar barra de status
                self._status_bar.showMessage(
                    f"Processamento concluído. Mantido: {result['kept_file'].path.name}, "
                    f"Removidos: {len(result['removed_files'])} arquivos."
                )
            else:
                # Exibir mensagem de erro
                QMessageBox.critical(
                    self,
                    "Erro ao Processar Duplicatas",
                    f"Ocorreu um erro ao processar o conjunto de duplicatas: {result['error']}"
                )

                # Atualizar barra de status
                self._status_bar.showMessage("Erro ao processar duplicatas.")

        except Exception as e:
            # Fechar diálogo de progresso
            progress_dialog.reject()

            # Exibir mensagem de erro
            QMessageBox.critical(
                self,
                "Erro ao Processar Duplicatas",
                f"Ocorreu um erro ao processar o conjunto de duplicatas: {str(e)}"
            )

            # Atualizar barra de status
            self._status_bar.showMessage("Erro ao processar duplicatas.")

        # Fechar diálogo de progresso
        progress_dialog.accept()

    @Slot()
    def _on_help_action(self):
        """Manipula a ação de ajuda."""
        QMessageBox.information(
            self,
            "Ajuda",
            "Fotix - Gerenciador de Duplicatas\n\n"
            "1. Clique em 'Escanear Diretórios' para iniciar a busca por duplicatas.\n"
            "2. Selecione um conjunto de duplicatas na lista para ver os arquivos.\n"
            "3. Selecione um arquivo e clique em 'Processar Selecionado' para manter esse arquivo e remover os outros.\n"
            "4. Use 'Gerenciar Backups' para ver e restaurar backups de arquivos removidos."
        )

    @Slot()
    def _on_about_action(self):
        """Manipula a ação de sobre."""
        QMessageBox.about(
            self,
            "Sobre Fotix",
            "Fotix - Gerenciador de Duplicatas\n\n"
            "Versão 1.0\n\n"
            "Um aplicativo para encontrar e gerenciar arquivos duplicados."
        )

    def closeEvent(self, event: QCloseEvent):
        """
        Manipula o evento de fechamento da janela.

        Args:
            event: Evento de fechamento.
        """
        # Confirmar saída
        response = QMessageBox.question(
            self,
            "Confirmar Saída",
            "Tem certeza que deseja sair?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if response == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
