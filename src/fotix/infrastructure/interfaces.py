"""
Interfaces para os serviços da camada de infraestrutura do Fotix.

Este módulo define os contratos (interfaces) para os serviços desta camada,
permitindo que as camadas superiores dependam de abstrações e não de implementações.
"""

from typing import Protocol, runtime_checkable

# Nota: Atualmente não há interfaces específicas para configuração de logging
# pois o módulo logging_config configura o sistema de logging padrão do Python
# sem precisar expor uma interface específica para isso.

# As interfaces como IFileSystemService, IConcurrencyService, IBackupService, IZipHandlerService
# serão definidas neste arquivo conforme forem implementadas nos próximos módulos. 