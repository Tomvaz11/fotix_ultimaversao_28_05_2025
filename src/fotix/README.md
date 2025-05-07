# Fotix

Fotix é uma aplicação para detecção e gerenciamento de arquivos duplicados.

## Módulos

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
