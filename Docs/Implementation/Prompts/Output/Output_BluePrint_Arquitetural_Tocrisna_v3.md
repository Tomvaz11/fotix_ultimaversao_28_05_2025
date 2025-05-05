# Fotix - Proposta de Arquitetura Técnica v1.0

## 1. Visão Geral da Arquitetura

A arquitetura proposta para o Fotix é uma **Arquitetura em Camadas (Layered Architecture)**. Esta abordagem foi escolhida por promover uma clara **Separação de Responsabilidades (SoC)**, alta **Coesão** dentro de cada camada e baixo **Acoplamento** entre elas. Isso facilita a manutenibilidade, testabilidade e evolução do sistema.

As camadas principais são:

1.  **Camada de Apresentação (UI):** Responsável pela interação com o usuário. Construída com PySide6.
2.  **Camada de Aplicação:** Orquestra os casos de uso, coordena as tarefas e atua como intermediária entre a UI e o Core/Infraestrutura. Contém a lógica de fluxo do aplicativo.
3.  **Camada de Domínio (Core):** Contém a lógica de negócio central e pura do Fotix – identificação de duplicatas, estratégias de seleção, modelos de dados essenciais. É independente de UI e detalhes de infraestrutura.
4.  **Camada de Infraestrutura:** Lida com todas as interações externas: sistema de arquivos, concorrência/paralelismo, manipulação de ZIPs, backups e logging. Fornece abstrações (Interfaces/Serviços) para a camada de Aplicação e Core.

**Justificativa:** A arquitetura em camadas é um padrão bem estabelecido e adequado para aplicações desktop como o Fotix. Ela permite isolar a complexidade da lógica de negócio (Core) das especificidades da interface gráfica (UI) e das interações com o sistema operacional (Infraestrutura), tornando o código mais organizado e testável. A definição explícita de interfaces entre as camadas, especialmente para a infraestrutura, garante a flexibilidade e a possibilidade de substituir implementações no futuro (ex: suportar outros formatos de arquivo compacto, mudar a estratégia de backup).

## 2. Diagrama de Componentes (Simplificado)

```
+-----------------------------------------------------+
|             Apresentação (fotix.ui)                 |
|        (PySide6 - Widgets, Views, Signals)          |
+-----------------------^-----------------------------+
                        | (Calls Application Services)
                        v
+-----------------------------------------------------+
|           Aplicação (fotix.application)             |
|      (Orquestração, Use Cases, Services)            |
|      - ScanService                                  |
|      - DuplicateManagementService                   |
|      - BackupRestoreService                         |
+-----------------------^--------^--------------------+
                        |        |(Uses Core Logic)
         (Uses Infrastructure Services) |
                        v        v
+------------------------+      +-----------------------+
|   Domínio (fotix.core) |      | Infra (fotix.infra)   |
| (Models, DupFinder,    |      | (Abstractions & Impl) |
|  SelectionStrategy)    |      | - FileSystemService   |
+------------------------+      | - ConcurrencyService  |
                                | - BackupService       |
                                | - ZipHandlerService   |
                                | - LoggingConfig       |
                                +-------^---------------+
                                        | (Interacts with OS, Libs)
                                        v
+-----------------------------------------------------+
|      Sistema Operacional / Bibliotecas Externas     |
| (Python Libs: pathlib, shutil, send2trash, BLAKE3,  |
|  concurrent.futures, stream-unzip, logging)         |
+-----------------------------------------------------+
```

*Legenda:* Setas indicam a direção principal das dependências (quem utiliza quem).

## 3. Descrição dos Componentes/Módulos

**3.1. `fotix.ui` (Camada de Apresentação)**

*   **Responsabilidade:** Interface gráfica do usuário (GUI). Exibir informações, capturar entradas do usuário (seleção de diretórios, configurações, confirmação de remoção), exibir progresso e resultados. Interage com a camada de Aplicação via chamadas de serviço e recebe atualizações via sinais/callbacks.
*   **Tecnologias:** PySide6.
*   **Dependências Diretas:** `fotix.application.interfaces`, `fotix.core.models` (para exibir dados).

**3.2. `fotix.application` (Camada de Aplicação)**

