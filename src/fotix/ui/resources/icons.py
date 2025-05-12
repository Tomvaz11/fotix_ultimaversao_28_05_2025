"""
Ícones para a interface gráfica do Fotix.

Este módulo fornece acesso aos ícones utilizados na interface gráfica do Fotix.
Os ícones são carregados a partir de recursos embutidos ou do sistema.
"""

from pathlib import Path
from typing import Dict, Optional

from PySide6.QtGui import QIcon
from PySide6.QtCore import QDir
from PySide6.QtWidgets import QStyle, QApplication

# Diretório base para ícones
_ICONS_DIR = Path(__file__).parent / "icons"

# Cache de ícones
_icon_cache: Dict[str, QIcon] = {}


def get_icon(name: str) -> QIcon:
    """
    Obtém um ícone pelo nome.

    Esta função tenta carregar o ícone a partir do diretório de recursos.
    Se o ícone não for encontrado, retorna um ícone padrão do sistema.

    Args:
        name: Nome do ícone (sem extensão).

    Returns:
        QIcon: O ícone carregado.
    """
    # Verificar se o ícone já está em cache
    if name in _icon_cache:
        return _icon_cache[name]

    # Tentar carregar o ícone a partir do diretório de recursos
    icon_path = _ICONS_DIR / f"{name}.png"
    if icon_path.exists():
        icon = QIcon(str(icon_path))
    else:
        # Usar ícone do sistema se o ícone não for encontrado
        icon = QIcon.fromTheme(name)

    # Armazenar em cache
    _icon_cache[name] = icon

    return icon


def get_standard_icon(icon_type: QStyle.StandardPixmap) -> QIcon:
    """
    Obtém um ícone padrão do sistema.

    Args:
        icon_type: Tipo de ícone padrão.

    Returns:
        QIcon: O ícone padrão.
    """
    app = QApplication.instance()
    if app is None:
        # Se não houver uma instância de QApplication, criar uma temporária
        import sys
        app = QApplication(sys.argv)

    return app.style().standardIcon(icon_type)


# Ícones comuns
ICON_APP = get_icon("app")
ICON_FOLDER = get_standard_icon(QStyle.SP_DirIcon)
ICON_FILE = get_standard_icon(QStyle.SP_FileIcon)
ICON_SCAN = get_icon("scan")
ICON_DUPLICATE = get_icon("duplicate")
ICON_SETTINGS = get_standard_icon(QStyle.SP_FileDialogDetailedView)
ICON_BACKUP = get_icon("backup")
ICON_RESTORE = get_icon("restore")
ICON_DELETE = get_standard_icon(QStyle.SP_TrashIcon)
ICON_HELP = get_standard_icon(QStyle.SP_MessageBoxQuestion)
ICON_EXIT = get_standard_icon(QStyle.SP_DialogCloseButton)
