# Arquitetura de Testes do Fotix

```
                                +-------------------+
                                |      tests        |
                                | (Pacote Principal)|
                                +-------------------+
                                          |
                                          |
                +-------------------------+-------------------------+
                |                                                   |
        +---------------+                                   +---------------+
        |     unit      |                                   |  integration  |
        | (Testes Unit.)|                                   | (Testes Integ.)|
        +---------------+                                   +---------------+
                |                                                   |
                |                                                   |
+---------------+---------------+---------------+     +-------------+-------------+-------------+-------------+
|               |               |               |     |             |             |             |             |
v               v               v               v     v             v             v             v             v
+------------+ +------------+ +------------+ +------------+ +------------+ +------------+ +------------+ +------------+
|   fotix    | |fotix.core  | |fotix.infra | |fotix.utils | |  fotix     | |fotix.core  | |fotix.app   | |fotix.infra |
|(Módulo Raiz)| |(Domínio)   | |(Infraest.) | |(Utilitários)| |(Módulo Raiz)| |(Domínio)   | |(Aplicação) | |(Infraest.) |
+------------+ +------------+ +------------+ +------------+ +------------+ +------------+ +------------+ +------------+
      |               |               |               |           |             |             |             |
      |               |               |               |           |             |             |             |
      v               v               v               v           v             v             v             v
+------------+ +------------+ +------------+ +------------+ +------------+ +------------+ +------------+ +------------+
|test_main.py| |test_models | |test_file_  | |test_helpers| |test_main_  | |test_complex| |test_scan_  | |test_infra_ |
|            | |test_duplic_| |system      | |test_image_ | |integration | |_scenarios  | |service     | |_base       |
|            | |_finder     | |test_zip_   | |utils       | |            | |test_compos_| |test_duplic_| |test_zip_   |
|            | |test_select_| |handler     | |            | |            | |_strategy   | |_management | |concurrency_|
|            | |_strategy   | |test_concur_| |            | |            | |            | |test_backup_| |backup      |
|            | |            | |test_backup | |            | |            | |            | |_restore    | |            |
+------------+ +------------+ +------------+ +------------+ +------------+ +------------+ +------------+ +------------+
                                                                                              |
                                                                                              |
                                                                                              v
                                                                                     +------------+
                                                                                     |test_app_   |
                                                                                     |services    |
                                                                                     |(Integração |
                                                                                     | entre      |
                                                                                     | serviços)  |
                                                                                     +------------+
```

## Descrição da Arquitetura de Testes

A estrutura de testes do Fotix segue uma organização que espelha a estrutura do código fonte, dividida em duas categorias principais: testes unitários e testes de integração.

### 1. Testes Unitários (`tests/unit/`)

Os testes unitários verificam o funcionamento isolado de componentes individuais, usando mocks para simular as dependências.

#### Organização:

- **tests/unit/fotix/**: Testes para o módulo raiz (main.py, config.py)
- **tests/unit/fotix/core/**: Testes para os componentes da camada de domínio
  - `test_models.py`: Testes para as estruturas de dados (FileInfo, DuplicateSet)
  - `test_duplicate_finder.py`: Testes para o algoritmo de detecção de duplicatas
  - `test_selection_strategy.py`: Testes para as estratégias de seleção
- **tests/unit/fotix/infrastructure/**: Testes para os componentes da camada de infraestrutura
  - `test_file_system.py`: Testes para o serviço de sistema de arquivos
  - `test_zip_handler.py`: Testes para o manipulador de arquivos ZIP
  - `test_concurrency.py`: Testes para o serviço de concorrência
  - `test_backup.py`: Testes para o serviço de backup
  - `test_interfaces.py`: Testes para as interfaces da infraestrutura
- **tests/unit/fotix/utils/**: Testes para os utilitários
  - `test_helpers.py`: Testes para funções auxiliares
  - `test_image_utils.py`: Testes para utilitários de imagem

### 2. Testes de Integração (`tests/integration/`)

Os testes de integração verificam a interação entre múltiplos componentes, garantindo que funcionem corretamente em conjunto.

#### Organização:

- **tests/integration/fotix/**: Testes para o módulo raiz
  - `test_main_integration.py`: Testes para o ponto de entrada da aplicação
- **tests/integration/fotix/core/**: Testes para integração entre componentes do domínio
  - `test_complex_scenarios_integration.py`: Testes para cenários complexos
  - `test_composite_strategy_integration.py`: Testes para estratégias compostas
- **tests/integration/fotix/application/**: Testes para a camada de aplicação
  - `test_scan_service_integration.py`: Testes para o serviço de varredura
  - `test_duplicate_management_service_integration.py`: Testes para o gerenciamento de duplicatas
  - `test_backup_restore_service_integration.py`: Testes para backup e restauração
  - `test_application_services_integration.py`: Testes para integração entre serviços
- **tests/integration/fotix/infrastructure/**: Testes para integração entre componentes de infraestrutura
  - `test_infrastructure_base_integration.py`: Testes para componentes base
  - `test_zip_concurrency_backup_integration.py`: Testes para integração entre ZIP, concorrência e backup

### 3. Fixtures e Utilitários de Teste

Os testes utilizam fixtures do pytest para configurar ambientes de teste consistentes:

- `temp_dir`: Cria um diretório temporário para testes
- `fs_service`: Cria uma instância do FileSystemService
- `zip_service`: Cria uma instância do ZipHandlerService
- `concurrency_service`: Cria uma instância do ConcurrencyService
- `backup_service`: Cria uma instância do BackupService

### 4. Padrões de Teste

Os testes seguem o padrão AAA (Arrange-Act-Assert):

1. **Arrange**: Configuração do ambiente e dados de teste
2. **Act**: Execução da funcionalidade a ser testada
3. **Assert**: Verificação dos resultados

### 5. Mapeamento com a Estrutura do Código Fonte

A estrutura de testes espelha a estrutura do código fonte:

```
src/fotix/                  tests/unit/fotix/                tests/integration/fotix/
├── core/                   ├── core/                        ├── core/
│   ├── models.py           │   ├── test_models.py           │   ├── test_complex_scenarios_integration.py
│   ├── duplicate_finder.py │   ├── test_duplicate_finder.py │   └── test_composite_strategy_integration.py
│   └── selection_strategy.py   └── test_selection_strategy.py
│
├── application/            ├── application/                 ├── application/
│   └── services/           │   └── services/                │   ├── test_scan_service_integration.py
│       ├── scan_service.py │       ├── test_scan_service.py │   ├── test_duplicate_management_service_integration.py
│       ├── duplicate_mgmt  │       ├── test_duplicate_mgmt  │   ├── test_backup_restore_service_integration.py
│       └── backup_restore  │       └── test_backup_restore  │   └── test_application_services_integration.py
│
├── infrastructure/         ├── infrastructure/              ├── infrastructure/
│   ├── file_system.py      │   ├── test_file_system.py      │   ├── test_infrastructure_base_integration.py
│   ├── zip_handler.py      │   ├── test_zip_handler.py      │   └── test_zip_concurrency_backup_integration.py
│   ├── concurrency.py      │   ├── test_concurrency.py
│   └── backup.py           │   └── test_backup.py
│
└── utils/                  └── utils/
    ├── helpers.py              ├── test_helpers.py
    └── image_utils.py          └── test_image_utils.py
```

Esta estrutura facilita a manutenção dos testes, pois cada componente do código fonte tem seus testes correspondentes organizados de forma similar.