*   **Responsabilidade:** Orquestrar os fluxos de trabalho (casos de uso). Inicia a varredura, coordena a análise de duplicatas, aplica a seleção, gerencia a remoção/backup e a restauração. Utiliza serviços da camada de Infraestrutura para tarefas como acesso a arquivos e execução paralela. Traduz ações da UI em operações do Core e da Infraestrutura. Contém a lógica de *como* as funcionalidades são executadas em sequência e em paralelo/assíncrono.
*   **Tecnologias:** Python.
*   **Subcomponentes (Exemplos):**
    *   `ScanService`: Gerencia o processo de varredura de diretórios e ZIPs, utilizando `ConcurrencyService`, `FileSystemService` e `ZipHandlerService`. Chama o `DuplicateFinderService`.
    *   `DuplicateManagementService`: Gerencia a seleção do arquivo a ser mantido (usando `SelectionStrategy` do Core), a remoção segura (usando `FileSystemService`) e o backup (usando `BackupService`).
    *   `BackupRestoreService`: Gerencia a listagem e restauração de backups (usando `BackupService` e `FileSystemService`).
*   **Dependências Diretas:** `fotix.core.interfaces`, `fotix.core.models`, `fotix.infrastructure.interfaces`, `fotix.config`.

**3.3. `fotix.core` (Camada de Domínio)**

*   **Responsabilidade:** Lógica de negócio central e independente. Contém os modelos de dados principais, o algoritmo de detecção de duplicatas (hashing, comparação) e as estratégias para selecionar qual arquivo manter. Deve ser totalmente testável sem depender da UI ou da infraestrutura concreta.
*   **Tecnologias:** Python, BLAKE3 (via wrapper).
*   **Subcomponentes (Exemplos):**
    *   `models`: Define as estruturas de dados (`FileInfo`, `DuplicateSet`, etc.) usando `dataclasses` ou `Pydantic`.
    *   `duplicate_finder`: Implementa a lógica de hashing (BLAKE3) e comparação, utilizando abstrações de acesso a arquivos (`FileSystemService`, `ZipHandlerService` via interfaces). Inclui a otimização de pré-filtragem por tamanho.
    *   `selection_strategy`: Implementa a lógica para escolher o arquivo a ser mantido com base nos critérios definidos (resolução, data, nome). Aplica o padrão Strategy.
*   **Dependências Diretas:** `fotix.core.models` (interno), `fotix.infrastructure.interfaces` (para abstrações de IO), `fotix.utils`.

**3.4. `fotix.infrastructure` (Camada de Infraestrutura)**

*   **Responsabilidade:** Interação com o mundo exterior e fornecimento de serviços técnicos genéricos como abstrações. Contém os *wrappers* para bibliotecas de baixo nível, garantindo que as camadas superiores dependam de interfaces estáveis e não de implementações concretas.
*   **Tecnologias:** Python, `pathlib`, `shutil`, `send2trash`, `concurrent.futures`, `stream-unzip`, `logging`.
*   **Subcomponentes (Exemplos + Interfaces):**
    *   `interfaces`: Define as interfaces (contratos) para os serviços desta camada (ex: `IFileSystemService`, `IConcurrencyService`, `IBackupService`, `IZipHandlerService`).
    *   `file_system`: Implementa `IFileSystemService` usando `pathlib`, `shutil`, `os.path.getsize`, `send2trash`.
    *   `concurrency`: Implementa `IConcurrencyService` usando `concurrent.futures`.
    *   `backup`: Implementa `IBackupService`, gerenciando a cópia de arquivos para uma área segura e a restauração. Pode usar `shutil` e armazenar metadados (ex: em JSON).
    *   `zip_handler`: Implementa `IZipHandlerService` usando `stream-unzip`.
    *   `logging_config`: Configura o sistema de logging padrão do Python.
*   **Dependências Diretas:** Depende das bibliotecas externas mencionadas. `fotix.core.models` (pode precisar de `FileInfo` para algumas operações), `fotix.utils`.

**3.5. `fotix.utils`**

*   **Responsabilidade:** Funções auxiliares, constantes e utilitários genéricos usados em múltiplas camadas.
*   **Tecnologias:** Python.
*   **Dependências Diretas:** Nenhuma dependência interna de outros módulos `fotix` (idealmente).

**3.6. `fotix.config`**

*   **Responsabilidade:** Carregar e fornecer acesso a configurações da aplicação (ex: caminho do backup, níveis de log, talvez limites de processamento).
*   **Tecnologias:** Python (pode usar `configparser`, `json`, `yaml` ou simples variáveis).
*   **Dependências Diretas:** Nenhuma dependência interna de outros módulos `fotix`.

