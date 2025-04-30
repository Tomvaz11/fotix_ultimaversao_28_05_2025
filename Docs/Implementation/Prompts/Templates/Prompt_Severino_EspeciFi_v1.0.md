# AGV Prompt Template: Severino v1.0 - Especificação Funcional Detalhada

## Tarefa Principal

Detalhar a especificação técnica para a funcionalidade/módulo descrito abaixo, baseando-se no contexto arquitetural fornecido. O resultado deve ser formatado de forma clara e precisa, pronto para ser usado na seção "Especificação da Funcionalidade/Módulo a ser Implementada" do prompt do agente Tocle.

## Contexto do Projeto e Arquitetura (Definido por Fases Anteriores)

- **Nome do Projeto:** `[NOME_DO_PROJETO]`
- **Objetivo Geral do Projeto:** `[BREVE DESCRIÇÃO DO PROPÓSITO GERAL DO PROJETO]`
- **Blueprint Arquitetural Relevante (Definido por Tocrisna):**
  - **Módulo/Arquivo Alvo desta Especificação:** `[CAMINHO/COMPLETO/DO/ARQUIVO_ALVO.py]`
  - **Principais Responsabilidades deste Módulo/Arquivo (Conforme Arquitetura):** `[COPIAR DESCRIÇÃO DA RESPONSABILIDADE DA ARQUITETURA]`
  - **Interfaces de Dependências (Contratos a serem Usados por este Módulo):**
    - `[COPIAR AS INTERFACES RELEVANTES DO BLUEPRINT DA TOCRISNA - Assinaturas e descrições das funções/métodos de outros módulos que este precisa chamar. Ex:]`
    - `utils.helpers.calcular_hash(file_path: Path) -> str`
    - `core.database.UserRepository.get_user_by_id(user_id: int) -> Optional[User]`
  - **Interfaces Expostas (Contratos Fornecidos por este Módulo):**
    - `[COPIAR AS INTERFACES RELEVANTES DO BLUEPRINT DA TOCRISNA - Assinaturas e descrições das funções/métodos públicos que este módulo deve expor. Ex:]`
    - `Classe 'DuplicateDetector' com método público 'find_duplicates(directory_path: Path) -> Dict[str, List[Path]]'`
  - **Estruturas de Dados Relevantes (Definidas pela Arquitetura):** `[COPIAR DEFINIÇÕES DE DATACLASSES/NAMEDTUPLES RELEVANTES DA ARQUITETURA]`

## Descrição de Alto Nível da Funcionalidade (Fornecida por Você)

> [COLE AQUI SUA DESCRIÇÃO EM LINGUAGEM NATURAL E CLARA DO QUE ESTA FUNCIONALIDADE ESPECÍFICA DEVE FAZER.  
> Exemplo: "Preciso que o DuplicateDetector encontre todas as fotos duplicadas dentro de uma pasta que o usuário escolher. Ele deve olhar só as imagens, ignorar as muito pequenas (tipo menos de 1KB), e me devolver uma lista mostrando quais arquivos são cópias uns dos outros. Se der erro ao abrir a pasta ou ler uma foto, ele não pode travar, tem que avisar e continuar."]

## Diretrizes para Geração da Especificação

1. **Clareza e Precisão:** A especificação deve ser inequívoca e fácil de entender por um desenvolvedor (ou pelo agente Tocle).
2. **Detalhamento:** Descreva os passos lógicos necessários para implementar a funcionalidade.
3. **Referência às Interfaces:** Quando o processamento envolver a interação com outros módulos, refira-se explicitamente às interfaces listadas no "Contexto Arquitetural".
4. **Inputs e Outputs:** Detalhe claramente os inputs esperados (parâmetros, tipos de dados) e os outputs (valores de retorno, tipos, efeitos colaterais).
5. **Regras de Negócio:** Incorpore todas as regras de negócio mencionadas na descrição de alto nível (ex: "ignorar arquivos < 1KB").
6. **Tratamento de Erros:** Especifique os principais cenários de erro mencionados ou implícitos e como devem ser tratados (ex: "Deve tratar `FileNotFoundError` para o diretório e `PermissionError` ao ler arquivos."). Sugira exceções apropriadas a serem levantadas ou tratadas.
7. **Casos de Borda:** Mencione casos de borda óbvios a serem considerados (ex: pasta vazia, nenhum arquivo duplicado encontrado).
8. **Formato Adequado:** Use linguagem clara, listas ou passos numerados se apropriado, para facilitar a leitura e implementação. A saída deve ser adequada para colar diretamente na seção "Especificação..." do `Prompt_Tocle`.

