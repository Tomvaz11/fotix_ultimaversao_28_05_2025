# Fotix - Módulos de Infraestrutura

Este pacote contém os módulos responsáveis pela interação com o mundo exterior e fornecimento de serviços técnicos genéricos como abstrações.

## Módulos

### file_system.py

O módulo `file_system.py` implementa a interface `IFileSystemService` para abstrair operações no sistema de arquivos, como leitura, escrita, movimentação para lixeira e listagem de diretórios.

#### Principais funcionalidades

- Obtenção de tamanho, datas de criação e modificação de arquivos
- Streaming de conteúdo de arquivos em blocos para processamento eficiente
- Listagem recursiva de diretórios com filtros por extensão
- Movimentação de arquivos para a lixeira do sistema (usando `send2trash`)
- Cópia de arquivos preservando metadados
- Criação de diretórios (incluindo diretórios aninhados)
- Verificação de existência de caminhos

#### Como usar

```python
from pathlib import Path
from fotix.infrastructure.file_system import FileSystemService

# Criar uma instância do serviço
fs_service = FileSystemService()

# Obter tamanho de um arquivo
size = fs_service.get_file_size(Path("caminho/para/arquivo.txt"))

# Ler conteúdo de um arquivo em blocos
for chunk in fs_service.stream_file_content(Path("arquivo_grande.dat")):
    # Processar cada bloco de bytes
    process_data(chunk)

# Listar arquivos em um diretório recursivamente
for file_path in fs_service.list_directory_contents(
    Path("diretorio"),
    recursive=True,
    file_extensions=[".jpg", ".png"]
):
    print(f"Encontrado: {file_path}")

# Mover um arquivo para a lixeira
fs_service.move_to_trash(Path("arquivo_a_remover.txt"))

# Copiar um arquivo
fs_service.copy_file(
    Path("arquivo_original.txt"),
    Path("copia_do_arquivo.txt")
)

# Criar um diretório
fs_service.create_directory(Path("novo_diretorio/subdiretorio"))

# Verificar se um caminho existe
if fs_service.path_exists(Path("arquivo.txt")):
    print("O arquivo existe")

# Obter timestamps
creation_time = fs_service.get_creation_time(Path("arquivo.txt"))
modification_time = fs_service.get_modification_time(Path("arquivo.txt"))
```

#### Tratamento de erros

O serviço implementa tratamento robusto de erros, lançando exceções apropriadas:

- `FileNotFoundError`: Quando um arquivo ou diretório não existe
- `PermissionError`: Quando há problemas de permissão
- `IsADirectoryError`: Quando um caminho de arquivo aponta para um diretório
- `NotADirectoryError`: Quando um caminho de diretório aponta para um arquivo
- `FileExistsError`: Quando um diretório já existe (ao criar com `exist_ok=False`)

Todas as operações são registradas no sistema de logging, facilitando a depuração.

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
