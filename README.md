# Fotix

Fotix é uma ferramenta para gerenciamento de arquivos duplicados, permitindo a identificação, seleção e remoção segura de duplicatas.

## Características

- Detecção de arquivos duplicados (baseada em hashing BLAKE3)
- Suporte para escanear dentro de arquivos ZIP
- Várias estratégias para selecionar automaticamente quais arquivos manter
- Remoção segura (usando a lixeira do sistema)
- Backup automático dos arquivos removidos
- Interface gráfica intuitiva com PySide6

## Instalação

### Requisitos

- Python 3.8 ou superior
- Dependências listadas em pyproject.toml

### Instalação do Desenvolvimento

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/fotix.git
cd fotix

# Crie e ative um ambiente virtual (opcional, mas recomendado)
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale o pacote em modo de desenvolvimento
pip install -e ".[dev]"
```

## Uso

(Em desenvolvimento)

## Estrutura do Projeto

O projeto segue uma arquitetura em camadas:

- **Camada de Apresentação (UI)**: Interface gráfica do usuário
- **Camada de Aplicação**: Coordena os casos de uso e gerencia o fluxo
- **Camada de Domínio (Core)**: Contém a lógica de negócio central
- **Camada de Infraestrutura**: Lida com interações externas (arquivos, etc.)

## Desenvolvimento

### Executando Testes

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=fotix
```

## Licença

MIT 