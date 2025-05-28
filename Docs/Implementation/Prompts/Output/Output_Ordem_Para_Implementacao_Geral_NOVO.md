## Análise de Implementação e Próximos Passos para Fotix

**Instruções para o Coordenador:**

Este documento organiza os módulos do projeto Fotix para guiar a implementação. Ele separa os "Módulos Base" (definições, utilitários e interfaces) dos "Módulos Principais" (que contêm a lógica central e as implementações concretas dos serviços).

*   **NÃO implemente os "Módulos Base" listados abaixo diretamente agora.** Suas pastas e arquivos básicos (como `__init__.py`, arquivos de interfaces, modelos de dados) serão criados ou modificados quando necessário pela IA (`ImplementadorMestre`) durante a implementação dos módulos principais que dependem deles. O conteúdo específico de módulos como `fotix.utils` será adicionado organicamente conforme a necessidade surgir.
*   **SIGA a "Ordem de Implementação Sugerida (Módulos Principais e Pontos de Teste de Integração)" abaixo.** Comece pelo **Item #1** da lista de Módulos Principais e prossiga sequencialmente.
*   Para **CADA item** da ordem numerada de Módulo Principal, use o `Prompt_ImplementadorMestre_vX.Y` (recomenda-se a versão mais recente, ex: v1.7+), preenchendo apenas o nome do módulo alvo (ex: "Item 1: `fotix.infrastructure.logging_service`"). Anexe sempre o `@Blueprint_Arquitetural.md`, este arquivo (`@Ordem_Com_Descricoes_e_Testes_Integracao.md`) e o código relevante já existente como contexto. A "Descrição de Alto Nível Inicial" listada abaixo para cada item servirá como ponto de partida para a IA.
*   **PONTOS DE TESTE DE INTEGRAÇÃO:** Em certos pontos, este documento indicará uma **">>> PARADA PARA TESTES DE INTEGRAÇÃO (Nome do Subsistema) <<<"**. Nestes momentos, **antes de prosseguir** com o próximo Módulo Principal da lista, você deverá usar um prompt dedicado para testes de integração (ex: `Prompt_IntegradorTester_vX.Y`, que será definido posteriormente) para guiar a IA na criação e execução de testes de integração para o grupo de módulos recém-concluído. Utilize os "Cenários Chave para Teste de Integração" listados como ponto de partida para esses testes. Após os testes de integração serem concluídos e validados, você poderá prosseguir para o próximo item da ordem de implementação.

---

### Módulos Base (Estrutura Inicial / Conteúdo On-Demand)

*   **`fotix.infrastructure.interfaces`**:
    *   **Responsabilidade:** Define os contratos (interfaces Python Protocol) para todos os serviços da camada de infraestrutura (`IFileSystemService`, `IZipService`, `IHashingService`, `IConcurrencyService`, `IBackupService`, `ILoggingService`).
*   **`fotix.domain.models`**:
    *   **Responsabilidade:** Define as estruturas de dados centrais do domínio (ex: `FileItem`, `DuplicateGroup`, `ScanSettings`, `BackupManifestEntry`).
*   **`fotix.utils.helpers`**:
    *   **Responsabilidade:** Contém funções auxiliares genéricas e utilitários que podem ser usados em múltiplas camadas (ex: formatação de datas, manipulação de strings, etc.).

---

### Ordem de Implementação Sugerida (Módulos Principais e Pontos de Teste de Integração) - COMECE AQUI (Item #1)

1.  **`fotix.infrastructure.logging_service.LoggingServiceImpl`**
    *   **Descrição de Alto Nível Inicial:** Implementar o serviço `ILoggingService` para configurar e gerenciar o logging da aplicação, permitindo registrar eventos importantes, erros e informações de depuração em arquivos.
    *   **Justificativa da Ordem:** Logging é fundamental para o desenvolvimento e depuração de todos os outros módulos. Implementá-lo primeiro permite que os módulos subsequentes já possam logar suas atividades.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.infrastructure.interfaces.ILoggingService`.

2.  **`fotix.infrastructure.file_system_service.FileSystemServiceImpl`**
    *   **Descrição de Alto Nível Inicial:** Implementar o serviço `IFileSystemService` para abstrair todas as interações com o sistema de arquivos, como leitura de metadados, listagem de diretórios, leitura de arquivos em chunks e remoção segura.
    *   **Justificativa da Ordem:** Operações de arquivo são a base para muitas funcionalidades do Fotix (hashing, backup, escaneamento).
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.infrastructure.interfaces.IFileSystemService`.

