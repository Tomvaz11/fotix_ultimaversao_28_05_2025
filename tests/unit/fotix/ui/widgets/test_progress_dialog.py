"""
Testes unitários para o diálogo de progresso.

Este módulo contém testes para verificar o funcionamento correto do diálogo
de progresso da aplicação Fotix.
"""

import sys
import pytest
from unittest.mock import MagicMock, patch

from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import Qt, QTimer

from fotix.ui.widgets.progress_dialog import ProgressDialog


# Fixture para a aplicação Qt
@pytest.fixture
def app():
    """Fixture que cria uma instância da aplicação Qt."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


# Fixture para o diálogo de progresso
@pytest.fixture
def progress_dialog(app):
    """Fixture que cria uma instância do diálogo de progresso."""
    dialog = ProgressDialog(
        title="Teste",
        message="Mensagem de teste",
        cancelable=True,
        auto_close=True
    )
    yield dialog
    dialog.reject()


# Fixture para o diálogo de progresso não cancelável
@pytest.fixture
def non_cancelable_dialog(app):
    """Fixture que cria uma instância do diálogo de progresso não cancelável."""
    dialog = ProgressDialog(
        title="Teste",
        message="Mensagem de teste",
        cancelable=False,
        auto_close=True
    )
    yield dialog
    dialog.reject()


class TestProgressDialog:
    """Testes para o diálogo de progresso."""

    def test_init(self, progress_dialog):
        """Testa a inicialização do diálogo."""
        # Verificar se o diálogo foi criado corretamente
        assert progress_dialog.windowTitle() == "Teste"
        assert progress_dialog._message == "Mensagem de teste"
        assert progress_dialog._cancelable is True
        assert progress_dialog._auto_close is True
        assert progress_dialog._callback is None

        # Verificar se os widgets foram criados
        assert progress_dialog._message_label is not None
        assert progress_dialog._progress_bar is not None
        assert progress_dialog._details_label is not None

    def test_init_non_cancelable(self, non_cancelable_dialog):
        """Testa a inicialização do diálogo não cancelável."""
        # Verificar se o diálogo foi criado corretamente
        assert non_cancelable_dialog._cancelable is False

        # Verificar que não há botão de cancelar
        assert not hasattr(non_cancelable_dialog, "_cancel_button")

    def test_set_progress(self, progress_dialog):
        """Testa a definição do valor de progresso."""
        # Chamar método
        progress_dialog.set_progress(0.5)

        # Verificar que a barra de progresso foi atualizada
        assert progress_dialog._progress_bar.value() == 50

        # Verificar que os detalhes foram atualizados
        assert progress_dialog._details_label.text() == "50%"

    def test_set_progress_with_details(self, progress_dialog):
        """Testa a definição do valor de progresso com detalhes."""
        # Chamar método
        progress_dialog.set_progress(0.75, "Processando arquivo 3 de 4")

        # Verificar que a barra de progresso foi atualizada
        assert progress_dialog._progress_bar.value() == 75

        # Verificar que os detalhes foram atualizados
        assert progress_dialog._details_label.text() == "Processando arquivo 3 de 4"

    @patch('fotix.ui.widgets.progress_dialog.QTimer.singleShot')
    def test_set_progress_auto_close(self, mock_timer, progress_dialog):
        """Testa a definição do valor de progresso com fechamento automático."""
        # Chamar método
        progress_dialog.set_progress(1.0)

        # Verificar que a barra de progresso foi atualizada
        assert progress_dialog._progress_bar.value() == 100

        # Verificar que o timer foi configurado
        mock_timer.assert_called_once()

    def test_set_message(self, progress_dialog):
        """Testa a definição da mensagem."""
        # Chamar método
        progress_dialog.set_message("Nova mensagem")

        # Verificar que a mensagem foi atualizada
        assert progress_dialog._message == "Nova mensagem"
        assert progress_dialog._message_label.text() == "Nova mensagem"

    def test_get_callback(self, progress_dialog):
        """Testa a obtenção da função de callback."""
        # Chamar método
        callback = progress_dialog.get_callback()

        # Verificar que o callback foi criado
        assert callback is not None
        assert progress_dialog._callback is not None
        assert progress_dialog._callback == callback

        # Testar o callback
        callback(0.25)
        assert progress_dialog._progress_bar.value() == 25

    def test_on_cancel_clicked(self, progress_dialog):
        """Testa o clique no botão de cancelar."""
        # Configurar mock
        progress_dialog.canceled = MagicMock()
        progress_dialog.reject = MagicMock()

        # Chamar método
        progress_dialog._on_cancel_clicked()

        # Verificar que o sinal foi emitido
        progress_dialog.canceled.emit.assert_called_once()

        # Verificar que o diálogo foi rejeitado
        progress_dialog.reject.assert_called_once()

    @patch('PySide6.QtWidgets.QDialog.closeEvent')
    def test_close_event_cancelable(self, mock_super_close, progress_dialog):
        """Testa o evento de fechamento do diálogo cancelável."""
        # Configurar mock
        progress_dialog.canceled = MagicMock()

        # Criar um evento de fechamento real
        from PySide6.QtGui import QCloseEvent
        event = QCloseEvent()

        # Chamar método
        progress_dialog.closeEvent(event)

        # Verificar que o sinal foi emitido
        progress_dialog.canceled.emit.assert_called_once()

        # Verificar que o método da classe pai foi chamado
        mock_super_close.assert_called_once()

    @patch('PySide6.QtWidgets.QDialog.closeEvent')
    def test_close_event_non_cancelable(self, mock_super_close, non_cancelable_dialog):
        """Testa o evento de fechamento do diálogo não cancelável."""
        # Configurar mock
        non_cancelable_dialog.canceled = MagicMock()

        # Criar um evento de fechamento real
        from PySide6.QtGui import QCloseEvent
        event = QCloseEvent()

        # Chamar método
        non_cancelable_dialog.closeEvent(event)

        # Verificar que o sinal não foi emitido
        non_cancelable_dialog.canceled.emit.assert_not_called()

        # Verificar que o método da classe pai foi chamado
        mock_super_close.assert_called_once()
