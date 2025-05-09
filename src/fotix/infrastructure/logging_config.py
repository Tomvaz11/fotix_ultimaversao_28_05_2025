"""Configuração do sistema de logging para a aplicação Fotix."""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fotix.config import AppSettings # Usando AppSettings diretamente


def setup_logging(config: AppSettings) -> None:
    """Configura o sistema de logging da aplicação.

    Utiliza as configurações fornecidas em `config` para definir o nível de log,
    o formato das mensagens e os handlers (console e, opcionalmente, arquivo).

    Args:
        config: Uma instância de AppSettings contendo as configurações de log.
    """
    try:
        log_level_str = config.LOG_LEVEL.upper()
        log_level = getattr(logging, log_level_str, logging.INFO)

        # Limpa handlers existentes para evitar duplicação em reconfigurações
        # (útil em cenários de teste ou reinicialização)
        root_logger = logging.getLogger()
        if root_logger.hasHandlers():
            for handler in list(root_logger.handlers): # Iterar sobre uma cópia
                root_logger.removeHandler(handler)
                handler.close()


        formatter = logging.Formatter(config.LOG_FORMAT)

        # Configuração do handler para o console (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level) # Nível do handler pode ser o mesmo do logger raiz

        root_logger.addHandler(console_handler)
        root_logger.setLevel(log_level) # Nível do logger raiz

        # Configuração do handler para arquivo, se especificado
        if config.LOG_FILE_PATH:
            log_file_path = Path(config.LOG_FILE_PATH)
            
            # Garante que o diretório do arquivo de log exista
            log_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Usa RotatingFileHandler para evitar arquivos de log muito grandes
            # Max 5MB por arquivo, mantém até 3 arquivos de backup.
            file_handler = RotatingFileHandler(
                log_file_path, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(log_level) # Nível do handler pode ser o mesmo do logger raiz
            root_logger.addHandler(file_handler)
            
            root_logger.info(f"Logging configurado. Nível: {log_level_str}. Arquivo de log: {log_file_path}")
        else:
            root_logger.info(f"Logging configurado. Nível: {log_level_str}. Sem arquivo de log.")

    except Exception as e:
        # Fallback para logging básico em caso de erro na configuração
        logging.basicConfig(
            level=logging.WARNING,
            format="%(asctime)s - %(name)s - %(levelname)s - [ERRO NA CONFIG DE LOG] - %(message)s"
        )
        logging.critical(f"Falha ao configurar o logging principal: {e}. Usando fallback.", exc_info=True)

if __name__ == '__main__': # pragma: no cover
    # Exemplo de uso e teste manual
    print("Demonstração da configuração de logging...")

    # Simula configurações para teste
    class MockAppSettings:
        LOG_LEVEL = "DEBUG"
        LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s (%(filename)s:%(lineno)d)"
        LOG_FILE_PATH: Path | None = Path("./fotix_test_app.log") # Testar com arquivo
        # LOG_FILE_PATH: Path | None = None # Testar sem arquivo

    mock_config = MockAppSettings()
    
    print(f"Configurando logging com Nível: {mock_config.LOG_LEVEL}, Formato: '{mock_config.LOG_FORMAT}', Arquivo: {mock_config.LOG_FILE_PATH}")
    setup_logging(config=mock_config) # type: ignore 

    # Testando logs em diferentes níveis
    logging.debug("Este é um log de debug.")
    logging.info("Este é um log de info.")
    logging.warning("Este é um log de warning.")
    logging.error("Este é um log de error.")
    logging.critical("Este é um log crítico.")

    # Exemplo de um logger nomeado
    outro_logger = logging.getLogger("meu_modulo_especifico")
    outro_logger.info("Log de um módulo específico.")

    if mock_config.LOG_FILE_PATH:
        print(f"Verifique o arquivo de log em: {mock_config.LOG_FILE_PATH.resolve()}")
    print("Demonstração concluída.") 