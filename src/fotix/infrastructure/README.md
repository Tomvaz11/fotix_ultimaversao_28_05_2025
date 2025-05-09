# Pacote de Infraestrutura (`fotix.infrastructure`)

Este pacote contém módulos que lidam com interações externas e preocupações transversais da aplicação Fotix.

## Módulos Principais:

*   `logging_config.py`: Configura o sistema de logging para toda a aplicação, com base nas definições em `fotix.config`.
*   `file_system.py` (A ser implementado): Implementação de `IFileSystemService` para abstrair operações no sistema de arquivos.
*   `concurrency.py` (A ser implementado): Implementação de `IConcurrencyService` para gerenciar tarefas concorrentes.
*   `backup.py` (A ser implementado): Implementação de `IBackupService` para gerenciamento de backups.
*   `zip_handler.py` (A ser implementado): Implementação de `IZipHandlerService` para leitura de arquivos ZIP.
*   `interfaces.py` (A ser implementado/atualizado): Define as interfaces (contratos) para os serviços desta camada.

## Responsabilidades:

*   Abstrair detalhes de baixo nível de interações com o sistema operacional, bibliotecas de terceiros, etc.
*   Fornecer implementações concretas das interfaces definidas em `fotix.infrastructure.interfaces`.
*   Gerenciar configurações de logging.

Este README será atualizado conforme novos módulos e funcionalidades forem adicionados a este pacote. 