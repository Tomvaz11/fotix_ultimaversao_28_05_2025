## Proposta de Arquitetura Técnica: Fotix v1.6

### 1. Visão Geral da Arquitetura

A arquitetura proposta para o Fotix é uma **Arquitetura em Camadas (Layered Architecture)**. Esta abordagem promove uma clara separação de responsabilidades, melhora a manutenibilidade, testabilidade e facilita a evolução do sistema. As camadas principais serão:

1.  **Camada de Apresentação (UI - User Interface):** Responsável pela interação com o usuário. (PySide6)
2.  **Camada de Aplicação (Application Services):** Orquestra os casos de uso, coordenando a lógica de domínio e os serviços de infraestrutura. Não contém lógica de negócio.
3.  **Camada de Domínio (Domain):** Contém a lógica de negócio central do Fotix, incluindo a identificação de duplicatas e a lógica de seleção de arquivos. É independente de UI e infraestrutura.
4.  **Camada de Infraestrutura (Infrastructure):** Lida com preocupações transversais e interações com o sistema externo, como acesso ao sistema de arquivos, hashing, concorrência, logging e backup. Fornece implementações concretas para as interfaces definidas pela camada de aplicação ou domínio.

**Justificativa:**
A arquitetura em camadas é ideal para aplicações desktop como o Fotix porque:
*   **Modularidade e SRP:** Cada camada tem uma responsabilidade clara.
*   **Testabilidade:** As camadas de Domínio e Aplicação podem ser testadas independentemente da UI e da infraestrutura real (usando mocks/stubs para as interfaces da infraestrutura).
*   **Manutenibilidade:** Mudanças na UI não devem impactar a lógica de negócio, e vice-versa. A troca de uma biblioteca de infraestrutura (ex: um novo algoritmo de hash) pode ser feita alterando apenas a implementação na camada de Infraestrutura, sem afetar as camadas superiores, desde que a interface seja mantida.
*   **Clareza:** A estrutura é bem compreendida e facilita a navegação no código.

### 2. Diagrama de Componentes (Simplificado)

