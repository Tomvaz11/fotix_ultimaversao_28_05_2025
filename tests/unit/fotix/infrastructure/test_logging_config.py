"""
Testes unitários para o módulo de configuração de logging.
"""

import logging
import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from fotix.infrastructure.logging_config import (LoggingConfig, get_logger,
                                                setup_logging, update_log_level)


class TestLoggingConfig:
    """Testes para a classe LoggingConfig."""
    
    def test_init_with_default_values(self):
        """Testa inicialização com valores padrão."""
        with mock.patch('fotix.infrastructure.logging_config.get_config') as mock_get_config:
            # Configura o mock
            mock_config = mock.MagicMock()
            mock_config.log_level = "INFO"
            mock_config.log_file = "/path/to/log.txt"
            mock_get_config.return_value = mock_config
            
            # Testa inicialização com valores padrão
            log_config = LoggingConfig()
            
            # Verifica se os valores corretos foram obtidos da configuração
            assert log_config.log_level == "INFO"
            assert log_config.log_file == "/path/to/log.txt"
    
    def test_init_with_custom_values(self):
        """Testa inicialização com valores personalizados."""
        with mock.patch('fotix.infrastructure.logging_config.get_config'):
            # Testa inicialização com valores personalizados
            log_config = LoggingConfig(log_level="DEBUG", log_file="/custom/path.log")
            
            # Verifica se os valores personalizados foram usados
            assert log_config.log_level == "DEBUG"
            assert log_config.log_file == "/custom/path.log"
    
    def test_configure_sets_root_logger_level(self):
        """Testa se o método configure define o nível do logger raiz corretamente."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            with mock.patch('fotix.infrastructure.logging_config.get_config'):
                # Configura o logging com um nível específico
                log_config = LoggingConfig(log_level="WARNING", log_file=log_file)
                
                # Configura o logger
                with mock.patch.object(LoggingConfig, '_setup_file_handler') as mock_setup:
                    root_logger = log_config.configure()
                    
                    # Verifica se o nível foi definido corretamente
                    assert root_logger.level == logging.WARNING
                    
                    # Verifica se há pelo menos um handler (console)
                    assert len(root_logger.handlers) > 0
    
    def test_setup_file_handler_creates_log_directory(self):
        """Testa se o setup_file_handler cria o diretório de log se não existir."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir) / "logs"
            log_file = log_dir / "test.log"
            
            with mock.patch('fotix.infrastructure.logging_config.get_config'):
                log_config = LoggingConfig(log_level="INFO", log_file=log_file)
                
                # Simula um logger e formatter
                logger = logging.getLogger("test_logger")
                formatter = logging.Formatter('%(asctime)s - %(message)s')
                
                # Configura o file handler
                log_config._setup_file_handler(logger, formatter, logging.INFO)
                
                # Verifica se o diretório foi criado
                assert log_dir.exists()
                
                # Importante: remover os handlers para evitar o erro de arquivo em uso
                for handler in logger.handlers[:]:
                    handler.close()
                    logger.removeHandler(handler)
    
    def test_update_log_level_changes_all_handlers(self):
        """Testa se update_log_level atualiza o nível em todos os handlers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            with mock.patch('fotix.infrastructure.logging_config.get_config'):
                # Configura o logging
                log_config = LoggingConfig(log_level="INFO", log_file=log_file)
                
                # Adiciona handlers
                root_logger = logging.getLogger()
                level_before = root_logger.level
                handlers_before = root_logger.handlers[:]
                
                with mock.patch.object(LoggingConfig, '_setup_file_handler'):
                    log_config.configure()
                    
                    # Atualiza o nível
                    log_config.update_log_level("DEBUG")
                    
                    # Verifica se o nível do logger foi atualizado
                    assert root_logger.level == logging.DEBUG
                    
                    # Verifica se o nível de todos os handlers foi atualizado
                    for handler in root_logger.handlers:
                        assert handler.level == logging.DEBUG
                
                # Restaura o estado do logger para não afetar outros testes
                root_logger.setLevel(level_before)
                for handler in root_logger.handlers[:]:
                    handler.close()  # Fechar o handler antes de removê-lo
                    root_logger.removeHandler(handler)
                for handler in handlers_before:
                    root_logger.addHandler(handler)
    
    def test_update_log_level_invalid_level(self):
        """Testa se update_log_level levanta ValueError para nível inválido."""
        with mock.patch('fotix.infrastructure.logging_config.get_config'):
            log_config = LoggingConfig()
            
            # Verifica se levanta ValueError para nível inválido
            with pytest.raises(ValueError):
                log_config.update_log_level("INVALID_LEVEL")


class TestLoggingFunctions:
    """Testes para as funções do módulo de logging."""
    
    def test_setup_logging_returns_configured_logger(self):
        """Testa se setup_logging retorna um logger configurado."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            # Patch para evitar efeitos colaterais nos arquivos reais
            with mock.patch('fotix.infrastructure.logging_config.LoggingConfig') as mock_config_class:
                # Configura o mock
                mock_config = mock.MagicMock()
                mock_config.configure.return_value = logging.getLogger()
                mock_config_class.return_value = mock_config
                
                # Chama a função
                logger = setup_logging(log_level="DEBUG", log_file=log_file)
                
                # Verifica se a classe foi chamada com os parâmetros corretos
                mock_config_class.assert_called_once_with("DEBUG", log_file)
                
                # Verifica se o método configure foi chamado
                mock_config.configure.assert_called_once()
                
                # Verifica se um logger foi retornado
                assert isinstance(logger, logging.Logger)
    
    def test_get_logger_returns_named_logger(self):
        """Testa se get_logger retorna um logger com o nome correto."""
        # Chama a função
        logger = get_logger("test_logger")
        
        # Verifica se o logger tem o nome correto
        assert logger.name == "test_logger"
    
    def test_update_log_level_raises_runtime_error_if_not_configured(self):
        """Testa se update_log_level levanta RuntimeError se o logging não foi configurado."""
        # Garante que _default_logging_config é None
        with mock.patch('fotix.infrastructure.logging_config._default_logging_config', None):
            # Verifica se levanta RuntimeError
            with pytest.raises(RuntimeError):
                update_log_level("DEBUG")
    
    def test_update_log_level_calls_config_update(self):
        """Testa se update_log_level chama o método update_log_level da instância de LoggingConfig."""
        # Cria um mock para _default_logging_config
        with mock.patch('fotix.infrastructure.logging_config._default_logging_config') as mock_config:
            # Chama a função
            update_log_level("DEBUG")
            
            # Verifica se o método foi chamado com o parâmetro correto
            mock_config.update_log_level.assert_called_once_with("DEBUG") 