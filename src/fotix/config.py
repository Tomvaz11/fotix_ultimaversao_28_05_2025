"""
Módulo de configuração do Fotix.

Este módulo é responsável por carregar e fornecer acesso às configurações da aplicação,
como caminhos de backup, níveis de log, e outras configurações necessárias para o
funcionamento adequado do sistema.
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

# Diretório padrão para as configurações
DEFAULT_CONFIG_DIR = Path.home() / ".fotix"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.json"

# Configurações padrão
DEFAULT_CONFIG = {
    "backup_dir": str(DEFAULT_CONFIG_DIR / "backups"),
    "log_level": "INFO",
    "log_file": str(DEFAULT_CONFIG_DIR / "fotix.log"),
    "concurrent_workers": os.cpu_count() or 4,
    "scan_extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
    "include_zips": True,
    "min_file_size": 1024,  # 1KB - ignorar arquivos muito pequenos
    "chunk_size": 65536,  # 64KB - tamanho dos chunks para leitura de arquivos
}


class ConfigManager:
    """
    Gerenciador de configurações do Fotix.
    
    Responsável por carregar, armazenar e fornecer acesso às configurações da aplicação.
    Utiliza um arquivo JSON para persistência das configurações.
    """
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Inicializa o gerenciador de configurações.
        
        Args:
            config_file: Caminho para o arquivo de configuração. Se None, utiliza o padrão.
        """
        self._config_file = config_file or DEFAULT_CONFIG_FILE
        self._config = DEFAULT_CONFIG.copy()
        self._load_config()
    
    def _load_config(self) -> None:
        """
        Carrega as configurações do arquivo. Se o arquivo não existir, cria com os valores padrão.
        """
        try:
            if self._config_file.exists():
                with open(self._config_file, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                    # Atualiza as configurações padrão com as do usuário
                    self._config.update(user_config)
            else:
                # Garante que o diretório existe
                self._config_file.parent.mkdir(parents=True, exist_ok=True)
                # Cria o diretório de backup se não existir
                Path(self._config["backup_dir"]).mkdir(parents=True, exist_ok=True)
                # Salva as configurações padrão
                self.save_config()
        except (json.JSONDecodeError, PermissionError, OSError) as e:
            # Em caso de erro, mantém as configurações padrão
            print(f"Erro ao carregar configurações: {e}. Utilizando configurações padrão.")
    
    def save_config(self) -> None:
        """
        Salva as configurações atuais no arquivo.
        
        Raises:
            OSError: Se ocorrer um erro ao salvar o arquivo.
        """
        try:
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=4)
        except (PermissionError, OSError) as e:
            raise OSError(f"Não foi possível salvar as configurações: {e}")
    
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
            value: O novo valor.
        """
        self._config[key] = value
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        Atualiza múltiplas configurações de uma vez.
        
        Args:
            config_dict: Dicionário com as configurações a serem atualizadas.
        """
        self._config.update(config_dict)
    
    @property
    def backup_dir(self) -> Path:
        """Diretório onde os backups serão armazenados."""
        return Path(self._config["backup_dir"])
    
    @backup_dir.setter
    def backup_dir(self, value: Union[str, Path]) -> None:
        """
        Define o diretório de backup.
        
        Args:
            value: Novo diretório de backup.
        """
        self._config["backup_dir"] = str(value)
    
    @property
    def log_level(self) -> str:
        """Nível de log da aplicação."""
        return self._config["log_level"]
    
    @log_level.setter
    def log_level(self, value: str) -> None:
        """
        Define o nível de log.
        
        Args:
            value: Novo nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        """
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if value.upper() not in valid_levels:
            raise ValueError(f"Nível de log inválido. Valores válidos: {', '.join(valid_levels)}")
        self._config["log_level"] = value.upper()
    
    @property
    def log_file(self) -> Path:
        """Arquivo onde os logs serão armazenados."""
        return Path(self._config["log_file"])
    
    @log_file.setter
    def log_file(self, value: Union[str, Path]) -> None:
        """
        Define o arquivo de log.
        
        Args:
            value: Novo arquivo de log.
        """
        self._config["log_file"] = str(value)
    
    @property
    def concurrent_workers(self) -> int:
        """Número de workers para processamento concorrente."""
        return self._config["concurrent_workers"]
    
    @concurrent_workers.setter
    def concurrent_workers(self, value: int) -> None:
        """
        Define o número de workers.
        
        Args:
            value: Novo número de workers.
            
        Raises:
            ValueError: Se o valor for menor que 1.
        """
        if value < 1:
            raise ValueError("O número de workers deve ser pelo menos 1")
        self._config["concurrent_workers"] = value
    
    @property
    def scan_extensions(self) -> list:
        """Lista de extensões de arquivo a serem consideradas durante a varredura."""
        return self._config["scan_extensions"]
    
    @scan_extensions.setter
    def scan_extensions(self, value: list) -> None:
        """
        Define as extensões a serem escaneadas.
        
        Args:
            value: Nova lista de extensões.
        """
        self._config["scan_extensions"] = value
    
    @property
    def include_zips(self) -> bool:
        """Indica se arquivos dentro de ZIPs devem ser considerados na busca de duplicatas."""
        return self._config["include_zips"]
    
    @include_zips.setter
    def include_zips(self, value: bool) -> None:
        """
        Define se deve incluir arquivos ZIP.
        
        Args:
            value: True para incluir, False para ignorar.
        """
        self._config["include_zips"] = bool(value)
    
    @property
    def min_file_size(self) -> int:
        """Tamanho mínimo de arquivo (em bytes) para ser considerado na busca."""
        return self._config["min_file_size"]
    
    @min_file_size.setter
    def min_file_size(self, value: int) -> None:
        """
        Define o tamanho mínimo de arquivo.
        
        Args:
            value: Novo tamanho mínimo em bytes.
            
        Raises:
            ValueError: Se o valor for menor que 0.
        """
        if value < 0:
            raise ValueError("O tamanho mínimo de arquivo não pode ser negativo")
        self._config["min_file_size"] = value
    
    @property
    def chunk_size(self) -> int:
        """Tamanho dos chunks para leitura de arquivos (em bytes)."""
        return self._config["chunk_size"]
    
    @chunk_size.setter
    def chunk_size(self, value: int) -> None:
        """
        Define o tamanho dos chunks para leitura de arquivos.
        
        Args:
            value: Novo tamanho de chunk em bytes.
            
        Raises:
            ValueError: Se o valor for menor que 1024.
        """
        if value < 1024:  # Pelo menos 1KB
            raise ValueError("O tamanho do chunk deve ser pelo menos 1KB")
        self._config["chunk_size"] = value


# Instância global para acesso fácil às configurações
_config_instance = None


def get_config(config_file: Optional[Path] = None) -> ConfigManager:
    """
    Obtém a instância global do gerenciador de configurações ou cria uma nova se necessário.
    
    Args:
        config_file: Caminho opcional para o arquivo de configuração.
        
    Returns:
        A instância do gerenciador de configurações.
    """
    global _config_instance
    if _config_instance is None or config_file is not None:
        _config_instance = ConfigManager(config_file)
    return _config_instance 