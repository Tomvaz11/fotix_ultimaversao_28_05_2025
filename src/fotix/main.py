"""
Ponto de entrada da aplicação Fotix.

Este módulo é o ponto de entrada principal da aplicação Fotix. Ele é responsável por
inicializar as camadas da aplicação, configurar a UI principal e iniciar o loop de
eventos da GUI.

Exemplo de uso:
    ```
    python -m fotix.main
    ```
"""

import sys
import logging

from PySide6.QtWidgets import QApplication

from fotix.ui.main_window import MainWindow
from fotix.infrastructure.logging_config import setup_logging, get_logger
from fotix.config import get_config, get_log_level


# Configurar logger para este módulo
logger = get_logger(__name__)


def setup_application() -> QApplication:
    """
    Configura a aplicação Qt.

    Esta função cria e configura a instância de QApplication com informações
    básicas como nome da organização, nome da aplicação, etc. Se já existir
    uma instância de QApplication, ela será reutilizada.

    Returns:
        QApplication: A instância de QApplication configurada.
    """
    # Verificar se já existe uma instância de QApplication
    app = QApplication.instance()
    if app is None:
        # Criar uma nova instância se não existir
        app = QApplication(sys.argv)

    app.setOrganizationName("Fotix")
    app.setApplicationName("Fotix - Gerenciador de Duplicatas")

    # Configurar estilo da aplicação
    app.setStyle("Fusion")

    return app


def main() -> int:
    """
    Função principal da aplicação.

    Esta função é o ponto de entrada principal da aplicação Fotix. Ela configura
    o logging, inicializa a aplicação Qt, cria a janela principal e inicia o
    loop de eventos.

    Returns:
        int: Código de saída da aplicação (0 para sucesso, outro valor para erro).
    """
    try:
        # Configurar logging
        # log_level = get_log_level() # Comentado para forçar DEBUG
        setup_logging(log_level=logging.DEBUG) # Forçando nível DEBUG para diagnóstico
        logger.info("Iniciando aplicação Fotix com LOG LEVEL FORÇADO PARA DEBUG")

        # Registrar informações básicas
        config = get_config()
        logger.debug(f"Configurações carregadas: {config}")

        # Configurar e iniciar a aplicação Qt
        app = setup_application()
        logger.debug("Aplicação Qt configurada")

        # Criar e exibir a janela principal
        main_window = MainWindow()
        main_window.show()
        logger.info("Janela principal exibida")

        # Iniciar o loop de eventos
        logger.debug("Iniciando loop de eventos")
        exit_code = app.exec()

        # Finalizar a aplicação
        logger.info(f"Aplicação finalizada com código de saída: {exit_code}")
        return exit_code

    except Exception as e:
        # Registrar erro não tratado
        logger.critical(f"Erro não tratado na aplicação: {str(e)}", exc_info=True)

        # Se a exceção ocorrer antes da inicialização da UI, exibir mensagem no console
        print(f"Erro crítico: {str(e)}")

        return 1


if __name__ == "__main__":
    sys.exit(main())
