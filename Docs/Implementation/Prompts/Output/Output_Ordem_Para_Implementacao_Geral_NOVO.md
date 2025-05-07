## Análise de Implementação e Próximos Passos para Fotix

**Instruções para o Coordenador:**

Este documento organiza os módulos do projeto Fotix para guiar a implementação. Ele separa os "Módulos Base" (definições, utilitários e interfaces) dos "Módulos Principais" (que contêm a lógica central e as implementações concretas dos serviços).

*   **NÃO implemente os "Módulos Base" listados abaixo diretamente agora.** Suas pastas e arquivos básicos (como `__init__.py`, arquivos de interfaces, modelos de dados) serão criados ou modificados quando necessário pela IA (`ImplementadorMestre`) durante a implementação dos módulos principais que dependem deles. O conteúdo específico de módulos como `fotix.utils` será adicionado organicamente conforme a necessidade surgir.
*   **SIGA a "Ordem de Implementação Sugerida (Módulos Principais e Pontos de Teste de Integração)" abaixo.** Comece pelo **Item #1** da lista de Módulos Principais e prossiga sequencialmente.
*   Para **CADA item** da ordem numerada de Módulo Principal, use o `Prompt_ImplementadorMestre_vX.Y` (recomenda-se a versão mais recente, ex: v1.7+), preenchendo apenas o nome do módulo alvo (ex: "Item 1: `fotix.config`"). Anexe sempre o `@Blueprint_Arquitetural.md`, este arquivo (`@Ordem_Com_Descricoes_e_Testes_Integracao.md`) e o código relevante já existente como contexto. A "Descrição de Alto Nível Inicial" listada abaixo para cada item servirá como ponto de partida para a IA.
*   **PONTOS DE TESTE DE INTEGRAÇÃO:** Em certos pontos, este documento indicará uma **">>> PARADA PARA TESTES DE INTEGRAÇÃO (Nome do Subsistema) <<<"**. Nestes momentos, **antes de prosseguir** com o próximo Módulo Principal da lista, você deverá usar um prompt dedicado para testes de integração (ex: `Prompt_IntegradorTester_vX.Y`, que será definido posteriormente) para guiar a IA na criação e execução de testes de integração para o grupo de módulos recém-concluído. Utilize os "Cenários Chave para Teste de Integração" listados como ponto de partida para esses testes. Após os testes de integração serem concluídos e validados, você poderá prosseguir para o próximo item da ordem de implementação.

---

### Módulos Base (Estrutura Inicial / Conteúdo On-Demand)

*   **`fotix.core.models`**: Define as estruturas de dados centrais do domínio (`FileInfo`, `DuplicateSet`, etc.) usando `dataclasses` ou `Pydantic`.
*   **`fotix.utils`** (e `fotix.utils.helpers`): Contém funções auxiliares, constantes e utilitários genéricos usados em múltiplas camadas.
*   **`fotix.infrastructure.interfaces`**: Define os contratos (interfaces) para os serviços da camada de infraestrutura (ex: `IFileSystemService`, `IConcurrencyService`, `IBackupService`, `IZipHandlerService`).
*   **`fotix.core.interfaces`**: Define os contratos (interfaces) para os serviços da camada de core/domínio (ex: `IDuplicateFinderService`, `ISelectionStrategy`).
*   **`fotix.application.interfaces`**: Define interfaces expostas pela camada de Aplicação para a UI (se houver). (Nota: O blueprint menciona `fotix.application.interfaces` como dependência da UI, mas não detalha seu conteúdo. Será criado/povoado conforme a necessidade da UI e dos serviços de aplicação).

---

### Ordem de Implementação Sugerida (Módulos Principais e Pontos de Teste de Integração) - COMECE AQUI (Item #1)

1.  **`fotix.config`**
    *   **Descrição de Alto Nível Inicial:** Carregar e fornecer acesso a configurações da aplicação, como caminhos de backup e níveis de log.
    *   **Justificativa da Ordem:** Muitas outras partes do sistema, especialmente logging e serviços de infraestrutura, dependerão de configurações. Implementar isso primeiro garante que as configurações estejam disponíveis.
    *   **Dependências Chave (Inferidas do Blueprint):** Nenhuma dependência interna de outros módulos `fotix`.

