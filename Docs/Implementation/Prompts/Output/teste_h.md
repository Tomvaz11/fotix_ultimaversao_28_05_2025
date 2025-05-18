## Cenários de Teste de Aceitação do Usuário (UAT) / E2E para Fotix

Aqui estão os cenários de teste manuais para o Coordenador:

---

**ID do Cenário:** `UAT_FOTIX_001`
**Título do Cenário:** Scan de Diretório com Duplicatas Simples, Seleção Manual, Backup e Remoção para Lixeira
**Referência à Funcionalidade no Blueprint/Ordem:**
*   Blueprint: 1 (Visão Geral), 3.1 (UI), 3.2 (ScanService, DuplicateManagementService), 3.3 (DuplicateFinder, SelectionStrategy - manual implied), 3.4 (FileSystemService, BackupService), 4.1 (IFileSystemService), 4.4 (IBackupService), 4.5 (IDuplicateFinderService), 5 (Gerenciamento de Dados - Backups), 7.1 (Operações de Arquivo).
*   Ordem: Itens 7, 8, 9, 10, 12, 13.
**Objetivo do Teste:** Validar o fluxo completo de escaneamento de um diretório com arquivos duplicados simples, visualização dos resultados, seleção manual de um arquivo para manter, e a subsequente operação de backup e envio dos demais para a lixeira.
**Módulos/Funcionalidades Principais Envolvidas (Conforme Blueprint):**
*   `fotix.ui` (Interação do usuário)
*   `fotix.application.services.scan_service` (Orquestração do scan)
*   `fotix.application.services.duplicate_management_service` (Gerenciamento da remoção e backup)
*   `fotix.core.duplicate_finder` (Lógica de detecção)
*   `fotix.core.models` (FileInfo, DuplicateSet)
*   `fotix.infrastructure.file_system` (Operações de arquivo, lixeira)
*   `fotix.infrastructure.backup` (Criação de backup)
*   `fotix.config` (Caminho do backup)
**Pré-condições:**
1.  Aplicação Fotix instalada e executando.
2.  Um diretório de teste (`C:\Fotix_Test\UAT_001` ou similar) contendo:
    *   `imageA_original.jpg` (ex: 1MB, 1920x1080, data 01/01/2023)
    *   `imageA_copy.jpg` (cópia exata de `imageA_original.jpg`, data 02/01/2023)
    *   `photo_unique.png` (um arquivo diferente)
3.  O diretório de backup configurado no Fotix está acessível e vazio.
4.  A lixeira do sistema está vazia ou contém itens facilmente distinguíveis.
**Dados de Teste Sugeridos:** Conforme descrito nas pré-condições.
**Passos para Execução:**
1.  Inicie a aplicação Fotix.
2.  Na UI, selecione o diretório de teste (`C:\Fotix_Test\UAT_001`) para escaneamento.
3.  Inicie o processo de scan.
4.  Observe a UI para o progresso (se aplicável) e a exibição dos resultados.
5.  Nos resultados, localize o conjunto de duplicatas contendo `imageA_original.jpg` e `imageA_copy.jpg`.
6.  Dentro deste conjunto, selecione manualmente `imageA_original.jpg` como o arquivo a ser mantido. (A UI deve indicar qual será mantido e qual será removido).
7.  Inicie a ação para processar as duplicatas selecionadas (ex: botão "Remover Selecionadas com Backup").
8.  Confirme a ação na caixa de diálogo de confirmação, se houver.
9.  Após a conclusão da operação, verifique o diretório de teste (`C:\Fotix_Test\UAT_001`).
10. Verifique o diretório de backup configurado no Fotix.
11. Verifique a lixeira do sistema.
**Resultado Esperado:**
*   Passo 4: A UI deve exibir um conjunto de duplicatas contendo `imageA_original.jpg` e `imageA_copy.jpg`. O arquivo `photo_unique.png` não deve ser listado como parte de um conjunto de duplicatas.
*   Passo 6: A UI deve refletir que `imageA_original.jpg` está marcado para ser mantido e `imageA_copy.jpg` está marcado para remoção/backup.
*   Passo 8: A operação deve prosseguir.
*   Passo 9: No diretório `C:\Fotix_Test\UAT_001`, o arquivo `imageA_original.jpg` deve permanecer, e `imageA_copy.jpg` não deve mais existir. `photo_unique.png` deve permanecer.
*   Passo 10: O diretório de backup deve conter uma estrutura (ex: subdiretório com ID do backup) e dentro dela, uma cópia de `imageA_copy.jpg`. Deve haver metadados do backup (ex: arquivo JSON).
*   Passo 11: A lixeira do sistema deve conter `imageA_copy.jpg`.
**Critério de Passagem Geral:** O Fotix identificou corretamente as duplicatas, permitiu a seleção manual, o arquivo selecionado foi mantido, o outro foi copiado para o backup e movido para a lixeira, e a UI refletiu o estado corretamente.

