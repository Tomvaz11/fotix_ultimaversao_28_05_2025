"""
Testes unitários para o módulo de configuração.
"""

import json
import logging
import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from fotix.config import (
    DEFAULT_CONFIG,
    get_default_config_path,
    load_config,
    save_config,
    get_config,
    get_log_level,
    get_backup_dir,
    update_config,
)


class TestDefaultConfigPath:
    """Testes para a função get_default_config_path."""

    @mock.patch('fotix.config.os.name', 'nt')
    @mock.patch('fotix.config.os.environ', {'APPDATA': r'C:\Users\Test\AppData\Roaming'})
    @mock.patch('fotix.config.Path')
    def test_default_config_path_windows(self, mock_path):
        """Testa se o caminho padrão no Windows é correto."""
        # Configurar o mock para retornar um caminho específico quando Path é chamado com o APPDATA
        mock_path_instance = mock.MagicMock()
        mock_fotix_instance = mock.MagicMock()

        mock_path.return_value = mock_path_instance
        mock_path_instance.__truediv__.return_value = mock_fotix_instance
        mock_fotix_instance.__truediv__.return_value = mock.MagicMock()

        # Configurar mkdir para não fazer nada
        mock_fotix_instance.mkdir.return_value = None

        get_default_config_path()

        # Verificar se Path foi chamado com o APPDATA correto
        mock_path.assert_called_with(r'C:\Users\Test\AppData\Roaming')
        # Verificar se o operador / foi chamado com 'Fotix'
        mock_path_instance.__truediv__.assert_called_with('Fotix')
        # Verificar se mkdir foi chamado com os parâmetros corretos
        mock_fotix_instance.mkdir.assert_called_with(parents=True, exist_ok=True)

    @mock.patch('fotix.config.os.name', 'posix')
    @mock.patch('fotix.config.Path')
    def test_default_config_path_linux(self, mock_path):
        """Testa se o caminho padrão no Linux é correto."""
        # Configurar o mock para simular Path.home() e operações de caminho
        mock_home_path = mock.MagicMock()
        mock_config_path = mock.MagicMock()
        mock_fotix_path = mock.MagicMock()

        mock_path.home.return_value = mock_home_path
        mock_home_path.__truediv__.return_value = mock_config_path
        mock_config_path.__truediv__.return_value = mock_fotix_path

        get_default_config_path()

        # Verificar se Path.home() foi chamado
        mock_path.home.assert_called_once()
        # Verificar se o operador / foi chamado com '.config'
        mock_home_path.__truediv__.assert_called_with('.config')
        # Verificar se o operador / foi chamado com 'fotix'
        mock_config_path.__truediv__.assert_called_with('fotix')


class TestLoadConfig:
    """Testes para a função load_config."""

    def test_load_nonexistent_config_creates_default(self):
        """Testa se um arquivo de configuração inexistente é criado com valores padrão."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"

            # Garante que o arquivo não existe
            assert not config_path.exists()

            # Carrega a configuração (deve criar o arquivo)
            config = load_config(config_path)

            # Verifica se o arquivo foi criado
            assert config_path.exists()

            # Verifica se o conteúdo é o padrão
            assert config == DEFAULT_CONFIG

            # Verifica se o arquivo contém o JSON correto
            with open(config_path, 'r', encoding='utf-8') as f:
                saved_config = json.load(f)
            assert saved_config == DEFAULT_CONFIG

    @mock.patch('fotix.config.get_default_config_path')
    def test_load_config_with_default_path(self, mock_get_default_config_path):
        """Testa se load_config usa o caminho padrão quando config_path é None."""
        with tempfile.TemporaryDirectory() as temp_dir:
            default_config_path = Path(temp_dir) / "default_config.json"
            mock_get_default_config_path.return_value = default_config_path

            # Garante que o arquivo não existe
            assert not default_config_path.exists()

            # Carrega a configuração com caminho padrão (None)
            config = load_config()

            # Verifica se get_default_config_path foi chamado
            mock_get_default_config_path.assert_called_once()

            # Verifica se o arquivo foi criado no caminho padrão
            assert default_config_path.exists()

    def test_load_existing_config(self):
        """Testa se um arquivo de configuração existente é carregado corretamente."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"

            # Cria um arquivo de configuração personalizado
            custom_config = {
                "backup_dir": "/custom/backup",
                "log_level": "DEBUG",
                "max_workers": 8
            }

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(custom_config, f)

            # Carrega a configuração
            config = load_config(config_path)

            # Verifica se os valores personalizados foram mantidos
            assert config["backup_dir"] == "/custom/backup"
            assert config["log_level"] == "DEBUG"
            assert config["max_workers"] == 8

            # Verifica se os valores padrão ausentes foram adicionados
            assert "log_file" in config
            assert "default_scan_dir" in config

    def test_load_invalid_json_raises_error(self):
        """Testa se um arquivo de configuração com JSON inválido gera erro."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"

            # Cria um arquivo com JSON inválido
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write("{invalid json")

            # Tenta carregar a configuração
            with pytest.raises(ValueError):
                load_config(config_path)


class TestSaveConfig:
    """Testes para a função save_config."""

    def test_save_config_creates_file(self):
        """Testa se a função save_config cria o arquivo corretamente."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"

            # Garante que o arquivo não existe
            assert not config_path.exists()

            # Salva uma configuração
            custom_config = {
                "backup_dir": "/custom/backup",
                "log_level": "DEBUG",
                "max_workers": 8
            }
            save_config(custom_config, config_path)

            # Verifica se o arquivo foi criado
            assert config_path.exists()

            # Verifica se o conteúdo é o esperado
            with open(config_path, 'r', encoding='utf-8') as f:
                saved_config = json.load(f)
            assert saved_config == custom_config

    @mock.patch('fotix.config.get_default_config_path')
    def test_save_config_with_default_path(self, mock_get_default_config_path):
        """Testa se save_config usa o caminho padrão quando config_path é None."""
        with tempfile.TemporaryDirectory() as temp_dir:
            default_config_path = Path(temp_dir) / "default_config.json"
            mock_get_default_config_path.return_value = default_config_path

            # Garante que o arquivo não existe
            assert not default_config_path.exists()

            # Salva uma configuração com caminho padrão (None)
            custom_config = {
                "backup_dir": "/custom/backup",
                "log_level": "DEBUG",
                "max_workers": 8
            }
            save_config(custom_config)

            # Verifica se get_default_config_path foi chamado
            mock_get_default_config_path.assert_called_once()

            # Verifica se o arquivo foi criado no caminho padrão
            assert default_config_path.exists()

            # Verifica se o conteúdo é o esperado
            with open(default_config_path, 'r', encoding='utf-8') as f:
                saved_config = json.load(f)
            assert saved_config == custom_config