```mermaid
graph TD
    subgraph Camada de Apresentação (UI)
        UI_Main[fotix.ui.MainWindow]
        UI_Config[fotix.ui.views.ConfigView]
        UI_Progress[fotix.ui.views.ProgressView]
        UI_Results[fotix.ui.views.ResultsView]
        UI_Restore[fotix.ui.views.RestoreView]
    end

    subgraph Camada de Aplicação (Application Services)
        App_Scan[fotix.application_services.ScanOrchestratorService]
        App_FileOp[fotix.application_services.FileOperationService]
        App_Restore[fotix.application_services.RestoreOrchestratorService]
    end

    subgraph Camada de Domínio (Domain)
        Domain_Models[fotix.domain.models]
        Domain_Finder[fotix.domain.duplicate_finder.DuplicateFinder]
        Domain_Selector[fotix.domain.selection_strategy.SelectionStrategy]
    end

    subgraph Camada de Infraestrutura (Infrastructure)
        Infra_FS[fotix.infrastructure.file_system_service.FileSystemServiceImpl]
        Infra_Zip[fotix.infrastructure.zip_service.ZipServiceImpl]
        Infra_Hash[fotix.infrastructure.hashing_service.HashingServiceImpl]
        Infra_Concurrency[fotix.infrastructure.concurrency_service.ConcurrencyServiceImpl]
        Infra_Backup[fotix.infrastructure.backup_service.BackupServiceImpl]
        Infra_Log[fotix.infrastructure.logging_service.LoggingServiceImpl]

        Infra_IF_FS[fotix.infrastructure.interfaces.IFileSystemService]
        Infra_IF_Zip[fotix.infrastructure.interfaces.IZipService]
        Infra_IF_Hash[fotix.infrastructure.interfaces.IHashingService]
        Infra_IF_Concurrency[fotix.infrastructure.interfaces.IConcurrencyService]
        Infra_IF_Backup[fotix.infrastructure.interfaces.IBackupService]
        Infra_IF_Log[fotix.infrastructure.interfaces.ILoggingService]
    end

    %% Conexões da UI para Aplicação
    UI_Main --> App_Scan
    UI_Main --> App_FileOp
    UI_Main --> App_Restore
    UI_Config --> App_Scan
    UI_Results --> App_FileOp
    UI_Restore --> App_Restore

    %% Conexões da Aplicação para Domínio
    App_Scan --> Domain_Finder
    App_Scan --> Domain_Selector
    App_Scan --> Domain_Models
    App_FileOp --> Domain_Models

    %% Conexões da Aplicação para Interfaces de Infraestrutura
    App_Scan --> Infra_IF_FS
    App_Scan --> Infra_IF_Zip
    App_Scan --> Infra_IF_Hash
    App_Scan --> Infra_IF_Concurrency
    App_Scan --> Infra_IF_Log

    App_FileOp --> Infra_IF_FS
    App_FileOp --> Infra_IF_Backup
    App_FileOp --> Infra_IF_Log

    App_Restore --> Infra_IF_Backup
    App_Restore --> Infra_IF_FS
    App_Restore --> Infra_IF_Log

    %% Implementações de Interfaces de Infraestrutura
    Infra_FS -.-> Infra_IF_FS
    Infra_Zip -.-> Infra_IF_Zip
    Infra_Hash -.-> Infra_IF_Hash
    Infra_Concurrency -.-> Infra_IF_Concurrency
    Infra_Backup -.-> Infra_IF_Backup
    Infra_Log -.-> Infra_IF_Log

    %% Dependências do Domínio (apenas para modelos, não para infraestrutura diretamente)
    Domain_Finder --> Domain_Models
    Domain_Selector --> Domain_Models

    %% Estilo
    classDef ui fill:#D6EAF8,stroke:#3498DB,stroke-width:2px;
    classDef app fill:#D1F2EB,stroke:#1ABC9C,stroke-width:2px;
    classDef domain fill:#FCF3CF,stroke:#F1C40F,stroke-width:2px;
    classDef infra fill:#FADBD8,stroke:#E74C3C,stroke-width:2px;
    classDef infra_if fill:#F5EEF8,stroke:#AF7AC5,stroke-width:2px;

    class UI_Main,UI_Config,UI_Progress,UI_Results,UI_Restore ui;
    class App_Scan,App_FileOp,App_Restore app;
    class Domain_Models,Domain_Finder,Domain_Selector domain;
    class Infra_FS,Infra_Zip,Infra_Hash,Infra_Concurrency,Infra_Backup,Infra_Log infra;
    class Infra_IF_FS,Infra_IF_Zip,Infra_IF_Hash,Infra_IF_Concurrency,Infra_IF_Backup,Infra_IF_Log infra_if;
```

### 3. Descrição dos Componentes/Módulos

#### 3.1. Camada de Apresentação (UI) - `fotix.ui`

*   **Responsabilidade Principal:** Interagir com o usuário, coletar entradas, exibir progresso e resultados, e delegar ações para a Camada de Aplicação.
*   **Tecnologias Chave:** PySide6.
*   **Decomposição:**
    *   `fotix.ui.main_window.MainWindow`:
        *   **Propósito:** Janela principal da aplicação, orquestra as diferentes views e menus.
        *   **Interações:** `ScanOrchestratorService`, `FileOperationService`, `RestoreOrchestratorService`.
        *   **Unidade de Trabalho:** Sim, principal container da UI.
    *   `fotix.ui.views.config_view.ConfigView`:
        *   **Propósito:** Permitir ao usuário selecionar diretórios, arquivos ZIP e configurar opções de escaneamento (ex: critérios de seleção).
        *   **Interações:** `ScanOrchestratorService` (para iniciar o escaneamento com as configurações).
        *   **Unidade de Trabalho:** Sim.
    *   `fotix.ui.views.progress_view.ProgressView`:
        *   **Propósito:** Exibir o progresso do escaneamento e remoção de arquivos, incluindo logs e estatísticas parciais.
        *   **Interações:** Observa eventos/sinais emitidos pelo `ScanOrchestratorService` e `FileOperationService`.
        *   **Unidade de Trabalho:** Sim.
    *   `fotix.ui.views.results_view.ResultsView`:
        *   **Propósito:** Apresentar os grupos de arquivos duplicados encontrados, qual arquivo foi selecionado para manter e permitir que o usuário revise/anule decisões antes da remoção.
        *   **Interações:** `FileOperationService` (para confirmar a remoção).
        *   **Unidade de Trabalho:** Sim.
    *   `fotix.ui.views.restore_view.RestoreView`:
        *   **Propósito:** Listar arquivos que foram "removidos" (movidos para backup) e permitir ao usuário restaurá-los para o local original.
        *   **Interações:** `RestoreOrchestratorService`.
        *   **Unidade de Trabalho:** Sim.
    *   `fotix.ui.widgets`: Módulo para componentes de UI reutilizáveis (ex: seletor de arquivos customizado, tabelas, etc.).