3.  **`fotix.infrastructure.hashing_service.HashingServiceImpl`**
    *   **Descrição de Alto Nível Inicial:** Implementar o serviço `IHashingService` para calcular hashes de arquivos de forma eficiente, utilizando o algoritmo BLAKE3, para identificar duplicatas.
    *   **Justificativa da Ordem:** O cálculo de hash é central para a funcionalidade principal de encontrar duplicatas. Depende de poder ler arquivos (via `IFileSystemService` indiretamente, através do fluxo de dados).
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.infrastructure.interfaces.IHashingService`.

---

**>>> PARADA PARA TESTES DE INTEGRAÇÃO (INFRAESTRUTURA BÁSICA DE ARQUIVOS E LOGGING) <<<**

*   **Módulos Implementados neste Grupo:**
    *   `fotix.infrastructure.logging_service.LoggingServiceImpl`
    *   `fotix.infrastructure.file_system_service.FileSystemServiceImpl`
    *   `fotix.infrastructure.hashing_service.HashingServiceImpl`
    *   (Módulos Base associados: `fotix.infrastructure.interfaces` contendo `ILoggingService`, `IFileSystemService`, `IHashingService`)
*   **Objetivo do Teste de Integração:** Validar que os serviços de logging, sistema de arquivos e hashing funcionam individualmente e que o `FileSystemService` pode fornecer dados para o `HashingService`, com todas as operações relevantes sendo logadas.
*   **Cenários Chave para Teste de Integração:**
    1.  **Leitura e Hashing com Logging:** Criar um arquivo de teste. Usar `FileSystemServiceImpl` para ler seus chunks e `HashingServiceImpl` para calcular seu hash. Verificar se o hash é o esperado e se as operações (leitura, início/fim do hash) são logadas pelo `LoggingServiceImpl`.
    2.  **Listagem de Diretório com Logging:** Usar `FileSystemServiceImpl` para listar arquivos em um diretório de teste (com alguns arquivos e subdiretórios). Verificar se a listagem está correta e se a operação é logada.
    3.  **Tratamento de Erro de Arquivo com Logging:** Tentar ler um arquivo inexistente usando `FileSystemServiceImpl`. Verificar se uma exceção apropriada é levantada (ou tratada internamente e sinalizada) e se um erro é logado pelo `LoggingServiceImpl`.
    4.  **Verificação de Hash Consistente:** Calcular o hash de um mesmo arquivo duas vezes e garantir que o resultado é idêntico.
*   **Instrução para o Coordenador:** Use o `Prompt_IntegradorTester_vX.Y` (a ser definido) para gerar testes para estes cenários, focando na interação entre esses serviços de infraestrutura. Após os testes passarem e serem validados, prossiga para o próximo item da ordem de implementação.

---

4.  **`fotix.infrastructure.zip_service.ZipServiceImpl`**
    *   **Descrição de Alto Nível Inicial:** Implementar o serviço `IZipService` para permitir a listagem de entradas e a leitura de arquivos de dentro de arquivos ZIP de forma eficiente (streaming).
    *   **Justificativa da Ordem:** Necessário para o escaneamento de arquivos ZIP, uma funcionalidade chave. Depende do `IFileSystemService` para acessar o arquivo ZIP em si.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.infrastructure.interfaces.IZipService`.

5.  **`fotix.infrastructure.concurrency_service.ConcurrencyServiceImpl`**
    *   **Descrição de Alto Nível Inicial:** Implementar o serviço `IConcurrencyService` para gerenciar a execução de tarefas em paralelo, utilizando `concurrent.futures`, otimizando processos como hashing de múltiplos arquivos.
    *   **Justificativa da Ordem:** Essencial para melhorar a performance do escaneamento, que pode ser intensivo.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.infrastructure.interfaces.IConcurrencyService`.

6.  **`fotix.domain.duplicate_finder.DuplicateFinder`**
    *   **Descrição de Alto Nível Inicial:** Implementar a lógica de negócio central para identificar grupos de arquivos duplicados com base em uma lista de `FileItem` (com seus hashes e metadados), utilizando pré-filtragem por tamanho e agrupamento por hash.
    *   **Justificativa da Ordem:** É o coração da funcionalidade de detecção de duplicatas. Requer que os modelos de dados (`FileItem`, `DuplicateGroup` de `fotix.domain.models`) estejam definidos.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.domain.models`.