---

**ID do Cenário:** `UAT_FOTIX_002`
**Título do Cenário:** Scan Incluindo Arquivos ZIP, Seleção Automática (Ex: Mais Recente), Backup e Remoção
**Referência à Funcionalidade no Blueprint/Ordem:**
*   Blueprint: 3.2 (ScanService - include_zips), 3.3 (SelectionStrategy - automática), 3.4 (ZipHandlerService), 4.2 (IZipHandlerService), 4.6 (ISelectionStrategy).
*   Ordem: Itens 4, 7, 8, 9, 10, 12, 13.
**Objetivo do Teste:** Validar a capacidade de escanear arquivos dentro de ZIPs, aplicar uma estratégia de seleção automática (ex: manter o arquivo mais recente), e processar com backup e remoção.
**Módulos/Funcionalidades Principais Envolvidas (Conforme Blueprint):**
*   `fotix.ui`
*   `fotix.application.services.scan_service`
*   `fotix.application.services.duplicate_management_service`
*   `fotix.core.duplicate_finder`
*   `fotix.core.selection_strategy` (implementação de "manter mais recente")
*   `fotix.infrastructure.zip_handler`
*   `fotix.infrastructure.file_system`
*   `fotix.infrastructure.backup`
**Pré-condições:**
1.  Aplicação Fotix instalada e executando.
2.  Um diretório de teste (`C:\Fotix_Test\UAT_002`) contendo:
    *   `document_v1.txt` (conteúdo: "Teste UAT002", data 01/01/2023)
    *   `archive.zip` contendo:
        *   `photos/document_v2.txt` (conteúdo: "Teste UAT002", data 02/01/2023)
        *   `other_file.dat`
3.  Opção de "incluir arquivos ZIP" está habilitada na UI (se for uma opção).
4.  Uma estratégia de seleção automática como "Manter o arquivo com data de modificação mais recente" está selecionada ou é o padrão.
5.  Diretório de backup e lixeira conforme UAT_FOTIX_001.
**Dados de Teste Sugeridos:** Conforme pré-condições. `document_v1.txt` e `archive.zip/photos/document_v2.txt` são duplicatas.
**Passos para Execução:**
1.  Inicie a aplicação Fotix.
2.  Configure/verifique se a opção de escanear ZIPs está ativa e a estratégia de seleção "manter mais recente" está selecionada.
3.  Selecione o diretório de teste (`C:\Fotix_Test\UAT_002`) para escaneamento.
4.  Inicie o processo de scan.
5.  Observe os resultados. O conjunto de duplicatas deve mostrar `document_v1.txt` e `archive.zip/photos/document_v2.txt`.
6.  Verifique se a UI (ou a lógica automática) pré-selecionou `archive.zip/photos/document_v2.txt` para ser mantido (pois é mais recente) e `document_v1.txt` para remoção.
7.  Inicie a ação para processar as duplicatas.
8.  Confirme a ação.
9.  Verifique o diretório de teste (`C:\Fotix_Test\UAT_002`).
10. Verifique o diretório de backup.
11. Verifique a lixeira.
**Resultado Esperado:**
*   Passo 5: A UI lista o conjunto de duplicatas {`document_v1.txt`, `archive.zip::photos/document_v2.txt`}.
*   Passo 6: `archive.zip::photos/document_v2.txt` (ou uma representação dele) está marcado para ser mantido; `document_v1.txt` está marcado para remoção.
*   Passo 9: Em `C:\Fotix_Test\UAT_002`, `document_v1.txt` não existe mais. O arquivo `archive.zip` permanece (a menos que a lógica seja para extrair e recriar, o que não está especificado; assume-se que o arquivo dentro do ZIP que é "mantido" significa que o ZIP não é alterado se o arquivo a ser mantido estiver nele).
*   Passo 10: O diretório de backup contém uma cópia de `document_v1.txt`.
*   Passo 11: A lixeira contém `document_v1.txt`.
**Critério de Passagem Geral:** Duplicatas entre arquivos soltos e arquivos dentro de ZIPs são encontradas, a estratégia automática seleciona corretamente, e o arquivo não selecionado é backupado e movido para lixeira.

