"""
Módulo de configuração de logging para o Fotix.

Este módulo é responsável por configurar o sistema de logging padrão do Python
para a aplicação Fotix, permitindo o registro de eventos e erros com diferentes
níveis de severidade em arquivo e console.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional, Union

from fotix.config import get_config


class LoggingConfig:
    """
    Configurador de logging para o Fotix.
    
    Responsável por configurar o logger padrão do Python para a aplicação,
    definindo formatos, níveis e handlers para saída em arquivo e console.
    """
    
    # Mapeamento de strings de nível de log para constantes do logging
    LOG_LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    def __init__(self, log_level: Optional[str] = None, log_file: Optional[Union[str, Path]] = None):
        """
        Inicializa o configurador de logging.
        
        Args:
            log_level: Nível de log a ser utilizado. Se None, utiliza o valor da configuração.
            log_file: Caminho para o arquivo de log. Se None, utiliza o valor da configuração.
        """
        self.config = get_config()
        self.log_level = log_level or self.config.log_level
        self.log_file = log_file or self.config.log_file
    
    def configure(self) -> logging.Logger:
        """
        Configura o sistema de logging e retorna o logger raiz.
        
        Returns:
            O logger raiz configurado.
        """
        # Converte o nível de log de string para constante
        level = self.LOG_LEVELS.get(self.log_level.upper(), logging.INFO)
        
        # Configura o logger raiz
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        
        # Remove handlers existentes para evitar duplicação
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Configura o formato dos logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Adiciona handler para saída no console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # Adiciona handler para saída em arquivo
        self._setup_file_handler(root_logger, formatter, level)
        
        return root_logger
    
    def _setup_file_handler(self, logger: logging.Logger, formatter: logging.Formatter, level: int) -> None:
        """
        Configura o handler para saída de logs em arquivo.
        
        Args:
            logger: O logger a ser configurado.
            formatter: O formatador para os logs.
            level: O nível de log.
        """
        # Garante que o diretório do arquivo de log existe
        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Usa RotatingFileHandler para limitar o tamanho do arquivo de log
            file_handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,  # Mantém até 5 arquivos de backup
                encoding='utf-8'
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
            # Log de sucesso na configuração
            logger.info(f"Sistema de log configurado. Nível: {self.log_level}, Arquivo: {log_path}")
        except (PermissionError, OSError) as e:
            # Em caso de erro, adiciona apenas um log no console
            logger.error(f"Não foi possível configurar o log em arquivo: {e}")
    
    def update_log_level(self, level: str) -> None:
        """
        Atualiza o nível de log em tempo de execução.
        
        Args:
            level: Novo nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            
        Raises:
            ValueError: Se o nível de log for inválido.
        """
        level = level.upper()
        if level not in self.LOG_LEVELS:
            valid_levels = ", ".join(self.LOG_LEVELS.keys())
            raise ValueError(f"Nível de log inválido. Valores válidos: {valid_levels}")
        
        # Atualiza o nível no objeto e na configuração
        self.log_level = level
        self.config.log_level = level
        
        # Atualiza o nível nos handlers existentes
        root_logger = logging.getLogger()
        level_value = self.LOG_LEVELS[level]
        root_logger.setLevel(level_value)
        
        for handler in root_logger.handlers:
            handler.setLevel(level_value)
        
        # Registra a mudança
        root_logger.info(f"Nível de log atualizado para: {level}")


# Instância global para acesso fácil
_default_logging_config = None


def setup_logging(log_level: Optional[str] = None, log_file: Optional[Union[str, Path]] = None) -> logging.Logger:
    """
    Configura o sistema de logging do Fotix.
    
    Esta função deve ser chamada no início da aplicação para configurar o logging.
    
    Args:
        log_level: Nível de log a ser utilizado. Se None, utiliza o valor da configuração.
        log_file: Caminho para o arquivo de log. Se None, utiliza o valor da configuração.
        
    Returns:
        O logger raiz configurado.
    """
    global _default_logging_config
    _default_logging_config = LoggingConfig(log_level, log_file)
    return _default_logging_config.configure()


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger com o nome especificado.
    
    Args:
        name: Nome do logger, geralmente o nome do módulo (__name__).
        
    Returns:
        Um logger configurado.
    """
    return logging.getLogger(name)


def update_log_level(level: str) -> None:
    """
    Atualiza o nível de log em tempo de execução.
    
    Args:
        level: Novo nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        
    Raises:
        RuntimeError: Se o logging não foi configurado primeiro.
        ValueError: Se o nível de log for inválido.
    """
    if _default_logging_config is None:
        raise RuntimeError("O logging não foi configurado. Chame setup_logging primeiro.")
    
    _default_logging_config.update_log_level(level) 