## 4. Definição das Interfaces Principais (Contratos)

Aqui estão exemplos das interfaces chave (localizadas em `fotix.infrastructure.interfaces` e `fotix.core.interfaces`), focando nos wrappers de infraestrutura e na interação Core-Aplicação:

**4.1. `fotix.infrastructure.interfaces.IFileSystemService`**

*   **Propósito:** Abstrair operações no sistema de arquivos.
*   **Assinaturas Chave:**
    *   `get_file_size(path: Path) -> int | None:` Retorna o tamanho do arquivo ou None se não existir/acessível.
    *   `stream_file_content(path: Path, chunk_size: int = 65536) -> Iterable[bytes]:` Retorna um iterador/gerador para ler o conteúdo do arquivo em blocos. Lança exceções apropriadas (ex: `FileNotFoundError`, `PermissionError`).
    *   `list_directory_contents(path: Path, recursive: bool = True, file_extensions: list[str] | None = None) -> Iterable[Path]:` Retorna um iterador/gerador para os caminhos de arquivos (e opcionalmente diretórios) dentro de um diretório, com filtros opcionais.
    *   `move_to_trash(path: Path) -> None:` Move o arquivo/diretório para a lixeira do sistema. Lança exceção em caso de falha.
    *   `copy_file(source: Path, destination: Path) -> None:` Copia um arquivo.
    *   `create_directory(path: Path, exist_ok: bool = True) -> None:` Cria um diretório.
    *   `path_exists(path: Path) -> bool:` Verifica se um caminho existe.
    *   `get_creation_time(path: Path) -> float | None:` Retorna o timestamp de criação.
    *   `get_modification_time(path: Path) -> float | None:` Retorna o timestamp de modificação.
*   **Estruturas de Dados:** `pathlib.Path`.

**4.2. `fotix.infrastructure.interfaces.IZipHandlerService`**

*   **Propósito:** Abstrair a leitura de arquivos dentro de arquivos ZIP.
*   **Assinaturas Chave:**
    *   `stream_zip_entries(zip_path: Path, file_extensions: list[str] | None = None) -> Iterable[tuple[str, int, Callable[[], Iterable[bytes]]]]:` Retorna um iterador/gerador. Cada item é uma tupla contendo: (nome do arquivo dentro do zip, tamanho do arquivo, uma função *lazy* que retorna um iterador/gerador para o conteúdo do arquivo em blocos). Permite processamento streaming sem extrair tudo para o disco. Lança exceções apropriadas.
*   **Estruturas de Dados:** `pathlib.Path`, `typing.Callable`, `typing.Iterable`.

**4.3. `fotix.infrastructure.interfaces.IConcurrencyService`**

*   **Propósito:** Abstrair a execução de tarefas concorrentes/paralelas.
*   **Assinaturas Chave:**
    *   `run_parallel(tasks: Iterable[Callable[[], T]]) -> Iterable[T]:` Executa uma coleção de funções (tasks) em paralelo (usando `ThreadPoolExecutor` ou `ProcessPoolExecutor`) e retorna os resultados na ordem correspondente. Gerencia o pool de workers.
    *   `submit_background_task(task: Callable[..., R], *args, **kwargs) -> Future[R]:` Submete uma tarefa para execução em background e retorna um objeto `Future` (ou similar) para acompanhamento.
*   **Estruturas de Dados:** `typing.Callable`, `typing.Iterable`, `concurrent.futures.Future` (ou abstração similar).

**4.4. `fotix.infrastructure.interfaces.IBackupService`**

*   **Propósito:** Abstrair as operações de backup e restauração.
*   **Assinaturas Chave:**
    *   `create_backup(files_to_backup: Iterable[tuple[Path, FileInfo]]) -> str:` Cria um backup dos arquivos fornecidos (copiando-os para local seguro). Retorna um ID único para o backup realizado. Armazena metadados (nomes originais, hashes, etc.).
    *   `list_backups() -> list[dict[str, Any]]:` Retorna uma lista de informações sobre os backups disponíveis (ID, data, número de arquivos, etc.).
    *   `restore_backup(backup_id: str, target_directory: Path | None = None) -> None:` Restaura os arquivos de um backup específico para seus locais originais ou para um diretório alvo. Lança exceção se o backup ID for inválido ou ocorrer erro na restauração.
    *   `delete_backup(backup_id: str) -> None:` Remove um backup específico.
