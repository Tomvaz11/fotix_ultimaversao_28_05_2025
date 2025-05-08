"""
Script de depuração para verificar todos os aspectos do módulo de logging.
"""

import os
import sys
import importlib
import traceback
from pathlib import Path

# Verifica a versão do Python
print(f"Python version: {sys.version}")

# Verifica o local onde o script está sendo executado
print(f"Working directory: {os.getcwd()}")

# Verificando estrutura de diretórios
print("\nVerificando estrutura de diretórios:")
directories = [
    "src/fotix",
    "src/fotix/infrastructure",
    "tests/unit",
    "tests/unit/fotix",
    "tests/unit/fotix/infrastructure"
]

for directory in directories:
    path = Path(directory)
    print(f"  {directory}: {'Existe' if path.exists() else 'Não existe'}")
    if path.exists():
        init_file = path / "__init__.py"
        print(f"    __init__.py: {'Existe' if init_file.exists() else 'Não existe'}")
        if init_file.exists():
            with open(init_file, 'rb') as f:
                content = f.read()
                print(f"      Tamanho: {len(content)} bytes")
                if b'\x00' in content:
                    print(f"      ALERTA: Arquivo contém bytes nulos!")

# Verifica se o módulo está no PYTHONPATH
print("\nVerificando PYTHONPATH:")
print(f"  sys.path: {sys.path}")

# Tenta importar o módulo
print("\nTentando importar módulos:")
modules_to_test = [
    "fotix",
    "fotix.config",
    "fotix.infrastructure",
    "fotix.infrastructure.logging_config"
]

for module_name in modules_to_test:
    print(f"\nImportando {module_name}...")
    try:
        module = importlib.import_module(module_name)
        print(f"  Importação bem-sucedida: {module}")
        print(f"  Localização: {getattr(module, '__file__', 'Desconhecida')}")
    except Exception as e:
        print(f"  ERRO: {e}")
        traceback.print_exc()

# Se chegou até aqui, tenta usar o módulo de logging
print("\nTentando usar o módulo de logging_config...")
try:
    from fotix.infrastructure.logging_config import setup_logging, get_logger, update_log_level
    print("  Importação do logging_config bem-sucedida")
    
    # Configura um arquivo de log temporário
    temp_log_file = Path("temp_test.log")
    print(f"  Configurando log para o arquivo: {temp_log_file.absolute()}")
    
    # Tenta configurar o logging
    logger_root = setup_logging(log_level="INFO", log_file=temp_log_file)
    print("  Configuração de logging bem-sucedida")
    
    # Obtém um logger
    logger = get_logger("debug_script")
    print("  Logger obtido com sucesso")
    
    # Testa diferentes níveis de log
    print("  Enviando mensagens com diferentes níveis:")
    logger.debug("Esta é uma mensagem DEBUG")
    logger.info("Esta é uma mensagem INFO")
    logger.warning("Esta é uma mensagem WARNING")
    logger.error("Esta é uma mensagem ERROR")
    
    # Altera o nível de log
    print("  Alterando nível de log para DEBUG")
    update_log_level("DEBUG")
    
    # Testa novamente
    logger.debug("Esta é uma mensagem DEBUG após a alteração do nível")
    
    # Verifica se o arquivo foi criado
    print(f"\nVerificando arquivo de log {temp_log_file}:")
    if temp_log_file.exists():
        print(f"  Arquivo criado com sucesso, tamanho: {temp_log_file.stat().st_size} bytes")
        print("  Conteúdo do arquivo:")
        with open(temp_log_file, 'r') as f:
            for line in f:
                print(f"    {line.rstrip()}")
    else:
        print(f"  ERRO: Arquivo não foi criado")
    
except Exception as e:
    print(f"  ERRO ao usar o módulo: {e}")
    traceback.print_exc()

print("\nDebug concluído.") 