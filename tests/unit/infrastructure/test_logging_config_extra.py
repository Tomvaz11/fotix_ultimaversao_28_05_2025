"""
Testes adicionais para o módulo de configuração de logging.
"""

import logging
from unittest import mock

import pytest

from fotix.infrastructure.logging_config import configure_logging


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