*   **Dependências Diretas:**
    *   `fotix.application_services.scan_orchestrator`
    *   `fotix.application_services.file_operation_service`
    *   `fotix.application_services.restore_orchestrator`
    *   `fotix.utils.helpers` (para formatação, etc.)

#### 3.2. Camada de Aplicação (Application Services) - `fotix.application_services`

*   **Responsabilidade Principal:** Orquestrar os fluxos de trabalho da aplicação (casos de uso). Não contém lógica de negócio, mas coordena os componentes do domínio e da infraestrutura para realizar tarefas.
*   **Tecnologias Chave:** Python.
*   **Componentes:**
    *   `fotix.application_services.scan_orchestrator.ScanOrchestratorService`:
        *   **Responsabilidade:** Gerencia todo o processo de escaneamento:
            1.  Recebe configurações da UI.
            2.  Usa `IFileSystemService` e `IZipService` para listar arquivos.
            3.  Usa `IConcurrencyService` para paralelizar a leitura e hashing.
            4.  Usa `IHashingService` para calcular hashes.
            5.  Usa `DuplicateFinder` (domínio) para identificar grupos de duplicatas.
            6.  Usa `SelectionStrategy` (domínio) para determinar qual arquivo manter.
            7.  Retorna os resultados para a UI.
            8.  Emite sinais/eventos de progresso.
        *   **Dependências Diretas:**
            *   `fotix.domain.duplicate_finder.DuplicateFinder`
            *   `fotix.domain.selection_strategy.SelectionStrategy`
            *   `fotix.domain.models`
            *   `fotix.infrastructure.interfaces.IFileSystemService`
            *   `fotix.infrastructure.interfaces.IZipService`
            *   `fotix.infrastructure.interfaces.IHashingService`
            *   `fotix.infrastructure.interfaces.IConcurrencyService`
            *   `fotix.infrastructure.interfaces.ILoggingService`
    *   `fotix.application_services.file_operation_service.FileOperationService`:
        *   **Responsabilidade:** Gerencia a remoção segura de arquivos duplicados e o backup.
            1.  Recebe a lista de arquivos a serem removidos (do `ScanOrchestratorService` ou da UI após revisão).
            2.  Usa `IBackupService` para fazer backup de cada arquivo antes da remoção.
            3.  Usa `IFileSystemService` (que usa `send2trash`) para remover o arquivo.
            4.  Gera relatório final.
        *   **Dependências Diretas:**
            *   `fotix.domain.models`
            *   `fotix.infrastructure.interfaces.IFileSystemService`
            *   `fotix.infrastructure.interfaces.IBackupService`
            *   `fotix.infrastructure.interfaces.ILoggingService`
    *   `fotix.application_services.restore_orchestrator.RestoreOrchestratorService`:
        *   **Responsabilidade:** Gerencia a restauração de arquivos a partir do backup.
            1.  Usa `IBackupService` para listar itens passíveis de restauração.
            2.  Usa `IBackupService` para executar a restauração de um item selecionado.
            3.  Usa `IFileSystemService` para verificar conflitos ou mover o arquivo restaurado.
        *   **Dependências Diretas:**
            *   `fotix.infrastructure.interfaces.IBackupService`
            *   `fotix.infrastructure.interfaces.IFileSystemService`
            *   `fotix.infrastructure.interfaces.ILoggingService`

