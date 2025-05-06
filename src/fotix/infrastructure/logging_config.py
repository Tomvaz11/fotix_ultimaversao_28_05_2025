"""
Configuração do sistema de logging para o Fotix.

Este módulo configura o sistema de logging padrão do Python para a aplicação Fotix.
Define formatos de log, níveis e handlers (console, arquivo) com base nas configurações
carregadas de `fotix.config`.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Dict, Optional, Union

from fotix.config import get_config

# Mapeamento de strings de nível de log para constantes do logging
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}


def configure_logging(logger_name: str = "fotix") -> logging.Logger:
    """
    Configura o sistema de logging para o Fotix.

    Args:
        logger_name: Nome do logger a ser configurado. O padrão é "fotix".

    Returns:
        logging.Logger: O logger configurado.
    """
    # Obter configurações de logging
    config = get_config()
    logging_config = config.get("logging") or {}

    # Criar logger
    logger = logging.getLogger(logger_name)

    # Definir nível de log global
    level_str = logging_config.get("level", "INFO")
    level = LOG_LEVELS.get(level_str, logging.INFO)
    logger.setLevel(level)

    # Remover handlers existentes para evitar duplicação
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Configurar handler de console
    if logging_config.get("console", {}).get("enabled", True):
        console_handler = _create_console_handler(logging_config.get("console", {}))
        logger.addHandler(console_handler)

    # Configurar handler de arquivo
    if logging_config.get("file", {}).get("enabled", True):
        file_handler = _create_file_handler(logging_config.get("file", {}))
        logger.addHandler(file_handler)

    # Configurar propagação
    logger.propagate = False

    return logger


def _create_console_handler(config: Dict) -> logging.Handler:
    """
    Cria um handler de console com base nas configurações fornecidas.

    Args:
        config: Configurações para o handler de console.

    Returns:
        logging.Handler: Handler de console configurado.
    """
    # Criar handler de console
    handler = logging.StreamHandler()

    # Definir nível de log
    level_str = config.get("level", "INFO")
    level = LOG_LEVELS.get(level_str, logging.INFO)
    handler.setLevel(level)

    # Definir formato
    format_str = config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    formatter = logging.Formatter(format_str)
    handler.setFormatter(formatter)

    return handler


def _create_file_handler(config: Dict) -> logging.Handler:
    """
    Cria um handler de arquivo com base nas configurações fornecidas.

    Args:
        config: Configurações para o handler de arquivo.

    Returns:
        logging.Handler: Handler de arquivo configurado.
    """
    # Obter caminho do arquivo de log
    filename = config.get("filename", "fotix.log")
    log_dir = _get_log_directory()
    log_path = log_dir / filename

    # Criar handler de arquivo rotativo
    max_size_mb = config.get("max_size_mb", 5)
    backup_count = config.get("backup_count", 3)

    handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=max_size_mb * 1024 * 1024,
        backupCount=backup_count,
        encoding="utf-8"
    )

    # Definir nível de log
    level_str = config.get("level", "DEBUG")
    level = LOG_LEVELS.get(level_str, logging.DEBUG)
    handler.setLevel(level)

    # Definir formato
    format_str = config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    formatter = logging.Formatter(format_str)
    handler.setFormatter(formatter)

    return handler


def _get_log_directory() -> Path:
    """
    Obtém o diretório para armazenar os arquivos de log.

    Returns:
        Path: Caminho para o diretório de logs.
    """
    # Usar o diretório de dados do usuário para armazenar logs
    log_dir = Path.home() / ".fotix" / "logs"
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Obtém um logger configurado para o módulo especificado.

    Se o logger raiz "fotix" ainda não foi configurado, configura-o.

    Args:
        name: Nome do módulo para o qual obter o logger. Se None, retorna o logger raiz "fotix".

    Returns:
        logging.Logger: Logger configurado.
    """
    root_logger_name = "fotix"

    # Verificar se o logger raiz já foi configurado
    root_logger = logging.getLogger(root_logger_name)
    if not root_logger.handlers:
        configure_logging(root_logger_name)

    # Se name for None, retornar o logger raiz
    if name is None:
        return root_logger

    # Caso contrário, retornar um logger para o módulo especificado
    if not name.startswith(root_logger_name):
        module_logger_name = f"{root_logger_name}.{name}"
    else:
        module_logger_name = name

    return logging.getLogger(module_logger_name)


def set_log_level(level: Union[str, int], logger_name: Optional[str] = None) -> None:
    """
    Define o nível de log para um logger específico.

    Args:
        level: Nível de log a ser definido. Pode ser uma string ("DEBUG", "INFO", etc.)
               ou uma constante do logging (logging.DEBUG, logging.INFO, etc.).
        logger_name: Nome do logger para o qual definir o nível. Se None, define para o logger raiz "fotix".
    """
    # Converter string para constante do logging, se necessário
    if isinstance(level, str):
        level = LOG_LEVELS.get(level.upper(), logging.INFO)

    # Obter o logger
    logger = get_logger(logger_name)

    # Definir o nível
    logger.setLevel(level)
