# Fotix

Fotix é uma ferramenta para identificação e gerenciamento de arquivos duplicados.

## Módulos

### config.py

O módulo `config.py` é responsável por carregar e fornecer acesso às configurações da aplicação, como caminhos de backup, níveis de log e outras configurações globais.

#### Principais funcionalidades

- Carregamento e salvamento de configurações em um arquivo JSON
- Acesso a configurações através de uma interface simples
- Valores padrão para todas as configurações
- Métodos de conveniência para acessar configurações específicas
- Implementação do padrão Singleton para garantir uma única instância do gerenciador de configurações

#### Como usar

```python
from fotix.config import get, set, get_backup_dir, get_log_level

# Obter uma configuração
log_level = get_log_level()  # Retorna o nível de log como um valor do módulo logging

# Definir uma configuração
set("max_workers", 8)

# Obter o diretório de backup
backup_dir = get_backup_dir()  # Retorna um objeto Path
```

#### Configurações disponíveis

- `backup_dir`: Diretório onde os backups serão armazenados
- `log_level`: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `log_file`: Caminho para o arquivo de log
- `max_workers`: Número máximo de workers para processamento paralelo
- `chunk_size`: Tamanho do chunk para leitura de arquivos
- `supported_extensions`: Lista de extensões de arquivo suportadas
- `scan_inside_archives`: Se deve escanear dentro de arquivos compactados
- `trash_enabled`: Se deve mover para a lixeira em vez de excluir

#### Localização do arquivo de configuração

- Windows: `%APPDATA%\Fotix\fotix_config.json`
- Unix-like: `~/.config/fotix/fotix_config.json`
