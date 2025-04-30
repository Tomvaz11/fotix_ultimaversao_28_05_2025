Aja como um formatador profissional de arquivos Markdown (.md).

Seu objetivo é padronizar o arquivo fornecido seguindo estas regras:

- Todos os títulos devem usar a hierarquia correta de Markdown: `#`, `##`, `###`, etc., conforme o nível de importância do título.
- Após um título como `## Tarefa Principal`, insira uma quebra de linha (linha em branco) e então adicione o parágrafo normalmente (sem usar `>`).
- Apenas descrições gerais como **visão geral**, **funcionalidades**, **público-alvo**, **resumo de cada seção**, devem ser convertidas em bloco de citação com `> `.
- **Não** use `>` em listas de diretrizes numeradas ou listas com `-` que não sejam puramente descritivas.
- Listas simples devem usar `-` (traço) e listas de etapas devem usar `1.`, `2.`, etc.
- Evite blocos de código (```) exceto quando o conteúdo for claramente código-fonte.
- Mantenha todos os placeholders `[NOME_DO_PROJETO]`, `[LISTA...]`, `[DESCRIÇÃO...]` exatamente como estão.
- O parágrafo final de instrução (sobre Severino e Tocle) deve permanecer fora de citações, como texto simples.
- Mantenha espaçamento de 1 linha entre seções, parágrafos, e listas.

O conteúdo a ser formatado começa abaixo desta linha:

--- (INÍCIO DO ARQUIVO PARA FORMATAÇÃO) ---

[COLE AQUI O ARQUIVO BAGUNÇADO]

--- (FIM DO ARQUIVO PARA FORMATAÇÃO) ---

Ao final, devolva **apenas o conteúdo formatado em Markdown puro**, sem adicionar comentários ou explicações.
