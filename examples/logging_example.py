"""
Exemplo de uso do módulo de logging do Fotix.

Este script demonstra como configurar e usar o sistema de logging do Fotix.
"""

import tempfile
from pathlib import Path

from fotix.config import Config
from fotix.infrastructure.logging_config import configure_logging, get_logger


def main():
    """Função principal do exemplo."""
    # Cria um diretório temporário para os logs
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = Path(temp_dir)
        print(f"Logs serão gravados em: {log_dir}")
        
        # Configura o logging com saída para arquivo
        config = Config({
            'log_level': 'DEBUG',
            'log_to_file': True,
            'log_dir': str(log_dir)
        })
        configure_logging(config)
        
        # Obtém um logger para este módulo
        logger = get_logger(__name__)
        
        # Gera logs de diferentes níveis
        logger.debug("Esta é uma mensagem de DEBUG")
        logger.info("Esta é uma mensagem de INFO")
        logger.warning("Esta é uma mensagem de WARNING")
        logger.error("Esta é uma mensagem de ERROR")
        logger.critical("Esta é uma mensagem de CRITICAL")
        
        # Lista os arquivos de log gerados
        log_files = list(log_dir.glob('fotix_*.log'))
        print(f"\nArquivos de log gerados: {len(log_files)}")
        for log_file in log_files:
            print(f"- {log_file.name}")
            
            # Mostra o conteúdo do arquivo de log
            print("\nConteúdo do arquivo de log:")
            with open(log_file, 'r', encoding='utf-8') as f:
                print(f.read())


if __name__ == "__main__":
    main()
