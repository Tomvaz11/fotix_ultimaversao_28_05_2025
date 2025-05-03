**Especificação da Funcionalidade/Módulo a ser Implementada:**

**1. Módulo Alvo:**
   `fotix/src/fotix/core/decision_logic.py`

**2. Função Alvo:**
   `decide_file_to_keep(group: DuplicateGroup) -> FileMetadata`

**3. Descrição Geral:**
   Implementar a lógica de decisão para selecionar um único arquivo `FileMetadata` a ser mantido dentro de um `DuplicateGroup`, que contém uma lista de arquivos duplicados (`FileMetadata`). A seleção deve seguir uma hierarquia de critérios: maior resolução, data de modificação mais recente e nome de arquivo mais curto. A função deve operar de forma pura, sem efeitos colaterais (como I/O ou modificação do estado global) e basear-se apenas nos dados fornecidos no `DuplicateGroup`.

**4. Inputs:**
   - `group`: Uma instância da classe `DuplicateGroup` (definida em `fotix.domain.models`). Espera-se que `group.files` contenha uma lista de objetos `FileMetadata` representando os arquivos duplicados. Cada `FileMetadata` *deve* idealmente conter os metadados necessários para a decisão (resolução, data de modificação), além dos campos base (`path`, `size`, `creation_time`).

**5. Output:**
   - Retorna: Um único objeto `FileMetadata`, correspondente ao arquivo selecionado para ser mantido, escolhido a partir da lista `group.files`.

**6. Lógica Detalhada e Regras de Negócio:**

   A função `decide_file_to_keep` deve executar os seguintes passos:

   a.  **Validação Inicial:**
       i.  Verificar se `group.files` não é `None` e contém pelo menos dois elementos. Se tiver menos de dois arquivos, a decisão não se aplica a um grupo de duplicatas. Lançar `ValueError` (Ver Seção 8 - Tratamento de Erros).
       ii. Se houver exatamente um arquivo, retornar esse arquivo (embora conceitualmente não seja um grupo de duplicatas, este pode ser um caso de borda a ser tratado). *Nota: O ponto i. tem precedência; se for estritamente para duplicatas, deve haver >= 2.* (Conforme diretriz 8, considerar o tratamento para < 2 como erro).

   b.  **Preparação dos Dados:**
       i.  Iterar sobre a lista `group.files`. Para cada `FileMetadata`, extrair os metadados relevantes para a decisão:
           -   **Resolução:** Assumir que `FileMetadata` terá um atributo ou método para fornecer a resolução como `(largura, altura)` ou `None` se não disponível/aplicável. Calcular a área (`largura * altura`).
           -   **Data de Modificação:** Assumir que `FileMetadata` terá um atributo ou método para fornecer a data/hora da última modificação (timestamp UTC ou objeto `datetime` comparável).
           -   **Nome do Arquivo:** Obter o nome base do arquivo a partir do `path` (`file.path.name`). Calcular o comprimento do nome.

   c.  **Aplicação dos Critérios (Hierárquico):**
   
       i.  **Critério 1: Maior Resolução:**
           -   Comparar todos os arquivos em `group.files` com base na área de resolução calculada.
           -   Arquivos sem dados de resolução (`None`) devem ser considerados como tendo a menor resolução possível (prioridade mais baixa neste critério).
           -   Selecionar o(s) arquivo(s) com a maior área de resolução.
           -   Se apenas um arquivo tiver a maior resolução, retorná-lo como o arquivo a ser mantido.
           -   Se houver empate (múltiplos arquivos com a mesma resolução máxima), passar esses arquivos empatados para o próximo critério.

       ii. **Critério 2: Data de Modificação Mais Recente (Aplicado aos Empatados da Resolução):**
           -   Comparar os arquivos empatados no critério anterior com base na sua data de modificação.
           -   Arquivos sem data de modificação (`None`) devem ser considerados como tendo a data mais antiga possível (prioridade mais baixa neste critério).
           -   Selecionar o(s) arquivo(s) com a data de modificação mais recente (maior timestamp).
           -   Se apenas um arquivo tiver a data mais recente, retorná-lo.
           -   Se houver empate (múltiplos arquivos com a mesma data de modificação mais recente), passar esses arquivos empatados para o próximo critério.

       iii. **Critério 3: Nome de Arquivo Mais Curto (Aplicado aos Empatados da Data):**
           -   Comparar os arquivos empatados no critério anterior com base no comprimento do nome do arquivo (`len(file.path.name)`).
           -   Selecionar o(s) arquivo(s) com o menor comprimento de nome.
           -   Se apenas um arquivo tiver o nome mais curto, retorná-lo.
           -   Se ainda houver empate (múltiplos arquivos com o mesmo menor comprimento de nome), selecionar arbitrariamente o *primeiro* arquivo encontrado entre os empatados finais (garantindo determinismo, por exemplo, baseado na ordem original da lista `group.files` filtrada). Retornar este arquivo.

