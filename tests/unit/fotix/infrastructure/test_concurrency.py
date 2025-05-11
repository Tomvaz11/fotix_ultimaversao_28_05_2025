"""
Testes unitários para o módulo de concorrência.

Este módulo contém testes para verificar o funcionamento correto do ConcurrencyService,
incluindo execução paralela de tarefas e submissão de tarefas em background.
"""

import time
import pytest
from concurrent.futures import Future
from unittest.mock import patch, MagicMock

from fotix.infrastructure.concurrency import ConcurrencyService


class TestConcurrencyService:
    """Testes para a classe ConcurrencyService."""

    def test_init_default_values(self):
        """Testa se a inicialização com valores padrão funciona corretamente."""
        # Arrange & Act
        service = ConcurrencyService()

        # Assert
        assert service._use_processes is False
        assert service._max_workers is not None
        assert service._executor is None

    def test_init_custom_values(self):
        """Testa se a inicialização com valores personalizados funciona corretamente."""
        # Arrange & Act
        service = ConcurrencyService(max_workers=5, use_processes=True)

        # Assert
        assert service._use_processes is True
        assert service._max_workers == 5
        assert service._executor is None

    def test_init_from_config(self):
        """Testa se a inicialização a partir da configuração funciona corretamente."""
        # Arrange
        with patch('fotix.infrastructure.concurrency.get_config') as mock_get_config:
            mock_get_config.return_value = {
                "concurrency": {
                    "max_workers": 8
                }
            }

            # Act
            service = ConcurrencyService()

            # Assert
            assert service._max_workers == 8
            mock_get_config.assert_called_once()

    def test_init_with_processes_cpu_count(self):
        """Testa se a inicialização com processos usa o número de CPUs quando não há configuração."""
        # Arrange
        with patch('fotix.infrastructure.concurrency.get_config') as mock_get_config, \
             patch('fotix.infrastructure.concurrency.os.cpu_count') as mock_cpu_count:
            mock_get_config.return_value = {}  # Sem configuração
            mock_cpu_count.return_value = 4

            # Act
            service = ConcurrencyService(use_processes=True)

            # Assert
            assert service._max_workers == 4
            mock_cpu_count.assert_called_once()

    def test_get_executor_thread(self):
        """Testa se o método _get_executor cria um ThreadPoolExecutor quando use_processes=False."""
        # Arrange
        service = ConcurrencyService(max_workers=3, use_processes=False)

        # Act
        executor = service._get_executor()

        # Assert
        assert executor is not None
        assert service._executor is executor
        assert executor.__class__.__name__ == 'ThreadPoolExecutor'

    def test_get_executor_process(self):
        """Testa se o método _get_executor cria um ProcessPoolExecutor quando use_processes=True."""
        # Arrange
        service = ConcurrencyService(max_workers=3, use_processes=True)

        # Act
        executor = service._get_executor()

        # Assert
        assert executor is not None
        assert service._executor is executor
        assert executor.__class__.__name__ == 'ProcessPoolExecutor'

    def test_run_parallel(self):
        """Testa se o método run_parallel executa tarefas em paralelo e retorna os resultados na ordem correta."""
        # Arrange
        service = ConcurrencyService(max_workers=4)

        def task1():
            time.sleep(0.1)
            return 1

        def task2():
            time.sleep(0.05)
            return 2

        def task3():
            time.sleep(0.2)
            return 3

        tasks = [task1, task2, task3]

        # Act
        results = service.run_parallel(tasks)

        # Assert
        assert results == [1, 2, 3]

    def test_run_parallel_empty_tasks(self):
        """Testa se o método run_parallel lida corretamente com uma lista vazia de tarefas."""
        # Arrange
        service = ConcurrencyService()

        # Act
        results = service.run_parallel([])

        # Assert
        assert results == []

    def test_run_parallel_with_exception(self):
        """Testa se o método run_parallel propaga exceções corretamente."""
        # Arrange
        service = ConcurrencyService()

        def task_with_exception():
            raise ValueError("Erro de teste")

        # Act & Assert
        with pytest.raises(ValueError, match="Erro de teste"):
            service.run_parallel([task_with_exception])

    def test_submit_background_task(self):
        """Testa se o método submit_background_task submete uma tarefa e retorna um Future."""
        # Arrange
        service = ConcurrencyService()

        def task(x, y):
            time.sleep(0.1)
            return x + y

        # Act
        future = service.submit_background_task(task, 2, 3)

        # Assert
        assert isinstance(future, Future)
        assert future.result() == 5

    def test_submit_background_task_with_exception(self):
        """Testa se o método submit_background_task lida corretamente com exceções na tarefa."""
        # Arrange
        service = ConcurrencyService()

        def task_with_exception():
            raise ValueError("Erro de teste")

        # Act
        future = service.submit_background_task(task_with_exception)

        # Assert
        with pytest.raises(ValueError, match="Erro de teste"):
            future.result()

    def test_shutdown(self):
        """Testa se o método shutdown encerra o executor corretamente."""
        # Arrange
        service = ConcurrencyService()
        executor = service._get_executor()

        # Mock o método shutdown do executor
        executor.shutdown = MagicMock()

        # Act
        service.shutdown(wait=True)

        # Assert
        executor.shutdown.assert_called_once_with(wait=True)
        assert service._executor is None

    def test_shutdown_without_executor(self):
        """Testa se o método shutdown lida corretamente quando não há executor."""
        # Arrange
        service = ConcurrencyService()
        assert service._executor is None

        # Act & Assert (não deve lançar exceção)
        service.shutdown()
        assert service._executor is None
