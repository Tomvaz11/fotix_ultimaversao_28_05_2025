# Fotix - Módulo de Interface Gráfica

Este diretório contém os módulos da camada de apresentação (UI) do Fotix, responsáveis pela interface gráfica do usuário.

## Módulos

### `main_window.py`

O módulo `main_window.py` implementa a janela principal da aplicação Fotix, que contém a interface gráfica para interação com o usuário.

#### Funcionalidades

- Exibição da interface principal com menu, barra de ferramentas e barra de status
- Integração com os serviços da camada de aplicação
- Gerenciamento de ações do usuário (escanear diretórios, processar duplicatas, etc.)
- Exibição de diálogos de progresso e configurações

#### Uso Básico

```python
from PySide6.QtWidgets import QApplication
import sys
from fotix.ui.main_window import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
```

### `widgets/duplicate_list_widget.py`

O módulo `duplicate_list_widget.py` implementa um widget personalizado para exibir conjuntos de arquivos duplicados e permitir ao usuário selecionar quais arquivos manter ou remover.

#### Funcionalidades

- Exibição de conjuntos de duplicatas em uma estrutura de árvore
- Seleção de arquivos para manter ou remover
- Exibição de informações detalhadas sobre os arquivos
- Menu de contexto para ações rápidas

### `widgets/file_info_widget.py`

O módulo `file_info_widget.py` implementa um widget personalizado para exibir informações detalhadas sobre um arquivo, como nome, caminho, tamanho, datas de criação e modificação.

#### Funcionalidades

- Exibição de metadados do arquivo (nome, caminho, tamanho, hash, etc.)
- Exibição de informações específicas para arquivos em ZIPs
- Exibição de resolução para arquivos de imagem

### `widgets/progress_dialog.py`

O módulo `progress_dialog.py` implementa um diálogo de progresso para exibir o andamento de operações longas, como varredura de diretórios, processamento de duplicatas, etc.

#### Funcionalidades

- Exibição de barra de progresso
- Exibição de mensagem e detalhes sobre a operação
- Suporte para cancelamento de operações
- Fechamento automático ao concluir

### `widgets/settings_dialog.py`

O módulo `settings_dialog.py` implementa um diálogo para exibir e modificar as configurações da aplicação, como diretório de backup, nível de log, etc.

#### Funcionalidades

- Exibição e edição de configurações da aplicação
- Organização em abas para diferentes categorias de configurações
- Seleção de diretórios e arquivos
- Salvamento automático das configurações

### `resources/icons.py`

O módulo `icons.py` fornece acesso aos ícones utilizados na interface gráfica do Fotix.

#### Funcionalidades

- Carregamento de ícones a partir de recursos embutidos ou do sistema
- Cache de ícones para melhor desempenho
- Acesso a ícones comuns através de constantes

## Dependências

- `PySide6`: Para a interface gráfica
- `fotix.core.models`: Para estruturas de dados como `FileInfo` e `DuplicateSet`
- `fotix.application.services`: Para acesso aos serviços da camada de aplicação
- `fotix.config`: Para acesso às configurações da aplicação
- `fotix.utils`: Para funções auxiliares

## Estrutura de Diretórios

```
fotix/ui/
├── __init__.py
├── main_window.py
├── README.md
├── resources/
│   ├── __init__.py
│   └── icons.py
└── widgets/
    ├── __init__.py
    ├── duplicate_list_widget.py
    ├── file_info_widget.py
    ├── progress_dialog.py
    └── settings_dialog.py
```
