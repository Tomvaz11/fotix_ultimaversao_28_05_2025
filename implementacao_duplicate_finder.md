# Implementação do Módulo DuplicateFinder para o Projeto Fotix

## Resumo da Implementação

Implementei com sucesso a funcionalidade de `DuplicateFinder` conforme solicitado. O módulo é responsável por encontrar grupos de arquivos duplicados a partir de um iterador de metadados de arquivos, utilizando uma estratégia de duas etapas:

1. **Agrupamento por tamanho**: Arquivos com tamanhos diferentes não podem ser duplicatas
2. **Agrupamento por hash**: Para cada grupo de arquivos com o mesmo tamanho, calcula-se o hash e agrupa-se por hash

A implementação segue todas as diretrizes especificadas:
- Aderência estrita às interfaces definidas
- Código limpo e legível (PEP 8)
- Modularidade e coesão (SRP)
- Type hints completos (PEP 484)
- Tratamento de erros robusto
- Documentação clara (docstrings PEP 257)
- Eficiência (uso de defaultdict para agrupamento)

Os testes unitários cobrem 100% do código, incluindo todos os casos especificados na documentação.

## Detalhamento Passo a Passo da Implementação

### 1. Análise do Pedido do Usuário

O pedido do usuário consistia em implementar a funcionalidade/módulo `DuplicateFinder` no arquivo `fotix/src/fotix/core/duplicate_finder.py`, seguindo rigorosamente as diretrizes e o contexto arquitetural fornecido.

Os arquivos de contexto fornecidos foram:
- `Output_Tocrisna_Architecture_v1.0.md`: Documento com a arquitetura geral do projeto Fotix
- `Severino_Core-Duplicate_Finder.md`: Especificação detalhada do módulo a ser implementado

### 2. Análise dos Arquivos de Contexto

Primeiro, analisei os arquivos de contexto para entender a arquitetura do projeto e os requisitos específicos do módulo:

#### Arquitetura Geral (Output_Tocrisna_Architecture_v1.0.md)

- **Arquitetura em Camadas**: Apresentação (GUI), Aplicação (Serviços), Núcleo (Core/Domain), Infraestrutura
- **Módulo Core**: Responsável pela lógica de negócio principal, independente de UI e I/O direto
- **Estruturas de Dados**: Definidas como dataclasses (`FileMetadata`, `DuplicateGroup`, etc.)
- **Interface do DuplicateFinder**: Método `find_duplicates` que recebe um iterador de `FileMetadata` e uma função de hash

#### Especificação do Módulo (Severino_Core-Duplicate_Finder.md)

- **Método Principal**: `find_duplicates(self, file_iterator: Iterator[FileMetadata], hash_function: callable) -> List[DuplicateGroup]`
- **Processamento**: Agrupamento por tamanho, cálculo de hash apenas para grupos com mais de um arquivo, tratamento de erros
- **Casos de Borda**: Iterador vazio, nenhuma duplicata, falhas no hash, etc.

### 3. Verificação da Estrutura de Diretórios

Verifiquei se a estrutura de diretórios necessária já existia:

```powershell
dir fotix\src\fotix\core
```

Como a estrutura não existia, precisei criá-la:

```powershell
mkdir -p fotix\src\fotix\core
mkdir -p tests\unit\core
```

### 4. Criação do Módulo Domain

Como o módulo `DuplicateFinder` depende das classes `FileMetadata` e `DuplicateGroup`, verifiquei se o módulo domain já existia:

```powershell
dir fotix\src\fotix\domain
```

Como não existia, criei o módulo domain e implementei as classes necessárias:

#### Criação do Diretório
```powershell
mkdir -p fotix\src\fotix\domain
```

