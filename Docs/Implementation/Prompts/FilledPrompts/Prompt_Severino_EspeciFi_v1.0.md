Este prompt foi criado para orientar uma LLM — neste caso, você, no papel do agente "Severino" — na execução da função de um especificador funcional, conforme descrito a seguir.

---

# AGV Prompt Template: Severino v1.0 - Especificação Funcional Detalhada

## Tarefa Principal

> Detalhar a especificação técnica para a funcionalidade/módulo descrito abaixo, baseando-se no contexto arquitetural fornecido.  
> O resultado deve ser formatado de forma clara e precisa, pronto para ser usado na seção "Especificação da Funcionalidade/Módulo a ser Implementada" do prompt do agente Tocle.

## Contexto do Projeto e Arquitetura (Definido por Fases Anteriores)

- **Nome do Projeto:** `Fotix`
- **Objetivo Geral do Projeto:**  
  > Aplicativo desktop desenvolvido em Python, com backend robusto e interface gráfica (GUI) completa, projetado para localizar e remover arquivos duplicados (idênticos) de imagens e vídeos em múltiplos diretórios e arquivos ZIP.
- **Blueprint Arquitetural Relevante (Definido por Tocrisna):**
  - **Módulo/Arquivo Alvo desta Especificação:** `fotix/src/fotix/core/duplicate_finder.py`
  - **Principais Responsabilidades deste Módulo/Arquivo (Conforme Arquitetura):**  
    > Implementar a lógica central de identificação de duplicatas. Contém a lógica de comparação, a estratégia de pré-filtragem por tamanho, e o agrupamento por hash. Define as estruturas de dados canônicas para representar arquivos, duplicatas e resultados. Deve ser independente de UI e I/O direto. (Nota: A lógica de *decisão* sobre qual arquivo manter reside em `decision_logic.py`).
  - **Interfaces de Dependências (Contratos a serem Usados por este Módulo):**
    - `hash_function: callable`: Uma função (provida pela camada de Aplicação) que aceita `FileMetadata` como entrada e retorna uma string representando o hash BLAKE3 do conteúdo do arquivo correspondente. A implementação desta função (que usará a camada de Infraestrutura para ler o arquivo) é responsabilidade do chamador.
    - `file_iterator: Iterator[FileMetadata]`: Um iterador (provido pela camada de Aplicação, populado pela Infraestrutura) que fornece instâncias de `FileMetadata` para os arquivos a serem analisados.
  - **Interfaces Expostas (Contratos Fornecidos por este Módulo):**
    - Classe `DuplicateFinder` com método público:  
      `find_duplicates(self, file_iterator: Iterator[FileMetadata], hash_function: callable) -> List[DuplicateGroup]`
  - **Estruturas de Dados Relevantes (Definidas pela Arquitetura):**

    ```python
    from dataclasses import dataclass, field
    from pathlib import Path
    from typing import List, Dict, Optional, Iterator

    @dataclass(frozen=True)
    class FileMetadata:
        path: Path
        size: int
        creation_time: float # Timestamp UTC

    @dataclass
    class DuplicateGroup:
        files: List[FileMetadata] # Lista de arquivos idênticos
        file_to_keep: Optional[FileMetadata] = None # Decidido pelo Core (Nota: Decidido por decision_logic.py, não por DuplicateFinder)
        hash_value: str # Hash que identifica o grupo
    ```

## Descrição de Alto Nível da Funcionalidade (Fornecida por Você)

> Implementar a lógica principal que recebe uma lista (iterador) de informações sobre arquivos (caminho, tamanho, data de criação) e uma função externa para calcular o hash de um arquivo.  
> O objetivo é primeiro agrupar eficientemente esses arquivos por tamanho. Em seguida, para os grupos que contêm mais de um arquivo (potenciais duplicatas), deve-se usar a função de hash fornecida para calcular o hash de cada arquivo nesses grupos.  
> Finalmente, agrupar os arquivos pelo hash calculado e retornar uma lista de grupos onde cada grupo contém apenas os arquivos com o mesmo hash (representando as duplicatas encontradas).  
> O processo deve ser robusto a possíveis erros na função de hash para arquivos individuais, pulando o arquivo problemático e continuando a análise.

## Diretrizes para Geração da Especificação

1. **Clareza e Precisão:** A especificação deve ser inequívoca e fácil de entender por um desenvolvedor (ou pelo agente Tocle).  
2. **Detalhamento:** Descreva os passos lógicos necessários para implementar a funcionalidade.  
3. **Referência às Interfaces:** Quando o processamento envolver a interação com outros módulos, refira-se explicitamente às interfaces listadas no "Contexto Arquitetural".  
4. **Inputs e Outputs:** Detalhe claramente os inputs esperados (parâmetros, tipos de dados) e os outputs (valores de retorno, tipos, efeitos colaterais).  
5. **Regras de Negócio:** Incorpore todas as regras de negócio mencionadas na descrição de alto nível (ex: pré-filtragem por tamanho, agrupamento por hash).  
6. **Tratamento de Erros:** Especifique os principais cenários de erro mencionados ou implícitos e como devem ser tratados (ex: erro ao calcular hash de um arquivo). Sugira exceções apropriadas a serem levantadas ou tratadas.  
7. **Casos de Borda:** Mencione casos de borda óbvios a serem considerados (ex: iterador vazio, nenhum arquivo duplicado encontrado).  
8. **Formato Adequado:** Use linguagem clara, listas ou passos numerados se apropriado, para facilitar a leitura e implementação. A saída deve ser adequada para colar diretamente na seção "Especificação..." do `Prompt_Tocle`.