2.  **`fotix.infrastructure.logging_config`**
    *   **Descrição de Alto Nível Inicial:** Configurar o sistema de logging padrão do Python para a aplicação Fotix, permitindo registro de eventos e erros.
    *   **Justificativa da Ordem:** Essencial para depuração e monitoramento desde as primeiras etapas de desenvolvimento de outros módulos.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.config` (para níveis de log, formatos, etc.).

3.  **`fotix.infrastructure.file_system`**
    *   **Descrição de Alto Nível Inicial:** Implementar a interface `IFileSystemService` para abstrair operações no sistema de arquivos, como leitura, escrita, movimentação para lixeira e listagem de diretórios.
    *   **Justificativa da Ordem:** É uma dependência fundamental para muitos outros serviços de infraestrutura e para a lógica de core que lida com arquivos.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.infrastructure.interfaces.IFileSystemService` (para definição do contrato), `fotix.utils` (potencialmente para helpers).

---

**>>> PARADA PARA TESTES DE INTEGRAÇÃO (INFRAESTRUTURA BÁSICA: CONFIGURAÇÃO, LOG E ARQUIVOS) <<<**

*   **Módulos Implementados neste Grupo:** `fotix.config`, `fotix.infrastructure.logging_config`, `fotix.infrastructure.file_system` (e seus módulos base associados como `fotix.infrastructure.interfaces`).
*   **Objetivo do Teste de Integração:** Verificar se as configurações são carregadas corretamente, se o logging funciona conforme configurado, e se o `FileSystemService` interage com o sistema de arquivos de forma esperada, logando suas operações.
*   **Cenários Chave para Teste de Integração:**
    1.  **Carregamento de Configuração e Logging:** Crie um arquivo de configuração simples, carregue-o com `fotix.config`, use uma configuração para definir o nível de log em `fotix.infrastructure.logging_config`, e verifique se uma mensagem de log de teste é emitida (ou não) de acordo com o nível.
    2.  **Operações do FileSystemService com Logging:** Use `FileSystemService` para criar um arquivo/diretório temporário, listar seu conteúdo, obter tamanho/datas e movê-lo para a lixeira. Verifique se as operações são bem-sucedidas e se os logs correspondentes (INFO, DEBUG) são gerados.
    3.  **Tratamento de Erro no FileSystemService com Logging:** Tente uma operação inválida no `FileSystemService` (ex: acessar um arquivo inexistente) e verifique se a exceção apropriada é levantada e se um log de ERRO é gerado.
*   **Instrução para o Coordenador:** Use o `Prompt_IntegradorTester_vX.Y` (a ser definido) para gerar testes para estes cenários. Após os testes passarem e serem validados, prossiga para o próximo item da ordem de implementação.

---

4.  **`fotix.infrastructure.zip_handler`**
    *   **Descrição de Alto Nível Inicial:** Implementar a interface `IZipHandlerService` para permitir a leitura de arquivos dentro de arquivos ZIP de forma eficiente (streaming).
    *   **Justificativa da Ordem:** Necessário para a funcionalidade de busca de duplicatas que precisa inspecionar o conteúdo de arquivos ZIP. Depende de conceitos de IO já estabelecidos.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.infrastructure.interfaces.IZipHandlerService`.

5.  **`fotix.infrastructure.concurrency`**
    *   **Descrição de Alto Nível Inicial:** Implementar a interface `IConcurrencyService` para gerenciar a execução de tarefas concorrentes/paralelas, utilizando `concurrent.futures`.
    *   **Justificativa da Ordem:** Será utilizado pelo `ScanService` para otimizar a varredura e processamento de arquivos. É um componente de infraestrutura genérico.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.infrastructure.interfaces.IConcurrencyService`.