#### 3.3. Camada de Domínio (Domain) - `fotix.domain`

*   **Responsabilidade Principal:** Contém a lógica de negócio pura e os modelos de dados centrais. É o coração da aplicação, independente de frameworks ou preocupações de IO.
*   **Tecnologias Chave:** Python, Dataclasses (ou Pydantic para validação).
*   **Componentes:**
    *   `fotix.domain.models`:
        *   **Responsabilidade:** Define as estruturas de dados centrais (ex: `FileItem`, `DuplicateGroup`, `ScanCriteria`). Serão usados dataclasses ou modelos Pydantic.
        *   **Dependências Diretas:** Nenhuma (além de tipos Python e Pydantic/Dataclasses).
    *   `fotix.domain.duplicate_finder.DuplicateFinder`:
        *   **Responsabilidade:** Implementa o algoritmo para identificar arquivos duplicados a partir de uma lista de `FileItem` com seus hashes e metadados. Realiza a pré-filtragem por tamanho e depois o agrupamento por hash.
        *   **Dependências Diretas:**
            *   `fotix.domain.models`
    *   `fotix.domain.selection_strategy.SelectionStrategy`:
        *   **Responsabilidade:** Implementa a lógica inteligente para decidir qual arquivo manter e quais remover dentro de um `DuplicateGroup`, com base nos critérios definidos (resolução, data, nome). Este pode ser um componente com diferentes implementações (Strategy Pattern).
        *   **Dependências Diretas:**
            *   `fotix.domain.models`

#### 3.4. Camada de Infraestrutura (Infrastructure) - `fotix.infrastructure`

*   **Responsabilidade Principal:** Fornece implementações concretas para as interfaces necessárias pelas camadas de Aplicação e Domínio. Lida com interações com o sistema de arquivos, bibliotecas de terceiros, concorrência, etc.
*   **Tecnologias Chave:** Python, `pathlib`, `shutil`, `send2trash`, `concurrent.futures`, `blake3`, `stream-unzip`, `logging`.
*   **Componentes (Implementações dos Serviços):**
    *   `fotix.infrastructure.file_system_service.FileSystemServiceImpl`:
        *   **Responsabilidade:** Implementa `IFileSystemService`. Usa `pathlib` para navegação e metadados, `shutil` para cópia/movimentação, e `send2trash` para remoção segura.
        *   **Dependências Diretas:** Nenhuma (além das bibliotecas Python padrão e `send2trash`).
    *   `fotix.infrastructure.zip_service.ZipServiceImpl`:
        *   **Responsabilidade:** Implementa `IZipService`. Usa `stream-unzip` para leitura eficiente de arquivos ZIP.
        *   **Dependências Diretas:** Nenhuma (além de `stream-unzip`).
    *   `fotix.infrastructure.hashing_service.HashingServiceImpl`:
        *   **Responsabilidade:** Implementa `IHashingService`. Usa `BLAKE3` para cálculo de hash.
        *   **Dependências Diretas:** Nenhuma (além de `blake3`).
    *   `fotix.infrastructure.concurrency_service.ConcurrencyServiceImpl`:
        *   **Responsabilidade:** Implementa `IConcurrencyService`. Usa `concurrent.futures.ThreadPoolExecutor` ou `ProcessPoolExecutor` para executar tarefas em paralelo.
        *   **Dependências Diretas:** Nenhuma (além de `concurrent.futures`).
    *   `fotix.infrastructure.backup_service.BackupServiceImpl`:
        *   **Responsabilidade:** Implementa `IBackupService`. Gerencia o backup (cópia para um local seguro) e a restauração de arquivos. Pode manter um índice simples dos backups (ex: arquivo JSON).
        *   **Dependências Diretas:** `fotix.infrastructure.interfaces.IFileSystemService` (para operações de arquivo).
    *   `fotix.infrastructure.logging_service.LoggingServiceImpl`:
        *   **Responsabilidade:** Implementa `ILoggingService`. Configura e usa o módulo `logging` do Python para registrar eventos da aplicação.
        *   **Dependências Diretas:** Nenhuma (além de `logging`).
