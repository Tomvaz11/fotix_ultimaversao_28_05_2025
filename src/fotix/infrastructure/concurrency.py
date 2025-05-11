"""
Módulo de concorrência para o Fotix.

Este módulo implementa a interface IConcurrencyService, fornecendo métodos para
executar tarefas em paralelo e em background, utilizando a biblioteca concurrent.futures.
Permite otimizar a execução de operações como varredura de arquivos e processamento
de dados, aproveitando múltiplos núcleos de CPU e threads.
"""

import os
from concurrent.futures import Future, ThreadPoolExecutor, ProcessPoolExecutor
from typing import Callable, Iterable, List, TypeVar, Optional

from fotix.infrastructure.logging_config import get_logger
from fotix.config import get_config

# Tipo genérico para resultados de operações paralelas
T = TypeVar('T')
R = TypeVar('R')

# Logger para este módulo
logger = get_logger(__name__)


class ConcurrencyService:
    """
    Implementação da interface IConcurrencyService.

    Esta classe fornece métodos para executar tarefas em paralelo e em background,
    utilizando threads ou processos. Gerencia automaticamente o pool de workers
    com base nas configurações e recursos do sistema.
    """

    def __init__(self, max_workers: Optional[int] = None, use_processes: bool = False):
        """
        Inicializa o serviço de concorrência.

        Args:
            max_workers: Número máximo de workers (threads ou processos).
                        Se None, será determinado automaticamente com base no sistema.
            use_processes: Se True, usa ProcessPoolExecutor em vez de ThreadPoolExecutor.
                          Recomendado para tarefas CPU-bound. Default é False.
        """
        self._use_processes = use_processes

        # Se max_workers não for especificado, determina automaticamente
        if max_workers is None:
            config = get_config()
            # Tenta obter da configuração, ou usa um valor baseado no sistema
            config_max_workers = config.get("concurrency", {}).get("max_workers")

            if config_max_workers is not None:
                max_workers = config_max_workers
            else:
                # Se não estiver na configuração, usa um valor baseado no sistema
                if use_processes:
                    # Para processos, usa o número de CPUs
                    max_workers = os.cpu_count() or 4
                else:
                    # Para threads, usa um múltiplo do número de CPUs
                    # (threads são boas para tarefas IO-bound)
                    cpu_count = os.cpu_count() or 4
                    max_workers = min(32, cpu_count * 4)  # Limita a 32 threads

        self._max_workers = max_workers
        self._executor = None

        logger.debug(f"ConcurrencyService inicializado com max_workers={max_workers}, "
                    f"use_processes={use_processes}")

    def _get_executor(self):
        """
        Obtém ou cria o executor apropriado (thread ou process).

        Returns:
            ThreadPoolExecutor ou ProcessPoolExecutor: O executor a ser usado.
        """
        if self._executor is None:
            if self._use_processes:
                logger.debug(f"Criando ProcessPoolExecutor com {self._max_workers} workers")
                self._executor = ProcessPoolExecutor(max_workers=self._max_workers)
            else:
                logger.debug(f"Criando ThreadPoolExecutor com {self._max_workers} workers")
                self._executor = ThreadPoolExecutor(max_workers=self._max_workers)

        return self._executor

    def run_parallel(self, tasks: Iterable[Callable[[], T]]) -> List[T]:
        """
        Executa uma coleção de funções (tasks) em paralelo e retorna os resultados.

        Args:
            tasks: Coleção de funções sem argumentos que retornam um resultado.
                  Cada função deve ser independente e thread-safe.

        Returns:
            List[T]: Os resultados das funções, na mesma ordem das tasks fornecidas.

        Note:
            Esta implementação gerencia internamente o pool de workers e o número
            máximo de threads/processos concorrentes, com base nas configurações
            e recursos do sistema.
        """
        executor = self._get_executor()
        task_list = list(tasks)  # Converte para lista para garantir a ordem

        logger.debug(f"Executando {len(task_list)} tarefas em paralelo")

        try:
            # Submete todas as tarefas e coleta os resultados na ordem
            results = list(executor.map(lambda f: f(), task_list))
            logger.debug(f"Execução paralela concluída com {len(results)} resultados")
            return results
        except Exception as e:
            logger.error(f"Erro durante execução paralela: {str(e)}")
            raise

    def submit_background_task(self, task: Callable[..., R], *args, **kwargs) -> Future[R]:
        """
        Submete uma tarefa para execução em background e retorna um objeto Future.

        Args:
            task: Função a ser executada em background.
            *args: Argumentos posicionais para a função.
            **kwargs: Argumentos nomeados para a função.

        Returns:
            Future[R]: Objeto Future que representa a execução da tarefa.
                      Pode ser usado para verificar o status, obter o resultado
                      ou cancelar a execução.
        """
        executor = self._get_executor()

        logger.debug(f"Submetendo tarefa em background: {task.__name__ if hasattr(task, '__name__') else str(task)}")

        # Submete a tarefa ao executor
        future = executor.submit(task, *args, **kwargs)

        return future

    def shutdown(self, wait: bool = True):
        """
        Encerra o executor, liberando recursos.

        Args:
            wait: Se True, aguarda a conclusão de todas as tarefas pendentes.
                 Se False, cancela as tarefas pendentes.
        """
        if self._executor is not None:
            logger.debug(f"Encerrando executor (wait={wait})")
            self._executor.shutdown(wait=wait)
            self._executor = None

    def __del__(self):
        """
        Destrutor que garante o encerramento do executor quando o objeto é coletado.
        """
        self.shutdown(wait=False)
