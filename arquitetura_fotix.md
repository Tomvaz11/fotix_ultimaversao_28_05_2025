# Arquitetura do Fotix

```
                                +-------------------+
                                |      fotix        |
                                | (Pacote Principal)|
                                +-------------------+
                                          |
                                          |
                +-------------------------+-------------------------+
                |                         |                         |
        +---------------+         +---------------+         +---------------+
        |     main.py   |         |   config.py   |         |   __init__.py |
        | (Ponto Entrada)|        | (Configurações)|        | (Metadados)   |
        +---------------+         +---------------+         +---------------+
                |
                |
+---------------+---------------+---------------+---------------+
|               |               |               |               |
|               |               |               |               |
v               v               v               v               v
+------------+ +------------+ +------------+ +------------+ +------------+
|     UI     | |  Application| |    Core    | |Infrastructure| |   Utils   |
|(Interface) | |  (Serviços) | | (Domínio)  | | (Infraest.)  | | (Utilitários)|
+------------+ +------------+ +------------+ +------------+ +------------+
      |               |               |               |               |
      |               |               |               |               |
      v               v               v               v               v
+------------+ +------------+ +------------+ +------------+ +------------+
|main_window | | services/  | |models.py   | |interfaces.py| |helpers.py |
|widgets/    | |            | |interfaces.py| |file_system.py| |image_utils.py|
|resources/  | |            | |duplicate_  | |zip_handler.py| |          |
|            | |            | |finder.py   | |concurrency.py| |          |
|            | |            | |selection_  | |backup.py     | |          |
|            | |            | |strategy.py | |logging_config.py|         |
+------------+ +------------+ +------------+ +------------+ +------------+
      |               |
      |               |
      v               v
+------------+ +------------+
|duplicate_  | |scan_service|
|list_widget | |duplicate_  |
|file_info_  | |management_ |
|widget      | |service     |
|progress_   | |backup_     |
|dialog      | |restore_    |
|settings_   | |service     |
|dialog      | |            |
+------------+ +------------+
```

## Descrição da Arquitetura

O Fotix segue uma arquitetura em camadas que separa claramente as responsabilidades:

### 1. Módulos Principais

- **main.py**: Ponto de entrada da aplicação, inicializa a UI e os serviços
- **config.py**: Gerencia as configurações da aplicação
- **__init__.py**: Define metadados do pacote e versão

### 2. Camadas Principais

#### UI (Interface do Usuário)
- **Responsabilidade**: Interface gráfica para interação com o usuário
- **Componentes**:
  - **main_window.py**: Janela principal da aplicação
  - **widgets/**: Componentes de UI reutilizáveis
  - **resources/**: Recursos como ícones

#### Application (Aplicação)
- **Responsabilidade**: Orquestração dos casos de uso e fluxos de trabalho
- **Componentes**:
  - **services/**: Implementação dos serviços de aplicação
    - **scan_service.py**: Serviço de varredura de diretórios
    - **duplicate_management_service.py**: Gerenciamento de duplicatas
    - **backup_restore_service.py**: Backup e restauração

#### Core (Domínio)
- **Responsabilidade**: Lógica de negócio central e independente
- **Componentes**:
  - **models.py**: Estruturas de dados do domínio (FileInfo, DuplicateSet)
  - **interfaces.py**: Interfaces para serviços do domínio
  - **duplicate_finder.py**: Algoritmo de detecção de duplicatas
  - **selection_strategy.py**: Estratégias para seleção de arquivos

#### Infrastructure (Infraestrutura)
- **Responsabilidade**: Interação com o mundo exterior e serviços técnicos
- **Componentes**:
  - **interfaces.py**: Interfaces para serviços de infraestrutura
  - **file_system.py**: Acesso ao sistema de arquivos
  - **zip_handler.py**: Manipulação de arquivos ZIP
  - **concurrency.py**: Serviços de concorrência
  - **backup.py**: Serviços de backup
  - **logging_config.py**: Configuração de logging

#### Utils (Utilitários)
- **Responsabilidade**: Funções auxiliares genéricas
- **Componentes**:
  - **helpers.py**: Funções auxiliares diversas
  - **image_utils.py**: Utilitários para manipulação de imagens

## Fluxo de Dependências

```
UI → Application → Core ← Infrastructure
                         ↑
                       Utils
```

- A camada UI depende da camada Application
- A camada Application depende da camada Core
- A camada Core define interfaces que são implementadas pela camada Infrastructure
- A camada Utils fornece funções auxiliares para todas as outras camadas

Esta arquitetura segue os princípios de Clean Architecture, onde as dependências apontam para dentro (em direção ao Core), e as camadas externas dependem das camadas internas, mas não o contrário.
