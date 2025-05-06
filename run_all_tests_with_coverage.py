"""
Script para executar todos os testes unitários do Fotix com cobertura.
Gera relatórios de cobertura em formato de terminal e HTML.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# Diretório do projeto
project_dir = Path(__file__).parent

# Arquivo de saída
output_file = project_dir / "test_coverage_results.txt"

# Remover o arquivo de saída se existir
if output_file.exists():
    os.remove(output_file)
    time.sleep(1)  # Aguardar um pouco para garantir que o arquivo foi removido

# Comando para executar os testes com cobertura
command = [
    sys.executable,
    "-m",
    "pytest",
    "tests",
    "-v",
    "--cov=fotix",
    "--cov-report=term-missing",
    "--cov-report=html"
]

# Definir PYTHONPATH para incluir o diretório src
env = os.environ.copy()
env["PYTHONPATH"] = str(project_dir / "src") + os.pathsep + env.get("PYTHONPATH", "")

print("Executando todos os testes com cobertura...")
print(f"Comando: {' '.join(command)}")
print("-" * 80)

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
    print(f"Relatório HTML de cobertura gerado em: {project_dir / 'htmlcov/index.html'}")
    print(f"Código de saída: {result.returncode}")

except Exception as e:
    print(f"Erro ao executar os testes: {e}")
    sys.exit(1)

# Sair com o código de retorno dos testes
sys.exit(result.returncode)