#### Implementação das Classes de Domínio (models.py)
```python
"""
Módulo que define as estruturas de dados principais do domínio do Fotix.

Este módulo contém as classes de dados (dataclasses) que representam as entidades
principais do domínio da aplicação, como metadados de arquivos e grupos de duplicatas.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass(frozen=True)
class FileMetadata:
    """
    Representa os metadados de um arquivo.
    
    Esta classe é imutável (frozen=True) e contém informações básicas sobre um arquivo,
    como seu caminho, tamanho e data de criação.
    
    Attributes:
        path: Caminho absoluto para o arquivo
        size: Tamanho do arquivo em bytes
        creation_time: Timestamp UTC da criação do arquivo
    """
    path: Path
    size: int
    creation_time: float  # Timestamp UTC


@dataclass
class DuplicateGroup:
    """
    Representa um grupo de arquivos duplicados.
    
    Um grupo de duplicatas contém dois ou mais arquivos que são idênticos
    (mesmo tamanho e mesmo hash).
    
    Attributes:
        files: Lista de metadados dos arquivos duplicados
        hash_value: O hash BLAKE3 comum a todos os arquivos no grupo
        file_to_keep: Arquivo que deve ser mantido (os outros podem ser removidos)
    """
    files: List[FileMetadata]
    hash_value: str
    file_to_keep: Optional[FileMetadata] = None
```

#### Criação do __init__.py para o Módulo Domain
```python
"""
Pacote de domínio do Fotix.

Este pacote contém as estruturas de dados e entidades principais do domínio da aplicação.
"""

from fotix.domain.models import FileMetadata, DuplicateGroup

__all__ = ['FileMetadata', 'DuplicateGroup']
```

### 5. Criação dos Arquivos __init__.py para os Módulos

Para garantir que os módulos fossem reconhecidos como pacotes Python, criei os arquivos __init__.py:

#### Para o Módulo Core
```python
"""
Pacote core do Fotix.

Este pacote contém a lógica de negócio principal da aplicação,
incluindo a identificação de duplicatas e algoritmos de decisão.
"""
```

#### Para o Módulo Principal (src/fotix)
```python
"""
Pacote principal do Fotix.

Fotix é uma aplicação desktop para localizar e remover arquivos duplicados
(imagens/vídeos) em diretórios e ZIPs, com seleção inteligente de qual
arquivo manter e backup seguro.
"""
```

### 6. Implementação da Classe DuplicateFinder

Implementei a classe `DuplicateFinder` conforme a especificação:

```python
"""
Módulo que implementa a lógica de identificação de arquivos duplicados.

Este módulo contém a classe DuplicateFinder, responsável por encontrar grupos
de arquivos duplicados a partir de um iterador de metadados de arquivos.
"""

import logging
from collections import defaultdict
from typing import Dict, Iterator, List, Callable

from fotix.domain import FileMetadata, DuplicateGroup


class DuplicateFinder:
    """
    Classe responsável por encontrar grupos de arquivos duplicados.
    
    Esta classe implementa a lógica para identificar arquivos duplicados
    baseando-se no tamanho e no hash do conteúdo dos arquivos.
    """
    
    def find_duplicates(
        self, 
        file_iterator: Iterator[FileMetadata], 
        hash_function: Callable[[FileMetadata], str]
    ) -> List[DuplicateGroup]:
        """
        Encontra grupos de arquivos duplicados a partir de um iterador de metadados.
        
        O processo de identificação de duplicatas ocorre em duas etapas:
        1. Agrupamento inicial por tamanho (arquivos com tamanhos diferentes não podem ser duplicatas)
        2. Para cada grupo de arquivos com o mesmo tamanho, cálculo do hash e agrupamento por hash
        
        Args:
            file_iterator: Um iterador que produz objetos FileMetadata
            hash_function: Uma função que recebe um FileMetadata e retorna o hash BLAKE3 do arquivo
                           correspondente, ou levanta uma exceção em caso de erro
        
        Returns:
            Uma lista de DuplicateGroup, onde cada grupo contém dois ou mais arquivos duplicados
            (mesmo tamanho e mesmo hash). A lista será vazia se nenhuma duplicata for encontrada.
        
        Raises:
            Não levanta exceções diretamente, mas a hash_function pode levantar exceções
            relacionadas a I/O (ex: OSError, PermissionError) que são capturadas internamente.
        """
        # Passo 1: Agrupamento inicial por tamanho
        files_by_size: Dict[int, List[FileMetadata]] = defaultdict(list)
        
        for file_meta in file_iterator:
            files_by_size[file_meta.size].append(file_meta)
        
        # Passo 2: Identificação e hashing de potenciais duplicatas
        result_groups: List[DuplicateGroup] = []
        
        for potential_duplicates in files_by_size.values():
            # Pré-filtragem: pula grupos com menos de 2 arquivos (não podem ser duplicatas)
            if len(potential_duplicates) < 2:
                continue
            
            # Agrupamento por hash dentro do grupo de tamanho
            hashes_in_group: Dict[str, List[FileMetadata]] = defaultdict(list)
            
            for file_meta in potential_duplicates:
                try:
                    # Cálculo do hash com tratamento de erro
                    hash_value = hash_function(file_meta)
                    hashes_in_group[hash_value].append(file_meta)
                except Exception as e:
                    # Loga um aviso e continua para o próximo arquivo
                    logging.warning(
                        f"Falha ao calcular hash para o arquivo {file_meta.path}: {str(e)}"
                    )
                    continue
            
            # Formação de grupos de duplicatas reais
            for hash_value, actual_duplicates in hashes_in_group.items():
                # Filtragem final: ignora grupos com menos de 2 arquivos
                if len(actual_duplicates) < 2:
                    continue
                
                # Cria um grupo de duplicatas
                duplicate_group = DuplicateGroup(
                    files=actual_duplicates,
                    hash_value=hash_value,
                    file_to_keep=None  # Será definido posteriormente por outro componente
                )
                
                result_groups.append(duplicate_group)
        
        return result_groups
```

