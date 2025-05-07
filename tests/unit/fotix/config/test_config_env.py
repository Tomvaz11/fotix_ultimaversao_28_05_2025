"""
Testes unitários para operações de ambiente do módulo de configuração.

Este arquivo contém testes para as operações de ambiente da classe Config,
incluindo carregamento de configurações de variáveis de ambiente.
"""

import os
import pytest
from fotix.config import Config


class TestConfigEnv:
    """Testes para operações de ambiente da classe Config."""

    def test_from_env(self, monkeypatch):
        """Testa o carregamento de variáveis de ambiente."""
        # Define variáveis de ambiente para o teste
        monkeypatch.setenv('FOTIX_LOG_LEVEL', 'DEBUG')
        monkeypatch.setenv('FOTIX_CUSTOM_KEY', 'value')
        monkeypatch.setenv('OTHER_VAR', 'ignored')

        config = Config.from_env()

        # Verifica se as variáveis com o prefixo correto foram carregadas
        assert config.get('log_level') == 'DEBUG'
        assert config.get('custom_key') == 'value'

        # Verifica se variáveis sem o prefixo foram ignoradas
        assert 'other_var' not in config

    def test_from_env_custom_prefix(self, monkeypatch):
        """Testa o carregamento de variáveis de ambiente com prefixo personalizado."""
        # Define variáveis de ambiente para o teste
        monkeypatch.setenv('CUSTOM_LOG_LEVEL', 'DEBUG')
        monkeypatch.setenv('FOTIX_LOG_LEVEL', 'INFO')

        config = Config.from_env(prefix='CUSTOM_')

        # Verifica se as variáveis com o prefixo correto foram carregadas
        assert config.get('log_level') == 'DEBUG'

        # Verifica se variáveis com outro prefixo foram ignoradas
        assert 'fotix_log_level' not in config

    def test_from_env_empty(self, monkeypatch):
        """Testa o carregamento quando não há variáveis de ambiente com o prefixo."""
        # Remove qualquer variável FOTIX_ que possa existir
        for key in list(os.environ.keys()):
            if key.startswith('FOTIX_'):
                monkeypatch.delenv(key)

        config = Config.from_env()

        # Verifica se os valores padrão foram inicializados
        assert 'app_data_dir' in config
        assert 'backup_dir' in config
        assert 'log_level' in config
        assert config.get('log_level') == 'INFO'
