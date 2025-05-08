# Fotix

Fotix é uma ferramenta para identificação e gerenciamento de arquivos duplicados.

## Características

- Detecção de arquivos duplicados usando hashing BLAKE3
- Suporte para escanear dentro de arquivos ZIP
- Estratégias configuráveis para seleção automática de arquivos a serem mantidos
- Backup seguro de arquivos antes da remoção
- Interface gráfica amigável construída com PySide6

## Instalação

### Requisitos

- Python 3.8 ou superior
- Dependências listadas em pyproject.toml

### Instalação para desenvolvimento

```bash
# Clone o repositório
git clone https://github.com/yourusername/fotix.git
cd fotix

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale o pacote em modo de desenvolvimento
pip install -e ".[dev]"
```

## Uso

```bash
# Execute a aplicação
python -m fotix.main
```

## Desenvolvimento

### Estrutura do projeto

```
fotix/
├── src/
│   └── fotix/
│       ├── __init__.py
│       ├── main.py             # Ponto de entrada da aplicação
│       ├── config.py           # Configurações da aplicação
│       ├── application/        # Camada de aplicação
│       ├── core/               # Camada de domínio
│       ├── infrastructure/     # Camada de infraestrutura
│       ├── ui/                 # Interface gráfica
│       └── utils/              # Utilitários
├── tests/
│   ├── unit/                   # Testes unitários
│   └── integration/            # Testes de integração
└── pyproject.toml              # Configuração do projeto
```

### Executando testes

```bash
# Execute todos os testes
pytest

# Execute testes com cobertura
pytest --cov=fotix

# Execute testes específicos
pytest tests/unit/fotix/test_config.py
```

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.
