"""
Módulo de configuração para a aplicação Fotix.

Este módulo é responsável por carregar e fornecer acesso às configurações da aplicação,
como caminhos de backup, níveis de log e outras configurações globais.

As configurações podem ser carregadas de:
- Arquivo de configuração (JSON, INI)
- Variáveis de ambiente
- Valores padrão definidos no código

Exemplo de uso:
    from fotix.config import Config
    
    # Carregar configurações de um arquivo
    config = Config.from_file('config.json')
    
    # Acessar uma configuração
    backup_path = config.get('backup_path')
    
    # Acessar com valor padrão se não existir
    log_level = config.get('log_level', 'INFO')
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Set, Tuple


class ConfigError(Exception):
    """Exceção levantada para erros relacionados à configuração."""
    pass


class Config:
    """
    Classe para gerenciar as configurações da aplicação.
    
    Fornece métodos para carregar configurações de diferentes fontes e
    acessar os valores de configuração de forma tipada.
    """
    
    def __init__(self, config_data: Dict[str, Any] = None):
        """
        Inicializa uma nova instância de Config.
        
        Args:
            config_data: Dicionário opcional com dados de configuração iniciais.
        """
        self._config: Dict[str, Any] = config_data or {}
        self._initialize_defaults()
    
    def _initialize_defaults(self) -> None:
        """
        Inicializa as configurações padrão se não estiverem definidas.
        """
        # Diretório de dados da aplicação
        if 'app_data_dir' not in self._config:
            self._config['app_data_dir'] = str(Path.home() / '.fotix')
        
        # Diretório de backup
        if 'backup_dir' not in self._config:
            self._config['backup_dir'] = str(Path(self._config['app_data_dir']) / 'backups')
        
        # Nível de log
        if 'log_level' not in self._config:
            self._config['log_level'] = 'INFO'
        
        # Tamanho do chunk para leitura de arquivos (em bytes)
        if 'file_read_chunk_size' not in self._config:
            self._config['file_read_chunk_size'] = 65536  # 64KB
        
        # Número máximo de workers para processamento paralelo
        if 'max_workers' not in self._config:
            self._config['max_workers'] = os.cpu_count() or 4
        
        # Extensões de arquivo a serem escaneadas por padrão
        if 'default_scan_extensions' not in self._config:
            self._config['default_scan_extensions'] = [
                '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp',  # Imagens
                '.mp4', '.avi', '.mov', '.wmv', '.mkv', '.flv',  # Vídeos
                '.mp3', '.wav', '.flac', '.ogg', '.aac',  # Áudio
                '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',  # Documentos
                '.zip', '.rar', '.7z', '.tar', '.gz'  # Arquivos compactados
            ]
    
    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> 'Config':
        """
        Cria uma instância de Config a partir de um arquivo de configuração.
        
        Suporta arquivos JSON e INI.
        
        Args:
            file_path: Caminho para o arquivo de configuração.
            
        Returns:
            Uma nova instância de Config com os dados carregados do arquivo.
            
        Raises:
            ConfigError: Se o arquivo não puder ser lido ou o formato for inválido.
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ConfigError(f"Arquivo de configuração não encontrado: {file_path}")
        
        try:
            if file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    return cls(config_data)
            else:
                raise ConfigError(f"Formato de arquivo de configuração não suportado: {file_path.suffix}")
        except json.JSONDecodeError as e:
            raise ConfigError(f"Erro ao decodificar arquivo JSON: {e}")
        except Exception as e:
            raise ConfigError(f"Erro ao carregar arquivo de configuração: {e}")
    
    @classmethod
    def from_env(cls, prefix: str = 'FOTIX_') -> 'Config':
        """
        Cria uma instância de Config a partir de variáveis de ambiente.
        
        As variáveis de ambiente devem ter o prefixo especificado.
        Por exemplo, FOTIX_BACKUP_DIR será mapeado para a configuração 'backup_dir'.
        
        Args:
            prefix: Prefixo das variáveis de ambiente a serem consideradas.
            
        Returns:
            Uma nova instância de Config com os dados carregados das variáveis de ambiente.
        """
        config_data = {}
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Remove o prefixo e converte para lowercase com underscore
                config_key = key[len(prefix):].lower()
                config_data[config_key] = value
        
        return cls(config_data)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém o valor de uma configuração.
        
        Args:
            key: Chave da configuração.
            default: Valor padrão a ser retornado se a chave não existir.
            
        Returns:
            O valor da configuração ou o valor padrão se a chave não existir.
        """
        return self._config.get(key, default)
    
    def get_path(self, key: str, default: Optional[Union[str, Path]] = None) -> Path:
        """
        Obtém o valor de uma configuração como um objeto Path.
        
        Args:
            key: Chave da configuração.
            default: Valor padrão a ser retornado se a chave não existir.
            
        Returns:
            O valor da configuração como um objeto Path.
            
        Raises:
            ConfigError: Se o valor não puder ser convertido para Path.
        """
        value = self.get(key, default)
        if value is None:
            raise ConfigError(f"Configuração não encontrada: {key}")
        
        try:
            return Path(value)
        except Exception as e:
            raise ConfigError(f"Erro ao converter configuração para Path: {e}")
    
    def get_int(self, key: str, default: Optional[int] = None) -> int:
        """
        Obtém o valor de uma configuração como um inteiro.
        
        Args:
            key: Chave da configuração.
            default: Valor padrão a ser retornado se a chave não existir.
            
        Returns:
            O valor da configuração como um inteiro.
            
        Raises:
            ConfigError: Se o valor não puder ser convertido para inteiro.
        """
        value = self.get(key, default)
        if value is None:
            raise ConfigError(f"Configuração não encontrada: {key}")
        
        try:
            return int(value)
        except ValueError:
            raise ConfigError(f"Valor de configuração não é um inteiro válido: {value}")
    
    def get_float(self, key: str, default: Optional[float] = None) -> float:
        """
        Obtém o valor de uma configuração como um float.
        
        Args:
            key: Chave da configuração.
            default: Valor padrão a ser retornado se a chave não existir.
            
        Returns:
            O valor da configuração como um float.
            
        Raises:
            ConfigError: Se o valor não puder ser convertido para float.
        """
        value = self.get(key, default)
        if value is None:
            raise ConfigError(f"Configuração não encontrada: {key}")
        
        try:
            return float(value)
        except ValueError:
            raise ConfigError(f"Valor de configuração não é um float válido: {value}")
    
    def get_bool(self, key: str, default: Optional[bool] = None) -> bool:
        """
        Obtém o valor de uma configuração como um booleano.
        
        Args:
            key: Chave da configuração.
            default: Valor padrão a ser retornado se a chave não existir.
            
        Returns:
            O valor da configuração como um booleano.
            
        Raises:
            ConfigError: Se o valor não puder ser convertido para booleano.
        """
        value = self.get(key, default)
        if value is None:
            raise ConfigError(f"Configuração não encontrada: {key}")
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            value = value.lower()
            if value in ('true', 'yes', '1', 'on'):
                return True
            if value in ('false', 'no', '0', 'off'):
                return False
        
        raise ConfigError(f"Valor de configuração não é um booleano válido: {value}")
    
    def get_list(self, key: str, default: Optional[List[Any]] = None) -> List[Any]:
        """
        Obtém o valor de uma configuração como uma lista.
        
        Args:
            key: Chave da configuração.
            default: Valor padrão a ser retornado se a chave não existir.
            
        Returns:
            O valor da configuração como uma lista.
            
        Raises:
            ConfigError: Se o valor não puder ser convertido para lista.
        """
        value = self.get(key, default)
        if value is None:
            raise ConfigError(f"Configuração não encontrada: {key}")
        
        if isinstance(value, list):
            return value
        
        if isinstance(value, str):
            try:
                # Tenta interpretar como JSON
                return json.loads(value)
            except json.JSONDecodeError:
                # Se não for JSON válido, divide por vírgulas
                return [item.strip() for item in value.split(',')]
        
        raise ConfigError(f"Valor de configuração não é uma lista válida: {value}")
    
    def set(self, key: str, value: Any) -> None:
        """
        Define o valor de uma configuração.
        
        Args:
            key: Chave da configuração.
            value: Valor a ser definido.
        """
        self._config[key] = value
    
    def save_to_file(self, file_path: Union[str, Path]) -> None:
        """
        Salva as configurações em um arquivo.
        
        Args:
            file_path: Caminho para o arquivo de configuração.
            
        Raises:
            ConfigError: Se não for possível salvar o arquivo.
        """
        file_path = Path(file_path)
        
        # Cria o diretório pai se não existir
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if file_path.suffix.lower() == '.json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self._config, f, indent=4)
            else:
                raise ConfigError(f"Formato de arquivo de configuração não suportado: {file_path.suffix}")
        except Exception as e:
            raise ConfigError(f"Erro ao salvar arquivo de configuração: {e}")
    
    def __getitem__(self, key: str) -> Any:
        """
        Permite acessar configurações usando a sintaxe de colchetes.
        
        Args:
            key: Chave da configuração.
            
        Returns:
            O valor da configuração.
            
        Raises:
            KeyError: Se a chave não existir.
        """
        if key not in self._config:
            raise KeyError(f"Configuração não encontrada: {key}")
        return self._config[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        """
        Permite definir configurações usando a sintaxe de colchetes.
        
        Args:
            key: Chave da configuração.
            value: Valor a ser definido.
        """
        self._config[key] = value
    
    def __contains__(self, key: str) -> bool:
        """
        Permite verificar se uma configuração existe usando o operador 'in'.
        
        Args:
            key: Chave da configuração.
            
        Returns:
            True se a configuração existir, False caso contrário.
        """
        return key in self._config
    
    def __repr__(self) -> str:
        """
        Retorna uma representação em string da instância de Config.
        
        Returns:
            Uma string representando a instância de Config.
        """
        return f"Config({self._config})"


# Instância global de configuração com valores padrão
default_config = Config()
