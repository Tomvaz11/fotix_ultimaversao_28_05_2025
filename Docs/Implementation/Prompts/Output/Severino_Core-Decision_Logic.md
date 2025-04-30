## Especificação da Funcionalidade/Módulo a ser Implementada

**Módulo/Arquivo Alvo:** `fotix/src/fotix/core/decision_logic.py`

**Funcionalidade:** Implementar a lógica de decisão para selecionar qual arquivo deve ser mantido dentro de um grupo de duplicatas idênticas, com base em critérios pré-definidos.

**Função Principal a ser Implementada:**

```python
from fotix.domain.models import DuplicateGroup, FileMetadata
import re # Importar para usar regex na análise de nomes
from pathlib import Path # Necessário para manipulação de caminhos

def decide_file_to_keep(group: DuplicateGroup) -> FileMetadata:
    """
    Seleciona o arquivo a ser mantido de um grupo de duplicatas idênticas.

    Aplica os seguintes critérios em ordem de prioridade:
    1. Data de criação mais antiga (creation_time).
    2. Nome de arquivo "limpo" (sem padrões de cópia comuns).
    3. Desempate final por ordem alfabética do caminho completo.

    Args:
        group: Um objeto DuplicateGroup contendo a lista de arquivos duplicados.

    Returns:
        O objeto FileMetadata do arquivo selecionado para ser mantido.

    Raises:
        ValueError: Se o grupo for nulo, ou se a lista de arquivos
                    for nula ou contiver menos de dois arquivos.
    """
    # Implementação segue abaixo
```

**Inputs:**

-   `group`: Uma instância da classe `DuplicateGroup` (definida em `fotix.domain.models`). Espera-se que contenha:
    -   `files`: Uma lista (`List[FileMetadata]`) contendo pelo menos duas instâncias de `FileMetadata`. Cada `FileMetadata` deve ter os atributos `path` (objeto `pathlib.Path`), `size` (int), e `creation_time` (float/timestamp UTC).
    -   `hash_value`: Uma string representando o hash que identifica o grupo (informativo, não usado diretamente na lógica de decisão).

**Outputs:**

-   Retorna uma única instância de `FileMetadata`, representando o arquivo escolhido para ser mantido.

**Processamento Detalhado:**

1.  **Validação de Entrada:**
    *   Verifique se o argumento `group` não é `None`.
    *   Verifique se `group.files` não é `None`.
    *   Verifique se `len(group.files) >= 2`.
    *   Se qualquer uma dessas validações falhar, levante uma exceção `ValueError` com uma mensagem clara (ex: "O grupo de duplicatas é inválido ou contém menos de dois arquivos.").

2.  **Inicialização:**
    *   Se a validação passar, atribua `group.files` a uma variável local `candidates` para facilitar o trabalho.
    *   `candidates: List[FileMetadata] = group.files`

3.  **Critério 1: Data de Criação Mais Antiga:**
    *   Determine o valor mínimo de `creation_time` entre todos os `FileMetadata` em `candidates`.
        *   `min_creation_time = min(f.creation_time for f in candidates)`
    *   Filtre a lista `candidates`, mantendo apenas aqueles cujo `creation_time` seja igual a `min_creation_time`.
        *   `candidates = [f for f in candidates if f.creation_time == min_creation_time]`
    *   **Verificação de Resultado:** Se `len(candidates) == 1`, o arquivo restante é o escolhido. Retorne este `FileMetadata`.

4.  **Critério 2: Nome de Arquivo "Limpo":**
    *   Execute este passo *apenas se* `len(candidates) > 1` após o Critério 1.
    *   Defina uma lista de padrões regex para identificar nomes de arquivo que sugerem ser cópias. Os padrões devem ser aplicados ao *stem* (nome do arquivo sem a extensão) e preferencialmente ancorados ao final do stem. Exemplos de padrões (use `re.IGNORECASE` se apropriado):
        *   `r'\((\d+)\)$'` (Ex: `arquivo(1).jpg`)
        *   `r' - C[oó]pia( \(\d+\))?$'` (Ex: `arquivo - Copia.jpg`, `arquivo - Cópia (2).jpg`)
        *   `r'[_ ]copy( \(\d+\))?$'` (Ex: `arquivo_copy.jpg`, `arquivo copy (3).jpg`)
        *   *(Considere adicionar outros padrões comuns se necessário)*
    *   Crie uma nova lista `clean_name_candidates`.
    *   Itere sobre os `candidates` atuais:
        *   Para cada `file_meta` em `candidates`:
            *   Obtenha o stem: `stem = file_meta.path.stem`
            *   Verifique se o `stem` corresponde a *qualquer* um dos padrões de cópia definidos.
            *   Se *não* houver correspondência com nenhum padrão, adicione `file_meta` à lista `clean_name_candidates`.
    *   **Avaliação dos Nomes Limpos:**
        *   **Caso A:** Se `len(clean_name_candidates) == 1`, este único arquivo com nome limpo é o escolhido. Retorne este `FileMetadata`.
        *   **Caso B:** Se `len(clean_name_candidates) > 1`, significa que há múltiplos arquivos com a data mais antiga e nomes limpos. Atualize a lista de `candidates` para conter apenas os arquivos de `clean_name_candidates`. Prossiga para o Critério 3 com esta lista reduzida.
            *   `candidates = clean_name_candidates`
        *   **Caso C:** Se `len(clean_name_candidates) == 0`, significa que *todos* os arquivos empatados na data mais antiga têm nomes que parecem cópias. Neste caso, *não* modifique a lista `candidates` (ela ainda contém todos os arquivos empatados do Critério 1). Prossiga para o Critério 3 com a lista `candidates` atual.

5.  **Critério 3: Desempate Final (Ordem Alfabética):**
    *   Execute este passo *apenas se* `len(candidates) > 1` após a execução (ou não execução/resultado) do Critério 2.
    *   Ordene a lista `candidates` atual em ordem alfabética com base no caminho completo do arquivo (`file_meta.path`). A conversão para string (`str(file_meta.path)`) pode ser necessária para a ordenação.
        *   `candidates.sort(key=lambda fm: str(fm.path))`
    *   Selecione o primeiro elemento da lista ordenada. Este é o arquivo escolhido.
    *   Retorne o primeiro `FileMetadata` da lista `candidates` ordenada.

**Tratamento de Erros:**

-   Levantar `ValueError` conforme descrito na seção "Validação de Entrada". Nenhum outro tratamento de erro específico é esperado neste nível, assumindo que os objetos `FileMetadata` estão corretamente preenchidos.

**Casos de Borda a Considerar:**

-   Grupo contendo exatamente 2 arquivos.
-   Todos os arquivos no grupo possuem o mesmo `creation_time`.
-   Todos os arquivos com a data de criação mais antiga possuem nomes que correspondem aos padrões de cópia (aciona o Caso C do Critério 2).
-   Múltiplos arquivos possuem a data de criação mais antiga e nomes "limpos" (aciona o Caso B do Critério 2 e subsequentemente o Critério 3).
-   Nomes de arquivos que podem falsamente corresponder aos padrões (ex: um nome legítimo terminando em `(1)`). A robustez dos padrões regex é importante.
-   Diferenças mínimas em `creation_time` devido à precisão de floating point (o uso de `==` deve ser seguro aqui, mas é algo a ter em mente se a fonte dos timestamps for variável).