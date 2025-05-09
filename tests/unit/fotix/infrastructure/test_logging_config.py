"""
Testes unitários para o módulo fotix.infrastructure.logging_config.

Estes testes verificam se o sistema de logging é configurado corretamente,
se os níveis de log funcionam como esperado e se as exceções são geradas
em situações de erro.
"""

import os
import sys
import logging
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from fotix.config import Config, reset_config
from fotix.infrastructure.logging_config import configure_logging, get_logger


@pytest.fixture
def temp_log_dir():
    """Cria um diretório temporário para arquivos de log."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_config():
    """Mock das configurações para isolar os testes."""
    # Reseta a configuração global para garantir um estado limpo
    reset_config()
    
    # Mock da configuração
    with mock.patch('fotix.infrastructure.logging_config.get_config') as mock_get_config:
        config = Config()
        config.log_level = "info"
        config.log_file = None  # Sem arquivo de log por padrão
        mock_get_config.return_value = config
        yield config


@pytest.fixture
def clean_handlers():
    """Remove todos os handlers do logger fotix após cada teste."""
    yield
    # Limpa os handlers após o teste
    logger = logging.getLogger("fotix")
    logger.handlers = []


class TestLoggingConfig:
    """Testes para o módulo de configuração de logging."""
    
    def test_configure_logging_defaults(self, mock_config, clean_handlers):
        """Testa se configure_logging usa valores padrão das configurações."""
        # Configure logging com valores padrão
        logger = configure_logging()
        
        # Verifica se o logger foi configurado corretamente
        assert logger.level == logging.INFO
        assert logger.name == "fotix"
        assert len(logger.handlers) == 1  # Apenas console por padrão
        assert isinstance(logger.handlers[0], logging.StreamHandler)
        assert logger.handlers[0].stream == sys.stdout
    
    def test_configure_logging_explicit_level(self, mock_config, clean_handlers):
        """Testa se configure_logging respeita o nível explicitamente fornecido."""
        # Configure logging com nível DEBUG explícito
        logger = configure_logging(log_level="debug")
        
        # Verifica se o nível foi configurado corretamente
        assert logger.level == logging.DEBUG
        assert logger.handlers[0].level == logging.DEBUG
    
    def test_configure_logging_with_file(self, mock_config, temp_log_dir, clean_handlers):
        """Testa se configure_logging configura corretamente o arquivo de log."""
        # Define caminho para o arquivo de log
        log_file = temp_log_dir / "test.log"
        
        # Configure logging com arquivo
        logger = configure_logging(log_file=log_file)
        
        # Verifica se ambos handlers (console e arquivo) foram configurados
        assert len(logger.handlers) == 2
        assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)
        
        # Escreve um log para testar
        logger.info("Test log message")
        
        # Verifica se o arquivo foi criado e contém a mensagem
        assert log_file.exists()
        with open(log_file, "r") as f:
            content = f.read()
            assert "Test log message" in content
    
    def test_configure_logging_invalid_level(self, mock_config, clean_handlers):
        """Testa se configure_logging levanta exceção para nível de log inválido."""
        with pytest.raises(ValueError) as excinfo:
            configure_logging(log_level="invalid_level")
        
        assert "Nível de log inválido" in str(excinfo.value)
    
    def test_configure_logging_file_error(self, mock_config, clean_handlers):
        """Testa se configure_logging levanta exceção quando há erro no arquivo de log."""
        # Mock para simular erro ao criar diretório
        with mock.patch('os.makedirs', side_effect=OSError("Permission denied")):
            with pytest.raises(OSError) as excinfo:
                configure_logging(log_file="/invalid/path/log.txt")
            
            assert "Permission denied" in str(excinfo.value)
    
    def test_configure_logging_no_console(self, mock_config, clean_handlers):
        """Testa se configure_logging respeita a opção de não usar console."""
        logger = configure_logging(console_output=False)
        
        # Não deve ter handlers de console
        assert len(logger.handlers) == 0
        assert not any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
    
    def test_get_logger_new(self, mock_config, clean_handlers):
        """Testa se get_logger configura um novo logger quando necessário."""
        # Remove todos os handlers para simular primeiro uso
        logging.getLogger("fotix").handlers = []
        
        # Obtem logger para um módulo específico
        logger = get_logger("fotix.test_module")
        
        # Verifica se o logger foi configurado corretamente
        assert logger.name == "fotix.test_module"
        # O logger raiz (fotix) deve ter handlers configurados
        assert len(logging.getLogger("fotix").handlers) > 0
    
    def test_get_logger_existing(self, mock_config, clean_handlers):
        """Testa se get_logger usa configuração existente."""
        # Configura o logger raiz primeiro
        root_logger = configure_logging(log_level="debug")
        
        # Obtem logger para um módulo específico
        module_logger = get_logger("test_module")
        
        # Verifica se o logger do módulo está usando a configuração do raiz
        assert module_logger.name == "fotix.test_module"
        assert logging.getLogger("fotix").level == logging.DEBUG
    
    def test_get_logger_with_full_name(self, mock_config, clean_handlers):
        """Testa se get_logger funciona corretamente com nomes completos."""
        # Configura o logger raiz primeiro
        configure_logging()
        
        # Obtem logger com nome já incluindo o namespace fotix
        logger = get_logger("fotix.infrastructure.test")
        
        # Verifica se o nome foi mantido sem duplicar o namespace
        assert logger.name == "fotix.infrastructure.test"
    
    def test_get_logger_root(self, mock_config, clean_handlers):
        """Testa se get_logger retorna o logger raiz quando solicitado."""
        # Configura o logger raiz primeiro
        root_logger = configure_logging()
        
        # Obtem o logger raiz
        logger = get_logger("fotix")
        
        # Deve ser o mesmo objeto
        assert logger is root_logger
    
    def test_logging_levels(self, mock_config, temp_log_dir, clean_handlers):
        """Testa se os diferentes níveis de log funcionam corretamente."""
        # Define caminho para o arquivo de log
        log_file = temp_log_dir / "levels.log"
        
        # Configure logging com nível INFO
        logger = configure_logging(log_file=log_file, log_level="info")
        
        # Envia logs em diferentes níveis
        logger.debug("Debug message")  # Não deve aparecer
        logger.info("Info message")    # Deve aparecer
        logger.warning("Warning message")  # Deve aparecer
        logger.error("Error message")  # Deve aparecer
        
        # Verifica o conteúdo do arquivo de log
        with open(log_file, "r") as f:
            content = f.read()
            assert "Debug message" not in content  # DEBUG < INFO, não deve ser logado
            assert "Info message" in content
            assert "Warning message" in content
            assert "Error message" in content 