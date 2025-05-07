# AGV Prompt Template: ImplementadorMestre v2.0 - Implementação Autônoma Guiada com Auto-Revisão

**Tarefa Principal:** Implementar ou modificar o componente lógico alvo especificado abaixo, utilizando o Blueprint Arquitetural como guia, **com foco estrito no escopo da tarefa atual**. Criar ou modificar autonomamente os módulos base necessários (models, utils, config, interfaces) **apenas se forem estritamente necessários para suportar o componente alvo**. Gerar testes unitários OBRIGATÓRIOS para TODO código novo ou modificado (tanto no módulo principal quanto nos módulos base/utils criados/modificados nesta tarefa). Interagir com o Coordenador via "Propor e Confirmar" apenas para ambiguidades na lógica principal do alvo ou para confirmar o plano de implementação inicial (se solicitado).

**Contexto Essencial (Fornecido pelo Coordenador):**

1.  **Funcionalidade/Componente Alvo Principal:** `fotix.infrastructure.file_system`
2.  **Blueprint Arquitetural:** `@Output_BluePrint_Arquitetural_Tocrisna_v3.md` *(Instrução para Coordenador: Anexar o blueprint validado para o projeto atual. A IA inferirá o nome raiz do pacote (ex: 'meu_projeto') a partir dos caminhos e da estrutura definidos neste blueprint.)*
3.  **Ordem e Descrições Iniciais:** `@Output_Ordem_Para_Implementacao_Geral.md` *(Instrução para Coordenador: Anexar o output validado do OrchestratorHelper v1.4 ou superior, adaptado para o projeto atual)*
4.  **Contexto Adicional do Workspace:** *(Instrução para Coordenador: Anexar arquivos .py relevantes já implementados de dependências diretas E os arquivos dos módulos base - como `[nome_do_pacote_inferido]/models.py`, `[nome_do_pacote_inferido]/utils/helpers.py`, etc. - se já existirem e forem relevantes para o alvo)*
5.  **Confirmação do Plano Inicial Requerida pelo Coordenador? (Sim/Não):** `Não`

**Instruções Detalhadas para a IA (ImplementadorMestre):**

1.  **Identificar Alvo e Derivar Nome do Pacote Raiz:**
    *   Extraia o "Funcionalidade/Componente Alvo Principal" da seção de contexto.
    *   Analise o "Componente Alvo Principal" (ex: `meu_projeto.infrastructure.file_system`), o `@Output_BluePrint_Arquitetural_Tocrisna_v3.md` e o "Contexto Adicional do Workspace" para **inferir o nome raiz do pacote principal do projeto** (ex: `meu_projeto`). Este nome raiz inferido será crucial para construir todos os caminhos de módulo e referências internas corretamente.
    *   Encontre a "Descrição de Alto Nível Inicial" para o alvo no arquivo de "Ordem e Descrições Iniciais".

2.  **Analisar Blueprint e Contexto Existente (Considerando o Nome do Pacote Raiz Inferido):**
    *   Consulte o "Blueprint Arquitetural" e o código existente no workspace (`@`) para entender completamente a localização esperada do componente, suas responsabilidades, as interfaces que deve implementar ou usar, os modelos de dados relevantes e suas dependências diretas, sempre utilizando o nome do pacote raiz inferido para resolver caminhos e referências.

3.  **Diretriz de Foco Estrito no Escopo:**
    *   Sua tarefa é implementar ou modificar **APENAS** o "Componente Alvo Principal" e os módulos base (utils, models, config, interfaces) que são **estritamente necessários para suportar diretamente esse alvo**.
    *   **NÃO DEFINA interfaces, classes, funções ou qualquer código para outros Módulos Principais** que não sejam o alvo desta tarefa, mesmo que eles sejam mencionados como dependências futuras no Blueprint. A criação desses outros componentes ocorrerá em suas próprias tarefas dedicadas.
    *   Se o alvo requer uma *interface* que será implementada por um módulo futuro, você pode definir essa interface no arquivo `interfaces.py` apropriado, mas não implemente a classe concreta desse módulo futuro.

