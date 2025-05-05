# AGV Prompt Template: ImplementadorMestre v1.4 - Implementação Autônoma Guiada

**Tarefa Principal:** Implementar ou modificar o componente lógico alvo especificado abaixo, utilizando o Blueprint Arquitetural como guia. Criar ou modificar autonomamente os módulos base necessários (models, utils, config, interfaces) conforme as definições do blueprint e as **diretrizes de boas práticas para módulos base** definidas abaixo. Interagir com o Coordenador via "Propor e Confirmar" apenas se houver ambiguidade significativa na lógica de negócio ou fluxo principal do alvo. Gerar código de produção e testes unitários de alta qualidade.

**Contexto Essencial (Fornecido pelo Coordenador):**

1.  **Funcionalidade/Componente Alvo Principal:** `Item 1: fotix.infrastructure.logging_config`
2.  **Blueprint Arquitetural:** `@Output_BluePrint_Arquitetural_Tocrisna_v3.md`
3.  **Ordem e Descrições Iniciais:** `@Output_Ordem_Para_Implementacao_Geral.md`
4.  **Contexto Adicional do Workspace:** Caso necessário, fique a vontade para consultar nossa codebase.

**Instruções Detalhadas para a IA (Cursor/Augment):**

1.  **Identificar Alvo e Descrição Inicial:** Extraia o Nome do Módulo Principal Alvo. Encontre sua "Descrição de Alto Nível Inicial" no arquivo `@Output_Ordem_Para_Implementacao_Geral.md` e use como ponto de partida.
2.  **Analisar Blueprint e Contexto:** Consulte **intensivamente** o `@Output_BluePrint_Arquitetural_Tocrisna_v3.md` e o `@Output_Ordem_Para_Implementacao_Geral.md` e o código existente anexado (`@`) para entender a localização, interfaces, modelos e dependências do Módulo Alvo Principal.
3.  **Gerenciar Módulos Base Autonomamente:**
    *   Determine quais Módulos Base (`models`, `config`, `utils`, `interfaces`) são necessários como dependência.
    *   Se precisar criar/modificar um Módulo Base, faça-o **seguindo as Diretrizes para Módulos Base (item 3.1 abaixo)** e as definições do Blueprint (se houver detalhes lá).
    *   Utilitários (`utils`): Se identificar lógica genérica, adicione a `fotix.utils.helpers.py`.
    *   **NÃO peça confirmação** para criar/modificar módulos base ou `utils` padrão, a menos que haja ambiguidade significativa ou conflito no Blueprint.

    **3.1. Diretrizes Específicas para Módulos Base (Models, Utils, Config, Interfaces):**
        *   **`Models` (`fotix.domain.models`):**
            *   Use **Pydantic `BaseModel`** (preferencial) ou `dataclasses` para definir estruturas claras.
            *   Aplique **Type Hints** rigorosos a todos os campos.
            *   Mantenha os modelos focados em **dados**, evitando lógica de negócio complexa dentro deles.
            *   Adicione **Docstrings** claras para cada modelo e campo importante.
        *   **`Utils` (`fotix.utils.helpers`):**
            *   Crie funções **pequenas, puras e com responsabilidade única (SRP)**.
            *   Garanta que **NÃO tenham dependências** de outros módulos internos do `fotix`.
            *   Use **Type Hints** e **Docstrings** claras.
            *   Inclua testes unitários simples para a lógica das funções em `tests/unit/utils/`.
        *   **`Config` (`fotix.config`):**
            *   Implemente uma forma simples de carregar/salvar configurações (ex: JSON, INI).
            *   Forneça acesso fácil e tipado às configurações.
            *   Evite lógica complexa neste módulo.
        *   **`Interfaces` (`*.interfaces.py`):**
            *   Use `typing.Protocol` (preferencial) ou `abc.ABC` para definir interfaces formais.
            *   Defina **assinaturas de métodos claras** com **Type Hints**.
            *   Use **Docstrings** para explicar o propósito da interface e de cada método.
            *   Mantenha as interfaces **mínimas e focadas** no contrato necessário.

4.  **Refinar Requisitos da Lógica Principal (Se Estritamente Necessário):** Se a Descrição Inicial + Blueprint forem ambíguos **especificamente sobre a LÓGICA DE NEGÓCIO ou FLUXO principal** do Módulo Alvo, use "Propor e Confirmar".
5.  **Implementar Módulo Alvo Principal:** Escreva o código nos arquivos corretos. Crie diretórios necessários.
6.  **Aplicar Boas Práticas (Módulo Principal):** Siga as diretrizes AGV: Código Limpo (PEP 8, KISS, SRP), Type Hints (PEP 484), Docstrings (PEP 257), Tratamento de Erros robusto.
7.  **Gerar Testes Unitários:** **OBRIGATÓRIO:** Crie testes (`pytest`) para novas funcionalidades/modificações no **módulo principal E nos módulos base/utils** que foram criados/modificados. Use **mocks** para isolar dependências externas ao módulo principal. Coloque em `tests/unit/` correspondente.
8.  **Gerar Relatório Detalhado:** Resuma o Módulo Alvo Principal. Detalhe quais **Módulos Base/Utils** foram criados/modificados e as principais alterações/adições neles. Liste arquivos totais alterados/criados. Mencione suposições chave.

**Resultado Esperado:**

*   Código Python de produção implementado/modificado (Módulo Principal + Módulos Base/Utils impactados).
*   Código Python de testes unitários correspondentes.
*   Relatório detalhado da implementação, incluindo ações nos módulos base/utils.