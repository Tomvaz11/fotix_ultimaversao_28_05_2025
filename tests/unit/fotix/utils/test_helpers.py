"""
Testes unitários para o módulo de funções auxiliares.

Este módulo contém testes para verificar o funcionamento correto das funções
utilitárias definidas em fotix.utils.helpers.
"""

import time
import pytest
from unittest.mock import MagicMock, patch

from fotix.utils.helpers import retry, chunk_list, measure_time


class TestRetry:
    """Testes para a função decoradora retry."""

    def test_successful_execution(self):
        """Testa se a função é executada normalmente quando não há exceções."""
        # Arrange
        mock_function = MagicMock(return_value="success")
        decorated_function = retry()(mock_function)

        # Act
        result = decorated_function("arg1", kwarg1="value1")

        # Assert
        assert result == "success"
        mock_function.assert_called_once_with("arg1", kwarg1="value1")

    def test_retry_on_exception(self):
        """Testa se a função é repetida quando ocorre uma exceção."""
        # Arrange
        mock_function = MagicMock(side_effect=[ValueError("Erro 1"), ValueError("Erro 2"), "success"])
        decorated_function = retry(max_attempts=3, delay=0.01)(mock_function)

        # Act
        result = decorated_function()

        # Assert
        assert result == "success"
        assert mock_function.call_count == 3

    def test_max_attempts_reached(self):
        """Testa se a exceção é propagada quando o número máximo de tentativas é atingido."""
        # Arrange
        mock_function = MagicMock(side_effect=ValueError("Erro de teste"))
        decorated_function = retry(max_attempts=3, delay=0.01)(mock_function)

        # Act & Assert
        with pytest.raises(ValueError, match="Erro de teste"):
            decorated_function()

        assert mock_function.call_count == 3

    def test_specific_exceptions(self):
        """Testa se apenas as exceções especificadas são capturadas."""
        # Arrange
        mock_function = MagicMock(side_effect=[ValueError("Erro 1"), "success"])
        decorated_function = retry(max_attempts=3, delay=0.01, exceptions=(ValueError,))(mock_function)

        # Act
        result = decorated_function()

        # Assert
        assert result == "success"
        assert mock_function.call_count == 2

    def test_ignore_other_exceptions(self):
        """Testa se exceções não especificadas são propagadas imediatamente."""
        # Arrange
        mock_function = MagicMock(side_effect=TypeError("Erro de tipo"))
        decorated_function = retry(max_attempts=3, delay=0.01, exceptions=(ValueError,))(mock_function)

        # Act & Assert
        with pytest.raises(TypeError, match="Erro de tipo"):
            decorated_function()

        assert mock_function.call_count == 1

    def test_with_logger(self):
        """Testa se o logger é utilizado corretamente."""
        # Arrange
        def test_func():
            pass

        mock_function = MagicMock(side_effect=[ValueError("Erro 1"), "success"])
        mock_function.__name__ = "test_func"
        mock_logger = MagicMock()

        decorated_function = retry(
            max_attempts=3,
            delay=0.01,
            exceptions=(ValueError,),
            logger=mock_logger
        )(mock_function)

        # Act
        result = decorated_function()

        # Assert
        assert result == "success"
        assert mock_function.call_count == 2
        assert mock_logger.warning.call_count == 1
        assert mock_logger.info.call_count == 1

    def test_with_logger_all_attempts_fail(self):
        """Testa se o logger registra erro quando todas as tentativas falham."""
        # Arrange
        def test_func():
            pass

        mock_function = MagicMock(side_effect=[ValueError("Erro 1"), ValueError("Erro 2"), ValueError("Erro 3")])
        mock_function.__name__ = "test_func"
        mock_logger = MagicMock()

        decorated_function = retry(
            max_attempts=3,
            delay=0.01,
            exceptions=(ValueError,),
            logger=mock_logger
        )(mock_function)

        # Act & Assert
        with pytest.raises(ValueError):
            decorated_function()

        assert mock_function.call_count == 3
        assert mock_logger.warning.call_count == 3
        assert mock_logger.info.call_count == 2
        assert mock_logger.error.call_count == 1
        mock_logger.error.assert_called_once_with(
            "Todas as 3 tentativas falharam para test_func"
        )


class TestChunkList:
    """Testes para a função chunk_list."""

    def test_empty_list(self):
        """Testa se a função lida corretamente com uma lista vazia."""
        # Act
        result = chunk_list([], 3)

        # Assert
        assert result == []

    def test_chunk_size_equal_to_list_size(self):
        """Testa se a função lida corretamente quando o tamanho do chunk é igual ao tamanho da lista."""
        # Arrange
        items = [1, 2, 3]

        # Act
        result = chunk_list(items, 3)

        # Assert
        assert result == [[1, 2, 3]]

    def test_chunk_size_greater_than_list_size(self):
        """Testa se a função lida corretamente quando o tamanho do chunk é maior que o tamanho da lista."""
        # Arrange
        items = [1, 2, 3]

        # Act
        result = chunk_list(items, 5)

        # Assert
        assert result == [[1, 2, 3]]

    def test_chunk_size_divides_list_size_evenly(self):
        """Testa se a função divide corretamente quando o tamanho da lista é múltiplo do tamanho do chunk."""
        # Arrange
        items = [1, 2, 3, 4, 5, 6]

        # Act
        result = chunk_list(items, 2)

        # Assert
        assert result == [[1, 2], [3, 4], [5, 6]]

    def test_chunk_size_does_not_divide_list_size_evenly(self):
        """Testa se a função divide corretamente quando o tamanho da lista não é múltiplo do tamanho do chunk."""
        # Arrange
        items = [1, 2, 3, 4, 5, 6, 7]

        # Act
        result = chunk_list(items, 3)

        # Assert
        assert result == [[1, 2, 3], [4, 5, 6], [7]]


class TestMeasureTime:
    """Testes para o decorador measure_time."""

    @patch('time.time')
    @patch('builtins.print')
    def test_measure_time(self, mock_print, mock_time):
        """Testa se o decorador mede corretamente o tempo de execução."""
        # Arrange
        mock_time.side_effect = [10.0, 12.5]  # Simula 2.5 segundos de execução

        @measure_time
        def test_function():
            return "result"

        # Act
        result = test_function()

        # Assert
        assert result == "result"
        mock_print.assert_called_once_with("Função test_function executada em 2.5000 segundos")

    @patch('time.time')
    @patch('builtins.print')
    def test_measure_time_with_args(self, mock_print, mock_time):
        """Testa se o decorador preserva os argumentos da função."""
        # Arrange
        mock_time.side_effect = [10.0, 12.5]

        @measure_time
        def test_function(a, b, c=3):
            return a + b + c

        # Act
        result = test_function(1, 2, c=4)

        # Assert
        assert result == 7
        mock_print.assert_called_once_with("Função test_function executada em 2.5000 segundos")
