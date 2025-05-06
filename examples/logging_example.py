"""
Exemplo de uso do módulo de logging do Fotix.
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório src ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fotix.infrastructure.logging_config import get_logger, set_log_level
from fotix.config import get_config

# Obter um logger para este módulo
logger = get_logger("examples.logging_example")

def main():
    """Função principal do exemplo."""
    # Exibir mensagens de log em diferentes níveis
    logger.debug("Esta é uma mensagem de DEBUG")
    logger.info("Esta é uma mensagem de INFO")
    logger.warning("Esta é uma mensagem de WARNING")
    logger.error("Esta é uma mensagem de ERROR")
    logger.critical("Esta é uma mensagem de CRITICAL")
    
    # Alterar o nível de log para DEBUG
    print("\nAlterando o nível de log para DEBUG:")
    set_log_level("DEBUG")
    
    # Exibir mensagens de log novamente
    logger.debug("Esta é uma mensagem de DEBUG (agora visível)")
    logger.info("Esta é uma mensagem de INFO")
    
    # Obter e exibir as configurações de logging
    config = get_config()
    logging_config = config.get("logging")
    print("\nConfigurações de logging:")
    print(f"Nível global: {logging_config.get('level')}")
    print(f"Console habilitado: {logging_config.get('console', {}).get('enabled')}")
    print(f"Arquivo habilitado: {logging_config.get('file', {}).get('enabled')}")
    
    # Informar onde os logs estão sendo salvos
    log_dir = Path.home() / ".fotix" / "logs"
    log_file = log_dir / logging_config.get("file", {}).get("filename", "fotix.log")
    print(f"\nOs logs estão sendo salvos em: {log_file}")

if __name__ == "__main__":
    main()
