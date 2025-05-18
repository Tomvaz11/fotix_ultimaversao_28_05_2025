# AGV Prompt Template: Geração de Cenários de Teste de Aceitação do Usuário (UAT) / E2E Manuais (v1.2 - Foco no Escopo)

**Tarefa Principal:** Com base nos artefatos do projeto especificados abaixo (Blueprint Arquitetural e Ordem de Implementação), gerar uma lista detalhada de cenários de teste manuais. Estes cenários devem permitir ao Coordenador (usuário humano) validar as funcionalidades principais da aplicação da perspectiva de um usuário final, cobrindo os fluxos de trabalho essenciais de ponta a ponta (End-to-End) **estritamente conforme definido nos artefatos fornecidos.**

**Restrição Fundamental de Escopo:**
*   Os cenários de teste devem se ater **EXCLUSIVAMENTE** às funcionalidades, capacidades e fluxos de trabalho que estão explicitamente descritos ou podem ser diretamente inferidos a partir do `@NOME_DO_ARQUIVO_BLUEPRINT.MD` e do `@NOME_DO_ARQUIVO_ORDEM.MD`.
*   **NÃO INCLUA cenários para funcionalidades, melhorias ou níveis de granularidade que não estejam claramente definidos ou implicados nesses documentos de referência.** O objetivo é validar o que foi especificado e planejado para implementação, não sugerir novas funcionalidades.

**Artefatos do Projeto para Análise (A SER PREENCHIDO PELO COORDENADOR - APENAS NOMES DOS ARQUIVOS):**

1.  **Blueprint Arquitetural Detalhado:** `@Output_BluePrint_Arquitetural_Tocrisna_v3.md`
    *   *(Instrução para Coordenador: Substitua pelo nome exato do arquivo do Blueprint Arquitetural validado do projeto atual.)*
2.  **Ordem de Implementação e Pontos de Teste:** `@Output_Ordem_Para_Implementacao_Geral.md`
    *   *(Instrução para Coordenador: Substitua pelo nome exato do arquivo da Ordem de Implementação e Pontos de Teste gerado pelo OrchestratorHelper.)*

**Instruções Detalhadas para a IA:**

1.  **Extração de Contexto e Análise Focada dos Artefatos:**
    *   **DERIVE o Nome do Projeto, o Objetivo Principal do Projeto e o Tipo de Interface Principal com o Usuário** a partir do conteúdo dos arquivos `@NOME_DO_ARQUIVO_BLUEPRINT.MD` e `@NOME_DO_ARQUIVO_ORDEM.MD`.
    *   Estude minuciosamente os artefatos fornecidos para entender a arquitetura, os serviços de aplicação, os componentes do core/domínio e da infraestrutura, e os fluxos de trabalho **que foram planejados para implementação.**

2.  **Identificação de Fluxos de Usuário Críticos (Conforme Especificado):**
    *   Com base na sua análise dos artefatos, identifique as jornadas de usuário mais críticas e completas **que estão dentro do escopo definido.**
    *   Priorize cenários que testem a integração de múltiplas funcionalidades e componentes chave (end-to-end) que foram explicitamente delineados.

3.  **Geração dos Cenários de Teste Manuais (Estrutura Mandatória):**
    *   Para cada fluxo de usuário crítico identificado (e dentro do escopo), gere um cenário de teste manual detalhado.
    *   **Cada cenário de teste DEVE seguir a seguinte estrutura MANDATÓRIA:**
        *   **ID do Cenário:** (Formato: `UAT_[NOME_PROJETO_CURTO_INFERIDO]_XXX`, onde XXX é um número sequencial)
        *   **Título do Cenário:** Um nome claro e conciso que descreva o objetivo do teste.
        *   **Referência à Funcionalidade no Blueprint/Ordem:** (Liste brevemente as seções/componentes dos artefatos que este cenário visa testar).
        *   **Objetivo do Teste:** Uma breve descrição do que este cenário visa validar na aplicação, alinhado com a funcionalidade especificada.
        *   **Módulos/Funcionalidades Principais Envolvidas (Conforme Blueprint):** Liste os principais componentes/serviços do projeto (conforme Blueprint) que são exercitados neste cenário.
        *   **Pré-condições:** Quaisquer condições que devem ser verdadeiras antes de iniciar o teste.
        *   **Dados de Teste Sugeridos (se aplicável):** Descreva uma sugestão de dados de entrada, configurações ou estado do sistema que o Coordenador pode preparar para este teste. Seja específico para o domínio do projeto inferido e para a funcionalidade sendo testada.
        *   **Passos para Execução:** Uma lista numerada e detalhada de cada ação que o usuário (Coordenador) deve realizar na interface do projeto (seja ela GUI, CLI, API, etc., conforme inferido).
        *   **Resultado Esperado (para cada passo ou grupo de passos chave):** O que o usuário deve observar ou qual deve ser o estado do sistema após a execução do(s) passo(s), **baseado no comportamento esperado pela especificação.**
        *   **Critério de Passagem Geral:** Uma declaração concisa de como determinar se o cenário de teste completo foi bem-sucedido em validar a funcionalidade especificada.

4.  **Quantidade e Diversidade Específica de Cenários (Dentro do Escopo):**
    *   **Gere entre 10 e 12 cenários de teste de aceitação.**
    *   **Certifique-se de incluir cenários que cubram (conforme aplicável e definido nos artefatos):**
        *   Os principais fluxos de sucesso.
        *   Tratamento de erros comuns previstos nos artefatos (ex: caminhos inválidos).
        *   Operações com diferentes tipos de dados ou volumes (se especificado).
        *   Cancelamento de operações (se a capacidade de cancelamento for parte do design).
        *   Diferentes estratégias ou opções configuráveis (se detalhadas nos artefatos).

5.  **Formato do Output:**
    *   Apresente os cenários de teste em **Markdown**, usando a estrutura detalhada no item 3.
    *   Organize os cenários de forma lógica e fácil de seguir.

**Lembretes para a IA:**
*   Adapte suas sugestões ao Tipo de Interface Principal com o Usuário que você inferiu dos artefatos.
*   Foque na perspectiva do usuário final interagindo com a aplicação **conforme ela foi desenhada**.
*   Os passos devem ser acionáveis e os resultados observáveis/verificáveis **em relação ao que foi especificado.**
*   A clareza e a completude de cada cenário em validar o escopo definido são cruciais.
*   **Reiterando: Não introduza funcionalidades ou expectativas que não estejam fundamentadas nos artefatos fornecidos.**