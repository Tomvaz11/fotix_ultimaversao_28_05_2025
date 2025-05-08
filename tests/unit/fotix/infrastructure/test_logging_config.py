"""
Testes unitários para o módulo de configuração de logging do Fotix.
"""

import os
import sys
import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Adiciona o diretório src ao path para permitir importações
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../src')))

# Importa o módulo a ser testado
from fotix.infrastructure import logging_config
from fotix.infrastructure.logging_config import configure_logging, get_logger, set_log_level


class TestLoggingConfig(unittest.TestCase):
    """Testes para o módulo de configuração de logging."""

    def setUp(self):
        """Configuração inicial para os testes."""
        # Reseta o estado do singleton
        logging_config._logging_configured = False

        # Limpa os handlers do logger raiz
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Cria um diretório temporário para os logs
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_file = Path(self.temp_dir.name) / "test_log.log"

    def tearDown(self):
        """Limpeza após os testes."""
        # Limpa os handlers do logger raiz
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            # Fecha o handler antes de removê-lo
            handler.close()
            root_logger.removeHandler(handler)

        # Reseta o estado do singleton
        logging_config._logging_configured = False

        # Remove o diretório temporário
        try:
            self.temp_dir.cleanup()
        except PermissionError:
            # No Windows, às vezes os arquivos de log não são liberados imediatamente
            # Ignoramos esse erro, pois os arquivos temporários serão limpos pelo sistema
            pass

    @patch('fotix.infrastructure.logging_config.get_log_level')
    @patch('fotix.infrastructure.logging_config.get_log_file')
    def test_configure_logging_default(self, mock_get_log_file, mock_get_log_level):
        """Testa a configuração padrão do logging."""
        # Configura os mocks
        mock_get_log_level.return_value = logging.INFO
        mock_get_log_file.return_value = self.log_file

        # Configura o logging
        configure_logging()

        # Verifica se os mocks foram chamados
        mock_get_log_level.assert_called_once()
        mock_get_log_file.assert_called_once()

        # Verifica se o logger raiz foi configurado corretamente
        root_logger = logging.getLogger()
        self.assertEqual(root_logger.level, logging.INFO)

        # Verifica se os handlers foram adicionados
        self.assertEqual(len(root_logger.handlers), 2)  # Console e arquivo

        # Verifica se o diretório do log foi criado
        self.assertTrue(self.log_file.parent.exists())

    def test_configure_logging_custom_level(self):
        """Testa a configuração do logging com nível personalizado."""
        # Configura o logging com nível DEBUG
        configure_logging(log_level=logging.DEBUG, log_file=self.log_file)

        # Verifica se o logger raiz foi configurado corretamente
        root_logger = logging.getLogger()
        self.assertEqual(root_logger.level, logging.DEBUG)

    def test_configure_logging_string_level(self):
        """Testa a configuração do logging com nível como string."""
        # Configura o logging com nível "DEBUG"
        configure_logging(log_level="DEBUG", log_file=self.log_file)

        # Verifica se o logger raiz foi configurado corretamente
        root_logger = logging.getLogger()
        self.assertEqual(root_logger.level, logging.DEBUG)

    def test_configure_logging_invalid_string_level(self):
        """Testa a configuração do logging com nível string inválido."""
        # Configura o logging com nível inválido (deve usar INFO como fallback)
        configure_logging(log_level="INVALID", log_file=self.log_file)

        # Verifica se o logger raiz foi configurado com INFO
        root_logger = logging.getLogger()
        self.assertEqual(root_logger.level, logging.INFO)

    def test_configure_logging_console_only(self):
        """Testa a configuração do logging apenas para console."""
        # Configura o logging apenas para console
        configure_logging(log_file=self.log_file, console_output=True, file_output=False)

        # Verifica se apenas o handler de console foi adicionado
        root_logger = logging.getLogger()
        self.assertEqual(len(root_logger.handlers), 1)

        # Verifica se o handler é do tipo StreamHandler
        self.assertIsInstance(root_logger.handlers[0], logging.StreamHandler)

    def test_configure_logging_file_only(self):
        """Testa a configuração do logging apenas para arquivo."""
        # Configura o logging apenas para arquivo
        configure_logging(log_file=self.log_file, console_output=False, file_output=True)

        # Verifica se apenas o handler de arquivo foi adicionado
        root_logger = logging.getLogger()
        self.assertEqual(len(root_logger.handlers), 1)

        # Verifica se o handler é do tipo RotatingFileHandler
        from logging.handlers import RotatingFileHandler
        self.assertIsInstance(root_logger.handlers[0], RotatingFileHandler)

    def test_configure_logging_custom_format(self):
        """Testa a configuração do logging com formato personalizado."""
        # Define um formato personalizado
        custom_format = "%(levelname)s - %(message)s"

        # Configura o logging com formato personalizado
        configure_logging(log_file=self.log_file, log_format=custom_format)

        # Verifica se o formato foi aplicado aos handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            self.assertEqual(handler.formatter._fmt, custom_format)

    def test_configure_logging_once(self):
        """Testa que o logging é configurado apenas uma vez."""
        # Configura o logging pela primeira vez
        configure_logging(log_level=logging.DEBUG, log_file=self.log_file)

        # Verifica o nível inicial
        root_logger = logging.getLogger()
        self.assertEqual(root_logger.level, logging.DEBUG)

        # Tenta configurar novamente com um nível diferente
        configure_logging(log_level=logging.ERROR, log_file=self.log_file)

        # Verifica que o nível não mudou (ainda é DEBUG)
        self.assertEqual(root_logger.level, logging.DEBUG)

    def test_get_logger(self):
        """Testa a obtenção de um logger configurado."""
        # Obtém um logger
        logger = get_logger("test_module")

        # Verifica se o logger tem o nome correto
        self.assertEqual(logger.name, "test_module")

        # Verifica se o logging foi configurado
        self.assertTrue(logging_config._logging_configured)

    @patch('fotix.infrastructure.logging_config.configure_logging')
    def test_get_logger_configures_if_needed(self, mock_configure_logging):
        """Testa que get_logger configura o logging se necessário."""
        # Reseta o estado do singleton
        logging_config._logging_configured = False

        # Obtém um logger (não precisamos verificar o retorno, apenas que configure_logging foi chamado)
        get_logger("test_module")

        # Verifica se configure_logging foi chamado
        mock_configure_logging.assert_called_once()

    def test_set_log_level(self):
        """Testa a alteração do nível de log em tempo de execução."""
        # Configura o logging inicialmente com INFO
        configure_logging(log_level=logging.INFO, log_file=self.log_file)

        # Verifica o nível inicial
        root_logger = logging.getLogger()
        self.assertEqual(root_logger.level, logging.INFO)

        # Altera o nível para DEBUG
        set_log_level(logging.DEBUG)

        # Verifica se o nível foi alterado
        self.assertEqual(root_logger.level, logging.DEBUG)

    def test_set_log_level_string(self):
        """Testa a alteração do nível de log usando string."""
        # Configura o logging inicialmente com INFO
        configure_logging(log_level=logging.INFO, log_file=self.log_file)

        # Verifica o nível inicial
        root_logger = logging.getLogger()
        self.assertEqual(root_logger.level, logging.INFO)

        # Altera o nível para DEBUG usando string
        set_log_level("DEBUG")

        # Verifica se o nível foi alterado
        self.assertEqual(root_logger.level, logging.DEBUG)

    def test_logging_to_file(self):
        """Testa se as mensagens de log são gravadas no arquivo."""
        # Configura o logging
        configure_logging(log_file=self.log_file, console_output=False)

        # Envia uma mensagem de log
        logging.info("Mensagem de teste")

        # Verifica se a mensagem foi gravada no arquivo
        with open(self.log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()

        self.assertIn("Mensagem de teste", log_content)

    def test_logging_to_console(self):
        """Testa se as mensagens de log são enviadas para o console."""
        # Configura o logging apenas para console
        configure_logging(log_file=self.log_file, file_output=False)

        # Não podemos verificar diretamente a saída do console em um teste unitário,
        # mas podemos verificar se o handler de console foi configurado corretamente
        root_logger = logging.getLogger()
        self.assertEqual(len(root_logger.handlers), 1)
        self.assertIsInstance(root_logger.handlers[0], logging.StreamHandler)

    def test_configure_logging_string_path(self):
        """Testa a configuração do logging com caminho de arquivo como string."""
        # Converte o caminho Path para string
        log_file_str = str(self.log_file)

        # Configura o logging com caminho como string
        configure_logging(log_file=log_file_str)

        # Verifica se o logging foi configurado corretamente
        root_logger = logging.getLogger()

        # Deve haver dois handlers (console e arquivo)
        self.assertEqual(len(root_logger.handlers), 2)

        # Verifica se o arquivo de log foi criado
        self.assertTrue(Path(log_file_str).exists())


if __name__ == '__main__':
    unittest.main()
