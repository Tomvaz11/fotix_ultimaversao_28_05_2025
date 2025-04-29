## Especificação Técnica Detalhada (Gerada para Tocle)

**Módulo/Classe Alvo:** Classe `DuplicateFinder` no arquivo `fotix/src/fotix/core/duplicate_finder.py`.

**Método Principal:**
`find_duplicates(self, file_iterator: Iterator[FileMetadata], hash_function: callable) -> List[DuplicateGroup]`

**Inputs:**

1.  `file_iterator`: Um iterador (`Iterator[FileMetadata]`) que fornece objetos `FileMetadata`. Cada `FileMetadata` é um dataclass `frozen=True` contendo:
    *   `path: Path` (Caminho absoluto para o arquivo)
    *   `size: int` (Tamanho do arquivo em bytes)
    *   `creation_time: float` (Timestamp UTC da criação do arquivo)
    Este iterador é a fonte primária de dados sobre os arquivos a serem analisados e é fornecido pela camada de Aplicação.
2.  `hash_function`: Uma função (`callable`) que adere ao seguinte contrato:
    *   **Argumento:** Recebe uma única instância de `FileMetadata`.
    *   **Retorno:** Retorna uma string (`str`) que representa o hash BLAKE3 do conteúdo do arquivo correspondente ao `FileMetadata.path`.
    *   **Implementação:** A lógica interna desta função (incluindo leitura de arquivo e tratamento de erros de I/O) é responsabilidade da camada de Aplicação/Infraestrutura que a fornece. Espera-se que a função levante uma exceção apropriada (ex: uma subclasse de `OSError` ou uma exceção customizada definida pela arquitetura) se o hash não puder ser gerado para um arquivo específico.

**Processamento:**

1.  **Agrupamento Inicial por Tamanho:**
    *   Inicialize um dicionário `files_by_size: Dict[int, List[FileMetadata]]`.
    *   Itere completamente sobre o `file_iterator` fornecido.
    *   Para cada `file_meta` obtido do iterador:
        *   Recupere o `size` de `file_meta`.
        *   Se `size` não for uma chave em `files_by_size`, crie uma nova entrada com uma lista vazia: `files_by_size[size] = []`.
        *   Adicione `file_meta` à lista `files_by_size[size]`.

2.  **Identificação e Hashing de Potenciais Duplicatas:**
    *   Inicialize uma lista vazia `result_groups: List[DuplicateGroup]` para armazenar os grupos de duplicatas finais.
    *   Itere sobre os *valores* (que são `List[FileMetadata]`) do dicionário `files_by_size`.
    *   Para cada lista `potential_duplicates` (correspondente a um tamanho específico):
        *   **Pré-filtragem:** Se `len(potential_duplicates) < 2`, pule para o próximo grupo de tamanho (não podem haver duplicatas).
        *   **Agrupamento por Hash (Dentro do Grupo de Tamanho):**
            *   Inicialize um dicionário `hashes_in_group: Dict[str, List[FileMetadata]]` para este grupo de tamanho específico.
            *   Itere sobre cada `file_meta` na lista `potential_duplicates`:
                *   **Cálculo de Hash com Tratamento de Erro:**
                    *   Use um bloco `try...except` para chamar `hash_value = hash_function(file_meta)`.
                    *   **Se `hash_function` levantar uma exceção:**
                        *   Registre um aviso (utilizando o sistema de logging padrão do Python, ex: `logging.warning`) informando que o cálculo do hash falhou para o arquivo `file_meta.path`, incluindo o tipo da exceção, se possível.
                        *   Continue para o próximo `file_meta` na lista `potential_duplicates` (ignore este arquivo para fins de agrupamento por hash).
                    *   **Se o hash for calculado com sucesso (`hash_value` obtido):**
                        *   Se `hash_value` não for uma chave em `hashes_in_group`, crie uma nova entrada: `hashes_in_group[hash_value] = []`.
                        *   Adicione `file_meta` à lista `hashes_in_group[hash_value]`.
        *   **Formação de Grupos de Duplicatas Reais:**
            *   Após processar todos os `file_meta` no grupo de tamanho atual, itere sobre os *valores* (que são `List[FileMetadata]`) do dicionário `hashes_in_group`.
            *   Para cada lista `actual_duplicates` (correspondente a um hash específico):
                *   **Filtragem Final:** Se `len(actual_duplicates) < 2`, ignore esta lista (não são duplicatas).
                *   **Criação do Grupo:** Crie uma instância de `DuplicateGroup`:
                    *   `files = actual_duplicates` (a lista de `FileMetadata` com o mesmo tamanho e hash).
                    *   `hash_value =` (a chave de hash correspondente a esta lista em `hashes_in_group`).
                    *   `file_to_keep = None` (conforme definido pela arquitetura, a decisão não é feita aqui).
                *   Adicione a instância `DuplicateGroup` criada à lista `result_groups`.

