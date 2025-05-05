## Análise do Blueprint Arquitetural (Fotix v1.0)

### Módulos Base (Fundamentais e Utilitários)

Estes módulos contêm definições essenciais, configurações ou utilidades transversais, geralmente implementados primeiro ou conforme necessário pelas camadas principais.

1.  **`fotix.utils`**
    *   **Responsabilidade Principal (Blueprint):** Funções auxiliares, constantes e utilitários genéricos usados em múltiplas camadas.
2.  **`fotix.config`**
    *   **Responsabilidade Principal (Blueprint):** Carregar e fornecer acesso a configurações da aplicação (ex: caminho do backup, níveis de log).
3.  **`fotix.core.models`**
    *   **Responsabilidade Principal (Blueprint):** Define as estruturas de dados (`FileInfo`, `DuplicateSet`, etc.) usando `dataclasses` ou `Pydantic`. Representa os dados centrais da aplicação.
4.  **`fotix.infrastructure.interfaces`**
    *   **Responsabilidade Principal (Blueprint):** Define as interfaces (contratos) para os serviços da camada de infraestrutura (ex: `IFileSystemService`, `IConcurrencyService`, `IBackupService`, `IZipHandlerService`). Garante o desacoplamento.
5.  **`fotix.core.interfaces`**
    *   **Responsabilidade Principal (Blueprint):** Define as interfaces expostas pela camada Core para serem usadas pela camada de Aplicação (ex: `IDuplicateFinderService`, `ISelectionStrategy`).

---

### Ordem de Implementação Sugerida (Módulos Principais)

Esta ordem foca nos módulos que contêm a lógica de implementação principal, seguindo as dependências identificadas no blueprint.

1.  **`fotix.infrastructure.logging_config`**
    *   **Descrição de Alto Nível Inicial:** Configura o sistema de logging para a aplicação Fotix. Define como as mensagens de log serão formatadas, para onde serão enviadas (console, arquivo) e o nível de detalhe inicial.
    *   *Justificativa da Ordem:* É uma configuração fundamental e independente, útil desde o início do desenvolvimento para rastrear o comportamento dos outros módulos. Depende apenas de bibliotecas externas e `fotix.config`.

2.  **`fotix.core.selection_strategy`**
    *   **Descrição de Alto Nível Inicial:** Implementa a lógica de negócio central para escolher qual arquivo manter dentro de um conjunto de duplicatas identificadas. Analisa os metadados dos arquivos (definidos em `fotix.core.models`) com base em critérios configurados (ex: resolução, data).
    *   *Justificativa da Ordem:* Representa uma parte pura da lógica de negócio (Core). Depende apenas dos `models` e `utils`, podendo ser desenvolvida e testada isoladamente no início.

3.  **`fotix.infrastructure.file_system`**
    *   **Descrição de Alto Nível Inicial:** Implementa a interface `IFileSystemService`, fornecendo a funcionalidade concreta para interagir com o sistema de arquivos. Encapsula operações como leitura de tamanho de arquivo, listagem de diretórios, leitura de conteúdo e movimentação para a lixeira, usando bibliotecas como `pathlib` e `send2trash`.
    *   *Justificativa da Ordem:* É um serviço de infraestrutura fundamental, necessário para muitas outras partes do sistema (Core e Application). Depende de `interfaces`, `utils` e bibliotecas externas.

4.  **`fotix.infrastructure.zip_handler`**
    *   **Descrição de Alto Nível Inicial:** Implementa a interface `IZipHandlerService` para lidar com a leitura de arquivos dentro de arquivos ZIP de forma eficiente (streaming). Permite acessar nomes, tamanhos e conteúdo dos arquivos internos sem extração completa.
    *   *Justificativa da Ordem:* Serviço de infraestrutura específico, necessário para a funcionalidade de busca de duplicatas (`duplicate_finder`). Depende de `interfaces` e bibliotecas externas.

5.  **`fotix.infrastructure.concurrency`**
    *   **Descrição de Alto Nível Inicial:** Implementa a interface `IConcurrencyService` para gerenciar a execução de tarefas em paralelo ou em background. Abstrai o uso de mecanismos como `concurrent.futures` (Thread/Process Pools).
    *   *Justificativa da Ordem:* Serviço de infraestrutura necessário para otimizar tarefas demoradas como a varredura e hashing na camada de Aplicação (`ScanService`). Depende de `interfaces` e bibliotecas externas.