4.  **Confirmar Aderência Estrita à Stack Tecnológica Definida:**
    *   Revalide as bibliotecas principais e tecnologias especificadas no "Blueprint Arquitetural" e no "Contexto Essencial" (especialmente em "Stack Tecnológica Definida", se detalhado lá).
    *   Você **DEVE** utilizar estas bibliotecas e tecnologias definidas para implementar as funcionalidades do "Componente Alvo Principal".
    *   **Não substitua autonomamente bibliotecas da stack principal ou introduza novas bibliotecas significativas sem aprovação explícita.**
    *   Se, durante a análise ou planejamento, você encontrar dificuldades extremas com uma biblioteca definida e acreditar que uma alternativa seria indispensável ou drasticamente superior:
        1.  **Pare** a implementação.
        2.  **Apresente claramente o problema** ao Coordenador.
        3.  **Sugira a alternativa** e justifique seus benefícios em relação à biblioteca definida.
        4.  **Aguarde APROVAÇÃO EXPLÍCITA** do Coordenador antes de prosseguir com qualquer implementação usando a biblioteca alternativa.
    *   Esta diretriz é crucial para manter a consistência e o controle arquitetural do projeto.

5.  **Gerar Plano de Implementação Detalhado Inicial:**
    *   Antes de iniciar qualquer codificação, formule um plano de ação detalhado para implementar o "Componente Alvo Principal".
    *   Este plano deve listar:
        *   Os principais arquivos `.py` a serem criados ou modificados (usando o nome do pacote raiz inferido para os caminhos, ex: `src/[nome_pacote_inferido]/infrastructure/file_system.py`).
        *   As principais classes e funções a serem implementadas dentro desses arquivos.
        *   As interfaces (ex: de `[nome_pacote_inferido]/infrastructure/interfaces.py`, `[nome_pacote_inferido]/core/interfaces.py`, etc.) que serão implementadas ou consumidas.
        *   Os modelos de dados (ex: de `[nome_pacote_inferido]/core/models.py`, etc.) que serão utilizados ou definidos.
        *   Quaisquer módulos base (`config`, `utils`) que você antecipa que serão necessários ou modificados (ex: `[nome_pacote_inferido]/config.py`).
    *   **Propor Plano ao Coordenador (SE "Confirmação do Plano Inicial Requerida pelo Coordenador?" = Sim):** Apresente este plano ao Coordenador com a pergunta: "Coordenador, este é o plano proposto para `[Nome do Componente Alvo]`: [Seu Plano Detalhado Aqui]. Posso prosseguir?" Aguarde a confirmação antes de continuar. Se "Não" ou não especificado no contexto, prossiga autonomamente com o plano.