*   **Interfaces (Contratos):**
    *   `fotix.infrastructure.interfaces` (módulo contendo as definições das interfaces como `IFileSystemService`, `IZipService`, etc.)

#### 3.5. Utilitários - `fotix.utils`

*   **Responsabilidade Principal:** Funções e classes auxiliares genéricas que podem ser usadas em múltiplas camadas (ex: formatação de datas, manipulação de strings, etc.).
*   **Componentes:**
    *   `fotix.utils.helpers`: Módulo com funções utilitárias.
*   **Dependências Diretas:** Nenhuma (além de bibliotecas Python padrão).

### 4. Definição das Interfaces Principais (`fotix.infrastructure.interfaces`)

As interfaces são definidas usando `typing.Protocol` para type hinting e verificação estática.

```python
# fotix/infrastructure/interfaces.py
from typing import Protocol, List, Iterator, Any, Dict, Optional, Tuple, Callable
from pathlib import Path
import dataclasses # ou from pydantic import BaseModel

# --- Modelos de Dados Comuns (Podem residir em fotix.domain.models) ---
@dataclasses.dataclass
class FileItem:
    path: Path
    size: int
    creation_time: float # Timestamp
    modification_time: float # Timestamp
    # Adicionar metadados específicos de imagem/vídeo aqui se necessário
    # ex: resolution: Optional[Tuple[int, int]] = None
    # ex: duration: Optional[float] = None # para vídeos
    content_hash: Optional[str] = None
    is_from_zip: bool = False
    zip_path: Optional[Path] = None
    name_in_zip: Optional[str] = None

@dataclasses.dataclass
class DuplicateGroup:
    files: List[FileItem]
    file_to_keep: Optional[FileItem] = None # Preenchido pela SelectionStrategy

@dataclasses.dataclass
class ScanSettings:
    paths_to_scan: List[Path]
    include_zip_files: bool
    # Critérios de seleção, etc.
    # ex: prefer_older_creation_date: bool = True
    # ex: prefer_higher_resolution: bool = True

@dataclasses.dataclass
class BackupManifestEntry:
    original_path: Path
    backup_path: Path
    timestamp: float
    metadata: Dict[str, Any] # Para infos adicionais do arquivo original

# --- Interfaces de Serviço ---

class IFileSystemService(Protocol):
    """Interface para operações no sistema de arquivos."""

    def get_file_size(self, path: Path) -> int:
        """Retorna o tamanho do arquivo em bytes."""
        ...

    def path_exists(self, path: Path) -> bool:
        """Verifica se um caminho existe."""
        ...

    def is_file(self, path: Path) -> bool:
        """Verifica se um caminho é um arquivo."""
        ...

    def is_dir(self, path: Path) -> bool:
        """Verifica se um caminho é um diretório."""
        ...

    def walk_directory(self, dir_path: Path) -> Iterator[Path]:
        """Percorre um diretório recursivamente, retornando caminhos de arquivos."""
        ...

    def read_file_chunks(self, path: Path, chunk_size: int = 65536) -> Iterator[bytes]:
        """Lê um arquivo em pedaços (chunks)."""
        ...

    def delete_file_safely(self, path: Path) -> None:
        """Remove um arquivo de forma segura (ex: para a lixeira)."""
        ...

    def move_file(self, source: Path, destination: Path) -> None:
        """Move um arquivo."""
        ...

    def copy_file(self, source: Path, destination: Path) -> None:
        """Copia um arquivo."""
        ...

    def create_directory(self, path: Path, parents: bool = True, exist_ok: bool = True) -> None:
        """Cria um diretório."""
        ...

    def get_creation_time(self, path: Path) -> float:
        """Retorna o timestamp de criação do arquivo."""
        ...
    
    def get_modification_time(self, path: Path) -> float:
        """Retorna o timestamp da última modificação do arquivo."""
        ...

class IZipService(Protocol):
    """Interface para manipulação de arquivos ZIP."""

    def list_zip_entries(self, zip_path: Path) -> Iterator[Tuple[str, int]]: # (entry_name, entry_size)
        """Lista entradas de um arquivo ZIP sem extrair tudo."""
        ...

    def stream_zip_entry_chunks(self, zip_path: Path, entry_name: str, chunk_size: int = 65536) -> Iterator[bytes]:
        """Lê uma entrada específica de um arquivo ZIP em pedaços (chunks)."""
        ...

class IHashingService(Protocol):
    """Interface para cálculo de hashes."""

    def create_hasher(self) -> Any: # Retorna um objeto hasher (ex: blake3.blake3())
        """Cria uma nova instância de um objeto hasher."""
        ...

    def update_hasher(self, hasher: Any, data: bytes) -> None:
        """Atualiza o hasher com novos dados."""
        ...

    def finalize_hash(self, hasher: Any) -> str:
        """Finaliza o cálculo e retorna o hash como string hexadecimal."""
        ...

    def calculate_hash_for_stream(self, stream: Iterator[bytes]) -> str:
        """Calcula o hash para um stream de bytes."""
        hasher = self.create_hasher()
        for chunk in stream:
            self.update_hasher(hasher, chunk)
        return self.finalize_hash(hasher)


class IConcurrencyService(Protocol):
    """Interface para execução de tarefas concorrentes/paralelas."""

    def run_tasks_in_parallel(self, tasks: List[Callable[[], Any]], max_workers: Optional[int] = None) -> List[Any]:
        """Executa uma lista de callables em paralelo e retorna os resultados."""
        ...
    
    # Poderia ter um método submit para tarefas individuais também, se necessário.
    # def submit_task(self, func: Callable[..., Any], *args, **kwargs) -> Future: ...


class IBackupService(Protocol):
    """Interface para operações de backup e restauração."""

    def initialize_backup_location(self, base_path: Path) -> None:
        """Configura o diretório base para backups."""
        ...

    def backup_file(self, file_path: Path) -> BackupManifestEntry:
        """Cria um backup do arquivo e retorna informações sobre o backup."""
        ...

    def list_backup_entries(self) -> List[BackupManifestEntry]:
        """Lista todas as entradas de backup disponíveis."""
        ...

    def restore_file(self, backup_entry: BackupManifestEntry, restore_to_original: bool = True, custom_destination: Optional[Path] = None) -> Path:
        """Restaura um arquivo a partir de uma entrada de backup."""
        ...

    def get_backup_metadata_path(self) -> Path:
        """Retorna o caminho para o arquivo de metadados do backup."""
        ...

class ILoggingService(Protocol):
    """Interface para logging."""
    
    def setup_logging(self, log_file_path: Path, level: int) -> None:
        ...

    def info(self, message: str) -> None:
        ...

    def warning(self, message: str) -> None:
        ...

    def error(self, message: str, exc_info: bool = False) -> None:
        ...

    def debug(self, message: str) -> None:
        ...

# --- Interfaces de Comunicação UI <-> Application (Signals/Slots ou Callbacks) ---
# Em PySide6, isso é naturalmente tratado com Signals e Slots.
# A UI se conectaria a sinais emitidos pelos Application Services.
# Exemplo de sinal que um Application Service poderia emitir:
# class ScanProgressSignal(QObject): # PySide6 QObject
#     progress_updated = Signal(int, str) # percent, message
#     scan_completed = Signal(list) # list of DuplicateGroup
#     error_occurred = Signal(str)
```

