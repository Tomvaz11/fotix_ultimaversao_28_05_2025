# AGV Prompt Template: Tocrisna v1.0 - Definição da Arquitetura Técnica

**Tarefa Principal:** Definir e documentar uma proposta de arquitetura técnica de alto nível para o projeto descrito abaixo. O foco deve ser na modularidade, clareza, manutenibilidade, e na definição clara dos principais componentes e suas interfaces de comunicação.

## Contexto e Definições Iniciais do Projeto (Fornecido por Você - Fase 1)

- **Nome do Projeto:** `[NOME_DO_PROJETO]`

- **Visão Geral / Objetivo Principal:**

    [DESCRIÇÃO CLARA DO PROPÓSITO GERAL DO SOFTWARE, O PROBLEMA QUE RESOLVE E SEU OBJETIVO FINAL.]

- **Funcionalidades Chave (Alto Nível):**

    - [LISTA (BULLET POINTS) DAS PRINCIPAIS CAPACIDADES OU FEATURES QUE O SOFTWARE DEVE TER.]

- **Público Alvo / Ambiente de Uso:** `[QUEM USARÁ O SOFTWARE E EM QUE CONTEXTO? ISSO AJUDA A INFERIR REQUISITOS NÃO FUNCIONAIS. Ex: Usuários finais em desktop, Aplicação web interna, Serviço de backend.]`

- **Stack Tecnológica Definida:**

  - **Linguagem Principal:** `[Ex: Python 3.10+]`
  - **Framework Principal (se houver):** `[Ex: FastAPI, Flask, Nenhum]`
  - **Bibliotecas Essenciais Pré-definidas:** `[Ex: Pillow, numpy, LangChain]`
  - **Banco de Dados (se aplicável):** `[Ex: PostgreSQL com pgvector, SQLite, Nenhum]`
  - **Outras Tecnologias Chave:** `[Ex: Docker, MLflow]`

- **Requisitos Não Funcionais Iniciais (se houver):**

  - Performance Esperada: `[Ex: Processar X itens por segundo, Tempo de resposta < Y ms]`
  - Escalabilidade: `[Ex: Deve suportar Z usuários concorrentes, Volume de dados esperado]`
  - Segurança: `[Ex: Nível básico de segurança para dados de usuário, Autenticação necessária]`

- **Principais Restrições (se houver):** `[Ex: Orçamento limitado, Prazo curto, Deve integrar com API X existente]`

## Diretrizes e Princípios Arquiteturais (Filosofia AGV)

1. **Modularidade e Separação de Responsabilidades (SRP):** Proponha uma divisão clara em módulos/componentes lógicos, cada um com uma responsabilidade bem definida. Minimize o acoplamento entre eles e maximize a coesão interna.
2. **Clareza e Manutenibilidade:** A arquitetura deve ser fácil de entender, manter e evoluir. Prefira soluções mais simples (KISS) quando apropriado.
3. **Definição Explícita de Interfaces:** **CRUCIAL:** Para os principais pontos de interação entre os módulos identificados, defina claramente as interfaces (contratos). Isso inclui:
   - Assinaturas de funções/métodos públicos chave.
   - Estruturas de dados (Dataclasses, NamedTuples, Pydantic Models) usadas para troca de informações.
   - Descreva brevemente o propósito de cada interface exposta.
4. **Testabilidade:** A arquitetura deve facilitar a escrita de testes unitários e de integração (ex: permitir injeção de dependência onde fizer sentido).
5. **Segurança Fundamental:** Incorpore princípios básicos de segurança desde o design (ex: onde a validação de input deve ocorrer, como dados sensíveis podem ser tratados – sugerir hashing/criptografia, necessidade de autenticação/autorizacao).
6. **Aderência à Stack:** Utilize primariamente as tecnologias definidas na Stack Tecnológica. Se sugerir uma tecnologia *adicional*, justifique claramente a necessidade.
7. **Padrões de Design:** Sugira e aplique padrões de design relevantes (ex: Repository, Service Layer, Observer, Strategy, etc.) onde eles agregarem valor à estrutura e manutenibilidade. Justifique brevemente a escolha.
8. **Escalabilidade (Básica):** Considere como a arquitetura pode suportar um crescimento moderado no futuro (ex: design sem estado para serviços, possibilidade de paralelizar tarefas).

## Resultado Esperado (Blueprint Arquitetural)

Um documento (preferencialmente em Markdown) descrevendo a arquitetura proposta, incluindo:

1. **Visão Geral da Arquitetura:** Um breve resumo da abordagem arquitetural escolhida (ex: Arquitetura em Camadas, Microsserviços simples, Baseada em Eventos, etc.) e uma justificativa.
2. **Diagrama de Componentes (Simplificado):** Um diagrama de blocos (pode ser textual/ASCII ou uma descrição clara) mostrando os principais módulos/componentes e suas interconexões de alto nível.
3. **Descrição dos Componentes/Módulos:** Para cada componente principal identificado:
   - Nome claro (ex: `core`, `api`, `data_access`, `utils`).
   - Responsabilidade principal.
   - Tecnologias chave da stack que serão usadas nele.
4. **Definição das Interfaces Principais:** Detalhamento dos contratos de comunicação entre os componentes chave (conforme Diretriz 3).
5. **Gerenciamento de Dados (se aplicável):** Como os dados serão persistidos e acessados (ex: Módulo `data_access` usando SQLAlchemy com padrão Repository).
6. **Estrutura de Diretórios Proposta:** Uma sugestão inicial para a organização das pastas e arquivos principais do projeto.
7. **Considerações de Segurança:** Resumo dos princípios de segurança aplicados no design.
8. **Justificativas e Trade-offs:** Breve explicação das principais decisões arquiteturais e por que alternativas foram descartadas (se relevante).

---

Este `Prompt_Tocrisna_Architecture_v1.0.md` fornece o framework para gerar a base estrutural do projeto. O output dele será essencial para alimentar os prompts do Severino (para detalhar funcionalidades) e do Tocle (para implementar).