## Resultado Esperado

> Um bloco de texto contendo a **Especificação Técnica Detalhada** da funcionalidade, pronta para ser usada no prompt do Tocle. O texto deve detalhar:  
> - Inputs exatos (com tipos, se possível inferir da arquitetura).  
> - Passos lógicos do processamento, incluindo chamadas às interfaces de dependência.  
> - Outputs exatos (com tipos, se possível inferir da arquitetura).  
> - Regras de negócio aplicadas.  
> - Tratamento de erro especificado.  
> - Casos de borda mencionados.

## Exemplo de Saída Esperada (para o exemplo da descrição de alto nível)

> Implementar a classe `DuplicateDetector` no arquivo `core/duplicate_detector.py`.

**Método Principal:** `find_duplicates(self, directory_path: Path) -> Dict[str, List[Path]]`

**Inputs:**

- `directory_path`: Um objeto `Path` representando o diretório a ser escaneado.

**Processamento:**

1. Verificar se `directory_path` existe e é um diretório. Se não for, levantar `FileNotFoundError`.
2. Inicializar um dicionário vazio `hash_map` para armazenar `hash -> lista_de_paths`.
3. Iterar por todos os arquivos dentro de `directory_path` (recursivamente ou não, conforme definido pela arquitetura - assumindo não recursivo aqui).
4. Para cada arquivo encontrado:  
   a. Tentar obter o tamanho do arquivo. Se ocorrer `PermissionError` ou outro `OSError` ao acessar, logar um aviso e pular para o próximo arquivo.  
   b. Verificar se o tamanho do arquivo é >= 1024 bytes (1KB). Se for menor, pular para o próximo arquivo.  
   c. Verificar se é um tipo de arquivo de imagem suportado (conforme definido pela arquitetura ou usar extensão comum como .jpg, .png, .gif - *Nota: Especificar tipos se a arquitetura definir*). Se não for, pular.  
   d. Tentar calcular o hash do arquivo chamando a interface `utils.helpers.calcular_hash(file_path)`. Se ocorrer erro durante o cálculo do hash (ex: erro de leitura), logar um aviso e pular.  
   e. Adicionar o `file_path` atual à lista de paths no `hash_map` correspondente ao hash calculado. Se o hash não existir como chave ainda, criá-lo com uma lista contendo o `file_path`.

5. Após iterar por todos os arquivos, filtrar o `hash_map`: manter apenas as entradas onde a lista de paths contém 2 ou mais arquivos (indicando duplicatas).
6. Retornar o dicionário `hash_map` filtrado.

**Outputs:**

- Um dicionário onde as chaves são strings de hash e os valores são listas de objetos `Path`, contendo apenas os grupos de arquivos com 2 ou mais ocorrências (duplicatas). Retorna um dicionário vazio se nenhuma duplicata for encontrada ou se a pasta estiver vazia/sem arquivos válidos.

**Tratamento de Erros:**

- Levantar `FileNotFoundError` se `directory_path` inicial não for um diretório válido.
- Capturar e logar `OSError` (como `PermissionError`) ao acessar arquivos individuais durante a iteração, continuando o processo para os demais arquivos.

**Casos de Borda:**

- Considerar o caso de diretório vazio.
- Considerar o caso de diretório sem arquivos de imagem válidos ou > 1KB.
- Considerar o caso onde nenhum arquivo possui duplicatas.