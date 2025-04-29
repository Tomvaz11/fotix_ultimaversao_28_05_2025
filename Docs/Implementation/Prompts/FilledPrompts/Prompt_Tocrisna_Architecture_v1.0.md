# AGV Prompt Template: Tocrisna v1.0 - Definição da Arquitetura Técnica

**Tarefa Principal:** Definir e documentar uma proposta de arquitetura técnica de alto nível para o projeto descrito abaixo. O foco deve ser na modularidade, clareza, manutenibilidade, e na definição clara dos principais componentes e suas interfaces de comunicação.

## Contexto e Definições Iniciais do Projeto

- **Nome do Projeto:** `Fotix`

- **Visão Geral / Objetivo Principal:**

    Aplicativo desktop desenvolvido em Python, com backend robusto e interface gráfica (GUI) completa, projetado para localizar e remover arquivos duplicados (idênticos) de imagens e vídeos em múltiplos diretórios e arquivos ZIP.
    O sistema analisa arquivos de mídia e, **somente ao identificar dois ou mais arquivos idênticos**, utiliza um algoritmo inteligente para decidir qual arquivo manter e qual remover, com base em critérios como maior resolução da imagem, data de criação mais antiga e estrutura do nome do arquivo (evitando cópias como "(1)", "cópia", etc.).
    A arquitetura é otimizada para grandes volumes de dados, utilizando processamento assíncrono, batching progressivo e execução paralela.
    O aplicativo também oferece sistema de backup e restauração para recuperação segura dos arquivos removidos.

- **Funcionalidades Chave (Alto Nível):**

    - Análise de arquivos de mídia (imagens e vídeos) em diretórios e arquivos ZIP.
    - Identificação precisa de arquivos duplicados (idênticos) utilizando hashing.
    - Seleção automática do arquivo a ser mantido entre duplicatas com base em critérios objetivos.
    - Remoção segura de duplicatas com backup automático.
    - Recuperação fácil de arquivos removidos através do sistema de restauração.
    - Processamento otimizado para grandes volumes de dados com execução assíncrona, paralela e em lotes.
    - Interface gráfica intuitiva para configuração e acompanhamento.
    - Geração de logs detalhados e relatórios resumidos com estatísticas pós-processamento.

- **Público Alvo / Ambiente de Uso:** `Usuários finais em desktop (Windows)`

- **Stack Tecnológica Definida:**

  - **Linguagem Principal:** Python 3.10+
  - **GUI (Interface Gráfica):** PySide6 (Qt for Python) — framework moderno para criação de interfaces desktop nativas.
  - **Motor de Escaneamento de Duplicatas:** BLAKE3 + pré-filtragem por tamanho com `os.path.getsize` para otimização inicial.
  - **Manipulação de Arquivos e Sistema de Arquivos:** pathlib + shutil + send2trash (remoção segura) + concurrent.futures (execução paralela).
  - **Descompactação Otimizada:** stream-unzip para leitura e extração progressiva de arquivos ZIP.

- **Requisitos Não Funcionais Iniciais:**

  - Capacidade de processar grandes volumes (100.000+ arquivos) sem travamentos.
  - Identificação rápida de duplicatas com uso eficiente de CPU, RAM e disco.
  - Backups automáticos para garantir segurança de dados.
  - GUI responsiva mesmo sob alta carga de processamento.
  - Compatibilidade garantida com Windows 10 ou superior.
  - Descompactação eficiente e rápida de grandes arquivos ZIP com baixo uso de memória.
  - Tratamento de erros em operações críticas de escrita e remoção.

- **Principais Restrições:**

    - Suporte exclusivo para Windows na primeira versão.
    - Sem integração com bancos de dados externos.
    - Análise limitada a arquivos idêticos (sem similaridade perceptual).
    - Suporte apenas ao formato ZIP para arquivos compactados.
    - Sem sistema de atualização automática previsto na primeira versão.
    - Desempenho condicionado à capacidade de hardware local do usuário.

## Diretrizes e Princípios Arquiteturais (Filosofia AGV)

1. **Modularidade e Separação de Responsabilidades (SRP):** Proponha uma divisão clara em módulos/componentes lógicos, cada um com uma responsabilidade bem definida. Minimize o acoplamento entre eles e maximize a coesão interna.
2. **Clareza e Manutenibilidade:** A arquitetura deve ser fácil de entender, manter e evoluir. Prefira soluções mais simples (KISS) quando apropriado.
3. **Definição Explícita de Interfaces:** **CRUCIAL:** Para os principais pontos de interação entre os módulos identificados, defina claramente as interfaces (contratos). Isso inclui:
   - Assinaturas de funções/métodos públicos chave.
   - Estruturas de dados (Dataclasses, NamedTuples, Pydantic Models) usadas para troca de informações.
   - Descreva brevemente o propósito de cada interface exposta.
4. **Testabilidade:** A arquitetura deve facilitar a escrita de testes unitários e de integração (ex: permitir injeção de dependência onde fizer sentido).
5. **Segurança Fundamental:** Incorpore princípios básicos de segurança desde o design (ex: onde a validação de input deve ocorrer, como dados sensíveis podem ser tratados – sugerir hashing/criptografia, necessidade de autenticação/autorização).
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