Ok, entendido. Assumirei o papel de **Tocrisna**, a arquiteta, e gerarei o Blueprint Arquitetural Detalhado para o projeto **Fotix**, seguindo rigorosamente as instruções e o contexto fornecido.

---

# Blueprint Arquitetural Detalhado - Projeto Fotix v1.0

**Arquiteta:** Tocrisna
**Data:** 24 de maio de 2024
**Versão:** 1.0

## 1. Visão Geral da Arquitetura

**Abordagem Escolhida:** Arquitetura **Modular Monolítica por Componentes**.

**Justificativa:**
Para um aplicativo desktop como o Fotix, uma arquitetura monolítica é apropriada, pois simplifica o desenvolvimento, o build e a distribuição (um único executável ou pacote de instalação). No entanto, para garantir manutenibilidade, testabilidade e escalabilidade do desenvolvimento (permitindo que diferentes partes sejam trabalhadas com menor acoplamento), adotaremos uma abordagem *modular* dentro do monólito.

Dividiremos a aplicação em componentes bem definidos, cada um com uma responsabilidade clara (SRP - Single Responsibility Principle). A comunicação entre esses componentes ocorrerá através de interfaces (contratos) explícitas, promovendo baixo acoplamento e alta coesão. Esta abordagem facilita:

*   **Desenvolvimento Paralelo:** Diferentes módulos podem ser desenvolvidos ou refatorados com menor impacto nos outros.
*   **Testabilidade:** Cada componente pode ser testado isoladamente (testes unitários) ou em conjunto com seus colaboradores diretos (testes de integração).
*   **Manutenibilidade:** A lógica de negócios fica encapsulada em módulos específicos, facilitando a compreensão e modificação.
*   **Reutilização:** Componentes bem definidos (como o motor de hashing ou o scanner) poderiam, teoricamente, ser reutilizados em outros contextos.

Esta abordagem se alinha diretamente aos princípios AGV de Modularidade, Baixo Acoplamento, Interfaces Explícitas e Clareza.

## 2. Diagrama de Componentes (Simplificado - Descrição Textual)

```
+--------------------------------------------------------------------------+
|                     Fotix Application (Monolith)                         |
+--------------------------------------------------------------------------+
|                                                                          |
|   +---------------------+      +-----------------------+      +---------+
|   |     GUI (PySide6)   |<---->|   Core Orchestrator   |<---->| Settings|
|   | (User Interface)    |      | (Workflow Management) |      | Manager |
|   +---------------------+      +-----------------------+      +---------+
|         ^                             |         ^                 ^
|         | (User Actions/              |         | (Config Data)   | (Config Data)
|         |  Display Updates)           |         |                 |
|         v                             v         v                 v
|   +---------------------+      +-----------------------+      +---------+
|   |      Logger         |<-----|      File Scanner     |      |  Utils  |
|   | (Logging/Reporting) |      | (Disk & ZIP Traversal)|      | (Common)|
|   +---------------------+      +-----------------------+      +---------+
|         ^                             |         ^                 ^
|         | (Log Events)                |         | (File Paths)    | (Helpers)
|         |                             v         v                 |
|   +---------------------+      +-----------------------+          |
|   |   Hashing Engine    |<-----|   Duplicate Analyzer  |          |
|   | (BLAKE3, Parallel)  |      | (Comparison & Logic)  |          |
|   +---------------------+      +-----------------------+          |
|         ^                             |         ^                 |
|         | (Hashes)                    |         | (Duplicate Sets)|
|         |                             v         v                 |
|   +---------------------+      +-----------------------+          |
|   | Backup/Restore Mgr  |<-----|   File Actions        |----------+
|   | (Manages Backups)   |      | (Remove, Restore Ops) |
|   +---------------------+      +-----------------------+
|         ^                             |
|         | (Backup Metadata)           | (FS Operations)
|         +-----------------------------+
|
+--------------------------------------------------------------------------+
|            File System (User Directories, ZIP Files, Backup Area)        |
+--------------------------------------------------------------------------+
```

**Fluxo Principal Simplificado:**

