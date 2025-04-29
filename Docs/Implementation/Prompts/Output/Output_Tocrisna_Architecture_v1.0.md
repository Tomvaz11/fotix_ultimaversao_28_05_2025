# Proposta de Arquitetura Técnica: Fotix v1.0

**Documento Preparado Por:** Tocrisna (Agente Arquiteta de Software)
**Versão:** 1.0
**Data:** 2024-08-28

## 1. Visão Geral da Arquitetura

A arquitetura proposta para o `Fotix` é uma **Arquitetura em Camadas (Layered Architecture)** com forte separação de responsabilidades. Esta abordagem foi escolhida por sua clareza, manutenibilidade e testabilidade, adequadas para uma aplicação desktop com funcionalidades bem definidas.

As camadas principais são:

1.  **Camada de Apresentação (GUI):** Responsável pela interface com o usuário.
2.  **Camada de Aplicação (Serviços):** Orquestra os casos de uso, atuando como fachada para o núcleo.
3.  **Camada de Núcleo (Core/Domain):** Contém a lógica de negócio principal (identificação de duplicatas, regras de decisão).
4.  **Camada de Infraestrutura:** Lida com preocupações transversais como acesso ao sistema de arquivos, paralelismo, logging e persistência de backups.

**Justificativa:**
*   **Modularidade:** Separa claramente a interface do usuário, a lógica de negócio e o acesso a recursos externos (sistema de arquivos, etc.).
*   **Manutenibilidade:** Alterações na GUI não devem impactar o Core, e vice-versa. Novas fontes de arquivos (ex: outros formatos compactados no futuro) podem ser adicionadas na Infraestrutura sem afetar o Core.
*   **Testabilidade:** Cada camada pode ser testada isoladamente. O Core, sendo independente de UI e I/O direto, é altamente testável unitariamente. A Camada de Aplicação pode ser testada com mocks da Infraestrutura e do Core.
*   **Clareza:** Facilita o entendimento do fluxo de dados e responsabilidades.
*   **GUI Responsiva:** Permite que as operações intensivas (Core e Infraestrutura) rodem em threads/processos separados, mantendo a GUI (Apresentação) responsiva.

## 2. Diagrama de Componentes (Simplificado - Descrição Textual)

```
+-----------------------+      +--------------------------+      +---------------------+      +------------------------+
|   Apresentação (GUI)  |<---->|  Aplicação (Serviços)    |<---->|   Núcleo (Core)     |<---->| Infraestrutura         |
|-----------------------|      |--------------------------|      |---------------------|      |------------------------|
| - PySide6 (Views)     |      | - Orquestração Casos Uso |      | - Lógica Duplicatas |      | - FileSystemService    |
| - ViewModels (Qt)     |      | - Gerencia Estado Scan   |      | - Algoritmo Decisão |      | - ZipHandlingService   |
| - Interação Usuário   |      | - Fachada p/ GUI         |      | - Hashing (BLAKE3)  |      | - ConcurrencyManager   |
| - Signals/Slots       |----->| - Comunicação Async GUI <------| - Estruturas Dados  |      | - BackupRestoreService |
+-----------------------+      +--------------------------+      +---------------------+      | - LoggingService       |
                                                                                            | - (pathlib, shutil,    |
                                                                                            |  send2trash,           |
                                                                                            |  stream-unzip,         |
                                                                                            |  concurrent.futures)   |
                                                                                            +------------------------+
        ^                                                                                            ^
        |                                                                                            |
        +----------------------------------------- Utilidades (`utils`) -----------------------------+
                                             (Funções Comuns, Constantes, etc.)
```

**Fluxo Principal (Exemplo: Scan):**
GUI -> Aplicação (inicia scan) -> Infraestrutura (lista arquivos) -> Core (pré-filtra, hash) -> Infraestrutura (lê arquivos p/ hash) -> Core (compara hashes, agrupa) -> Aplicação (recebe resultados) -> GUI (exibe resultados)

## 3. Descrição dos Componentes/Módulos

1.  **`fotix.gui` (Apresentação)**
    *   **Responsabilidade:** Renderizar a interface gráfica, capturar entradas do usuário (seleção de diretórios, configurações), exibir o progresso e os resultados do escaneamento, permitir ações sobre os resultados (exclusão, restauração).
    *   **Tecnologias:** PySide6 (Qt for Python).
    *   **Interação:** Comunica-se *exclusivamente* com a camada `fotix.application` através de chamadas de método e recebe atualizações via Signals/Slots do Qt (ou um mecanismo similar de callback/fila) para manter a responsividade.

