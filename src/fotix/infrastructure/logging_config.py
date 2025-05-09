"""
Configuração do sistema de logging para o Fotix.

Este módulo configura o sistema de logging padrão do Python para a aplicação Fotix,
permitindo o registro de eventos e erros em diferentes níveis de severidade.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
import sys
from pathlib import Path
from typing import Optional, Union

from fotix.config import get_config


def configure_logging(
    log_file: Optional[Union[str, Path]] = None,
    log_level: Optional[str] = None,
    console_output: bool = True,
    file_max_size_mb: int = 5,
    file_backup_count: int = 3
) -> logging.Logger:
    """
    Configura o sistema de logging do Python para a aplicação Fotix.
    
    Args:
        log_file: Caminho para o arquivo de log. Se None, usa o valor definido nas configurações.
        log_level: Nível de log ("debug", "info", "warning", "error", "critical").
                  Se None, usa o valor definido nas configurações.
        console_output: Se True, adiciona um handler para saída no console.
        file_max_size_mb: Tamanho máximo do arquivo de log em megabytes antes de rotacionar.
        file_backup_count: Número de arquivos de backup a manter quando rotacionar.
    
    Returns:
        O logger configurado para a aplicação.
    
    Raises:
        ValueError: Se o nível de log é inválido.
        OSError: Se ocorrer erro ao criar o diretório de log ou arquivo.
    """
    # Obtem configurações da aplicação
    config = get_config()
    
    # Usa valores das configurações se não forem fornecidos explicitamente
    if log_level is None:
        log_level = config.log_level
    
    if log_file is None and config.log_file is not None:
        log_file = config.log_file
    
    # Converte Path para string se necessário
    if isinstance(log_file, Path):
        log_file = str(log_file)
    
    # Obtém o nível de log do Python a partir do nome do nível
    try:
        log_level_value = getattr(logging, log_level.upper())
    except (AttributeError, TypeError):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        raise ValueError(
            f"Nível de log inválido: {log_level}. "
            f"Valores válidos: {', '.join(valid_levels)}"
        )
    
    # Logger raiz da aplicação
    logger = logging.getLogger("fotix")
    logger.setLevel(log_level_value)
    logger.handlers = []  # Remove handlers existentes para evitar duplicidade
    
    # Formato do log
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Handler para saída no console (stdout)
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_format)
        console_handler.setLevel(log_level_value)
        logger.addHandler(console_handler)
    
    # Handler para arquivo de log (se especificado)
    if log_file:
        try:
            # Garante que o diretório pai exista
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            
            # Configura RotatingFileHandler para limitação de tamanho e rotação automática
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=file_max_size_mb * 1024 * 1024,  # Converte MB para bytes
                backupCount=file_backup_count,
                encoding="utf-8"
            )
            file_handler.setFormatter(log_format)
            file_handler.setLevel(log_level_value)
            logger.addHandler(file_handler)
        except OSError as e:
            # Loga o erro no console (não podemos usar o logger ainda)
            print(f"Erro ao configurar arquivo de log: {e}", file=sys.stderr)
            raise
    
    # Configura para não propagar logs para o handler raiz (evita duplicidade)
    logger.propagate = False
    
    # Log inicial para confirmar a configuração
    logger.debug(f"Logging configurado com nível {log_level.upper()}")
    if log_file:
        logger.debug(f"Logs sendo salvos em: {log_file}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger específico para um módulo ou componente do Fotix.
    
    Permite logar com um nome específico mantendo a configuração global.
    Se o logging ainda não foi configurado, configura-o automaticamente.
    
    Args:
        name: Nome do logger, geralmente o nome do módulo (__name__)
    
    Returns:
        Um logger configurado para o módulo/componente especificado.
    """
    # Verifica se o logger raiz já foi configurado
    root_logger = logging.getLogger("fotix")
    
    if not root_logger.handlers:
        # Se não tem handlers, é porque ainda não foi configurado
        configure_logging()
    
    # Retorna um logger filho com o nome especificado
    if name == "fotix":
        return root_logger
    
    # Garante que estamos usando o namespace correto para os módulos do Fotix
    if not name.startswith("fotix.") and name != "fotix":
        name = f"fotix.{name}"
    
    return logging.getLogger(name)


# Configuração padrão ao importar o módulo
default_logger = configure_logging() 