"""
Testes unitários para o módulo de configuração (fotix.config).
"""

import json
import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from fotix.config import (
    Config, load_config, get_config, reset_config, LOG_LEVELS
)


class TestConfig:
    """Testes para a classe Config."""

    def test_default_config_values(self):
        """Testa se os valores padrão são configurados corretamente."""
        config = Config()
        
        assert config.backup_dir.parts[-2:] == ("Fotix", "backups")
        assert config.log_level == "info"
        assert config.log_file.parts[-3:] == ("Fotix", "logs", "fotix.log")
        assert isinstance(config.max_workers, int)
        assert config.max_workers > 0
        assert isinstance(config.file_extensions, list)
        assert config.chunk_size == 65536
        assert config.min_file_size == 1024

    def test_config_post_init_validation(self):
        """Testa a validação no método __post_init__."""
        # Teste com nível de log válido
        config = Config(log_level="debug")
        assert config.log_level == "debug"
        
        # Teste com nível de log inválido
        with pytest.raises(ValueError):
            Config(log_level="invalid_level")
        
        # Teste com string para backup_dir
        # No Windows, o separador de caminho é diferente, então usamos Path para comparar
        backup_dir_str = "/tmp/fotix/backups"
        config = Config(backup_dir=backup_dir_str)
        assert isinstance(config.backup_dir, Path)
        assert config.backup_dir == Path(backup_dir_str)
        
        # Teste com string para log_file
        log_file_str = "/tmp/fotix/logs/fotix.log"
        config = Config(log_file=log_file_str)
        assert isinstance(config.log_file, Path)
        assert config.log_file == Path(log_file_str)

    def test_get_log_level_value(self):
        """Testa o método get_log_level_value()."""
        for level_name, level_value in LOG_LEVELS.items():
            config = Config(log_level=level_name)
            assert config.get_log_level_value() == level_value

    def test_to_dict(self):
        """Testa o método to_dict()."""
        config = Config()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert "backup_dir" in config_dict
        assert "log_level" in config_dict
        assert "log_file" in config_dict
        assert "max_workers" in config_dict
        assert "file_extensions" in config_dict
        assert "chunk_size" in config_dict
        assert "min_file_size" in config_dict
        
        # Verifica se as Paths foram convertidas para strings
        assert isinstance(config_dict["backup_dir"], str)
        assert isinstance(config_dict["log_file"], str)

    def test_save_to_file(self):
        """Testa o método save_to_file()."""
        config = Config()
        
        # Usa um arquivo temporário para o teste
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.json"
            
            # Testa a função
            config.save_to_file(config_file)
            
            # Verifica se o arquivo foi criado
            assert config_file.exists()
            
            # Verifica se o conteúdo é um JSON válido
            with open(config_file, 'r', encoding='utf-8') as f:
                saved_config = json.load(f)
            
            # Verifica se os valores foram salvos corretamente
            assert saved_config["log_level"] == config.log_level
            assert saved_config["max_workers"] == config.max_workers
            assert saved_config["chunk_size"] == config.chunk_size
            assert saved_config["min_file_size"] == config.min_file_size
    
    def test_save_to_file_error(self):
        """Testa erros ao salvar o arquivo de configuração."""
        config = Config()
        
        # Simula um erro de IO ao salvar o arquivo
        with patch("builtins.open", side_effect=OSError("erro simulado")):
            with pytest.raises(OSError):
                config.save_to_file("config.json")


class TestConfigModule:
    """Testes para as funções do módulo de configuração."""
    
    def setup_method(self):
        """Setup para cada teste."""
        reset_config()
    
    def teardown_method(self):
        """Teardown após cada teste."""
        reset_config()
    
    def test_load_config_default(self):
        """Testa carregamento de configuração padrão."""
        config = load_config()
        assert isinstance(config, Config)
        
        # Testa singleton
        config2 = load_config()
        assert config is config2  # Verifica se é a mesma instância
    
    def test_load_config_from_file(self):
        """Testa carregamento de configuração de arquivo."""
        # Cria um arquivo de configuração de teste
        test_config = {
            "log_level": "debug",
            "max_workers": 8,
            "chunk_size": 32768,
            "min_file_size": 2048
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
            json.dump(test_config, temp)
            temp_path = temp.name
        
        try:
            # Carrega a configuração do arquivo
            config = load_config(temp_path)
            
            # Verifica se os valores foram carregados corretamente
            assert config.log_level == "debug"
            assert config.max_workers == 8
            assert config.chunk_size == 32768
            assert config.min_file_size == 2048
        finally:
            # Limpa o arquivo temporário
            os.unlink(temp_path)
    
    def test_load_config_file_not_found(self):
        """Testa comportamento quando o arquivo não existe."""
        # Usa um caminho que certamente não existe
        non_existent_file = "/path/to/non/existent/file.json"
        
        # Deve usar a configuração padrão sem erro
        config = load_config(non_existent_file)
        assert isinstance(config, Config)
        assert config.log_level == "info"  # valor padrão
    
    def test_load_config_invalid_json(self):
        """Testa comportamento com JSON inválido."""
        # Cria um arquivo com JSON inválido
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
            temp.write("{invalid json")
            temp_path = temp.name
        
        try:
            # Deve lançar ValueError
            with pytest.raises(ValueError):
                load_config(temp_path)
        finally:
            # Limpa o arquivo temporário
            os.unlink(temp_path)
    
    def test_load_config_io_error(self):
        """Testa comportamento com erro de IO."""
        # Simula um erro de IO ao abrir o arquivo usando Path.exists()
        # mas lançando exceção no open
        
        # Criamos um mock para Path.exists() que retorna True
        # e um mock para open() que lança OSError
        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', side_effect=OSError("Erro simulado")):
            with pytest.raises(OSError):
                load_config("config_that_raises_error.json")
    
    def test_get_config(self):
        """Testa a função get_config()."""
        # Primeiro acesso deve carregar configuração padrão
        config1 = get_config()
        assert isinstance(config1, Config)
        
        # Segundo acesso deve retornar a mesma instância
        config2 = get_config()
        assert config1 is config2
    
    def test_reset_config(self):
        """Testa a função reset_config()."""
        # Carrega a configuração
        config1 = get_config()
        
        # Reseta a configuração
        reset_config()
        
        # Carrega novamente - deve ser uma nova instância
        config2 = get_config()
        assert config1 is not config2 