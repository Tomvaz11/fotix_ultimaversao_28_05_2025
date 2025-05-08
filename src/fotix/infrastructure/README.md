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

### `file_system.py`

Implementa `IFileSystemService` para fornecer acesso seguro e abstraído ao sistema de arquivos:

- Operações de leitura e cópia de arquivos
- Listagem recursiva e não-recursiva de diretórios com filtros por extensão
- Movimentação de arquivos para a lixeira do sistema
- Acesso a metadados como tamanho, data de criação e modificação
- Streaming eficiente de conteúdo de arquivos em blocos

#### Utilização:

```python
from pathlib import Path
from fotix.infrastructure.file_system import FileSystemService

# Criar uma instância do serviço
fs_service = FileSystemService()

# Operações com arquivos
arquivo = Path("exemplo.txt")
if fs_service.path_exists(arquivo):
    # Obter tamanho
    tamanho = fs_service.get_file_size(arquivo)
    print(f"Tamanho: {tamanho} bytes")
    
    # Obter metadados temporais
    data_criacao = fs_service.get_creation_time(arquivo)
    data_mod = fs_service.get_modification_time(arquivo)
    
    # Ler conteúdo em streaming
    for chunk in fs_service.stream_file_content(arquivo):
        # Processar cada bloco de bytes
        pass
    
    # Copiar o arquivo
    fs_service.copy_file(arquivo, Path("copia_exemplo.txt"))
    
    # Mover para a lixeira (remoção segura)
    fs_service.move_to_trash(Path("copia_exemplo.txt"))

# Operações com diretórios
diretorio = Path("meus_arquivos")
fs_service.create_directory(diretorio)

# Listar arquivos em um diretório (apenas JPG e PNG)
for arquivo in fs_service.list_directory_contents(
    diretorio, 
    recursive=True,
    file_extensions=[".jpg", ".png"]
):
    print(f"Encontrado: {arquivo}")
```

### Outros módulos (a serem implementados)

- `concurrency.py`: Gerenciamento de tarefas concorrentes e paralelas
- `backup.py`: Gerenciamento de backups de arquivos
- `zip_handler.py`: Manipulação de arquivos ZIP
- `interfaces.py`: Interfaces (contratos) para os serviços desta camada 