---

**ID do Cenário:** `UAT_FOTIX_003`
**Título do Cenário:** Listagem de Backups Existentes e Restauração para Local Original
**Referência à Funcionalidade no Blueprint/Ordem:**
*   Blueprint: 3.2 (BackupRestoreService), 4.4 (IBackupService - list_backups, restore_backup).
*   Ordem: Item 11.
**Objetivo do Teste:** Validar a funcionalidade de listar backups previamente criados e restaurar um backup específico para seu local original.
**Módulos/Funcionalidades Principais Envolvidas (Conforme Blueprint):**
*   `fotix.ui` (Interface para listar e restaurar backups)
*   `fotix.application.services.backup_restore_service`
*   `fotix.infrastructure.backup`
*   `fotix.infrastructure.file_system`
**Pré-condições:**
1.  Aplicação Fotix instalada e executando.
2.  Um backup foi criado anteriormente (ex: pelo UAT_FOTIX_001, onde `imageA_copy.jpg` do diretório `C:\Fotix_Test\UAT_001` foi backupado).
3.  O arquivo `imageA_copy.jpg` não existe mais em `C:\Fotix_Test\UAT_001`.
4.  O diretório de backup contém o backup de `imageA_copy.jpg`.
**Dados de Teste Sugeridos:** Backup criado no UAT_FOTIX_001.
**Passos para Execução:**
1.  Inicie a aplicação Fotix.
2.  Navegue para a seção de gerenciamento de backups na UI.
3.  A UI deve listar os backups disponíveis, incluindo o backup de `imageA_copy.jpg` (identificado por ID, data, etc.).
4.  Selecione o backup correspondente a `imageA_copy.jpg`.
5.  Escolha a opção para restaurar para o local original.
6.  Confirme a ação de restauração.
7.  Após a conclusão, verifique o diretório `C:\Fotix_Test\UAT_001`.
8.  Verifique o diretório de backup (o backup em si deve permanecer, a menos que especificado o contrário).
**Resultado Esperado:**
*   Passo 3: A lista de backups na UI exibe informações sobre o backup de `imageA_copy.jpg`.
*   Passo 6: A operação de restauração é iniciada e concluída com sucesso.
*   Passo 7: O arquivo `imageA_copy.jpg` agora existe novamente em `C:\Fotix_Test\UAT_001` com seu conteúdo original.
*   Passo 8: O registro do backup e seus arquivos ainda existem no diretório de backup (restaurar não remove o backup).
**Critério de Passagem Geral:** A aplicação lista corretamente os backups, e a restauração para o local original recria o arquivo com sucesso.

---