### 5. Gerenciamento de Dados

*   **Dados de Arquivos (temporários durante o escaneamento):** Serão mantidos em memória usando os `FileItem` e `DuplicateGroup` (definidos em `fotix.domain.models`). Para grandes volumes, a estratégia de "batching progressivo" é chave:
    1.  Listar arquivos (metadados básicos: caminho, tamanho).
    2.  Pré-filtrar por tamanho para identificar candidatos potenciais a duplicatas.
    3.  Processar em lotes (batches) os grupos de arquivos com mesmo tamanho:
        *   Calcular hashes para esses arquivos (paralelamente).
        *   Identificar duplicatas exatas dentro do lote.
    4.  Liberar da memória arquivos que não são duplicatas ou que já foram processados.
*   **Backup de Arquivos Removidos:**
    *   Os arquivos removidos serão movidos para um diretório de backup específico (ex: `AppData/Fotix/Backups/YYYYMMDD_HHMMSS/<hash_original_do_arquivo>/nome_original.ext`).
    *   O `BackupServiceImpl` manterá um arquivo de manifesto (ex: `backup_manifest.json` ou `backup_manifest.sqlite`) nesse diretório, registrando:
        *   Caminho original do arquivo.
        *   Caminho do arquivo no backup.
        *   Timestamp do backup.
        *   Hash do arquivo (para verificação).
        *   Outros metadados relevantes.
    *   Este manifesto será usado pelo `RestoreOrchestratorService` e `RestoreView`.