6.  **`fotix.infrastructure.backup`**
    *   **Descrição de Alto Nível Inicial:** Implementar a interface `IBackupService` para gerenciar a criação, listagem, restauração e exclusão de backups de arquivos.
    *   **Justificativa da Ordem:** Depende do `FileSystemService` para as operações de cópia e pode ser necessário para a gestão de duplicatas.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.infrastructure.interfaces.IBackupService`, `fotix.infrastructure.interfaces.IFileSystemService` (via injeção), `fotix.core.models.FileInfo` (para metadados), `fotix.config` (para caminho de backup).

---

**>>> PARADA PARA TESTES DE INTEGRAÇÃO (INFRAESTRUTURA AVANÇADA: ZIP, CONCORRÊNCIA E BACKUP) <<<**

*   **Módulos Implementados neste Grupo:** `fotix.infrastructure.zip_handler`, `fotix.infrastructure.concurrency`, `fotix.infrastructure.backup` (e seus módulos base associados).
*   **Objetivo do Teste de Integração:** Validar que os serviços de manipulação de ZIPs, execução concorrente e gerenciamento de backups funcionam corretamente e interagem adequadamente com os serviços de infraestrutura base (FileSystem).
*   **Cenários Chave para Teste de Integração:**
    1.  **Leitura de ZIP com ZipHandlerService:** Crie um arquivo ZIP de teste com alguns arquivos dentro. Use o `ZipHandlerService` para listar e extrair (via stream) o conteúdo de um dos arquivos, verificando nome, tamanho e conteúdo.
    2.  **Execução Concorrente com ConcurrencyService:** Crie algumas tarefas simples (ex: funções que dormem por um curto período e retornam um valor) e execute-as usando o `ConcurrencyService`. Verifique se são executadas (potencialmente em paralelo) e se os resultados são retornados corretamente.
    3.  **Ciclo de Vida do Backup com BackupService:** Use o `BackupService` para criar um backup de alguns arquivos de teste (utilizando `FileSystemService` para criar os arquivos originais). Liste os backups, restaure um deles (para local original ou novo) e verifique a integridade dos arquivos restaurados. Finalmente, delete o backup.
    4.  **BackupService interagindo com FileSystemService e Logging:** Certifique-se que as operações do `BackupService` (criar, restaurar) utilizam o `FileSystemService` subjacente e que essas ações são devidamente logadas.
*   **Instrução para o Coordenador:** Use o `Prompt_IntegradorTester_vX.Y` (a ser definido) para gerar testes para estes cenários. Após os testes passarem e serem validados, prossiga para o próximo item da ordem de implementação.

---

7.  **`fotix.core.duplicate_finder`**
    *   **Descrição de Alto Nível Inicial:** Implementar a lógica central de detecção de duplicatas, incluindo hashing de arquivos (BLAKE3) e comparação, utilizando abstrações para acesso a arquivos.
    *   **Justificativa da Ordem:** É o coração da funcionalidade principal. Depende das interfaces de infraestrutura para acesso a arquivos (normais e ZIP) e dos modelos de dados.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.core.interfaces.IDuplicateFinderService` (para definição do contrato), `fotix.core.models`, `fotix.infrastructure.interfaces.IFileSystemService`, `fotix.infrastructure.interfaces.IZipHandlerService`, `fotix.utils`.

