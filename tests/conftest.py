"""
Configuração para os testes do Fotix.
"""

import os
import sys
from pathlib import Path

# Obtém o caminho absoluto para o diretório raiz do projeto
root_dir = Path(__file__).parent.parent.absolute()
src_dir = root_dir / "fotix" / "src"

# Adiciona o diretório src ao PYTHONPATH
sys.path.insert(0, str(src_dir))
print(f"Adicionado ao PYTHONPATH: {src_dir}")

