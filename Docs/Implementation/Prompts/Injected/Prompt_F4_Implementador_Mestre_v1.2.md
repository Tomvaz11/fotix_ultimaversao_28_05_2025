# AGV Prompt Template: ImplementadorMestre v1.2 - Implementação Guiada por Blueprint e Ordem

**Tarefa Principal:** Implementar ou modificar a funcionalidade/componente lógico alvo especificado abaixo, utilizando o Blueprint Arquitetural e a Descrição de Alto Nível Inicial (fornecida no arquivo de Ordem) como guias principais. Interagir com o Coordenador para esclarecimentos mínimos necessários (via "Propor e Confirmar"). Gerar código de produção e testes unitários de alta qualidade.

**Contexto Essencial (Fornecido pelo Coordenador):**

1.  **Funcionalidade/Componente Alvo:** `[Item X da Ordem: Nome Completo do Módulo. Ex: "Item 3: fotix.core.models"]` (**ÚNICO CAMPO A SER PREENCHIDO PELO COORDENADOR NESTA SEÇÃO**)
2.  **Blueprint Arquitetural:** `@Output_BluePrint_Arquitetural_Tocrisna_v3.md`
3.  **Ordem e Descrições Iniciais:** `@Output_Ordem_Para_Implementacao_Geral.md`
4.  **Contexto Adicional do Workspace:** *Fique a vontade para consultar nossa codebase.*

**Instruções Detalhadas para a IA (Cursor/Augment):**

1.  **Identificar Alvo e Descrição:** Extraia o Nome do Módulo do campo "Funcionalidade/Componente Alvo". Encontre a entrada correspondente no arquivo `@Output_Ordem_Para_Implementacao_Geral.md` anexado e use a **"Descrição de Alto Nível Inicial"** fornecida lá como ponto de partida para os requisitos.
2.  **Analisar Blueprint e Contexto:** Consulte **intensivamente** o `@Output_BluePrint_Arquitetural_Tocrisna_v3.md` para determinar a localização exata, interfaces, modelos e dependências. Se a implementação já foi iniciada, analise o código ou a codebase existente anexado (`@`) para usar corretamente as dependências já implementadas.
3.  **Refinar Requisitos (Se Estritamente Necessário - Abordagem Propor/Confirmar):** Se a Descrição Inicial + Blueprint forem ambíguos para detalhes CRUCIAIS, **NÃO peça ao Coordenador para detalhar tecnicamente.** Proponha uma **solução padrão/lógica específica** e peça uma **confirmação simples**. Só faça isso se for essencial.
4.  **Implementar a Lógica:** Escreva o código Python nos arquivos corretos. **Crie os diretórios necessários** (ex: `src/fotix/core/`) se eles ainda não existirem, seguindo a estrutura definida no Blueprint.
5.  **Criar/Usar Utilitários (`utils`) Organicamete:** Se identificar lógica genérica, crie/adicione a função em `fotix.utils.helpers.py` (criando o arquivo/diretórios se necessário). Mencione no relatório. Garanta que `utils` não tenha dependências internas.
6.  **Aplicar Boas Práticas:** Siga as diretrizes AGV: Código Limpo (PEP 8, KISS, SRP), Type Hints (PEP 484), Docstrings (PEP 257), Tratamento de Erros robusto.
7.  **Gerar Testes Unitários:** **OBRIGATÓRIO:** Crie testes (`pytest`) para novas funcionalidades/modificações. Cobrir casos relevantes, use **mocks**, coloque em `tests/unit/` correspondente (criando diretórios se necessário).
8.  **Gerar Relatório Conciso:** Resuma o que foi feito, arquivos alterados/criados, suposições chave e adições a `utils`.

**Resultado Esperado:**

*   Código Python de produção implementado/modificado.
*   Código Python de testes unitários correspondentes.
*   Breve relatório resumindo a implementação.