8.  **`fotix.core.selection_strategy`**
    *   **Descrição de Alto Nível Inicial:** Implementar diferentes estratégias para selecionar automaticamente qual arquivo manter de um conjunto de duplicatas, com base em critérios como data, resolução ou nome.
    *   **Justificativa da Ordem:** Complementa o `duplicate_finder` ao fornecer a lógica para resolver os conjuntos de duplicatas encontrados.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.core.interfaces.ISelectionStrategy` (para definição do contrato), `fotix.core.models`.

---

**>>> PARADA PARA TESTES DE INTEGRAÇÃO (LÓGICA DE DOMÍNIO - CORE) <<<**

*   **Módulos Implementados neste Grupo:** `fotix.core.duplicate_finder`, `fotix.core.selection_strategy` (e seus módulos base associados como `fotix.core.models`, `fotix.core.interfaces`).
*   **Objetivo do Teste de Integração:** Garantir que a lógica de detecção de duplicatas e as estratégias de seleção funcionam corretamente, utilizando implementações mock ou stubs dos serviços de infraestrutura (`IFileSystemService`, `IZipHandlerService`).
*   **Cenários Chave para Teste de Integração:**
    1.  **Detecção de Duplicatas (Arquivos Simples):** Crie um cenário com alguns arquivos duplicados e alguns únicos em uma estrutura de diretório simulada (usando mocks para `IFileSystemService`). Execute `IDuplicateFinderService.find_duplicates` e verifique se os `DuplicateSet`s corretos são retornados.
    2.  **Detecção de Duplicatas (Incluindo ZIPs):** Similar ao anterior, mas inclua arquivos duplicados dentro de um arquivo ZIP simulado (usando mocks para `IZipHandlerService` e `IFileSystemService`). Verifique se duplicatas entre arquivos normais e arquivos em ZIPs são encontradas.
    3.  **Aplicação de SelectionStrategy:** Crie um `DuplicateSet` de teste com `FileInfo`s variados (diferentes datas, nomes). Instancie uma `ISelectionStrategy` específica e chame `select_file_to_keep`, verificando se o arquivo correto é escolhido com base nos critérios da estratégia.
    4.  **Progresso do DuplicateFinder:** Se `progress_callback` for implementado no `IDuplicateFinderService`, teste se ele é chamado apropriadamente durante uma operação de busca de duplicatas simulada.
*   **Instrução para o Coordenador:** Use o `Prompt_IntegradorTester_vX.Y` (a ser definido) para gerar testes para estes cenários, focando em mocks para as dependências de infraestrutura. Após os testes passarem e serem validados, prossiga para o próximo item da ordem de implementação.

---

9.  **`fotix.application.services.scan_service`**
    *   **Descrição de Alto Nível Inicial:** Orquestrar o processo de varredura de diretórios e ZIPs, utilizando os serviços de concorrência, sistema de arquivos, manipulador de ZIP e o buscador de duplicatas do core.
    *   **Justificativa da Ordem:** Combina vários serviços de infraestrutura e o `duplicate_finder` do core para realizar uma funcionalidade chave da aplicação.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.core.interfaces.IDuplicateFinderService`, `fotix.infrastructure.interfaces.IConcurrencyService`, `fotix.infrastructure.interfaces.IFileSystemService`, `fotix.infrastructure.interfaces.IZipHandlerService`.

10. **`fotix.application.services.duplicate_management_service`**
    *   **Descrição de Alto Nível Inicial:** Gerenciar a seleção do arquivo a ser mantido (usando `SelectionStrategy`), a remoção segura (usando `FileSystemService`) e o backup (usando `BackupService`).
    *   **Justificativa da Ordem:** Lida com as ações subsequentes à descoberta de duplicatas, utilizando as estratégias do core e os serviços de infraestrutura.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.core.interfaces.ISelectionStrategy`, `fotix.infrastructure.interfaces.IFileSystemService`, `fotix.infrastructure.interfaces.IBackupService`.

11. **`fotix.application.services.backup_restore_service`**
    *   **Descrição de Alto Nível Inicial:** Gerenciar a listagem e restauração de backups, utilizando os serviços de backup e sistema de arquivos da infraestrutura.
    *   **Justificativa da Ordem:** Fornece a funcionalidade de recuperação, completando o ciclo de gerenciamento de arquivos.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.infrastructure.interfaces.IBackupService`, `fotix.infrastructure.interfaces.IFileSystemService`.

---

**>>> PARADA PARA TESTES DE INTEGRAÇÃO (CAMADA DE APLICAÇÃO - LÓGICA DE ORQUESTRAÇÃO) <<<**

*   **Módulos Implementados neste Grupo:** `fotix.application.services.scan_service`, `fotix.application.services.duplicate_management_service`, `fotix.application.services.backup_restore_service` (e seus módulos base associados).
*   **Objetivo do Teste de Integração:** Verificar se os serviços da camada de aplicação orquestram corretamente os serviços do core e da infraestrutura para executar os casos de uso completos (ainda sem UI). Utilizar implementações reais dos serviços de infraestrutura e core já testados.
*   **Cenários Chave para Teste de Integração:**
    1.  **Fluxo Completo de Scan e Identificação:** Use `ScanService` para escanear um diretório de teste (com arquivos e ZIPs contendo duplicatas). Verifique se o serviço retorna os `DuplicateSet`s esperados, utilizando as implementações reais de `DuplicateFinder`, `FileSystemService`, `ZipHandlerService` e `ConcurrencyService`.
    2.  **Fluxo de Gerenciamento de Duplicata (Seleção e Remoção com Backup):** Pegue um `DuplicateSet` do cenário anterior. Use `DuplicateManagementService` para aplicar uma `SelectionStrategy`, identificar o arquivo a ser removido, fazer o backup (verificando com `BackupService`) e mover o arquivo para a lixeira (verificando com `FileSystemService`).
    3.  **Fluxo de Restauração de Backup:** Use `BackupRestoreService` para listar os backups criados no cenário anterior. Restaure um backup específico e verifique se os arquivos são restaurados corretamente em seus locais originais ou em um novo local.
    4.  **Interação entre Scan e Management Services:** Simule um fluxo onde o `ScanService` encontra duplicatas, e então o `DuplicateManagementService` processa um desses conjuntos.
