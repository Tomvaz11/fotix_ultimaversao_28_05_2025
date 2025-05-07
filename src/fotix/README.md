# Fotix

Fotix é uma aplicação para detecção e gerenciamento de arquivos duplicados.

## Módulos

### `fotix.infrastructure.logging_config`

O módulo `logging_config.py` é responsável por configurar o sistema de logging padrão do Python para a aplicação Fotix, permitindo o registro de eventos e erros.

#### Características

- Configuração do sistema de logging com base nas configurações da aplicação
- Suporte a diferentes níveis de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Saída para console e opcionalmente para arquivo
- Formato personalizável para mensagens de log
- Obtenção de loggers configurados para módulos específicos
- Tratamento de erros robusto

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

### `fotix.config`

O módulo `config.py` é responsável por carregar e fornecer acesso às configurações da aplicação, como caminhos de backup, níveis de log e outras configurações globais.

#### Características

- Carregamento de configurações de diferentes fontes:
  - Arquivo de configuração (JSON)
  - Variáveis de ambiente
  - Valores padrão definidos no código
- Acesso tipado às configurações (int, float, bool, path, list)
- Salvamento de configurações em arquivo
- Tratamento de erros robusto

#### Exemplo de uso

```python
from fotix.config import Config

# Carregar configurações de um arquivo
config = Config.from_file('config.json')

# Carregar configurações de variáveis de ambiente (FOTIX_*)
config = Config.from_env()

# Acessar uma configuração
backup_path = config.get('backup_path')

# Acessar com valor padrão se não existir
log_level = config.get('log_level', 'INFO')

# Acessar com tipo específico
max_workers = config.get_int('max_workers')
backup_dir = config.get_path('backup_dir')
enable_feature = config.get_bool('enable_feature')
file_extensions = config.get_list('file_extensions')

# Definir uma configuração
config.set('custom_setting', 'value')

# Salvar configurações em um arquivo
config.save_to_file('config.json')
```

#### Configurações padrão

O módulo define as seguintes configurações padrão:

- `app_data_dir`: Diretório de dados da aplicação (`~/.fotix`)
- `backup_dir`: Diretório de backup (`~/.fotix/backups`)
- `log_level`: Nível de log (`INFO`)
- `file_read_chunk_size`: Tamanho do chunk para leitura de arquivos (65536 bytes)
- `max_workers`: Número máximo de workers para processamento paralelo (número de CPUs)
- `default_scan_extensions`: Lista de extensões de arquivo a serem escaneadas por padrão