1.  **GUI** recebe a ação do usuário (ex: iniciar scan) e chama o **Core Orchestrator**.
2.  **Orchestrator** busca configurações no **Settings Manager**.
3.  **Orchestrator** instrui o **File Scanner** a encontrar arquivos nos locais e ZIPs especificados.
4.  **Scanner** percorre diretórios e usa `stream-unzip` para ZIPs, retornando/yieldando caminhos de arquivos para o **Orchestrator**. (Progresso é reportado via Orchestrator para a GUI).
5.  **Orchestrator** passa os arquivos (em lotes) para o **Hashing Engine**.
6.  **Hashing Engine** usa `os.path.getsize` para pré-filtragem e `BLAKE3` com `concurrent.futures` para calcular hashes em paralelo, retornando hashes para o **Orchestrator**. (Progresso reportado).
7.  **Orchestrator** envia os hashes e metadados associados ao **Duplicate Analyzer**.
8.  **Analyzer** compara hashes, identifica grupos de duplicatas e aplica a lógica de seleção para marcar quais remover. Retorna os resultados para o **Orchestrator**.
9.  **Orchestrator** apresenta os resultados (via callback/sinal) na **GUI** para revisão/confirmação do usuário (se aplicável, ou procede automaticamente).
10. **Orchestrator**, após confirmação, instrui o **File Actions** a remover os arquivos selecionados.
11. **File Actions** usa **Backup/Restore Mgr** para registrar o backup e `send2trash` para remover os arquivos.
12. **Backup/Restore Mgr** gerencia a área de backup.
13. **Orchestrator** atualiza a **GUI** com o status final e chama o **Logger** para registrar a operação e gerar relatórios.
14. O componente **Utils** fornece funções auxiliares (ex: formatação de tamanho, manipulação de paths) usadas por vários outros componentes.

## 3. Descrição dos Componentes/Módulos

| Componente              | Responsabilidade Principal                                                                                                | Tecnologias Chave                                           |
| :---------------------- | :------------------------------------------------------------------------------------------------------------------------ | :---------------------------------------------------------- |
| **`fotix.gui`**         | Interação com o usuário, apresentação de dados e progresso, captura de configurações de scan/remoção.                     | PySide6 (Qt for Python)                                     |
| **`fotix.core`**        | Orquestração do fluxo de trabalho principal (scan -> hash -> analyze -> remove/restore), coordenação entre componentes.    | Python (Lógica de controle)                                 |
| **`fotix.scanner`**     | Navegação eficiente em diretórios e extração progressiva de arquivos de ZIPs para identificar candidatos à análise.         | `pathlib`, `os.walk`, `stream-unzip`                        |
| **`fotix.hasher`**      | Cálculo de hashes de arquivos (com pré-filtragem por tamanho), otimizado para desempenho com processamento paralelo.      | `os.path.getsize`, `hashlib` (para BLAKE3), `concurrent.futures` |
| **`fotix.analyzer`**    | Comparação de hashes para identificar grupos de arquivos idênticos. Aplicação da lógica de seleção (critérios) para decidir qual manter/remover. | Python (Estruturas de dados: dicts, lists)                  |
| **`fotix.actions`**     | Execução segura de operações no sistema de arquivos: remoção para a lixeira, cópia para backup, restauração de arquivos.   | `send2trash`, `shutil`, `pathlib`                           |
| **`fotix.backup`**      | Gerenciamento da área de backup (metadados e arquivos), lógica para listar backups e obter informações para restauração.  | `pathlib`, `json` ou `csv` (para metadados)                  |
| **`fotix.settings`**    | Carregamento e salvamento das configurações da aplicação (ex: últimos diretórios escaneados, preferências do usuário).    | `pathlib`, `json` ou `configparser`                         |
| **`fotix.logger`**      | Registro de eventos importantes, erros e informações de depuração. Geração de relatórios resumidos pós-processamento.    | `logging` (módulo padrão Python)                            |
| **`fotix.utils`**       | Funções auxiliares e estruturas de dados comuns utilizadas por múltiplos componentes (ex: formatação, constantes).         | Python                                                      |
| **`fotix.models`** (Opcional) | Definição de estruturas de dados formais (ex: `dataclasses` ou Pydantic models) para `FileInfo`, `ScanResult`, etc., para clareza nas interfaces. | `dataclasses` ou `pydantic`                               |

## 4. Definição das Interfaces Principais (Contratos)