*   **Logs da Aplicação:**
    *   Gerenciados pelo `LoggingServiceImpl`, gravados em arquivos de texto em um diretório específico (ex: `AppData/Fotix/Logs/fotix_YYYY-MM-DD.log`).
*   **Relatórios:**
    *   Gerados pelo `FileOperationService` após a remoção, possivelmente em formato CSV ou TXT simples, resumindo as ações tomadas.

### 6. Estrutura de Diretórios Proposta (Layout `src`)

```
fotix_project/
├── src/
│   └── fotix/
│       ├── __init__.py
│       ├── main.py                 # Ponto de entrada: QApplication, inicializa MainWindow e serviços
│       │
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── main_window.py
│       │   ├── views/
│       │   │   ├── __init__.py
│       │   │   ├── config_view.py
│       │   │   ├── progress_view.py
│       │   │   ├── results_view.py
│       │   │   └── restore_view.py
│       │   └── widgets/              # Componentes de UI reutilizáveis (ex: FileBrowserWidget)
│       │       └── __init__.py
│       │
│       ├── application_services/
│       │   ├── __init__.py
│       │   ├── scan_orchestrator.py
│       │   ├── file_operation_service.py
│       │   └── restore_orchestrator.py
│       │
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── models.py             # Dataclasses/Pydantic: FileItem, DuplicateGroup, etc.
│       │   ├── duplicate_finder.py
│       │   └── selection_strategy.py
│       │
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   ├── interfaces.py         # Definição das IService (IFileSystemService, etc.)
│       │   ├── file_system_service.py # FileSystemServiceImpl
│       │   ├── zip_service.py         # ZipServiceImpl
│       │   ├── hashing_service.py     # HashingServiceImpl
│       │   ├── concurrency_service.py # ConcurrencyServiceImpl
│       │   ├── backup_service.py      # BackupServiceImpl
│       │   └── logging_service.py     # LoggingServiceImpl
│       │
│       └── utils/
│           ├── __init__.py
│           └── helpers.py            # Funções utilitárias gerais
│
├── tests/                          # Testes unitários e de integração
│   ├── __init__.py
│   ├── unit/
│   │   ├── ui/
│   │   ├── application_services/
│   │   ├── domain/
│   │   └── infrastructure/
│   └── integration/
│
├── data/                           # Dados gerados pelo usuário/aplicação (NÃO versionados)
│   ├── backups/                    # Diretório de backup dos arquivos removidos
│   └── logs/                       # Logs da aplicação
│
├── resources/                      # Ícones, etc. (se houver)
│
├── pyproject.toml                  # Configuração do projeto e dependências (PEP 517/518)
├── setup.cfg                       # Configurações de build/linters (opcional com pyproject.toml)
├── README.md
└── .gitignore
```

### 7. Considerações de Segurança

