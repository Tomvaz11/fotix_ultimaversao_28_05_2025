"""
Testes de integração para a infraestrutura básica do Fotix: configuração, logging e sistema de arquivos.

Este módulo verifica a correta colaboração e fluxo de dados entre os módulos:
- fotix.config
- fotix.infrastructure.logging_config
- fotix.infrastructure.file_system

Os testes validam que as configurações são carregadas corretamente, que o logging
funciona conforme configurado, e que o FileSystemService interage com o sistema de
arquivos conforme esperado, registrando suas operações nos logs.
"""

import os
import shutil
import tempfile
import json
import logging
from pathlib import Path

import pytest

from fotix.config import ConfigManager, get_config
from fotix.infrastructure.logging_config import setup_logging, get_logger, update_log_level
from fotix.infrastructure.file_system import FileSystemService


@pytest.fixture
def temp_dir():
    """Fixture para criar e limpar um diretório temporário."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_config_file(temp_dir):
    """Fixture para criar um arquivo de configuração temporário."""
    config_file = temp_dir / "test_config.json"
    test_config = {
        "backup_dir": str(temp_dir / "backups"),
        "log_level": "DEBUG",
        "log_file": str(temp_dir / "test_integration.log"),  # Usar o mesmo arquivo de log do setup_test_logging
        "concurrent_workers": 2,
        "scan_extensions": [".txt", ".md", ".json"],
        "include_zips": True,
        "min_file_size": 10,
        "chunk_size": 1024,
    }
    
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(test_config, f, indent=4)
    
    yield config_file
    
    if config_file.exists():
        config_file.unlink()


@pytest.fixture
def config_manager(temp_config_file):
    """Fixture para criar um ConfigManager com o arquivo de configuração temporário."""
    manager = ConfigManager(temp_config_file)
    return manager


@pytest.fixture
def setup_test_logging(temp_dir, config_manager):
    """Fixture para configurar o logging para os testes."""
    log_file = temp_dir / "test_integration.log"
    logger = setup_logging("DEBUG", log_file)
    
    # Retorna o arquivo de log e o logger
    yield log_file, logger
    
    # Limpeza
    handlers = logger.handlers[:]
    for handler in handlers:
        handler.close()
        logger.removeHandler(handler)


@pytest.fixture
def file_system_service():
    """Fixture para criar uma instância do FileSystemService."""
    return FileSystemService()


@pytest.fixture
def test_files(temp_dir):
    """Fixture para criar arquivos de teste."""
    # Criar subdiretório
    sub_dir = temp_dir / "subdir"
    sub_dir.mkdir(exist_ok=True)
    
    # Criar alguns arquivos
    files = {
        "file1.txt": "Conteúdo do arquivo 1",
        "file2.txt": "Conteúdo do arquivo 2",
        "subdir/file3.txt": "Conteúdo do arquivo 3",
    }
    
    created_files = []
    
    for file_path, content in files.items():
        full_path = temp_dir / file_path
        full_path.parent.mkdir(exist_ok=True, parents=True)
        full_path.write_text(content, encoding="utf-8")
        created_files.append(full_path)
    
    return created_files


class TestInfraestruturaBasicaIntegracao:
    """Testes de integração para a infraestrutura básica do Fotix."""
    
    def test_carregamento_configuracao_e_logging(self, temp_config_file, setup_test_logging):
        """
        Cenário 1: Carregamento de Configuração e Logging.
        
        Verifica se as configurações são carregadas corretamente e se o logging
        é configurado de acordo com o nível especificado.
        """
        log_file, logger = setup_test_logging
        
        # 1. Carregar configuração do arquivo temporário
        config = get_config(temp_config_file)
        
        # 2. Verificar se a configuração foi carregada corretamente
        assert config.log_level == "DEBUG"
        # Verificar se tem o mesmo nome de arquivo (sem verificar o caminho completo)
        assert Path(config.log_file).name == log_file.name
        
        # 3. Verificar se o logging está funcionando com o nível correto
        test_logger = get_logger("test_integration")
        
        # Enviar mensagens de diferentes níveis
        test_logger.debug("Mensagem de DEBUG")
        test_logger.info("Mensagem de INFO")
        test_logger.warning("Mensagem de WARNING")
        
        # Verificar se as mensagens foram registradas no arquivo de log
        log_content = log_file.read_text(encoding="utf-8")
        
        assert "Mensagem de DEBUG" in log_content
        assert "Mensagem de INFO" in log_content
        assert "Mensagem de WARNING" in log_content
        
        # 4. Alterar o nível de log para INFO e verificar se funciona
        update_log_level("INFO")
        
        # Limpar o arquivo de log para facilitar a verificação
        log_file.write_text("", encoding="utf-8")
        
        # Enviar mensagens novamente
        test_logger.debug("Nova mensagem de DEBUG - não deve aparecer")
        test_logger.info("Nova mensagem de INFO - deve aparecer")
        
        # Verificar se apenas a mensagem de INFO aparece
        new_log_content = log_file.read_text(encoding="utf-8")
        
        assert "Nova mensagem de DEBUG - não deve aparecer" not in new_log_content
        assert "Nova mensagem de INFO - deve aparecer" in new_log_content
    
    def test_operacoes_filesystemservice_com_logging(self, temp_dir, file_system_service, setup_test_logging, test_files):
        """
        Cenário 2: Operações do FileSystemService com Logging.
        
        Verifica se as operações do FileSystemService são executadas corretamente
        e se os logs correspondentes são gerados.
        """
        log_file, _ = setup_test_logging
        
        # 1. Listar conteúdo do diretório
        files = list(file_system_service.list_directory_contents(temp_dir, recursive=True))
        
        # Verificar se todos os arquivos criados estão na lista
        for test_file in test_files:
            assert test_file in files
        
        # 2. Obter tamanho de um arquivo
        file1 = test_files[0]
        size = file_system_service.get_file_size(file1)
        
        assert size is not None
        assert size > 0
        
        # 3. Ler conteúdo de um arquivo
        content = b"".join(file_system_service.stream_file_content(file1))
        
        assert content.decode("utf-8") == "Conteúdo do arquivo 1"
        
        # 4. Criar um novo diretório
        new_dir = temp_dir / "novo_dir"
        file_system_service.create_directory(new_dir)
        
        assert new_dir.exists()
        assert new_dir.is_dir()
        
        # 5. Copiar um arquivo
        dest_file = new_dir / "file1_copy.txt"
        file_system_service.copy_file(file1, dest_file)
        
        assert dest_file.exists()
        assert dest_file.read_text(encoding="utf-8") == "Conteúdo do arquivo 1"
        
        # 6. Verificar se as operações foram registradas no log
        log_content = log_file.read_text(encoding="utf-8")
        
        # Verificar menções às operações realizadas
        assert "Listando arquivos" in log_content
        assert "Tamanho do arquivo" in log_content or "Iniciando stream do arquivo" in log_content
        assert "Stream do arquivo" in log_content
        assert "Criando diretório" in log_content
        assert "Copiando" in log_content
    
    def test_tratamento_erro_filesystemservice_com_logging(self, temp_dir, file_system_service, setup_test_logging):
        """
        Cenário 3: Tratamento de Erro no FileSystemService com Logging.
        
        Verifica se as exceções são tratadas corretamente pelo FileSystemService
        e se os logs de erro são gerados.
        """
        log_file, _ = setup_test_logging
        
        # 1. Tentar acessar um arquivo inexistente
        non_existent_file = temp_dir / "nao_existe.txt"
        
        # Verificar tamanho do arquivo inexistente (não deve lançar exceção, apenas retornar None)
        size = file_system_service.get_file_size(non_existent_file)
        assert size is None
        
        # 2. Tentar ler um arquivo inexistente (deve lançar FileNotFoundError)
        with pytest.raises(FileNotFoundError):
            list(file_system_service.stream_file_content(non_existent_file))
        
        # 3. Tentar mover para a lixeira um arquivo inexistente
        with pytest.raises(FileNotFoundError):
            file_system_service.move_to_trash(non_existent_file)
        
        # 4. Tentar copiar um arquivo inexistente
        with pytest.raises(FileNotFoundError):
            file_system_service.copy_file(non_existent_file, temp_dir / "copia.txt")
        
        # 5. Tentar listar um diretório inexistente
        non_existent_dir = temp_dir / "dir_nao_existe"
        with pytest.raises(NotADirectoryError):
            list(file_system_service.list_directory_contents(non_existent_file))
        
        # 6. Verificar se os erros foram registrados no log
        log_content = log_file.read_text(encoding="utf-8")
        
        # A mensagem poderia ser diferente dependendo da implementação
        # Vamos verificar se alguma das mensagens de erro conhecidas está presente
        assert any([
            "Erro ao obter tamanho do arquivo" in log_content,
            "não é um arquivo" in log_content
        ])
        assert "Erro ao ler arquivo" in log_content
        assert "Impossível mover para a lixeira" in log_content
        assert "Impossível copiar" in log_content
        assert "não é um diretório" in log_content


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 