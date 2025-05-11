# Fotix - Módulo de Concorrência

O módulo de concorrência (`concurrency.py`) implementa a interface `IConcurrencyService`, fornecendo métodos para executar tarefas em paralelo e em background, utilizando a biblioteca `concurrent.futures` do Python.

## Funcionalidades

- **Execução paralela de tarefas**: Permite executar múltiplas funções simultaneamente, aproveitando múltiplos núcleos de CPU ou threads.
- **Tarefas em background**: Permite submeter tarefas para execução em segundo plano e monitorar seu progresso.
- **Configuração automática**: Determina automaticamente o número ideal de workers com base nos recursos do sistema ou nas configurações fornecidas.
- **Suporte a threads e processos**: Permite escolher entre `ThreadPoolExecutor` (para tarefas IO-bound) e `ProcessPoolExecutor` (para tarefas CPU-bound).
- **Gerenciamento de recursos**: Libera automaticamente os recursos quando não são mais necessários.

## Uso Básico

### Execução Paralela de Tarefas

```python
from fotix.infrastructure.concurrency import ConcurrencyService

# Criar uma instância do serviço
concurrency_service = ConcurrencyService()

# Definir algumas tarefas
def task1():
    # Alguma operação demorada
    return "Resultado 1"

def task2():
    # Outra operação demorada
    return "Resultado 2"

# Executar as tarefas em paralelo
results = concurrency_service.run_parallel([task1, task2])
print(results)  # ["Resultado 1", "Resultado 2"]
```

### Tarefas em Background

```python
from fotix.infrastructure.concurrency import ConcurrencyService

# Criar uma instância do serviço
concurrency_service = ConcurrencyService()

# Definir uma tarefa com argumentos
def process_file(file_path, options):
    # Processamento demorado
    return f"Arquivo {file_path} processado com {options}"

# Submeter a tarefa para execução em background
future = concurrency_service.submit_background_task(
    process_file, 
    "caminho/para/arquivo.txt", 
    options={"quality": "high"}
)

# Verificar se a tarefa foi concluída
if future.done():
    print("Tarefa concluída!")
else:
    print("Tarefa ainda em execução...")

# Obter o resultado (bloqueia até a conclusão)
result = future.result()
print(result)  # "Arquivo caminho/para/arquivo.txt processado com {'quality': 'high'}"
```

### Uso com Processos (para tarefas CPU-bound)

```python
from fotix.infrastructure.concurrency import ConcurrencyService

# Criar uma instância do serviço usando processos
concurrency_service = ConcurrencyService(use_processes=True)

# Definir tarefas CPU-intensivas
def compute_hash(data):
    # Cálculo intensivo de hash
    return hash(data)

# Executar as tarefas em processos paralelos
results = concurrency_service.run_parallel([
    lambda: compute_hash("dados1"),
    lambda: compute_hash("dados2"),
    lambda: compute_hash("dados3")
])
```

### Liberação de Recursos

```python
from fotix.infrastructure.concurrency import ConcurrencyService

concurrency_service = ConcurrencyService()

# ... usar o serviço ...

# Liberar recursos quando não for mais necessário
concurrency_service.shutdown()
```

## Configuração

O serviço de concorrência pode ser configurado de várias maneiras:

1. **Diretamente no construtor**:
   ```python
   # Limitar a 4 workers
   concurrency_service = ConcurrencyService(max_workers=4)
   
   # Usar processos em vez de threads
   concurrency_service = ConcurrencyService(use_processes=True)
   ```

2. **Via arquivo de configuração**:
   ```json
   {
     "concurrency": {
       "max_workers": 8
     }
   }
   ```

Se não for especificado, o número de workers será determinado automaticamente:
- Para threads: `min(32, os.cpu_count() * 4)`
- Para processos: `os.cpu_count()`

## Considerações de Uso

- Use **threads** (`use_processes=False`, padrão) para tarefas **IO-bound** (leitura/escrita de arquivos, rede).
- Use **processos** (`use_processes=True`) para tarefas **CPU-bound** (cálculos intensivos, processamento de imagens).
- Evite compartilhar objetos complexos entre processos, pois isso pode causar problemas de serialização.
- Lembre-se de chamar `shutdown()` quando terminar de usar o serviço para liberar recursos.
- Para tarefas muito simples, o overhead de criar threads/processos pode superar o benefício da paralelização.
