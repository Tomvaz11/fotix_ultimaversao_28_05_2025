"""
Módulo de configuração para o Fotix.

Este módulo fornece acesso às configurações da aplicação, como caminhos de backup,
níveis de log e outras configurações do sistema.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional, Any, Union

# Configuração padrão
DEFAULT_CONFIG = {
    "backup_dir": str(Path.home() / "fotix_backups"),
    "log_level": "INFO",
    "log_file": str(Path.home() / "fotix_logs" / "fotix.log"),
    "max_workers": 4,
    "default_scan_dir": str(Path.home()),
}

# Singleton para a configuração
_config_instance = None


def get_default_config_path() -> Path:
    """
    Retorna o caminho padrão para o arquivo de configuração.
    
    O arquivo de configuração é armazenado no diretório de configuração do usuário,
    que varia de acordo com o sistema operacional.
    
    Returns:
        Path: Caminho para o arquivo de configuração padrão.
    """
    # No Windows, usamos %APPDATA%
    if os.name == 'nt':
        config_dir = Path(os.environ.get('APPDATA', str(Path.home()))) / "Fotix"
    # No Linux/Mac, usamos ~/.config
    else:
        config_dir = Path.home() / ".config" / "fotix"
    
    # Garante que o diretório existe
    config_dir.mkdir(parents=True, exist_ok=True)
    
    return config_dir / "config.json"


def load_config(config_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """
    Carrega as configurações do arquivo especificado ou do arquivo padrão.
    
    Se o arquivo não existir, cria um novo com as configurações padrão.
    
    Args:
        config_path: Caminho opcional para o arquivo de configuração.
                    Se None, usa o caminho padrão.
    
    Returns:
        Dict[str, Any]: Dicionário com as configurações carregadas.
    
    Raises:
        ValueError: Se o arquivo de configuração existir mas não for um JSON válido.
    """
    if config_path is None:
        config_path = get_default_config_path()
    else:
        config_path = Path(config_path)
    
    # Se o arquivo não existir, cria com as configurações padrão
    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG.copy()
    
    # Carrega o arquivo existente
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Garante que todas as chaves padrão existam
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
        
        return config
    except json.JSONDecodeError as e:
        raise ValueError(f"Arquivo de configuração inválido: {e}") from e


def save_config(config: Dict[str, Any], config_path: Optional[Union[str, Path]] = None) -> None:
    """
    Salva as configurações no arquivo especificado ou no arquivo padrão.
    
    Args:
        config: Dicionário com as configurações a serem salvas.
        config_path: Caminho opcional para o arquivo de configuração.
                    Se None, usa o caminho padrão.
    
    Raises:
        IOError: Se não for possível escrever no arquivo.
    """
    if config_path is None:
        config_path = get_default_config_path()
    else:
        config_path = Path(config_path)
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)


def get_config(config_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """
    Retorna a instância singleton da configuração.
    
    Na primeira chamada, carrega a configuração do arquivo.
    Nas chamadas subsequentes, retorna a mesma instância, a menos que
    config_path seja especificado.
    
    Args:
        config_path: Caminho opcional para o arquivo de configuração.
                    Se None, usa o caminho padrão na primeira chamada
                    ou a instância já carregada nas chamadas subsequentes.
    
    Returns:
        Dict[str, Any]: Dicionário com as configurações.
    """
    global _config_instance
    
    if _config_instance is None or config_path is not None:
        _config_instance = load_config(config_path)
    
    return _config_instance


def get_log_level() -> int:
    """
    Retorna o nível de log configurado como um valor inteiro do módulo logging.
    
    Returns:
        int: Nível de log (logging.DEBUG, logging.INFO, etc.)
    """
    config = get_config()
    level_str = config.get("log_level", "INFO").upper()
    
    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    return log_levels.get(level_str, logging.INFO)


def get_backup_dir() -> Path:
    """
    Retorna o diretório de backup configurado.
    
    Returns:
        Path: Caminho para o diretório de backup.
    """
    config = get_config()
    backup_dir = Path(config.get("backup_dir", DEFAULT_CONFIG["backup_dir"]))
    
    # Garante que o diretório existe
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    return backup_dir


def update_config(key: str, value: Any) -> None:
    """
    Atualiza uma configuração específica e salva no arquivo.
    
    Args:
        key: Chave da configuração a ser atualizada.
        value: Novo valor para a configuração.
    """
    config = get_config()
    config[key] = value
    save_config(config)
