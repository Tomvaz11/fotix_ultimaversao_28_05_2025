# AGV Prompt Template: Tocle v1.0 - Implementação de Código Novo

**Tarefa Principal:** Implementar a funcionalidade/módulo descrito na seção "Especificação" abaixo, criando o arquivo Python `fotix/src/fotix/core/decision_logic.py`. Siga rigorosamente as diretrizes e o contexto arquitetural fornecido.

**Contexto Arquitetural (Definido por Tocrisna / Fase Anterior):**

*   **Nome do Projeto:** `Fotix`
*   **Objetivo Geral do Projeto:** Aplicativo desktop Python com GUI para localizar e remover arquivos duplicados (imagens/vídeos) em diretórios e ZIPs, usando critérios inteligentes (data, nome) para manter o melhor arquivo, com backup/restauração e otimização para grandes volumes.
*   **Localização deste Módulo/Arquivo:** `fotix/src/fotix/core/decision_logic.py`
*   **Principais Responsabilidades deste Módulo/Arquivo:** Implementar a lógica de decisão para selecionar qual arquivo deve ser mantido dentro de um grupo de duplicatas idênticas, com base em critérios pré-definidos (data de criação, nome "limpo", ordem alfabética).
*   **Interfaces de Dependências (Contratos a serem Usados):**
    *   `fotix.domain.models.DuplicateGroup`: Dataclass contendo a lista de arquivos duplicados (`List[FileMetadata]`).
    *   `fotix.domain.models.FileMetadata`: Dataclass contendo metadados do arquivo (`path`, `size`, `creation_time`).
    *   `re` (Standard Library): Para análise de padrões em nomes de arquivos.
    *   `pathlib` (Standard Library): Para manipulação de caminhos de arquivos.
    *   `[Nenhuma dependência externa significativa de *outros módulos do projeto Fotix* definida pela arquitetura para esta implementação específica. A função opera nos dados fornecidos.]`
*   **Interfaces Expostas (Contratos a serem Fornecidos - se aplicável):**
    *   `def decide_file_to_keep(group: DuplicateGroup) -> FileMetadata`: Função pública que implementa a lógica de decisão.
*   **Padrões de Design Chave (Relevantes para esta Implementação):** `Separação de Responsabilidades (SRP)` (A função tem uma única responsabilidade bem definida).
*   **Estrutura de Dados Principal (Relevantes para esta Implementação):**
    *   `fotix.domain.models.FileMetadata`: `dataclass(frozen=True)` com `path: Path`, `size: int`, `creation_time: float`.
    *   `fotix.domain.models.DuplicateGroup`: `dataclass` com `files: List[FileMetadata]`, `hash_value: str`, `file_to_keep: Optional[FileMetadata]`.

**Especificação da Funcionalidade/Módulo a ser Implementada:**

```
Implementar a função `decide_file_to_keep` no arquivo `fotix/src/fotix/core/decision_logic.py`.

**Função Principal a ser Implementada:**

```python
from fotix.domain.models import DuplicateGroup, FileMetadata
import re # Importar para usar regex na análise de nomes
from pathlib import Path # Necessário para manipulação de caminhos
from typing import List # Necessário para type hints internos

def decide_file_to_keep(group: DuplicateGroup) -> FileMetadata:
    """
    Seleciona o arquivo a ser mantido de um grupo de duplicatas idênticas.

    Aplica os seguintes critérios em ordem de prioridade:
    1. Data de criação mais antiga (creation_time).
    2. Nome de arquivo "limpo" (sem padrões de cópia comuns).
    3. Desempate final por ordem alfabética do caminho completo.

    Args:
        group: Um objeto DuplicateGroup contendo a lista de arquivos duplicados.
                Espera-se que group.files contenha pelo menos dois arquivos.

    Returns:
        O objeto FileMetadata do arquivo selecionado para ser mantido.

    Raises:
        ValueError: Se o grupo for nulo, ou se a lista de arquivos
                    for nula ou contiver menos de dois arquivos.
    """
    # Implementação segue aqui
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
    *   Defina uma lista de padrões regex para identificar nomes de arquivo que sugerem ser cópias. Os padrões devem ser aplicados ao *stem* (nome do arquivo sem a extensão) e preferencialmente ancorados ao final do stem. Exemplos de padrões (use `re.IGNORECASE`):
        *   `r'\((\d+)\)$'` (Ex: `arquivo(1).jpg`)
        *   `r' - C[oó]pia( \(\d+\))?$'` (Ex: `arquivo - Copia.jpg`, `arquivo - Cópia (2).jpg`)
        *   `r'[_ ]copy( \(\d+\))?$'` (Ex: `arquivo_copy.jpg`, `arquivo copy (3).jpg`)
        *   *(Considere adicionar outros padrões comuns se necessário)*
    *   Crie uma nova lista `clean_name_candidates`.
    *   Itere sobre os `candidates` atuais:
        *   Para cada `file_meta` em `candidates`:
            *   Obtenha o stem: `stem = file_meta.path.stem`
            *   Verifique se o `stem` corresponde a *qualquer* um dos padrões de cópia definidos usando `re.search`.
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

