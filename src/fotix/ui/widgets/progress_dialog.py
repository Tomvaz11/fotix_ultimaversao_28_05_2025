"""
Diálogo de progresso para operações longas.

Este módulo implementa um diálogo de progresso para exibir o andamento de
operações longas, como varredura de diretórios, processamento de duplicatas, etc.
"""

from typing import Optional, Callable

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QProgressBar,
    QLabel, QPushButton, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer


class ProgressDialog(QDialog):
    """
    Diálogo de progresso para operações longas.
    
    Este diálogo exibe uma barra de progresso e uma mensagem para informar
    o usuário sobre o andamento de uma operação longa.
    
    Signals:
        canceled: Emitido quando o usuário cancela a operação.
    """
    
    # Sinais
    canceled = Signal()
    
    def __init__(
        self,
        title: str,
        message: str,
        parent: Optional[QDialog] = None,
        cancelable: bool = True,
        auto_close: bool = True
    ):
        """
        Inicializa o diálogo de progresso.
        
        Args:
            title: Título do diálogo.
            message: Mensagem inicial.
            parent: Widget pai opcional.
            cancelable: Se True, exibe um botão para cancelar a operação.
            auto_close: Se True, fecha automaticamente o diálogo quando o progresso chegar a 100%.
        """
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self.setModal(True)
        
        self._message = message
        self._cancelable = cancelable
        self._auto_close = auto_close
        self._callback: Optional[Callable[[float], None]] = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura a interface do usuário."""
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Mensagem
        self._message_label = QLabel(self._message)
        self._message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._message_label)
        
        # Barra de progresso
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        layout.addWidget(self._progress_bar)
        
        # Detalhes
        self._details_label = QLabel()
        self._details_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._details_label)
        
        # Botões
        button_layout = QHBoxLayout()
        
        if self._cancelable:
            self._cancel_button = QPushButton("Cancelar")
            self._cancel_button.clicked.connect(self._on_cancel_clicked)
            button_layout.addWidget(self._cancel_button)
        
        layout.addLayout(button_layout)
    
    def set_progress(self, value: float, details: Optional[str] = None):
        """
        Define o valor atual do progresso.
        
        Args:
            value: Valor do progresso (0.0 a 1.0).
            details: Detalhes opcionais sobre o progresso atual.
        """
        # Converter para porcentagem
        percent = int(value * 100)
        
        # Atualizar barra de progresso
        self._progress_bar.setValue(percent)
        
        # Atualizar detalhes
        if details:
            self._details_label.setText(details)
        else:
            self._details_label.setText(f"{percent}%")
        
        # Fechar automaticamente se o progresso chegar a 100%
        if self._auto_close and percent >= 100:
            # Usar um timer para fechar após um breve atraso
            QTimer.singleShot(500, self.accept)
    
    def set_message(self, message: str):
        """
        Define a mensagem principal.
        
        Args:
            message: Nova mensagem.
        """
        self._message = message
        self._message_label.setText(message)
    
    def get_callback(self) -> Callable[[float], None]:
        """
        Retorna uma função de callback para atualizar o progresso.
        
        Esta função pode ser passada para métodos que aceitam um callback
        de progresso, como ScanService.scan_directories().
        
        Returns:
            Callable[[float], None]: Função de callback.
        """
        if not self._callback:
            def callback(value: float):
                self.set_progress(value)
            self._callback = callback
        
        return self._callback
    
    @Slot()
    def _on_cancel_clicked(self):
        """Manipula o clique no botão de cancelar."""
        self.canceled.emit()
        self.reject()
    
    def closeEvent(self, event):
        """
        Manipula o evento de fechamento do diálogo.
        
        Args:
            event: Evento de fechamento.
        """
        if self._cancelable:
            self.canceled.emit()
        super().closeEvent(event)
