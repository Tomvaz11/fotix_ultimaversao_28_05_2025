Este prompt foi criado para orientar uma LLM — neste caso, você, no papel do agente "Severino" — na execução da função de um especificador funcional, conforme descrito a seguir.

---

# AGV Prompt Template: Severino v1.0 - Especificação Funcional Detalhada

## Tarefa Principal

Detalhar a especificação técnica para a funcionalidade/módulo descrito abaixo, baseando-se no contexto arquitetural fornecido. O resultado deve ser formatado de forma clara e precisa, pronto para ser usado na seção "Especificação da Funcionalidade/Módulo a ser Implementada" do prompt do agente Tocle.

## Contexto do Projeto e Arquitetura (Definido por Fases Anteriores)

- **Nome do Projeto:** `Fotix`
- **Objetivo Geral do Projeto:** `Aplicativo desktop desenvolvido em Python, com backend robusto e interface gráfica (GUI) completa, projetado para localizar e remover arquivos duplicados (idênticos) de imagens e vídeos em múltiplos diretórios e arquivos ZIP, utilizando um algoritmo inteligente para decidir qual arquivo manter com base em critérios objetivos (resolução, data, nome), com backup e restauração.`
- **Blueprint Arquitetural Relevante (Definido por Tocrisna):**
  - **Módulo/Arquivo Alvo desta Especificação:** `fotix/src/fotix/core/decision_logic.py`
  - **Principais Responsabilidades deste Módulo/Arquivo (Conforme Arquitetura):** `Implementar o algoritmo de decisão para escolher qual arquivo manter dentro de um grupo de duplicatas idênticas, aplicando critérios de negócio como data de criação e estrutura do nome do arquivo.`
  - **Interfaces de Dependências (Contratos a serem Usados por este Módulo):**
    - `Este módulo depende primariamente das estruturas de dados definidas, não de chamadas diretas a outras interfaces de serviço durante sua execução principal. As estruturas de dados necessárias são:`
    - `domain.models.FileMetadata`
    - `domain.models.DuplicateGroup`
    - `(Potencialmente funções auxiliares de 'fotix.utils' para análise de nomes de arquivo, se criadas)`
  - **Interfaces Expostas (Contratos Fornecidos por este Módulo):**
    - `(Função principal a ser implementada neste módulo ou usada por fotix.core.duplicate_finder)`
    - `decide_file_to_keep(group: DuplicateGroup) -> FileMetadata`: `Aplica as regras de negócio para selecionar o melhor arquivo dentro de um grupo de duplicatas.`
  - **Estruturas de Dados Relevantes (Definidas pela Arquitetura):**
    ```python
    from dataclasses import dataclass, field
    from pathlib import Path
    from typing import List, Dict, Optional, Iterator, Tuple # Tuple adicionado para possível resolução futura

    @dataclass(frozen=True)
    class FileMetadata:
        path: Path
        size: int
        creation_time: float # Timestamp UTC
        # Nota: A resolução não está presente na definição atual da arquitetura.
        # A lógica inicial focará nos campos disponíveis: creation_time e path (para nome).

    @dataclass
    class DuplicateGroup:
        files: List[FileMetadata] # Lista de arquivos idênticos
        file_to_keep: Optional[FileMetadata] = None # A ser preenchido por esta lógica
        hash_value: str # Hash que identifica o grupo
    ```

## Descrição de Alto Nível da Funcionalidade (Fornecida por Você)

> [Preciso que o módulo `decision_logic.py` implemente a lógica para escolher automaticamente qual arquivo deve ser preservado dentro de um grupo de arquivos duplicados idênticos (`DuplicateGroup`). A escolha deve seguir uma ordem de prioridade:
> 1.  **Data de Criação:** Preferir o arquivo com a data de criação (`creation_time`) mais antiga.
> 2.  **Nome do Arquivo:** Se houver empate na data de criação, preferir o arquivo cujo nome *não* contenha padrões comuns de cópia (ex: "(1)", "(2)", " - Cópia", "_copy").
> 3.  **Critério de Desempate Final:** Se ainda houver empate (mesma data mais antiga, nomes igualmente "limpos" ou "sujos"), escolher arbitrariamente um dos candidatos restantes (por exemplo, o primeiro encontrado ou baseado na ordem alfabética do caminho completo).
> A função principal deve receber um `DuplicateGroup` e retornar o `FileMetadata` do arquivo escolhido para ser mantido.]

## Diretrizes para Geração da Especificação

1. **Clareza e Precisão:** A especificação deve ser inequívoca e fácil de entender por um desenvolvedor (ou pelo agente Tocle).
2. **Detalhamento:** Descreva os passos lógicos necessários para implementar a funcionalidade.
3. **Referência às Interfaces:** Quando o processamento envolver a interação com outros módulos, refira-se explicitamente às interfaces listadas no "Contexto Arquitetural". (Neste caso, focar no uso das Estruturas de Dados).
4. **Inputs e Outputs:** Detalhe claramente os inputs esperados (parâmetros, tipos de dados) e os outputs (valores de retorno, tipos, efeitos colaterais).
5. **Regras de Negócio:** Incorpore todas as regras de negócio mencionadas na descrição de alto nível (data, nome, desempate).
6. **Tratamento de Erros:** Especifique os principais cenários de erro mencionados ou implícitos e como devem ser tratados (ex: grupo inválido). Sugira exceções apropriadas a serem levantadas ou tratadas.
7. **Casos de Borda:** Mencione casos de borda óbvios a serem considerados (ex: grupo com apenas 2 arquivos, empates em critérios).
8. **Formato Adequado:** Use linguagem clara, listas ou passos numerados se apropriado, para facilitar a leitura e implementação. A saída deve ser adequada para colar diretamente na seção "Especificação..." do `Prompt_Tocle`.

