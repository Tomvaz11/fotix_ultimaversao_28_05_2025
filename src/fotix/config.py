"""
Módulo de configuração do Fotix.

Este módulo é responsável por carregar e fornecer acesso às configurações da aplicação.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

# Valores padrão para configurações
DEFAULT_CONFIG = {
    "logging": {
        "level": "INFO",
        "console": {
            "enabled": True,
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "file": {
            "enabled": True,
            "level": "DEBUG",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "filename": "fotix.log",
            "max_size_mb": 5,
            "backup_count": 3
        }
    },
    "backup": {
        "path": str(Path.home() / "fotix_backups"),
        "enabled": True
    }
}


class Config:
    """
    Classe para gerenciar as configurações da aplicação.
    
    Esta classe carrega as configurações de um arquivo JSON e fornece
    métodos para acessar essas configurações.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Inicializa a configuração.
        
        Args:
            config_path: Caminho para o arquivo de configuração. Se None,
                         usa o caminho padrão.
        """
        self._config_path = config_path or self._get_default_config_path()
        self._config = self._load_config()
    
    def _get_default_config_path(self) -> Path:
        """
        Retorna o caminho padrão para o arquivo de configuração.
        
        Returns:
            Path: Caminho para o arquivo de configuração.
        """
        # Usar o diretório de dados do usuário para armazenar a configuração
        app_data_dir = Path.home() / ".fotix"
        os.makedirs(app_data_dir, exist_ok=True)
        return app_data_dir / "config.json"
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Carrega as configurações do arquivo.
        
        Se o arquivo não existir, cria um novo com as configurações padrão.
        
        Returns:
            Dict[str, Any]: Configurações carregadas.
        """
        if not self._config_path.exists():
            # Criar o arquivo de configuração com valores padrão
            self._save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
        
        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            # Garantir que todas as configurações padrão estejam presentes
            self._ensure_default_values(config)
            return config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Erro ao carregar configuração: {e}. Usando valores padrão.")
            return DEFAULT_CONFIG
    
    def _ensure_default_values(self, config: Dict[str, Any]) -> None:
        """
        Garante que todas as configurações padrão estejam presentes no dicionário de configuração.
        
        Args:
            config: Dicionário de configuração a ser verificado e atualizado.
        """
        def _update_dict_recursive(target, source):
            for key, value in source.items():
                if key not in target:
                    target[key] = value
                elif isinstance(value, dict) and isinstance(target[key], dict):
                    _update_dict_recursive(target[key], value)
        
        _update_dict_recursive(config, DEFAULT_CONFIG)
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """
        Salva as configurações no arquivo.
        
        Args:
            config: Configurações a serem salvas.
        """
        try:
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
        except IOError as e:
            print(f"Erro ao salvar configuração: {e}")
    
    def get(self, section: str, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Obtém uma configuração.
        
        Args:
            section: Seção da configuração.
            key: Chave da configuração dentro da seção. Se None, retorna toda a seção.
            default: Valor padrão a ser retornado se a configuração não existir.
        
        Returns:
            Any: Valor da configuração ou o valor padrão se não existir.
        """
        if section not in self._config:
            return default
        
        if key is None:
            return self._config[section]
        
        return self._config[section].get(key, default)
    
    def set(self, section: str, key: str, value: Any) -> None:
        """
        Define uma configuração.
        
        Args:
            section: Seção da configuração.
            key: Chave da configuração dentro da seção.
            value: Valor a ser definido.
        """
        if section not in self._config:
            self._config[section] = {}
        
        self._config[section][key] = value
        self._save_config(self._config)
    
    def save(self) -> None:
        """
        Salva as configurações atuais no arquivo.
        """
        self._save_config(self._config)


# Instância global de configuração
_config_instance = None


def get_config(config_path: Optional[Path] = None) -> Config:
    """
    Obtém a instância global de configuração.
    
    Args:
        config_path: Caminho para o arquivo de configuração. Se None,
                     usa o caminho padrão.
    
    Returns:
        Config: Instância de configuração.
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_path)
    return _config_instance