**7. Dependências e Estruturas de Dados:**
   - A implementação deve usar as definições de `FileMetadata` e `DuplicateGroup` do módulo `fotix.domain.models`.
   - A implementação *não* deve chamar diretamente nenhuma função de I/O ou serviços externos. Deve operar exclusivamente sobre os dados passados via `group`.

**8. Tratamento de Erros:**
   - Se `group` for `None` ou `group.files` for `None`, lançar `ValueError` com uma mensagem apropriada (ex: "DuplicateGroup inválido ou lista de arquivos vazia.").
   - Se `group.files` contiver menos de 2 arquivos, lançar `ValueError` com uma mensagem apropriada (ex: "Não é possível decidir entre menos de dois arquivos.").
   - **Metadados Ausentes:** A lógica de decisão (passo 6.c) deve tratar explicitamente casos onde metadados (resolução, data de modificação) estão ausentes (`None`) para um ou mais arquivos, tratando-os como a menor prioridade dentro do respectivo critério, em vez de lançar um erro. Se *todos* os arquivos em um estágio de desempate não tiverem o metadado relevante, o processo continua para o próximo critério com todos esses arquivos.

**9. Casos de Borda:**
   - **Grupo com 2 arquivos:** A lógica deve funcionar corretamente.
   - **Todos os metadados idênticos:** Se todos os arquivos tiverem a mesma resolução (ou nenhuma), mesma data de modificação (ou nenhuma) e mesmo comprimento de nome, o critério 6.c.iii (último passo do desempate) garantirá que um arquivo seja escolhido (o primeiro entre os empatados finais).
   - **Arquivos sem resolução:** Serão corretamente priorizados abaixo dos que possuem resolução.
   - **Arquivos sem data de modificação:** Serão corretamente priorizados abaixo dos que possuem data de modificação.

**10. Premissas:**
    - Assume-se que a estrutura `FileMetadata` (definida em `fotix.domain.models`) conterá ou fornecerá acesso aos metadados necessários: resolução (como `(largura, altura)` ou similar) e data de modificação (como timestamp ou `datetime`). Se estes não estiverem presentes na definição atual, a implementação desta função assume que eles *serão* adicionados/acessíveis no objeto `FileMetadata` recebido.
    - Assume-se que a ordem dos arquivos dentro do `group.files` original pode ser usada como um critério final de desempate determinístico, se necessário.

**11. Exemplo (Ilustrativo):**

    ```
    # Exemplo de como a função seria chamada (não parte da implementação)
    # file1 = FileMetadata(path=Path("a.jpg"), size=100, creation_time=..., resolution=(1920, 1080), modification_time=1678886400.0, name_len=5)
    # file2 = FileMetadata(path=Path("b_copy.jpg"), size=100, creation_time=..., resolution=(1920, 1080), modification_time=1678886500.0, name_len=10)
    # file3 = FileMetadata(path=Path("c.jpg"), size=100, creation_time=..., resolution=(800, 600), modification_time=1678886600.0, name_len=5)
    # group = DuplicateGroup(files=[file1, file2, file3], hash_value="some_hash")
    #
    # chosen_file = decide_file_to_keep(group)
    # # Esperado: file2 (maior resolução empata file1 e file2, file2 é mais recente que file1)
    ```