"""
Testes unitários para o módulo de configuração de logging.
"""

import logging
import tempfile
from pathlib import Path
from unittest import mock

from fotix.infrastructure.logging_config import setup_logging, get_logger, reconfigure_logging


class TestSetupLogging:
    """Testes para a função setup_logging."""

    def test_setup_logging_with_defaults(self):
        """Testa se setup_logging configura o logger raiz com valores padrão."""
        # Mock para get_log_level e get_config
        with mock.patch('fotix.infrastructure.logging_config.get_log_level', return_value=logging.INFO), \
             mock.patch('fotix.infrastructure.logging_config.get_config', return_value={"log_file": None}):

            # Salvar os handlers originais
            original_handlers = logging.getLogger().handlers.copy()

            try:
                # Configurar o logging
                logger = setup_logging()

                # Verificar se o logger foi configurado corretamente
                assert logger.level == logging.INFO

                # Verificar se pelo menos um handler é StreamHandler
                stream_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
                assert len(stream_handlers) >= 1
            finally:
                # Restaurar os handlers originais
                root_logger = logging.getLogger()
                for handler in root_logger.handlers[:]:
                    root_logger.removeHandler(handler)
                for handler in original_handlers:
                    root_logger.addHandler(handler)

    def test_setup_logging_with_custom_level(self):
        """Testa se setup_logging configura o logger raiz com nível personalizado."""
        # Salvar os handlers originais
        original_handlers = logging.getLogger().handlers.copy()
        original_level = logging.getLogger().level

        try:
            # Configurar o logging com nível personalizado
            logger = setup_logging(log_level=logging.DEBUG, log_file=None)

            # Verificar se o logger foi configurado corretamente
            assert logger.level == logging.DEBUG
        finally:
            # Restaurar os handlers originais e o nível
            root_logger = logging.getLogger()
            root_logger.setLevel(original_level)
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
            for handler in original_handlers:
                root_logger.addHandler(handler)

    def test_setup_logging_with_string_level(self):
        """Testa se setup_logging aceita níveis de log como strings."""
        # Salvar os handlers originais
        original_handlers = logging.getLogger().handlers.copy()
        original_level = logging.getLogger().level

        try:
            # Configurar o logging com nível como string
            logger = setup_logging(log_level="ERROR", log_file=None)

            # Verificar se o logger foi configurado corretamente
            assert logger.level == logging.ERROR
        finally:
            # Restaurar os handlers originais e o nível
            root_logger = logging.getLogger()
            root_logger.setLevel(original_level)
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
            for handler in original_handlers:
                root_logger.addHandler(handler)

    def test_setup_logging_with_file(self):
        """Testa se setup_logging configura o logger raiz com arquivo de log."""
        # Criar um diretório temporário para o arquivo de log
        temp_dir = tempfile.mkdtemp()
        try:
            log_file = Path(temp_dir) / "test.log"

            # Salvar os handlers originais
            original_handlers = logging.getLogger().handlers.copy()
            original_level = logging.getLogger().level

            try:
                # Configurar o logging com arquivo
                logger = setup_logging(log_level=logging.INFO, log_file=log_file, console=False)

                # Verificar se o logger foi configurado corretamente
                assert logger.level == logging.INFO

                # Verificar se há pelo menos um RotatingFileHandler
                file_handlers = [h for h in logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
                assert len(file_handlers) >= 1

                # Verificar se o arquivo de log foi criado
                assert log_file.exists()
            finally:
                # Restaurar os handlers originais e o nível
                root_logger = logging.getLogger()
                root_logger.setLevel(original_level)
                for handler in root_logger.handlers[:]:
                    # Fechar o handler antes de removê-lo
                    handler.close()
                    root_logger.removeHandler(handler)
                for handler in original_handlers:
                    root_logger.addHandler(handler)
        finally:
            # Limpar o diretório temporário manualmente
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass

    def test_setup_logging_creates_log_directory(self):
        """Testa se setup_logging cria o diretório do arquivo de log se não existir."""
        # Criar um diretório temporário para o arquivo de log
        temp_dir = tempfile.mkdtemp()
        try:
            log_dir = Path(temp_dir) / "logs"
            log_file = log_dir / "test.log"

            # Salvar os handlers originais
            original_handlers = logging.getLogger().handlers.copy()
            original_level = logging.getLogger().level

            try:
                # Configurar o logging com arquivo em diretório que não existe
                setup_logging(log_level=logging.INFO, log_file=log_file, console=False)

                # Verificar se o diretório foi criado
                assert log_dir.exists()
                assert log_file.exists()
            finally:
                # Restaurar os handlers originais e o nível
                root_logger = logging.getLogger()
                root_logger.setLevel(original_level)
                for handler in root_logger.handlers[:]:
                    # Fechar o handler antes de removê-lo
                    handler.close()
                    root_logger.removeHandler(handler)
                for handler in original_handlers:
                    root_logger.addHandler(handler)
        finally:
            # Limpar o diretório temporário manualmente
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass

    def test_setup_logging_reconfigures_existing_logger(self):
        """Testa se setup_logging reconfigura um logger existente."""
        # Salvar os handlers originais
        original_handlers = logging.getLogger().handlers.copy()
        original_level = logging.getLogger().level

        try:
            # Configurar o logging inicialmente
            logger1 = setup_logging(log_level=logging.INFO, log_file=None)

            # Reconfigurar o logging
            logger2 = setup_logging(log_level=logging.DEBUG, log_file=None)

            # Verificar se o logger foi reconfigurado
            assert logger2.level == logging.DEBUG

            # Verificar se é o mesmo logger (raiz)
            assert logger1 is logger2
        finally:
            # Restaurar os handlers originais e o nível
            root_logger = logging.getLogger()
            root_logger.setLevel(original_level)
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
            for handler in original_handlers:
                root_logger.addHandler(handler)


class TestGetLogger:
    """Testes para a função get_logger."""

    def test_get_logger_configures_root_if_needed(self):
        """Testa se get_logger configura o logger raiz se ainda não configurado."""
        # Resetar o estado do módulo
        import fotix.infrastructure.logging_config
        fotix.infrastructure.logging_config._root_logger_configured = False

        # Mock para setup_logging
        with mock.patch('fotix.infrastructure.logging_config.setup_logging') as mock_setup:
            mock_setup.return_value = logging.getLogger()

            # Obter um logger
            get_logger("test_module")

            # Verificar se setup_logging foi chamado
            mock_setup.assert_called_once()

    def test_get_logger_returns_correct_logger(self):
        """Testa se get_logger retorna o logger correto para o nome especificado."""
        # Salvar os handlers originais
        original_handlers = logging.getLogger().handlers.copy()
        original_level = logging.getLogger().level

        try:
            # Configurar o logging
            setup_logging(log_level=logging.INFO, log_file=None)

            # Obter um logger
            logger = get_logger("test_module")

            # Verificar se o logger tem o nome correto
            assert logger.name == "test_module"
        finally:
            # Restaurar os handlers originais e o nível
            root_logger = logging.getLogger()
            root_logger.setLevel(original_level)
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
            for handler in original_handlers:
                root_logger.addHandler(handler)


class TestReconfigureLogging:
    """Testes para a função reconfigure_logging."""

    def test_reconfigure_logging_calls_setup_logging(self):
        """Testa se reconfigure_logging chama setup_logging."""
        # Mock para setup_logging
        with mock.patch('fotix.infrastructure.logging_config.setup_logging') as mock_setup:
            # Chamar reconfigure_logging
            reconfigure_logging()

            # Verificar se setup_logging foi chamado
            mock_setup.assert_called_once()


class TestIntegration:
    """Testes de integração para o módulo de logging_config."""

    def test_log_message_to_file(self):
        """Testa se uma mensagem de log é escrita no arquivo."""
        # Criar um diretório temporário para o arquivo de log
        temp_dir = tempfile.mkdtemp()
        try:
            log_file = Path(temp_dir) / "test.log"

            # Salvar os handlers originais
            original_handlers = logging.getLogger().handlers.copy()
            original_level = logging.getLogger().level

            try:
                # Configurar o logging com arquivo
                setup_logging(log_level=logging.DEBUG, log_file=log_file, console=False)

                # Obter um logger e escrever uma mensagem
                logger = get_logger("test_integration")
                test_message = "Mensagem de teste para arquivo"
                logger.info(test_message)

                # Verificar se a mensagem foi escrita no arquivo
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                    assert test_message in log_content
            finally:
                # Restaurar os handlers originais e o nível
                root_logger = logging.getLogger()
                root_logger.setLevel(original_level)
                for handler in root_logger.handlers[:]:
                    # Fechar o handler antes de removê-lo
                    handler.close()
                    root_logger.removeHandler(handler)
                for handler in original_handlers:
                    root_logger.addHandler(handler)
        finally:
            # Limpar o diretório temporário manualmente
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass

    def test_log_respects_level(self):
        """Testa se o logger respeita o nível configurado."""
        # Criar um diretório temporário para o arquivo de log
        temp_dir = tempfile.mkdtemp()
        try:
            log_file = Path(temp_dir) / "test.log"

            # Salvar os handlers originais
            original_handlers = logging.getLogger().handlers.copy()
            original_level = logging.getLogger().level

            try:
                # Configurar o logging com nível INFO
                setup_logging(log_level=logging.INFO, log_file=log_file, console=False)

                # Obter um logger e escrever mensagens em diferentes níveis
                logger = get_logger("test_integration")
                debug_message = "Mensagem de DEBUG que não deve aparecer"
                info_message = "Mensagem de INFO que deve aparecer"

                logger.debug(debug_message)
                logger.info(info_message)

                # Verificar se apenas a mensagem INFO foi escrita no arquivo
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                    assert debug_message not in log_content
                    assert info_message in log_content
            finally:
                # Restaurar os handlers originais e o nível
                root_logger = logging.getLogger()
                root_logger.setLevel(original_level)
                for handler in root_logger.handlers[:]:
                    # Fechar o handler antes de removê-lo
                    handler.close()
                    root_logger.removeHandler(handler)
                for handler in original_handlers:
                    root_logger.addHandler(handler)
        finally:
            # Limpar o diretório temporário manualmente
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
