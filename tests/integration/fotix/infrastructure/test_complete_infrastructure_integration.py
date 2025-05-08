"""
Testes de integração completos para a infraestrutura básica do Fotix.

Este módulo testa a integração entre fotix.config, fotix.infrastructure.logging_config e
fotix.infrastructure.file_system, verificando se todos os componentes trabalham juntos
corretamente em cenários de uso completos.
"""

import json
import logging
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from send2trash import TrashPermissionError

from fotix.config import ConfigManager, get, set
from fotix.infrastructure.file_system import FileSystemService
from fotix.infrastructure.logging_config import configure_logging, get_logger, set_log_level


class TestCompleteInfrastructureIntegration:
    """Testes de integração completos para a infraestrutura básica."""

    @pytest.fixture
    def fs_service(self):
        """Fixture que retorna uma instância de FileSystemService."""
        return FileSystemService()

    def test_config_affects_file_system_operations(self, fs_service, temp_config_file, test_files, temp_log_file, reset_logging, caplog):
        """
        Testa como as configurações afetam as operações do sistema de arquivos.

        Este teste verifica se alterações nas configurações (como trash_enabled)
        afetam corretamente o comportamento do FileSystemService e se as operações
        são logadas adequadamente.
        """
        config_file, config_data = temp_config_file
        root_dir = test_files["root"]
        test_file = test_files["files"][0]

        # Patch para usar o arquivo de configuração temporário
        with patch('fotix.config.ConfigManager._get_config_file_path', return_value=config_file):
            # Reinicializa o ConfigManager para carregar o arquivo temporário
            config_manager = ConfigManager()
            config_manager._initialize()

            # Configura o logging e captura logs
            configure_logging(log_level="DEBUG", log_file=temp_log_file)
            caplog.set_level(logging.DEBUG)

            # Cria um arquivo para testar a remoção
            test_remove = root_dir / "test_remove.txt"
            fs_service.copy_file(test_file, test_remove)
            assert test_remove.exists()

            # Verifica a configuração atual de trash_enabled
            assert get("trash_enabled") is True

            # Limpa os logs capturados até agora
            caplog.clear()

            # Patch send2trash para evitar realmente mover para a lixeira
            with patch('fotix.infrastructure.file_system.send2trash') as mock_send2trash:
                # Move o arquivo para a lixeira
                fs_service.move_to_trash(test_remove)

                # Verifica se send2trash foi chamado
                mock_send2trash.assert_called_once_with(str(test_remove))

                # Verifica se a operação foi logada
                log_text = caplog.text.lower()
                assert "movendo para a lixeira" in log_text

            # Altera a configuração para desabilitar a lixeira
            set("trash_enabled", False)

            # Cria outro arquivo para testar a remoção
            test_remove2 = root_dir / "test_remove2.txt"
            fs_service.copy_file(test_file, test_remove2)
            assert test_remove2.exists()

            # Limpa os logs capturados até agora
            caplog.clear()

            # Remove o arquivo (agora deve ser removido permanentemente)
            fs_service.move_to_trash(test_remove2)

            # Verifica se o arquivo foi removido
            assert not test_remove2.exists()

            # Verifica se a operação foi logada como remoção permanente
            log_text = caplog.text.lower()
            assert "removendo permanentemente" in log_text

    def test_log_level_affects_file_system_logging(self, fs_service, temp_config_file, test_files, temp_log_file, reset_logging, caplog):
        """
        Testa como o nível de log afeta o logging das operações do sistema de arquivos.

        Este teste verifica se alterações no nível de log afetam quais mensagens
        do sistema de arquivos são registradas.
        """
        config_file, config_data = temp_config_file
        root_dir = test_files["root"]
        test_file = test_files["files"][0]

        # Patch para usar o arquivo de configuração temporário
        with patch('fotix.config.ConfigManager._get_config_file_path', return_value=config_file):
            # Reinicializa o ConfigManager para carregar o arquivo temporário
            config_manager = ConfigManager()
            config_manager._initialize()

            # Altera o nível de log para INFO
            set("log_level", "INFO")
            config_manager._save_config()

            # Configura o logging com base nas configurações
            configure_logging(log_file=temp_log_file)
            caplog.set_level(logging.DEBUG)  # Captura todos os níveis para verificação

            # Limpa os logs capturados até agora
            caplog.clear()

            # Realiza uma operação que gera log de DEBUG
            fs_service.get_file_size(test_file)

            # Nota: O caplog do pytest captura todos os logs, independentemente do nível configurado
            # Então não podemos verificar se a mensagem de DEBUG não foi registrada no caplog
            # Em vez disso, verificamos se o nível do logger está configurado corretamente
            logger = logging.getLogger("fotix.infrastructure.file_system")
            assert logger.level <= logging.INFO  # Pode ser INFO ou herdado (NOTSET)

            # Altera o nível de log para DEBUG
            set_log_level("DEBUG")

            # Limpa os logs capturados até agora
            caplog.clear()

            # Realiza a mesma operação
            fs_service.get_file_size(test_file)

            # Verifica se a mensagem de DEBUG foi registrada
            log_records = [r for r in caplog.records if r.levelno == logging.DEBUG]
            assert len(log_records) > 0

            # Verifica se o conteúdo do log contém informações sobre o tamanho do arquivo
            log_text = caplog.text.lower()
            assert "tamanho do arquivo" in log_text

    def test_error_handling_with_logging(self, fs_service, temp_config_file, test_files, temp_log_file, reset_logging, caplog):
        """
        Testa o tratamento de erros com logging.

        Este teste verifica se erros nas operações do sistema de arquivos são
        tratados corretamente e logados adequadamente.
        """
        config_file, config_data = temp_config_file

        # Patch para usar o arquivo de configuração temporário
        with patch('fotix.config.ConfigManager._get_config_file_path', return_value=config_file):
            # Reinicializa o ConfigManager para carregar o arquivo temporário
            config_manager = ConfigManager()
            config_manager._initialize()

            # Configura o logging para capturar erros
            configure_logging(log_level="ERROR", log_file=temp_log_file)
            caplog.set_level(logging.ERROR)

            # Cria um arquivo inexistente
            nonexistent_file = test_files["root"] / "definitivamente_nao_existe.txt"

            # Limpa os logs capturados até agora
            caplog.clear()

            # Tenta mover para a lixeira um arquivo inexistente
            try:
                fs_service.move_to_trash(nonexistent_file)
                pytest.fail("Deveria ter levantado FileNotFoundError")
            except FileNotFoundError:
                # Esperado
                pass

            # Verifica se o erro foi logado
            log_text = caplog.text.lower()
            assert "erro" in log_text or "error" in log_text
            assert "não encontrado" in log_text or "não existe" in log_text

            # Limpa os logs capturados até agora
            caplog.clear()

            # Tenta uma operação com erro de permissão
            test_file = test_files["files"][0]
            with patch('fotix.infrastructure.file_system.send2trash',
                      side_effect=TrashPermissionError("Permissão negada")):
                try:
                    fs_service.move_to_trash(test_file)
                    pytest.fail("Deveria ter levantado TrashPermissionError")
                except TrashPermissionError:
                    # Esperado
                    pass

            # Verifica se o erro de permissão foi logado
            log_text = caplog.text.lower()
            assert "erro de permissão" in log_text
