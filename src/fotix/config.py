"""
Módulo de configuração para o Fotix.

Este módulo é responsável por carregar e fornecer acesso às configurações da aplicação,
como caminhos de backup, níveis de log, e outras configurações globais.
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union, List

# Valores padrão para configurações
DEFAULT_CONFIG = {
    "backup_dir": str(Path.home() / "fotix_backups"),
    "log_level": "INFO",
    "log_file": str(Path.home() / "fotix_logs" / "fotix.log"),
    "max_workers": 4,  # Número máximo de workers para processamento paralelo
    "chunk_size": 65536,  # Tamanho do chunk para leitura de arquivos (64KB)
    "supported_extensions": [
        # Imagens
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp",
        # Documentos
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt",
        # Áudio/Vídeo
        ".mp3", ".mp4", ".avi", ".mov", ".mkv", ".wav",
        # Arquivos compactados
        ".zip", ".rar", ".7z", ".tar", ".gz"
    ],
    "scan_inside_archives": True,  # Se deve escanear dentro de arquivos compactados
    "trash_enabled": True,  # Se deve mover para a lixeira em vez de excluir
}

# Nome do arquivo de configuração
CONFIG_FILENAME = "fotix_config.json"


class ConfigManager:
    """
    Gerenciador de configurações para o Fotix.
    
    Responsável por carregar, salvar e fornecer acesso às configurações da aplicação.
    """
    
    _instance = None
    _config: Dict[str, Any] = {}
    _config_file: Optional[Path] = None
    
    def __new__(cls):
        """Implementa o padrão Singleton para garantir uma única instância."""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Inicializa o gerenciador de configurações."""
        self._config = DEFAULT_CONFIG.copy()
        self._config_file = self._get_config_file_path()
        self._load_config()
    
    def _get_config_file_path(self) -> Path:
        """
        Determina o caminho para o arquivo de configuração.
        
        Em sistemas Windows, usa %APPDATA%/Fotix.
        Em sistemas Unix-like, usa ~/.config/fotix.
        
        Returns:
            Path: Caminho para o arquivo de configuração.
        """
        if os.name == 'nt':  # Windows
            config_dir = Path(os.environ.get('APPDATA', str(Path.home()))) / "Fotix"
        else:  # Unix-like
            config_dir = Path.home() / ".config" / "fotix"
        
        # Garante que o diretório existe
        config_dir.mkdir(parents=True, exist_ok=True)
        
        return config_dir / CONFIG_FILENAME
    
    def _load_config(self) -> None:
        """
        Carrega as configurações do arquivo de configuração.
        Se o arquivo não existir, cria um com as configurações padrão.
        """
        if not self._config_file.exists():
            self._save_config()
            return
        
        try:
            with open(self._config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                # Atualiza as configurações padrão com as carregadas
                self._config.update(loaded_config)
        except (json.JSONDecodeError, IOError) as e:
            # Em caso de erro, mantém as configurações padrão e loga o erro
            print(f"Erro ao carregar configurações: {e}. Usando configurações padrão.")
    
    def _save_config(self) -> None:
        """Salva as configurações atuais no arquivo de configuração."""
        try:
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4)
        except IOError as e:
            print(f"Erro ao salvar configurações: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém o valor de uma configuração.
        
        Args:
            key: A chave da configuração.
            default: Valor padrão caso a chave não exista.
            
        Returns:
            O valor da configuração ou o valor padrão.
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Define o valor de uma configuração.
        
        Args:
            key: A chave da configuração.
            value: O valor a ser definido.
        """
        self._config[key] = value
        self._save_config()
    
    def get_backup_dir(self) -> Path:
        """
        Obtém o diretório de backup.
        
        Returns:
            Path: O caminho para o diretório de backup.
        """
        backup_dir = Path(self.get("backup_dir"))
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir
    
    def get_log_level(self) -> int:
        """
        Obtém o nível de log configurado.
        
        Returns:
            int: O nível de log como um valor inteiro do módulo logging.
        """
        level_str = self.get("log_level", "INFO")
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return level_map.get(level_str, logging.INFO)
    
    def get_log_file(self) -> Path:
        """
        Obtém o caminho para o arquivo de log.
        
        Returns:
            Path: O caminho para o arquivo de log.
        """
        log_file = Path(self.get("log_file"))
        log_file.parent.mkdir(parents=True, exist_ok=True)
        return log_file
    
    def get_max_workers(self) -> int:
        """
        Obtém o número máximo de workers para processamento paralelo.
        
        Returns:
            int: O número máximo de workers.
        """
        return int(self.get("max_workers", 4))
    
    def get_chunk_size(self) -> int:
        """
        Obtém o tamanho do chunk para leitura de arquivos.
        
        Returns:
            int: O tamanho do chunk em bytes.
        """
        return int(self.get("chunk_size", 65536))
    
    def get_supported_extensions(self) -> List[str]:
        """
        Obtém a lista de extensões de arquivo suportadas.
        
        Returns:
            List[str]: Lista de extensões suportadas.
        """
        return self.get("supported_extensions", [])
    
    def is_scan_inside_archives_enabled(self) -> bool:
        """
        Verifica se o escaneamento dentro de arquivos compactados está habilitado.
        
        Returns:
            bool: True se habilitado, False caso contrário.
        """
        return bool(self.get("scan_inside_archives", True))
    
    def is_trash_enabled(self) -> bool:
        """
        Verifica se a movimentação para a lixeira está habilitada.
        
        Returns:
            bool: True se habilitado, False caso contrário.
        """
        return bool(self.get("trash_enabled", True))
    
    def reset_to_defaults(self) -> None:
        """Redefine todas as configurações para os valores padrão."""
        self._config = DEFAULT_CONFIG.copy()
        self._save_config()


# Exporta uma instância única do ConfigManager para uso em toda a aplicação
config_manager = ConfigManager()


# Funções de conveniência para acesso às configurações
def get(key: str, default: Any = None) -> Any:
    """
    Obtém o valor de uma configuração.
    
    Args:
        key: A chave da configuração.
        default: Valor padrão caso a chave não exista.
        
    Returns:
        O valor da configuração ou o valor padrão.
    """
    return config_manager.get(key, default)


def set(key: str, value: Any) -> None:
    """
    Define o valor de uma configuração.
    
    Args:
        key: A chave da configuração.
        value: O valor a ser definido.
    """
    config_manager.set(key, value)


def get_backup_dir() -> Path:
    """
    Obtém o diretório de backup.
    
    Returns:
        Path: O caminho para o diretório de backup.
    """
    return config_manager.get_backup_dir()


def get_log_level() -> int:
    """
    Obtém o nível de log configurado.
    
    Returns:
        int: O nível de log como um valor inteiro do módulo logging.
    """
    return config_manager.get_log_level()


def get_log_file() -> Path:
    """
    Obtém o caminho para o arquivo de log.
    
    Returns:
        Path: O caminho para o arquivo de log.
    """
    return config_manager.get_log_file()


def get_max_workers() -> int:
    """
    Obtém o número máximo de workers para processamento paralelo.
    
    Returns:
        int: O número máximo de workers.
    """
    return config_manager.get_max_workers()


def get_chunk_size() -> int:
    """
    Obtém o tamanho do chunk para leitura de arquivos.
    
    Returns:
        int: O tamanho do chunk em bytes.
    """
    return config_manager.get_chunk_size()


def get_supported_extensions() -> List[str]:
    """
    Obtém a lista de extensões de arquivo suportadas.
    
    Returns:
        List[str]: Lista de extensões suportadas.
    """
    return config_manager.get_supported_extensions()


def is_scan_inside_archives_enabled() -> bool:
    """
    Verifica se o escaneamento dentro de arquivos compactados está habilitado.
    
    Returns:
        bool: True se habilitado, False caso contrário.
    """
    return config_manager.is_scan_inside_archives_enabled()


def is_trash_enabled() -> bool:
    """
    Verifica se a movimentação para a lixeira está habilitada.
    
    Returns:
        bool: True se habilitado, False caso contrário.
    """
    return config_manager.is_trash_enabled()


def reset_to_defaults() -> None:
    """Redefine todas as configurações para os valores padrão."""
    config_manager.reset_to_defaults()
