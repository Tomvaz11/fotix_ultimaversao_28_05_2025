# Módulos de Infraestrutura do Fotix

Este diretório contém os módulos de infraestrutura do Fotix, que são responsáveis por interagir com o mundo exterior e fornecer serviços técnicos genéricos.

## Módulo de Logging (`logging_config.py`)

O módulo `logging_config.py` configura o sistema de logging padrão do Python para a aplicação Fotix. Ele define formatos de log, níveis e handlers (console, arquivo) com base nas configurações carregadas de `fotix.config`.

### Funcionalidades

- Configuração de logging baseada em configurações carregadas de `fotix.config`
- Suporte para logging em console e arquivo
- Rotação automática de arquivos de log
- Níveis de log configuráveis
- API simples para obter loggers configurados

### Como usar

```python
from fotix.infrastructure.logging_config import get_logger

# Obter um logger para o módulo atual
logger = get_logger(__name__)

# Usar o logger
logger.debug("Mensagem de debug")
logger.info("Mensagem de informação")
logger.warning("Mensagem de aviso")
logger.error("Mensagem de erro")
logger.critical("Mensagem crítica")

# Alterar o nível de log
from fotix.infrastructure.logging_config import set_log_level
set_log_level("DEBUG")  # Ou set_log_level(logging.DEBUG)
```

### Configuração

As configurações de logging são definidas no arquivo de configuração do Fotix, que é gerenciado pelo módulo `fotix.config`. As configurações padrão são:

```python
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
}
```

Você pode modificar essas configurações usando o módulo `fotix.config`:

```python
from fotix.config import get_config

config = get_config()
config.set("logging", "level", "DEBUG")
config.set("logging", "console", {"enabled": True, "level": "DEBUG"})
config.save()
```

### Localização dos Logs

Os arquivos de log são armazenados no diretório `~/.fotix/logs/`, onde `~` é o diretório home do usuário.
