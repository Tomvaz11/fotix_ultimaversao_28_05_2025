# Fotix - Camada de Infraestrutura

A camada de infraestrutura do Fotix lida com todas as interações externas e fornece serviços técnicos genéricos como abstrações. Ela contém os wrappers para bibliotecas de baixo nível, garantindo que as camadas superiores dependam de interfaces estáveis e não de implementações concretas.

## Módulos

### `logging_config`

Este módulo configura o sistema de logging padrão do Python para a aplicação Fotix, permitindo o registro de eventos e erros em diferentes níveis de severidade.

**Funcionalidades principais:**

- Configuração centralizada do logging para toda a aplicação
- Suporte a logs no console e em arquivo
- Rotação automática de arquivos de log (tamanho máximo e backup)
- Diferentes níveis de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Função auxiliar `get_logger()` para obter loggers específicos para cada módulo

**Exemplo de uso:**

```python
from fotix.infrastructure.logging_config import get_logger

# Obter um logger para o módulo atual
logger = get_logger(__name__)

# Registrar mensagens em diferentes níveis
logger.debug("Informação detalhada para debugging")
logger.info("Informação geral sobre o progresso")
logger.warning("Aviso sobre condição potencialmente problemática")
logger.error("Erro que impediu execução de uma operação")
logger.critical("Erro grave que pode afetar o funcionamento da aplicação")
```

### `file_system`

Este módulo implementa a interface `IFileSystemService`, fornecendo abstrações para operações no sistema de arquivos como leitura, escrita, movimentação para lixeira e listagem de diretórios.

**Funcionalidades principais:**

- Leitura de conteúdo de arquivos via streaming (eficiente para arquivos grandes)
- Listagem recursiva de diretórios com filtragem por extensão
- Movimentação segura de arquivos para a lixeira do sistema (usando `send2trash`)
- Cópia de arquivos com preservação de metadados
- Criação de diretórios com suporte para criação de diretórios pais
- Obtenção de informações como tamanho, data de criação e modificação de arquivos

**Exemplo de uso:**

```python
from pathlib import Path
from fotix.infrastructure.file_system import FileSystemService

# Criar instância do serviço
fs_service = FileSystemService()

# Listar arquivos em um diretório, recursivamente, filtrando por extensão
images_dir = Path("C:/Users/Photos")
image_files = fs_service.list_directory_contents(
    path=images_dir,
    recursive=True,
    file_extensions=['.jpg', '.png', '.jpeg']
)

# Processar cada arquivo de imagem encontrado
for image_path in image_files:
    # Obter tamanho e timestamp de modificação
    size = fs_service.get_file_size(image_path)
    mod_time = fs_service.get_modification_time(image_path)
    
    print(f"Imagem: {image_path}, Tamanho: {size}, Modificado: {mod_time}")
    
    # Fazer backup de uma imagem
    fs_service.copy_file(image_path, Path("C:/Backup") / image_path.name)
    
    # Ler conteúdo de um arquivo em chunks para processamento eficiente
    for chunk in fs_service.stream_file_content(image_path):
        # Processar cada bloco de bytes...
        pass
```

## Interfaces

Os contratos (interfaces) para os serviços desta camada estão definidos no módulo `interfaces.py`. Essas interfaces garantem que as camadas superiores da aplicação possam depender de contratos estáveis em vez de implementações específicas.

**IFileSystemService:** Define o contrato para operações no sistema de arquivos, incluindo métodos para obter tamanho, ler conteúdo, listar diretórios, mover para lixeira, copiar arquivos e obter timestamps.

---

Esta documentação será atualizada à medida que novos serviços de infraestrutura forem implementados. 