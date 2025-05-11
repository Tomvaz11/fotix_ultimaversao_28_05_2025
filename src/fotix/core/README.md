# Fotix - Módulo Core

Este diretório contém os módulos da camada de domínio (core) do Fotix, responsáveis pela lógica de negócio central e independente da aplicação.

## Módulos

### `models.py`

O módulo `models.py` define as estruturas de dados centrais do domínio, como `FileInfo` e `DuplicateSet`, usando dataclasses para garantir tipagem forte e validação de dados.

#### Classes Principais

- `FileInfo`: Representa informações sobre um arquivo no sistema, incluindo metadados como caminho, tamanho, hash, datas de criação e modificação.
- `DuplicateSet`: Representa um conjunto de arquivos duplicados, com base em seu conteúdo (hash).

### `interfaces.py`

O módulo `interfaces.py` define os contratos (interfaces) para os serviços da camada de domínio, como detecção de duplicatas e estratégias de seleção.

#### Interfaces Principais

- `IDuplicateFinderService`: Define como encontrar conjuntos de arquivos duplicados.
- `ISelectionStrategy`: Define como selecionar qual arquivo manter de um conjunto de duplicatas.

### `duplicate_finder.py`

O módulo `duplicate_finder.py` implementa a interface `IDuplicateFinderService`, fornecendo a lógica central para identificar arquivos duplicados com base em seu conteúdo (hash).

#### Funcionalidades

- Detecção de duplicatas em diretórios e arquivos individuais
- Suporte para análise de arquivos dentro de ZIPs
- Hashing eficiente usando o algoritmo BLAKE3
- Otimização por pré-filtragem de arquivos por tamanho
- Relatório de progresso durante a análise

#### Uso Básico

```python
from pathlib import Path
from fotix.core.duplicate_finder import DuplicateFinderService
from fotix.infrastructure.file_system import FileSystemService
from fotix.infrastructure.zip_handler import ZipHandlerService

# Criar instâncias dos serviços necessários
file_system_service = FileSystemService()
zip_handler_service = ZipHandlerService()

# Criar o serviço de detecção de duplicatas
duplicate_finder = DuplicateFinderService(
    file_system_service=file_system_service,
    zip_handler_service=zip_handler_service
)

# Definir caminhos para análise
scan_paths = [
    Path("C:/Fotos"),
    Path("D:/Backup/Fotos")
]

# Função opcional para reportar progresso
def progress_callback(progress: float):
    print(f"Progresso: {progress * 100:.1f}%")

# Encontrar duplicatas
duplicate_sets = duplicate_finder.find_duplicates(
    scan_paths=scan_paths,
    include_zips=True,
    progress_callback=progress_callback
)

# Exibir resultados
print(f"Encontrados {len(duplicate_sets)} conjuntos de duplicatas")

for i, duplicate_set in enumerate(duplicate_sets, 1):
    print(f"\nConjunto {i} - {len(duplicate_set.files)} arquivos - {duplicate_set.size} bytes")
    for file in duplicate_set.files:
        print(f"  - {file.path}")
```

### `selection_strategy.py` (a ser implementado)

O módulo `selection_strategy.py` implementará a interface `ISelectionStrategy`, fornecendo diferentes estratégias para selecionar automaticamente qual arquivo manter de um conjunto de duplicatas, com base em critérios como data, resolução ou nome.

## Dependências

- `fotix.infrastructure.interfaces`: Para acesso a serviços de infraestrutura como `IFileSystemService` e `IZipHandlerService`.
- `fotix.utils.helpers`: Para funções auxiliares como `measure_time`.
- Biblioteca externa `blake3`: Para cálculo de hash eficiente.