7.  **`fotix.domain.selection_strategy.SelectionStrategy`**
    *   **Descrição de Alto Nível Inicial:** Implementar a lógica para decidir automaticamente qual arquivo manter dentro de um grupo de duplicatas, com base em critérios configuráveis (ex: data, resolução).
    *   **Justificativa da Ordem:** Complementa o `DuplicateFinder` ao automatizar a seleção de arquivos, uma etapa importante do fluxo de trabalho.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.domain.models`.

---

**>>> PARADA PARA TESTES DE INTEGRAÇÃO (NÚCLEO DE DETECÇÃO DE DUPLICATAS) <<<**

*   **Módulos Implementados neste Grupo:**
    *   `fotix.infrastructure.zip_service.ZipServiceImpl`
    *   `fotix.infrastructure.concurrency_service.ConcurrencyServiceImpl` (seu uso será testado mais no `ScanOrchestratorService`)
    *   `fotix.domain.duplicate_finder.DuplicateFinder`
    *   `fotix.domain.selection_strategy.SelectionStrategy`
    *   (Módulos Base associados: `fotix.domain.models`, `fotix.infrastructure.interfaces` contendo `IZipService`, `IConcurrencyService`)
*   **Objetivo do Teste de Integração:** Validar que o `DuplicateFinder` pode processar uma lista de `FileItem` (com hashes pré-calculados) e identificar corretamente os grupos de duplicatas, e que `SelectionStrategy` pode selecionar o arquivo correto para manter. Testar a integração do `IZipService` com o `IHashingService` para hashear arquivos dentro de ZIPs.
*   **Cenários Chave para Teste de Integração:**
    1.  **Identificação de Duplicatas Simples:** Fornecer uma lista de `FileItem` com alguns duplicados (mesmo hash, tamanhos diferentes para teste de pré-filtro, e mesmo hash/tamanho) e alguns únicos. Verificar se `DuplicateFinder` retorna os grupos corretos.
    2.  **Seleção de Arquivo por Estratégia:** Para um `DuplicateGroup` conhecido, aplicar diferentes configurações de `SelectionStrategy` (ex: preferir mais antigo, preferir nome específico) e verificar se o `file_to_keep` é selecionado corretamente.
    3.  **Hashing de Arquivo em ZIP:** Usar `ZipServiceImpl` para extrair chunks de um arquivo dentro de um ZIP e `HashingServiceImpl` para calcular seu hash. Verificar se o hash é o esperado para o conteúdo do arquivo.
    4.  **Cenário Sem Duplicatas:** Fornecer uma lista de `FileItem` todos únicos. Verificar se `DuplicateFinder` retorna uma lista vazia de grupos de duplicatas.
*   **Instrução para o Coordenador:** Use o `Prompt_IntegradorTester_vX.Y` para gerar testes que validem a lógica do domínio e a capacidade de processar arquivos ZIP. O `ConcurrencyService` será mais testado com o `ScanOrchestrator`. Após os testes passarem, prossiga.

---

8.  **`fotix.application_services.scan_orchestrator.ScanOrchestratorService`**
    *   **Descrição de Alto Nível Inicial:** Orquestrar o processo completo de escaneamento: listar arquivos (usando `IFileSystemService` e `IZipService`), calcular hashes (usando `IHashingService` e `IConcurrencyService`), identificar duplicatas (usando `DuplicateFinder`), e aplicar estratégias de seleção (usando `SelectionStrategy`).
    *   **Justificativa da Ordem:** Este serviço integra vários componentes de infraestrutura e domínio para realizar um dos principais casos de uso da aplicação.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.domain.duplicate_finder.DuplicateFinder`, `fotix.domain.selection_strategy.SelectionStrategy`, `fotix.domain.models`, `fotix.infrastructure.interfaces.IFileSystemService`, `fotix.infrastructure.interfaces.IZipService`, `fotix.infrastructure.interfaces.IHashingService`, `fotix.infrastructure.interfaces.IConcurrencyService`, `fotix.infrastructure.interfaces.ILoggingService`.

---

**>>> PARADA PARA TESTES DE INTEGRAÇÃO (FLUXO DE ESCANEAMENTO COMPLETO) <<<**