1.  **Remoção Segura:** Uso de `send2trash` (ou equivalente no Windows) via `IFileSystemService` para mover arquivos para a lixeira em vez de exclusão permanente, permitindo recuperação fácil pelo usuário fora do app, se necessário. O backup interno do Fotix é a camada primária de segurança.
2.  **Validação de Entradas:**
    *   Caminhos de diretórios fornecidos pela UI devem ser validados (existência, permissões de leitura) antes de iniciar o escaneamento.
    *   Isso será feito na Camada de Aplicação (`ScanOrchestratorService`) usando o `IFileSystemService`.
3.  **Operações de Arquivo Críticas:**
    *   Todas as operações de escrita/deleção (backup, remoção, restauração) devem ter tratamento de erro robusto (ex: `try-except` para `IOError`, `PermissionError`) e logar falhas. O `IFileSystemService` e `IBackupService` são responsáveis por isso.
4.  **Backup:** O sistema de backup automático é uma medida de segurança fundamental contra remoção acidental.
5.  **Sem Dados Sensíveis:** O aplicativo lida principalmente com metadados de arquivos e os próprios arquivos. Não há gerenciamento de senhas ou dados pessoais sensíveis além dos nomes dos arquivos e seus conteúdos.
6.  **Integridade do Backup:** O `BackupServiceImpl` pode opcionalmente verificar o hash do arquivo após a cópia para o diretório de backup para garantir a integridade da cópia.

### 8. Justificativas e Trade-offs

*   **Arquitetura em Camadas vs. Mais Simples:** Para um projeto com a complexidade funcional descrita (async, GUI responsiva, lógica de decisão, backup), uma arquitetura mais simples (ex: tudo em poucos arquivos) rapidamente se tornaria difícil de manter e testar. O overhead inicial da arquitetura em camadas compensa a longo prazo.
*   **Interfaces Explícitas (Protocolos):** Adicionam um pouco de verbosidade, mas são cruciais para:
    *   **Desacoplamento:** Permite que as camadas superiores dependam de abstrações.
    *   **Testabilidade:** Facilita o mocking/stubbing das dependências de infraestrutura.
    *   **Clareza:** Documentam explicitamente os contratos entre componentes.
*   **Injeção de Dependência:** Embora não explicitamente detalhado como um framework de DI será usado, a arquitetura é projetada para suportá-la. As implementações dos serviços de infraestrutura (ex: `FileSystemServiceImpl`) seriam instanciadas e injetadas nos serviços da camada de aplicação, que por sua vez são usados pela UI. Isso pode ser feito manualmente na inicialização da aplicação (`main.py`) ou com uma biblioteca de DI simples se o projeto crescer.
*   **`concurrent.futures` vs. `asyncio`:** `concurrent.futures` é mais simples para tarefas vinculadas à CPU (como hashing, com `ProcessPoolExecutor`) ou IO bloqueante (como algumas operações de arquivo, com `ThreadPoolExecutor`) em um contexto de aplicação desktop tradicional. `asyncio` seria uma alternativa, mas pode adicionar complexidade na integração com uma GUI síncrona como PySide6 e com bibliotecas que não são nativamente async. A stack definida já inclui `concurrent.futures`.
*   **`stream-unzip`:** Escolhido para descompactação otimizada de ZIPs grandes, evitando carregar todo o arquivo ZIP na memória. Isso se alinha com o requisito de baixo uso de memória.
*   **BLAKE3:** Escolhido por sua velocidade, sendo um algoritmo de hashing moderno e eficiente.
*   **Pydantic vs. Dataclasses para Modelos:** Pydantic oferece validação de dados em tempo de execução, o que é útil, mas dataclasses são mais leves. A escolha pode ser feita por `fotix.domain.models` com base na necessidade de validação estrita. Para esta proposta, dataclasses são suficientes, mas Pydantic é uma boa alternativa.
*   **Sem Banco de Dados Externo:** Conforme a restrição. O manifesto de backup (JSON/SQLite) é uma solução simples para persistência leve. Se os requisitos de consulta ao backup se tornarem complexos, um SQLite embutido seria o próximo passo lógico.