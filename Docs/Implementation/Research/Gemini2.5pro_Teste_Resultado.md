Ok, vamos estruturar a pesquisa profunda conforme solicitado.

---

## Projeto
Desenvolver, em **Python**, uma aplicação desktop (**Windows**, **sem web**) para **detectar fotos e vídeos idênticos/duplicados**, composta por backend e frontend.

---

## Resultado da Pesquisa

### **1. GUI (Frontend)**

**Perguntas-chave:**
- Quais frameworks/bibliotecas GUI mais modernos, utilizados e bem-mantidos para aplicações Python **desktop Windows**?
- Quais oferecem melhor performance, experiência do usuário e ecossistema de componentes?

---

#### **Top Candidatos**

1.  **PySide6 / PyQt6 (Qt for Python)**
    *   Link Oficial (PySide6 - LGPL): [https://www.qt.io/qt-for-python](https://www.qt.io/qt-for-python)
    *   Link Oficial (PyQt6 - GPL/Comercial): [https://riverbankcomputing.com/software/pyqt/intro](https://riverbankcomputing.com/software/pyqt/intro)
2.  **CustomTkinter**
    *   Link Oficial: [https://github.com/TomSchimansky/CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
3.  **Dear PyGui**
    *   Link Oficial: [https://github.com/hoffstadt/DearPyGui](https://github.com/hoffstadt/DearPyGui)
4.  **Tkinter** (Built-in)
    *   Link Oficial: [https://docs.python.org/3/library/tkinter.html](https://docs.python.org/3/library/tkinter.html)
5.  **wxPython**
    *   Link Oficial: [https://www.wxpython.org/](https://www.wxpython.org/)

---

#### **Resumo Comparativo**

| Framework/Biblioteca | Prós | Contras | Adoção/Maturidade | Performance | Facilidade de Uso | Ecossistema |
|---|---|---|---|---|---|---|
| **PySide6 / PyQt6** | - Visual moderno e nativo (Qt).<br>- Grande conjunto de widgets ricos.<br>- Multiplataforma robusto.<br>- Excelente documentação e comunidade.<br>- Bom desempenho (C++ por baixo).<br>- Qt Designer para UI visual. | - Curva de aprendizado maior que Tkinter.<br>- Tamanho da aplicação pode ser maior.<br>- Licenciamento (PyQt: GPL/Comercial, PySide: LGPL - mais flexível). | Muito Alta (Qt é padrão industrial) | Boa a Excelente | Moderada | Excelente |
| **CustomTkinter** | - Aparência moderna e customizável sobre Tkinter.<br>- Fácil de aprender para quem conhece Tkinter.<br>- Leve comparado a Qt/wxPython.<br>- Desenvolvimento ativo. | - Baseado em Tkinter, pode herdar limitações.<br>- Menos widgets nativos que Qt/wxPython.<br>- Ecossistema menor. | Crescente / Recente | Boa | Fácil a Moderada | Razoável (baseado em Tkinter) |
| **Dear PyGui** | - **Performance excepcional** (renderização via GPU).<br>- Paradigma de "Immediate Mode GUI" (diferente, pode ser mais simples para certos UIs dinâmicos).<br>- Bom para visualização de dados e UIs com muitos updates. | - Paradigma diferente, curva de aprendizado específica.<br>- Menos widgets "tradicionais" que Qt/wx.<br>- Layout pode ser menos intuitivo inicialmente.<br>- Comunidade menor que Qt/Tkinter. | Média / Recente | **Excelente** | Moderada (paradigma diferente) | Razoável (foco em performance) |
| **Tkinter** | - **Built-in**, sem dependências extras.<br>- Mais simples para iniciar.<br>- Estável e maduro.<br>- Boa documentação básica. | - Visual "antigo" por padrão.<br>- Menos widgets avançados.<br>- Performance pode degradar com UIs complexas. | Muito Alta (padrão Python) | Razoável | Fácil | Razoável (extensível, mas menos rico) |
| **wxPython** | - Widgets com aparência nativa da plataforma.<br>- Maduro e estável.<br>- Boa documentação e comunidade.<br>- Conjunto razoável de widgets. | - Menos popular que Qt atualmente.<br>- Pode ter complexidades de instalação/empacotamento.<br>- Curva de aprendizado moderada. | Alta / Maduro | Boa | Moderada | Boa |

---

#### **Recomendação Final**

*   **Opção 1 (Recomendada): PySide6 (LGPL)** - Oferece o melhor equilíbrio entre visual moderno, conjunto rico de componentes, bom desempenho e flexibilidade de licença para uma aplicação desktop profissional. A curva de aprendizado é compensada pelo poder e ecossistema.
*   **Opção 2 (Alternativa Simples/Moderna): CustomTkinter** - Se a prioridade for um visual moderno com menor curva de aprendizado e menos dependências (comparado ao Qt), e se os widgets disponíveis forem suficientes. Ideal para projetos mais simples ou protótipos rápidos com boa aparência.
*   **Opção 3 (Foco em Performance): Dear PyGui** - Se a UI exigir altíssima performance de renderização (ex: visualização em tempo real de muitos itens) e a equipe estiver disposta a aprender o paradigma de "Immediate Mode".

---

#### **Referências**

*   PySide6 vs PyQt6: [https://wiki.python.org/moin/PyQtVsPySide](https://wiki.python.org/moin/PyQtVsPySide)
*   CustomTkinter Showcase: [https://github.com/TomSchimansky/CustomTkinter/blob/master/examples/README.md](https://github.com/TomSchimansky/CustomTkinter/blob/master/examples/README.md)
*   Dear PyGui Examples: [https://github.com/hoffstadt/DearPyGui/tree/master/Examples](https://github.com/hoffstadt/DearPyGui/tree/master/Examples)
*   Python GUI Frameworks Comparison (2023/2024): (Pesquisar por artigos recentes em blogs como Real Python, Towards Data Science, ou discussões no Reddit r/Python) - Exemplo genérico: [https://realpython.com/python-gui-tkinter/](https://realpython.com/python-gui-tkinter/) (Tkinter), [https://realpython.com/python-pyqt-gui-calculator/](https://realpython.com/python-pyqt-gui-calculator/) (PyQt)

---

### **2. Motor de Escaneamento de Duplicatas Idênticas**

**Perguntas-chave:**
- Quais bibliotecas especializadas (imagens e vídeos) são líderes de mercado para **cálculo de hash criptográfico** e comparação byte-a-byte?
- Quais apresentam **melhor desempenho** (tempo de processamento, uso de memória, GPU opcional)?

---

#### **Top Candidatos**

1.  **`hashlib`** (Built-in)
    *   Link Oficial: [https://docs.python.org/3/library/hashlib.html](https://docs.python.org/3/library/hashlib.html)
    *   Função Principal: Cálculo de hashes criptográficos (MD5, SHA-1, SHA-256, SHA-512, etc.).
2.  **Leitura de Arquivo e Comparação Byte-a-Byte** (Built-in I/O)
    *   Link Oficial: [https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files](https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files)
    *   Função Principal: Comparação direta do conteúdo binário dos arquivos.
3.  **`os` (para `os.path.getsize`)** (Built-in)
    *   Link Oficial: [https://docs.python.org/3/library/os.path.html#os.path.getsize](https://docs.python.org/3/library/os.path.html#os.path.getsize)
    *   Função Principal: Obter o tamanho do arquivo para filtragem inicial rápida.
4.  **(Opcional/Alternativo) `xxhash`**
    *   Link Oficial: [https://github.com/ifduyue/python-xxhash](https://github.com/ifduyue/python-xxhash)
    *   Função Principal: Cálculo de hash não-criptográfico extremamente rápido. *Nota: Não garante unicidade como hash criptográfico, usar com cautela ou como pré-filtro.*

---

#### **Resumo Comparativo**

| Técnica/Biblioteca | Prós | Contras | Performance | Uso de Memória | GPU? | Observações |
|---|---|---|---|---|---|---|
| **`hashlib` (SHA-256, etc.)** | - Built-in, padrão e seguro.<br>- **Garante identificação de arquivos idênticos** (colisões são teoricamente possíveis, mas astronomicamente improváveis para arquivos diferentes).<br>- Relativamente rápido (implementação em C/OpenSSL).<br>- Leitura em chunks para arquivos grandes. | - Mais lento que hashes não-criptográficos (como xxHash).<br>- CPU-bound. | Boa (otimizada em C) | Baixo (lendo em chunks) | Não | **Método principal recomendado para identificar duplicatas idênticas.** |
| **Comparação Byte-a-Byte** | - **Método definitivo** para confirmar identidade.<br>- Built-in (operações de I/O).<br>- Conceitualmente simples. | - **Muito lento** para arquivos grandes.<br>- I/O-bound (limitado pela velocidade do disco).<br>- Deve ser usado *após* filtragem por tamanho e/ou hash. | Lenta (depende do I/O) | Baixo (lendo em chunks) | Não | Usar como confirmação final *se* houver suspeita de colisão de hash (raro) ou se hashes não forem usados. |
| **`os.path.getsize`** | - **Extremamente rápido**.<br>- Built-in.<br>- Ótimo filtro inicial (arquivos de tamanhos diferentes não podem ser idênticos). | - Não identifica duplicatas, apenas elimina não-candidatos. | Excelente | Mínimo | Não | **Passo essencial e obrigatório** antes de calcular hashes ou comparar bytes. |
| **`xxhash`** | - **Extremamente rápido** (geralmente mais rápido que `hashlib`).<br>- Leve. | - **Não é criptográfico**, colisões são mais prováveis que SHA-256.<br>- Não garante identidade, apenas alta probabilidade.<br>- Requer instalação (`pip install xxhash`). | Excelente | Baixo (lendo em chunks) | Não | Pode ser usado como um *pré-filtro* rápido *antes* do `hashlib` se a performance for crítica, mas introduz complexidade e risco (mínimo) de falsos positivos se não seguido por hash criptográfico ou byte-a-byte. |

**Nota sobre GPU:** Aceleração por GPU geralmente não é aplicável/eficiente para hashes criptográficos padrão ou comparação byte-a-byte. É mais comum em tarefas como *perceptual hashing* (para imagens *similares*, não idênticas) ou machine learning.

---

#### **Recomendação Final**

A estratégia mais robusta e eficiente para detectar duplicatas *idênticas* é:

1.  **Agrupar arquivos por tamanho:** Use `os.path.getsize()` para rapidamente agrupar todos os arquivos candidatos pelo seu tamanho exato. Arquivos com tamanhos diferentes não podem ser idênticos.
2.  **Calcular Hash Criptográfico:** Para cada grupo de arquivos com o mesmo tamanho (contendo 2 ou mais arquivos), calcule um hash criptográfico seguro (ex: **SHA-256**) usando **`hashlib`**. Leia os arquivos em chunks para controlar o uso de memória (ex: `hashlib.update(chunk)` em um loop).
3.  **Comparar Hashes:** Arquivos com o mesmo tamanho e o mesmo hash SHA-256 são considerados idênticos com altíssima probabilidade (praticamente certeza).
4.  **(Opcional) Comparação Byte-a-Byte:** Se uma garantia *absoluta* for necessária (paranoia extrema contra colisões de SHA-256, que são negligenciáveis na prática para este fim), realize uma comparação byte-a-byte entre os arquivos que tiveram hash e tamanho idênticos.

**Recomendação Principal:** Use **`os.path.getsize`** para filtragem inicial e **`hashlib` (SHA-256)** para a identificação final. Processe os arquivos em paralelo (ver Camada 3) para acelerar.

---

#### **Referências**

*   `hashlib` Documentation: [https://docs.python.org/3/library/hashlib.html](https://docs.python.org/3/library/hashlib.html)
*   Efficient File Hashing in Python: [https://stackoverflow.com/questions/22058048/hashing-a-file-in-python](https://stackoverflow.com/questions/22058048/hashing-a-file-in-python)
*   `xxhash` GitHub: [https://github.com/ifduyue/python-xxhash](https://github.com/ifduyue/python-xxhash)
*   Discussão sobre Hash Collisions: (Pesquisar "SHA-256 collision probability practical")

---

### **3. Manipulação de Arquivos & Sistema**

**Perguntas-chave:**
- Quais bibliotecas Python recomendadas para operações intensivas de I/O (cópia, exclusão, restauração) com suporte robusto a **multithreading/multiprocessing**?
- Quais opções facilitam interação segura com a **Lixeira do Windows** (move, restore, purge)?

---

#### **Top Candidatos**

1.  **`concurrent.futures`** (Built-in)
    *   Link Oficial: [https://docs.python.org/3/library/concurrent.futures.html](https://docs.python.org/3/library/concurrent.futures.html)
    *   Função Principal: Interface de alto nível para execução assíncrona usando threads (`ThreadPoolExecutor`) ou processos (`ProcessPoolExecutor`).
2.  **`multiprocessing`** (Built-in)
    *   Link Oficial: [https://docs.python.org/3/library/multiprocessing.html](https://docs.python.org/3/library/multiprocessing.html)
    *   Função Principal: Criação e gerenciamento de processos para contornar o GIL (Global Interpreter Lock) e obter paralelismo real em tarefas CPU-bound (como hashing).
3.  **`shutil`** (Built-in)
    *   Link Oficial: [https://docs.python.org/3/library/shutil.html](https://docs.python.org/3/library/shutil.html)
    *   Função Principal: Operações de arquivo de alto nível (cópia, movimentação, exclusão *permanente*).
4.  **`pathlib`** (Built-in)
    *   Link Oficial: [https://docs.python.org/3/library/pathlib.html](https://docs.python.org/3/library/pathlib.html)
    *   Função Principal: Abordagem orientada a objetos para manipulação de caminhos de sistema de arquivos. Integra-se bem com `os` e `shutil`.
5.  **`send2trash`** (Third-Party)
    *   Link Oficial: [https://github.com/hsoft/send2trash](https://github.com/hsoft/send2trash)
    *   Função Principal: **Move arquivos/diretórios para a Lixeira** do sistema de forma segura e multiplataforma (incluindo Windows).
6.  **`winshell`** (Third-Party, Windows-only)
    *   Link Oficial: [https://github.com/tjguk/winshell](https://github.com/tjguk/winshell) ou [https://pypi.org/project/winshell/](https://pypi.org/project/winshell/)
    *   Função Principal: Acesso a funcionalidades do shell do Windows, incluindo operações mais avançadas com a **Lixeira (esvaziar, potencialmente listar/restaurar - embora restaurar seja complexo)**.

---

#### **Resumo Comparativo**

| Biblioteca/Módulo | Prós | Contras | Paralelismo | Operações de Arquivo | Interação Lixeira | Windows-Specific |
|---|---|---|---|---|---|---|
| **`concurrent.futures`** | - API simples para paralelismo.<br>- Gerencia pools de workers (threads/processos). | - Abstração, menos controle fino que `threading`/`multiprocessing` diretamente. | Excelente (Threads ou Processos) | N/A (coordena tarefas) | N/A | Não |
| **`multiprocessing`** | - **Paralelismo real** (CPU-bound tasks como hashing).<br>- Contorna o GIL. | - Mais complexo para gerenciar (comunicação inter-processos, serialização).<br>- Maior overhead que threads. | Excelente (Processos) | N/A (coordena tarefas) | N/A | Não |
| **`shutil`** | - Operações de arquivo robustas e padrão.<br>- Cópia com metadados, exclusão de árvores, etc. | - **Exclusão é permanente** (não vai para a lixeira por padrão).<br>- Operações são bloqueantes (podem ser executadas em threads/processos). | N/A (executa operações) | Excelente (Cópia, Mover, Excluir Permanente) | Não | Não |
| **`pathlib`** | - API moderna e OO para caminhos.<br>- Torna o código mais legível. | - Foco em caminhos, menos em operações complexas (usa `os`/`shutil` por baixo). | N/A (manipula caminhos) | Boa (Básicas: renomear, excluir) | Não | Não |
| **`send2trash`** | - **Forma segura e recomendada de mover para a Lixeira**.<br>- Simples de usar.<br>- Multiplataforma. | - Requer instalação (`pip install send2trash`).<br>- Apenas move *para* a lixeira, não gerencia (restaurar, esvaziar). | N/A (executa operação) | N/A | **Excelente (Mover para)** | Não (funciona no Windows) |
| **`winshell`** | - Acesso a funções específicas do Windows Shell.<br>- **Pode esvaziar a Lixeira**.<br>- Potencialmente outras interações (listar, restaurar - mais complexo). | - **Windows-only**.<br>- Menos comum/padrão que `send2trash`.<br>- Requer instalação (`pip install winshell`).<br>- Restaurar da lixeira programaticamente é não-trivial. | N/A (executa operação) | N/A | **Boa (Mover para, Esvaziar, etc.)** | **Sim** |

---

#### **Recomendação Final**

*   **Paralelismo:** Use **`concurrent.futures.ProcessPoolExecutor`** para paralelizar as tarefas CPU-bound (cálculo de hash) e potencialmente tarefas I/O-bound (leitura de muitos arquivos pequenos/médios, embora `ThreadPoolExecutor` também possa ser considerado para I/O). `ProcessPoolExecutor` é geralmente preferível para garantir o uso de múltiplos cores no cálculo de hash.
*   **Manipulação de Caminhos:** Use **`pathlib`** para uma manipulação de caminhos mais limpa e moderna.
*   **Operações de Arquivo (Cópia/Mover):** Use **`shutil`** para cópias ou movimentações que *não* envolvam a lixeira.
*   **Exclusão Segura (Lixeira):** Use **`send2trash`** para mover arquivos duplicados para a Lixeira do Windows. Esta é a abordagem mais segura e esperada pelo usuário.
*   **Interação Avançada com Lixeira (Opcional):** Se for necessário implementar funcionalidades como "Esvaziar Lixeira" diretamente da aplicação, use **`winshell`**, aceitando a dependência exclusiva do Windows. Para restauração, a complexidade aumenta significativamente e pode ser melhor deixar para o usuário fazer via Explorador de Arquivos.

---

#### **Referências**

*   `concurrent.futures` Documentation: [https://docs.python.org/3/library/concurrent.futures.html](https://docs.python.org/3/library/concurrent.futures.html)
*   `multiprocessing` vs `threading`: [https://realpython.com/python-concurrency/](https://realpython.com/python-concurrency/)
*   `shutil` Documentation: [https://docs.python.org/3/library/shutil.html](https://docs.python.org/3/library/shutil.html)
*   `pathlib` Documentation: [https://docs.python.org/3/library/pathlib.html](https://docs.python.org/3/library/pathlib.html)
*   `send2trash` GitHub: [https://github.com/hsoft/send2trash](https://github.com/hsoft/send2trash)
*   `winshell` Documentation/Examples: (Consultar PyPI ou GitHub) [https://pypi.org/project/winshell/](https://pypi.org/project/winshell/)

---

### **4. Descompactação Otimizada de Arquivos Compactados**

**Perguntas-chave:**
- Quais bibliotecas Python permitem **descompactar arquivos enquanto processam** os dados simultaneamente (streaming/unpacking sob demanda), maximizando o desempenho?
- Quais são as opções mais modernas, eficientes e compatíveis com grandes volumes de dados?

---

#### **Top Candidatos**

1.  **`zipfile`** (Built-in)
    *   Link Oficial: [https://docs.python.org/3/library/zipfile.html](https://docs.python.org/3/library/zipfile.html)
    *   Função Principal: Manipulação de arquivos ZIP. Suporta leitura de membros individuais como streams.
2.  **`tarfile`** (Built-in)
    *   Link Oficial: [https://docs.python.org/3/library/tarfile.html](https://docs.python.org/3/library/tarfile.html)
    *   Função Principal: Manipulação de arquivos TAR (incluindo tar.gz, tar.bz2, tar.xz). Suporta extração de membros como streams.
3.  **`rarfile`** (Third-Party)
    *   Link Oficial: [https://github.com/markokr/rarfile](https://github.com/markokr/rarfile) ou [https://pypi.org/project/rarfile/](https://pypi.org/project/rarfile/)
    *   Função Principal: Manipulação de arquivos RAR. Frequentemente requer o executável `unrar` externo. Pode suportar leitura de membros via `open()`.
4.  **`py7zr`** (Third-Party)
    *   Link Oficial: [https://github.com/miurahr/py7zr](https://github.com/miurahr/py7zr)
    *   Função Principal: Manipulação de arquivos 7z (pura Python ou com bibliotecas C). Verificar documentação para suporte a streaming/leitura de membro individual.
5.  **`libarchive-c`** (Third-Party Wrapper)
    *   Link Oficial: [https://github.com/Changaco/python-libarchive-c](https://github.com/Changaco/python-libarchive-c)
    *   Função Principal: Bindings Python para a biblioteca `libarchive`, que suporta uma vasta gama de formatos de compressão e arquivamento, com foco em streaming.

---

#### **Resumo Comparativo**

| Biblioteca | Prós | Contras | Formatos Suportados | Streaming/On-Demand | Dependências | Eficiência |
|---|---|---|---|---|---|---|
| **`zipfile`** | - Built-in, fácil de usar.<br>- **Suporta `ZipFile.open()` para ler membros como streams** sem extração completa.<br>- Maduro e estável. | - Apenas ZIP. | ZIP | **Sim (via `open()`)** | Nenhuma (Python Standard Library) | Boa |
| **`tarfile`** | - Built-in.<br>- Suporta vários formatos TAR (gz, bz2, xz).<br>- **Suporta extração de membros como streams** (`extractfile()`). | - Apenas TAR. | TAR, TAR.GZ, TAR.BZ2, TAR.XZ | **Sim (via `extractfile()`)** | Nenhuma (Python Standard Library) | Boa |
| **`rarfile`** | - Suporta formato popular RAR. | - Requer instalação (`pip install rarfile`).<br>- **Frequentemente requer executável `unrar` externo**, o que complica distribuição e dependências.<br>- Licenciamento do RAR pode ser restritivo. | RAR | **Sim (via `open()`)** | Python Lib + `unrar` (geralmente) | Depende do backend `unrar` |
| **`py7zr`** | - Suporta formato 7z.<br>- Pode ser puro Python (sem dependências C/externas para funções básicas). | - Requer instalação (`pip install py7zr`).<br>- Suporte a streaming pode depender da implementação (verificar docs).<br>- Menos maduro que `zipfile`/`tarfile`. | 7z | **Verificar Documentação (provável que sim)** | Python Lib (pode ter opcionais) | Razoável a Boa |
| **`libarchive-c`** | - **Suporta uma vasta gama de formatos** (zip, tar, 7z, rar, iso, etc.).<br>- Projetado com streaming em mente.<br>- Potencialmente muito eficiente (usa lib C). | - Requer instalação (`pip install libarchive-c`).<br>- **Requer a biblioteca `libarchive` instalada no sistema**, o que pode ser um desafio no Windows. | Muitos (ZIP, TAR, 7z, RAR, ISO, etc.) | **Sim (design principal)** | Python Lib + `libarchive` (sistema) | Potencialmente Excelente |

---

#### **Recomendação Final**

*   **Para ZIP e TAR:** Use as bibliotecas built-in **`zipfile`** e **`tarfile`**. Ambas oferecem métodos (`ZipFile.open()` e `TarFile.extractfile()`) que retornam objetos file-like para ler o conteúdo de um membro do arquivo *sem* precisar extrair todo o arquivo para o disco primeiro. Isso é ideal para streaming e processamento sob demanda (ex: ler o stream diretamente para o `hashlib`).
*   **Para RAR:** Se o suporte a RAR for essencial, use **`rarfile`**, mas esteja ciente da dependência do executável `unrar`. Implemente a lógica para usar o método `open()` do `rarfile` para obter um stream do membro.
*   **Para 7z:** Use **`py7zr`**, verificando na documentação a melhor forma de acessar o conteúdo de um membro como stream.
*   **Opção Avançada/Abrangente:** Se for necessário suportar *muitos* formatos diferentes com uma única biblioteca e a instalação da dependência `libarchive` no Windows for viável, **`libarchive-c`** é uma opção poderosa e eficiente focada em streaming.

**Estratégia Chave:** Independentemente da biblioteca, a otimização vem de *não* extrair o arquivo inteiro. Obtenha a lista de membros, itere sobre os que interessam (fotos/vídeos), use o método apropriado (`open()`, `extractfile()`) para obter um objeto file-like para cada membro, e passe esse objeto file-like para a função de hashing (lendo em chunks, como se fosse um arquivo normal).

---

#### **Referências**

*   `zipfile` `open()` method: [https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile.open](https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile.open)
*   `tarfile` `extractfile()` method: [https://docs.python.org/3/library/tarfile.html#tarfile.TarFile.extractfile](https://docs.python.org/3/library/tarfile.html#tarfile.TarFile.extractfile)
*   `rarfile` Documentation: [https://rarfile.readthedocs.io/en/latest/](https://rarfile.readthedocs.io/en/latest/)
*   `py7zr` GitHub: [https://github.com/miurahr/py7zr](https://github.com/miurahr/py7zr)
*   `libarchive` Website: [https://www.libarchive.org/](https://www.libarchive.org/)
*   `python-libarchive-c` GitHub: [https://github.com/Changaco/python-libarchive-c](https://github.com/Changaco/python-libarchive-c)
*   Stack Overflow: Searching for "python process zip member without extracting" or similar for practical examples.

---

Espero que esta pesquisa detalhada seja útil para o desenvolvimento do seu projeto!