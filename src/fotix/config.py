"""
Módulo de configuração do Fotix.

Este módulo é responsável por carregar e fornecer acesso a configurações 
da aplicação, como caminhos de backup e níveis de log.
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union, List
from dataclasses import dataclass, field, asdict

# Constante com os valores padrão para níveis de log
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

@dataclass
class Config:
    """
    Classe que contém todas as configurações da aplicação.
    
    Utiliza dataclasses para fornecer tipagem estática e validação básica.
    """
    # Diretório onde os backups serão armazenados
    backup_dir: Path = field(default_factory=lambda: Path(os.path.expanduser("~")) / "Fotix" / "backups")
    
    # Nível de log padrão
    log_level: str = "info"
    
    # Arquivo de log
    log_file: Optional[Path] = field(default_factory=lambda: Path(os.path.expanduser("~")) / "Fotix" / "logs" / "fotix.log")
    
    # Número máximo de workers para processamento paralelo
    max_workers: int = min(32, (os.cpu_count() or 4) + 4)
    
    # Extensões de arquivo para processamento (vazio significa todas)
    file_extensions: List[str] = field(default_factory=list)
    
    # Tamanho do bloco para leitura de arquivos (em bytes)
    chunk_size: int = 65536
    
    # Tamanho mínimo de arquivo para considerar duplicatas (em bytes)
    # Arquivos menores que este tamanho serão ignorados na busca de duplicatas
    min_file_size: int = 1024  # 1KB
    
    def __post_init__(self):
        """Valida e normaliza os valores após a inicialização."""
        # Converte strings em Path se necessário
        if isinstance(self.backup_dir, str):
            self.backup_dir = Path(self.backup_dir)
        
        if isinstance(self.log_file, str):
            self.log_file = Path(self.log_file)
        
        # Valida o nível de log
        if self.log_level.lower() not in LOG_LEVELS:
            raise ValueError(
                f"Nível de log inválido: {self.log_level}. "
                f"Valores válidos: {', '.join(LOG_LEVELS.keys())}"
            )
        self.log_level = self.log_level.lower()
    
    def get_log_level_value(self) -> int:
        """Retorna o valor numérico do nível de log configurado."""
        return LOG_LEVELS[self.log_level]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a configuração para um dicionário."""
        config_dict = asdict(self)
        
        # Converte objetos Path para strings para facilitar a serialização
        if self.backup_dir:
            config_dict["backup_dir"] = str(self.backup_dir)
        
        if self.log_file:
            config_dict["log_file"] = str(self.log_file)
            
        return config_dict
    
    def save_to_file(self, file_path: Union[str, Path]) -> None:
        """
        Salva as configurações em um arquivo JSON.
        
        Args:
            file_path: Caminho para o arquivo onde as configurações serão salvas.
        
        Raises:
            OSError: Se houver erro ao salvar o arquivo.
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)
            
        # Cria o diretório pai se não existir
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=4)
        except OSError as e:
            logging.error(f"Erro ao salvar configurações: {e}")
            raise


# Instância global de configuração
_config_instance: Optional[Config] = None


def load_config(config_file: Optional[Union[str, Path]] = None) -> Config:
    """
    Carrega configurações de um arquivo JSON ou usa valores padrão.
    
    Args:
        config_file: Caminho para o arquivo de configuração JSON (opcional).
                     Se None, usa apenas os valores padrão.
    
    Returns:
        Uma instância de Config com as configurações carregadas.
    
    Raises:
        ValueError: Se o arquivo de configuração não contiver JSON válido.
        OSError: Se houver erro ao ler o arquivo.
    """
    global _config_instance
    
    # Se já existe uma instância de Config, retorna ela
    if _config_instance is not None:
        return _config_instance
    
    # Configuração padrão
    config = Config()
    
    # Se um arquivo de configuração foi especificado, tenta carregá-lo
    if config_file:
        if isinstance(config_file, str):
            config_file = Path(config_file)
            
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Atualiza a configuração com os valores do arquivo
                for key, value in config_data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
                
                # Executa a validação
                config.__post_init__()
            except json.JSONDecodeError as e:
                logging.error(f"Erro ao decodificar o arquivo de configuração: {e}")
                raise ValueError(f"Arquivo de configuração inválido: {e}")
            except OSError as e:
                logging.error(f"Erro ao ler o arquivo de configuração: {e}")
                raise
    
    # Armazena a instância global
    _config_instance = config
    return config


def get_config() -> Config:
    """
    Retorna a instância atual de configuração.
    
    Se nenhuma configuração foi carregada anteriormente, 
    carrega uma configuração padrão.
    
    Returns:
        A instância atual de Config.
    """
    global _config_instance
    
    if _config_instance is None:
        return load_config()
    
    return _config_instance


def reset_config() -> None:
    """
    Reseta a configuração para o estado não inicializado.
    
    Útil principalmente para testes.
    """
    global _config_instance
    _config_instance = None 