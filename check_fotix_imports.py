import sys
import os
from pathlib import Path

# Constrói o caminho para o diretório \'src\'
# Supõe que este script está na raiz do projeto, e \'src\' está no mesmo nível.
project_root = Path(__file__).parent.resolve()
src_path = project_root / "src"

print(f"Tentando adicionar ao sys.path: {src_path}")
if src_path.exists() and src_path.is_dir():
    sys.path.insert(0, str(src_path))
    print(f"Conteúdo atual do sys.path (primeiros itens): {sys.path[:5]}")
else:
    print(f"ERRO: Diretório src não encontrado em {src_path}")
    sys.exit(1)

print("\nTentando importar fotix.config...")
try:
    import fotix.config
    print("SUCESSO: fotix.config importado.")
    print(f"Localização de fotix.config: {fotix.config.__file__}")
except ImportError as e:
    print(f"ERRO ao importar fotix.config: {e}")
except Exception as e:
    print(f"ERRO INESPERADO ao importar fotix.config: {e}")

print("\nTentando importar fotix.infrastructure.logging_config...")
try:
    import fotix.infrastructure.logging_config
    print("SUCESSO: fotix.infrastructure.logging_config importado.")
    print(f"Localização de fotix.infrastructure.logging_config: {fotix.infrastructure.logging_config.__file__}")
except ImportError as e:
    print(f"ERRO ao importar fotix.infrastructure.logging_config: {e}")
except Exception as e:
    print(f"ERRO INESPERADO ao importar fotix.infrastructure.logging_config: {e}")

print("\nTentando importar fotix.infrastructure.file_system...")
try:
    import fotix.infrastructure.file_system
    print("SUCESSO: fotix.infrastructure.file_system importado.")
    print(f"Localização de fotix.infrastructure.file_system: {fotix.infrastructure.file_system.__file__}")
except ImportError as e:
    print(f"ERRO ao importar fotix.infrastructure.file_system: {e}")
except Exception as e:
    print(f"ERRO INESPERADO ao importar fotix.infrastructure.file_system: {e}") 