**ID do Cenário:** `UAT_FOTIX_004`
**Título do Cenário:** Restauração de Backup para um Local Personalizado
**Referência à Funcionalidade no Blueprint/Ordem:**
*   Blueprint: 3.2 (BackupRestoreService), 4.4 (IBackupService - restore_backup com target_directory).
*   Ordem: Item 11.
**Objetivo do Teste:** Validar a funcionalidade de restaurar um backup para um diretório alvo especificado pelo usuário, diferente do original.
**Módulos/Funcionalidades Principais Envolvidas (Conforme Blueprint):**
*   `fotix.ui`
*   `fotix.application.services.backup_restore_service`
*   `fotix.infrastructure.backup`
*   `fotix.infrastructure.file_system`
**Pré-condições:**
1.  Mesmas pré-condições do UAT_FOTIX_003.
2.  Um diretório de destino para restauração existe e está vazio, ex: `C:\Fotix_Test\Restore_Target`.
**Dados de Teste Sugeridos:** Backup criado no UAT_FOTIX_001, diretório de destino `C:\Fotix_Test\Restore_Target`.
**Passos para Execução:**
1.  Inicie a aplicação Fotix.
2.  Navegue para a seção de gerenciamento de backups.
3.  Selecione o backup correspondente a `imageA_copy.jpg`.
4.  Escolha a opção para restaurar e especifique o diretório alvo como `C:\Fotix_Test\Restore_Target`.
5.  Confirme a ação de restauração.
6.  Após a conclusão, verifique o diretório `C:\Fotix_Test\Restore_Target`.
7.  Verifique o local original (`C:\Fotix_Test\UAT_001`) para garantir que o arquivo não foi restaurado lá.
**Resultado Esperado:**
*   Passo 5: A operação de restauração é concluída com sucesso.
*   Passo 6: O arquivo `imageA_copy.jpg` agora existe em `C:\Fotix_Test\Restore_Target`. Se o backup mantiver a estrutura de subdiretórios original, ela deve ser recriada dentro do diretório alvo.
*   Passo 7: O arquivo `imageA_copy.jpg` não existe em `C:\Fotix_Test\UAT_001`.
**Critério de Passagem Geral:** A restauração para um local personalizado copia o arquivo do backup para o novo diretório especificado.

---

**ID do Cenário:** `UAT_FOTIX_005`
**Título do Cenário:** Exclusão de um Backup Existente
**Referência à Funcionalidade no Blueprint/Ordem:**
*   Blueprint: 3.2 (BackupRestoreService), 4.4 (IBackupService - delete_backup).
*   Ordem: Item 11.
**Objetivo do Teste:** Validar a funcionalidade de remover permanentemente um backup do sistema.
**Módulos/Funcionalidades Principais Envolvidas (Conforme Blueprint):**
*   `fotix.ui`
*   `fotix.application.services.backup_restore_service`
*   `fotix.infrastructure.backup`
**Pré-condições:**
1.  Mesmas pré-condições do UAT_FOTIX_003 (um backup existe).
**Dados de Teste Sugeridos:** Backup criado no UAT_FOTIX_001.
**Passos para Execução:**
1.  Inicie a aplicação Fotix.
2.  Navegue para a seção de gerenciamento de backups.
3.  A UI lista o backup de `imageA_copy.jpg`.
4.  Selecione o backup correspondente a `imageA_copy.jpg`.
5.  Escolha a opção para excluir o backup.
6.  Confirme a ação de exclusão (esta ação deve ser claramente comunicada como permanente).
7.  Após a conclusão, atualize a lista de backups na UI.
8.  Verifique o diretório de backup no sistema de arquivos.
**Resultado Esperado:**
*   Passo 6: A operação de exclusão é concluída com sucesso.
*   Passo 7: O backup de `imageA_copy.jpg` não é mais listado na UI.
*   Passo 8: Os arquivos e metadados associados ao backup de `imageA_copy.jpg` foram removidos do diretório de backup.
**Critério de Passagem Geral:** O backup selecionado é removido da lista da UI e seus arquivos são deletados do sistema de armazenamento de backups.

---

