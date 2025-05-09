"""Módulo de configuração para a aplicação Fotix.

Este módulo é responsável por carregar e fornecer acesso às configurações
da aplicação, como caminhos de backup, níveis de log, etc.

As configurações são carregadas a partir de variáveis de ambiente e/ou
um arquivo .env, com validação fornecida pela Pydantic.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import field_validator, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

# Níveis de log válidos, para validação
VALID_LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
LogLevelliteral = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class AppSettings(BaseSettings):
    """Define as configurações da aplicação.

    As configurações são carregadas de variáveis de ambiente ou de um arquivo .env.
    A prioridade é:
    1. Variáveis de ambiente (com prefixo FOTIX_).
    2. Valores no arquivo .env (com prefixo FOTIX_).
    3. Valores padrão definidos aqui.
    """

    BACKUP_PATH: Path = Path.home() / ".fotix_backups"
    LOG_LEVEL: LogLevelliteral = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
    LOG_FILE_PATH: Path | None = None # Caminho para o arquivo de log, se desejado

    # Configuração do Pydantic para carregar de um arquivo .env
    # O nome do arquivo .env pode ser configurado via variável de ambiente DOTENV_PATH
    model_config = SettingsConfigDict(
        env_prefix="FOTIX_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("LOG_LEVEL", mode="before")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        """Converte para maiúsculas e valida o nível de log."""
        if not isinstance(value, str):
            raise ValueError("LOG_LEVEL deve ser uma string")
        upper_value = value.upper()
        if upper_value not in VALID_LOG_LEVELS:
            raise ValueError(f"Nível de log inválido: '{value}'. Deve ser um de {VALID_LOG_LEVELS}")
        return upper_value

    @field_validator("BACKUP_PATH", mode="before")
    @classmethod
    def resolve_backup_path(cls, value: str | Path) -> Path:
        """Resolve o caminho de backup para um caminho absoluto.
        Garante que o diretório pai exista, se possível (best-effort).
        """
        path_value = Path(value) if isinstance(value, str) else value
        
        resolved_path = path_value.resolve()
        return resolved_path

    @field_validator("LOG_FILE_PATH", mode="before")
    @classmethod
    def resolve_log_file_path(cls, value: str | Path | None) -> Path | None:
        """Resolve o caminho do arquivo de log para um caminho absoluto, se fornecido."""
        if value is None:
            return None
        path_value = Path(value) if isinstance(value, str) else value
        return path_value.resolve()


@lru_cache
def get_settings() -> AppSettings:
    """Retorna uma instância cacheada das configurações da aplicação.

    A utilização de `lru_cache` garante que as configurações sejam carregadas
    apenas uma vez e que a mesma instância seja reutilizada, evitando
    leituras repetidas de arquivos ou variáveis de ambiente.

    Returns:
        AppSettings: Uma instância de AppSettings com as configurações carregadas.
    """
    try:
        return AppSettings()
    except ValidationError as e:
        print(f"Erro de validação ao carregar as configurações: {e}")
        raise


if __name__ == "__main__": # pragma: no cover
    # Exemplo de como usar e verificar as configurações
    print("Tentando carregar configurações...")
    try:
        settings = get_settings()
        print("\nConfigurações Carregadas com Sucesso:")
        print(f"  Caminho de Backup: {settings.BACKUP_PATH} (Existe: {settings.BACKUP_PATH.exists()})")
        print(f"  Nível de Log: {settings.LOG_LEVEL}")
        print(f"  Formato do Log: {settings.LOG_FORMAT}")
        print(f"  Caminho do Arquivo de Log: {settings.LOG_FILE_PATH}")

        # Para testar o carregamento de um .env, crie um arquivo .env na raiz do projeto
        # (onde o script é executado, ou onde Pydantic procura) com, por exemplo:
        # FOTIX_LOG_LEVEL="DEBUG"
        # FOTIX_BACKUP_PATH="/tmp/my_fotix_backups"
        # FOTIX_LOG_FILE_PATH="/tmp/fotix_app.log"

        print("\nPara testar com variáveis de ambiente ou arquivo .env:")
        print("Exemplo de arquivo .env (nomeado '.env' na raiz do projeto):")
        print("FOTIX_LOG_LEVEL=DEBUG")
        print("FOTIX_BACKUP_PATH=/tmp/fotix_test_backups")
        print("FOTIX_LOG_FILE_PATH=fotix_app.log")
        print("\nExemplo de variáveis de ambiente (Linux/macOS):")
        print("export FOTIX_LOG_LEVEL=WARNING")
        print("export FOTIX_BACKUP_PATH='~/fotix_env_backups'")
        print("\nExemplo de variáveis de ambiente (Windows PowerShell):")
        print("$env:FOTIX_LOG_LEVEL='CRITICAL'")
        print("$env:FOTIX_BACKUP_PATH='C:\\\\Users\\\\SeuUsuario\\\\fotix_env_backups_win'")
        
        # Teste de criação de diretório (opcional, pode ser movido para lógica da aplicação)
        # if not settings.BACKUP_PATH.exists():
        #     try:
        #         print(f"\nTentando criar o diretório de backup em: {settings.BACKUP_PATH}")
        #         settings.BACKUP_PATH.mkdir(parents=True, exist_ok=True)
        #         print(f"Diretório de backup criado ou já existente.")
        #     except Exception as e:
        #         print(f"Falha ao criar diretório de backup: {e}")
        # else:
        #     print(f"\nDiretório de backup já existe em: {settings.BACKUP_PATH}")

    except ValidationError as e:
        print("\nErro Crítico: Falha ao carregar as configurações da aplicação.")
        print("Detalhes do Erro de Validação:")
        print(e)
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")