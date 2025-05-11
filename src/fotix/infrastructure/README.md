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