**ID do Cenário:** `UAT_FOTIX_006`
**Título do Cenário:** Tentativa de Scan de Diretório Inválido ou Inacessível
**Referência à Funcionalidade no Blueprint/Ordem:**
*   Blueprint: 7.1 (Tratamento de Erros como `FileNotFoundError`, `PermissionError`), 7.2 (Validação de Entrada).
*   Ordem: Implícito na robustez dos serviços de sistema de arquivo e scan.
**Objetivo do Teste:** Validar o comportamento da aplicação ao tentar escanear um caminho de diretório que não existe ou para o qual não há permissão de leitura.
**Módulos/Funcionalidades Principais Envolvidas (Conforme Blueprint):**
*   `fotix.ui` (Captura de entrada, exibição de erro)
*   `fotix.application.services.scan_service` (ou validação na UI antes de chamar o serviço)
*   `fotix.infrastructure.file_system` (Tentativa de acesso ao caminho)
**Pré-condições:**
1.  Aplicação Fotix instalada e executando.
**Dados de Teste Sugeridos:**
*   Caminho inexistente: `C:\NaoExisteEsteDiretorio123`
*   Caminho inacessível: Um diretório do sistema para o qual o usuário atual não tem permissões de leitura (pode requerer configuração específica no SO para teste).
**Passos para Execução:**
1.  Inicie a aplicação Fotix.
2.  Na UI, tente selecionar ou digitar um caminho de diretório inexistente (ex: `C:\NaoExisteEsteDiretorio123`) para escaneamento.
3.  Tente iniciar o processo de scan.
4.  Observe a resposta da UI.
5.  (Opcional, se fácil de configurar) Repita os passos 2-4 com um caminho de diretório válido mas inacessível devido a permissões.
**Resultado Esperado:**
*   Passo 3/4: A aplicação deve lidar graciosamente com o erro. Idealmente:
    *   Uma mensagem de erro clara é exibida na UI informando que o caminho é inválido, não encontrado ou inacessível.
    *   A aplicação não deve travar ou apresentar comportamento inesperado.
    *   O processo de scan não deve ser iniciado efetivamente para o caminho inválido.
*   Logs da aplicação (se configurados para registrar erros) devem conter informações sobre a tentativa falha.
**Critério de Passagem Geral:** O Fotix impede o scan de caminhos inválidos/inacessíveis e informa o usuário sobre o problema de forma clara, sem travar.

---

**ID do Cenário:** `UAT_FOTIX_007`
**Título do Cenário:** Scan de Diretório Sem Duplicatas
**Referência à Funcionalidade no Blueprint/Ordem:**
*   Blueprint: Fluxo de scan normal.
*   Ordem: Item 9.
**Objetivo do Teste:** Validar que a aplicação se comporta corretamente e informa o usuário quando nenhum arquivo duplicado é encontrado em um scan.
**Módulos/Funcionalidades Principais Envolvidas (Conforme Blueprint):**
*   `fotix.ui`
*   `fotix.application.services.scan_service`
*   `fotix.core.duplicate_finder`
**Pré-condições:**
1.  Aplicação Fotix instalada e executando.
2.  Um diretório de teste (`C:\Fotix_Test\UAT_007`) contendo apenas arquivos únicos (ex: `unique1.txt`, `unique2.jpg`, `unique3.mp4`).
**Dados de Teste Sugeridos:** Conforme pré-condições.
**Passos para Execução:**
1.  Inicie a aplicação Fotix.
2.  Selecione o diretório de teste (`C:\Fotix_Test\UAT_007`) para escaneamento.
3.  Inicie o processo de scan.
4.  Observe a UI para o progresso e a exibição dos resultados.
**Resultado Esperado:**
*   Passo 4: A UI deve indicar que o scan foi concluído e que nenhum conjunto de duplicatas foi encontrado. Uma mensagem informativa clara deve ser exibida. A lista de duplicatas deve estar vazia.
**Critério de Passagem Geral:** O Fotix completa o scan e informa corretamente ao usuário que não foram encontradas duplicatas.

---

**ID do Cenário:** `UAT_FOTIX_008`
**Título do Cenário:** Scan com Filtro de Extensões de Arquivo (se suportado pela UI)
**Referência à Funcionalidade no Blueprint/Ordem:**
*   Blueprint: 4.1 (`IFileSystemService.list_directory_contents` com `file_extensions`), 4.2 (`IZipHandlerService.stream_zip_entries` com `file_extensions`). A UI precisaria expor essa opção.
*   Ordem: Assumindo que o `ScanService` pode passar esse filtro para os serviços de infraestrutura.
**Objetivo do Teste:** Validar que, se a UI permitir especificar extensões de arquivo, o scan considera apenas esses tipos de arquivo. (Se a UI não tiver essa opção, este teste pode ser adaptado para verificar o comportamento padrão de quais arquivos são escaneados).
**Módulos/Funcionalidades Principais Envolvidas (Conforme Blueprint):**
*   `fotix.ui` (Se houver campo para filtro de extensão)
*   `fotix.application.services.scan_service`
*   `fotix.core.duplicate_finder`
*   `fotix.infrastructure.file_system`
*   `fotix.infrastructure.zip_handler`
**Pré-condições:**
1.  Aplicação Fotix instalada e executando.
2.  Um diretório de teste (`C:\Fotix_Test\UAT_008`) contendo:
    *   `image_dup1.jpg`
    *   `image_dup2.jpg` (duplicata de `image_dup1.jpg`)
    *   `document_dup1.txt`
    *   `document_dup2.txt` (duplicata de `document_dup1.txt`)
    *   `video_unique.mp4`