2.  **`fotix.application` (Aplicação/Serviços)**
    *   **Responsabilidade:** Orquestrar os fluxos de trabalho (casos de uso). Atua como uma fachada entre a GUI e o Core/Infraestrutura. Gerencia o estado geral da aplicação (ex: scan em andamento, resultados carregados). Inicia tarefas em background (usando `ConcurrencyManager` da Infraestrutura) e coordena a comunicação assíncrona de volta para a GUI (progresso, resultados, erros).
    *   **Tecnologias:** Python puro, `dataclasses`/`pydantic`.
    *   **Interação:** Chamado pela `gui`. Chama métodos do `core` para lógica de negócio e da `infrastructure` para operações de I/O, paralelismo e outras preocupações externas.

3.  **`fotix.core` (Núcleo/Domain)**
    *   **Responsabilidade:** Implementar a lógica central de identificação de duplicatas. Contém o algoritmo de hashing (usando BLAKE3), a lógica de comparação, a estratégia de pré-filtragem por tamanho, e o algoritmo de decisão para escolher qual arquivo manter. Define as estruturas de dados canônicas para representar arquivos, duplicatas e resultados. **Deve ser independente de UI e I/O direto.**
    *   **Tecnologias:** Python puro, BLAKE3 (via biblioteca), `dataclasses`/`pydantic`.
    *   **Interação:** Chamado pela `application`. Pode solicitar dados de arquivos (ex: stream de bytes para hashing) através de interfaces implementadas pela `infrastructure`, mas não acessa o sistema de arquivos diretamente.

4.  **`fotix.infrastructure` (Infraestrutura)**
    *   **Responsabilidade:** Lidar com todas as interações com o mundo exterior e preocupações transversais. Isso inclui:
        *   Acesso ao sistema de arquivos (listar diretórios, obter metadados, ler, mover, deletar arquivos).
        *   Manipulação de arquivos ZIP (leitura e extração otimizada).
        *   Gerenciamento de concorrência/paralelismo (pools de threads/processos).
        *   Operações de backup e restauração.
        *   Logging.
        *   (Opcional) Persistência de configuração.
    *   **Tecnologias:** `pathlib`, `shutil`, `os.path`, `send2trash`, `stream-unzip`, `concurrent.futures`, `logging`, Python puro.
    *   **Interação:** Chamado pela `application` para executar tarefas de I/O ou gerenciar concorrência. Implementa interfaces que podem ser usadas pelo `core` (ex: para obter dados de arquivos de forma abstrata).

5.  **`fotix.utils` (Utilidades)**
    *   **Responsabilidade:** Fornecer funções auxiliares, constantes, e talvez classes base ou decoradores usados por múltiplos módulos/camadas. Ex: formatação de tamanho de arquivo, setup inicial de logging.
    *   **Tecnologias:** Python puro.
    *   **Interação:** Usado por qualquer outra camada conforme necessário.

## 4. Definição das Interfaces Principais (Contratos entre Camadas)

Usaremos `dataclasses` ou `pydantic` para definir estruturas de dados claras.

**Estruturas de Dados Chave:**

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Iterator

@dataclass(frozen=True)
class FileMetadata:
    path: Path
    size: int
    creation_time: float # Timestamp UTC
    # Potencialmente outros metadados úteis para decisão (resolução, etc. - a serem extraídos seletivamente)
    # hash: Optional[str] = None # Preenchido durante o processamento

@dataclass
class ScanConfig:
    directories_to_scan: List[Path]
    include_zip_files: bool
    # Outras configurações (ex: filtros de extensão, tamanho mínimo/máximo)

@dataclass
class DuplicateGroup:
    files: List[FileMetadata] # Lista de arquivos idênticos
    file_to_keep: Optional[FileMetadata] = None # Decidido pelo Core
    hash_value: str # Hash que identifica o grupo

@dataclass
class ScanProgress:
    files_scanned: int
    duplicates_found: int
    current_phase: str # Ex: "Listing files", "Hashing", "Comparing"
    error_message: Optional[str] = None

@dataclass
class BackupInfo:
    original_path: Path
    backup_path: Path
    timestamp: float
