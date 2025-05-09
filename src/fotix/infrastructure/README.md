# Pacote de Infraestrutura (`fotix.infrastructure`)

Este pacote é responsável por todas as interações da aplicação Fotix com o mundo exterior e pelo fornecimento de serviços técnicos genéricos como abstrações.

## Módulos Principais

-   **`interfaces.py`**: Define os contratos (interfaces Python `Protocol`) para os serviços da camada de infraestrutura. Exemplos incluem:
    -   `IFileSystemService`: Abstração para operações no sistema de arquivos.
    -   (Outras interfaces como `IZipHandlerService`, `IConcurrencyService`, `IBackupService` serão definidas aqui conforme são implementadas).

-   **`file_system.py`**: Implementação concreta de `IFileSystemService` utilizando bibliotecas padrão do Python como `pathlib`, `shutil`, e bibliotecas de terceiros como `send2trash`.

-   **`logging_config.py`**: (A ser implementado) Configuração do sistema de logging para a aplicação.

-   **`zip_handler.py`**: (A ser implementado) Implementação de `IZipHandlerService` para ler arquivos dentro de arquivos ZIP (ex: usando `stream-unzip`).

-   **`concurrency.py`**: (A ser implementado) Implementação de `IConcurrencyService` para gerenciar tarefas concorrentes/paralelas (ex: usando `concurrent.futures`).

-   **`backup.py`**: (A ser implementado) Implementação de `IBackupService` para gerenciar backups de arquivos.

## Design

A camada de infraestrutura visa desacoplar as camadas superiores (Aplicação, Core) dos detalhes de implementação de interações externas. Ao depender de interfaces definidas neste pacote, as camadas superiores se tornam mais testáveis e flexíveis a mudanças nas implementações subjacentes (por exemplo, trocar a biblioteca de manipulação de ZIP ou a forma como a concorrência é gerenciada).

## Responsabilidades:

*   Abstrair detalhes de baixo nível de interações com o sistema operacional, bibliotecas de terceiros, etc.
*   Fornecer implementações concretas das interfaces definidas em `fotix.infrastructure.interfaces`.
*   Gerenciar configurações de logging.

Este README será atualizado conforme novos módulos e funcionalidades forem adicionados a este pacote. 