**Dados de Teste Sugeridos:** Conforme pré-condições.
**Passos para Execução:**
1.  Inicie a aplicação Fotix.
2.  Configure o filtro de extensões para incluir apenas `.jpg` (se a UI permitir). Se não, observe o comportamento padrão.
3.  Selecione o diretório de teste (`C:\Fotix_Test\UAT_008`) para escaneamento.
4.  Inicie o processo de scan.
5.  Observe os resultados.
6.  (Se a UI permitir) Repita os passos 2-5, mas com o filtro para incluir apenas `.txt`.
**Resultado Esperado:**
*   Passo 5 (filtro `.jpg`): A UI deve listar apenas o conjunto de duplicatas {`image_dup1.jpg`, `image_dup2.jpg`}. As duplicatas de `.txt` não devem ser mostradas.
*   Passo 6 (filtro `.txt`): A UI deve listar apenas o conjunto de duplicatas {`document_dup1.txt`, `document_dup2.txt`}. As duplicatas de `.jpg` não devem ser mostradas.
*   Se não houver filtro na UI, o resultado esperado é que AMBOS os conjuntos de duplicatas (`.jpg` e `.txt`) sejam encontrados se o comportamento padrão for escanear todos os tipos de arquivo para os quais o hashing é aplicável.
**Critério de Passagem Geral:** O Fotix respeita o filtro de extensão (se aplicável via UI) ou demonstra um comportamento de escaneamento padrão consistente para diferentes tipos de arquivo.

---

**ID do Cenário:** `UAT_FOTIX_009`
**Título do Cenário:** Processamento de Duplicatas onde um Arquivo está Solto e Outro em um ZIP
**Referência à Funcionalidade no Blueprint/Ordem:**
*   Blueprint: Cenário de scan e gerenciamento envolvendo ZIPs.
*   Ordem: Itens 4, 7, 8, 9, 10.
**Objetivo do Teste:** Especificamente testar a identificação e o gerenciamento de um conjunto de duplicatas onde um arquivo está no sistema de arquivos diretamente e sua duplicata está dentro de um arquivo ZIP.
**Módulos/Funcionalidades Principais Envolvidas (Conforme Blueprint):**
*   Todos os módulos envolvidos no scan, identificação, seleção e processamento de duplicatas, incluindo `ZipHandlerService`.
**Pré-condições:**
1.  Aplicação Fotix instalada e executando.
2.  Um diretório de teste (`C:\Fotix_Test\UAT_009`) contendo:
    *   `config_file.ini` (data 01/01/2023)
    *   `backup_archive.zip` contendo `settings/config_file.ini` (duplicata do arquivo solto, data 02/01/2023)
3.  Estratégia de seleção "manter mais recente" selecionada.
**Dados de Teste Sugeridos:** Conforme pré-condições.
**Passos para Execução:**
1.  Inicie a aplicação Fotix.
2.  Verifique se a opção de escanear ZIPs está ativa.
3.  Selecione o diretório de teste (`C:\Fotix_Test\UAT_009`).
4.  Inicie o scan.
5.  Nos resultados, verifique o conjunto de duplicatas {`config_file.ini`, `backup_archive.zip::settings/config_file.ini`}.
6.  Verifique se `backup_archive.zip::settings/config_file.ini` está pré-selecionado para ser mantido (devido à data mais recente).
7.  Inicie a ação para processar as duplicatas.
8.  Confirme.
9.  Verifique o diretório `C:\Fotix_Test\UAT_009`, o diretório de backup e a lixeira.
**Resultado Esperado:**
*   Passo 5: O conjunto de duplicatas é corretamente identificado.
*   Passo 6: O arquivo dentro do ZIP é selecionado para ser mantido.
*   Passo 9:
    *   `C:\Fotix_Test\UAT_009`: `config_file.ini` (solto) não existe mais. `backup_archive.zip` ainda existe.
    *   Diretório de Backup: Contém uma cópia de `config_file.ini` (solto).
    *   Lixeira: Contém `config_file.ini` (solto).
