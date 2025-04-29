```markdown
# AGV Prompt Template: Tocle v1.0 - Implementação de Código Novo

**Tarefa Principal:** Implementar a funcionalidade/módulo descrito na seção "Especificação" abaixo, criando ou modificando o arquivo Python `[NOME_DO_ARQUIVO_A_SER_CRIADO_OU_MODIFICADO.py]`. Siga rigorosamente as diretrizes e o contexto arquitetural fornecido.

**Contexto Arquitetural (Definido por Tocrisna / Fase Anterior):**

*   **Nome do Projeto:** `[NOME_DO_PROJETO]`
*   **Objetivo Geral do Projeto:** `[BREVE DESCRIÇÃO DO PROPÓSITO GERAL DO PROJETO]`
*   **Localização deste Módulo/Arquivo:** `[CAMINHO/PASTA/ONDE/ESTE/ARQUIVO/DEVE_FICAR.py]`
*   **Principais Responsabilidades deste Módulo/Arquivo:** `[DESCRIÇÃO CONCISA DO QUE ESTE ARQUIVO DEVE FAZER, CONFORME ARQUITETURA]`
*   **Interfaces de Dependências (Contratos a serem Usados):**
    *   `[FORNECER AQUI AS ASSINATURAS E DESCRIÇÕES DAS FUNÇÕES/MÉTODOS/CLASSES DE *OUTROS MÓDULOS* QUE ESTE CÓDIGO PRECISA CHAMAR. SEJA PRECISO. Exemplos:]`
    *   `utils.helpers.calcular_hash(file_path: Path) -> str`: Calcula e retorna o hash xxhash de um arquivo.
    *   `core.database.UserRepository.get_user_by_id(user_id: int) -> Optional[User]`: Busca um usuário no DB pelo ID. Retorna um objeto User ou None.
    *   `api_client.ExternalService.send_data(data: Dict) -> bool`: Envia dados para um serviço externo. Retorna True em sucesso.
    *   `[Se não houver dependências externas diretas, indicar: Nenhuma dependência externa significativa definida pela arquitetura para esta implementação.]`
*   **Interfaces Expostas (Contratos a serem Fornecidos - se aplicável):**
    *   `[SE ESTE MÓDULO EXPÕE FUNÇÕES/CLASSES PARA OUTROS USarem, LISTAR SUAS ASSINATURAS ESPERADAS AQUI. Exemplo:]`
    *   `Classe 'DuplicateDetector' com método publico 'find_duplicates(directory_path: Path) -> Dict[str, List[Path]]'`
    *   `[Se for um script principal ou não expõe interface direta, indicar: N/A]`
*   **Padrões de Design Chave (Relevantes para esta Implementação):** `[PADRÕES RELEVANTES DA ARQUITETURA - Ex: 'Seguir padrão Repository', 'Usar Injeção de Dependência para DatabaseClient']`
*   **Estrutura de Dados Principal (Relevantes para esta Implementação):** `[DEFINIÇÃO DE CLASSES DE DADOS/NAMEDTUPLES RELEVANTES DEFINIDAS PELA ARQUITETURA QUE ESTE MÓDULO USARÁ OU RETORNARÁ]`

**Especificação da Funcionalidade/Módulo a ser Implementada:**

```
[DESCRIÇÃO DETALHADA DA FUNCIONALIDADE A SER IMPLEMENTADA. SEJA ESPECÍFICO:
- Quais inputs são esperados?
- Qual processamento deve ocorrer (referenciando as Interfaces de Dependências acima quando necessário)?
- Quais outputs ou efeitos colaterais são esperados (referenciando as Interfaces Expostas acima se aplicável)?
- Quais regras de negócio se aplicam?
- Quais casos de borda devem ser considerados?
- Exemplo: "Implementar a classe `DuplicateDetector` no arquivo `core/duplicate_detector.py`. Deve ter um método público `find_duplicates(directory_path: Path) -> Dict[str, List[Path]]`. Internamente, deve iterar pelos arquivos de imagem no `directory_path`, ignorar arquivos < 1KB, chamar `utils.helpers.calcular_hash()` para cada arquivo válido, agrupar caminhos por hash em um dicionário e retorná-lo. Deve tratar `FileNotFoundError` para o diretório e `PermissionError` ao ler arquivos."]
```

**Stack Tecnológica Permitida (Definida na Fase 1):**

*   **Linguagem:** Python `[VERSÃO - Ex: 3.10+]`
*   **Frameworks Principais:** `[LISTAR - Ex: Nenhum, Flask, Django]`
*   **Bibliotecas Essenciais:** `[LISTAR - Ex: Pillow, numpy, xxhash]` (Permitir importação apenas destas, das bibliotecas padrão Python e dos outros módulos do projeto definidos nas dependências, a menos que explicitamente instruído a adicionar nova dependência).

**Diretrizes Específicas de Implementação:**

1.  **Aderência Estrita às Interfaces:** Implementar a funcionalidade utilizando e expondo *exatamente* as interfaces definidas na seção "Contexto Arquitetural". Não faça chamadas a outros módulos não listados nas dependências.
2.  **Código Limpo e Legível (PEP 8):** Seguir rigorosamente o PEP 8 para formatação, nomenclatura e estilo. Priorizar clareza e simplicidade (KISS).
3.  **Modularidade e Coesão (SRP):** Criar funções e classes com responsabilidades únicas e bem definidas. Manter alta coesão dentro do módulo.
4.  **Type Hints (PEP 484):** Utilizar type hints completos e precisos para todas as funções, métodos, parâmetros e variáveis importantes.
5.  **Tratamento de Erros Robusto:**
    *   Antecipar e tratar erros potenciais (ex: I/O, dados inválidos, falhas de dependência, erros retornados pelas interfaces chamadas).
    *   Usar exceções específicas. Propagar ou tratar erros de forma clara.
    *   Utilizar `try/except/finally` e gerenciadores de contexto (`with`) apropriadamente.
6.  **Segurança Básica:**
    *   Validar e sanitizar todos os inputs externos ou não confiáveis (incluindo parâmetros recebidos).
    *   Evitar práticas inseguras comuns.
    *   Usar bibliotecas padrão e seguras para operações sensíveis.
7.  **Documentação (Docstrings PEP 257):** Escrever docstrings claras e completas para o módulo, classes, funções e métodos públicos (propósito, `Args`, `Returns`, `Raises`), referenciando os contratos de interface quando relevante. Comentar apenas lógica complexa.
8.  **Sem Código Morto/Desnecessário:** Implementar apenas o necessário para a funcionalidade especificada.
9.  **Testes Unitários:** **OBRIGATÓRIO:** Gerar testes unitários (usando `[NOME_DO_FRAMEWORK_DE_TESTE - Ex: pytest, unittest]`) para as funções/métodos públicos implementados. Os testes devem:
    *   Cobrir casos de sucesso e casos de erro básicos.
    *   **Utilizar mocks/stubs para simular as "Interfaces de Dependências"** (não chamar o código real de outros módulos).
    *   Verificar se os "Outputs Esperados" (retornos ou efeitos colaterais mockados) estão corretos.
    *   Colocar os testes em um arquivo correspondente na estrutura de testes (ex: `tests/unit/test_[nome_do_modulo].py`).
10. **Eficiência (Consideração):** Escrever código razoavelmente eficiente para a tarefa, sem otimização prematura.

**Resultado Esperado:**

1.  **Código Python Completo:** O conteúdo final do arquivo `[NOME_DO_ARQUIVO_A_SER_CRIADO_OU_MODIFICADO.py]` com a funcionalidade implementada.
2.  **Código de Testes Unitários:** O conteúdo do arquivo de teste correspondente (ex: `tests/unit/test_[nome_do_modulo].py`) com os testes unitários gerados, utilizando mocks para dependências.
3.  **(Opcional) Breve Relatório:** Explicação de decisões de implementação, desafios ou sugestões.

```

---

Este prompt agora formaliza a dependência das interfaces definidas pela arquitetura e instrui explicitamente a IA a usar mocks nos testes unitários, reforçando a abordagem de integração incremental e testes focados no módulo atual.