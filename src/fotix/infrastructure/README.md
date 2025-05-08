# Fotix - Camada de Infraestrutura

Esta camada contém os componentes responsáveis pela interação com o mundo exterior e fornecimento de serviços técnicos genéricos como abstrações.

## Módulos

### `logging_config.py`

Configuração do sistema de logging para a aplicação Fotix. Permite o registro de eventos e erros com diferentes níveis de severidade tanto em arquivo quanto no console.

#### Principais funcionalidades:

- Configuração centralizada do sistema de logging do Python
- Suporte a diferentes níveis de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Saída de logs para console e arquivo simultaneamente
- Arquivo de log configurável com rotação automática (máximo 10MB, mantendo até 5 backups)
- Atualização dinâmica do nível de log em tempo de execução

#### Utilização:

```python
from fotix.infrastructure.logging_config import setup_logging, get_logger, update_log_level

# Configurar o sistema de logging no início da aplicação
setup_logging()  # Usa os valores do arquivo de configuração

# Obter um logger para o módulo atual
logger = get_logger(__name__)

# Usar o logger
logger.debug("Mensagem de debug")
logger.info("Informação importante")
logger.warning("Alerta sobre algo")
logger.error("Um erro ocorreu")
logger.critical("Erro crítico")

# Alterar o nível de log em tempo de execução
update_log_level("DEBUG")  # Ativa todos os níveis de log
```

### Outros módulos (a serem implementados)

- `file_system.py`: Operações no sistema de arquivos
- `concurrency.py`: Gerenciamento de tarefas concorrentes e paralelas
- `backup.py`: Gerenciamento de backups de arquivos
- `zip_handler.py`: Manipulação de arquivos ZIP
- `interfaces.py`: Interfaces (contratos) para os serviços desta camada 