**Critério de Passagem Geral:** O sistema lida corretamente com duplicatas跨filesystem/ZIP, aplicando a estratégia e processando os arquivos conforme esperado.

---

**ID do Cenário:** `UAT_FOTIX_010`
**Título do Cenário:** Teste de Estratégia de Seleção: Manter Arquivo com Nome Mais Curto (ou outro critério específico)
**Referência à Funcionalidade no Blueprint/Ordem:**
*   Blueprint: 3.3 (`selection_strategy` - por nome), 4.6 (`ISelectionStrategy`).
*   Ordem: Item 8, 10.
**Objetivo do Teste:** Validar uma estratégia de seleção específica baseada em critério de nome (ex: "manter nome mais curto", ou "manter nome alfabeticamente primeiro" se for uma opção clara).
**Módulos/Funcionalidades Principais Envolvidas (Conforme Blueprint):**
*   `fotix.ui` (para selecionar a estratégia, se aplicável, e visualizar seleção)
*   `fotix.application.services.duplicate_management_service`
*   `fotix.core.selection_strategy` (implementação da estratégia de nome)
**Pré-condições:**
1.  Aplicação Fotix instalada e executando.
2.  Um diretório de teste (`C:\Fotix_Test\UAT_010`) contendo:
    *   `photo_album_cover.jpg`
    *   `photo.jpg` (duplicata de `photo_album_cover.jpg`)
    *   `img_final_version.jpg` (duplicata de `photo_album_cover.jpg`)
    (Todos com mesmo conteúdo, tamanho, e data para isolar o critério do nome).
3.  A estratégia de seleção "Manter arquivo com nome mais curto" (ou similar baseado em nome) está disponível e selecionada na UI.
**Dados de Teste Sugeridos:** Conforme pré-condições.
**Passos para Execução:**
1.  Inicie a aplicação Fotix.
2.  Selecione a estratégia de seleção "Manter nome mais curto" (ou o critério de nome específico sendo testado).
3.  Selecione o diretório de teste (`C:\Fotix_Test\UAT_010`) para escaneamento.
4.  Inicie o scan.
5.  Nos resultados, localize o conjunto de duplicatas {`photo_album_cover.jpg`, `photo.jpg`, `img_final_version.jpg`}.
6.  Verifique se a UI (ou a lógica automática) pré-selecionou `photo.jpg` para ser mantido.
7.  Inicie a ação para processar as duplicatas.
8.  Confirme.
9.  Verifique o diretório de teste, o diretório de backup e a lixeira.
**Resultado Esperado:**
*   Passo 6: `photo.jpg` está marcado para ser mantido. Os outros dois estão marcados para remoção.
*   Passo 9:
    *   `C:\Fotix_Test\UAT_010`: Apenas `photo.jpg` permanece.
    *   Diretório de Backup: Contém cópias de `photo_album_cover.jpg` e `img_final_version.jpg`.
    *   Lixeira: Contém `photo_album_cover.jpg` e `img_final_version.jpg`.
**Critério de Passagem Geral:** A estratégia de seleção baseada no nome do arquivo é aplicada corretamente, e os arquivos são processados conforme a seleção.

---