6.  **`fotix.core.duplicate_finder`**
    *   **Descrição de Alto Nível Inicial:** Implementa a lógica central de detecção de duplicatas. Utiliza hashing (BLAKE3) e comparação de arquivos, interagindo com o sistema de arquivos e arquivos ZIP através das abstrações (`IFileSystemService`, `IZipHandlerService`) para manter-se independente da infraestrutura concreta.
    *   *Justificativa da Ordem:* Componente central da lógica de negócio. Depende dos `models`, `utils` e das *interfaces* de infraestrutura (que já teriam suas implementações básicas prontas nos passos anteriores para permitir testes integrados).

7.  **`fotix.infrastructure.backup`**
    *   **Descrição de Alto Nível Inicial:** Implementa a interface `IBackupService`, gerenciando a cópia segura de arquivos para uma área de backup e sua posterior restauração ou listagem. Pode envolver o armazenamento de metadados sobre os backups.
    *   *Justificativa da Ordem:* Serviço de infraestrutura que depende de outros serviços (`IFileSystemService`), `models` e `config`. Necessário para a funcionalidade de gerenciamento e restauração na camada de Aplicação.

8.  **`fotix.application.services.scan_service`**
    *   **Descrição de Alto Nível Inicial:** Orquestra o caso de uso de varredura de diretórios e arquivos ZIP em busca de duplicatas. Coordena o uso dos serviços de infraestrutura (`IFileSystemService`, `IZipHandlerService`, `IConcurrencyService`) e invoca a lógica central de busca (`IDuplicateFinderService`).
    *   *Justificativa da Ordem:* Primeiro serviço de aplicação, implementando um fluxo principal. Depende das interfaces do Core e da Infraestrutura, e de suas implementações para funcionar.

9.  **`fotix.application.services.duplicate_management_service`**
    *   **Descrição de Alto Nível Inicial:** Orquestra o caso de uso de gerenciamento das duplicatas encontradas. Utiliza a estratégia de seleção (`ISelectionStrategy`) para determinar o arquivo a manter e coordena a remoção segura (via `IFileSystemService`) e o backup (via `IBackupService`) dos demais.
    *   *Justificativa da Ordem:* Serviço de aplicação complementar ao `ScanService`. Depende das interfaces do Core (`ISelectionStrategy`), da Infraestrutura (`IFileSystemService`, `IBackupService`) e dos `models`.

10. **`fotix.application.services.backup_restore_service`**
    *   **Descrição de Alto Nível Inicial:** Orquestra os casos de uso relacionados à gestão de backups. Utiliza o `IBackupService` para listar backups existentes, restaurar arquivos a partir de um backup específico e possivelmente excluir backups antigos.
    *   *Justificativa da Ordem:* Serviço de aplicação focado na funcionalidade de backup/restauração. Depende principalmente da interface `IBackupService` e `IFileSystemService`.

11. **`fotix.ui`**
    *   **Descrição de Alto Nível Inicial:** Implementa a interface gráfica do usuário (GUI) usando PySide6. Exibe informações (arquivos, duplicatas, progresso), captura entradas do usuário (pastas, seleções, confirmações) e interage com a camada de Aplicação para iniciar ações e receber atualizações.
    *   *Justificativa da Ordem:* A camada de apresentação depende da camada de Aplicação (serviços/interfaces) para executar as funcionalidades e dos `models` para exibir dados. É implementada após a lógica principal estar disponível.

12. **`fotix.main`**
    *   **Descrição de Alto Nível Inicial:** Ponto de entrada principal da aplicação Fotix. Responsável por inicializar os componentes necessários (configuração, logging, serviços da aplicação, UI), conectar as camadas e iniciar o loop de eventos da interface gráfica.
    *   *Justificativa da Ordem:* É o ponto que une todas as partes. Precisa que a UI e os serviços da Aplicação estejam prontos para serem instanciados e conectados.

---

**Observação sobre Ciclos:** Nenhuma dependência cíclica *entre os módulos principais listados na ordem* foi detectada com base no blueprint fornecido. As dependências seguem o fluxo esperado da Arquitetura em Camadas (UI -> Application -> Core / Infrastructure).