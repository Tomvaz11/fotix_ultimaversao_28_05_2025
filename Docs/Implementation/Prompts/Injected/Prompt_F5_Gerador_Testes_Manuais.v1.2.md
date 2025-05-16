# AGV Prompt Template: Geração de Cenários de Teste de Aceitação do Usuário (UAT) / E2E Manuais (v1.2)

**Tarefa Principal:** Com base nos artefatos do projeto especificados abaixo (Blueprint Arquitetural e Ordem de Implementação), gerar uma lista detalhada de cenários de teste manuais. Estes cenários devem permitir ao Coordenador (usuário humano) validar as funcionalidades principais da aplicação da perspectiva de um usuário final, cobrindo os fluxos de trabalho essenciais de ponta a ponta (End-to-End).

**Artefatos do Projeto para Análise (A SER PREENCHIDO PELO COORDENADOR - APENAS NOMES DOS ARQUIVOS):**

1.  **Blueprint Arquitetural Detalhado:** `@Output_BluePrint_Arquitetural_Tocrisna_v3.md`
    *   *(Instrução para Coordenador: Substitua pelo nome exato do arquivo do Blueprint Arquitetural validado do projeto atual.)*
2.  **Ordem de Implementação e Pontos de Teste:** `@Output_Ordem_Para_Implementacao_Geral.md`
    *   *(Instrução para Coordenador: Substitua pelo nome exato do arquivo da Ordem de Implementação e Pontos de Teste gerado pelo OrchestratorHelper.)*

**Instruções Detalhadas para a IA:**

1.  **Extração de Contexto e Análise dos Artefatos:**
    *   **DERIVE o Nome do Projeto, o Objetivo Principal do Projeto e o Tipo de Interface Principal com o Usuário** a partir do conteúdo dos arquivos `@NOME_DO_ARQUIVO_BLUEPRINT.MD` e `@NOME_DO_ARQUIVO_ORDEM.MD`.
    *   Estude minuciosamente o `@NOME_DO_ARQUIVO_BLUEPRINT.MD` para entender a arquitetura geral, os principais serviços de aplicação, os componentes do core/domínio e da infraestrutura relevantes para a interação com o usuário.
    *   Revise o `@NOME_DO_ARQUIVO_ORDEM.MD` para identificar as funcionalidades chave que foram implementadas e os fluxos de trabalho que a aplicação deve suportar.

2.  **Identificação de Fluxos de Usuário Críticos:**
    *   Com base na sua análise, identifique as jornadas de usuário mais críticas e completas para o projeto inferido.
    *   Priorize cenários que testem a integração de múltiplas funcionalidades e componentes chave (end-to-end), refletindo o uso real da aplicação.

3.  **Geração dos Cenários de Teste Manuais:**
    *   Para cada fluxo de usuário crítico identificado, gere um cenário de teste manual detalhado.
    *   **Cada cenário de teste DEVE seguir a seguinte estrutura MANDATÓRIA:**
        *   **ID do Cenário:** (Formato: `UAT_[NOME_PROJETO_CURTO_INFERIDO]_XXX`, onde XXX é um número sequencial)
        *   **Título do Cenário:** Um nome claro e conciso que descreva o objetivo do teste.
        *   **Objetivo do Teste:** Uma breve descrição do que este cenário visa validar na aplicação.
        *   **Módulos/Funcionalidades Principais Envolvidas:** Liste os principais componentes/serviços do projeto (conforme Blueprint) que são exercitados neste cenário.
        *   **Pré-condições:** Quaisquer condições que devem ser verdadeiras antes de iniciar o teste.
        *   **Dados de Teste Sugeridos (se aplicável):** Descreva uma sugestão de dados de entrada, configurações ou estado do sistema que o Coordenador pode preparar para este teste. Seja específico para o domínio do projeto inferido.
        *   **Passos para Execução:** Uma lista numerada e detalhada de cada ação que o usuário (Coordenador) deve realizar na interface do projeto (seja ela GUI, CLI, API, etc., conforme inferido).
        *   **Resultado Esperado (para cada passo ou grupo de passos chave):** O que o usuário deve observar ou qual deve ser o estado do sistema após a execução do(s) passo(s).
        *   **Critério de Passagem Geral:** Uma declaração concisa de como determinar se o cenário de teste completo foi bem-sucedido.

4.  **Cobertura de Cenários:**
    *   Gere um número razoável de cenários de teste principais (sugestão: 5 a 10, dependendo da complexidade do projeto inferido) que cubram os fluxos mais importantes e representativos.
    *   Se possível, inclua cenários que testem o tratamento de erros comuns ou condições de borda que um usuário poderia encontrar.
    *   4.1.  **Quantidade e Diversidade Específica de Cenários:**
        *   Por favor, gere entre 10 e 12 cenários de teste de aceitação.
        *   Certifique-se de incluir cenários que cubram o tratamento de erros, operações com grandes volumes, cancelamento de operações e diferentes estratégias de seleção, além dos fluxos principais.

5.  **Formato do Output:**
    *   Apresente os cenários de teste em **Markdown**, usando a estrutura detalhada no item 3.
    *   Organize os cenários de forma lógica e fácil de seguir.

**Lembretes para a IA:**
*   Adapte suas sugestões ao Tipo de Interface Principal com o Usuário que você inferiu.
*   Foque na perspectiva do usuário final interagindo com a aplicação.
*   Os passos devem ser acionáveis e os resultados observáveis/verificáveis.
*   A clareza e a completude de cada cenário são mais importantes do que a quantidade total de cenários.