"""
Testes de integração para a infraestrutura básica:
- fotix.config
- fotix.infrastructure.logging_config
- fotix.infrastructure.file_system
"""
import pytest
import logging
import tempfile
import shutil
from pathlib import Path
import configparser

# Suposições de importação baseadas no blueprint e nos nomes dos módulos
# Estas importações podem precisar de ajuste dependendo da estrutura real do projeto
from fotix.config import AppConfig # Supondo que AppConfig é a classe de configuração
from fotix.infrastructure.logging_config import setup_logging # Supondo esta função de setup
from fotix.infrastructure.file_system import FileSystemService # Implementação real
from fotix.infrastructure.interfaces import IFileSystemService # Interface

# Nome do logger usado pelo FileSystemService (suposição, pode precisar de ajuste)
FS_LOGGER_NAME = FileSystemService.logger.name if hasattr(FileSystemService, 'logger') else 'fotix.infrastructure.file_system'


@pytest.fixture(scope="function")
def temp_config_file_path():
    """
    Cria um arquivo de configuração temporário para os testes.
    Retorna o caminho para o arquivo e o deleta após o teste.
    """
    temp_dir = tempfile.mkdtemp()
    config_file = Path(temp_dir) / "test_config.ini"

    def _create_config(log_level="INFO", backup_path="default/backup/path"):
        config = configparser.ConfigParser()
        config["Logging"] = {"level": log_level}
        config["Paths"] = {"backup_directory": backup_path}
        with open(config_file, "w") as f:
            config.write(f)
        return config_file

    yield _create_config
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="function")
def base_temp_dir():
    """
    Cria um diretório temporário para testes do FileSystemService.
    O diretório é limpo após os testes.
    """
    test_dir = Path(tempfile.mkdtemp(prefix="fotix_fs_test_"))
    yield test_dir
    shutil.rmtree(test_dir)


@pytest.fixture(scope="function")
def file_system_service() -> IFileSystemService:
    """Fornece uma instância do FileSystemService."""
    # O FileSystemService real não deve precisar de argumentos se for autossuficiente
    # ou se suas dependências (como config) forem obtidas globalmente ou via DI implícita.
    # Se ele precisa de config, isso pode precisar ser ajustado.
    return FileSystemService()


def test_config_loading_and_logging_setup(temp_config_file_path, caplog):
    """
    Cenário 1: Carregamento de Configuração e Logging.
    Verifica se as configurações são carregadas e o logging funciona conforme configurado.
    """
    # Teste com nível DEBUG
    debug_config_path = temp_config_file_path(log_level="DEBUG")
    debug_app_config = AppConfig(config_file_path=str(debug_config_path))
    
    # Reseta os handlers para evitar duplicação entre chamadas de setup_logging
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    setup_logging(config=debug_app_config) # Supondo que setup_logging usa o config

    test_logger = logging.getLogger("test_integration_logger_debug")
    
    with caplog.at_level(logging.DEBUG, logger=test_logger.name):
        test_logger.debug("Esta é uma mensagem de debug.")
        test_logger.info("Esta é uma mensagem de info.")
    
    assert "Esta é uma mensagem de debug." in caplog.text
    assert "Esta é uma mensagem de info." in caplog.text
    caplog.clear()

    # Teste com nível WARNING
    warning_config_path = temp_config_file_path(log_level="WARNING")
    warning_app_config = AppConfig(config_file_path=str(warning_config_path))

    # Reseta os handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
        
    setup_logging(config=warning_app_config)
    
    test_logger_warning = logging.getLogger("test_integration_logger_warning")

    with caplog.at_level(logging.INFO, logger=test_logger_warning.name): # Captura INFO para ver o que NÃO é logado
        test_logger_warning.debug("Esta mensagem de debug NÃO deve aparecer.")
        test_logger_warning.info("Esta mensagem de info NÃO deve aparecer.")
        test_logger_warning.warning("Esta é uma mensagem de warning.")
    
    assert "Esta mensagem de debug NÃO deve aparecer." not in caplog.text
    assert "Esta mensagem de info NÃO deve aparecer." not in caplog.text
    assert "Esta é uma mensagem de warning." in caplog.text
    caplog.clear()

    # Garante que o logger raiz também reflita a configuração (opcional, depende da implementação de setup_logging)
    # Este teste pode precisar de ajuste fino com base em como setup_logging afeta o logger raiz
    # e os loggers específicos da aplicação.
    # Por enquanto, focamos nos loggers de teste.


