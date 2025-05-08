"""
Testes unitários para o módulo fotix.config.
"""

import json
import os
from pathlib import Path
import pytest
import tempfile
import shutil

from fotix.config import ConfigManager, get_config, DEFAULT_CONFIG


class TestConfigManager:
    """Testes para a classe ConfigManager."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Fixture que cria um diretório temporário para os testes."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        # Limpa o diretório temporário após os testes
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def temp_config_file(self, temp_config_dir):
        """Fixture que cria um arquivo de configuração temporário."""
        config_file = temp_config_dir / "config.json"
        return config_file
    
    @pytest.fixture
    def config_manager(self, temp_config_file):
        """Fixture que cria uma instância de ConfigManager com arquivo temporário."""
        return ConfigManager(temp_config_file)
    
    def test_init_creates_config_file(self, temp_config_file):
        """Testa se o inicializador cria o arquivo de configuração se não existir."""
        # Verificar que o arquivo não existe inicialmente
        assert not temp_config_file.exists()
        
        # Criar o gerenciador de configurações
        ConfigManager(temp_config_file)
        
        # Verificar que o arquivo foi criado
        assert temp_config_file.exists()
        
        # Verificar que o conteúdo do arquivo é válido (JSON válido)
        with open(temp_config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # Verificar que todas as configurações padrão estão presentes
        for key in DEFAULT_CONFIG:
            assert key in config
    
    def test_get_config_returns_same_instance(self, temp_config_file):
        """Testa se get_config retorna a mesma instância quando chamado múltiplas vezes."""
        # Resetar a instância global para o teste
        import fotix.config
        fotix.config._config_instance = None
        
        # Obter a instância pela primeira vez
        config1 = get_config(temp_config_file)
        
        # Obter a instância novamente
        config2 = get_config()
        
        # Verificar que são a mesma instância
        assert config1 is config2
        
        # Verificar que uma nova instância é criada quando um novo arquivo é especificado
        config3 = get_config(Path(tempfile.mktemp()))
        assert config1 is not config3
    
    def test_save_config(self, config_manager, temp_config_file):
        """Testa se as configurações são salvas corretamente."""
        # Modificar uma configuração
        config_manager.log_level = "DEBUG"
        
        # Salvar as configurações
        config_manager.save_config()
        
        # Carregar as configurações diretamente do arquivo
        with open(temp_config_file, "r", encoding="utf-8") as f:
            saved_config = json.load(f)
        
        # Verificar que a configuração foi salva corretamente
        assert saved_config["log_level"] == "DEBUG"
    
    def test_get_nonexistent_key(self, config_manager):
        """Testa o comportamento ao tentar obter uma chave inexistente."""
        # Tentar obter uma chave que não existe
        value = config_manager.get("nonexistent_key")
        
        # Verificar que o valor retornado é None
        assert value is None
        
        # Verificar que o valor padrão é retornado quando especificado
        value = config_manager.get("nonexistent_key", "default_value")
        assert value == "default_value"
    
    def test_set_and_get(self, config_manager):
        """Testa se é possível definir e obter valores corretamente."""
        # Definir um valor
        config_manager.set("test_key", "test_value")
        
        # Verificar que o valor pode ser obtido
        assert config_manager.get("test_key") == "test_value"
    
    def test_update(self, config_manager):
        """Testa se o método update atualiza múltiplas configurações corretamente."""
        # Definir valores iniciais
        config_manager.set("key1", "value1")
        config_manager.set("key2", "value2")
        
        # Atualizar os valores
        config_manager.update({"key1": "new_value1", "key3": "value3"})
        
        # Verificar que os valores foram atualizados corretamente
        assert config_manager.get("key1") == "new_value1"
        assert config_manager.get("key2") == "value2"
        assert config_manager.get("key3") == "value3"
    
    def test_property_backup_dir(self, config_manager):
        """Testa a propriedade backup_dir."""
        # Definir um novo valor
        new_dir = Path("/tmp/new_backup_dir")
        config_manager.backup_dir = new_dir
        
        # Verificar que o valor foi atualizado
        assert config_manager.backup_dir == new_dir
        
        # Verificar que o valor interno foi atualizado como string
        assert config_manager.get("backup_dir") == str(new_dir)
    
    def test_property_log_level(self, config_manager):
        """Testa a propriedade log_level."""
        # Definir um novo valor
        config_manager.log_level = "debug"
        
        # Verificar que o valor foi normalizado para maiúsculas
        assert config_manager.log_level == "DEBUG"
        
        # Verificar que um valor inválido gera uma exceção
        with pytest.raises(ValueError):
            config_manager.log_level = "INVALID_LEVEL"
    
    def test_property_log_file(self, config_manager):
        """Testa a propriedade log_file."""
        # Definir um novo valor
        new_file = Path("/tmp/new_log.txt")
        config_manager.log_file = new_file
        
        # Verificar que o valor foi atualizado
        assert config_manager.log_file == new_file
        
        # Verificar que o valor interno foi atualizado como string
        assert config_manager.get("log_file") == str(new_file)
    
    def test_property_concurrent_workers(self, config_manager):
        """Testa a propriedade concurrent_workers."""
        # Definir um novo valor
        config_manager.concurrent_workers = 8
        
        # Verificar que o valor foi atualizado
        assert config_manager.concurrent_workers == 8
        
        # Verificar que um valor inválido gera uma exceção
        with pytest.raises(ValueError):
            config_manager.concurrent_workers = 0
    
    def test_property_scan_extensions(self, config_manager):
        """Testa a propriedade scan_extensions."""
        # Definir um novo valor
        new_extensions = [".mp4", ".avi"]
        config_manager.scan_extensions = new_extensions
        
        # Verificar que o valor foi atualizado
        assert config_manager.scan_extensions == new_extensions
    
    def test_property_include_zips(self, config_manager):
        """Testa a propriedade include_zips."""
        # Valor inicial deve ser True (padrão)
        assert config_manager.include_zips is True
        
        # Definir como False
        config_manager.include_zips = False
        
        # Verificar que o valor foi atualizado
        assert config_manager.include_zips is False
        
        # Verificar que valores não-booleanos são convertidos
        config_manager.include_zips = 1
        assert config_manager.include_zips is True
        
        config_manager.include_zips = 0
        assert config_manager.include_zips is False
    
    def test_property_min_file_size(self, config_manager):
        """Testa a propriedade min_file_size."""
        # Definir um novo valor
        config_manager.min_file_size = 2048
        
        # Verificar que o valor foi atualizado
        assert config_manager.min_file_size == 2048
        
        # Verificar que um valor inválido gera uma exceção
        with pytest.raises(ValueError):
            config_manager.min_file_size = -1
    
    def test_property_chunk_size(self, config_manager):
        """Testa a propriedade chunk_size."""
        # Definir um novo valor
        config_manager.chunk_size = 131072  # 128KB
        
        # Verificar que o valor foi atualizado
        assert config_manager.chunk_size == 131072
        
        # Verificar que um valor muito pequeno gera uma exceção
        with pytest.raises(ValueError):
            config_manager.chunk_size = 512  # Menor que 1KB
    
    def test_load_config_handles_invalid_json(self, temp_config_file):
        """Testa se _load_config lida corretamente com JSON inválido."""
        # Criar um arquivo com JSON inválido
        with open(temp_config_file, "w", encoding="utf-8") as f:
            f.write("{invalid json")
        
        # Criar o gerenciador de configurações (deve usar valores padrão)
        config = ConfigManager(temp_config_file)
        
        # Verificar que as configurações padrão foram usadas
        assert config.log_level == DEFAULT_CONFIG["log_level"]
    
    def test_load_config_merges_user_settings(self, temp_config_file):
        """Testa se _load_config mescla corretamente as configurações do usuário."""
        # Criar um arquivo com algumas configurações personalizadas
        user_config = {
            "log_level": "DEBUG",
            "include_zips": False
        }
        with open(temp_config_file, "w", encoding="utf-8") as f:
            json.dump(user_config, f)
        
        # Criar o gerenciador de configurações
        config = ConfigManager(temp_config_file)
        
        # Verificar que as configurações personalizadas foram aplicadas
        assert config.log_level == "DEBUG"
        assert config.include_zips is False
        
        # Verificar que as configurações não personalizadas mantêm os valores padrão
        assert config.concurrent_workers == DEFAULT_CONFIG["concurrent_workers"]
    
    def test_save_config_handles_permission_error(self, config_manager, monkeypatch):
        """Testa se save_config lida corretamente com erros de permissão."""
        # Mock de open que levanta PermissionError
        def mock_open(*args, **kwargs):
            raise PermissionError("Permissão negada")
        
        # Aplicar o mock
        monkeypatch.setattr("builtins.open", mock_open)
        
        # Verificar que a exceção apropriada é levantada
        with pytest.raises(OSError):
            config_manager.save_config() 