Esta é a parte mais crítica para garantir baixo acoplamento. As interfaces definem COMO os componentes interagem, sem expor detalhes internos. Usaremos *type hints* do Python para clareza.

*(Nota: Estas são assinaturas conceituais. A implementação exata pode usar sinais/slots do Qt, callbacks, async/await, ou geradores, dependendo da necessidade de comunicação síncrona/assíncrona e atualização da GUI.)*

**Estruturas de Dados Comuns (Exemplo - podem residir em `fotix.models`)**

```python
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import datetime

@dataclass
class FileInfo:
    path: Path
    size: int
    modified_time: float # from os.path.getmtime
    creation_time: float # from os.path.getctime
    resolution: Optional[Tuple[int, int]] = None # Para imagens/vídeos
    hash: Optional[str] = None
    is_in_zip: bool = False
    zip_path: Optional[Path] = None

@dataclass
class ScanConfig:
    directories_to_scan: List[Path]
    zip_files_to_scan: List[Path]
    include_subdirs: bool = True
    file_types: List[str] = ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.avi', '.mov'] # Exemplo

@dataclass
class DuplicateGroup:
    hash: str
    files: List[FileInfo]
    file_to_keep: Optional[FileInfo] = None
    files_to_remove: Optional[List[FileInfo]] = None

@dataclass
class ScanResult:
    total_files_scanned: int
    total_size_scanned: int
    duplicate_groups: List[DuplicateGroup]
    errors: List[Tuple[Path, str]] # Arquivos que falharam ao processar

@dataclass
class RemovalAction:
     files_to_remove: List[FileInfo] # Lista final aprovada

@dataclass
class RemovalResult:
    files_removed_count: int
    space_saved: int
    backup_id: str # Identificador do backup criado
    errors: List[Tuple[Path, str]]

@dataclass
class BackupInfo:
    backup_id: str
    timestamp: datetime.datetime
    original_files_count: int
    total_size: int
    manifest_path: Path # Path para o arquivo de metadados do backup

@dataclass
class RestoreResult:
    files_restored_count: int
    errors: List[Tuple[Path, str]]
```

**Interfaces Chave:**

*   **GUI -> Core Orchestrator:**
    *   `trigger_scan(config: ScanConfig)`
    *   `trigger_removal(action: RemovalAction)`
    *   `trigger_restore(backup_id: str)`
    *   `request_backup_list()`
    *   `request_settings()`
    *   `save_settings(settings_data: Dict)`
    *   `cancel_current_operation()`

*   **Core Orchestrator -> GUI (Callbacks/Sinais):**
    *   `update_progress(current_step: str, percentage: float, message: str)`
    *   `report_scan_results(result: ScanResult)`
    *   `report_removal_result(result: RemovalResult)`
    *   `report_restore_result(result: RestoreResult)`
    *   `report_backup_list(backups: List[BackupInfo])`
    *   `report_settings(settings_data: Dict)`
    *   `report_error(error_title: str, error_message: str)`

*   **Core Orchestrator <-> File Scanner:**
    *   `scan_files(config: ScanConfig) -> Iterable[FileInfo]` (Pode ser um gerador para processamento em streaming/lotes)
    *   (Scanner pode chamar `update_progress` no Orchestrator)

*   **Core Orchestrator <-> Hashing Engine:**
    *   `calculate_hashes(files_batch: List[FileInfo]) -> List[FileInfo]` (Retorna a lista com hashes preenchidos ou erros)
    *   (Hasher pode chamar `update_progress` no Orchestrator)

*   **Core Orchestrator <-> Duplicate Analyzer:**
    *   `find_and_select_duplicates(all_files: List[FileInfo]) -> List[DuplicateGroup]` (Retorna grupos com seleção feita)

*   **Core Orchestrator <-> File Actions:**
    *   `perform_removal(files_to_remove: List[FileInfo], backup_location: Path) -> Tuple[List[FileInfo], List[Tuple[Path, str]]]` (Retorna lista de arquivos removidos com sucesso e lista de erros)
    *   `perform_restore(files_to_restore: List[FileInfo], target_base_path: Path) -> Tuple[List[FileInfo], List[Tuple[Path, str]]]` (Retorna lista de arquivos restaurados e lista de erros)

