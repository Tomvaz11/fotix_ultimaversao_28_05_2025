"""
Widget para exibição de informações detalhadas de arquivos.

Este módulo implementa um widget personalizado para exibir informações detalhadas
sobre um arquivo, como nome, caminho, tamanho, datas de criação e modificação.
"""

from typing import Optional, Tuple, Callable, List
from datetime import datetime
import io

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QFrame,
    QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt
from PIL import Image

from fotix.core.models import FileInfo
from fotix.utils.image_utils import get_image_resolution


def get_image_resolution_from_bytes(content_provider: Callable[[], List[bytes]]) -> Optional[Tuple[int, int]]:
    """
    Obtém a resolução de uma imagem a partir de bytes.

    Args:
        content_provider: Função que retorna o conteúdo do arquivo em bytes.

    Returns:
        Tuple[int, int]: Resolução da imagem (largura, altura) ou None se não for possível obter.
    """
    try:
        content = content_provider()
        if not content:
            return None

        # Concatenar todos os chunks de bytes
        buffer = io.BytesIO(b''.join(content))

        # Abrir imagem com PIL
        with Image.open(buffer) as img:
            return img.size
    except Exception:
        return None


class FileInfoWidget(QWidget):
    """
    Widget para exibição de informações detalhadas de arquivos.

    Este widget exibe informações detalhadas sobre um arquivo, como nome,
    caminho, tamanho, datas de criação e modificação.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Inicializa o widget de informações de arquivo.

        Args:
            parent: Widget pai opcional.
        """
        super().__init__(parent)

        self._setup_ui()

    def _setup_ui(self):
        """Configura a interface do usuário."""
        # Layout principal
        main_layout = QVBoxLayout(self)

        # Título
        self._title_label = QLabel("Informações do Arquivo")
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        # Área de rolagem para o conteúdo
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Widget de conteúdo
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)

        # Layout de formulário para as informações
        self._form_layout = QFormLayout(content_widget)
        self._form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Campos de informação
        self._name_label = QLabel()
        self._path_label = QLabel()
        self._path_label.setWordWrap(True)
        self._size_label = QLabel()
        self._hash_label = QLabel()
        self._creation_time_label = QLabel()
        self._modification_time_label = QLabel()
        self._in_zip_label = QLabel()
        self._zip_path_label = QLabel()
        self._zip_path_label.setWordWrap(True)
        self._resolution_label = QLabel()

        # Adicionar campos ao layout
        self._form_layout.addRow("Nome:", self._name_label)
        self._form_layout.addRow("Caminho:", self._path_label)
        self._form_layout.addRow("Tamanho:", self._size_label)
        self._form_layout.addRow("Hash:", self._hash_label)
        self._form_layout.addRow("Criação:", self._creation_time_label)
        self._form_layout.addRow("Modificação:", self._modification_time_label)
        self._form_layout.addRow("Em ZIP:", self._in_zip_label)
        self._form_layout.addRow("Caminho ZIP:", self._zip_path_label)
        self._form_layout.addRow("Resolução:", self._resolution_label)

        # Adicionar widgets ao layout principal
        main_layout.addWidget(self._title_label)
        main_layout.addWidget(scroll_area)

        # Limpar os campos
        self.clear()

    def set_file_info(self, file_info: FileInfo):
        """
        Define as informações do arquivo a serem exibidas.

        Args:
            file_info: Informações do arquivo.
        """
        # Nome do arquivo
        self._name_label.setText(file_info.filename)

        # Caminho do arquivo
        self._path_label.setText(str(file_info.path))

        # Tamanho do arquivo
        self._size_label.setText(self._format_size(file_info.size))

        # Hash do arquivo
        self._hash_label.setText(file_info.hash if file_info.hash else "N/A")

        # Data de criação
        if file_info.creation_datetime:
            self._creation_time_label.setText(
                file_info.creation_datetime.strftime("%d/%m/%Y %H:%M:%S")
            )
        else:
            self._creation_time_label.setText("N/A")

        # Data de modificação
        if file_info.modification_datetime:
            self._modification_time_label.setText(
                file_info.modification_datetime.strftime("%d/%m/%Y %H:%M:%S")
            )
        else:
            self._modification_time_label.setText("N/A")

        # Em ZIP
        self._in_zip_label.setText("Sim" if file_info.in_zip else "Não")

        # Caminho ZIP
        if file_info.in_zip and file_info.zip_path:
            self._zip_path_label.setText(f"{file_info.zip_path} -> {file_info.internal_path}")
        else:
            self._zip_path_label.setText("N/A")

        # Resolução (para imagens)
        resolution = None
        if file_info.path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            if file_info.in_zip and file_info.content_provider:
                # Obter resolução a partir do conteúdo do arquivo em ZIP
                resolution = get_image_resolution_from_bytes(file_info.content_provider)
            else:
                # Obter resolução a partir do arquivo no sistema de arquivos
                resolution = get_image_resolution(file_info.path)

        if resolution:
            self._resolution_label.setText(f"{resolution[0]} x {resolution[1]}")
        else:
            self._resolution_label.setText("N/A")

    def clear(self):
        """Limpa as informações exibidas."""
        self._name_label.setText("N/A")
        self._path_label.setText("N/A")
        self._size_label.setText("N/A")
        self._hash_label.setText("N/A")
        self._creation_time_label.setText("N/A")
        self._modification_time_label.setText("N/A")
        self._in_zip_label.setText("N/A")
        self._zip_path_label.setText("N/A")
        self._resolution_label.setText("N/A")

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