## Resultado Esperado

> Um bloco de texto contendo a **Especificação Técnica Detalhada** da funcionalidade, pronta para ser usada no prompt do Tocle.  
> O texto deve detalhar:  
> - Inputs exatos (com tipos, se possível inferir da arquitetura).  
> - Passos lógicos do processamento, incluindo chamadas às interfaces de dependência.  
> - Outputs exatos (com tipos, se possível inferir da arquitetura).  
> - Regras de negócio aplicadas.  
> - Tratamento de erro especificado.  
> - Casos de borda mencionados.

## Especificação Técnica Detalhada (Gerada para Tocle)

**Módulo/Classe Alvo:** Classe `DuplicateFinder` no arquivo `fotix/src/fotix/core/duplicate_finder.py`.

**Método Principal:**  
`find_duplicates(self, file_iterator: Iterator[FileMetadata], hash_function: callable) -> List[DuplicateGroup]`

**Inputs:**

- `file_iterator`: Um iterador que produz objetos `FileMetadata` (contendo `path`, `size`, `creation_time`). Este iterador é fornecido pela camada de Aplicação.
- `hash_function`: Uma função (callable) fornecida pela camada de Aplicação. Espera-se que esta função receba um objeto `FileMetadata` como argumento e retorne uma string representando o hash BLAKE3 do conteúdo do arquivo correspondente. A função deve encapsular qualquer lógica de I/O necessária (provavelmente chamando a camada de Infraestrutura) e tratar seus próprios erros de I/O internos, possivelmente levantando uma exceção específica se o hash não puder ser calculado para um determinado arquivo.

**Processamento:**

1. Inicializar um dicionário `files_by_size: Dict[int, List[FileMetadata]]` para agrupar metadados de arquivos pelo tamanho (`size`).
2. Iterar sobre `file_iterator`:
   - Para cada `file_metadata` obtido, adicionar `file_metadata` à lista correspondente à sua `file_metadata.size` no dicionário `files_by_size`.
3. Inicializar uma lista vazia `duplicate_groups: List[DuplicateGroup]`.
4. Inicializar um dicionário `hash_map: Dict[str, List[FileMetadata]]` para agrupar arquivos pelo seu hash dentro de cada grupo de tamanho.
5. Iterar sobre os valores (listas de `FileMetadata`) no dicionário `files_by_size`:
   - Para cada lista `potential_duplicates` onde `len(potential_duplicates) > 1`:
     - Limpar `hash_map` para o grupo de tamanho atual.
     - Iterar sobre cada `file_metadata` em `potential_duplicates`:
       - Tentar calcular o hash chamando `hash_value = hash_function(file_metadata)`.
       - **Tratamento de Erro:**  
         Se a chamada a `hash_function` levantar uma exceção (ex: `IOError`, `PermissionError` encapsulada pela `hash_function`, ou uma exceção customizada indicando falha no hash), registrar um aviso (usando o sistema de logging padrão) informando que o hash não pôde ser calculado para `file_metadata.path` e pular para o próximo arquivo na lista `potential_duplicates`.  
         Não interromper o processo geral.
       - Se o hash for calculado com sucesso, adicionar `file_metadata` à lista correspondente a `hash_value` no `hash_map`.
     - Após processar todos os arquivos no grupo de tamanho atual, iterar sobre os valores (listas de `FileMetadata`) no `hash_map`:
       - Para cada lista `actual_duplicates` onde `len(actual_duplicates) > 1`:
         - Criar uma instância de `DuplicateGroup` com `files = actual_duplicates` e `hash_value =` (o hash correspondente a este grupo). O campo `file_to_keep` deve ser `None`.
         - Adicionar esta instância à lista `duplicate_groups`.
6. Retornar a lista `duplicate_groups`.

**Outputs:**

- Uma lista (`List[DuplicateGroup]`) contendo instâncias de `DuplicateGroup`. Cada `DuplicateGroup` representa um conjunto de 2 ou mais arquivos idênticos (mesmo tamanho e mesmo hash), contendo a lista dos `FileMetadata` desses arquivos e o valor do hash compartilhado.
- Retorna uma lista vazia se `file_iterator` estiver vazio, ou se nenhum grupo de arquivos idênticos (com 2 ou mais membros) for encontrado após a análise de tamanho e hash.

**Tratamento de Erros:**

- O método `find_duplicates` em si não deve levantar exceções de I/O, pois não realiza I/O direto.
- Deve capturar exceções levantadas pela `hash_function` fornecida durante o cálculo do hash para arquivos individuais.  
  Ao capturar tal exceção, deve logar um aviso e continuar o processamento com os arquivos restantes, excluindo o arquivo problemático da análise de duplicatas.

**Casos de Borda:**

- Considerar o caso de um `file_iterator` vazio: deve retornar uma lista vazia.
- Considerar o caso onde arquivos têm o mesmo tamanho, mas hashes diferentes: nenhum `DuplicateGroup` deve ser gerado para eles.
- Considerar o caso onde todos os arquivos são únicos (sem duplicatas por tamanho ou por hash): deve retornar uma lista vazia.
- O comportamento com arquivos de tamanho 0 deve ser tratado naturalmente pelo agrupamento (serão agrupados juntos se houver mais de um, e então hasheados).