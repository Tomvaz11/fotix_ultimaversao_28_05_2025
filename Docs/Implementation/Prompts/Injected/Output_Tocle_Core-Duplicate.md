# AGV Prompt Template: Tocle v1.0 - Implementação de Código Novo

**Tarefa Principal:** Implementar a funcionalidade/módulo descrito na seção "Especificação" abaixo, criando ou modificando o arquivo Python `fotix/src/fotix/core/duplicate_finder.py`. Siga rigorosamente as diretrizes e o contexto arquitetural fornecido.

**Contexto Arquitetural (Definido por Tocrisna / Fase Anterior):**

*   **Nome do Projeto:** `Fotix`
*   **Objetivo Geral do Projeto:** `Aplicativo desktop Python/PySide6 para localizar e remover arquivos duplicados (imagens/vídeos) em diretórios e ZIPs, com seleção inteligente de qual arquivo manter e backup seguro.`
*   **Localização deste Módulo/Arquivo:** `fotix/src/fotix/core/duplicate_finder.py`
*   **Principais Responsabilidades deste Módulo/Arquivo:** `Implementa a lógica central para encontrar grupos de arquivos duplicados exatos (mesmo tamanho e hash BLAKE3) a partir de um iterador de metadados de arquivos.`
*   **Interfaces de Dependências (Contratos a serem Usados):**
    *   `Iterator[FileMetadata]`: Um iterador fornecido externamente (pela camada de Aplicação) que produz instâncias de `FileMetadata`. Não é uma função/classe a ser chamada diretamente, mas a fonte de dados principal.
    *   `hash_function(file_meta: FileMetadata) -> str`: Uma função (callable) fornecida externamente (pela camada de Aplicação/Infraestrutura). Recebe um `FileMetadata`, calcula e retorna o hash BLAKE3 do conteúdo do arquivo correspondente (`file_meta.path`). É responsável por sua própria lógica de I/O e tratamento de erros, levantando uma exceção (ex: `OSError` ou customizada) se o hash não puder ser gerado.
    *   `fotix.core.domain.FileMetadata (dataclass, frozen=True)`: Estrutura de dados esperada do iterador. Contém: `path: Path`, `size: int`, `creation_time: float`. (Assumindo que esta definição virá de um módulo `domain` ou similar).
    *   `fotix.core.domain.DuplicateGroup (dataclass)`: Estrutura de dados a ser retornada. Contém: `files: List[FileMetadata]`, `hash_value: str`, `file_to_keep: Optional[FileMetadata]`. (Assumindo que esta definição virá de um módulo `domain` ou similar).
*   **Interfaces Expostas (Contratos a serem Fornecidos - se aplicável):**
    *   Classe `DuplicateFinder`
    *   Método público na classe `DuplicateFinder`: `find_duplicates(self, file_iterator: Iterator[FileMetadata], hash_function: callable) -> List[DuplicateGroup]`
*   **Padrões de Design Chave (Relevantes para esta Implementação):** `Strategy Pattern (para hash_function injetada), Separação de Responsabilidades (SRP).`
*   **Estrutura de Dados Principal (Relevantes para esta Implementação):**
    *   `FileMetadata (dataclass, frozen=True)`: `path: Path`, `size: int`, `creation_time: float`. Usado como input via iterador.
    *   `DuplicateGroup (dataclass)`: `files: List[FileMetadata]`, `hash_value: str`, `file_to_keep: Optional[FileMetadata]`. Usado como output na lista de retorno.

**Especificação da Funcionalidade/Módulo a ser Implementada:**

```markdown
Implementar a classe `DuplicateFinder` no arquivo `fotix/src/fotix/core/duplicate_finder.py`.
A classe deve conter um método público principal: `find_duplicates`.

**Método:** `find_duplicates(self, file_iterator: Iterator[FileMetadata], hash_function: callable) -> List[DuplicateGroup]`

**Inputs:**

1.  `file_iterator`: Um `Iterator[FileMetadata]`. Cada `FileMetadata` (dataclass `frozen=True`) contém `path: Path`, `size: int`, `creation_time: float`.
2.  `hash_function`: Uma função `callable` que recebe `FileMetadata` e retorna `str` (hash BLAKE3), ou levanta exceção em caso de erro de I/O ao ler o arquivo.

**Processamento:**

1.  **Agrupamento Inicial por Tamanho:**
    *   Crie um `Dict[int, List[FileMetadata]]` chamado `files_by_size`.
    *   Itere sobre `file_iterator`. Para cada `file_meta`:
        *   Adicione `file_meta` à lista em `files_by_size` correspondente ao `file_meta.size`.

2.  **Identificação e Hashing de Potenciais Duplicatas:**
    *   Inicialize `result_groups: List[DuplicateGroup] = []`.
    *   Itere sobre as listas (`potential_duplicates`) em `files_by_size.values()`.
    *   Se `len(potential_duplicates) < 2`, continue para a próxima lista.
    *   **Agrupamento por Hash (Dentro do Grupo de Tamanho):**
        *   Crie um `Dict[str, List[FileMetadata]]` chamado `hashes_in_group`.
        *   Itere sobre cada `file_meta` em `potential_duplicates`:
            *   **Cálculo de Hash com Tratamento de Erro:**
                *   Use `try...except` para chamar `hash_value = hash_function(file_meta)`.
                *   **Em caso de exceção:** Logue um aviso (`logging.warning`) com o caminho do arquivo e o erro. Continue para o próximo `file_meta`.
                *   **Se sucesso:** Adicione `file_meta` à lista em `hashes_in_group` correspondente ao `hash_value`.
    *   **Formação de Grupos de Duplicatas Reais:**
        *   Itere sobre as listas (`actual_duplicates`) em `hashes_in_group.values()`.
        *   Se `len(actual_duplicates) < 2`, continue.
        *   Crie uma instância de `DuplicateGroup` com:
            *   `files = actual_duplicates`
            *   `hash_value =` (a chave correspondente do dicionário `hashes_in_group`)
            *   `file_to_keep = None`
        *   Adicione o `DuplicateGroup` criado a `result_groups`.

3.  **Retorno:** Retorne `result_groups`.

**Outputs:**

-   Uma `List[DuplicateGroup]`. Cada `DuplicateGroup` contém `files: List[FileMetadata]` (2+ arquivos), `hash_value: str`, e `file_to_keep: Optional[FileMetadata]` (sempre `None` neste estágio).
-   Retorna lista vazia se nenhuma duplicata for encontrada.

**Tratamento de Erros Específico:**

-   Não tratar erros de I/O da leitura de arquivos diretamente (responsabilidade da `hash_function`).
-   Capturar exceções levantadas pela `hash_function`.
-   Logar um aviso claro (usando `logging`) quando `hash_function` falhar para um arquivo, incluindo o caminho e o erro.
-   Garantir que o processo continue para outros arquivos após uma falha no hash de um arquivo específico.

**Casos de Borda a Considerar:**

-   Iterador vazio -> `[]`.
-   Nenhuma duplicata por tamanho -> `[]`.
-   Duplicatas por tamanho, mas hashes diferentes -> `[]`.
-   Todos os arquivos idênticos -> Uma `DuplicateGroup` com todos os arquivos.
-   Múltiplos grupos de duplicatas -> Múltiplas `DuplicateGroup` na lista.
-   Arquivos de tamanho zero -> Devem ser agrupados e hasheados normalmente.
-   Falha no hash de alguns arquivos -> Esses arquivos são ignorados no agrupamento por hash, o processo continua.
```

