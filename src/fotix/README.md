# Fotix

Fotix é um utilitário para detecção e gerenciamento de arquivos duplicados, focado em imagens.

## Estrutura do Projeto

O projeto está organizado em camadas, seguindo princípios de separação de responsabilidades:

1. **Camada de Apresentação (UI):** Interface gráfica usando PySide6.
2. **Camada de Aplicação:** Orquestração dos casos de uso.
3. **Camada de Domínio (Core):** Lógica de negócio central.
4. **Camada de Infraestrutura:** Interações com o sistema operacional e bibliotecas externas.

## Módulos Implementados

### fotix.config

O módulo de configuração permite carregar e gerenciar configurações da aplicação, como:

- Diretório para backup de arquivos
- Níveis de log
- Configurações de processamento concorrente
- Extensões de arquivo para busca de duplicatas
- E outras configurações relevantes

#### Uso

```python
from fotix.config import get_config

# Obter a instância do gerenciador de configurações
config = get_config()

# Acessar configurações
backup_dir = config.backup_dir
log_level = config.log_level

# Modificar configurações
config.log_level = "DEBUG"
config.concurrent_workers = 8

# Salvar as configurações
config.save_config()
```

As configurações são automaticamente salvas em `~/.fotix/config.json` e são carregadas na inicialização. 