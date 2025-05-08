"""
Exemplo de uso do módulo de logging do Fotix.
"""

from fotix.infrastructure.logging_config import setup_logging, get_logger, update_log_level

# Configurar o logging
logger_root = setup_logging(log_level="INFO")
logger_root.info("Logging configurado com sucesso.")

# Obter um logger para este módulo
logger = get_logger(__name__)

# Demonstrar diferentes níveis de log
logger.debug("Esta mensagem de DEBUG não deve aparecer com nível INFO")
logger.info("Esta é uma mensagem de INFO")
logger.warning("Este é um AVISO")
logger.error("Este é um ERRO")

# Alterar o nível de log para DEBUG
update_log_level("DEBUG")

# Agora a mensagem de DEBUG deve aparecer
logger.debug("Agora esta mensagem de DEBUG deve aparecer")

print("Exemplo concluído. Verifique o console acima e o arquivo de log.") 