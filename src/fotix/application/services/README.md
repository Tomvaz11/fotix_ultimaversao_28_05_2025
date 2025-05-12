# Fotix - Serviços da Camada de Aplicação

Este diretório contém os serviços específicos da camada de aplicação do Fotix, responsáveis por implementar os casos de uso da aplicação e orquestrar a interação entre a UI e as camadas de domínio (core) e infraestrutura.

## Módulos

### `scan_service.py`

O módulo `scan_service.py` implementa o `ScanService`, responsável por orquestrar o processo de varredura de diretórios e arquivos ZIP, utilizando os serviços de concorrência, sistema de arquivos, manipulador de ZIP e o buscador de duplicatas do core.

#### Funcionalidades

- Varredura de diretórios em busca de arquivos duplicados
- Filtragem de diretórios aninhados para evitar processamento redundante
- Validação de diretórios de entrada
- Suporte para análise de arquivos dentro de ZIPs
- Relatório de progresso durante a varredura

#### Uso Básico

```python
from pathlib import Path
from fotix.application.services.scan_service import ScanService

# Criar o serviço de varredura (com as dependências necessárias)
scan_service = ScanService(
    duplicate_finder_service=duplicate_finder_service,
    file_system_service=file_system_service,
    zip_handler_service=zip_handler_service,
    concurrency_service=concurrency_service
)

# Definir diretórios para varredura
directories = [
    Path("C:/Fotos"),
    Path("D:/Backup/Fotos")
]

# Varrer diretórios em busca de duplicatas
duplicate_sets = scan_service.scan_directories(
    directories=directories,
    include_zips=True,
    file_extensions=['.jpg', '.png', '.gif'],
    progress_callback=lambda progress: print(f"Progresso: {progress * 100:.1f}%")
)

# Processar os resultados
for duplicate_set in duplicate_sets:
    print(f"Encontrado conjunto de duplicatas com hash {duplicate_set.hash}")
    print(f"Tamanho: {duplicate_set.size} bytes, Arquivos: {duplicate_set.count}")
    for file_info in duplicate_set.files:
        print(f"  - {file_info.path}")
```

### `duplicate_management_service.py`

O módulo `duplicate_management_service.py` implementa o `DuplicateManagementService`, responsável por gerenciar a seleção do arquivo a ser mantido (usando `SelectionStrategy`), a remoção segura (usando `FileSystemService`) e o backup (usando `BackupService`).

#### Funcionalidades

- Seleção automática ou personalizada do arquivo a ser mantido
- Backup dos arquivos antes da remoção
- Remoção segura de arquivos duplicados (movendo para a lixeira)
- Tratamento de erros durante o processo
- Suporte para arquivos normais (arquivos dentro de ZIPs são ignorados para remoção)

#### Uso Básico

```python
from pathlib import Path
from fotix.application.services.duplicate_management_service import DuplicateManagementService
from fotix.core.selection_strategy import create_strategy
from fotix.infrastructure.file_system import FileSystemService
from fotix.infrastructure.backup import BackupService

# Criar instâncias dos serviços necessários
file_system_service = FileSystemService()
backup_service = BackupService(file_system_service)
selection_strategy = create_strategy('highest_resolution', file_system_service)

# Criar o serviço de gerenciamento de duplicatas
duplicate_mgmt_service = DuplicateManagementService(
    selection_strategy=selection_strategy,
    file_system_service=file_system_service,
    backup_service=backup_service
)

# Processar um conjunto de duplicatas
result = duplicate_mgmt_service.process_duplicate_set(
    duplicate_set=duplicate_set,
    create_backup=True,
    custom_selection=None  # Se None, usa a estratégia de seleção
)

# Verificar o resultado
if result['error'] is None:
    print(f"Arquivo mantido: {result['kept_file'].path}")
    print(f"Arquivos removidos: {len(result['removed_files'])}")
    print(f"ID do backup: {result['backup_id']}")
else:
    print(f"Erro: {result['error']}")
```
