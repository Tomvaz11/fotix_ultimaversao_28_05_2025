# Camada de Infraestrutura do Fotix

Esta camada é responsável pela interação com o mundo exterior e fornecimento de serviços técnicos genéricos como abstrações. Contém os wrappers para bibliotecas de baixo nível, garantindo que as camadas superiores dependam de interfaces estáveis e não de implementações concretas.

## Módulos

### `logging_config.py`

O módulo `logging_config.py` é responsável por configurar o sistema de logging padrão do Python para a aplicação Fotix, permitindo o registro de eventos e erros.

#### Características

- Configuração do sistema de logging com base nas configurações da aplicação
- Suporte a diferentes níveis de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Saída para console e opcionalmente para arquivo
- Formato personalizável para mensagens de log
- Obtenção de loggers configurados para módulos específicos
- Tratamento de erros robusto

#### Classes e Funções

- `LoggingError`: Exceção levantada para erros relacionados ao logging
- `LoggingConfig`: Classe para configurar o sistema de logging
  - `__init__(config=None)`: Inicializa uma nova instância de LoggingConfig
  - `configure()`: Configura o sistema de logging
  - `get_logger(name)`: Obtém um logger para o módulo especificado
  - `_get_log_file_path()`: Obtém o caminho para o arquivo de log
- `configure_logging(config=None)`: Configura o sistema de logging
- `get_logger(name)`: Obtém um logger configurado para o módulo especificado

#### Exemplo de uso

```python
from fotix.infrastructure.logging_config import configure_logging, get_logger
from fotix.config import Config

# Configurar o logging com as configurações padrão
configure_logging()

# Ou com configurações personalizadas
config = Config({'log_level': 'DEBUG', 'log_to_file': True})
configure_logging(config)

# Obter um logger para um módulo específico
logger = get_logger(__name__)

# Usar o logger
logger.info("Mensagem informativa")
logger.debug("Mensagem de depuração")
logger.warning("Aviso")
logger.error("Erro")
logger.critical("Erro crítico")
```

#### Configurações relacionadas

O módulo utiliza as seguintes configurações do módulo `fotix.config`:

- `log_level`: Nível de log (padrão: 'INFO')
- `log_format`: Formato das mensagens de log (padrão: '%(asctime)s - %(levelname)s - %(name)s - %(message)s')
- `log_date_format`: Formato da data/hora nos logs (padrão: '%Y-%m-%d %H:%M:%S')
- `log_to_file`: Se deve gravar logs em arquivo (padrão: False)
- `log_dir`: Diretório para arquivos de log (padrão: '~/.fotix/logs')