*   **Módulos Implementados neste Grupo:**
    *   `fotix.application_services.scan_orchestrator.ScanOrchestratorService`
    *   (E todos os módulos dos quais ele depende, já implementados e testados unitariamente/em integrações menores)
*   **Objetivo do Teste de Integração:** Validar o fluxo completo de escaneamento orquestrado pelo `ScanOrchestratorService`, desde a entrada (caminhos a escanear) até a saída (lista de `DuplicateGroup` com seleções feitas). Verificar o uso da concorrência.
*   **Cenários Chave para Teste de Integração:**
    1.  **Escaneamento de Diretório com Duplicatas:** Configurar um diretório com alguns arquivos duplicados e únicos. Executar o `ScanOrchestratorService` e verificar se os `DuplicateGroup`s corretos são identificados e se a `SelectionStrategy` padrão foi aplicada.
    2.  **Escaneamento com Arquivos ZIP:** Incluir arquivos ZIP contendo duplicatas (internas ao ZIP e com arquivos fora do ZIP) no escaneamento. Verificar se são processados corretamente.
    3.  **Escaneamento com Concorrência:** Executar um escaneamento em um volume maior de arquivos (simulados) e verificar (indiretamente, por tempo ou logs, se o `ConcurrencyService` o permitir) que o processamento paralelo está ocorrendo e se os resultados são consistentes.
    4.  **Escaneamento de Caminho Inválido/Vazio:** Tentar escanear um caminho que não existe ou um diretório vazio. Verificar se o serviço lida com isso de forma graciosa (ex: retorna lista vazia, loga aviso).
*   **Instrução para o Coordenador:** Use o `Prompt_IntegradorTester_vX.Y` para criar testes de integração end-to-end para o `ScanOrchestratorService`. Estes testes serão mais complexos, envolvendo a configuração de um ambiente de arquivos de teste. Após validação, prossiga.

---

9.  **`fotix.infrastructure.backup_service.BackupServiceImpl`**
    *   **Descrição de Alto Nível Inicial:** Implementar o serviço `IBackupService` para gerenciar o backup de arquivos (copiando-os para um local seguro) e a restauração, mantendo um manifesto dos backups.
    *   **Justificativa da Ordem:** O serviço de backup é crucial para a segurança das operações de arquivo e é um pré-requisito para `FileOperationService` e `RestoreOrchestratorService`.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.infrastructure.interfaces.IBackupService`, `fotix.infrastructure.interfaces.IFileSystemService` (para operações de arquivo), `fotix.domain.models.BackupManifestEntry`.

10. **`fotix.application_services.file_operation_service.FileOperationService`**
    *   **Descrição de Alto Nível Inicial:** Orquestrar a remoção segura de arquivos duplicados, utilizando o `IBackupService` para backup prévio e o `IFileSystemService` para a remoção (para a lixeira).
    *   **Justificativa da Ordem:** Implementa o caso de uso de remoção de arquivos, que depende do `ScanOrchestratorService` (para obter a lista de arquivos a remover) e do `BackupService`.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.domain.models`, `fotix.infrastructure.interfaces.IFileSystemService`, `fotix.infrastructure.interfaces.IBackupService`, `fotix.infrastructure.interfaces.ILoggingService`.

---

**>>> PARADA PARA TESTES DE INTEGRAÇÃO (OPERAÇÕES DE ARQUIVO: BACKUP E REMOÇÃO) <<<**

*   **Módulos Implementados neste Grupo:**
    *   `fotix.infrastructure.backup_service.BackupServiceImpl`
    *   `fotix.application_services.file_operation_service.FileOperationService`
*   **Objetivo do Teste de Integração:** Validar que o `BackupServiceImpl` pode fazer backup e listar backups, e que o `FileOperationService` pode usar o `BackupServiceImpl` para fazer backup de um arquivo e, em seguida, usar o `FileSystemServiceImpl` para movê-lo para a lixeira.
*   **Cenários Chave para Teste de Integração:**
    1.  **Backup e Verificação:** Criar um arquivo de teste. Usar `BackupServiceImpl` para fazer backup. Verificar se o arquivo existe no local de backup e se uma entrada correspondente está no manifesto.
    2.  **Remoção com Backup:** Fornecer uma lista simulada de `FileItem` (representando um arquivo a ser removido). Executar `FileOperationService` para remover. Verificar se o arquivo foi backupeado pelo `BackupServiceImpl` e se o arquivo original foi movido para a lixeira (ou simulado, se `send2trash` for difícil de testar automaticamente).
    3.  **Tentativa de Backup de Arquivo Inexistente:** Tentar fazer backup de um arquivo que não existe. Verificar se `BackupServiceImpl` lida com o erro e loga apropriadamente.
    4.  **Listagem de Backups:** Após alguns backups, usar `BackupServiceImpl` para listar as entradas e verificar se correspondem aos backups feitos.
