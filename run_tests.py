"""
Script para executar os testes unitários do Fotix.
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório src ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pytest

if __name__ == "__main__":
    # Executar os testes
    result = pytest.main(["-v", "tests/unit/infrastructure/test_logging_config.py"])
    
    # Exibir o resultado
    print(f"\nResultado dos testes: {result}")
    
    # Sair com o código de retorno dos testes
    sys.exit(result)
