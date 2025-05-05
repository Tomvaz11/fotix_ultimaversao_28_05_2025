## Análise de Implementação e Próximos Passos para Fotix

**Instruções para o Coordenador:**

Este documento organiza os módulos do projeto Fotix para guiar a implementação. Ele separa os "Módulos Base" (definições, utilitários, configurações e estruturas de dados) dos "Módulos Principais" (que contêm a lógica central e as implementações concretas dos serviços).

*   **NÃO implemente os "Módulos Base" listados abaixo diretamente agora.** Suas pastas e arquivos básicos (como `__init__.py`, `interfaces.py`, `models.py`) serão criados quando necessário pela IA durante a implementação dos módulos principais que dependem deles. O conteúdo específico de `fotix.utils` será adicionado organicamente conforme a necessidade surgir nos módulos principais. A estrutura inicial de `fotix.config` pode ser simples e expandida depois.
*   **SIGA a "Ordem de Implementação Sugerida (Módulos Principais)" abaixo.** Comece pelo **Item #1** e prossiga sequencialmente.
*   Para **CADA item** da ordem numerada, use o `Prompt_ImplementadorMestre_vX.Y` (use a versão mais atual), preenchendo apenas o nome do módulo alvo (ex: "Item 1: fotix.infrastructure.logging_config"). Anexe sempre o `@Blueprint_Arquitetural.md`, este arquivo (`@Ordem_Com_Descricoes.md`) e o código relevante já existente como contexto. A "Descrição de Alto Nível Inicial" listada abaixo para cada item servirá como ponto de partida para a IA.

---

### Módulos Base (Estrutura Inicial / Conteúdo On-Demand)

Estes módulos contêm definições, estruturas ou utilitários que são pré-requisitos ou suportam os módulos principais. Sua estrutura básica será criada conforme necessário.

*   **`fotix.config`:** Responsável por carregar e fornecer acesso a configurações da aplicação (ex: caminho do backup, níveis de log).
*   **`fotix.utils`:** Contém funções auxiliares, constantes e utilitários genéricos usados em múltiplas camadas. O conteúdo será adicionado conforme necessário.
*   **`fotix.infrastructure.interfaces`:** Define as interfaces (contratos) para os serviços da camada de infraestrutura (ex: `IFileSystemService`, `IConcurrencyService`, `IBackupService`, `IZipHandlerService`). A IA criará este arquivo e definirá as interfaces conforme os módulos de implementação (`fotix.infrastructure.*`) são criados.
*   **`fotix.core.models`:** Define as estruturas de dados centrais (ex: `FileInfo`, `DuplicateSet`) usando `dataclasses` ou `Pydantic`. A IA criará este arquivo e definirá os modelos conforme necessário, principalmente ao implementar `fotix.core.duplicate_finder`.
*   **`fotix.core.interfaces`:** Define as interfaces (contratos) para os serviços da camada de domínio que são expostos para a camada de aplicação (ex: `IDuplicateFinderService`, `ISelectionStrategy`). A IA criará este arquivo e definirá as interfaces conforme os módulos de implementação (`fotix.core.*`) são criados.
*   **`fotix.application.interfaces`:** Define as interfaces (contratos) expostas pela camada de Aplicação para a camada de UI (se houver necessidade explícita de interfaces entre Aplicação e UI). A IA criará este arquivo se/quando a implementação da UI o exigir.

---

### Ordem de Implementação Sugerida (Módulos Principais)

1.  **`fotix.infrastructure.logging_config`**
    *   **Descrição de Alto Nível Inicial:** Configurar o sistema de logging padrão do Python para a aplicação Fotix. Definir formatos de log, níveis e possíveis handlers (console, arquivo) com base nas configurações carregadas de `fotix.config`.
    *   *Justificativa da Ordem:* O logging é fundamental e deve estar disponível desde o início para auxiliar no desenvolvimento e depuração dos módulos subsequentes. É relativamente independente de outras lógicas.

2.  **`fotix.infrastructure.file_system`**
    *   **Descrição de Alto Nível Inicial:** Implementar a interface `IFileSystemService` definida em `fotix.infrastructure.interfaces`. Esta implementação proverá funcionalidades concretas para interagir com o sistema de arquivos local, como listar diretórios, obter tamanho de arquivo, ler conteúdo de forma eficiente (streaming), mover para a lixeira e copiar arquivos, usando bibliotecas como `pathlib`, `shutil` e `send2trash`.
    *   *Justificativa da Ordem:* Operações de sistema de arquivos são a base para muitas outras funcionalidades (scan, backup, core). Implementar esta abstração cedo permite que os módulos Core e Application dependam de um contrato estável (`IFileSystemService`).

3.  **`fotix.infrastructure.zip_handler`**
    *   **Descrição de Alto Nível Inicial:** Implementar a interface `IZipHandlerService` definida em `fotix.infrastructure.interfaces`. Focará em ler o conteúdo de arquivos dentro de arquivos ZIP de forma eficiente (streaming), sem a necessidade de extração completa para o disco, utilizando a biblioteca `stream-unzip`.
    *   *Justificativa da Ordem:* Necessário para a funcionalidade central de scan dentro de ZIPs. Depende de conceitos básicos de arquivo (caminhos), mas é uma capacidade específica de IO que o Core precisará (via interface).

4.  **`fotix.infrastructure.concurrency`**
    *   **Descrição de Alto Nível Inicial:** Implementar a interface `IConcurrencyService` definida em `fotix.infrastructure.interfaces`. Fornecerá uma forma abstrata de executar tarefas em paralelo (provavelmente usando `concurrent.futures.ThreadPoolExecutor` inicialmente) para otimizar operações como hashing de múltiplos arquivos.
    *   *Justificativa da Ordem:* A concorrência será crucial para o desempenho do `duplicate_finder`. Implementar esta abstração permite que a lógica de concorrência seja gerenciada separadamente da lógica de negócio principal.