### 7. Implementação dos Testes Unitários

Criei testes unitários abrangentes para a classe `DuplicateFinder`:

```python
"""
Testes unitários para a classe DuplicateFinder.

Este módulo contém testes para verificar o comportamento da classe DuplicateFinder
em diferentes cenários, incluindo casos de sucesso e casos de erro.
"""

import logging
from pathlib import Path
from typing import Iterator, List
from unittest.mock import Mock, patch

import pytest

from fotix.core.duplicate_finder import DuplicateFinder
from fotix.domain import FileMetadata, DuplicateGroup


class TestDuplicateFinder:
    """Testes para a classe DuplicateFinder."""

    def setup_method(self):
        """Configuração executada antes de cada teste."""
        self.finder = DuplicateFinder()
        
        # Cria alguns objetos FileMetadata para usar nos testes
        self.file1 = FileMetadata(
            path=Path("/path/to/file1.jpg"),
            size=1000,
            creation_time=1600000000.0
        )
        self.file2 = FileMetadata(
            path=Path("/path/to/file2.jpg"),
            size=1000,
            creation_time=1600001000.0
        )
        self.file3 = FileMetadata(
            path=Path("/path/to/file3.jpg"),
            size=1000,
            creation_time=1600002000.0
        )
        self.file4 = FileMetadata(
            path=Path("/path/to/file4.jpg"),
            size=2000,
            creation_time=1600003000.0
        )
        self.file5 = FileMetadata(
            path=Path("/path/to/file5.jpg"),
            size=2000,
            creation_time=1600004000.0
        )
        self.file6 = FileMetadata(
            path=Path("/path/to/file6.jpg"),
            size=3000,
            creation_time=1600005000.0
        )
        self.file7 = FileMetadata(
            path=Path("/path/to/empty1.txt"),
            size=0,
            creation_time=1600006000.0
        )
        self.file8 = FileMetadata(
            path=Path("/path/to/empty2.txt"),
            size=0,
            creation_time=1600007000.0
        )

    def test_empty_iterator(self):
        """Testa o comportamento com um iterador vazio."""
        # Cria um iterador vazio
        file_iterator = iter([])
        hash_function = Mock()
        
        # Executa o método find_duplicates
        result = self.finder.find_duplicates(file_iterator, hash_function)
        
        # Verifica se o resultado é uma lista vazia
        assert result == []
        # Verifica se a hash_function não foi chamada
        hash_function.assert_not_called()

    def test_no_duplicates_by_size(self):
        """Testa o comportamento quando não há arquivos com o mesmo tamanho."""
        # Cria um iterador com arquivos de tamanhos diferentes
        file_iterator = iter([self.file1, self.file4, self.file6])
        hash_function = Mock()
        
        # Executa o método find_duplicates
        result = self.finder.find_duplicates(file_iterator, hash_function)
        
        # Verifica se o resultado é uma lista vazia
        assert result == []
        # Verifica se a hash_function não foi chamada
        hash_function.assert_not_called()

    def test_duplicates_by_size_but_different_hash(self):
        """Testa o comportamento quando há arquivos com o mesmo tamanho, mas hashes diferentes."""
        # Cria um iterador com arquivos do mesmo tamanho
        file_iterator = iter([self.file1, self.file2, self.file3])
        
        # Configura a hash_function para retornar hashes diferentes
        hash_function = Mock(side_effect=["hash1", "hash2", "hash3"])
        
        # Executa o método find_duplicates
        result = self.finder.find_duplicates(file_iterator, hash_function)
        
        # Verifica se o resultado é uma lista vazia
        assert result == []
        # Verifica se a hash_function foi chamada para cada arquivo
        assert hash_function.call_count == 3

    def test_one_duplicate_group(self):
        """Testa o comportamento quando há um grupo de arquivos duplicados."""
        # Cria um iterador com alguns arquivos duplicados
        file_iterator = iter([self.file1, self.file2, self.file3, self.file4, self.file6])
        
        # Configura a hash_function para retornar o mesmo hash para os 3 primeiros arquivos
        def mock_hash(file_meta: FileMetadata) -> str:
            if file_meta.size == 1000:
                return "same_hash"
            return f"hash_{file_meta.size}"
        
        hash_function = Mock(side_effect=mock_hash)
        
        # Executa o método find_duplicates
        result = self.finder.find_duplicates(file_iterator, hash_function)
        
        # Verifica se o resultado contém um grupo de duplicatas
        assert len(result) == 1
        assert isinstance(result[0], DuplicateGroup)
        assert result[0].hash_value == "same_hash"
        assert len(result[0].files) == 3
        assert self.file1 in result[0].files
        assert self.file2 in result[0].files
        assert self.file3 in result[0].files
        assert result[0].file_to_keep is None
        
        # Verifica se a hash_function foi chamada para os arquivos com tamanho 1000
        # (a implementação otimiza e não chama a função para arquivos sem duplicatas por tamanho)
        assert hash_function.call_count == 3

    def test_multiple_duplicate_groups(self):
        """Testa o comportamento quando há múltiplos grupos de arquivos duplicados."""
        # Cria um iterador com múltiplos grupos de duplicatas
        file_iterator = iter([
            self.file1, self.file2, self.file3,  # Grupo 1 (tamanho 1000)
            self.file4, self.file5,              # Grupo 2 (tamanho 2000)
            self.file6,                          # Sem duplicatas
            self.file7, self.file8               # Grupo 3 (tamanho 0)
        ])
        
        # Configura a hash_function para retornar hashes apropriados
        def mock_hash(file_meta: FileMetadata) -> str:
            if file_meta.size == 1000:
                return "hash_1000"
            elif file_meta.size == 2000:
                return "hash_2000"
            elif file_meta.size == 0:
                return "hash_0"
            return f"hash_{file_meta.size}"
        
        hash_function = Mock(side_effect=mock_hash)
        
        # Executa o método find_duplicates
        result = self.finder.find_duplicates(file_iterator, hash_function)
        
        # Verifica se o resultado contém três grupos de duplicatas
        assert len(result) == 3
        
        # Verifica o primeiro grupo (tamanho 1000)
        group_1000 = next(g for g in result if g.hash_value == "hash_1000")
        assert len(group_1000.files) == 3
        assert self.file1 in group_1000.files
        assert self.file2 in group_1000.files
        assert self.file3 in group_1000.files
        
        # Verifica o segundo grupo (tamanho 2000)
        group_2000 = next(g for g in result if g.hash_value == "hash_2000")
        assert len(group_2000.files) == 2
        assert self.file4 in group_2000.files
        assert self.file5 in group_2000.files
        
        # Verifica o terceiro grupo (tamanho 0)
        group_0 = next(g for g in result if g.hash_value == "hash_0")
        assert len(group_0.files) == 2
        assert self.file7 in group_0.files
        assert self.file8 in group_0.files
        
        # Verifica se a hash_function foi chamada para os arquivos em grupos com duplicatas por tamanho
        # (a implementação otimiza e não chama a função para arquivos sem duplicatas por tamanho)
        assert hash_function.call_count == 7

    def test_hash_function_error(self):
        """Testa o comportamento quando a hash_function levanta uma exceção."""
        # Cria um iterador com arquivos do mesmo tamanho
        file_iterator = iter([self.file1, self.file2, self.file3])
        
        # Configura a hash_function para levantar uma exceção para o segundo arquivo
        def mock_hash_with_error(file_meta: FileMetadata) -> str:
            if file_meta.path == self.file2.path:
                raise OSError("Erro ao ler o arquivo")
            return "hash_value"
        
        hash_function = Mock(side_effect=mock_hash_with_error)
        
        # Captura os logs para verificar se o aviso foi registrado
        with patch.object(logging, 'warning') as mock_warning:
            # Executa o método find_duplicates
            result = self.finder.find_duplicates(file_iterator, hash_function)
            
            # Verifica se o aviso foi registrado
            mock_warning.assert_called_once()
            assert "Falha ao calcular hash para o arquivo" in mock_warning.call_args[0][0]
            assert "Erro ao ler o arquivo" in mock_warning.call_args[0][0]
        
        # Verifica se o resultado contém um grupo de duplicatas com os arquivos 1 e 3
        assert len(result) == 1
        assert len(result[0].files) == 2
        assert self.file1 in result[0].files
        assert self.file3 in result[0].files
        assert self.file2 not in result[0].files
        
        # Verifica se a hash_function foi chamada para cada arquivo
        assert hash_function.call_count == 3

    def test_all_files_identical(self):
        """Testa o comportamento quando todos os arquivos são idênticos."""
        # Cria um iterador com vários arquivos do mesmo tamanho
        file_iterator = iter([self.file1, self.file2, self.file3])
        
        # Configura a hash_function para retornar o mesmo hash para todos os arquivos
        hash_function = Mock(return_value="same_hash_for_all")
        
        # Executa o método find_duplicates
        result = self.finder.find_duplicates(file_iterator, hash_function)
        
        # Verifica se o resultado contém um único grupo com todos os arquivos
        assert len(result) == 1
        assert len(result[0].files) == 3
        assert self.file1 in result[0].files
        assert self.file2 in result[0].files
        assert self.file3 in result[0].files
        assert result[0].hash_value == "same_hash_for_all"
        
        # Verifica se a hash_function foi chamada para cada arquivo
        assert hash_function.call_count == 3
```

