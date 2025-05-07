"""
Módulo de configuração de logging para a aplicação Fotix.

Este módulo é responsável por configurar o sistema de logging padrão do Python
para a aplicação Fotix, permitindo o registro de eventos e erros.

Exemplo de uso:
    from fotix.infrastructure.logging_config import configure_logging, get_logger
    from fotix.config import Config

    # Configurar o logging com as configurações padrão
    configure_logging()

    # Ou com configurações personalizadas
    config = Config({'log_level': 'DEBUG'})
    configure_logging(config)

    # Obter um logger para um módulo específico
    logger = get_logger(__name__)

    # Usar o logger
    logger.info("Mensagem informativa")
    logger.debug("Mensagem de depuração")
    logger.warning("Aviso")
    logger.error("Erro")
    logger.critical("Erro crítico")
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Union

from fotix.config import Config, default_config


class LoggingError(Exception):
    """Exceção levantada para erros relacionados ao logging."""
    pass


class LoggingConfig:
    """
    Classe para configurar o sistema de logging do Python para a aplicação Fotix.

    Esta classe permite configurar o logging com base nas configurações fornecidas,
    incluindo nível de log, formato, saída para console e arquivo.
    """

    # Mapeamento de strings de nível de log para constantes do logging
    LOG_LEVELS = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    # Formato padrão para mensagens de log
    DEFAULT_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'

    # Formato padrão para data/hora
    DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, config: Optional[Config] = None):
        """
        Inicializa uma nova instância de LoggingConfig.

        Args:
            config: Instância opcional de Config com configurações de logging.
                   Se None, usa a instância global default_config.
        """
        self.config = config or default_config
        self._configured = False

    def configure(self) -> logging.Logger:
        """
        Configura o sistema de logging com base nas configurações.

        Returns:
            O logger raiz configurado.

        Raises:
            LoggingError: Se ocorrer um erro durante a configuração.
        """
        if self._configured:
            return logging.getLogger()

        try:
            # Obtém as configurações de logging
            log_level_str = self.config.get('log_level', 'INFO').upper()
            log_format = self.config.get('log_format', self.DEFAULT_FORMAT)
            log_date_format = self.config.get('log_date_format', self.DEFAULT_DATE_FORMAT)
            log_to_file = self.config.get_bool('log_to_file', False)
            log_file_path = self._get_log_file_path() if log_to_file else None

            # Converte a string de nível de log para a constante correspondente
            if log_level_str not in self.LOG_LEVELS:
                raise LoggingError(f"Nível de log inválido: {log_level_str}")
            log_level = self.LOG_LEVELS[log_level_str]

            # Configura o logger raiz
            root_logger = logging.getLogger()
            root_logger.setLevel(log_level)

            # Remove handlers existentes para evitar duplicação
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

            # Cria o formatador
            formatter = logging.Formatter(log_format, log_date_format)

            # Adiciona handler para console
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)

            # Adiciona handler para arquivo, se configurado
            if log_to_file and log_file_path:
                # Cria o diretório pai se não existir
                log_file_path.parent.mkdir(parents=True, exist_ok=True)

                file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
                file_handler.setLevel(log_level)
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)

            self._configured = True
            return root_logger

        except Exception as e:
            raise LoggingError(f"Erro ao configurar logging: {e}")

    def _get_log_file_path(self) -> Path:
        """
        Obtém o caminho para o arquivo de log.

        Returns:
            O caminho para o arquivo de log.
        """
        # Obtém o diretório de logs da configuração ou usa o padrão
        log_dir = None
        if 'log_dir' in self.config:
            log_dir = self.config.get_path('log_dir')
        else:
            app_data_dir = self.config.get_path('app_data_dir', Path.home() / '.fotix')
            log_dir = app_data_dir / 'logs'

        # Cria o nome do arquivo de log com a data atual
        date_str = datetime.now().strftime('%Y-%m-%d')
        return log_dir / f"fotix_{date_str}.log"

    def get_logger(self, name: str) -> logging.Logger:
        """
        Obtém um logger configurado para o módulo especificado.

        Args:
            name: Nome do logger, geralmente o nome do módulo (__name__).

        Returns:
            Um logger configurado.
        """
        # Garante que o logging está configurado
        if not self._configured:
            self.configure()

        return logging.getLogger(name)


# Instância global para configuração de logging
_logging_config = LoggingConfig()


def configure_logging(config: Optional[Config] = None) -> logging.Logger:
    """
    Configura o sistema de logging para a aplicação Fotix.

    Args:
        config: Instância opcional de Config com configurações de logging.
               Se None, usa a instância global default_config.

    Returns:
        O logger raiz configurado.

    Raises:
        LoggingError: Se ocorrer um erro durante a configuração.
    """
    global _logging_config
    _logging_config = LoggingConfig(config)
    return _logging_config.configure()


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger configurado para o módulo especificado.

    Args:
        name: Nome do logger, geralmente o nome do módulo (__name__).

    Returns:
        Um logger configurado.
    """
    return _logging_config.get_logger(name)
