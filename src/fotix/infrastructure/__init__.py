"""
Pacote de infraestrutura para o Fotix.

Este pacote contém os módulos que lidam com a interação com o mundo exterior
e fornecem serviços técnicos genéricos como abstrações. Inclui wrappers para
bibliotecas de baixo nível, garantindo que as camadas superiores dependam de
interfaces estáveis e não de implementações concretas.

Módulos:
    - logging_config: Configuração do sistema de logging padrão do Python.
    - file_system: Implementação de IFileSystemService usando pathlib, shutil, etc.
    - concurrency: Implementação de IConcurrencyService usando concurrent.futures.
    - backup: Implementação de IBackupService para gerenciamento de backups.
    - zip_handler: Implementação de IZipHandlerService usando stream-unzip.
    - interfaces: Definição das interfaces para os serviços desta camada.
"""
