"""Testes para o módulo de configuração fotix.config."""

import os
from pathlib import Path
from unittest import mock

import pytest
from pydantic import ValidationError

# Importa o módulo a ser testado.
# É importante limpar o cache de get_settings antes de cada teste
# para garantir que as configurações sejam recarregadas.
from fotix.config import AppSettings, get_settings, VALID_LOG_LEVELS

# Objeto para simular variáveis de ambiente
@pytest.fixture(autouse=True)
def clear_settings_cache_and_env_vars():
    """Limpa o cache de get_settings() e as variáveis de ambiente relevantes antes de cada teste."""
    get_settings.cache_clear()
    # Lista de variáveis de ambiente que o AppSettings pode usar
    env_vars_to_clear = [
        "FOTIX_BACKUP_PATH",
        "FOTIX_LOG_LEVEL",
        "FOTIX_LOG_FORMAT",
        "FOTIX_LOG_FILE_PATH",
        "DOTENV_PATH"  # Se Pydantic estiver configurado para usar isso
    ]
    # Salva e remove as variáveis de ambiente existentes
    original_env_vars = {}
    for var_name in env_vars_to_clear:
        if var_name in os.environ:
            original_env_vars[var_name] = os.environ[var_name]
            del os.environ[var_name]
    
    yield  # Executa o teste

    # Restaura as variáveis de ambiente originais
    get_settings.cache_clear() # Limpa novamente para o próximo teste
    for var_name, value in original_env_vars.items():
        os.environ[var_name] = value
    # Garante que as variáveis que não existiam originalmente sejam removidas
    for var_name in env_vars_to_clear:
        if var_name not in original_env_vars and var_name in os.environ:
            del os.environ[var_name]


def test_default_settings_load_correctly():
    """Verifica se as configurações padrão são carregadas corretamente."""
    settings = get_settings()
    assert settings.BACKUP_PATH == Path.home().resolve() / ".fotix_backups"
    assert settings.LOG_LEVEL == "INFO"
    assert settings.LOG_FORMAT == "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
    assert settings.LOG_FILE_PATH is None
    assert settings.model_config["env_prefix"] == "FOTIX_"

@mock.patch.dict(os.environ, {
    "FOTIX_BACKUP_PATH": "/tmp/custom_backup",
    "FOTIX_LOG_LEVEL": "DEBUG",
    "FOTIX_LOG_FORMAT": "custom_format",
    "FOTIX_LOG_FILE_PATH": "/tmp/fotix_test.log"
})
def test_settings_load_from_environment_variables():
    """Verifica se as configurações são carregadas corretamente das variáveis de ambiente."""
    settings = get_settings()
    assert settings.BACKUP_PATH == Path("/tmp/custom_backup").resolve()
    assert settings.LOG_LEVEL == "DEBUG"
    assert settings.LOG_FORMAT == "custom_format"
    assert settings.LOG_FILE_PATH == Path("/tmp/fotix_test.log").resolve()

def test_log_level_validation_case_insensitive():
    """Verifica se LOG_LEVEL aceita minúsculas e converte para maiúsculas."""
    with mock.patch.dict(os.environ, {"FOTIX_LOG_LEVEL": "warning"}):
        settings = get_settings()
        assert settings.LOG_LEVEL == "WARNING"

@pytest.mark.parametrize("invalid_level", ["INVALID", "DEBU", "information"])
def test_log_level_validation_invalid_value(invalid_level: str):
    """Verifica se LOG_LEVEL levanta erro para valores inválidos."""
    with mock.patch.dict(os.environ, {"FOTIX_LOG_LEVEL": invalid_level}):
        with pytest.raises(ValidationError) as excinfo:
            get_settings()
        assert "Nível de log inválido" in str(excinfo.value)
        assert f"'{invalid_level.upper()}'" in str(excinfo.value) or f"'{invalid_level}'" in str(excinfo.value)

def test_backup_path_resolves_correctly():
    """Verifica se BACKUP_PATH é resolvido para um caminho absoluto."""
    # Usando .. para forçar resolução
    test_path_str = "./some_relative_path/../another_path"
    expected_path = Path(test_path_str).resolve()
    with mock.patch.dict(os.environ, {"FOTIX_BACKUP_PATH": test_path_str}):
        settings = get_settings()
        assert settings.BACKUP_PATH == expected_path
        assert settings.BACKUP_PATH.is_absolute()

def test_log_file_path_resolves_correctly_if_set():
    """Verifica se LOG_FILE_PATH é resolvido para um caminho absoluto se fornecido."""
    test_path_str = "relative_log_dir/fotix.log"
    expected_path = Path(test_path_str).resolve()
    with mock.patch.dict(os.environ, {"FOTIX_LOG_FILE_PATH": test_path_str}):
        settings = get_settings()
        assert settings.LOG_FILE_PATH == expected_path
        assert settings.LOG_FILE_PATH.is_absolute() # O validador de Path da Pydantic deve fazer isso

