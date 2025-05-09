"""
Módulo de configuração de logging para o Fotix.

Este módulo configura o sistema de logging padrão do Python para a aplicação Fotix,
permitindo o registro de eventos e erros em diferentes níveis. Utiliza o módulo
de configuração para obter parâmetros como nível de log e caminho do arquivo de log.

Exemplo de uso:
    ```python
    from fotix.infrastructure.logging_config import setup_logging, get_logger

    # Configurar o logging (normalmente chamado apenas uma vez na inicialização)
    setup_logging()

    # Obter um logger para um módulo específico
    logger = get_logger(__name__)
    
    # Usar o logger
    logger.debug("Mensagem de debug")
    logger.info("Mensagem informativa")
    logger.warning("Aviso")
    logger.error("Erro")
    logger.critical("Erro crítico")
    ```
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional, Union

from fotix.config import get_config, get_log_level

# Singleton para o logger raiz configurado
_root_logger_configured = False


def setup_logging(log_level: Optional[Union[int, str]] = None, 
                  log_file: Optional[Union[str, Path]] = None,
                  console: bool = True) -> logging.Logger:
    """
    Configura o sistema de logging para a aplicação Fotix.
    
    Esta função configura o logger raiz com handlers para console e/ou arquivo,
    definindo o nível de log e o formato das mensagens. Se não forem fornecidos
    parâmetros, os valores serão obtidos do módulo de configuração.
    
    Args:
        log_level: Nível de log (opcional). Se não fornecido, será obtido da configuração.
                  Pode ser um valor inteiro (logging.DEBUG, logging.INFO, etc.) ou
                  uma string ('DEBUG', 'INFO', etc.).
        log_file: Caminho para o arquivo de log (opcional). Se não fornecido, 
                 será obtido da configuração.
        console: Se True, adiciona um handler para o console. Default é True.
    
    Returns:
        logging.Logger: O logger raiz configurado.
    """
    global _root_logger_configured
    
    # Obter configurações se não fornecidas
    if log_level is None:
        log_level = get_log_level()
    elif isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper(), logging.INFO)
    
    if log_file is None:
        config = get_config()
        log_file = config.get("log_file")
    
    # Configurar o logger raiz
    root_logger = logging.getLogger()
    
    # Limpar handlers existentes se já configurado
    if _root_logger_configured:
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
    
    # Definir o nível de log
    root_logger.setLevel(log_level)
    
    # Criar o formatador
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Adicionar handler para console se solicitado
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Adicionar handler para arquivo se um caminho for fornecido
    if log_file:
        log_file_path = Path(log_file)
        
        # Garantir que o diretório do arquivo de log exista
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Usar RotatingFileHandler para limitar o tamanho do arquivo
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Marcar como configurado
    _root_logger_configured = True
    
    # Log inicial para confirmar a configuração
    root_logger.debug(f"Logging configurado. Nível: {logging.getLevelName(root_logger.level)}")
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger configurado para o módulo especificado.
    
    Se o logger raiz ainda não foi configurado, configura-o automaticamente
    com os valores padrão da configuração.
    
    Args:
        name: Nome do logger, geralmente __name__ do módulo.
    
    Returns:
        logging.Logger: O logger configurado.
    """
    # Configurar o logger raiz se ainda não foi feito
    if not _root_logger_configured:
        setup_logging()
    
    # Retornar o logger para o nome especificado
    return logging.getLogger(name)


def reconfigure_logging() -> None:
    """
    Reconfigura o logging com as configurações atuais.
    
    Útil quando as configurações de logging foram alteradas e é necessário
    aplicar as novas configurações.
    """
    setup_logging()