```

**Stack Tecnológica Permitida (Definida na Fase 1):**

*   **Linguagem:** Python `3.10+`
*   **Frameworks Principais:** `Nenhum` (para este módulo específico)
*   **Bibliotecas Essenciais:** `re`, `pathlib` (Standard Library), `Pillow`, `BLAKE3`, `send2trash`, `stream-unzip`, `concurrent.futures` (Permitir importação apenas destas - conforme necessidade contextual do projeto -, das bibliotecas padrão Python e dos outros módulos do projeto definidos nas dependências, principalmente `fotix.domain.models`).

**Diretrizes Específicas de Implementação:**

1.  **Aderência Estrita às Interfaces:** Implementar a funcionalidade utilizando as estruturas `DuplicateGroup` e `FileMetadata` como input e expondo *exatamente* a função `decide_file_to_keep` com a assinatura definida. Utilize as dependências listadas (`re`, `pathlib`, `typing`).
2.  **Código Limpo e Legível (PEP 8):** Seguir rigorosamente o PEP 8 para formatação, nomenclatura e estilo. Priorizar clareza e simplicidade (KISS).
3.  **Modularidade e Coesão (SRP):** A função deve focar exclusivamente na lógica de decisão. Funções auxiliares internas podem ser criadas se aumentarem a clareza.
4.  **Type Hints (PEP 484):** Utilizar type hints completos e precisos para a função, parâmetros, variáveis internas importantes e o valor de retorno, conforme especificado.
5.  **Tratamento de Erros Robusto:**
    *   Implementar a validação de entrada e levantar `ValueError` conforme especificado.
    *   Garantir que a lógica interna lide corretamente com os casos descritos (ex: lista vazia após filtragem, múltiplos candidatos).
6.  **Segurança Básica:** A validação de entrada (`ValueError`) é a principal medida de segurança aqui. Não há manipulação direta de arquivos ou dados externos sensíveis nesta função.
7.  **Documentação (Docstrings PEP 257):** Escrever a docstring completa para a função `decide_file_to_keep`, detalhando propósito, `Args`, `Returns` e `Raises`, conforme o template fornecido na especificação. Comentar apenas lógica complexa ou os padrões regex se necessário.
8.  **Sem Código Morto/Desnecessário:** Implementar apenas o necessário para a funcionalidade especificada.
9.  **Testes Unitários:** **OBRIGATÓRIO:** Gerar testes unitários usando `pytest` para a função `decide_file_to_keep`. Os testes devem:
    *   Cobrir casos de sucesso para cada critério de decisão.
    *   Cobrir os casos de borda descritos na especificação (ex: empate no critério 1, todos nomes são "cópia", empate no critério 2, etc.).
    *   Cobrir o caso de erro (`ValueError` para input inválido).
    *   **Não é necessário usar mocks/stubs para simular dependências de *outros módulos Fotix*, pois não há chamadas diretas para eles.** Use objetos `FileMetadata` e `DuplicateGroup` de teste criados manualmente com os dados necessários para cada cenário. Pode ser útil mockar `re.search` se for necessário controle fino sobre o matching dos padrões em casos de teste específicos.
    *   Verificar se o `FileMetadata` retornado é o esperado para cada caso de teste.
    *   Colocar os testes no arquivo `tests/core/test_decision_logic.py`.
10. **Eficiência (Consideração):** O algoritmo proposto (filtragem sequencial) é razoavelmente eficiente para o número de arquivos esperado em um único grupo de duplicatas. Evitar complexidade desnecessária.

**Resultado Esperado:**

1.  **Código Python Completo:** O conteúdo final do arquivo `fotix/src/fotix/core/decision_logic.py` com a função `decide_file_to_keep` implementada.
2.  **Código de Testes Unitários:** O conteúdo do arquivo de teste `tests/core/test_decision_logic.py` com os testes unitários para `decide_file_to_keep` usando `pytest`.
3.  **(Opcional) Breve Relatório:** Explicação de decisões de implementação (ex: escolha dos padrões regex finais), desafios ou sugestões.