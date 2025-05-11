# Fotix - Módulo de Infraestrutura

Este diretório contém os módulos da camada de infraestrutura do Fotix, responsáveis pela interação com o mundo exterior e pelo fornecimento de serviços técnicos genéricos como abstrações.

## Módulos

### `interfaces.py`

O módulo `interfaces.py` define os contratos (interfaces) para os serviços da camada de infraestrutura, como acesso ao sistema de arquivos, manipulação de ZIPs, concorrência e backup. Estas interfaces permitem que as camadas superiores (core e aplicação) dependam de abstrações em vez de implementações concretas, facilitando testes e manutenção.

#### Interfaces Principais

- `IFileSystemService`: Abstrai operações no sistema de arquivos
- `IZipHandlerService`: Abstrai a leitura de arquivos dentro de arquivos ZIP
- `IConcurrencyService`: Abstrai a execução de tarefas concorrentes/paralelas
- `IBackupService`: Abstrai as operações de backup e restauração

#### Uso Básico

```python
from fotix.infrastructure.interfaces import IFileSystemService
from typing import Protocol

# Verificar se uma classe implementa a interface
def is_file_system_service(obj) -> bool:
    return isinstance(obj, IFileSystemService)

# Criar uma função que aceita qualquer implementação da interface
def process_files(fs_service: IFileSystemService, directory_path):
    for file_path in fs_service.list_directory_contents(directory_path):
        # Processar cada arquivo...
        pass
```

### `file_system.py`

O módulo `file_system.py` implementa a interface `IFileSystemService`, fornecendo métodos para operações no sistema de arquivos como leitura, escrita, movimentação para lixeira e listagem de diretórios.

#### Funcionalidades

- Obtenção de tamanho, data de criação e modificação de arquivos
- Streaming eficiente de conteúdo de arquivos em blocos
- Listagem recursiva de diretórios com filtros por extensão
- Movimentação segura de arquivos para a lixeira do sistema
- Cópia de arquivos preservando metadados
- Criação de diretórios com suporte a hierarquias
- Verificação de existência de caminhos
- Tratamento robusto de erros e logging de operações

#### Uso Básico

```python
from fotix.infrastructure.file_system import FileSystemService
from pathlib import Path

# Criar uma instância do serviço
fs_service = FileSystemService()

# Listar arquivos em um diretório
for file_path in fs_service.list_directory_contents(Path("/caminho/para/diretorio")):
    # Obter informações sobre o arquivo
    size = fs_service.get_file_size(file_path)
    mod_time = fs_service.get_modification_time(file_path)

    print(f"Arquivo: {file_path}, Tamanho: {size}, Modificado: {mod_time}")

# Copiar um arquivo
fs_service.copy_file(Path("origem.txt"), Path("destino.txt"))

# Mover um arquivo para a lixeira
fs_service.move_to_trash(Path("arquivo_indesejado.txt"))
```

### `concurrency.py`

O módulo `concurrency.py` implementa a interface `IConcurrencyService`, fornecendo métodos para executar tarefas em paralelo e em background, utilizando a biblioteca `concurrent.futures` do Python.

#### Funcionalidades

- **Execução paralela de tarefas**: Permite executar múltiplas funções simultaneamente, aproveitando múltiplos núcleos de CPU ou threads.
- **Tarefas em background**: Permite submeter tarefas para execução em segundo plano e monitorar seu progresso.
- **Configuração automática**: Determina automaticamente o número ideal de workers com base nos recursos do sistema ou nas configurações fornecidas.
- **Suporte a threads e processos**: Permite escolher entre `ThreadPoolExecutor` (para tarefas IO-bound) e `ProcessPoolExecutor` (para tarefas CPU-bound).
- **Gerenciamento de recursos**: Libera automaticamente os recursos quando não são mais necessários.

#### Uso Básico

```python
from fotix.infrastructure.concurrency import ConcurrencyService

# Criar uma instância do serviço
concurrency_service = ConcurrencyService()

# Definir algumas tarefas
def task1():
    # Alguma operação demorada
    return "Resultado 1"

def task2():
    # Outra operação demorada
    return "Resultado 2"

# Executar as tarefas em paralelo
results = concurrency_service.run_parallel([task1, task2])
print(results)  # ["Resultado 1", "Resultado 2"]

# Submeter uma tarefa para execução em background
future = concurrency_service.submit_background_task(
    lambda x: x * 2,
    10
)

# Obter o resultado (bloqueia até a conclusão)
result = future.result()  # 20
```

#### Considerações de Uso