class TestGetConfig:
    """Testes para a função get_config."""

    def test_get_config_singleton(self):
        """Testa se get_config retorna a mesma instância nas chamadas subsequentes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"

            # Primeira chamada - deve carregar do arquivo
            config1 = get_config(config_path)

            # Modifica a configuração em memória
            config1["test_key"] = "test_value"

            # Segunda chamada sem path - deve retornar a mesma instância
            config2 = get_config()

            # Verifica se é a mesma instância (modificação refletida)
            assert "test_key" in config2
            assert config2["test_key"] == "test_value"

            # Terceira chamada com path - deve recarregar do arquivo
            config3 = get_config(config_path)

            # Verifica se foi recarregado (modificação não refletida)
            assert "test_key" not in config3

    @mock.patch('fotix.config._config_instance', None)
    @mock.patch('fotix.config.load_config')
    def test_get_config_calls_load_config(self, mock_load_config):
        """Testa se get_config chama load_config na primeira chamada."""
        mock_load_config.return_value = {"mocked": True}

        config = get_config()

        # Verifica se load_config foi chamado
        mock_load_config.assert_called_once()
        assert config == {"mocked": True}


class TestGetLogLevel:
    """Testes para a função get_log_level."""

    @mock.patch('fotix.config.get_config')
    def test_get_log_level_valid(self, mock_get_config):
        """Testa se get_log_level retorna o nível correto para valores válidos."""
        test_cases = [
            ("DEBUG", logging.DEBUG),
            ("INFO", logging.INFO),
            ("WARNING", logging.WARNING),
            ("ERROR", logging.ERROR),
            ("CRITICAL", logging.CRITICAL),
            ("debug", logging.DEBUG),  # Teste de case-insensitive
        ]

        for level_str, expected_level in test_cases:
            mock_get_config.return_value = {"log_level": level_str}
            assert get_log_level() == expected_level

    @mock.patch('fotix.config.get_config')
    def test_get_log_level_invalid_defaults_to_info(self, mock_get_config):
        """Testa se get_log_level retorna INFO para valores inválidos."""
        mock_get_config.return_value = {"log_level": "INVALID_LEVEL"}
        assert get_log_level() == logging.INFO


class TestGetBackupDir:
    """Testes para a função get_backup_dir."""

    @mock.patch('fotix.config.get_config')
    @mock.patch('pathlib.Path.mkdir')
    def test_get_backup_dir_creates_directory(self, mock_mkdir, mock_get_config):
        """Testa se get_backup_dir cria o diretório se não existir."""
        mock_get_config.return_value = {"backup_dir": "/test/backup"}

        backup_dir = get_backup_dir()

        assert backup_dir == Path("/test/backup")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


class TestUpdateConfig:
    """Testes para a função update_config."""

    @mock.patch('fotix.config.get_config')
    @mock.patch('fotix.config.save_config')
    def test_update_config_modifies_and_saves(self, mock_save_config, mock_get_config):
        """Testa se update_config modifica a configuração e salva."""
        mock_config = {"existing_key": "old_value"}
        mock_get_config.return_value = mock_config

        update_config("new_key", "new_value")

        # Verifica se a configuração foi modificada
        assert mock_config["new_key"] == "new_value"

        # Verifica se save_config foi chamado com a configuração modificada
        mock_save_config.assert_called_once_with(mock_config)