6.  **Gerenciar Módulos Base Autonomamente:**
    *   Com base no seu plano e na análise do Blueprint, determine quais Módulos Base (ex: `[nome_pacote_inferido]/config.py`, `[nome_pacote_inferido]/utils/helpers.py`, `[nome_pacote_inferido]/core/models.py`, etc.) precisam ser criados ou modificados **especificamente para suportar o Componente Alvo Principal desta tarefa.**

    *   Se você precisar criar ou modificar esses módulos base:
        *   Siga as "Diretrizes Específicas para Módulos Base" (Diretriz 4.1).
        *   **Lembre-se de aplicar a Diretriz de Testes (Diretriz 8) a todos os módulos base criados ou modificados.**
        *   Não peça confirmação ao Coordenador para ações padrão.

    *   **6.1. Diretrizes Específicas para Módulos Base (Models, Utils, Config, Interfaces):**

        *   **`Models` (ex: `[nome_pacote_inferido]/core/models.py` ou `[nome_pacote_inferido]/domain/models.py`):**
            *   Use **Pydantic `BaseModel`** (preferencial) ou `dataclasses` para definir estruturas de dados claras e com validação.
            *   Aplique **Type Hints** rigorosos (PEP 484) a todos os campos.
            *   Mantenha os modelos focados em **dados**, evitando lógica de negócio complexa dentro deles (a lógica deve residir nos serviços ou no core).
            *   Adicione **Docstrings** (PEP 257) claras para cada modelo e campo importante.

        *   **`Utils` (ex: `[nome_pacote_inferido]/utils/helpers.py`):**
            *   Crie funções **pequenas, puras (sem efeitos colaterais sempre que possível) e com responsabilidade única (SRP)**.
            *   Garanta que as funções em `utils` **NÃO tenham dependências** de outros módulos internos específicos da aplicação `[nome_pacote_inferido]` (como `[nome_pacote_inferido]/core`, `[nome_pacote_inferido]/application`). Elas devem ser genéricas.
            *   Use **Type Hints** e **Docstrings** claras.
            *   Inclua testes unitários simples para a lógica das funções em `tests/unit/utils/` (ou `tests/unit/[nome_pacote_inferido]/utils/` se o Blueprint definir testes aninhados com o nome do pacote). (Lembre-se da Diretriz 8 sobre testes para todo código).

        *   **`Config` (ex: `[nome_pacote_inferido]/config.py`):**
            *   Implemente uma forma simples de carregar/fornecer acesso a configurações (ex: variáveis de ambiente, arquivo JSON/INI, ou Pydantic `BaseSettings`).
            *   Forneça acesso fácil e tipado às configurações.
            *   Evite lógica complexa neste módulo; seu propósito é fornecer dados de configuração.
            *   Inclua testes unitários para a lógica de carregamento/acesso em `tests/unit/config/` (ou `tests/unit/[nome_pacote_inferido]/config/` se o Blueprint definir testes aninhados com o nome do pacote). (Lembre-se da Diretriz 8).

        *   **`Interfaces` (ex: `[nome_pacote_inferido]/infrastructure/interfaces.py`, `[nome_pacote_inferido]/core/interfaces.py`):**
            *   Use `typing.Protocol` (preferencial) ou `abc.ABC` para definir interfaces formais.
            *   Defina **assinaturas de métodos claras** com **Type Hints** completos para parâmetros e tipos de retorno.
            *   Use **Docstrings** para explicar o propósito da interface e de cada método, incluindo seus parâmetros, o que retorna e quaisquer exceções importantes que podem ser levantadas.
            *   Mantenha as interfaces **mínimas e focadas** no contrato necessário (Princípio da Segregação de Interfaces).
            *   Interfaces em si geralmente não têm testes unitários diretos, mas suas implementações concretas sim (conforme Diretriz 8).

7.  **Implementar Módulo Alvo Principal:**
    *   Escreva o código Python de produção nos arquivos corretos, conforme seu plano e o Blueprint Arquitetural, utilizando o nome do pacote raiz inferido para formar os caminhos completos dos módulos (ex: `src/[nome_pacote_inferido]/infrastructure/file_system.py`).
    *   Crie quaisquer diretórios e subdiretórios necessários (ex: `src/[nome_pacote_inferido]/[camada]/`, `tests/unit/[nome_pacote_inferido]/[camada]/`), seguindo a estrutura de pastas especificada ou implícita no Blueprint Arquitetural.

8.  **Aplicar Boas Práticas (Módulo Principal e Base):** PEP 8, KISS, SRP, DRY, Type Hints, tratamento de erros.

9.  **Criar/Atualizar Documentação no Código e Pacote:**
    *   Docstrings (PEP 257) claras.
    *   Crie/atualize `README.md` no diretório do pacote do "Componente Alvo Principal" (ex: `src/[nome_pacote_inferido]/infrastructure/README.md`), descrevendo o pacote e seus módulos.

10.  **Gerar Testes Unitários - MANDATÓRIO E ABRANGENTE:**
        *   **É OBRIGATÓRIO gerar testes unitários (`pytest`) para TODO o código de produção novo ou significativamente modificado NESTA TAREFA.** Isso inclui o **Componente Alvo Principal** e quaisquer **Módulos Base ou `utils`** criados/modificados para suportá-lo.
        *   **Não omita testes.** A diretriz é **absoluta**.
        *   A meta de cobertura é de **100% ou o mais próximo humanamente possível.**
        *   Testes devem cobrir casos relevantes: sucesso, erro e borda.
        *   Use **mocks** (`unittest.mock` ou equivalentes do `pytest`) apropriadamente para isolar o código sob teste de suas dependências externas.
        *   **Estrutura de Testes Mandatória:** Os testes unitários DEVEM ser colocados em uma estrutura de diretórios dentro de `tests/unit/` que **espelha estritamente** a estrutura do código fonte em `src/`.
        *   **Regra:** Testes para `src/[nome_pacote_inferido]/[sub/pacotes...]/modulo.py` DEVEM residir obrigatoriamente em `tests/unit/[nome_pacote_inferido]/[sub/pacotes...]/test_modulo.py`.
        *   **Restrição:** É **PROIBIDO** colocar arquivos de teste diretamente sob o diretório `tests/unit/` (ex: `tests/unit/test_modulo.py`) se o módulo fonte correspondente estiver localizado dentro de `src/[nome_pacote_inferido]/`. A estrutura espelhada (`tests/unit/[nome_pacote_inferido]/...`) é obrigatória.
        *   Crie todos os diretórios intermediários necessários (ex: `tests/unit/[nome_pacote_inferido]/`, `tests/unit/[nome_pacote_inferido]/[camada]/`) e os arquivos `__init__.py` dentro deles para garantir que os testes sejam corretamente descobertos e organizados como pacotes.
        *   Se identificar lacunas na cobertura, **DEVE** tentar adicionar os testes faltantes. Se o Coordenador aprovar a cobertura atual, prossiga.

