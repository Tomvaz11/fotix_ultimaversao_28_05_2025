"""
Funções auxiliares genéricas para o Fotix.

Este módulo contém funções utilitárias que podem ser usadas em diferentes
partes da aplicação, sem dependências específicas de outros módulos do Fotix.
"""

import time
from typing import Callable, TypeVar, Any, List, Dict, Optional, Tuple
from functools import wraps
import logging

# Tipo genérico para resultados de funções
T = TypeVar('T')


def retry(max_attempts: int = 3, delay: float = 1.0, 
          backoff_factor: float = 2.0, exceptions: Tuple[Exception, ...] = (Exception,),
          logger: Optional[logging.Logger] = None) -> Callable:
    """
    Decorador para tentar executar uma função várias vezes em caso de exceção.
    
    Args:
        max_attempts: Número máximo de tentativas. Default é 3.
        delay: Tempo de espera inicial entre tentativas em segundos. Default é 1.0.
        backoff_factor: Fator de multiplicação do delay a cada nova tentativa. Default é 2.0.
        exceptions: Tupla de exceções que devem ser capturadas. Default é (Exception,).
        logger: Logger opcional para registrar as tentativas e erros.
    
    Returns:
        Callable: Decorador que envolve a função alvo.
    
    Example:
        ```python
        @retry(max_attempts=3, delay=1.0, exceptions=(ConnectionError, TimeoutError))
        def fetch_data(url):
            # Código que pode falhar temporariamente
            return requests.get(url).json()
        ```
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if logger:
                        logger.warning(
                            f"Tentativa {attempt}/{max_attempts} falhou para {func.__name__}: {str(e)}"
                        )
                    
                    if attempt < max_attempts:
                        if logger:
                            logger.info(f"Aguardando {current_delay:.2f}s antes da próxima tentativa")
                        
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        if logger:
                            logger.error(
                                f"Todas as {max_attempts} tentativas falharam para {func.__name__}"
                            )
            
            # Se chegou aqui, todas as tentativas falharam
            raise last_exception
        
        return wrapper
    
    return decorator


def chunk_list(items: List[T], chunk_size: int) -> List[List[T]]:
    """
    Divide uma lista em chunks de tamanho especificado.
    
    Args:
        items: Lista a ser dividida.
        chunk_size: Tamanho de cada chunk.
    
    Returns:
        List[List[T]]: Lista de chunks.
    
    Example:
        ```python
        chunks = chunk_list([1, 2, 3, 4, 5, 6, 7], 3)
        # Resultado: [[1, 2, 3], [4, 5, 6], [7]]
        ```
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def measure_time(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorador para medir o tempo de execução de uma função.
    
    Args:
        func: Função a ser medida.
    
    Returns:
        Callable: Função decorada que registra o tempo de execução.
    
    Example:
        ```python
        @measure_time
        def process_data(data):
            # Processamento que pode ser demorado
            return result
        ```
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        print(f"Função {func.__name__} executada em {end_time - start_time:.4f} segundos")
        return result
    
    return wrapper