5.  **`fotix.infrastructure.backup`**
    *   **Descrição de Alto Nível Inicial:** Implementar a interface `IBackupService` definida em `fotix.infrastructure.interfaces`. Gerenciará a cópia segura de arquivos para uma área de backup designada, o armazenamento de metadados sobre os backups e a capacidade de listar e restaurar esses backups. Utilizará o `IFileSystemService` para operações de arquivo.
    *   *Justificativa da Ordem:* Implementa a funcionalidade de backup/restauração. Depende do `IFileSystemService` e possivelmente de `fotix.core.models` (para `FileInfo`). É uma parte importante da infraestrutura de segurança/recuperação.

6.  **`fotix.core.duplicate_finder`**
    *   **Descrição de Alto Nível Inicial:** Implementar a lógica central de detecção de duplicatas, definindo e implementando a interface `IDuplicateFinderService` (de `fotix.core.interfaces`). Utilizará as abstrações `IFileSystemService` e `IZipHandlerService` (injetadas) para acessar dados de arquivos e ZIPs, aplicará hashing (BLAKE3) e comparação para identificar conjuntos de arquivos idênticos (`DuplicateSet` de `fotix.core.models`). Incluirá otimizações como pré-filtragem por tamanho.
    *   *Justificativa da Ordem:* É o coração da lógica de negócio. Depende das interfaces de infraestrutura (IO, ZIP) e dos modelos de dados (`FileInfo`, `DuplicateSet`). Sua implementação habilita a funcionalidade principal da aplicação.

7.  **`fotix.core.selection_strategy`**
    *   **Descrição de Alto Nível Inicial:** Implementar diferentes estratégias para selecionar qual arquivo manter dentro de um `DuplicateSet`, definindo e implementando a interface `ISelectionStrategy` (de `fotix.core.interfaces`). As estratégias podem se basear em critérios como data, resolução (se aplicável a imagens/vídeos no futuro, por agora focar em data/nome/caminho), ou outros definidos nos requisitos.
    *   *Justificativa da Ordem:* Complementa a lógica do core, definindo *como* agir sobre as duplicatas encontradas. Depende dos modelos (`DuplicateSet`, `FileInfo`) e será usada pela camada de Aplicação.

8.  **`fotix.application.services.scan_service`**
    *   **Descrição de Alto Nível Inicial:** Orquestrar o processo completo de varredura. Irá receber os caminhos a serem escaneados, utilizar o `IDuplicateFinderService` (do Core) para encontrar as duplicatas, e possivelmente usar o `IConcurrencyService` (da Infraestrutura) para gerenciar a execução. Coordenará a interação entre Core e Infra durante a varredura.
    *   *Justificativa da Ordem:* É o primeiro serviço de aplicação que orquestra um fluxo de trabalho principal, utilizando serviços do Core e da Infraestrutura já implementados (ou suas interfaces).

9.  **`fotix.application.services.duplicate_management_service`**
    *   **Descrição de Alto Nível Inicial:** Gerenciar as ações sobre os conjuntos de duplicatas encontrados. Utilizará a `ISelectionStrategy` (do Core) para determinar o arquivo a manter, e os serviços `IFileSystemService` (para mover para a lixeira) e `IBackupService` (para backup antes da remoção) da Infraestrutura para executar as ações.
    *   *Justificativa da Ordem:* Orquestra o fluxo de resolução de duplicatas, dependendo dos resultados do scan (implícito), das estratégias do Core e dos serviços de manipulação de arquivos/backup da Infraestrutura.

10. **`fotix.application.services.backup_restore_service`**
    *   **Descrição de Alto Nível Inicial:** Orquestrar as operações relacionadas a backups. Utilizará o `IBackupService` para listar, restaurar e deletar backups, e o `IFileSystemService` se necessário para operações de arquivo durante a restauração.
    *   *Justificativa da Ordem:* Implementa a interface do usuário para a funcionalidade de backup/restauração, dependendo diretamente do `IBackupService` da Infraestrutura.

11. **`fotix.ui` (Implementação Principal, ex: `fotix.ui.main_window`)**
    *   **Descrição de Alto Nível Inicial:** Construir a interface gráfica do usuário utilizando PySide6. Exibirá os controles para iniciar a varredura, mostrará os resultados (conjuntos de duplicatas), permitirá ao usuário revisar e confirmar ações (remoção/backup), exibirá progresso e status, e permitirá gerenciar backups. Interagirá com os serviços da camada de Aplicação (`ScanService`, `DuplicateManagementService`, `BackupRestoreService`).
    *   *Justificativa da Ordem:* A UI é a camada mais externa, dependendo dos serviços da camada de Aplicação para realizar qualquer ação significativa. Só pode ser construída de forma funcional quando a camada de aplicação estiver pronta.

12. **`fotix.main`**
    *   **Descrição de Alto Nível Inicial:** Ponto de entrada da aplicação. Será responsável por inicializar as dependências (configuração, logging), instanciar as camadas (Infraestrutura, Core, Aplicação - configurando a injeção de dependência se aplicável), criar e exibir a janela principal da UI (`fotix.ui.main_window`), e iniciar o loop de eventos da aplicação Qt.
    *   *Justificativa da Ordem:* É o ponto final que conecta todas as partes e inicia a execução da aplicação. Depende da UI e da inicialização das camadas inferiores.