### 8. Configuração para Execução dos Testes

Para executar os testes, precisei configurar o ambiente para que o Python pudesse encontrar os módulos:

#### Criação dos Arquivos __init__.py para os Pacotes de Teste
```python
# tests/__init__.py
"""
Pacote de testes do Fotix.
"""

# tests/unit/__init__.py
"""
Pacote de testes unitários do Fotix.
"""

# tests/unit/core/__init__.py
"""
Pacote de testes unitários para o módulo core do Fotix.
"""
```

#### Criação do setup.py para Instalação em Modo de Desenvolvimento
```python
"""
Script de instalação do Fotix.
"""

from setuptools import setup, find_packages

setup(
    name="fotix",
    version="0.1.0",
    package_dir={"": "fotix/src"},
    packages=find_packages(where="fotix/src"),
    python_requires=">=3.10",
    install_requires=[],
)
```

#### Instalação do Pacote em Modo de Desenvolvimento
```powershell
pip install -e .
```

#### Criação do conftest.py para Configurar o PYTHONPATH
```python
"""
Configuração para os testes do Fotix.
"""

import os
import sys
from pathlib import Path

# Adiciona o diretório src ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent / "fotix" / "src"))
```

### 9. Execução e Ajuste dos Testes

Executei os testes para verificar se a implementação estava correta:

