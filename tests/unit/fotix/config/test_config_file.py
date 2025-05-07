"""
Testes unitários para operações de arquivo do módulo de configuração.

Este arquivo contém testes para as operações de arquivo da classe Config,
incluindo carregamento de configurações de arquivos e salvamento de
configurações em arquivos.
"""

import os
import json
import tempfile
from pathlib import Path
import pytest
from fotix.config import Config, ConfigError


class TestConfigFile:
    """Testes para operações de arquivo da classe Config."""

    def test_from_file_json(self):
        """Testa o carregamento de um arquivo JSON."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp:
            config_data = {
                'log_level': 'DEBUG',
                'custom_key': 'value'
            }
            temp.write(json.dumps(config_data).encode('utf-8'))
            temp_path = temp.name

        try:
            config = Config.from_file(temp_path)
            assert config.get('log_level') == 'DEBUG'
            assert config.get('custom_key') == 'value'
        finally:
            os.unlink(temp_path)

    def test_from_file_nonexistent(self):
        """Testa o carregamento de um arquivo inexistente."""
        with pytest.raises(ConfigError):
            Config.from_file('/nonexistent/file.json')

    def test_from_file_invalid_json(self):
        """Testa o carregamento de um arquivo JSON inválido."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp:
            temp.write(b'invalid json')
            temp_path = temp.name

        try:
            with pytest.raises(ConfigError):
                Config.from_file(temp_path)
        finally:
            os.unlink(temp_path)

    def test_from_file_unsupported_format(self):
        """Testa o carregamento de um arquivo com formato não suportado."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp:
            temp.write(b'some text')
            temp_path = temp.name

        try:
            with pytest.raises(ConfigError):
                Config.from_file(temp_path)
        finally:
            os.unlink(temp_path)

    def test_save_to_file_json(self):
        """Testa o salvamento em um arquivo JSON."""
        config = Config({'log_level': 'DEBUG', 'custom_key': 'value'})

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp:
            temp_path = temp.name

        try:
            config.save_to_file(temp_path)

            # Verifica se o arquivo foi criado e contém os dados corretos
            with open(temp_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)

            assert saved_data['log_level'] == 'DEBUG'
            assert saved_data['custom_key'] == 'value'
        finally:
            os.unlink(temp_path)

    def test_save_to_file_unsupported_format(self):
        """Testa o salvamento em um arquivo com formato não suportado."""
        config = Config()

        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp:
            temp_path = temp.name

        try:
            with pytest.raises(ConfigError):
                config.save_to_file(temp_path)
        finally:
            os.unlink(temp_path)

    def test_save_to_file_create_parent_dirs(self):
        """Testa o salvamento em um arquivo com criação de diretórios pai."""
        config = Config({'log_level': 'DEBUG'})

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / 'subdir' / 'config.json'

            config.save_to_file(file_path)

            # Verifica se o arquivo foi criado
            assert file_path.exists()

            # Verifica se o conteúdo está correto
            with open(file_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)

            assert saved_data['log_level'] == 'DEBUG'
