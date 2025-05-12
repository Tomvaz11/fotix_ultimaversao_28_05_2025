"""
Testes unitários para o módulo fotix.main.

Este módulo contém testes unitários para o ponto de entrada principal da aplicação Fotix.
"""

import sys
import unittest
from unittest.mock import patch, MagicMock

import pytest

# Aplicar patch no logger antes de importar o módulo main
with patch('fotix.infrastructure.logging_config.get_logger'):
    from fotix.main import main, setup_application


class TestSetupApplication(unittest.TestCase):
    """Testes para a função setup_application."""

    @patch('fotix.main.QApplication')
    def test_setup_application_configures_app_correctly(self, mock_qapp):
        """Testa se a função setup_application configura a aplicação corretamente."""
        # Configurar o mock
        mock_app_instance = MagicMock()
        mock_qapp.instance.return_value = None
        mock_qapp.return_value = mock_app_instance

        # Chamar a função
        result = setup_application()

        # Verificar se QApplication.instance() foi chamado
        mock_qapp.instance.assert_called_once()

        # Verificar se QApplication foi criado com sys.argv (apenas se não existir instância)
        mock_qapp.assert_called_once_with(sys.argv)

        # Verificar se os métodos de configuração foram chamados corretamente
        mock_app_instance.setOrganizationName.assert_called_once_with("Fotix")
        mock_app_instance.setApplicationName.assert_called_once_with("Fotix - Gerenciador de Duplicatas")
        mock_app_instance.setStyle.assert_called_once_with("Fusion")

        # Verificar se a função retorna a instância de QApplication
        self.assertEqual(result, mock_app_instance)

    @patch('fotix.main.QApplication')
    def test_setup_application_reuses_existing_app(self, mock_qapp):
        """Testa se a função setup_application reutiliza uma instância existente de QApplication."""
        # Configurar o mock para simular uma instância existente
        mock_existing_app = MagicMock()
        mock_qapp.instance.return_value = mock_existing_app

        # Chamar a função
        result = setup_application()

        # Verificar se QApplication.instance() foi chamado
        mock_qapp.instance.assert_called_once()

        # Verificar se QApplication não foi criado novamente
        mock_qapp.assert_not_called()

        # Verificar se os métodos de configuração foram chamados na instância existente
        mock_existing_app.setOrganizationName.assert_called_once_with("Fotix")
        mock_existing_app.setApplicationName.assert_called_once_with("Fotix - Gerenciador de Duplicatas")
        mock_existing_app.setStyle.assert_called_once_with("Fusion")

        # Verificar se a função retorna a instância existente
        self.assertEqual(result, mock_existing_app)


class TestMain(unittest.TestCase):
    """Testes para a função main."""

    @patch('fotix.main.logger')  # Patch diretamente o logger do módulo
    @patch('fotix.main.setup_logging')
    @patch('fotix.main.get_log_level')
    @patch('fotix.main.get_config')
    @patch('fotix.main.setup_application')
    @patch('fotix.main.MainWindow')
    def test_main_success_flow(self, mock_main_window, mock_setup_application,
                              mock_get_config, mock_get_log_level,
                              mock_setup_logging, mock_logger):
        """Testa o fluxo de sucesso da função main."""
        # Configurar os mocks
        mock_app = MagicMock()
        mock_app.exec.return_value = 0
        mock_setup_application.return_value = mock_app

        mock_window = MagicMock()
        mock_main_window.return_value = mock_window

        mock_get_log_level.return_value = "INFO"
        mock_get_config.return_value = {"key": "value"}

        # Chamar a função
        result = main()

        # Verificar se as funções foram chamadas corretamente
        mock_get_log_level.assert_called_once()
        mock_setup_logging.assert_called_once_with(log_level="INFO")
        mock_get_config.assert_called_once()
        mock_setup_application.assert_called_once()
        mock_main_window.assert_called_once()
        mock_window.show.assert_called_once()
        mock_app.exec.assert_called_once()

        # Verificar se o logger foi usado corretamente
        assert mock_logger.info.call_count >= 2
        assert mock_logger.debug.call_count >= 1

        # Verificar se a função retorna o código de saída correto
        self.assertEqual(result, 0)

    @patch('fotix.main.logger')  # Patch diretamente o logger do módulo
    @patch('fotix.main.setup_logging')
    @patch('fotix.main.get_log_level')
    def test_main_handles_exceptions(self, mock_get_log_level, mock_setup_logging, mock_logger):
        """Testa se a função main trata exceções corretamente."""
        # Fazer get_log_level lançar uma exceção
        mock_get_log_level.side_effect = Exception("Erro de teste")

        # Chamar a função
        with patch('builtins.print') as mock_print:
            result = main()

        # Verificar se o logger registrou o erro
        mock_logger.critical.assert_called_once()
        self.assertIn("Erro de teste", mock_logger.critical.call_args[0][0])

        # Verificar se a mensagem foi impressa no console
        mock_print.assert_called_once()
        self.assertIn("Erro de teste", mock_print.call_args[0][0])

        # Verificar que setup_logging não foi chamado quando get_log_level lançou exceção
        mock_setup_logging.assert_not_called()

        # Verificar se a função retorna o código de erro
        self.assertEqual(result, 1)


if __name__ == '__main__':
    pytest.main(['-xvs', __file__])