```powershell
python -m pytest tests/unit/core/test_duplicate_finder.py -v
```

Inicialmente, dois testes falharam devido a uma diferença entre o comportamento esperado e o comportamento real da implementação:

1. No teste `test_one_duplicate_group`, esperava-se que a função de hash fosse chamada 5 vezes, mas foi chamada apenas 3 vezes.
2. No teste `test_multiple_duplicate_groups`, esperava-se que a função de hash fosse chamada 8 vezes, mas foi chamada apenas 7 vezes.

Isso ocorreu porque a implementação otimiza e não chama a função de hash para arquivos que não têm duplicatas por tamanho. Ajustei os testes para refletir esse comportamento:

```python
# Antes
assert hash_function.call_count == 5

# Depois
# Verifica se a hash_function foi chamada para os arquivos com tamanho 1000
# (a implementação otimiza e não chama a função para arquivos sem duplicatas por tamanho)
assert hash_function.call_count == 3
```

```python
# Antes
assert hash_function.call_count == 8

# Depois
# Verifica se a hash_function foi chamada para os arquivos em grupos com duplicatas por tamanho
# (a implementação otimiza e não chama a função para arquivos sem duplicatas por tamanho)
assert hash_function.call_count == 7
```

### 10. Verificação da Cobertura de Código