def test_settings_load_from_dotenv_file(tmp_path: Path):
    """Verifica se as configurações são carregadas de um arquivo .env."""
    env_content = """
FOTIX_BACKUP_PATH="/test_dotenv/backup_dotenv"
FOTIX_LOG_LEVEL=CRITICAL
# Comentário no .env
FOTIX_LOG_FILE_PATH="logs/fotix_dotenv.log"
"""
    dotenv_file = tmp_path / ".env"
    dotenv_file.write_text(env_content, encoding="utf-8")

    # Pydantic procura o .env no diretório de trabalho atual por padrão
    # ou no caminho especificado em SettingsConfigDict.
    # Para o teste, podemos mockar o diretório de trabalho ou garantir que o .env está onde Pydantic espera.
    # Alternativamente, podemos forçar o AppSettings a usar este arquivo específico.
    # A maneira mais fácil é garantir que DOTENV_PATH (se usado por Pydantic) ou o cwd()
    # permita que o arquivo seja encontrado.
    # Para este teste, vamos instanciar AppSettings diretamente, especificando o _env_file.
    
    # Limpar cache para forçar re-leitura
    get_settings.cache_clear()
    
    # Mudar o diretório de trabalho para tmp_path onde o .env está
    original_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        settings = get_settings() # get_settings() usa AppSettings() que lerá o .env do cwd
        
        assert settings.BACKUP_PATH == Path("/test_dotenv/backup_dotenv").resolve()
        assert settings.LOG_LEVEL == "CRITICAL"
        assert settings.LOG_FILE_PATH == (tmp_path / "logs/fotix_dotenv.log").resolve()

        # Verifica se o diretório para o log foi criado (não é responsabilidade do config, mas testamos a resolução)
        # O Pydantic v2 com Path não cria automaticamente, apenas resolve.
        # O nosso validador também não cria.
        # A criação do diretório LOG_FILE_PATH.parent é responsabilidade do módulo de logging.

    finally:
        os.chdir(original_cwd) # Restaura o diretório de trabalho original
        # Limpa o .env criado para não interferir em outros testes ou execuções.
        if dotenv_file.exists():
            dotenv_file.unlink()
        # Limpar o cache novamente para o próximo teste que pode não querer este .env
        get_settings.cache_clear()


def test_get_settings_is_cached():
    """Verifica se get_settings() retorna instâncias cacheadas."""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2

    # Modificando uma variável de ambiente para ver se uma nova instância é criada (não deveria, por causa do cache)
    with mock.patch.dict(os.environ, {"FOTIX_LOG_LEVEL": "ERROR"}):
        settings3 = get_settings()
        assert settings3 is settings1 # Ainda deve ser a instância cacheada
        assert settings3.LOG_LEVEL == "INFO" # O valor original cacheado

    # Limpando o cache e obtendo novamente
    get_settings.cache_clear()
    with mock.patch.dict(os.environ, {"FOTIX_LOG_LEVEL": "CRITICAL"}):
        settings4 = get_settings()
        assert settings4 is not settings1
        assert settings4.LOG_LEVEL == "CRITICAL"


def test_all_valid_log_levels_are_accepted():
    """Testa se todos os níveis de log definidos em VALID_LOG_LEVELS são aceitos."""
    for level in VALID_LOG_LEVELS:
        get_settings.cache_clear() # Garante que estamos testando a validação
        with mock.patch.dict(os.environ, {"FOTIX_LOG_LEVEL": level}):
            settings = get_settings()
            assert settings.LOG_LEVEL == level
        get_settings.cache_clear()
        with mock.patch.dict(os.environ, {"FOTIX_LOG_LEVEL": level.lower()}):
            settings = get_settings()
            assert settings.LOG_LEVEL == level # Deve ser convertido para maiúsculo

def test_extra_fields_in_env_are_ignored():
    """Verifica se campos extras no ambiente/arquivo .env são ignorados (extra='ignore')."""
    with mock.patch.dict(os.environ, {
        "FOTIX_LOG_LEVEL": "INFO",
        "FOTIX_NON_EXISTENT_CONFIG": "some_value" # Este campo não existe em AppSettings
    }):
        try:
            settings = get_settings()
            assert settings.LOG_LEVEL == "INFO"
            assert not hasattr(settings, "NON_EXISTENT_CONFIG")
        except ValidationError:
            pytest.fail("ValidationError foi levantada inesperadamente com extra='ignore'") 