*   **Instrução para o Coordenador:** Use o `Prompt_IntegradorTester_vX.Y` (a ser definido) para gerar testes para estes cenários, utilizando as implementações reais dos módulos das camadas inferiores. Após os testes passarem e serem validados, prossiga para o próximo item da ordem de implementação.

---

12. **`fotix.ui`** (Componentes principais, ex: `fotix.ui.main_window`)
    *   **Descrição de Alto Nível Inicial:** Implementar a interface gráfica do usuário (GUI) com PySide6, permitindo interação do usuário para selecionar diretórios, visualizar duplicatas, confirmar ações e ver progresso.
    *   **Justificativa da Ordem:** A UI é a camada mais externa e depende dos serviços da camada de aplicação para funcionar.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.application.interfaces` (ou diretamente os serviços de aplicação), `fotix.core.models` (para exibir dados).

13. **`fotix.main`**
    *   **Descrição de Alto Nível Inicial:** Ponto de entrada da aplicação. Responsável por inicializar as camadas da aplicação, configurar a UI principal e iniciar o loop de eventos da GUI.
    *   **Justificativa da Ordem:** É o último componente que une todas as partes da aplicação.
    *   **Dependências Chave (Inferidas do Blueprint):** `fotix.ui`, `fotix.application` (para inicialização dos serviços).

---

**>>> PARADA PARA TESTES DE INTEGRAÇÃO (INTEGRAÇÃO UI-APLICAÇÃO) <<<**

*   **Módulos Implementados neste Grupo:** `fotix.ui` (componentes principais), `fotix.main`.
*   **Objetivo do Teste de Integração:** Validar a comunicação e o fluxo de dados entre a Camada de Apresentação (UI) e a Camada de Aplicação. Garantir que as ações do usuário na UI disparem corretamente os serviços de aplicação e que os resultados/atualizações sejam refletidos na UI.
*   **Cenários Chave para Teste de Integração:** (Estes podem requerer ferramentas de teste de UI ou abordagens de simulação de eventos de UI)
    1.  **Scan a partir da UI:** Simule a seleção de um diretório na UI e o início de um scan. Verifique se o `ScanService` na camada de aplicação é invocado com os parâmetros corretos e se a UI exibe informações de progresso (se aplicável) e, eventualmente, os resultados (lista de duplicatas).
    2.  **Seleção e Remoção de Duplicata via UI:** A partir de uma lista de duplicatas exibida na UI, simule a seleção de um arquivo para manter e a confirmação para remover os outros. Verifique se o `DuplicateManagementService` é chamado, se o backup ocorre e se o arquivo é movido para a lixeira, com a UI atualizando seu estado.
    3.  **Restauração de Backup via UI:** Simule a navegação pela lista de backups na UI, a seleção de um backup e o acionamento da restauração. Verifique se o `BackupRestoreService` é invocado e se a UI reflete o sucesso ou falha da operação.
    4.  **Exibição de Dados do Core na UI:** Certifique-se de que os `FileInfo` e `DuplicateSet` (de `fotix.core.models`) são corretamente formatados e exibidos nos componentes apropriados da UI.
*   **Instrução para o Coordenador:** Use o `Prompt_IntegradorTester_vX.Y` (a ser definido), possivelmente em conjunto com prompts específicos para testes de UI (se disponíveis), para gerar testes para estes cenários. Estes testes podem ser mais complexos e podem envolver o uso de mocks para partes da UI ou simulação de interações. Após os testes passarem e serem validados, a implementação inicial dos principais componentes estará concluída.