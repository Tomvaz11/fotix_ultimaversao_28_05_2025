# Fotix - Módulos de Infraestrutura

Este pacote contém os módulos responsáveis pela interação com o mundo exterior e fornecimento de serviços técnicos genéricos como abstrações.

## Módulos

### logging_config.py

O módulo `logging_config.py` é responsável por configurar o sistema de logging padrão do Python para a aplicação Fotix, permitindo o registro de eventos e erros.

#### Principais funcionalidades

- Configuração do logger raiz com handlers para console e/ou arquivo
- Rotação automática de arquivos de log quando atingem um tamanho máximo
- Obtenção de loggers configurados para módulos específicos
- Alteração do nível de log em tempo de execução
- Integração com o módulo de configuração para obter níveis de log e caminhos de arquivo

#### Como usar

```python
from fotix.infrastructure.logging_config import configure_logging, get_logger, set_log_level

# Configurar o logging com valores padrão (obtidos de fotix.config)
configure_logging()

# Ou configurar com valores personalizados
configure_logging(
    log_level=logging.DEBUG,
    log_file=Path("/caminho/para/log.log"),
    console_output=True,
    file_output=True
)

# Obter um logger para um módulo específico
logger = get_logger(__name__)
logger.info("Mensagem informativa")
logger.debug("Mensagem de depuração")
logger.warning("Aviso")
logger.error("Erro")

# Alterar o nível de log em tempo de execução
set_log_level(logging.DEBUG)  # ou "DEBUG" como string
```

#### Configurações disponíveis

- `log_level`: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `log_file`: Caminho para o arquivo de log
- `log_format`: Formato das mensagens de log
- `date_format`: Formato da data/hora nas mensagens de log
- `console_output`: Se deve enviar logs para o console
- `file_output`: Se deve enviar logs para um arquivo
- `max_file_size`: Tamanho máximo do arquivo de log antes da rotação
- `backup_count`: Número máximo de arquivos de backup a manter

#### Constantes

- `DEFAULT_LOG_FORMAT`: Formato padrão das mensagens de log
- `DEFAULT_DATE_FORMAT`: Formato padrão da data/hora nas mensagens de log
- `MAX_LOG_SIZE`: Tamanho máximo do arquivo de log (10 MB)
- `BACKUP_COUNT`: Número máximo de arquivos de backup (5)