**Stack Tecnológica Permitida (Definida na Fase 1):**

*   **Linguagem:** Python `3.10+`
*   **Frameworks Principais:** `Nenhum framework específico para este módulo core.`
*   **Bibliotecas Essenciais:** `typing`, `pathlib`, `logging`, `collections` (e outras bibliotecas padrão do Python conforme necessário). Nenhuma biblioteca externa adicional é necessária para a lógica interna desta classe, baseando-se nas interfaces fornecidas.

**Diretrizes Específicas de Implementação:**

1.  **Aderência Estrita às Interfaces:** Implementar a funcionalidade utilizando e expondo *exatamente* as interfaces definidas na seção "Contexto Arquitetural". Chamar apenas a `hash_function` fornecida.
2.  **Código Limpo e Legível (PEP 8):** Seguir rigorosamente o PEP 8. Priorizar clareza e simplicidade (KISS).
3.  **Modularidade e Coesão (SRP):** A classe `DuplicateFinder` deve focar exclusivamente na lógica de encontrar duplicatas, sem se preocupar com a origem dos dados (iterador) ou como o hash é calculado (função injetada).
4.  **Type Hints (PEP 484):** Utilizar type hints completos e precisos para o método, parâmetros e variáveis importantes (como os dicionários internos).
5.  **Tratamento de Erros Robusto:** Implementar o `try/except` ao redor da chamada `hash_function` conforme especificado, logando os erros adequadamente.
6.  **Segurança Básica:** A segurança primária aqui reside em confiar no contrato da `hash_function` e não executar operações de I/O diretas. Validar os tipos de dados recebidos (via type hints) é importante.
7.  **Documentação (Docstrings PEP 257):** Escrever docstrings claras para a classe `DuplicateFinder` e seu método `find_duplicates`, explicando propósito, argumentos (`Args`), retorno (`Returns`) e exceções que *este método* pode indiretamente deixar passar ou que a `hash_function` pode gerar (`Raises` se aplicável ao contrato da hash_function).
8.  **Sem Código Morto/Desnecessário:** Implementar apenas a lógica de agrupamento e hashing descrita.
9.  **Testes Unitários:** **OBRIGATÓRIO:** Gerar testes unitários usando `pytest` para o método `find_duplicates`. Os testes devem:
    *   Cobrir casos de sucesso (sem duplicatas, uma duplicata, múltiplas duplicatas), casos de borda (iterador vazio, arquivos tamanho zero) e casos de erro (falha na `hash_function`).
    *   **Utilizar mocks/stubs para simular o `file_iterator` e a `hash_function`**. O mock da `hash_function` deve ser capaz de simular tanto sucesso quanto falha (levantar exceção) para arquivos específicos.
    *   Verificar se a lista de `DuplicateGroup` retornada está correta.
    *   Verificar se o logging de aviso ocorre quando o mock da `hash_function` levanta uma exceção.
    *   Colocar os testes em `tests/unit/core/test_duplicate_finder.py`.
10. **Eficiência (Consideração):** Usar estruturas de dados eficientes (ex: `collections.defaultdict` para agrupamento) para lidar potencialmente com muitos arquivos. A iteração principal sobre os arquivos ocorre apenas uma vez para agrupar por tamanho. O hashing ocorre apenas para grupos com tamanho > 1.

**Resultado Esperado:**

1.  **Código Python Completo:** O conteúdo final do arquivo `fotix/src/fotix/core/duplicate_finder.py` com a classe `DuplicateFinder` e seu método `find_duplicates` implementados.
2.  **Código de Testes Unitários:** O conteúdo do arquivo `tests/unit/core/test_duplicate_finder.py` com os testes unitários para `DuplicateFinder`, utilizando mocks para `file_iterator` e `hash_function`.
3.  **(Opcional) Breve Relatório:** N/A neste momento.