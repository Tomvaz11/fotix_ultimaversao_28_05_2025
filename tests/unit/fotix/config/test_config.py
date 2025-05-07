"""
Testes unitários para o módulo de configuração.

Este arquivo contém testes para as funcionalidades básicas da classe Config,
incluindo inicialização, acesso a configurações com diferentes tipos de dados,
e operações básicas como set, bracket access e contains.
"""

import os
from pathlib import Path
import pytest
from fotix.config import Config, ConfigError


class TestConfig:
    """Testes para a classe Config."""

    def test_init_with_empty_data(self):
        """Testa a inicialização com dados vazios."""
        config = Config()
        assert isinstance(config, Config)
        # Verifica se os valores padrão foram inicializados
        assert 'app_data_dir' in config
        assert 'backup_dir' in config
        assert 'log_level' in config
        assert config.get('log_level') == 'INFO'

    def test_initialize_defaults(self):
        """Testa se todos os valores padrão são inicializados corretamente."""
        config = Config()
        # Verifica todos os valores padrão
        assert config.get('app_data_dir') == str(Path.home() / '.fotix')
        assert config.get('backup_dir') == str(Path(config.get('app_data_dir')) / 'backups')
        assert config.get('log_level') == 'INFO'
        assert config.get('file_read_chunk_size') == 65536
        assert config.get('max_workers') == os.cpu_count() or config.get('max_workers') == 4
        assert isinstance(config.get('default_scan_extensions'), list)
        assert '.jpg' in config.get('default_scan_extensions')
        assert '.zip' in config.get('default_scan_extensions')

    def test_init_with_data(self):
        """Testa a inicialização com dados fornecidos."""
        data = {'log_level': 'DEBUG', 'custom_key': 'value'}
        config = Config(data)
        assert config.get('log_level') == 'DEBUG'
        assert config.get('custom_key') == 'value'
        # Verifica se os valores padrão para chaves não fornecidas foram inicializados
        assert 'app_data_dir' in config
        assert 'backup_dir' in config

    def test_get_existing_key(self):
        """Testa a obtenção de uma chave existente."""
        config = Config({'key': 'value'})
        assert config.get('key') == 'value'

    def test_get_nonexistent_key_with_default(self):
        """Testa a obtenção de uma chave inexistente com valor padrão."""
        config = Config()
        assert config.get('nonexistent', 'default') == 'default'

    def test_get_nonexistent_key_without_default(self):
        """Testa a obtenção de uma chave inexistente sem valor padrão."""
        config = Config()
        assert config.get('nonexistent') is None

    def test_get_path_valid(self):
        """Testa a obtenção de um caminho válido."""
        test_path = '/tmp' if os.name != 'nt' else 'C:/temp'
        config = Config({'path': test_path})
        path = config.get_path('path')
        assert isinstance(path, Path)
        assert path == Path(test_path)

    def test_get_path_nonexistent(self):
        """Testa a obtenção de um caminho inexistente."""
        config = Config()
        with pytest.raises(ConfigError):
            config.get_path('nonexistent')

    def test_get_path_with_default(self):
        """Testa a obtenção de um caminho com valor padrão."""
        config = Config()
        default_path = '/default' if os.name != 'nt' else 'C:/default'
        path = config.get_path('nonexistent', default_path)
        assert isinstance(path, Path)
        assert path == Path(default_path)

    def test_get_int_valid(self):
        """Testa a obtenção de um inteiro válido."""
        config = Config({'int': 42, 'str_int': '42'})
        assert config.get_int('int') == 42
        assert config.get_int('str_int') == 42

    def test_get_int_invalid(self):
        """Testa a obtenção de um valor que não é inteiro."""
        config = Config({'not_int': 'abc'})
        with pytest.raises(ConfigError):
            config.get_int('not_int')

    def test_get_int_nonexistent(self):
        """Testa a obtenção de um inteiro inexistente."""
        config = Config()
        with pytest.raises(ConfigError):
            config.get_int('nonexistent')

    def test_get_int_with_default(self):
        """Testa a obtenção de um inteiro com valor padrão."""
        config = Config()
        assert config.get_int('nonexistent', 42) == 42

    def test_get_float_valid(self):
        """Testa a obtenção de um float válido."""
        config = Config({'float': 3.14, 'str_float': '3.14'})
        assert config.get_float('float') == 3.14
        assert config.get_float('str_float') == 3.14

    def test_get_float_invalid(self):
        """Testa a obtenção de um valor que não é float."""
        config = Config({'not_float': 'abc'})
        with pytest.raises(ConfigError):
            config.get_float('not_float')

    def test_get_float_nonexistent(self):
        """Testa a obtenção de um float inexistente."""
        config = Config()
        with pytest.raises(ConfigError):
            config.get_float('nonexistent')

    def test_get_float_with_default(self):
        """Testa a obtenção de um float com valor padrão."""
        config = Config()
        assert config.get_float('nonexistent', 3.14) == 3.14

    def test_get_bool_valid(self):
        """Testa a obtenção de um booleano válido."""
        config = Config({
            'bool_true': True,
            'bool_false': False,
            'str_true1': 'true',
            'str_true2': 'yes',
            'str_true3': '1',
            'str_true4': 'on',
            'str_false1': 'false',
            'str_false2': 'no',
            'str_false3': '0',
            'str_false4': 'off'
        })
        assert config.get_bool('bool_true') is True
        assert config.get_bool('bool_false') is False
        assert config.get_bool('str_true1') is True
        assert config.get_bool('str_true2') is True
        assert config.get_bool('str_true3') is True
        assert config.get_bool('str_true4') is True
        assert config.get_bool('str_false1') is False
        assert config.get_bool('str_false2') is False
        assert config.get_bool('str_false3') is False
        assert config.get_bool('str_false4') is False

    def test_get_bool_invalid(self):
        """Testa a obtenção de um valor que não é booleano."""
        config = Config({'not_bool': 'abc'})
        with pytest.raises(ConfigError):
            config.get_bool('not_bool')

    def test_get_bool_nonexistent(self):
        """Testa a obtenção de um booleano inexistente."""
        config = Config()
        with pytest.raises(ConfigError):
            config.get_bool('nonexistent')

    def test_get_bool_with_default(self):
        """Testa a obtenção de um booleano com valor padrão."""
        config = Config()
        assert config.get_bool('nonexistent', True) is True

    def test_get_list_valid(self):
        """Testa a obtenção de uma lista válida."""
        config = Config({
            'list': [1, 2, 3],
            'str_list_json': '[1, 2, 3]',
            'str_list_csv': '1, 2, 3'
        })
        assert config.get_list('list') == [1, 2, 3]
        assert config.get_list('str_list_json') == [1, 2, 3]
        assert config.get_list('str_list_csv') == ['1', '2', '3']

    def test_get_list_invalid(self):
        """Testa a obtenção de um valor que não é lista."""
        config = Config({'not_list': 42})
        with pytest.raises(ConfigError):
            config.get_list('not_list')

    def test_get_list_nonexistent(self):
        """Testa a obtenção de uma lista inexistente."""
        config = Config()
        with pytest.raises(ConfigError):
            config.get_list('nonexistent')

    def test_get_list_with_default(self):
        """Testa a obtenção de uma lista com valor padrão."""
        config = Config()
        assert config.get_list('nonexistent', [1, 2, 3]) == [1, 2, 3]

    def test_set_value(self):
        """Testa a definição de um valor."""
        config = Config()
        config.set('key', 'value')
        assert config.get('key') == 'value'

    def test_bracket_access(self):
        """Testa o acesso usando colchetes."""
        config = Config({'key': 'value'})
        assert config['key'] == 'value'

        with pytest.raises(KeyError):
            _ = config['nonexistent']

    def test_bracket_assignment(self):
        """Testa a atribuição usando colchetes."""
        config = Config()
        config['key'] = 'value'
        assert config.get('key') == 'value'

    def test_contains(self):
        """Testa o operador 'in'."""
        config = Config({'key': 'value'})
        assert 'key' in config
        assert 'nonexistent' not in config

    def test_repr(self):
        """Testa a representação em string."""
        config = Config({'key': 'value'})
        assert repr(config).startswith("Config({'key': 'value'")
        assert "'app_data_dir':" in repr(config)
        assert "'backup_dir':" in repr(config)
        assert "'log_level': 'INFO'" in repr(config)

    def test_get_path_invalid(self):
        """Testa a obtenção de um caminho com valor inválido que causa exceção."""
        # Criamos uma classe que, quando convertida para string, causa uma exceção
        class PathErrorSimulator:
            def __str__(self):
                raise ValueError("Erro simulado ao converter para string")

        config = Config({'invalid_path': PathErrorSimulator()})
        with pytest.raises(ConfigError) as excinfo:
            config.get_path('invalid_path')

        # Verifica se a mensagem de erro contém a informação esperada
        assert "Erro ao converter configuração para Path" in str(excinfo.value)
