# AGV Prompt Template: ImplementadorMestre v1.5 - Implementação Autônoma Guiada

**Tarefa Principal:** Implementar ou modificar o componente lógico alvo especificado abaixo, utilizando o Blueprint Arquitetural como guia. Criar ou modificar autonomamente os módulos base necessários (models, utils, config, interfaces) conforme as definições do blueprint e boas práticas. **Gerar testes unitários OBRIGATÓRIOS para TODO código novo ou modificado (tanto no módulo principal quanto nos módulos base/utils).** Interagir com o Coordenador via "Propor e Confirmar" apenas para ambiguidades na lógica principal.

**Contexto Essencial (Fornecido pelo Coordenador):**

1.  **Funcionalidade/Componente Alvo Principal:** `Item 1: fotix.infrastructure.logging_config`
2.  **Blueprint Arquitetural:** `@Output_BluePrint_Arquitetural_Tocrisna_v3.md`
3.  **Ordem e Descrições Iniciais:** `@Output_Ordem_Para_Implementacao_Geral.md`
4.  **Contexto Adicional do Workspace:** Caso necessário, fique a vontade para consultar nossa codebase.

**Instruções Detalhadas para a IA (Cursor/Augment):**

1.  **Identificar Alvo e Descrição Inicial:** Extraia o Alvo Principal. Encontre sua Descrição Inicial no `@Output_Ordem_Para_Implementacao_Geral.md`.
2.  **Analisar Blueprint e Contexto:** Consulte `@Output_BluePrint_Arquitetural_Tocrisna_v3.md` e o código existente (`@`) para entender localização, interfaces, modelos, dependências.
3.  **Gerenciar Módulos Base Autonomamente:**
    *   Determine Módulos Base necessários.
    *   Se criar/modificar, siga as Diretrizes 3.1 e **gere testes unitários para eles (ver Diretriz 7)**.
    *   Utilitários (`utils`): Adicione funções organicamente. **Gere testes unitários para elas (ver Diretriz 7)**.
    *   Não peça confirmação para ações padrão em módulos base/utils, a menos que haja conflito/ambiguidade extrema no Blueprint.

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

4.  **Refinar Requisitos da Lógica Principal (Se Estritamente Necessário):** Use "Propor e Confirmar" só para ambiguidades na LÓGICA/FLUXO principal do alvo.
5.  **Implementar Módulo Alvo Principal:** Escreva o código nos arquivos corretos. Crie diretórios necessários.
6.  **Aplicar Boas Práticas (Módulo Principal):** Código Limpo (PEP 8, KISS, SRP), Type Hints (PEP 484), Docstrings (PEP 257), Tratamento de Erros robusto.
7.  **Gerar Testes Unitários - MANDATÓRIO E ABRANGENTE:**
    *   **É OBRIGATÓRIO gerar testes unitários (`pytest`) para TODO o código de produção novo ou significativamente modificado nesta execução.** Isso inclui:
        *   Funções/métodos públicos do **Módulo Alvo Principal**.
        *   Funções/classes adicionadas ou modificadas nos **Módulos Base** (ex: `models.py`, `config.py`).
        *   Funções adicionadas ou modificadas em **`fotix.utils.helpers.py`**.
    *   **Não omita testes** para nenhum artefato de código gerado, mesmo que pareçam simples. A diretriz de testes é **absoluta**.
    *   Os testes devem cobrir casos relevantes (sucesso, erro, borda).
    *   Use **mocks** para isolar o código sob teste de suas dependências externas (aplicável principalmente aos testes do Módulo Alvo Principal e talvez Infraestrutura).
    *   Coloque os testes na estrutura `tests/unit/` correspondente (criando diretórios se necessário).
8.  **Gerar Relatório Detalhado:** Ao final, forneça um relatório claro resumindo:
    *   O que foi implementado/modificado no **Módulo Alvo Principal**.
    *   Quais **Módulos Base ou `utils`** foram **criados ou modificados**, listando as principais adições/alterações E **confirmando que testes unitários foram gerados para eles**.
    *   Quais arquivos foram criados/alterados no total (código e teste).
    *   Quaisquer suposições ou decisões importantes tomadas autonomamente.

**Resultado Esperado:**

*   Código Python de produção implementado/modificado (Módulo Principal + Módulos Base/Utils impactados).
*   Código Python de testes unitários **correspondentes a todo o código gerado**.
*   Relatório detalhado da implementação, confirmando a criação dos testes para todos os módulos.