*   **Core Orchestrator <-> Backup/Restore Manager:**
    *   `create_backup(removed_files: List[FileInfo]) -> BackupInfo`
    *   `get_backup_list() -> List[BackupInfo]`
    *   `get_files_for_restore(backup_id: str) -> List[FileInfo]`
    *   `get_backup_storage_path() -> Path`

*   **Core Orchestrator <-> Settings Manager:**
    *   `load_settings() -> Dict`
    *   `save_settings(settings_data: Dict)`

*   **Qualquer Componente -> Logger:**
    *   `log_info(message: str, component: str)`
    *   `log_warning(message: str, component: str)`
    *   `log_error(message: str, component: str, exc_info=None)`
    *   `generate_summary_report(result: Union[ScanResult, RemovalResult]) -> str`

## 5. Gerenciamento de Dados

*   **Dados Temporários/Em Memória:**
    *   Listas de `FileInfo` durante o scan e hashing.
    *   Dicionários mapeando hashes para listas de `FileInfo` durante a análise.
    *   Estruturas `ScanResult`, `DuplicateGroup`, etc.
    *   *Consideração:* Para volumes *extremamente* grandes (muito além de 100k arquivos, dependendo da RAM), pode ser necessário otimizar o uso de memória, processando arquivos em lotes menores ou usando estruturas de dados mais eficientes em memória (ou até mesmo armazenamento temporário em disco, embora adicione complexidade). A abordagem inicial será manter em memória, otimizando conforme necessário.
*   **Configurações da Aplicação:**
    *   Armazenadas em um arquivo de configuração (ex: `config.json` ou `settings.ini`) em um local padrão do sistema operacional para dados de aplicativos do usuário (ex: `%APPDATA%\Fotix` no Windows). O `Settings Manager` encapsula essa lógica.
*   **Dados de Backup:**
    *   Arquivos removidos serão copiados para um diretório de backup dedicado (configurável, com um padrão seguro).
    *   Uma estrutura de subdiretórios por backup (usando `backup_id` ou timestamp) será usada.
    *   Um arquivo de manifesto (ex: `manifest.json`) em cada subdiretório de backup armazenará os metadados dos arquivos removidos (caminho original, hash, tamanho, data da remoção, etc.), essencial para a restauração. O `Backup/Restore Manager` gerencia isso.
*   **Logs:**
    *   Arquivos de log de texto plano (`fotix.log`) armazenados em um local padrão para logs de aplicativos ou junto às configurações. O `Logger` gerencia a rotação e o nível de log.

## 6. Estrutura de Diretórios Proposta

```
fotix/
├── fotix/                  # Pacote principal da aplicação
│   ├── __init__.py
│   ├── main.py             # Ponto de entrada, inicializa GUI e Core
│   ├── gui/                # Componentes PySide6 UI (Views, Widgets)
│   │   ├── __init__.py
│   │   ├── main_window.py  # Janela principal
│   │   └── ...             # Outros dialogs, widgets
│   ├── core/               # Lógica central e orquestração
│   │   ├── __init__.py
│   │   └── orchestrator.py # Gerenciador de fluxo
│   ├── scanner/            # Lógica de escaneamento de arquivos/ZIP
│   │   ├── __init__.py
│   │   └── file_scanner.py
│   ├── hasher/             # Lógica de cálculo de hash
│   │   ├── __init__.py
│   │   └── file_hasher.py  # Implementação com BLAKE3/Parallel
│   ├── analyzer/           # Lógica de análise de duplicatas e seleção
│   │   ├── __init__.py
│   │   └── duplicate_analyzer.py
│   ├── actions/            # Operações de arquivo (remoção, restauração)
│   │   ├── __init__.py
│   │   └── file_actions.py
│   ├── backup/             # Gerenciamento de backup/restauração
│   │   ├── __init__.py
│   │   └── backup_manager.py
│   ├── settings/           # Gerenciamento de configuração
│   │   ├── __init__.py
│   │   └── settings_manager.py
│   ├── logger/             # Configuração e interface de logging
│   │   ├── __init__.py
│   │   └── logger_setup.py
│   ├── utils/              # Utilitários compartilhados
│   │   ├── __init__.py
│   │   └── helpers.py
│   └── models/             # (Opcional) Definições de dataclasses/estruturas
│       ├── __init__.py
│       └── data_models.py
├── tests/                  # Testes unitários e de integração
│   ├── test_scanner.py
│   ├── test_hasher.py
│   ├── ...
├── docs/                   # Documentação (incluindo este blueprint)
│   └── architecture.md
├── resources/              # Ícones, arquivos de UI (.ui), etc.
│   └── icons/
├── requirements.txt        # Dependências Python
├── setup.py                # (Ou pyproject.toml) Script de build/instalação
└── README.md
```

