# Fotix - Módulo de Infraestrutura

Este diretório contém os módulos da camada de infraestrutura do Fotix, responsáveis pela interação com o mundo exterior e pelo fornecimento de serviços técnicos genéricos como abstrações.

## Módulos

### `logging_config.py`

O módulo `logging_config.py` configura o sistema de logging padrão do Python para a aplicação Fotix, permitindo o registro de eventos e erros em diferentes níveis. Utiliza o módulo de configuração para obter parâmetros como nível de log e caminho do arquivo de log.

#### Funcionalidades

- Configuração do logger raiz do Python
- Definição de níveis de log com base nas configurações
- Configuração de handlers para console e arquivo
- Rotação automática de arquivos de log
- Formatação de mensagens de log

#### Uso Básico

```python
from fotix.infrastructure.logging_config import setup_logging, get_logger

# Configurar o logging (normalmente chamado apenas uma vez na inicialização)
setup_logging()

# Obter um logger para um módulo específico
logger = get_logger(__name__)

# Usar o logger
logger.debug("Mensagem de debug")
logger.info("Mensagem informativa")
logger.warning("Aviso")
logger.error("Erro")
logger.critical("Erro crítico")
```

#### Configurações Personalizadas

```python
from fotix.infrastructure.logging_config import setup_logging
import logging

# Configurar o logging com nível personalizado
setup_logging(log_level=logging.DEBUG)

# Configurar o logging com arquivo personalizado
setup_logging(log_file="/caminho/para/meu_log.log")

# Configurar o logging sem saída para console
setup_logging(console=False)

# Reconfigurar o logging após alterações nas configurações
from fotix.infrastructure.logging_config import reconfigure_logging
reconfigure_logging()
```

#### Integração com o Módulo de Configuração

O módulo utiliza `fotix.config` para obter configurações de logging:

- `log_level`: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `log_file`: Caminho para o arquivo de log

Se não forem fornecidos parâmetros explícitos para `setup_logging()`, esses valores serão obtidos automaticamente do módulo de configuração.
