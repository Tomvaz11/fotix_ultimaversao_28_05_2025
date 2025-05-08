# Fotix

Fotix é um utilitário para detecção e gerenciamento de arquivos duplicados, com foco especial em imagens.

## Características

- Detecção de arquivos duplicados baseada em conteúdo (usando algoritmo de hash BLAKE3)
- Detecção de duplicatas dentro de arquivos ZIP
- Estratégias configuráveis para seleção automática de quais arquivos manter
- Backup automático de arquivos removidos
- Interface gráfica intuitiva (PySide6)
- Processamento paralelo para melhor desempenho

## Instalação

### Requisitos

- Python 3.8 ou superior
- Dependências listadas em `pyproject.toml`

### Para desenvolvedores

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/fotix.git
cd fotix
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

3. Instale o pacote em modo de desenvolvimento:
```bash
pip install -e ".[dev]"
```

## Execução

```bash
python -m fotix
```

## Estrutura do Projeto

O projeto está organizado em camadas:

1. **UI** (`fotix.ui`): Interface gráfica usando PySide6
2. **Aplicação** (`fotix.application`): Serviços de orquestração
3. **Core** (`fotix.core`): Lógica de negócio (detecção de duplicatas, estratégias)
4. **Infraestrutura** (`fotix.infrastructure`): Interação com recursos externos

## Testes

Execute os testes com:

```bash
pytest
```

Para relatório de cobertura:

```bash
pytest --cov=fotix
```

## Contribuindo

Contribuições são bem-vindas! Por favor, siga as diretrizes de código e de testes.

## Licença

MIT 