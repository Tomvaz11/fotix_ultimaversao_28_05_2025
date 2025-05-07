"""
Camada de Infraestrutura do Fotix.

Esta camada é responsável pela interação com o mundo exterior e fornecimento de serviços
técnicos genéricos como abstrações. Contém os wrappers para bibliotecas de baixo nível,
garantindo que as camadas superiores dependam de interfaces estáveis e não de implementações
concretas.

Módulos:
    - interfaces: Define as interfaces (contratos) para os serviços desta camada
    - file_system: Implementa IFileSystemService usando pathlib, shutil, etc.
    - concurrency: Implementa IConcurrencyService usando concurrent.futures
    - backup: Implementa IBackupService para gerenciar backups de arquivos
    - zip_handler: Implementa IZipHandlerService para manipular arquivos ZIP
    - logging_config: Configura o sistema de logging padrão do Python
"""