*   **Instrução para o Coordenador:** Use o `Prompt_IntegradorTester_vX.Y` para testar os fluxos de backup e remoção. Verifique a integridade do manifesto de backup. Após validação, prossiga.

---

11. **`fotix.application_services.restore_orchestrator.RestoreOrchestratorService`**
    *   **Descrição de Alto Nível Inicial:** Orquestrar a restauração de arquivos a partir do backup, usando `IBackupService` para listar e executar restaurações e `IFileSystemService` para gerenciar o arquivo restaurado.
    *   **Justificativa da Ordem:** Implementa o caso de uso de restauração, completando o ciclo de vida do backup.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.infrastructure.interfaces.IBackupService`, `fotix.infrastructure.interfaces.IFileSystemService`, `fotix.infrastructure.interfaces.ILoggingService`.

---

**>>> PARADA PARA TESTES DE INTEGRAÇÃO (FLUXO DE RESTAURAÇÃO) <<<**

*   **Módulos Implementados neste Grupo:**
    *   `fotix.application_services.restore_orchestrator.RestoreOrchestratorService`
*   **Objetivo do Teste de Integração:** Validar que o `RestoreOrchestratorService` pode listar backups disponíveis (via `IBackupService`) e restaurar um arquivo selecionado para seu local original ou um novo local.
*   **Cenários Chave para Teste de Integração:**
    1.  **Listar e Restaurar para Original:** Fazer backup de um arquivo. Listar backups usando `RestoreOrchestratorService`. Selecionar a entrada e restaurar para o local original. Verificar se o arquivo está no local original.
    2.  **Restaurar para Destino Customizado:** Fazer backup de um arquivo. Restaurar para um diretório de destino customizado. Verificar se o arquivo está no novo local.
    3.  **Tentativa de Restaurar Entrada Inválida:** Tentar restaurar usando uma `BackupManifestEntry` inválida/inexistente. Verificar tratamento de erro.
    4.  **Restauração com Conflito de Arquivo (Opcional):** Se o arquivo original ainda existir, como o serviço lida com isso (substitui, renomeia, falha - conforme especificação).
*   **Instrução para o Coordenador:** Use o `Prompt_IntegradorTester_vX.Y` para testar o fluxo de restauração. Após validação, prossiga para a camada de UI.

---

12. **`fotix.ui.views.ConfigView`**
    *   **Descrição de Alto Nível Inicial:** Implementar a tela de configuração onde o usuário seleciona diretórios/ZIPs e define opções de escaneamento, interagindo com `ScanOrchestratorService`.
    *   **Justificativa da Ordem:** É o ponto de entrada do usuário para a funcionalidade principal de escaneamento. Depende do `ScanOrchestratorService` estar funcional para iniciar um escaneamento.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.application_services.ScanOrchestratorService`.

13. **`fotix.ui.views.ProgressView`**
    *   **Descrição de Alto Nível Inicial:** Implementar a tela que exibe o progresso do escaneamento e das operações de arquivo, observando sinais/eventos dos serviços de aplicação.
    *   **Justificativa da Ordem:** Fornece feedback vital ao usuário durante operações demoradas. Pode ser desenvolvida em paralelo ou após `ConfigView`, pois depende de sinais emitidos pelos serviços de aplicação.
    *   **Dependências Chave (Inferidas do Blueprint):** Sinais/eventos de `ScanOrchestratorService`, `FileOperationService`.

14. **`fotix.ui.views.ResultsView`**
    *   **Descrição de Alto Nível Inicial:** Implementar a tela que apresenta os grupos de arquivos duplicados encontrados, permite revisão e confirma a remoção através do `FileOperationService`.
    *   **Justificativa da Ordem:** Permite ao usuário interagir com os resultados do escaneamento e acionar a remoção. Depende dos resultados do `ScanOrchestratorService` e interage com `FileOperationService`.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.application_services.FileOperationService`, dados do `ScanOrchestratorService`.

15. **`fotix.ui.views.RestoreView`**
    *   **Descrição de Alto Nível Inicial:** Implementar a tela que lista arquivos backupeados e permite ao usuário restaurá-los, interagindo com `RestoreOrchestratorService`.
    *   **Justificativa da Ordem:** Fornece a interface para a funcionalidade de restauração.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.application_services.RestoreOrchestratorService`.