3.  **Retorno:** Retorne a lista `result_groups`.

**Outputs:**

-   **Valor de Retorno:** Uma lista (`List[DuplicateGroup]`) contendo zero ou mais instâncias de `DuplicateGroup`.
-   **Conteúdo de `DuplicateGroup`:** Cada instância representa um conjunto de arquivos identificados como duplicatas exatas (mesmo tamanho e mesmo hash BLAKE3). Contém:
    *   `files: List[FileMetadata]` (Lista com 2 ou mais `FileMetadata` dos arquivos duplicados).
    *   `hash_value: str` (O hash BLAKE3 comum a todos os arquivos no grupo).
    *   `file_to_keep: Optional[FileMetadata]` (Será sempre `None` ao ser retornado por este método).
-   **Condições de Retorno Vazio:** A lista retornada será vazia se:
    *   O `file_iterator` inicial estiver vazio.
    *   Nenhum grupo de arquivos tiver o mesmo tamanho.
    *   Grupos de arquivos com o mesmo tamanho não compartilharem o mesmo hash após a análise.
    *   Em resumo, se nenhum conjunto de 2 ou mais arquivos idênticos for encontrado.

**Tratamento de Erros Específico:**

-   O método `find_duplicates` *não deve* tratar erros de I/O diretamente relacionados à leitura de arquivos, pois essa responsabilidade é delegada à `hash_function`.
-   O método *deve* implementar um tratamento robusto para exceções levantadas pela `hash_function` durante a iteração:
    *   Capturar exceções que podem ser levantadas pela `hash_function` (ex: `IOError`, `PermissionError`, ou exceções customizadas definidas no contrato da `hash_function`).
    *   Ao capturar uma exceção para um arquivo específico, logar um aviso claro contendo o caminho do arquivo e a natureza do erro.
    *   Garantir que o processo continue para os demais arquivos, efetivamente pulando o arquivo problemático na análise de duplicatas por hash. Não permitir que a falha em um único arquivo interrompa a análise completa.

**Casos de Borda a Considerar:**

-   **Iterador Vazio:** `file_iterator` não produz nenhum `FileMetadata`. O método deve retornar `[]` corretamente.
-   **Nenhuma Duplicata por Tamanho:** Todos os arquivos têm tamanhos únicos. O loop de hashing não será acionado, resultando em `[]`.
-   **Duplicatas por Tamanho, Mas Não por Hash:** Arquivos compartilham o mesmo tamanho, mas após o hashing, nenhum grupo de 2 ou mais arquivos compartilha o mesmo hash. O resultado deve ser `[]`.
-   **Todos os Arquivos São Idênticos:** Todos os arquivos têm o mesmo tamanho e o mesmo hash. Deve retornar uma única `DuplicateGroup` contendo todos os `FileMetadata`.
-   **Múltiplos Grupos de Duplicatas:** Vários conjuntos distintos de arquivos duplicados são encontrados. A lista retornada deve conter uma `DuplicateGroup` para cada conjunto.
-   **Arquivos de Tamanho Zero:** Devem ser agrupados corretamente pelo tamanho 0. Se houver mais de um, serão hasheados. Se os hashes coincidirem (provavelmente serão idênticos para conteúdo vazio), formarão um `DuplicateGroup`.
-   **Falha no Hash de Alguns Arquivos:** Conforme especificado no Tratamento de Erros, esses arquivos devem ser ignorados para o agrupamento por hash, mas o processo deve continuar com os demais.