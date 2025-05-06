"""
Script para executar os testes unitários do Fotix e salvar o resultado em um arquivo.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# Diretório do projeto
project_dir = Path(__file__).parent

# Arquivo de saída
output_file = project_dir / "test_results.txt"

# Remover o arquivo de saída se existir
if output_file.exists():
    os.remove(output_file)
    time.sleep(1)  # Aguardar um pouco para garantir que o arquivo foi removido

# Comando para executar os testes
command = [
    sys.executable,
    "-m",
    "pytest",
    "tests/unit/infrastructure/test_logging_config.py",
    "-v"
]

# Definir PYTHONPATH para incluir o diretório src
env = os.environ.copy()
env["PYTHONPATH"] = str(project_dir / "src") + os.pathsep + env.get("PYTHONPATH", "")

# Executar o comando e capturar a saída
try:
    result = subprocess.run(
        command,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False
    )

    # Salvar a saída em um arquivo
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result.stdout)

    # Exibir a saída também no console
    print(result.stdout)

    print(f"\nTestes executados. Resultado salvo em {output_file}")
    print(f"Código de saída: {result.returncode}")

except Exception as e:
    print(f"Erro ao executar os testes: {e}")
    sys.exit(1)

# Sair com o código de retorno dos testes
sys.exit(result.returncode)
