"""
Módulo de configuração de logging para o Fotix.

Este módulo é responsável por configurar o sistema de logging padrão do Python
para a aplicação Fotix, permitindo o registro de eventos e erros.
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Dict, Any, Union

from fotix.config import get_log_level, get_log_file


# Constantes para formatação de logs
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Tamanho máximo do arquivo de log (10 MB)
MAX_LOG_SIZE = 10 * 1024 * 1024

# Número máximo de arquivos de backup
BACKUP_COUNT = 5

# Singleton para controlar se o logging já foi configurado
_logging_configured = False


def configure_logging(
    log_level: Optional[Union[int, str]] = None,
    log_file: Optional[Union[str, Path]] = None,
    log_format: str = DEFAULT_LOG_FORMAT,
    date_format: str = DEFAULT_DATE_FORMAT,
    console_output: bool = True,
    file_output: bool = True,
    max_file_size: int = MAX_LOG_SIZE,
    backup_count: int = BACKUP_COUNT
) -> None:
    """
    Configura o sistema de logging do Python para a aplicação Fotix.
    
    Esta função configura o logger raiz para registrar mensagens no console e/ou
    em um arquivo, com rotação automática quando o tamanho máximo é atingido.
    
    Args:
        log_level: Nível de log (logging.DEBUG, logging.INFO, etc.) ou string 
                  correspondente. Se None, usa o valor de fotix.config.
        log_file: Caminho para o arquivo de log. Se None, usa o valor de fotix.config.
        log_format: Formato das mensagens de log.
        date_format: Formato da data/hora nas mensagens de log.
        console_output: Se True, envia logs para o console.
        file_output: Se True, envia logs para um arquivo.
        max_file_size: Tamanho máximo do arquivo de log antes da rotação.
        backup_count: Número máximo de arquivos de backup a manter.
    """
    global _logging_configured
    
    # Evita configurar o logging mais de uma vez
    if _logging_configured:
        return
    
    # Obtém o nível de log das configurações se não for especificado
    if log_level is None:
        log_level = get_log_level()
    elif isinstance(log_level, str):
        # Converte string para constante do logging
        log_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Obtém o caminho do arquivo de log das configurações se não for especificado
    if log_file is None:
        log_file = get_log_file()
    elif isinstance(log_file, str):
        log_file = Path(log_file)
    
    # Configura o logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove handlers existentes para evitar duplicação
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Cria o formatador
    formatter = logging.Formatter(log_format, date_format)
    
    # Adiciona handler para console se solicitado
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Adiciona handler para arquivo se solicitado
    if file_output and log_file:
        # Garante que o diretório do arquivo de log existe
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Marca o logging como configurado
    _logging_configured = True
    
    # Log inicial para confirmar a configuração
    logging.info(f"Logging configurado. Nível: {logging.getLevelName(log_level)}")


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger configurado para o módulo especificado.
    
    Se o logging ainda não foi configurado, configura-o automaticamente.
    
    Args:
        name: Nome do logger, geralmente __name__ do módulo.
        
    Returns:
        Um objeto Logger configurado.
    """
    # Configura o logging se ainda não foi feito
    if not _logging_configured:
        configure_logging()
    
    return logging.getLogger(name)


def set_log_level(level: Union[int, str]) -> None:
    """
    Altera o nível de log em tempo de execução.
    
    Args:
        level: Novo nível de log (logging.DEBUG, logging.INFO, etc.) ou string 
              correspondente.
    """
    # Converte string para constante do logging se necessário
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    
    # Altera o nível do logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    logging.info(f"Nível de log alterado para: {logging.getLevelName(level)}")


# Configura o logging automaticamente na importação do módulo
configure_logging()
