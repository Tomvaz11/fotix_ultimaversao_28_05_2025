"""
Testes unitários para o widget de lista de duplicatas.

Este módulo contém testes para verificar o funcionamento correto do widget
de lista de duplicatas da aplicação Fotix.
"""

import sys
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from PySide6.QtWidgets import QApplication, QTreeWidgetItem, QMessageBox
from PySide6.QtCore import Qt

from fotix.ui.widgets.duplicate_list_widget import DuplicateListWidget
from fotix.core.models import DuplicateSet, FileInfo


# Fixture para a aplicação Qt
@pytest.fixture
def app():
    """Fixture que cria uma instância da aplicação Qt."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


# Fixture para o widget de lista de duplicatas
@pytest.fixture
def duplicate_list_widget(app):
    """Fixture que cria uma instância do widget de lista de duplicatas."""
    widget = DuplicateListWidget()
    yield widget
    widget.deleteLater()


# Fixture para criar um conjunto de duplicatas de teste
@pytest.fixture
def duplicate_set():
    """Fixture que cria um conjunto de duplicatas de teste."""
    file1 = FileInfo(
        path=Path("/test/file1.jpg"),
        size=1024,
        hash="abc123",
        creation_time=1609459200.0,  # 2021-01-01
        modification_time=1609459200.0
    )

    file2 = FileInfo(
        path=Path("/test/file2.jpg"),
        size=1024,
        hash="abc123",
        creation_time=1609545600.0,  # 2021-01-02
        modification_time=1609545600.0
    )

    return DuplicateSet(
        files=[file1, file2],
        hash="abc123"
    )


class TestDuplicateListWidget:
    """Testes para o widget de lista de duplicatas."""

    def test_init(self, duplicate_list_widget):
        """Testa a inicialização do widget."""
        # Verificar se o widget foi criado corretamente
        assert duplicate_list_widget._tree_widget is not None
        assert duplicate_list_widget._file_info_widget is not None
        assert duplicate_list_widget._process_button is not None
        assert duplicate_list_widget._process_button.isEnabled() is False

    def test_set_duplicate_sets(self, duplicate_list_widget, duplicate_set):
        """Testa a definição de conjuntos de duplicatas."""
        # Configurar mock para _populate_tree
        duplicate_list_widget._populate_tree = MagicMock()

        # Chamar método
        duplicate_list_widget.set_duplicate_sets([duplicate_set])

        # Verificar que os conjuntos foram armazenados
        assert duplicate_list_widget._duplicate_sets == [duplicate_set]

        # Verificar que _populate_tree foi chamado
        duplicate_list_widget._populate_tree.assert_called_once()

    def test_populate_tree(self, duplicate_list_widget, duplicate_set):
        """Testa o preenchimento da árvore com conjuntos de duplicatas."""
        # Configurar mock para clear
        duplicate_list_widget._tree_widget.clear = MagicMock()

        # Armazenar conjunto de duplicatas
        duplicate_list_widget._duplicate_sets = [duplicate_set]

        # Chamar método
        duplicate_list_widget._populate_tree()

        # Verificar que clear foi chamado
        duplicate_list_widget._tree_widget.clear.assert_called_once()

    def test_populate_tree_with_selected_file(self, duplicate_list_widget, duplicate_set):
        """Testa o preenchimento da árvore com um arquivo selecionado para manter."""
        # Definir um arquivo selecionado no conjunto de duplicatas
        duplicate_set.selected_file = duplicate_set.files[0]

        # Armazenar conjunto de duplicatas
        duplicate_list_widget._duplicate_sets = [duplicate_set]

        # Criar um mock para QTreeWidgetItem.setBackground
        with patch('fotix.ui.widgets.duplicate_list_widget.QTreeWidgetItem') as mock_item:
            # Criar um mock para o método setBackground
            mock_instance = MagicMock()
            mock_item.return_value = mock_instance

            # Chamar o método
            duplicate_list_widget._populate_tree()

            # Verificar que o método setBackground foi chamado pelo menos uma vez
            # com os parâmetros corretos
            mock_instance.setBackground.assert_any_call(0, Qt.GlobalColor.green)


    def test_format_size(self, duplicate_list_widget):
        """Testa a formatação de tamanho em bytes."""
        # Testar diferentes tamanhos
        assert duplicate_list_widget._format_size(500) == "500 B"
        assert duplicate_list_widget._format_size(1500) == "1.5 KB"
        assert duplicate_list_widget._format_size(1500000) == "1.4 MB"
        assert duplicate_list_widget._format_size(1500000000) == "1.4 GB"

    @patch('fotix.ui.widgets.duplicate_list_widget.QMessageBox.question')
    def test_on_process_clicked_canceled(self, mock_message_box, duplicate_list_widget, duplicate_set):
        """Testa o clique no botão de processar quando o usuário cancela."""
        # Configurar mocks
        mock_message_box.return_value = QMessageBox.StandardButton.No
        duplicate_list_widget.process_duplicate = MagicMock()

        # Configurar estado
        duplicate_list_widget._current_duplicate_set = duplicate_set
        duplicate_list_widget._current_file = duplicate_set.files[0]

        # Chamar método
        duplicate_list_widget._on_process_clicked()

        # Verificar que a mensagem foi exibida
        mock_message_box.assert_called_once()

        # Verificar que o sinal não foi emitido
        duplicate_list_widget.process_duplicate.emit.assert_not_called()

    @patch('fotix.ui.widgets.duplicate_list_widget.QMessageBox.question')
    def test_on_process_clicked_confirmed(self, mock_message_box, duplicate_list_widget, duplicate_set):
        """Testa o clique no botão de processar quando o usuário confirma."""
        # Configurar mocks
        mock_message_box.return_value = QMessageBox.StandardButton.Yes
        duplicate_list_widget.process_duplicate = MagicMock()

        # Configurar estado
        duplicate_list_widget._current_duplicate_set = duplicate_set
        duplicate_list_widget._current_file = duplicate_set.files[0]

        # Chamar método
        duplicate_list_widget._on_process_clicked()

        # Verificar que a mensagem foi exibida
        mock_message_box.assert_called_once()

        # Verificar que o sinal foi emitido
        duplicate_list_widget.process_duplicate.emit.assert_called_once_with(
            duplicate_set, duplicate_set.files[0]
        )

    def test_on_selection_changed_no_selection(self, duplicate_list_widget):
        """Testa a mudança de seleção quando não há itens selecionados."""
        # Configurar mock
        duplicate_list_widget._tree_widget.selectedItems = MagicMock(return_value=[])
        duplicate_list_widget.duplicate_selected = MagicMock()
        duplicate_list_widget.file_selected = MagicMock()

        # Chamar método
        duplicate_list_widget._on_selection_changed()

        # Verificar que nenhum sinal foi emitido
        duplicate_list_widget.duplicate_selected.emit.assert_not_called()
        duplicate_list_widget.file_selected.emit.assert_not_called()

    def test_on_selection_changed_duplicate_set(self, duplicate_list_widget, duplicate_set):
        """Testa a mudança de seleção para um conjunto de duplicatas."""
        # Criar item mock
        item = MagicMock()
        item.data.return_value = duplicate_set

        # Configurar mock
        duplicate_list_widget._tree_widget.selectedItems = MagicMock(return_value=[item])
        duplicate_list_widget.duplicate_selected = MagicMock()
        duplicate_list_widget._file_info_widget.clear = MagicMock()

        # Chamar método
        duplicate_list_widget._on_selection_changed()

        # Verificar que o sinal foi emitido
        duplicate_list_widget.duplicate_selected.emit.assert_called_once_with(duplicate_set)

        # Verificar que o widget de informações foi limpo
        duplicate_list_widget._file_info_widget.clear.assert_called_once()

        # Verificar que o botão de processar está desabilitado
        assert duplicate_list_widget._process_button.isEnabled() is False

    def test_on_selection_changed_file_info(self, duplicate_list_widget, duplicate_set):
        """Testa a mudança de seleção para um arquivo."""
        # Criar item mock para o arquivo
        file_item = MagicMock()
        file_item.data.return_value = duplicate_set.files[0]

        # Criar item mock para o pai (conjunto de duplicatas)
        parent_item = MagicMock()
        parent_item.data.return_value = duplicate_set
        file_item.parent.return_value = parent_item

        # Configurar mock
        duplicate_list_widget._tree_widget.selectedItems = MagicMock(return_value=[file_item])
        duplicate_list_widget.file_selected = MagicMock()
        duplicate_list_widget._file_info_widget.set_file_info = MagicMock()

        # Chamar método
        duplicate_list_widget._on_selection_changed()

        # Verificar que o sinal foi emitido
        duplicate_list_widget.file_selected.emit.assert_called_once_with(duplicate_set.files[0])

        # Verificar que o widget de informações foi atualizado
        duplicate_list_widget._file_info_widget.set_file_info.assert_called_once_with(duplicate_set.files[0])

        # Verificar que o botão de processar está habilitado
        assert duplicate_list_widget._process_button.isEnabled() is True

    def test_toggle_expand_item(self, duplicate_list_widget):
        """Testa a alternância de expansão de um item."""
        # Criar item mock
        item = MagicMock()

        # Testar expansão quando o item está colapsado
        item.isExpanded.return_value = False
        duplicate_list_widget._toggle_expand_item(item)
        item.setExpanded.assert_called_once_with(True)

        # Resetar mock
        item.reset_mock()

        # Testar colapso quando o item está expandido
        item.isExpanded.return_value = True
        duplicate_list_widget._toggle_expand_item(item)
        item.setExpanded.assert_called_once_with(False)

    def test_refresh(self, duplicate_list_widget):
        """Testa a atualização da exibição."""
        # Configurar mock
        duplicate_list_widget._populate_tree = MagicMock()

        # Chamar método
        duplicate_list_widget.refresh()

        # Verificar que _populate_tree foi chamado
        duplicate_list_widget._populate_tree.assert_called_once()

    def test_on_item_double_clicked(self, duplicate_list_widget):
        """Testa o duplo clique em um item."""
        # Configurar mocks
        duplicate_list_widget.process_duplicate = MagicMock()

        # Criar item de teste para FileInfo
        file_info = MagicMock(spec=FileInfo)
        file_info.path = MagicMock()
        file_info.path.name = "test.jpg"

        # Configurar mock para item
        item = MagicMock()
        item.data.return_value = file_info

        # Criar item pai para DuplicateSet
        duplicate_set = MagicMock(spec=DuplicateSet)
        parent_item = MagicMock()
        parent_item.data.return_value = duplicate_set
        item.parent.return_value = parent_item

        # Configurar mock para QMessageBox.question
        with patch('fotix.ui.widgets.duplicate_list_widget.QMessageBox.question') as mock_question:
            mock_question.return_value = QMessageBox.StandardButton.Yes

            # Chamar método
            duplicate_list_widget._on_item_double_clicked(item, 0)

            # Verificar que a caixa de diálogo foi exibida
            mock_question.assert_called_once()

            # Verificar que o sinal foi emitido
            duplicate_list_widget.process_duplicate.emit.assert_called_once_with(duplicate_set, file_info)

    def test_on_item_double_clicked_canceled(self, duplicate_list_widget):
        """Testa o duplo clique em um item quando o usuário cancela."""
        # Configurar mocks
        duplicate_list_widget.process_duplicate = MagicMock()

        # Criar item de teste para FileInfo
        file_info = MagicMock(spec=FileInfo)
        file_info.path = MagicMock()
        file_info.path.name = "test.jpg"

        # Configurar mock para item
        item = MagicMock()
        item.data.return_value = file_info

        # Criar item pai para DuplicateSet
        duplicate_set = MagicMock(spec=DuplicateSet)
        parent_item = MagicMock()
        parent_item.data.return_value = duplicate_set
        item.parent.return_value = parent_item

        # Configurar mock para QMessageBox.question
        with patch('fotix.ui.widgets.duplicate_list_widget.QMessageBox.question') as mock_question:
            mock_question.return_value = QMessageBox.StandardButton.No

            # Chamar método
            duplicate_list_widget._on_item_double_clicked(item, 0)

            # Verificar que a caixa de diálogo foi exibida
            mock_question.assert_called_once()

            # Verificar que o sinal não foi emitido
            duplicate_list_widget.process_duplicate.emit.assert_not_called()

    def test_on_item_double_clicked_not_file_info(self, duplicate_list_widget):
        """Testa o duplo clique em um item que não é FileInfo."""
        # Configurar mocks
        duplicate_list_widget.process_duplicate = MagicMock()

        # Criar item de teste que não é FileInfo
        item = MagicMock()
        item.data.return_value = "not a file info"

        # Chamar método
        duplicate_list_widget._on_item_double_clicked(item, 0)

        # Verificar que o sinal não foi emitido
        duplicate_list_widget.process_duplicate.emit.assert_not_called()

    @patch('fotix.ui.widgets.duplicate_list_widget.QMenu')
    @patch('fotix.ui.widgets.duplicate_list_widget.QAction')
    def test_show_context_menu(self, mock_action_class, mock_menu_class, duplicate_list_widget):
        """Testa a exibição do menu de contexto."""
        # Configurar mocks
        mock_menu = MagicMock()
        mock_menu_class.return_value = mock_menu

        mock_action = MagicMock()
        mock_action_class.return_value = mock_action

        # Criar item de teste para FileInfo
        file_info = MagicMock(spec=FileInfo)
        file_info.path = MagicMock()
        file_info.path.name = "test.jpg"

        # Criar mock para o item
        mock_item = MagicMock()
        mock_item.data.return_value = file_info

        # Configurar mock para QTreeWidget.itemAt
        duplicate_list_widget._tree_widget.itemAt = MagicMock(return_value=mock_item)

        # Configurar mock para QTreeWidget.viewport
        mock_viewport = MagicMock()
        mock_viewport.mapToGlobal = MagicMock(return_value=MagicMock())
        duplicate_list_widget._tree_widget.viewport = MagicMock(return_value=mock_viewport)

        # Configurar mock para actions
        mock_menu.actions.return_value = [mock_action]

        # Chamar método
        duplicate_list_widget._show_context_menu(MagicMock())

        # Verificar que o menu foi criado e exibido
        mock_menu_class.assert_called_once()
        mock_menu.addAction.assert_called_once()
        mock_menu.exec.assert_called_once()

    def test_on_keep_file(self, duplicate_list_widget):
        """Testa a ação de manter um arquivo."""
        # Configurar mocks
        duplicate_list_widget.process_duplicate = MagicMock()

        # Criar objetos de teste
        file_info = MagicMock(spec=FileInfo)
        file_info.path = MagicMock()
        file_info.path.name = "test.jpg"

        duplicate_set = MagicMock(spec=DuplicateSet)
        duplicate_list_widget._current_duplicate_set = duplicate_set

        # Configurar mock para QMessageBox.question
        with patch('fotix.ui.widgets.duplicate_list_widget.QMessageBox.question') as mock_question:
            mock_question.return_value = QMessageBox.StandardButton.Yes

            # Chamar método
            duplicate_list_widget._on_keep_file(file_info)

            # Verificar que a caixa de diálogo foi exibida
            mock_question.assert_called_once()

            # Verificar que o sinal foi emitido
            duplicate_list_widget.process_duplicate.emit.assert_called_once_with(duplicate_set, file_info)

    def test_on_keep_file_canceled(self, duplicate_list_widget):
        """Testa a ação de manter um arquivo quando o usuário cancela."""
        # Configurar mocks
        duplicate_list_widget.process_duplicate = MagicMock()

        # Criar objetos de teste
        file_info = MagicMock(spec=FileInfo)
        file_info.path = MagicMock()
        file_info.path.name = "test.jpg"

        duplicate_set = MagicMock(spec=DuplicateSet)
        duplicate_list_widget._current_duplicate_set = duplicate_set

        # Configurar mock para QMessageBox.question
        with patch('fotix.ui.widgets.duplicate_list_widget.QMessageBox.question') as mock_question:
            mock_question.return_value = QMessageBox.StandardButton.No

            # Chamar método
            duplicate_list_widget._on_keep_file(file_info)

            # Verificar que a caixa de diálogo foi exibida
            mock_question.assert_called_once()

            # Verificar que o sinal não foi emitido
            duplicate_list_widget.process_duplicate.emit.assert_not_called()

    def test_on_keep_file_no_duplicate_set(self, duplicate_list_widget):
        """Testa a ação de manter um arquivo quando não há conjunto de duplicatas selecionado."""
        # Configurar mocks
        duplicate_list_widget.process_duplicate = MagicMock()

        # Criar objetos de teste
        file_info = MagicMock(spec=FileInfo)
        file_info.path = MagicMock()
        duplicate_list_widget._current_duplicate_set = None

        # Chamar método
        duplicate_list_widget._on_keep_file(file_info)

        # Verificar que o sinal não foi emitido
        duplicate_list_widget.process_duplicate.emit.assert_not_called()

    @patch('fotix.ui.widgets.duplicate_list_widget.QMenu')
    @patch('fotix.ui.widgets.duplicate_list_widget.QAction')
    def test_show_context_menu_duplicate_set(self, mock_action_class, mock_menu_class, duplicate_list_widget):
        """Testa a exibição do menu de contexto para um conjunto de duplicatas."""
        # Configurar mocks
        mock_menu = MagicMock()
        mock_menu_class.return_value = mock_menu

        mock_action = MagicMock()
        mock_action_class.return_value = mock_action

        # Criar item de teste para DuplicateSet
        duplicate_set = MagicMock(spec=DuplicateSet)

        # Criar mock para o item
        mock_item = MagicMock()
        mock_item.data.return_value = duplicate_set

        # Configurar mock para QTreeWidget.itemAt
        duplicate_list_widget._tree_widget.itemAt = MagicMock(return_value=mock_item)

        # Configurar mock para QTreeWidget.viewport
        mock_viewport = MagicMock()
        mock_viewport.mapToGlobal = MagicMock(return_value=MagicMock())
        duplicate_list_widget._tree_widget.viewport = MagicMock(return_value=mock_viewport)

        # Configurar mock para actions
        mock_menu.actions.return_value = [mock_action]

        # Chamar método
        duplicate_list_widget._show_context_menu(MagicMock())

        # Verificar que o menu foi criado e exibido
        mock_menu_class.assert_called_once()
        mock_menu.addAction.assert_called_once()
        mock_menu.exec.assert_called_once()

    @patch('fotix.ui.widgets.duplicate_list_widget.QMenu')
    def test_show_context_menu_no_item(self, mock_menu_class, duplicate_list_widget):
        """Testa a exibição do menu de contexto quando não há item selecionado."""
        # Configurar mock para QTreeWidget.itemAt
        duplicate_list_widget._tree_widget.itemAt = MagicMock(return_value=None)

        # Chamar método
        duplicate_list_widget._show_context_menu(MagicMock())

        # Verificar que o menu não foi criado
        mock_menu_class.assert_not_called()

    @patch('fotix.ui.widgets.duplicate_list_widget.QMenu')
    def test_show_context_menu_unknown_data(self, mock_menu_class, duplicate_list_widget):
        """Testa a exibição do menu de contexto quando o item tem dados desconhecidos."""
        # Configurar mocks
        mock_menu = MagicMock()
        mock_menu_class.return_value = mock_menu

        # Criar mock para o item com dados desconhecidos
        mock_item = MagicMock()
        mock_item.data.return_value = "unknown data"

        # Configurar mock para QTreeWidget.itemAt
        duplicate_list_widget._tree_widget.itemAt = MagicMock(return_value=mock_item)

        # Configurar mock para QTreeWidget.viewport
        mock_viewport = MagicMock()
        mock_viewport.mapToGlobal = MagicMock(return_value=MagicMock())
        duplicate_list_widget._tree_widget.viewport = MagicMock(return_value=mock_viewport)

        # Configurar mock para actions
        mock_menu.actions.return_value = []

        # Chamar método
        duplicate_list_widget._show_context_menu(MagicMock())

        # Verificar que o menu foi criado mas não foi exibido
        mock_menu_class.assert_called_once()
        mock_menu.exec.assert_not_called()

    @patch('fotix.ui.widgets.duplicate_list_widget.QMenu')
    def test_show_context_menu_file_info_with_parent(self, mock_menu_class, duplicate_list_widget):
        """Testa a exibição do menu de contexto para um FileInfo com um pai DuplicateSet."""
        # Configurar mocks
        mock_menu = MagicMock()
        mock_menu_class.return_value = mock_menu

        # Criar item de teste para FileInfo
        file_info = MagicMock(spec=FileInfo)
        file_info.path = MagicMock()
        file_info.path.name = "test.jpg"

        # Criar mock para o item
        mock_item = MagicMock()
        mock_item.data.return_value = file_info

        # Criar item pai para DuplicateSet
        duplicate_set = MagicMock(spec=DuplicateSet)
        parent_item = MagicMock()
        parent_item.data.return_value = duplicate_set
        mock_item.parent.return_value = parent_item

        # Configurar mock para QTreeWidget.itemAt
        duplicate_list_widget._tree_widget.itemAt = MagicMock(return_value=mock_item)

        # Configurar mock para QTreeWidget.viewport
        mock_viewport = MagicMock()
        mock_viewport.mapToGlobal = MagicMock(return_value=MagicMock())
        duplicate_list_widget._tree_widget.viewport = MagicMock(return_value=mock_viewport)

        # Configurar mock para actions
        mock_menu.actions.return_value = [MagicMock()]

        # Chamar método
        duplicate_list_widget._show_context_menu(MagicMock())

        # Verificar que o menu foi criado e exibido
        mock_menu_class.assert_called_once()
        mock_menu.addAction.assert_called_once()
        mock_menu.exec.assert_called_once()

        # Verificar que o conjunto de duplicatas atual foi definido
        assert duplicate_list_widget._current_duplicate_set == duplicate_set
