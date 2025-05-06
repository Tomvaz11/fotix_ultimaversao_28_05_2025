"""
Testes unitários para o módulo de configuração de logging.

Este módulo contém testes para a implementação do serviço de logging,
incluindo casos normais, casos de erro e casos de borda.
"""

import logging
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from fotix.config import Config
from fotix.infrastructure.logging_config import (
    configure_logging,
    get_logger,
    set_log_level,
)


@pytest.fixture
def mock_config():
    """Fixture para simular a configuração."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.json"
        with mock.patch("fotix.infrastructure.logging_config.get_config") as mock_get_config:
            config = Config(config_path)
            mock_get_config.return_value = config
            yield config


@pytest.fixture(autouse=True)
def reset_loggers():
    """
    Fixture para resetar os loggers após cada teste.

    Esta fixture é executada automaticamente para cada teste (autouse=True).
    """
    yield
    # Remover todos os handlers do logger fotix
    logger = logging.getLogger("fotix")
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Remover todos os handlers do logger fotix.test
    logger = logging.getLogger("fotix.test")
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Remover todos os handlers do logger fotix.test_remove_handlers
    logger = logging.getLogger("fotix.test_remove_handlers")
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)


# Testes para configure_logging

def test_configure_logging_creates_logger():
    """Testa se configure_logging cria um logger com o nome correto."""
    logger = configure_logging("fotix.test")
    assert logger.name == "fotix.test"
    assert not logger.propagate
    assert logger.level == logging.INFO  # Nível padrão


def test_configure_logging_sets_level_from_config(mock_config):
    """Testa se configure_logging define o nível de log a partir da configuração."""
    # Configurar nível de log
    mock_config.set("logging", "level", "DEBUG")

    logger = configure_logging("fotix.test")
    assert logger.level == logging.DEBUG


def test_configure_logging_adds_console_handler(mock_config):
    """Testa se configure_logging adiciona um handler de console."""
    # Configurar handler de console e desabilitar handler de arquivo
    mock_config.set("logging", "console", {
        "enabled": True,
        "level": "INFO",
        "format": "%(levelname)s - %(message)s"
    })
    mock_config.set("logging", "file", {"enabled": False})

    logger = configure_logging("fotix.test")

    # Verificar se há um handler de console
    console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.handlers.RotatingFileHandler)]
    assert len(console_handlers) == 1

    # Verificar nível e formato
    handler = console_handlers[0]
    assert handler.level == logging.INFO
    assert handler.formatter._fmt == "%(levelname)s - %(message)s"


def test_configure_logging_adds_file_handler(mock_config):
    """Testa se configure_logging adiciona um handler de arquivo."""
    # Configurar handler de arquivo e desabilitar handler de console
    mock_config.set("logging", "file", {
        "enabled": True,
        "level": "DEBUG",
        "format": "%(asctime)s - %(message)s",
        "filename": "test.log",
        "max_size_mb": 1,
        "backup_count": 2
    })
    mock_config.set("logging", "console", {"enabled": False})

    # Usar um diretório temporário para os logs
    with tempfile.TemporaryDirectory() as temp_dir:
        # Patch para usar o diretório temporário
        with mock.patch("fotix.infrastructure.logging_config._get_log_directory") as mock_get_log_dir:
            mock_get_log_dir.return_value = Path(temp_dir)

            # Configurar o logger
            logger = configure_logging("fotix.test")

            # Verificar se há um handler de arquivo
            file_handlers = [h for h in logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
            assert len(file_handlers) == 1

            # Verificar nível e formato
            handler = file_handlers[0]
            assert handler.level == logging.DEBUG
            assert handler.formatter._fmt == "%(asctime)s - %(message)s"
            assert handler.baseFilename.endswith("test.log")
            assert handler.maxBytes == 1 * 1024 * 1024
            assert handler.backupCount == 2

            # Fechar o handler para liberar o arquivo
            handler.close()


def test_configure_logging_disables_console_handler(mock_config):
    """Testa se configure_logging não adiciona um handler de console quando desabilitado."""
    # Desabilitar handler de console
    mock_config.set("logging", "console", {"enabled": False})

    logger = configure_logging("fotix.test")

    # Verificar se não há handler de console
    console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.handlers.RotatingFileHandler)]
    assert len(console_handlers) == 0


def test_configure_logging_disables_file_handler(mock_config):
    """Testa se configure_logging não adiciona um handler de arquivo quando desabilitado."""
    # Desabilitar handler de arquivo
    mock_config.set("logging", "file", {"enabled": False})

    logger = configure_logging("fotix.test")

    # Verificar se não há handler de arquivo
    file_handlers = [h for h in logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
    assert len(file_handlers) == 0


def test_configure_logging_removes_existing_handlers():
    """
    Testa se configure_logging remove handlers existentes.
    
    Este teste é específico para cobrir a linha 51 em logging_config.py
    que remove handlers existentes do logger.
    """
    # Criar um logger com o mesmo nome que será usado em configure_logging
    logger_name = "fotix.test_remove_handlers"
    logger = logging.getLogger(logger_name)
    
    # Adicionar um handler ao logger
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    
    # Verificar que o logger tem um handler
    assert len(logger.handlers) == 1
    
    # Configurar o logger com o mesmo nome
    with mock.patch("fotix.infrastructure.logging_config.get_config"):
        # Desabilitar handlers para simplificar o teste
        with mock.patch("fotix.infrastructure.logging_config._create_console_handler"):
            with mock.patch("fotix.infrastructure.logging_config._create_file_handler"):
                configure_logging(logger_name)
    
    # Verificar que o handler original foi removido
    # O logger pode ter novos handlers dependendo da configuração
    assert handler not in logger.handlers


# Testes para get_logger

def test_get_logger_calls_configure_logging():
    """Testa se get_logger chama configure_logging quando o logger raiz não tem handlers."""
    # Garantir que o logger raiz não tenha handlers
    root_logger = logging.getLogger("fotix")
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Verificar que o logger raiz não tem handlers
    assert not root_logger.handlers

    # Patch a função configure_logging para verificar se ela é chamada
    with mock.patch("fotix.infrastructure.logging_config.configure_logging") as mock_configure:
        # Configurar o mock para retornar um logger com handlers
        mock_logger = mock.MagicMock()
        mock_logger.handlers = [mock.MagicMock()]
        mock_configure.return_value = mock_logger

        # Obter logger
        get_logger()

        # Verificar se configure_logging foi chamado
        mock_configure.assert_called_once_with("fotix")


def test_get_logger_returns_module_logger():
    """Testa se get_logger retorna um logger para o módulo especificado."""
    # Configurar o logger raiz primeiro
    configure_logging()

    # Obter logger para um módulo
    logger = get_logger("test_module")

    # Verificar se o logger tem o nome correto
    assert logger.name == "fotix.test_module"


def test_get_logger_handles_full_name():
    """Testa se get_logger lida corretamente com nomes completos."""
    # Configurar o logger raiz primeiro
    configure_logging()

    # Obter logger com nome completo
    logger = get_logger("fotix.test_module")

    # Verificar se o logger tem o nome correto
    assert logger.name == "fotix.test_module"


# Testes para set_log_level

def test_set_log_level_with_string():
    """Testa se set_log_level define o nível de log a partir de uma string."""
    # Configurar o logger
    logger = configure_logging("fotix.test")

    # Definir nível de log
    set_log_level("DEBUG", "fotix.test")

    # Verificar se o nível foi definido
    assert logger.level == logging.DEBUG


def test_set_log_level_with_constant():
    """Testa se set_log_level define o nível de log a partir de uma constante."""
    # Configurar o logger
    logger = configure_logging("fotix.test")

    # Definir nível de log
    set_log_level(logging.ERROR, "fotix.test")

    # Verificar se o nível foi definido
    assert logger.level == logging.ERROR


def test_set_log_level_for_root_logger():
    """Testa se set_log_level define o nível de log para o logger raiz."""
    # Configurar o logger raiz
    root_logger = configure_logging()

    # Definir nível de log
    set_log_level("WARNING")

    # Verificar se o nível foi definido
    assert root_logger.level == logging.WARNING
