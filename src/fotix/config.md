# Módulo de Configuração (fotix.config)

Este módulo é responsável por carregar e fornecer acesso às configurações da aplicação Fotix.

## Funcionalidades

- Carregamento de configurações de um arquivo JSON
- Valores padrão para todas as configurações essenciais
- API flexível para acessar e modificar configurações
- Validação de valores para propriedades importantes
- Tratamento de erros durante o carregamento e salvamento
- Pattern Singleton para acesso global às configurações

## Configurações Disponíveis

O módulo gerencia as seguintes configurações:

- `backup_dir`: Diretório onde os backups serão armazenados
- `log_level`: Nível de log da aplicação (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `log_file`: Arquivo onde os logs serão armazenados
- `concurrent_workers`: Número de workers para processamento concorrente
- `scan_extensions`: Lista de extensões de arquivo a serem consideradas durante a varredura
- `include_zips`: Se arquivos dentro de ZIPs devem ser considerados na busca
- `min_file_size`: Tamanho mínimo de arquivo (em bytes) para ser considerado
- `chunk_size`: Tamanho dos chunks para leitura de arquivos (em bytes)

## Uso

```python
from fotix.config import get_config

# Obter a instância do gerenciador de configurações
config = get_config()

# Acessar configurações
backup_dir = config.backup_dir
log_level = config.log_level

# Modificar configurações
config.log_level = "DEBUG"
config.concurrent_workers = 8

# Métodos genéricos
value = config.get("custom_key", "valor_padrao")
config.set("custom_key", "novo_valor")
config.update({"key1": "value1", "key2": "value2"})

# Salvar as configurações
config.save_config()
```

## Localização das Configurações

As configurações são armazenadas em `~/.fotix/config.json` por padrão, mas você pode especificar um arquivo diferente:

```python
from pathlib import Path
from fotix.config import get_config

custom_config = get_config(Path("/caminho/para/config.json"))
``` 