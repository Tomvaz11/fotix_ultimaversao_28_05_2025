# Módulos de Infraestrutura do Fotix

Este diretório contém os módulos de infraestrutura do Fotix, que são responsáveis por interagir com o mundo exterior e fornecer serviços técnicos genéricos.

## Módulo de Sistema de Arquivos (`file_system.py`)

O módulo `file_system.py` implementa a interface `IFileSystemService` definida em `interfaces.py`, fornecendo funcionalidades concretas para interagir com o sistema de arquivos local, como listar diretórios, obter tamanho de arquivo, ler conteúdo de forma eficiente (streaming), mover para a lixeira e copiar arquivos.

### Funcionalidades

- Obtenção de tamanho, data de criação e modificação de arquivos
- Leitura eficiente (streaming) de conteúdo de arquivos
- Listagem recursiva de diretórios com filtros de extensão
- Movimentação segura de arquivos para a lixeira do sistema
- Cópia de arquivos e criação de diretórios
- Verificação de existência de caminhos

### Como usar

```python
from pathlib import Path
from fotix.infrastructure.file_system import FileSystemService

# Criar uma instância do serviço
fs_service = FileSystemService()

# Listar arquivos em um diretório (recursivamente)
for file_path in fs_service.list_directory_contents(Path("caminho/para/diretorio")):
    print(f"Arquivo: {file_path}")
    print(f"Tamanho: {fs_service.get_file_size(file_path)} bytes")

# Listar apenas arquivos com extensões específicas
image_files = fs_service.list_directory_contents(
    Path("caminho/para/diretorio"),
    file_extensions=[".jpg", ".png", ".gif"]
)

# Ler conteúdo de um arquivo em blocos
for chunk in fs_service.stream_file_content(Path("caminho/para/arquivo.txt")):
    # Processar cada bloco de dados
    process_data(chunk)

# Mover um arquivo para a lixeira
fs_service.move_to_trash(Path("caminho/para/arquivo.txt"))

# Copiar um arquivo
fs_service.copy_file(
    Path("caminho/para/origem.txt"),
    Path("caminho/para/destino.txt")
)

# Criar um diretório
fs_service.create_directory(Path("caminho/para/novo/diretorio"))
```

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