def test_file_system_service_operations_with_logging(
    file_system_service: IFileSystemService, base_temp_dir: Path, caplog
):
    """
    Cenário 2: Operações do FileSystemService com Logging.
    Verifica operações e logs gerados.
    """
    # Configura logging para este teste (pode ser herdado se configurado globalmente via autouse fixture)
    # Aqui, vamos assumir uma configuração de logging padrão ou reconfigurar rapidamente.
    # Idealmente, setup_logging já foi chamado, ou uma fixture garante isso.
    # Para isolamento, vamos assumir que o logger do FileSystemService está ativo e em um nível que captura INFO/DEBUG.
    # Se `setup_logging` não foi chamado por uma fixture, você pode precisar chamá-lo aqui
    # com uma configuração padrão/de teste.
    
    # Exemplo: garantir que o logger do FileSystemService esteja em DEBUG para capturar tudo
    # logging.getLogger(FS_LOGGER_NAME).setLevel(logging.DEBUG) # Ajuste conforme necessário

    test_file = base_temp_dir / "test_file.txt"
    test_content = "Conteúdo do arquivo de teste."
    
    caplog.set_level(logging.DEBUG, logger=FS_LOGGER_NAME)

    # Criar e escrever arquivo
    with open(test_file, "w") as f:
        f.write(test_content)
    assert file_system_service.path_exists(test_file)
    # Log de criação (se FileSystemService logar isso internamente ao ser usado para criar/verificar)
    # Se FileSystemService não loga a criação externa, não haverá log aqui.
    # Vamos focar nas operações do próprio serviço.

    # Testar get_file_size
    size = file_system_service.get_file_size(test_file)
    assert size == len(test_content.encode('utf-8'))
    assert f"Calculando tamanho do arquivo: {test_file}" in caplog.text # Suposição de mensagem de log
    caplog.clear()

    # Testar list_directory_contents
    sub_dir = base_temp_dir / "sub"
    file_system_service.create_directory(sub_dir)
    assert f"Criando diretório: {sub_dir}" in caplog.text
    caplog.clear()

    another_file = sub_dir / "another.log"
    with open(another_file, "w") as f:
        f.write("log content")
    
    contents = list(file_system_service.list_directory_contents(base_temp_dir, recursive=True))
    assert test_file in contents
    assert another_file in contents
    assert f"Listando conteúdo do diretório: {base_temp_dir}" in caplog.text # Suposição de mensagem de log
    caplog.clear()

    # Testar move_to_trash (difícil de verificar o log exato sem saber a implementação)
    # Apenas verificamos que a função é chamada e o arquivo não existe mais
    # send2trash pode ter seus próprios logs ou não, FileSystemService pode logar a chamada.
    file_system_service.move_to_trash(test_file)
    assert not file_system_service.path_exists(test_file)
    assert f"Movendo para lixeira: {test_file}" in caplog.text # Suposição de mensagem de log
    caplog.clear()


def test_file_system_service_error_handling_with_logging(
    file_system_service: IFileSystemService, base_temp_dir: Path, caplog
):
    """
    Cenário 3: Tratamento de Erro no FileSystemService com Logging.
    Verifica exceções e logs de ERRO.
    """
    # logging.getLogger(FS_LOGGER_NAME).setLevel(logging.DEBUG) # Assegura captura de todos os níveis
    caplog.set_level(logging.ERROR, logger=FS_LOGGER_NAME)

    non_existent_file = base_temp_dir / "arquivo_nao_existe.txt"

    # Tentar obter tamanho de arquivo inexistente
    # A interface IFileSystemService especifica `get_file_size(...) -> int | None`
    # Então, deve retornar None, não levantar FileNotFoundError diretamente,
    # mas pode logar um warning ou erro se essa for a política.
    # O cenário de teste original pede para "verificar se a exceção apropriada é levantada"
    # Isso implica que algumas operações podem levantar exceções.
    # Vamos ajustar para uma operação que DEVE levantar exceção, como stream_file_content

    with pytest.raises(FileNotFoundError): # Supondo que stream_file_content levanta se não existe
        # Consome o gerador para forçar a execução
        list(file_system_service.stream_file_content(non_existent_file))

    # Verifica o log de ERRO (a mensagem exata depende da implementação)
    assert f"Erro ao tentar ler o arquivo {non_existent_file}: Arquivo não encontrado." in caplog.text or \
           f"Arquivo não encontrado: {non_existent_file}" in caplog.text # Flexibilidade na mensagem
    caplog.clear()

    # Tentar mover para lixeira arquivo inexistente
    # send2trash pode levantar exceção se o arquivo não existir.
    # FileSystemService deveria capturar e logar, ou propagar.
    # Se propaga, o teste deve esperar a exceção. Se trata, verifica o log.
    # Vamos assumir que FileSystemService loga um erro e não levanta, ou levanta uma exceção customizada.
    # Para o teste, vamos assumir que ele falha "graciosamente" (não levanta, mas loga erro)
    # ou levanta uma exceção específica que o teste espera.
    # O blueprint diz "Lança exceção em caso de falha" para move_to_trash.
    
    # Se send2trash.exceptions.TrashPermissionError ou FileNotFoundError podem ocorrer
    with pytest.raises(Exception): # Genérico, idealmente seria mais específico
        file_system_service.move_to_trash(non_existent_file)
    
    assert f"Erro ao mover para lixeira {non_existent_file}" in caplog.text or \
           f"Falha ao mover para lixeira, arquivo não encontrado: {non_existent_file}" in caplog.text # Flexibilidade
    caplog.clear() 