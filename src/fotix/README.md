# Fotix

Fotix é uma ferramenta para gerenciamento de arquivos duplicados, permitindo a identificação, seleção e remoção segura de duplicatas.

## Estrutura do Pacote

O projeto segue uma arquitetura em camadas, dividida nas seguintes partes:

- **Camada de Apresentação (UI)**: Interface gráfica do usuário construída com PySide6.
- **Camada de Aplicação**: Coordena os casos de uso e orquestra os serviços.
- **Camada de Domínio (Core)**: Contém a lógica de negócio central.
- **Camada de Infraestrutura**: Lida com interações externas como sistema de arquivos, concorrência e logging.

### Módulos Implementados

#### `fotix.config`

Módulo responsável por carregar e fornecer acesso às configurações da aplicação.

Principais funcionalidades:
- Carregamento de configurações a partir de arquivos JSON
- Valores padrão para todas as configurações necessárias
- Validação e normalização dos valores de configuração
- Salvamento de configurações em arquivos

Uso básico:

```python
from fotix.config import get_config

# Obter a configuração (carrega automaticamente os valores padrão)
config = get_config()

# Acessar valores de configuração
backup_dir = config.backup_dir
log_level = config.log_level

# Obter o valor numérico do nível de log para o módulo logging
log_level_value = config.get_log_level_value()

# Salvar configurações em um arquivo
config.save_to_file("caminho/para/config.json")
```

Para carregar configurações de um arquivo específico:

```python
from fotix.config import load_config

# Carregar configurações de um arquivo
config = load_config("caminho/para/config.json")
``` 