## Resultado Esperado

> Um bloco de texto contendo a **Especificação Técnica Detalhada** da funcionalidade, pronta para ser usada no prompt do Tocle. O texto deve detalhar:
> - Inputs exatos (com tipos, se possível inferir da arquitetura).
> - Passos lógicos do processamento, incluindo chamadas às interfaces de dependência (se houver).
> - Outputs exatos (com tipos, se possível inferir da arquitetura).
> - Regras de negócio aplicadas.
> - Tratamento de erro especificado.
> - Casos de borda mencionados.

---

**(Início da Saída Gerada para Tocle)**

Implementar a função `decide_file_to_keep` no arquivo `fotix/src/fotix/core/decision_logic.py`. Esta função será responsável por selecionar qual arquivo manter de um grupo de duplicatas.

**Função Principal:** `decide_file_to_keep(group: DuplicateGroup) -> FileMetadata`

**Inputs:**

- `group`: Um objeto `DuplicateGroup` contendo:
    - `files`: Uma lista de objetos `FileMetadata` (com `path`, `size`, `creation_time`) representando os arquivos duplicados idênticos. A lista deve conter pelo menos 2 arquivos.
    - `hash_value`: O hash comum aos arquivos do grupo.

**Processamento:**

1.  **Validação de Entrada:**
    *   Verificar se `group` não é `None`.
    *   Verificar se `group.files` não é `None` e contém pelo menos 2 instâncias de `FileMetadata`.
    *   Se qualquer uma dessas verificações falhar, levantar uma exceção `ValueError` com uma mensagem descritiva (ex: "O grupo de duplicatas deve conter pelo menos dois arquivos para decisão.").

2.  **Inicialização:**
    *   Copiar a lista `group.files` para uma lista de trabalho `candidates` para não modificar o objeto original (se necessário, embora `FileMetadata` seja frozen).

3.  **Critério 1: Data de Criação Mais Antiga:**
    *   Encontrar o valor mínimo de `creation_time` entre todos os arquivos em `candidates`.
    *   Filtrar a lista `candidates`, mantendo apenas os arquivos que possuem o `creation_time` mínimo encontrado.
    *   Se, após esta filtragem, restar apenas 1 arquivo em `candidates`, este é o arquivo escolhido. Retornar este `FileMetadata`.

4.  **Critério 2: Nome de Arquivo "Limpo":**
    *   Se mais de 1 arquivo permanecer em `candidates` após o Critério 1:
        *   Definir uma lista de padrões de nomes de arquivo indicativos de cópias (ex: `r'\((\d+)\)$'`, `r' - C[oó]pia( \d+)?$'`, `r'_copy(\d+)?$'`). Os padrões devem ser aplicados ao *stem* (nome sem extensão) do arquivo.
        *   Criar uma sub-lista `clean_name_candidates` contendo apenas os arquivos de `candidates` cujo `path.stem` *não* corresponda a nenhum dos padrões de cópia.
        *   **Se** a lista `clean_name_candidates` contiver exatamente 1 arquivo, este é o arquivo escolhido. Retornar este `FileMetadata`.
        *   **Se** a lista `clean_name_candidates` contiver mais de 1 arquivo (múltiplos candidatos com nomes "limpos" e mesma data antiga), prosseguir para o Critério 3 usando *apenas* os arquivos de `clean_name_candidates`.
        *   **Se** a lista `clean_name_candidates` estiver vazia (todos os candidatos restantes têm nomes que parecem cópias), prosseguir para o Critério 3 usando a lista `candidates` original (antes da filtragem por nome).

5.  **Critério 3: Desempate Final:**
    *   Se mais de 1 arquivo permanecer na lista de candidatos atual (`clean_name_candidates` se não vazia e com mais de 1 elemento, ou `candidates` caso contrário):
        *   Ordenar os candidatos restantes alfabeticamente com base no caminho completo (`file.path`).
        *   Selecionar o primeiro arquivo da lista ordenada. Este é o arquivo escolhido. Retornar este `FileMetadata`.

**Outputs:**

- Um objeto `FileMetadata` representando o arquivo único selecionado para ser mantido dentro do grupo de duplicatas.

**Tratamento de Erros:**

- Levantar `ValueError` se o `group` de entrada for inválido (nulo, ou `group.files` nulo ou com menos de 2 arquivos).

**Casos de Borda:**

- Grupo com exatamente 2 arquivos.
- Todos os arquivos no grupo têm o mesmo `creation_time`.
- Todos os arquivos com a data mais antiga têm nomes que indicam cópias.
- Múltiplos arquivos têm a data mais antiga e nomes "limpos" (requer desempate final).
- Nomes de arquivos contendo os padrões de cópia em locais inesperados (garantir que a lógica de regex/string matching seja robusta).