16. **`fotix.ui.main_window.MainWindow`**
    *   **Descrição de Alto Nível Inicial:** Implementar a janela principal da aplicação que orquestra e integra todas as diferentes views (`ConfigView`, `ProgressView`, `ResultsView`, `RestoreView`) e menus.
    *   **Justificativa da Ordem:** É o contêiner principal da UI; implementá-la por último permite integrar as views já desenvolvidas.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.application_services.ScanOrchestratorService`, `fotix.application_services.FileOperationService`, `fotix.application_services.RestoreOrchestratorService`, e todas as Views.

17. **`fotix.ui.widgets`**
    *   **Descrição de Alto Nível Inicial:** Desenvolver componentes de UI reutilizáveis (ex: seletor de arquivos customizado, tabelas) conforme a necessidade das Views.
    *   **Justificativa da Ordem:** Estes são componentes de suporte para as Views. Devem ser implementados conforme as Views os exijam, podendo ser desenvolvidos iterativamente ao longo da implementação da UI.
    *   **Dependências Chave (Inferidas do Blueprint):** Nenhuma direta a outros módulos principais, mas são usados pelas Views.

---

**>>> PARADA PARA TESTES DE INTEGRAÇÃO (UI COM SERVIÇOS DE APLICAÇÃO - FLUXOS PRINCIPAIS) <<<**

*   **Módulos Implementados neste Grupo:**
    *   `fotix.ui.views.ConfigView`
    *   `fotix.ui.views.ProgressView`
    *   `fotix.ui.views.ResultsView`
    *   `fotix.ui.views.RestoreView`
    *   `fotix.ui.main_window.MainWindow`
    *   (Serviços de Aplicação já implementados e testados)
*   **Objetivo do Teste de Integração:** Validar que as principais Views da UI interagem corretamente com os respectivos Serviços de Aplicação, cobrindo os fluxos de usuário de ponta a ponta.
*   **Cenários Chave para Teste de Integração:**
    1.  **Fluxo de Escaneamento e Revisão:**
        *   Usar `ConfigView` para selecionar um diretório de teste (com duplicatas conhecidas).
        *   Iniciar o escaneamento e observar o `ProgressView`.
        *   Verificar se `ResultsView` exibe os duplicados corretamente.
    2.  **Fluxo de Remoção a partir da UI:**
        *   A partir dos resultados em `ResultsView`, selecionar arquivos para remoção.
        *   Confirmar a remoção e observar `ProgressView` (se aplicável para feedback da remoção).
        *   Verificar (manual ou programaticamente, se possível) que os arquivos foram "removidos" e backupeados.
    3.  **Fluxo de Restauração a partir da UI:**
        *   Usar `RestoreView` para listar os backups feitos no cenário anterior.
        *   Selecionar um item e restaurá-lo.
        *   Verificar se o arquivo foi restaurado para o local correto.
    4.  **Navegação e Orquestração pela MainWindow:** Verificar se a `MainWindow` gerencia corretamente a exibição e transição entre as diferentes views.
*   **Instrução para o Coordenador:** Use o `Prompt_IntegradorTester_vX.Y` (ou realize testes manuais guiados se a automação da UI for complexa neste estágio) para validar os fluxos principais da aplicação através da interface do usuário. Foque na correta passagem de dados e acionamento de ações entre UI e Camada de Aplicação.

---

18. **`fotix.main`** (Ponto de Entrada da Aplicação)
    *   **Descrição de Alto Nível Inicial:** Configurar e iniciar a aplicação PySide6, instanciar os serviços de aplicação (com suas dependências de infraestrutura injetadas), instanciar e exibir a `MainWindow`.
    *   **Justificativa da Ordem:** É o ponto de entrada da aplicação; implementá-lo após todos os componentes principais estarem prontos permite a correta inicialização e injeção de dependências.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.ui.main_window.MainWindow`, todos os serviços de aplicação e infraestrutura (para instanciação e injeção).