Verifiquei a cobertura de código para garantir que todos os caminhos de execução estavam sendo testados:

```powershell
python -m pytest tests/unit/core/test_duplicate_finder.py --cov=fotix.core.duplicate_finder
```

O resultado mostrou 100% de cobertura de código para o módulo `duplicate_finder.py`.

## Desvios da Especificação Original

Durante a implementação, não houve desvios significativos da especificação original. A única diferença foi a otimização na chamada da função de hash, que não é chamada para arquivos que não têm duplicatas por tamanho. Isso é uma otimização válida e está de acordo com a especificação, que menciona:

> Eficiência (Consideração): Usar estruturas de dados eficientes (ex: collections.defaultdict para agrupamento) para lidar potencialmente com muitos arquivos. A iteração principal sobre os arquivos ocorre apenas uma vez para agrupar por tamanho. O hashing ocorre apenas para grupos com tamanho > 1.

## Estrutura Final do Projeto

```
fotix/
├── src/
│   └── fotix/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   └── duplicate_finder.py
│       └── domain/
│           ├── __init__.py
│           └── models.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── unit/
│       ├── __init__.py
│       └── core/
│           ├── __init__.py
│           └── test_duplicate_finder.py
└── setup.py
```

## Diagrama Visual da Estrutura

```
+------------------+       +------------------+
|  DuplicateFinder |       |   FileMetadata   |
|------------------|       |------------------|
| find_duplicates()|------>| path: Path       |
+------------------+       | size: int        |
         |                 | creation_time    |
         |                 +------------------+
         |                          ^
         v                          |
+------------------+       +------------------+
|  DuplicateGroup  |       |   hash_function  |
|------------------|       |------------------|
| files: List      |<------| (FileMetadata)   |
| hash_value: str  |       |     -> str       |
| file_to_keep     |       +------------------+
+------------------+
```

O diagrama acima mostra as principais classes e suas relações:

1. `DuplicateFinder` é a classe principal que implementa a lógica de identificação de duplicatas.
2. `FileMetadata` é uma classe de dados que representa os metadados de um arquivo.
3. `DuplicateGroup` é uma classe de dados que representa um grupo de arquivos duplicados.
4. `hash_function` é uma função injetada que calcula o hash de um arquivo a partir de seu `FileMetadata`.

O fluxo de execução é o seguinte:

1. `DuplicateFinder.find_duplicates()` recebe um iterador de `FileMetadata` e uma função de hash.
2. Os arquivos são agrupados por tamanho.
3. Para cada grupo de arquivos com o mesmo tamanho, a função de hash é chamada para calcular o hash de cada arquivo.
4. Os arquivos com o mesmo hash são agrupados em instâncias de `DuplicateGroup`.
5. A lista de `DuplicateGroup` é retornada.