```

**Interfaces (Assinaturas de Métodos Chave):**

*   **`fotix.application.ScanService` (Interface exposta para a `gui`)**
    *   `start_scan(config: ScanConfig) -> None`: Inicia um novo processo de scan em background. Dispara sinais/callbacks para progresso.
    *   `get_current_results() -> List[DuplicateGroup]`: Retorna os grupos de duplicatas encontrados até o momento (ou ao final).
    *   `process_deletions(groups: List[DuplicateGroup]) -> None`: Inicia o processo de backup e remoção dos arquivos marcados para exclusão (não os `file_to_keep`). Dispara sinais/callbacks para progresso/conclusão.
    *   `restore_from_backup(backup_info: BackupInfo) -> None`: Inicia a restauração de um arquivo.
    *   `get_backup_list() -> List[BackupInfo]`: Retorna a lista de backups disponíveis.
    *   *Sinais/Callbacks para GUI (Conceitual):* `progress_updated(progress: ScanProgress)`, `scan_completed(results: List[DuplicateGroup])`, `deletion_completed()`, `error_occurred(message: str)`

*   **`fotix.core.DuplicateFinder` (Interface usada pela `application`)**
    *   `find_duplicates(file_iterator: Iterator[FileMetadata], hash_function: callable) -> List[DuplicateGroup]`: Recebe um iterador de metadados de arquivos e uma função para obter o hash (fornecida via `infrastructure`), retorna os grupos de duplicatas. O processo interno envolve:
        1. Pré-filtragem por tamanho.
        2. Agrupamento por tamanho.
        3. Hashing (usando `hash_function`) apenas para grupos com mais de um arquivo.
        4. Comparação final por hash.
    *   `decide_file_to_keep(group: DuplicateGroup) -> FileMetadata`: Aplica as regras de negócio (resolução, data, nome) para selecionar o melhor arquivo dentro de um grupo de duplicatas.

*   **`fotix.infrastructure.FileSystemService` (Interface usada pela `application` e potencialmente pelo `core` via `application`)**
    *   `scan_directory_recursively(path: Path, include_zip: bool) -> Iterator[FileMetadata]`: Itera sobre arquivos em diretórios, retornando `FileMetadata` básico (sem hash). Delega a extração de ZIPs ao `ZipHandlingService`.
    *   `get_file_stream(path: Path) -> Iterator[bytes]`: Retorna um iterador/stream de bytes para um arquivo (usado para hashing pelo `core`).
    *   `move_file_to_trash(path: Path) -> None`: Move um arquivo para a lixeira do sistema de forma segura (usando `send2trash`).
    *   `get_file_metadata(path: Path) -> FileMetadata`: Obtém metadados detalhados de um arquivo (pode incluir extração de metadados de mídia se necessário para a decisão do `core`).

*   **`fotix.infrastructure.ZipHandlingService` (Interface usada pelo `FileSystemService`)**
    *   `stream_files_from_zip(zip_path: Path) -> Iterator[Tuple[str, Iterator[bytes], int]]`: Usa `stream-unzip` para iterar sobre os arquivos dentro de um ZIP, retornando o nome do arquivo interno, um iterador para seus bytes e seu tamanho, sem extrair tudo para o disco.

*   **`fotix.infrastructure.ConcurrencyManager` (Interface usada pela `application`)**
    *   `submit_cpu_bound_task(func: callable, *args, **kwargs) -> Future`: Submete uma tarefa intensiva em CPU (ex: hashing de múltiplos arquivos) para execução em um pool de processos (`ProcessPoolExecutor`).
    *   `submit_io_bound_task(func: callable, *args, **kwargs) -> Future`: Submete uma tarefa intensiva em I/O (ex: listar muitos arquivos, ler muitos arquivos pequenos) para execução em um pool de threads (`ThreadPoolExecutor`).

*   **`fotix.infrastructure.BackupRestoreService` (Interface usada pela `application`)**
    *   `backup_file(source_path: Path) -> BackupInfo`: Move o arquivo para um local de backup seguro e retorna informações sobre o backup.
    *   `restore_file(backup_info: BackupInfo) -> None`: Restaura um arquivo do backup para seu local original.
    *   `list_backups() -> List[BackupInfo]`: Lista os backups existentes.
    *   `purge_old_backups(days_threshold: int) -> None`: (Opcional) Remove backups antigos.

## 5. Gerenciamento de Dados

*   **Dados de Scan:** Mantidos em memória durante o processamento pela `application` e `core`, usando as `dataclasses` definidas. Os resultados finais são passados para a `gui`. Não há persistência dos resultados do scan entre sessões do aplicativo na v1.0.
*   **Backups:** Gerenciados pela `BackupRestoreService` na camada de `infrastructure`. Os arquivos removidos são movidos para um diretório de backup dedicado (configurável, ex: `AppData/Local/Fotix/Backup` ou similar), possivelmente com metadados adicionais (um pequeno arquivo de índice ou nomeando os backups de forma informativa).
*   **Logs:** Gerenciados pela `LoggingService` na `infrastructure`. Logs detalhados são escritos em arquivos (`AppData/Local/Fotix/Logs`), e relatórios resumidos podem ser gerados ao final do processo.
*   **Configuração:** Configurações simples (últimos diretórios usados, etc.) podem ser salvas em um arquivo de configuração (ex: INI, JSON) gerenciado pela `infrastructure`.

## 6. Estrutura de Diretórios Proposta

```
fotix/
├── src/
│   └── fotix/
│       ├── __init__.py
│       ├── main.py           # Ponto de entrada da aplicação
│       ├── gui/              # Camada de Apresentação (PySide6 Widgets, Views, ViewModels)
│       │   ├── __init__.py
│       │   ├── main_window.py
│       │   └── widgets/
│       ├── application/      # Camada de Aplicação (Serviços/Orquestração)
│       │   ├── __init__.py
│       │   └── scan_service.py
│       ├── core/             # Camada de Núcleo (Lógica de Negócio)
│       │   ├── __init__.py
│       │   ├── duplicate_finder.py
│       │   └── decision_logic.py
│       ├── infrastructure/   # Camada de Infraestrutura
│       │   ├── __init__.py
│       │   ├── file_system.py
│       │   ├── zip_handler.py
│       │   ├── concurrency.py
│       │   ├── backup.py
│       │   └── logging_setup.py
│       ├── domain/           # Estruturas de dados compartilhadas (Dataclasses/Pydantic) - Alternativa a colocá-las em 'core'
│       │   ├── __init__.py
│       │   └── models.py
│       └── utils/            # Utilidades
│           ├── __init__.py
│           └── helpers.py
├── tests/                  # Testes unitários e de integração
│   ├── __init__.py
│   ├── gui/
│   ├── application/
│   ├── core/
│   └── infrastructure/
├── data/                   # (Opcional) Dados de exemplo, recursos
├── docs/                   # Documentação
├── scripts/                # Scripts auxiliares (build, etc.)
├── requirements.txt        # Dependências
└── README.md
```

## 7. Considerações de Segurança

*   **Validação de Input:** A camada `gui` e `application` devem validar as entradas do usuário (ex: caminhos de diretório existem e são acessíveis).
*   **Operações de Arquivo Seguras:** Usar `send2trash` para exclusão minimiza o risco de perda acidental de dados. O sistema de backup é a principal salvaguarda.
*   **Tratamento de Erros:** Capturar exceções específicas de I/O (`FileNotFoundError`, `PermissionError`) na camada de `infrastructure` e reportá-las adequadamente para a `application` e `gui` para informar o usuário. Evitar falhas silenciosas em operações críticas (backup, delete).
*   **Permissões:** A aplicação rodará com as permissões do usuário logado. Garantir que o acesso a arquivos e diretórios respeite as permissões do sistema operacional.
*   **Hashing Seguro:** BLAKE3 é um algoritmo de hash criptográfico moderno e rápido, adequado para identificação de arquivos idênticos e resistente a colisões acidentais.
*   **Dados Sensíveis:** O aplicativo lida com caminhos de arquivo do usuário. Não há dados sensíveis adicionais (senhas, etc.) previstos. Logs devem evitar informações excessivamente detalhadas que possam ser sensíveis, se aplicável.

## 8. Justificativas e Trade-offs

*   **Arquitetura em Camadas vs. Outras:** Escolhida pela simplicidade e clareza para uma aplicação desktop. Microsserviços seriam excessivos. Uma arquitetura puramente baseada em eventos poderia adicionar complexidade na comunicação entre componentes para este escopo.
*   **`concurrent.futures`:** Oferece uma abstração de alto nível para paralelismo (threads para I/O, processos para CPU-bound como hashing BLAKE3), simplificando o gerenciamento em comparação com `threading` ou `multiprocessing` puros.
*   **`stream-unzip`:** Essencial para o requisito de lidar com grandes ZIPs com baixo uso de memória, processando arquivos um a um em vez de extrair tudo de uma vez.
*   **PySide6 (Qt):** Framework robusto e maduro para GUIs desktop, com bom suporte a multithreading (via `QThread` e signals/slots) que se integra bem com a necessidade de tarefas em background.
*   **BLAKE3:** Oferece excelente desempenho para hashing, crucial para a velocidade de identificação de duplicatas em grandes volumes.
*   **Separação `core` vs. `infrastructure`:** Garante que a lógica de negócio principal seja pura e testável, isolada dos detalhes de implementação de I/O, que podem mudar (ex: suportar outros formatos compactados no futuro).
*   **Interfaces Explícitas:** A definição clara das interfaces e estruturas de dados é crucial para o baixo acoplamento e facilita a evolução e os testes (mocking).
*   **Trade-off:** A comunicação assíncrona entre a camada de Aplicação/Infraestrutura (background threads/processes) e a GUI adiciona alguma complexidade (gerenciamento de signals/slots ou filas), mas é necessária para a responsividade da UI.

---

Esta proposta fornece um blueprint sólido para o desenvolvimento do `Fotix`, priorizando os requisitos funcionais e não funcionais definidos, com foco em uma estrutura manutenível e robusta.