*   **Estruturas de Dados:** `pathlib.Path`, `fotix.core.models.FileInfo`.

**4.5. `fotix.core.interfaces.IDuplicateFinderService`** (Interface definida pelo Core, usada pela Aplicação)

*   **Propósito:** Define como encontrar conjuntos de arquivos duplicados.
*   **Assinaturas Chave:**
    *   `find_duplicates(scan_paths: list[Path], include_zips: bool, progress_callback: Callable[[float], None] | None = None) -> list[DuplicateSet]:` Analisa os caminhos fornecidos (diretórios e/ou ZIPs) e retorna uma lista de conjuntos de arquivos duplicados. Usa `IFileSystemService` e `IZipHandlerService` internamente (injetados). Pode aceitar um callback para reportar progresso.
*   **Estruturas de Dados:** `pathlib.Path`, `fotix.core.models.DuplicateSet`.

**4.6. `fotix.core.interfaces.ISelectionStrategy`** (Interface definida pelo Core, usada pela Aplicação via `DuplicateManagementService`)

*   **Propósito:** Define como selecionar o arquivo a ser mantido de um conjunto de duplicatas.
*   **Assinaturas Chave:**
    *   `select_file_to_keep(duplicate_set: DuplicateSet) -> FileInfo:` Recebe um conjunto de arquivos duplicados e retorna o `FileInfo` do arquivo que deve ser mantido com base nos critérios implementados (resolução, data, nome, etc.).
*   **Estruturas de Dados:** `fotix.core.models.DuplicateSet`, `fotix.core.models.FileInfo`.

## 5. Gerenciamento de Dados

*   **Dados de Aplicação (Estado Temporário):** Listas de arquivos, conjuntos de duplicatas, seleções do usuário serão mantidos em memória durante a execução, gerenciados principalmente pela Camada de Aplicação e representados pelos modelos em `fotix.core.models`.
*   **Persistência:**
    *   **Backups:** Os arquivos removidos serão copiados para um diretório de backup dedicado (configurável via `fotix.config`). Metadados sobre cada backup (ID, data, mapeamento de arquivos originais/backup) serão armazenados, possivelmente em arquivos JSON ou um banco de dados simples baseado em arquivo (ex: SQLite, gerenciado via `fotix.infrastructure.backup`), dentro do diretório de backup. A restrição "sem integração com bancos de dados *externos*" é mantida; um SQLite local para metadados de backup é considerado parte da gestão interna da aplicação.
    *   **Configurações:** Configurações do usuário (últimos diretórios escaneados, preferências) podem ser salvas em um arquivo de configuração (ex: INI, JSON) no diretório de dados do usuário.

## 6. Estrutura de Diretórios Proposta (`src` Layout)

```
fotix/
├── src/
│   └── fotix/
│       ├── __init__.py
│       ├── main.py             # Ponto de entrada da aplicação, inicializa UI e Application
│       │
│       ├── application/
│       │   ├── __init__.py
│       │   ├── services/         # Módulos para cada serviço (scan, manage, backup)
│       │   │   ├── __init__.py
│       │   │   ├── scan_service.py
│       │   │   ├── duplicate_management_service.py
│       │   │   └── backup_restore_service.py
│       │   └── interfaces.py     # Interfaces EXPOSTAS pela Application (se houver, para UI)
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── models.py         # Dataclasses/Pydantic para FileInfo, DuplicateSet, etc.
│       │   ├── duplicate_finder.py # Lógica principal de hashing e comparação
│       │   ├── selection_strategy.py # Implementações da estratégia de seleção
│       │   └── interfaces.py     # Interfaces DEFINIDAS pelo Core (IDuplicateFinder, ISelectionStrategy)
│       │
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   ├── interfaces.py     # Definição das interfaces (IFileSystemService, etc.) - CRUCIAL
│       │   ├── file_system.py    # Implementação de IFileSystemService
│       │   ├── concurrency.py    # Implementação de IConcurrencyService
│       │   ├── backup.py         # Implementação de IBackupService
│       │   ├── zip_handler.py    # Implementação de IZipHandlerService
│       │   └── logging_config.py # Configuração do logger
│       │
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── main_window.py    # Janela principal (PySide6)
│       │   ├── widgets/          # Widgets customizados da UI
│       │   │   └── ...
│       │   ├── resources/        # Ícones, etc. (.qrc)
│       │   └── view_models.py    # Opcional: Modelos de visão se usar MVVM
│       │
│       ├── utils/
│       │   ├── __init__.py
│       │   └── helpers.py        # Funções utilitárias
│       │
│       └── config.py             # Carregamento e acesso à configuração
│
├── tests/                      # Testes unitários e de integração
│   ├── __init__.py
│   ├── unit/
│   │   ├── application/
│   │   ├── core/
│   │   ├── infrastructure/
│   │   └── ui/
│   └── integration/
│       └── ...
│
├── pyproject.toml              # Definição do projeto e dependências (PEP 621)
├── README.md
├── LICENSE
└── ... (outros arquivos: docs, examples, etc.)
```

