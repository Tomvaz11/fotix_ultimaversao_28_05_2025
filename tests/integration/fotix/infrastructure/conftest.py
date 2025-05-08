"""
Fixtures compartilhadas para testes de integração da infraestrutura do Fotix.
"""

import os
import json
import tempfile
import logging
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Cria um diretório temporário para testes."""
    with tempfile.TemporaryDirectory(prefix="fotix_test_") as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def temp_config_file(temp_dir):
    """Cria um arquivo de configuração temporário para testes."""
    config_file = temp_dir / "fotix_config.json"
    config_data = {
        "backup_dir": str(temp_dir / "backups"),
        "log_level": "DEBUG",
        "log_file": str(temp_dir / "logs" / "fotix.log"),
        "max_workers": 2,
        "chunk_size": 4096,
        "supported_extensions": [".jpg", ".png", ".txt"],
        "scan_inside_archives": True,
        "trash_enabled": True
    }

    # Cria o diretório de logs
    log_dir = temp_dir / "logs"
    log_dir.mkdir(exist_ok=True)

    # Escreve o arquivo de configuração
    with open(config_file, "w") as f:
        json.dump(config_data, f, indent=2)

    yield config_file, config_data


@pytest.fixture
def temp_log_file(temp_dir):
    """Cria um arquivo de log temporário para testes."""
    log_file = temp_dir / "logs" / "fotix.log"
    log_dir = log_file.parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # Cria o arquivo vazio
    with open(log_file, "w") as f:
        f.write("")

    yield log_file

    # Limpa o arquivo de log após o teste
    if log_file.exists():
        with open(log_file, "w") as f:
            f.write("")


@pytest.fixture
def reset_logging():
    """Reseta a configuração de logging após o teste."""
    yield

    # Remove todos os handlers do logger raiz
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Reseta o nível de log
    root_logger.setLevel(logging.WARNING)


@pytest.fixture
def test_files(temp_dir):
    """Cria arquivos de teste em um diretório temporário."""
    # Cria subdiretórios
    subdir1 = temp_dir / "subdir1"
    subdir2 = temp_dir / "subdir2"
    subdir1.mkdir()
    subdir2.mkdir()

    # Cria arquivos com diferentes extensões
    files = [
        temp_dir / "test1.txt",
        temp_dir / "test2.jpg",
        subdir1 / "test3.png",
        subdir1 / "test4.txt",
        subdir2 / "test5.pdf"
    ]

    # Escreve conteúdo nos arquivos
    for i, file_path in enumerate(files):
        with open(file_path, "w") as f:
            f.write(f"Conteúdo do arquivo {i+1}")

    return {
        "root": temp_dir,
        "subdirs": [subdir1, subdir2],
        "files": files
    }