## 7. Considerações de Segurança

*   **Operações de Arquivo:**
    *   Usar `send2trash` para remoção oferece uma camada de segurança ao mover para a lixeira do sistema em vez de exclusão permanente direta.
    *   O backup automático antes da remoção é uma medida de segurança fundamental contra perda de dados acidental.
    *   O aplicativo deve solicitar confirmação explícita do usuário antes de realizar operações destrutivas (remoção).
*   **Acesso ao Sistema de Arquivos:**
    *   O aplicativo só deve solicitar/exigir as permissões estritamente necessárias para ler os diretórios/arquivos a serem escaneados e para escrever/excluir na área de backup e nos locais dos arquivos a serem removidos. Evitar operações com privilégios elevados, se possível.
*   **Tratamento de Erros:**
    *   Implementar tratamento robusto de exceções para operações de I/O (arquivo não encontrado, permissão negada, disco cheio durante backup/restore). Informar o usuário claramente sobre falhas sem travar a aplicação.
*   **Manipulação de Caminhos:**
    *   Validar e normalizar caminhos fornecidos pelo usuário ou lidos de configurações para evitar problemas de segurança relacionados a path traversal (embora menos crítico em um app desktop local, é boa prática). Usar `pathlib` ajuda nisso.
*   **Dependências:**
    *   Manter as dependências (PySide6, stream-unzip, etc.) atualizadas para mitigar vulnerabilidades conhecidas.

## 8. Justificativas e Trade-offs

*   **Modular Monolith vs Microservices:** Escolhido Monolith por simplicidade de deploy para desktop. A modularidade interna mitiga os problemas de manutenibilidade de um monólito tradicional. *Trade-off:* Menor escalabilidade independente de componentes comparado a microserviços (irrelevante para este caso de uso).
*   **Interfaces Explícitas:** Essencial para baixo acoplamento e testabilidade. *Trade-off:* Exige disciplina na definição e manutenção dos contratos entre componentes.
*   **Processamento Paralelo (`concurrent.futures`):** Necessário para desempenho em tarefas I/O-bound (leitura) e CPU-bound (hashing). *Trade-off:* Adiciona complexidade no gerenciamento de threads/processos e na sincronização/agregação de resultados. Requer cuidado para não sobrecarregar o sistema (limitar número de workers).
*   **`stream-unzip`:** Fundamental para o requisito de baixo uso de memória com ZIPs grandes. *Trade-off:* Pode ser ligeiramente mais lento que descompactar tudo de uma vez para ZIPs *pequenos*, mas o benefício em arquivos grandes compensa.
*   **`send2trash`:** Segurança aprimorada (lixeira do sistema). *Trade-off:* Depende da funcionalidade da lixeira do SO e pode falhar em alguns ambientes ou configurações específicas; requer fallback ou tratamento de erro claro.
*   **Gerenciamento de Dados em Memória:** Simplicidade inicial. *Trade-off:* Potencial gargalo de memória para datasets *extremamente* grandes. Pode exigir otimizações futuras (batching mais agressivo, estruturas de dados eficientes, ou uso de temp files/DBs leves como SQLite se a memória se tornar um fator limitante crítico).
*   **Identificação por Hash (Idênticos):** Simples e rápido (BLAKE3). *Trade-off:* Não detecta duplicatas *visualmente similares* mas não idênticas (ex: diferentes formatos, resoluções, edições leves), conforme definido nas restrições.

---

Este blueprint fornece a base para o desenvolvimento do Fotix, focando em uma estrutura organizada, manutenível e alinhada aos requisitos e restrições iniciais. As interfaces definidas serão cruciais para guiar a implementação e integração dos componentes.