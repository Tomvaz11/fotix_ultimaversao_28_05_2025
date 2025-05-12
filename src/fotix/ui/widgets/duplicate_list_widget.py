"""
Widget para exibição e gerenciamento de duplicatas.

Este módulo implementa um widget personalizado para exibir conjuntos de arquivos
duplicados e permitir ao usuário selecionar quais arquivos manter ou remover.
"""

from typing import List, Optional, Dict, Any, Callable

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QHeaderView, QSplitter, QFrame, QMenu, QMessageBox
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QAction, QIcon, QContextMenuEvent

from fotix.core.models import DuplicateSet, FileInfo
from fotix.ui.widgets.file_info_widget import FileInfoWidget
from fotix.ui.resources.icons import ICON_DELETE, ICON_DUPLICATE


class DuplicateListWidget(QWidget):
    """
    Widget para exibição e gerenciamento de duplicatas.
    
    Este widget exibe uma lista de conjuntos de arquivos duplicados e permite
    ao usuário selecionar quais arquivos manter ou remover.
    
    Signals:
        duplicate_selected: Emitido quando um conjunto de duplicatas é selecionado.
        file_selected: Emitido quando um arquivo é selecionado.
        process_duplicate: Emitido quando o usuário solicita o processamento de um conjunto de duplicatas.
    """
    
    # Sinais
    duplicate_selected = Signal(DuplicateSet)
    file_selected = Signal(FileInfo)
    process_duplicate = Signal(DuplicateSet, FileInfo)
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Inicializa o widget de lista de duplicatas.
        
        Args:
            parent: Widget pai opcional.
        """
        super().__init__(parent)
        
        self._duplicate_sets: List[DuplicateSet] = []
        self._current_duplicate_set: Optional[DuplicateSet] = None
        self._current_file: Optional[FileInfo] = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura a interface do usuário."""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Splitter para dividir a lista de duplicatas e os detalhes do arquivo
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Árvore de duplicatas
        self._tree_widget = QTreeWidget()
        self._tree_widget.setHeaderLabels(["Conjuntos de Duplicatas", "Tamanho", "Arquivos"])
        self._tree_widget.setColumnWidth(0, 300)
        self._tree_widget.setColumnWidth(1, 100)
        self._tree_widget.setColumnWidth(2, 80)
        self._tree_widget.setAlternatingRowColors(True)
        self._tree_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree_widget.customContextMenuRequested.connect(self._show_context_menu)
        self._tree_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self._tree_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        # Widget de informações do arquivo
        self._file_info_widget = FileInfoWidget()
        
        # Adicionar widgets ao splitter
        splitter.addWidget(self._tree_widget)
        splitter.addWidget(self._file_info_widget)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        # Adicionar splitter ao layout principal
        main_layout.addWidget(splitter)
        
        # Barra de botões
        button_layout = QHBoxLayout()
        
        # Botão para processar duplicatas
        self._process_button = QPushButton("Processar Selecionado")
        self._process_button.setIcon(ICON_DELETE)
        self._process_button.setEnabled(False)
        self._process_button.clicked.connect(self._on_process_clicked)
        
        # Adicionar botões ao layout
        button_layout.addStretch()
        button_layout.addWidget(self._process_button)
        
        # Adicionar layout de botões ao layout principal
        main_layout.addLayout(button_layout)
    
    def set_duplicate_sets(self, duplicate_sets: List[DuplicateSet]):
        """
        Define os conjuntos de duplicatas a serem exibidos.
        
        Args:
            duplicate_sets: Lista de conjuntos de duplicatas.
        """
        self._duplicate_sets = duplicate_sets
        self._populate_tree()
    
    def _populate_tree(self):
        """Preenche a árvore com os conjuntos de duplicatas."""
        self._tree_widget.clear()
        
        for duplicate_set in self._duplicate_sets:
            # Criar item para o conjunto de duplicatas
            item = QTreeWidgetItem(self._tree_widget)
            item.setText(0, f"Hash: {duplicate_set.hash[:8]}...")
            item.setText(1, self._format_size(duplicate_set.size))
            item.setText(2, str(duplicate_set.count))
            item.setIcon(0, ICON_DUPLICATE)
            item.setData(0, Qt.ItemDataRole.UserRole, duplicate_set)
            
            # Adicionar arquivos como filhos
            for file_info in duplicate_set.files:
                child = QTreeWidgetItem(item)
                child.setText(0, str(file_info.path.name))
                child.setText(1, self._format_size(file_info.size))
                child.setData(0, Qt.ItemDataRole.UserRole, file_info)
                
                # Destacar o arquivo selecionado para manter (se houver)
                if duplicate_set.selected_file == file_info:
                    child.setBackground(0, Qt.GlobalColor.green)
        
        self._tree_widget.expandAll()
    
    def _format_size(self, size: int) -> str:
        """
        Formata um tamanho em bytes para uma string legível.
        
        Args:
            size: Tamanho em bytes.
        
        Returns:
            str: Tamanho formatado (ex: "1.2 MB").
        """
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"
    
    @Slot()
    def _on_selection_changed(self):
        """Manipula a mudança de seleção na árvore."""
        selected_items = self._tree_widget.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        data = item.data(0, Qt.ItemDataRole.UserRole)
        
        if isinstance(data, DuplicateSet):
            self._current_duplicate_set = data
            self._current_file = None
            self.duplicate_selected.emit(data)
            self._file_info_widget.clear()
            self._process_button.setEnabled(False)
        elif isinstance(data, FileInfo):
            self._current_file = data
            self.file_selected.emit(data)
            self._file_info_widget.set_file_info(data)
            
            # Obter o conjunto de duplicatas pai
            parent_item = item.parent()
            if parent_item:
                parent_data = parent_item.data(0, Qt.ItemDataRole.UserRole)
                if isinstance(parent_data, DuplicateSet):
                    self._current_duplicate_set = parent_data
                    self._process_button.setEnabled(True)
    
    @Slot(QTreeWidgetItem, int)
    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """
        Manipula o duplo clique em um item da árvore.
        
        Args:
            item: Item clicado.
            column: Coluna clicada.
        """
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, FileInfo):
            self._current_file = data
            
            # Obter o conjunto de duplicatas pai
            parent_item = item.parent()
            if parent_item:
                parent_data = parent_item.data(0, Qt.ItemDataRole.UserRole)
                if isinstance(parent_data, DuplicateSet):
                    self._current_duplicate_set = parent_data
                    
                    # Perguntar se deseja processar este conjunto
                    response = QMessageBox.question(
                        self,
                        "Processar Duplicata",
                        f"Deseja manter o arquivo '{data.path.name}' e remover os outros duplicados?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if response == QMessageBox.StandardButton.Yes:
                        self.process_duplicate.emit(self._current_duplicate_set, self._current_file)
    
    @Slot()
    def _on_process_clicked(self):
        """Manipula o clique no botão de processar."""
        if self._current_duplicate_set and self._current_file:
            # Confirmar a ação
            response = QMessageBox.question(
                self,
                "Processar Duplicata",
                f"Deseja manter o arquivo '{self._current_file.path.name}' e remover os outros duplicados?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if response == QMessageBox.StandardButton.Yes:
                self.process_duplicate.emit(self._current_duplicate_set, self._current_file)
    
    @Slot(object)
    def _show_context_menu(self, position):
        """
        Exibe o menu de contexto.
        
        Args:
            position: Posição do clique.
        """
        item = self._tree_widget.itemAt(position)
        if not item:
            return
        
        data = item.data(0, Qt.ItemDataRole.UserRole)
        
        menu = QMenu(self)
        
        if isinstance(data, FileInfo):
            # Menu para arquivo
            action_keep = QAction("Manter este arquivo", self)
            action_keep.triggered.connect(lambda: self._on_keep_file(data))
            menu.addAction(action_keep)
            
            # Obter o conjunto de duplicatas pai
            parent_item = item.parent()
            if parent_item:
                parent_data = parent_item.data(0, Qt.ItemDataRole.UserRole)
                if isinstance(parent_data, DuplicateSet):
                    self._current_duplicate_set = parent_data
        
        elif isinstance(data, DuplicateSet):
            # Menu para conjunto de duplicatas
            action_expand = QAction("Expandir/Colapsar", self)
            action_expand.triggered.connect(lambda: self._toggle_expand_item(item))
            menu.addAction(action_expand)
        
        if menu.actions():
            menu.exec(self._tree_widget.viewport().mapToGlobal(position))
    
    def _on_keep_file(self, file_info: FileInfo):
        """
        Manipula a ação de manter um arquivo.
        
        Args:
            file_info: Arquivo a ser mantido.
        """
        if self._current_duplicate_set:
            # Confirmar a ação
            response = QMessageBox.question(
                self,
                "Processar Duplicata",
                f"Deseja manter o arquivo '{file_info.path.name}' e remover os outros duplicados?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if response == QMessageBox.StandardButton.Yes:
                self.process_duplicate.emit(self._current_duplicate_set, file_info)
    
    def _toggle_expand_item(self, item: QTreeWidgetItem):
        """
        Alterna a expansão de um item.
        
        Args:
            item: Item a ser expandido/colapsado.
        """
        if item.isExpanded():
            item.setExpanded(False)
        else:
            item.setExpanded(True)
    
    def refresh(self):
        """Atualiza a exibição dos conjuntos de duplicatas."""
        self._populate_tree()
