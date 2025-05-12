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