**ID do Cenário:** `UAT_FOTIX_011`
**Título do Cenário:** Configuração do Caminho de Backup e Verificação de Uso
**Referência à Funcionalidade no Blueprint/Ordem:**
*   Blueprint: 3.6 (`fotix.config`), 5 (Persistência - Configurações, Backups).
*   Ordem: Item 1, usado pelo item 6 (BackupService).
**Objetivo do Teste:** Validar que o usuário pode configurar o caminho do diretório de backup e que a aplicação utiliza esse caminho configurado ao criar backups.
**Módulos/Funcionalidades Principais Envolvidas (Conforme Blueprint):**
*   `fotix.ui` (Interface para alterar configurações, se houver)
*   `fotix.config` (Carregamento e fornecimento da configuração)
*   `fotix.infrastructure.backup` (Uso do caminho configurado)
**Pré-condições:**
1.  Aplicação Fotix instalada e executando.
2.  Um novo diretório vazio existe, ex: `D:\Meus_Backups_Fotix`, que será o novo caminho de backup.
3.  Um diretório de teste com duplicatas simples, ex: `C:\Fotix_Test\UAT_011_Scan` com `file1.txt` e `file2.txt` (duplicatas).
**Dados de Teste Sugeridos:** Novo caminho `D:\Meus_Backups_Fotix`. Diretório de scan `C:\Fotix_Test\UAT_011_Scan`.
**Passos para Execução:**
1.  Inicie a aplicação Fotix.
2.  Acesse a seção de configurações da aplicação (se houver uma UI para isso; caso contrário, isso pode envolver a edição manual de um arquivo de configuração antes de iniciar o Fotix, conforme especificado pela aplicação).
3.  Altere o caminho do diretório de backup para `D:\Meus_Backups_Fotix`. Salve as configurações. (Se for edição manual, reinicie o Fotix se necessário).
4.  Selecione o diretório `C:\Fotix_Test\UAT_011_Scan` para escaneamento.
5.  Inicie o scan.
6.  No conjunto de duplicatas {`file1.txt`, `file2.txt`}, selecione `file1.txt` para manter e `file2.txt` para remover/backup.
7.  Inicie a ação para processar. Confirme.
8.  Após a conclusão, verifique o diretório `D:\Meus_Backups_Fotix`.
9.  Verifique também o antigo/padrão diretório de backup para garantir que não foi usado.
**Resultado Esperado:**
*   Passo 3: A configuração do caminho de backup é atualizada com sucesso.
*   Passo 8: O diretório `D:\Meus_Backups_Fotix` contém o backup de `file2.txt`.
*   Passo 9: O diretório de backup anterior/padrão não contém o backup de `file2.txt` desta operação.
**Critério de Passagem Geral:** A aplicação utiliza o caminho de backup configurado pelo usuário para armazenar os arquivos de backup.

---

**ID do Cenário:** `UAT_FOTIX_012`
**Título do Cenário:** Indicação de Progresso Durante Scan Demorado
**Referência à Funcionalidade no Blueprint/Ordem:**
*   Blueprint: 3.1 (UI - exibir progresso), 4.5 (`IDuplicateFinderService` - `progress_callback`).
*   Ordem: Item 7, 9.
**Objetivo do Teste:** Validar que a UI exibe alguma forma de indicação de progresso durante operações potencialmente longas, como o scan de um diretório grande.
**Módulos/Funcionalidades Principais Envolvidas (Conforme Blueprint):**
*   `fotix.ui` (Exibição de progresso)
*   `fotix.application.services.scan_service` (Coordenação e repasse do callback)
*   `fotix.core.duplicate_finder` (Chamada do callback de progresso)
**Pré-condições:**
1.  Aplicação Fotix instalada e executando.
2.  Um diretório de teste (`C:\Fotix_Test\UAT_012_LargeScan`) contendo um número significativo de arquivos e subdiretórios (ex: centenas ou milhares de arquivos pequenos, alguns ZIPs) para simular um scan demorado.
**Dados de Teste Sugeridos:** Diretório grande e/ou com muitos arquivos.
**Passos para Execução:**
1.  Inicie a aplicação Fotix.
2.  Selecione o diretório de teste (`C:\Fotix_Test\UAT_012_LargeScan`) para escaneamento.
3.  Inicie o processo de scan.
4.  Observe atentamente a UI durante o processo de scan.
**Resultado Esperado:**
*   Passo 4: A UI deve fornecer feedback visual de que o scan está em andamento. Isso pode ser uma barra de progresso, uma porcentagem de conclusão, uma mensagem "Escaneando arquivo X de Y", um ícone animado, ou similar. O feedback deve ser atualizado periodicamente. A UI não deve parecer "congelada".
*   Ao final, o resultado do scan (duplicatas encontradas ou mensagem de "nenhuma duplicata") deve ser exibido.
**Critério de Passagem Geral:** A aplicação fornece feedback de progresso adequado ao usuário durante operações demoradas, mantendo a UI responsiva.