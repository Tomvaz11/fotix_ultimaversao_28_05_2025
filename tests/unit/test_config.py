"""
Testes unitários para o módulo de configuração.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from fotix.config import Config, get_config


@pytest.fixture
def temp_config_file():
    """Fixture para criar um arquivo de configuração temporário."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.json"
        yield config_path


def test_config_init_creates_default_config_path():
    """Testa se o construtor cria o caminho padrão quando não é fornecido."""
    with mock.patch("fotix.config.Config._get_default_config_path") as mock_get_path:
        with mock.patch("fotix.config.Config._load_config") as mock_load:
            mock_path = mock.MagicMock()
            mock_get_path.return_value = mock_path

            config = Config()

            assert config._config_path == mock_path
            mock_get_path.assert_called_once()


def test_get_default_config_path_creates_directory():
    """Testa se _get_default_config_path cria o diretório se não existir."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with mock.patch("pathlib.Path.home") as mock_home:
            # Configurar o mock para retornar o diretório temporário
            mock_home.return_value = Path(temp_dir)

            # Chamar o método
            config = Config()
            path = config._get_default_config_path()

            # Verificar se o diretório foi criado
            expected_dir = Path(temp_dir) / ".fotix"
            assert expected_dir.exists()
            assert path == expected_dir / "config.json"


def test_load_config_creates_file_if_not_exists(temp_config_file):
    """Testa se _load_config cria o arquivo de configuração se não existir."""
    # Verificar que o arquivo não existe
    assert not temp_config_file.exists()

    # Criar configuração com o arquivo temporário
    config = Config(temp_config_file)

    # Verificar que o arquivo foi criado
    assert temp_config_file.exists()

    # Verificar que o conteúdo é o padrão
    with open(temp_config_file, "r", encoding="utf-8") as f:
        saved_config = json.load(f)

    from fotix.config import DEFAULT_CONFIG
    assert saved_config == DEFAULT_CONFIG


def test_load_config_handles_json_error(temp_config_file):
    """Testa se _load_config lida com erros de JSON."""
    # Criar um arquivo de configuração inválido
    with open(temp_config_file, "w", encoding="utf-8") as f:
        f.write("invalid json")

    # Criar configuração com o arquivo inválido
    with mock.patch("builtins.print") as mock_print:
        config = Config(temp_config_file)

        # Verificar que o erro foi tratado
        mock_print.assert_called_once()
        assert "Erro ao carregar configuração" in mock_print.call_args[0][0]

    # Verificar que a configuração padrão foi usada
    from fotix.config import DEFAULT_CONFIG
    assert config._config == DEFAULT_CONFIG


def test_load_config_handles_io_error():
    """Testa se _load_config lida com erros de IO."""
    # Criar um caminho para um arquivo em um diretório que não existe
    config_path = Path("/nonexistent/directory/config.json")

    # Criar configuração com o caminho inválido
    with mock.patch("builtins.print") as mock_print:
        with mock.patch("builtins.open") as mock_open:
            # Configurar o mock para lançar uma exceção ao tentar abrir o arquivo
            mock_open.side_effect = IOError("Erro de IO")

            config = Config(config_path)

            # Verificar que o erro foi tratado
            mock_print.assert_called_once()
            assert "Erro ao salvar configuração" in mock_print.call_args[0][0]

    # Verificar que a configuração padrão foi usada
    from fotix.config import DEFAULT_CONFIG
    assert config._config == DEFAULT_CONFIG


def test_ensure_default_values_adds_missing_keys():
    """Testa se _ensure_default_values adiciona chaves ausentes."""
    # Criar uma configuração incompleta
    config_dict = {
        "logging": {
            "level": "DEBUG"
        }
    }

    # Criar configuração
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.json"

        # Salvar a configuração incompleta
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_dict, f)

        # Carregar a configuração
        config = Config(config_path)

        # Verificar que as chaves padrão foram adicionadas
        assert "console" in config._config["logging"]
        assert "file" in config._config["logging"]
        assert "backup" in config._config


def test_save_config_handles_io_error(temp_config_file):
    """Testa se _save_config lida com erros de IO."""
    # Criar configuração
    config = Config(temp_config_file)

    # Simular um erro de IO ao salvar
    with mock.patch("builtins.open") as mock_open:
        mock_open.side_effect = IOError("Erro de IO")

        with mock.patch("builtins.print") as mock_print:
            # Tentar salvar a configuração
            config._save_config(config._config)

            # Verificar que o erro foi tratado
            mock_print.assert_called_once()
            assert "Erro ao salvar configuração" in mock_print.call_args[0][0]


def test_get_nonexistent_section():
    """Testa se get retorna o valor padrão quando a seção não existe."""
    # Criar configuração
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.json"
        config = Config(config_path)

        # Tentar obter uma seção que não existe
        result = config.get("nonexistent_section", default="default_value")

        # Verificar que o valor padrão foi retornado
        assert result == "default_value"


def test_get_nonexistent_key():
    """Testa se get retorna o valor padrão quando a chave não existe."""
    # Criar configuração
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.json"
        config = Config(config_path)

        # Tentar obter uma chave que não existe
        result = config.get("logging", "nonexistent_key", default="default_value")

        # Verificar que o valor padrão foi retornado
        assert result == "default_value"


def test_set_nonexistent_section():
    """Testa se set cria uma nova seção quando ela não existe."""
    # Criar configuração
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.json"
        config = Config(config_path)

        # Definir um valor em uma seção que não existe
        config.set("new_section", "key", "value")

        # Verificar que a seção foi criada
        assert "new_section" in config._config
        assert config._config["new_section"]["key"] == "value"


def test_save_method():
    """Testa se o método save chama _save_config."""
    # Criar configuração
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.json"
        config = Config(config_path)

        # Patch o método _save_config
        with mock.patch.object(config, "_save_config") as mock_save:
            # Chamar o método save
            config.save()

            # Verificar que _save_config foi chamado
            mock_save.assert_called_once_with(config._config)


def test_get_config_returns_singleton():
    """Testa se get_config retorna a mesma instância."""
    # Limpar a instância global
    import fotix.config
    fotix.config._config_instance = None

    # Obter a configuração
    config1 = get_config()
    config2 = get_config()

    # Verificar que é a mesma instância
    assert config1 is config2
