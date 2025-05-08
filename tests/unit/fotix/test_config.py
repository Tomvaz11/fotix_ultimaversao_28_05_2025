"""
Testes unitários para o módulo de configuração do Fotix.
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import logging

# Adiciona o diretório src ao path para permitir importações
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

# Importa o módulo a ser testado
from fotix.config import (
    ConfigManager, get, set, get_backup_dir, get_log_level, get_log_file,
    get_max_workers, get_chunk_size, get_supported_extensions,
    is_scan_inside_archives_enabled, is_trash_enabled, reset_to_defaults,
    DEFAULT_CONFIG
)


class TestConfigManager(unittest.TestCase):
    """Testes para a classe ConfigManager."""

    def setUp(self):
        """Configura o ambiente de teste."""
        # Cria um diretório temporário para os testes
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "test_config.json"

        # Patch para o método _get_config_file_path
        self.patcher = patch.object(
            ConfigManager, '_get_config_file_path',
            return_value=self.config_path
        )
        self.mock_get_path = self.patcher.start()

        # Reseta o singleton para cada teste
        ConfigManager._instance = None

    def tearDown(self):
        """Limpa o ambiente após cada teste."""
        self.patcher.stop()
        self.temp_dir.cleanup()
        ConfigManager._instance = None

    def test_singleton_pattern(self):
        """Testa se o padrão Singleton está funcionando corretamente."""
        config1 = ConfigManager()
        config2 = ConfigManager()
        self.assertIs(config1, config2)

    def test_default_config(self):
        """Testa se as configurações padrão são carregadas corretamente."""
        config = ConfigManager()
        for key, value in DEFAULT_CONFIG.items():
            self.assertEqual(config.get(key), value)

    def test_load_config(self):
        """Testa o carregamento de configurações de um arquivo."""
        # Cria um arquivo de configuração de teste
        test_config = {
            "backup_dir": "/test/backup",
            "log_level": "DEBUG"
        }
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(test_config, f)

        # Instancia o ConfigManager, que deve carregar o arquivo
        config = ConfigManager()

        # Verifica se as configurações foram carregadas corretamente
        self.assertEqual(config.get("backup_dir"), "/test/backup")
        self.assertEqual(config.get("log_level"), "DEBUG")

        # Verifica se as configurações padrão não especificadas no arquivo foram mantidas
        self.assertEqual(config.get("max_workers"), DEFAULT_CONFIG["max_workers"])

    def test_save_config(self):
        """Testa a gravação de configurações em um arquivo."""
        config = ConfigManager()
        config.set("backup_dir", "/new/backup/path")

        # Verifica se o arquivo foi criado
        self.assertTrue(self.config_path.exists())

        # Verifica se o conteúdo do arquivo está correto
        with open(self.config_path, 'r', encoding='utf-8') as f:
            saved_config = json.load(f)

        self.assertEqual(saved_config["backup_dir"], "/new/backup/path")

    def test_get_with_default(self):
        """Testa o método get com um valor padrão."""
        config = ConfigManager()
        # Chave que não existe
        self.assertEqual(config.get("non_existent_key", "default_value"), "default_value")

    def test_get_backup_dir(self):
        """Testa o método get_backup_dir."""
        config = ConfigManager()
        backup_dir = config.get_backup_dir()
        self.assertEqual(backup_dir, Path(config.get("backup_dir")))

    def test_get_log_level(self):
        """Testa o método get_log_level."""
        config = ConfigManager()

        # Testa cada nível de log
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }

        for level_str, level_int in level_map.items():
            config.set("log_level", level_str)
            self.assertEqual(config.get_log_level(), level_int)

        # Testa com um nível inválido (deve retornar INFO)
        config.set("log_level", "INVALID_LEVEL")
        self.assertEqual(config.get_log_level(), logging.INFO)

    def test_get_log_file(self):
        """Testa o método get_log_file."""
        config = ConfigManager()
        log_file = config.get_log_file()
        self.assertEqual(log_file, Path(config.get("log_file")))

    def test_get_max_workers(self):
        """Testa o método get_max_workers."""
        config = ConfigManager()
        self.assertEqual(config.get_max_workers(), config.get("max_workers"))

        # Testa com um valor diferente
        config.set("max_workers", 8)
        self.assertEqual(config.get_max_workers(), 8)

    def test_get_chunk_size(self):
        """Testa o método get_chunk_size."""
        config = ConfigManager()
        self.assertEqual(config.get_chunk_size(), config.get("chunk_size"))

        # Testa com um valor diferente
        config.set("chunk_size", 131072)
        self.assertEqual(config.get_chunk_size(), 131072)

    def test_get_supported_extensions(self):
        """Testa o método get_supported_extensions."""
        config = ConfigManager()
        self.assertEqual(config.get_supported_extensions(), config.get("supported_extensions"))

        # Testa com um valor diferente
        new_extensions = [".txt", ".pdf"]
        config.set("supported_extensions", new_extensions)
        self.assertEqual(config.get_supported_extensions(), new_extensions)

    def test_is_scan_inside_archives_enabled(self):
        """Testa o método is_scan_inside_archives_enabled."""
        config = ConfigManager()
        self.assertEqual(config.is_scan_inside_archives_enabled(), config.get("scan_inside_archives"))

        # Testa com um valor diferente
        config.set("scan_inside_archives", False)
        self.assertFalse(config.is_scan_inside_archives_enabled())

    def test_is_trash_enabled(self):
        """Testa o método is_trash_enabled."""
        config = ConfigManager()
        self.assertEqual(config.is_trash_enabled(), config.get("trash_enabled"))

        # Testa com um valor diferente
        config.set("trash_enabled", False)
        self.assertFalse(config.is_trash_enabled())

    def test_reset_to_defaults(self):
        """Testa o método reset_to_defaults."""
        config = ConfigManager()

        # Altera algumas configurações
        config.set("backup_dir", "/custom/path")
        config.set("log_level", "DEBUG")

        # Reseta para os valores padrão
        config.reset_to_defaults()

        # Verifica se as configurações foram redefinidas
        for key, value in DEFAULT_CONFIG.items():
            self.assertEqual(config.get(key), value)

    def test_error_handling_load(self):
        """Testa o tratamento de erros ao carregar configurações."""
        # Cria um arquivo de configuração inválido
        with open(self.config_path, 'w', encoding='utf-8') as f:
            f.write("invalid json")

        # Deve usar as configurações padrão em caso de erro
        config = ConfigManager()
        for key, value in DEFAULT_CONFIG.items():
            self.assertEqual(config.get(key), value)

    @patch('builtins.open')
    def test_error_handling_save(self, mock_open):
        """Testa o tratamento de erros ao salvar configurações."""
        # Simula um erro de IO ao salvar
        mock_open.side_effect = IOError("Erro simulado")

        # Não deve lançar exceção
        config = ConfigManager()
        try:
            config.set("backup_dir", "/new/path")
        except Exception as e:
            self.fail(f"set() levantou uma exceção inesperada: {e}")

    @patch('fotix.config.ConfigManager._get_config_file_path')
    def test_config_file_path_unix(self, mock_get_path):
        """Testa o caminho do arquivo de configuração em sistemas Unix-like."""
        # Este teste verifica se o método _get_config_file_path é chamado
        # durante a inicialização do ConfigManager

        # Reseta o singleton para forçar a reinicialização
        ConfigManager._instance = None

        # Configura o mock para retornar um caminho qualquer
        mock_get_path.return_value = Path('mocked_path')

        # Cria uma nova instância, que deve chamar _get_config_file_path
        _ = ConfigManager()

        # Verifica se o método foi chamado
        mock_get_path.assert_called_once()

    @patch('os.name', 'posix')  # Simula um sistema Unix-like
    def test_config_file_path_unix_like(self):
        """Testa o caminho do arquivo de configuração em sistemas Unix-like."""
        # Temporariamente remove o patch existente para _get_config_file_path
        self.patcher.stop()

        # Cria um patch para Path.home() que será aplicado apenas neste teste
        with patch('pathlib.Path.home') as mock_home:
            # Configura o mock para Path.home()
            mock_home_path = MagicMock(spec=Path)
            mock_home.return_value = mock_home_path

            # Configura o comportamento do caminho mockado
            config_dir_mock = MagicMock(spec=Path)
            mock_home_path.__truediv__.return_value = config_dir_mock
            config_dir_mock.__truediv__.return_value = config_dir_mock

            # Reseta o singleton para forçar a reinicialização
            ConfigManager._instance = None

            # Cria uma instância do ConfigManager, que chamará _get_config_file_path internamente
            # durante a inicialização
            ConfigManager()

            # Verifica se os caminhos foram construídos corretamente
            mock_home_path.__truediv__.assert_called_with(".config")
            config_dir_mock.__truediv__.assert_any_call("fotix")

            # Verifica se mkdir foi chamado com os argumentos corretos
            config_dir_mock.mkdir.assert_called_with(parents=True, exist_ok=True)

        # Restaura o patch original para não afetar outros testes
        self.mock_get_path = self.patcher.start()


class TestConfigFunctions(unittest.TestCase):
    """Testes para as funções de conveniência do módulo config."""

    def setUp(self):
        """Configura o ambiente de teste."""
        # Cria um diretório temporário para os testes
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "test_config.json"

        # Patch para o método _get_config_file_path
        self.patcher = patch.object(
            ConfigManager, '_get_config_file_path',
            return_value=self.config_path
        )
        self.mock_get_path = self.patcher.start()

        # Reseta o singleton para cada teste
        ConfigManager._instance = None

    def tearDown(self):
        """Limpa o ambiente após cada teste."""
        self.patcher.stop()
        self.temp_dir.cleanup()
        ConfigManager._instance = None

    def test_get_function(self):
        """Testa a função get."""
        # Configura um valor
        set("test_key", "test_value")

        # Verifica se get retorna o valor correto
        self.assertEqual(get("test_key"), "test_value")
        self.assertEqual(get("non_existent", "default"), "default")

    def test_set_function(self):
        """Testa a função set."""
        set("test_key", "test_value")
        self.assertEqual(get("test_key"), "test_value")

    def test_get_backup_dir_function(self):
        """Testa a função get_backup_dir."""
        set("backup_dir", "/test/backup")
        self.assertEqual(get_backup_dir(), Path("/test/backup"))

    def test_get_log_level_function(self):
        """Testa a função get_log_level."""
        set("log_level", "DEBUG")
        self.assertEqual(get_log_level(), logging.DEBUG)

    def test_get_log_file_function(self):
        """Testa a função get_log_file."""
        set("log_file", "/test/log.txt")
        self.assertEqual(get_log_file(), Path("/test/log.txt"))

    def test_get_max_workers_function(self):
        """Testa a função get_max_workers."""
        set("max_workers", 8)
        self.assertEqual(get_max_workers(), 8)

    def test_get_chunk_size_function(self):
        """Testa a função get_chunk_size."""
        set("chunk_size", 131072)
        self.assertEqual(get_chunk_size(), 131072)

    def test_get_supported_extensions_function(self):
        """Testa a função get_supported_extensions."""
        extensions = [".txt", ".pdf"]
        set("supported_extensions", extensions)
        self.assertEqual(get_supported_extensions(), extensions)

    def test_is_scan_inside_archives_enabled_function(self):
        """Testa a função is_scan_inside_archives_enabled."""
        set("scan_inside_archives", False)
        self.assertFalse(is_scan_inside_archives_enabled())

    def test_is_trash_enabled_function(self):
        """Testa a função is_trash_enabled."""
        set("trash_enabled", False)
        self.assertFalse(is_trash_enabled())

    def test_reset_to_defaults_function(self):
        """Testa a função reset_to_defaults."""
        # Altera algumas configurações
        set("backup_dir", "/custom/path")
        set("log_level", "DEBUG")

        # Reseta para os valores padrão
        reset_to_defaults()

        # Verifica se as configurações foram redefinidas
        for key, value in DEFAULT_CONFIG.items():
            self.assertEqual(get(key), value)


if __name__ == '__main__':
    unittest.main()