- Use **threads** (`use_processes=False`, padrão) para tarefas **IO-bound** (leitura/escrita de arquivos, rede).
- Use **processos** (`use_processes=True`) para tarefas **CPU-bound** (cálculos intensivos, processamento de imagens).
- Lembre-se de chamar `shutdown()` quando terminar de usar o serviço para liberar recursos.

### `backup.py`

O módulo `backup.py` implementa a interface `IBackupService`, fornecendo métodos para criar, listar, restaurar e excluir backups de arquivos. Utiliza um sistema de armazenamento baseado em arquivos, com metadados em JSON.

#### Funcionalidades

- **Criação de backups**: Copia arquivos para uma área segura e gera IDs únicos para cada backup.
- **Armazenamento de metadados**: Salva informações como caminhos originais, hashes e timestamps.
- **Listagem de backups**: Fornece informações sobre backups disponíveis (data, número de arquivos, tamanho).
- **Restauração seletiva**: Permite restaurar arquivos para seus locais originais ou para um diretório específico.
- **Exclusão segura**: Remove backups e seus metadados de forma controlada.
- **Tratamento robusto de erros**: Lida com diversos tipos de erros durante as operações.

#### Uso Básico

```python
from fotix.infrastructure.backup import BackupService
from fotix.infrastructure.file_system import FileSystemService
from fotix.core.models import FileInfo
from pathlib import Path

# Criar instâncias dos serviços
fs_service = FileSystemService()
backup_service = BackupService(file_system_service=fs_service)

# Preparar arquivos para backup
files_to_backup = []
for file_path in fs_service.list_directory_contents(Path("/caminho/para/diretorio")):
    # Criar FileInfo para o arquivo
    file_info = FileInfo(
        path=file_path,
        size=fs_service.get_file_size(file_path),
        hash="hash_do_arquivo",  # Normalmente calculado pelo DuplicateFinder
        creation_time=fs_service.get_creation_time(file_path),
        modification_time=fs_service.get_modification_time(file_path)
    )
    files_to_backup.append((file_path, file_info))

# Criar backup
backup_id = backup_service.create_backup(files_to_backup)
print(f"Backup criado com ID: {backup_id}")

# Listar backups disponíveis
backups = backup_service.list_backups()
for backup in backups:
    print(f"Backup {backup['id']} criado em {backup['date']}, {backup['file_count']} arquivos")

# Restaurar backup para um diretório específico
backup_service.restore_backup(backup_id, Path("/caminho/para/restauracao"))

# Excluir backup
backup_service.delete_backup(backup_id)
```

### `zip_handler.py`

O módulo `zip_handler.py` implementa a interface `IZipHandlerService` para manipulação eficiente de arquivos ZIP. Ele utiliza a biblioteca `stream-unzip` para processar arquivos ZIP em streaming, sem extrair todo o conteúdo para o disco ou memória de uma vez.

#### Funcionalidades

- **Streaming de arquivos ZIP**: Acesso eficiente ao conteúdo de arquivos ZIP grandes, processando apenas o necessário.
- **Filtragem por extensão**: Capacidade de filtrar arquivos dentro do ZIP por extensão.
- **Acesso lazy ao conteúdo**: O conteúdo de cada arquivo é acessado apenas quando necessário, economizando memória.
- **Tratamento robusto de erros**: Lida com diversos tipos de erros que podem ocorrer durante o processamento.

#### Uso Básico

```python
from pathlib import Path
from fotix.infrastructure.zip_handler import ZipHandlerService

# Criar uma instância do serviço
zip_service = ZipHandlerService()

# Processar um arquivo ZIP, filtrando apenas imagens
zip_path = Path("caminho/para/arquivo.zip")
for file_name, file_size, content_fn in zip_service.stream_zip_entries(zip_path, file_extensions=['.jpg', '.png']):
    print(f"Arquivo: {file_name}, Tamanho: {file_size} bytes")

    # Processar o conteúdo do arquivo
    content_chunks = list(content_fn())
    content = b''.join(content_chunks)

    # Fazer algo com o conteúdo...
    # Por exemplo, salvar em um novo arquivo:
    # with open(f"output/{file_name}", "wb") as f:
    #     f.write(content)
```

#### Tratamento de Erros

O serviço lida com vários tipos de erros que podem ocorrer durante o processamento de arquivos ZIP:

- `FileNotFoundError`: Se o arquivo ZIP não existir.
- `PermissionError`: Se não houver permissão para ler o arquivo ZIP.
- `ValueError`: Se o arquivo não for um ZIP válido.
- `NotStreamUnzippable`: Se o arquivo ZIP não puder ser processado em streaming.

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
