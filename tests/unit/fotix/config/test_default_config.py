"""
Testes unitários para a instância global de configuração padrão.
"""

from fotix.config import Config, default_config


def test_default_config():
    """Testa a instância global de configuração padrão."""
    assert isinstance(default_config, Config)
    assert 'app_data_dir' in default_config
    assert 'backup_dir' in default_config
    assert 'log_level' in default_config
    assert default_config.get('log_level') == 'INFO'