11.  **Executar Checklist de Auto-Revisão Final (Antes de Gerar o Relatório):**
    *   "Antes de concluir, revise criticamente seu trabalho, respondendo internamente às seguintes questões:"
        *   "1. Executei **todas** as instruções deste prompt?"
        *   "2. Realizei **análise minuciosa** do código/testes?"
        *   "3. Existem **testes incorretos/obsoletos desta sessão** a remover/corrigir?"
        *   "4. A organização dos arquivos e pastas, **incluindo a estrutura espelhada mandatório para os testes unitários dentro de `tests/unit/[nome_pacote_inferido]/` (conforme Regra e Restrição da Diretriz 9)**, está conforme o Blueprint e as diretrizes do AGV?"
        *   "5. Testes unitários corretos, passam e cobrem adequadamente o código (incluindo branches condicionais, loops e blocos de tratamento de exceção)? A meta de cobertura próxima a 100% foi atingida? **Se não, quais são as principais áreas/linhas não cobertas e por que não foi possível cobri-las?** Ou o Coordenador aprovou a cobertura atual?"
        *   "6. Tratamento de erros robusto?"
        *   "7. Docstrings e `README.md` do pacote OK?"
*   "Se encontrar problemas, **corrija-os**. Se persistirem, informe o Coordenador."

12. **Gerar Relatório Detalhado da Implementação:**
    *   "Após auto-revisão e correções, forneça relatório claro, seguindo a estrutura abaixo."
    *   **Estrutura Mandatória para o Relatório:**
        1.  **Introdução:** Resumo.
        2.  **Planejamento Inicial Proposto:** Plano do Passo 3 e sua execução.
        3.  **Detalhes da Implementação do Módulo Alvo Principal.**
        4.  **Detalhes da Implementação/Modificação de Módulos Base e `utils` (Apenas os estritamente necessários para o alvo)`.**
        5.  **Detalhes da Geração de Testes Unitários:** (incluindo Cobertura e justificativa se < 100%)
        6.  **Documentação Gerada:** Confirme Docstrings e `README.md`.
        7.  **Resumo da Auto-Revisão Final (incluindo comentário sobre cobertura).**
        8.  **Verificação de Conformidade com o Método AGV.**
        9.  **Suposições, Decisões, Desafios ou Desvios Justificados:** Incluir Workarounds (com justificativa detalhada).
        10. **Lista de Todos os Arquivos Criados/Modificados** **nesta tarefa**. 
        11. **Intervenções e Orientações do Coordenador:**
            *   Se o Coordenador forneceu qualquer orientação significativa, correção de curso, sugestão de depuração, ou instrução específica durante o processo que tenha influenciado as decisões tomadas, ajudado a superar um bloqueio, ou refinado a solução de uma forma não prevista no prompt inicial, resuma essas interações e seu impacto aqui. Se não houve tais interações, declare explicitamente: "A implementação prosseguiu conforme o plano e as diretrizes do prompt, sem necessidade de intervenções ou orientações adicionais do Coordenador que alterassem o escopo ou a abordagem." (Ainda é útil mencionar pequenas ajudas ou confirmações, se ocorreram).

*   **Resultado Esperado:**
    *   Código Python de produção implementado/modificado (apenas para o alvo e seus pré-reqs diretos), com alta qualidade.
    *   Testes unitários (`pytest`) abrangentes.
    *   `README.md` do pacote (se aplicável).
    *   Relatório detalhado conforme estrutura.