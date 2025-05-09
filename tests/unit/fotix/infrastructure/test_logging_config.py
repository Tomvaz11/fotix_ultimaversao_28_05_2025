"""Testes para o módulo de configuração de logging da Fotix."""

import logging
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, call # Adicionado call

from fotix.config import AppSettings # Import AppSettings
from fotix.infrastructure.logging_config import setup_logging


class TestLoggingConfig(unittest.TestCase):
    """Testa a função setup_logging."""

    def setUp(self):
        """Prepara o ambiente para cada teste."""
        # Guarda os handlers originais do logger raiz para restaurá-los depois
        self.root_logger = logging.getLogger()
        self.original_handlers = list(self.root_logger.handlers)
        self.original_level = self.root_logger.level

        # Limpa os handlers do logger raiz antes de cada teste
        for handler in self.original_handlers:
            self.root_logger.removeHandler(handler)
            handler.close() # Fecha o handler para liberar recursos, especialmente arquivos

    def tearDown(self):
        """Limpa o ambiente após cada teste."""
        # Restaura os handlers e o nível original do logger raiz
        current_handlers = list(self.root_logger.handlers)
        for handler in current_handlers:
            self.root_logger.removeHandler(handler)
            handler.close()
        
        for handler in self.original_handlers:
            self.root_logger.addHandler(handler)
        self.root_logger.setLevel(self.original_level)

    @patch('fotix.infrastructure.logging_config.logging.StreamHandler')
    @patch('fotix.infrastructure.logging_config.logging.FileHandler') # Mock FileHandler também
    @patch('fotix.infrastructure.logging_config.logging.Formatter')
    @patch('fotix.infrastructure.logging_config.logging.getLogger')
    def test_setup_logging_console_only(
        self, 
        mock_getLogger, 
        mock_Formatter, 
        mock_FileHandler, # Adicionado mock_FileHandler
        mock_StreamHandler
    ):
        """Testa a configuração de logging apenas para console."""
        mock_root_logger = MagicMock()
        mock_getLogger.return_value = mock_root_logger
        
        mock_formatter_instance = MagicMock()
        mock_Formatter.return_value = mock_formatter_instance

        mock_console_handler_instance = MagicMock()
        mock_StreamHandler.return_value = mock_console_handler_instance

        config_dict = {
            "LOG_LEVEL": "INFO",
            "LOG_FORMAT": "%(message)s",
            "LOG_FILE_PATH": None,
            "BACKUP_PATH": Path("/tmp/backup") # Adicionar campos obrigatórios de AppSettings
        }
        config = AppSettings(**config_dict)

        setup_logging(config)

        mock_getLogger.assert_called_once_with() # Deve pegar o logger raiz
        mock_Formatter.assert_called_once_with("%(message)s")
        
        mock_StreamHandler.assert_called_once_with(unittest.mock.ANY) # sys.stdout
        mock_console_handler_instance.setFormatter.assert_called_once_with(mock_formatter_instance)
        mock_console_handler_instance.setLevel.assert_called_once_with(logging.INFO)
        
        mock_root_logger.addHandler.assert_called_once_with(mock_console_handler_instance)
        mock_root_logger.setLevel.assert_called_once_with(logging.INFO)
        
        mock_FileHandler.assert_not_called() # Não deve chamar FileHandler

    @patch('fotix.infrastructure.logging_config.Path.mkdir')
    @patch('fotix.infrastructure.logging_config.RotatingFileHandler') # Usando RotatingFileHandler
    @patch('fotix.infrastructure.logging_config.logging.StreamHandler')
    @patch('fotix.infrastructure.logging_config.logging.Formatter')
    @patch('fotix.infrastructure.logging_config.logging.getLogger')
    def test_setup_logging_with_file(
        self, 
        mock_getLogger, 
        mock_Formatter, 
        mock_StreamHandler, 
        mock_RotatingFileHandler, # Mock para RotatingFileHandler
        mock_mkdir
    ):
        """Testa a configuração de logging com console e arquivo."""
        mock_root_logger = MagicMock()
        mock_getLogger.return_value = mock_root_logger
        
        mock_formatter_instance = MagicMock()
        mock_Formatter.return_value = mock_formatter_instance

        mock_console_handler_instance = MagicMock()
        mock_StreamHandler.return_value = mock_console_handler_instance
        
        mock_file_handler_instance = MagicMock()
        mock_RotatingFileHandler.return_value = mock_file_handler_instance

        log_file_str = "/tmp/test_app.log" # Usar string para simular entrada de config
        config_dict = {
            "LOG_LEVEL": "DEBUG",
            "LOG_FORMAT": "%(levelname)s: %(message)s",
            "LOG_FILE_PATH": Path(log_file_str), # Criar Path aqui como AppSettings faria
            "BACKUP_PATH": Path("/tmp/backup_file_test")
        }
        config = AppSettings(**config_dict)

        setup_logging(config)

        mock_getLogger.assert_called_once_with()
        mock_Formatter.assert_called_once_with("%(levelname)s: %(message)s")
        
        # Verifica console handler
        mock_StreamHandler.assert_called_once_with(unittest.mock.ANY) # sys.stdout
        mock_console_handler_instance.setFormatter.assert_called_once_with(mock_formatter_instance)
        mock_console_handler_instance.setLevel.assert_called_once_with(logging.DEBUG)
        
        # Verifica file handler (RotatingFileHandler)
        # Espera o caminho absoluto que Path() resolveria no sistema atual.
        expected_log_file_path = Path(log_file_str).resolve()
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_RotatingFileHandler.assert_called_once_with(
            expected_log_file_path, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
        )
        mock_file_handler_instance.setFormatter.assert_called_once_with(mock_formatter_instance)
        mock_file_handler_instance.setLevel.assert_called_once_with(logging.DEBUG)

        # Verifica se ambos os handlers foram adicionados
        self.assertEqual(mock_root_logger.addHandler.call_count, 2)
        mock_root_logger.addHandler.assert_any_call(mock_console_handler_instance)
        mock_root_logger.addHandler.assert_any_call(mock_file_handler_instance)
        
        mock_root_logger.setLevel.assert_called_once_with(logging.DEBUG)

    @patch('fotix.infrastructure.logging_config.logging.basicConfig')
    @patch('fotix.infrastructure.logging_config.logging.getLogger')
    def test_setup_logging_exception_fallback(self, mock_getLogger, mock_basicConfig):
        """Testa o fallback do logging em caso de exceção na configuração."""
        mock_getLogger.side_effect = Exception("Erro ao obter logger")

        config_dict = {
            "LOG_LEVEL": "INFO",
            "LOG_FORMAT": "%(message)s",
            "LOG_FILE_PATH": None,
            "BACKUP_PATH": Path("/tmp/backup_exception")
        }
        config = AppSettings(**config_dict)
        
        setup_logging(config)

        # mock_basicConfig.assert_called_once()
        # Verifica se o nível e o formato do fallback estão corretos (parcialmente)
        # A chamada principal que nos interessa é a que define level e format.
        # Se houver outras chamadas (como a implícita de logging.critical), elas podem não ter todos os args.
        # Por isso, verificamos se *alguma* chamada corresponde aos nossos parâmetros de fallback.

        # Extrai a formatação da chamada real que tem os argumentos que esperamos
        found_correct_call = False
        for c_args, c_kwargs in mock_basicConfig.call_args_list: # Desempacota args e kwargs diretamente
            if c_kwargs.get('level') == logging.WARNING and \
               "[ERRO NA CONFIG DE LOG]" in c_kwargs.get('format', ""):
                found_correct_call = True
                break
        self.assertTrue(found_correct_call, msg="Chamada esperada para basicConfig com parâmetros de fallback não encontrada")

    @patch('fotix.infrastructure.logging_config.logging.StreamHandler')
    @patch('fotix.infrastructure.logging_config.logging.FileHandler')
    @patch('fotix.infrastructure.logging_config.logging.Formatter')
    @patch('fotix.infrastructure.logging_config.logging.getLogger')
    def test_setup_logging_clears_existing_handlers(
        self, 
        mock_getLogger, 
        mock_Formatter, 
        mock_FileHandler,
        mock_StreamHandler
    ):
        """Testa se os handlers existentes são limpos antes de adicionar novos."""
        mock_root_logger = MagicMock()
        # Simula que o logger já tem handlers
        mock_existing_handler1 = MagicMock()
        mock_existing_handler2 = MagicMock()
        mock_root_logger.handlers = [mock_existing_handler1, mock_existing_handler2]
        mock_root_logger.hasHandlers.return_value = True # Garante que hasHandlers() retorne True

        mock_getLogger.return_value = mock_root_logger
        
        mock_formatter_instance = MagicMock()
        mock_Formatter.return_value = mock_formatter_instance

        mock_console_handler_instance = MagicMock()
        mock_StreamHandler.return_value = mock_console_handler_instance

        config_dict = {
            "LOG_LEVEL": "INFO",
            "LOG_FORMAT": "%(message)s",
            "LOG_FILE_PATH": None,
            "BACKUP_PATH": Path("/tmp/backup_clear_handlers")
        }
        config = AppSettings(**config_dict)

        setup_logging(config)

        # Verifica se os handlers existentes foram removidos
        mock_root_logger.removeHandler.assert_any_call(mock_existing_handler1)
        mock_root_logger.removeHandler.assert_any_call(mock_existing_handler2)
        mock_existing_handler1.close.assert_called_once()
        mock_existing_handler2.close.assert_called_once()
        
        # Verifica se o novo handler foi adicionado
        mock_root_logger.addHandler.assert_called_with(mock_console_handler_instance)


if __name__ == '__main__': # pragma: no cover
    unittest.main() 