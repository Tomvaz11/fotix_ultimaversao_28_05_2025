"""
Testes unitários para o módulo de configuração de logging.

Este arquivo contém testes para as funcionalidades do módulo logging_config,
incluindo configuração de logging, obtenção de loggers e tratamento de erros.
"""

import io
import logging
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from fotix.config import Config
from fotix.infrastructure.logging_config import (
    LoggingConfig, LoggingError, configure_logging, get_logger
)


class TestLoggingConfig:
    """Testes para a classe LoggingConfig."""

    def setup_method(self):
        """Configuração executada antes de cada teste."""
        # Salva os handlers originais para restaurar depois
        self.original_handlers = logging.getLogger().handlers.copy()
        # Limpa os handlers existentes
        logging.getLogger().handlers.clear()

    def teardown_method(self):
        """Limpeza executada após cada teste."""
        # Restaura os handlers originais
        logging.getLogger().handlers = self.original_handlers

    def test_init_with_config(self):
        """Testa a inicialização com uma instância de Config."""
        config = Config({'log_level': 'DEBUG'})
        logging_config = LoggingConfig(config)
        assert logging_config.config == config
        assert not logging_config._configured

    def test_init_without_config(self):
        """Testa a inicialização sem uma instância de Config."""
        logging_config = LoggingConfig()
        assert logging_config.config is not None
        assert not logging_config._configured

    def test_configure_basic(self):
        """Testa a configuração básica do logging."""
        config = Config({'log_level': 'INFO'})
        logging_config = LoggingConfig(config)

        logger = logging_config.configure()

        assert logger is logging.getLogger()
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1  # Console handler
        assert isinstance(logger.handlers[0], logging.StreamHandler)
        assert logger.handlers[0].stream == sys.stdout
        assert logging_config._configured

    def test_configure_with_file(self):
        """Testa a configuração com saída para arquivo."""
        # Cria um diretório temporário
        temp_dir = tempfile.mkdtemp()
        try:
            log_dir = Path(temp_dir)
            config = Config({
                'log_level': 'DEBUG',
                'log_to_file': True,
                'log_dir': str(log_dir)
            })
            logging_config = LoggingConfig(config)

            logger = logging_config.configure()

            assert logger is logging.getLogger()
            assert logger.level == logging.DEBUG
            assert len(logger.handlers) == 2  # Console + File handlers
            assert isinstance(logger.handlers[0], logging.StreamHandler)
            assert isinstance(logger.handlers[1], logging.FileHandler)

            # Verifica se o arquivo de log foi criado no diretório correto
            log_files = list(log_dir.glob('fotix_*.log'))
            assert len(log_files) == 1

            # Fecha os handlers para liberar os arquivos
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)
        finally:
            # Limpa os handlers antes de tentar remover o diretório
            for handler in logging.getLogger().handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    handler.close()
                    logging.getLogger().removeHandler(handler)

            # Tenta remover o diretório temporário
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass

    def test_configure_invalid_level(self):
        """Testa a configuração com um nível de log inválido."""
        config = Config({'log_level': 'INVALID'})
        logging_config = LoggingConfig(config)

        with pytest.raises(LoggingError) as excinfo:
            logging_config.configure()

        assert "Nível de log inválido: INVALID" in str(excinfo.value)

    def test_configure_twice(self):
        """Testa a configuração chamada duas vezes."""
        config = Config({'log_level': 'INFO'})
        logging_config = LoggingConfig(config)

        logger1 = logging_config.configure()
        logger2 = logging_config.configure()

        assert logger1 is logger2
        assert len(logger1.handlers) == 1  # Não deve duplicar handlers

    def test_get_logger(self):
        """Testa a obtenção de um logger para um módulo específico."""
        config = Config({'log_level': 'INFO'})
        logging_config = LoggingConfig(config)

        # Configura o logging explicitamente
        logging_config.configure()

        # Obtém um logger para um módulo específico
        logger = logging_config.get_logger('test_module')

        assert logger.name == 'test_module'
        assert logger.level == 0  # O nível do logger específico não é definido
        assert logging.getLogger().level == logging.INFO  # O nível do logger raiz é definido

    def test_get_logger_auto_configure(self):
        """Testa a obtenção de um logger sem configurar explicitamente."""
        config = Config({'log_level': 'INFO'})
        logging_config = LoggingConfig(config)

        # Obtém um logger sem configurar explicitamente
        logger = logging_config.get_logger('test_module')

        assert logger.name == 'test_module'
        assert logging_config._configured  # Deve ter configurado automaticamente

    def test_get_log_file_path_custom(self):
        """Testa a obtenção do caminho do arquivo de log com diretório personalizado."""
        config = Config({'log_dir': '/custom/log/dir'})
        logging_config = LoggingConfig(config)

        log_path = logging_config._get_log_file_path()

        assert log_path.parent == Path('/custom/log/dir')
        assert log_path.name.startswith('fotix_')
        assert log_path.name.endswith('.log')

    def test_get_log_file_path_default(self):
        """Testa a obtenção do caminho do arquivo de log com diretório padrão."""
        config = Config()  # Usa valores padrão
        logging_config = LoggingConfig(config)

        # Verifica se o método não lança exceção
        log_path = logging_config._get_log_file_path()

        # Verifica o caminho do arquivo de log
        expected_parent = Path(config.get('app_data_dir')) / 'logs'
        assert log_path.parent == expected_parent
        assert log_path.name.startswith('fotix_')
        assert log_path.name.endswith('.log')


class TestLoggingFunctions:
    """Testes para as funções de logging."""

    def setup_method(self):
        """Configuração executada antes de cada teste."""
        # Salva os handlers originais para restaurar depois
        self.original_handlers = logging.getLogger().handlers.copy()
        # Limpa os handlers existentes
        logging.getLogger().handlers.clear()

    def teardown_method(self):
        """Limpeza executada após cada teste."""
        # Restaura os handlers originais
        logging.getLogger().handlers = self.original_handlers

    def test_configure_logging(self):
        """Testa a função configure_logging."""
        config = Config({'log_level': 'DEBUG'})

        logger = configure_logging(config)

        assert logger is logging.getLogger()
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 1

    def test_get_logger_function(self):
        """Testa a função get_logger."""
        # Configura o logging primeiro
        configure_logging(Config({'log_level': 'INFO'}))

        # Obtém um logger
        logger = get_logger('test_module')

        assert logger.name == 'test_module'

    def test_logging_output(self):
        """Testa a saída do logging para diferentes níveis."""
        # Configura o logging com nível INFO
        configure_logging(Config({'log_level': 'INFO'}))

        # Cria um handler de teste para capturar as mensagens
        test_handler = logging.StreamHandler(io.StringIO())
        root_logger = logging.getLogger()
        root_logger.addHandler(test_handler)

        try:
            # Obtém um logger e envia mensagens
            logger = get_logger('test_output')

            logger.debug("Esta mensagem de DEBUG não deve aparecer")
            logger.info("Esta mensagem de INFO deve aparecer")
            logger.warning("Esta mensagem de WARNING deve aparecer")
            logger.error("Esta mensagem de ERROR deve aparecer")

            # Obtém a saída capturada
            output = test_handler.stream.getvalue()

            # Verifica se as mensagens apropriadas aparecem na saída
            assert "DEBUG" not in output
            assert "Esta mensagem de INFO deve aparecer" in output
            assert "Esta mensagem de WARNING deve aparecer" in output
            assert "Esta mensagem de ERROR deve aparecer" in output
        finally:
            # Remove o handler de teste
            root_logger.removeHandler(test_handler)
