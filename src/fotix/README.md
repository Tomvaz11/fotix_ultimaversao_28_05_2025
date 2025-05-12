# Fotix - Módulos Principais

Este diretório contém os módulos principais da aplicação Fotix.

## Módulos

### `main.py`

O módulo `main.py` é o ponto de entrada da aplicação Fotix. Ele é responsável por inicializar as camadas da aplicação, configurar a UI principal e iniciar o loop de eventos da GUI.

#### Funcionalidades

- Configuração do sistema de logging
- Inicialização da aplicação Qt
- Criação e exibição da janela principal
- Tratamento de erros não capturados

#### Uso Básico

```python
# Executar a aplicação
python -m fotix.main
```

#### Componentes Principais

- `setup_application()`: Configura a aplicação Qt, verificando se já existe uma instância de QApplication e reutilizando-a se existir.
- `main()`: Função principal que configura o logging, inicializa a aplicação Qt, cria a janela principal e inicia o loop de eventos.

#### Dependências

- `fotix.ui.main_window`: Para a janela principal da aplicação
- `fotix.infrastructure.logging_config`: Para configuração do sistema de logging
- `fotix.config`: Para acesso às configurações da aplicação
- `PySide6.QtWidgets`: Para a interface gráfica

### `config.py`

O módulo `config.py` é responsável por carregar e fornecer acesso às configurações da aplicação. Ele oferece:

- Carregamento de configurações a partir de um arquivo JSON
- Valores padrão para configurações não especificadas
- Acesso centralizado às configurações via padrão Singleton
- Funções auxiliares para obter configurações específicas (diretório de backup, nível de log)
- Atualização e salvamento de configurações

#### Uso Básico

```python
from fotix.config import get_config, get_backup_dir, get_log_level, update_config

# Obter todas as configurações
config = get_config()
print(f"Nível de log: {config['log_level']}")

# Obter configurações específicas
backup_dir = get_backup_dir()  # Retorna um objeto Path
log_level = get_log_level()    # Retorna um valor de logging (ex: logging.INFO)

# Atualizar uma configuração
update_config("max_workers", 8)
```

#### Configurações Disponíveis

| Configuração | Tipo | Descrição | Valor Padrão |
|--------------|------|-----------|--------------|
| `backup_dir` | str | Diretório para armazenar backups | `~/fotix_backups` |
| `log_level` | str | Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL) | `INFO` |
| `log_file` | str | Caminho para o arquivo de log | `~/fotix_logs/fotix.log` |
| `max_workers` | int | Número máximo de workers para processamento paralelo | `4` |
| `default_scan_dir` | str | Diretório padrão para iniciar a varredura | `~` (diretório home) |

#### Localização do Arquivo de Configuração

O arquivo de configuração é armazenado em:

- Windows: `%APPDATA%\Fotix\config.json`
- Linux/Mac: `~/.config/fotix/config.json`

Se o arquivo não existir, ele será criado automaticamente com os valores padrão na primeira vez que as configurações forem acessadas.