## 7. Considerações de Segurança

1.  **Operações de Arquivo:** Usar `send2trash` em vez de exclusão direta é fundamental para a recuperação. A camada de infraestrutura (`FileSystemService`, `BackupService`) deve implementar tratamento robusto de erros (ex: `PermissionError`, `FileNotFoundError`) para todas as operações de IO. As operações de escrita/remoção devem ser claramente confirmadas pelo usuário na UI.
2.  **Validação de Entrada:** Os caminhos fornecidos pelo usuário na UI devem ser validados minimamente (ex: verificar se existem, se são diretórios válidos) antes de serem passados para as camadas inferiores. Isso ocorre na camada de UI ou no início da camada de Aplicação.
3.  **Path Traversal:** Embora seja uma aplicação desktop local, sanitizar ou validar caminhos para evitar construção de caminhos inesperados é uma boa prática, especialmente ao lidar com nomes de arquivos dentro de ZIPs ou ao construir caminhos de backup/restauração. A biblioteca `pathlib` ajuda a mitigar alguns desses riscos.
4.  **Tratamento de Erros:** Captura e log detalhado de exceções em pontos críticos (IO, processamento paralelo, descompactação) para diagnóstico e para evitar término abrupto da aplicação.
5.  **Recursos:** Limitar o número de workers paralelos (em `ConcurrencyService`) para evitar sobrecarga do sistema do usuário. Monitorar uso de memória durante a descompactação e hashing (usar streaming sempre que possível).
6.  **Dependências:** Manter as dependências atualizadas para corrigir vulnerabilidades conhecidas.

## 8. Justificativas e Trade-offs

*   **Arquitetura em Camadas:**
    *   *Prós:* Excelente separação de responsabilidades, alta testabilidade (mocking de camadas/interfaces), manutenibilidade. Clara organização do código.
    *   *Contras:* Pode introduzir alguma sobrecarga/boilerplate (chamadas passando por múltiplas camadas). Requer disciplina para manter os limites das camadas.
*   **Interfaces Explícitas para Infraestrutura:**
    *   *Prós:* Desacopla o código de aplicação/core das implementações concretas de IO, concorrência, etc. Facilita testes (mocking fácil) e futuras mudanças (ex: suportar 7zip, usar async IO diferente). Imposto pela Diretriz 3.
    *   *Contras:* Adiciona um nível de indireção. Requer definição cuidadosa das interfaces.
*   **`src` Layout:**
    *   *Prós:* Padrão moderno para pacotes Python, evita problemas comuns de importação, separa claramente o código fonte dos arquivos de configuração/teste. Facilita o empacotamento.
    *   *Contras:* Pode ser ligeiramente menos familiar para desenvolvedores acostumados com layouts mais antigos.
*   **Tecnologias Escolhidas:** As tecnologias (`PySide6`, `BLAKE3`, `stream-unzip`, `concurrent.futures`, `send2trash`) foram selecionadas com base nos requisitos explícitos do projeto, visando desempenho, modernidade e segurança.
*   **Foco em Duplicatas Idênticas:** Simplifica o core, usando hashing. A alternativa (similaridade perceptual) adicionaria complexidade significativa (requer bibliotecas de processamento de imagem/vídeo, algoritmos diferentes).
*   **Processamento Paralelo vs. Assíncrono (asyncio):** `concurrent.futures` foi escolhido por ser mais adequado para tarefas *CPU-bound* (hashing) e *IO-bound* (leitura de arquivos) em paralelo, e talvez mais simples de integrar em uma aplicação desktop tradicional do que uma abordagem `asyncio` pura, especialmente considerando a integração com PySide6 e bibliotecas de IO síncronas. No entanto, `asyncio` poderia ser considerado para otimizar operações puramente de IO se a concorrência se tornar um gargalo complexo de gerenciar com threads/processos.