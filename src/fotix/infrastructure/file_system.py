"""
Implementação do serviço de sistema de arquivos do Fotix.

Este módulo implementa a interface IFileSystemService para abstrair operações
no sistema de arquivos, como leitura, escrita, movimentação para lixeira e listagem de diretórios.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

from send2trash import send2trash

from fotix.config import get as get_config
from fotix.infrastructure.logging_config import get_logger
from fotix.utils.helpers import filter_by_extensions, normalize_path

# Obtém um logger configurado para este módulo
logger = get_logger(__name__)


class FileSystemService:
    """
    Implementação da interface IFileSystemService.

    Esta classe fornece métodos para operações comuns no sistema de arquivos,
    como leitura, escrita, movimentação para lixeira e listagem de diretórios.
    """

    def get_file_size(self, path: Path) -> Optional[int]:
        """
        Retorna o tamanho do arquivo em bytes.

        Args:
            path: Caminho do arquivo.

        Returns:
            Tamanho do arquivo em bytes ou None se o arquivo não existir ou não for acessível.

        Raises:
            PermissionError: Se o arquivo existir mas não for acessível por permissões.
        """
        path = normalize_path(path)

        try:
            if not path.is_file():
                logger.debug(f"Tentativa de obter tamanho de um caminho que não é um arquivo: {path}")
                return None

            size = path.stat().st_size
            logger.debug(f"Tamanho do arquivo {path}: {size} bytes")
            return size
        except FileNotFoundError:
            logger.debug(f"Arquivo não encontrado ao obter tamanho: {path}")
            return None
        except PermissionError as e:
            logger.error(f"Erro de permissão ao obter tamanho do arquivo {path}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro ao obter tamanho do arquivo {path}: {str(e)}")
            return None

    def stream_file_content(self, path: Path, chunk_size: int = None) -> Iterable[bytes]:
        """
        Retorna um iterador/gerador para ler o conteúdo do arquivo em blocos.

        Args:
            path: Caminho do arquivo.
            chunk_size: Tamanho do bloco em bytes para leitura. Se None, usa o valor da configuração.

        Returns:
            Um iterador/gerador que produz blocos de bytes do arquivo.

        Raises:
            FileNotFoundError: Se o arquivo não existir.
            PermissionError: Se o arquivo não for acessível por permissões.
            IsADirectoryError: Se o caminho apontar para um diretório.
        """
        path = normalize_path(path)

        # Se chunk_size não for fornecido, usa o valor da configuração
        if chunk_size is None:
            chunk_size = get_config("chunk_size", 65536)

        logger.debug(f"Iniciando streaming do arquivo {path} com chunk_size={chunk_size}")

        # Verifica se o caminho é um diretório antes de tentar abri-lo
        if path.is_dir():
            logger.error(f"Tentativa de fazer streaming de um diretório: {path}")
            raise IsADirectoryError(f"Caminho é um diretório: {path}")

        try:
            with open(path, 'rb') as file:
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk

            logger.debug(f"Streaming do arquivo {path} concluído")
        except FileNotFoundError:
            logger.error(f"Arquivo não encontrado ao fazer streaming: {path}")
            raise
        except PermissionError as e:
            logger.error(f"Erro de permissão ao fazer streaming do arquivo {path}: {str(e)}")
            raise
        except IsADirectoryError:
            logger.error(f"Tentativa de fazer streaming de um diretório: {path}")
            raise
        except Exception as e:
            logger.error(f"Erro ao fazer streaming do arquivo {path}: {str(e)}")
            raise

    def list_directory_contents(
        self,
        path: Path,
        recursive: bool = True,
        file_extensions: Optional[List[str]] = None
    ) -> Iterable[Path]:
        """
        Retorna um iterador/gerador para os caminhos de arquivos dentro de um diretório.

        Args:
            path: Caminho do diretório.
            recursive: Se True, lista arquivos em subdiretórios recursivamente.
            file_extensions: Lista opcional de extensões de arquivo para filtrar (ex: ['.jpg', '.png']).
                            Se None, todos os arquivos são incluídos.

        Returns:
            Um iterador/gerador que produz objetos Path para cada arquivo encontrado.

        Raises:
            FileNotFoundError: Se o diretório não existir.
            NotADirectoryError: Se o caminho não apontar para um diretório.
            PermissionError: Se o diretório não for acessível por permissões.
        """
        path = normalize_path(path)

        if not path.exists():
            logger.error(f"Diretório não encontrado: {path}")
            raise FileNotFoundError(f"Diretório não encontrado: {path}")

        if not path.is_dir():
            logger.error(f"Caminho não é um diretório: {path}")
            raise NotADirectoryError(f"Caminho não é um diretório: {path}")

        logger.debug(f"Listando conteúdo do diretório {path} (recursive={recursive}, extensions={file_extensions})")

        try:
            if recursive:
                for item in path.rglob('*'):
                    if item.is_file() and filter_by_extensions(item, file_extensions):
                        yield item
            else:
                for item in path.iterdir():
                    if item.is_file() and filter_by_extensions(item, file_extensions):
                        yield item

            logger.debug(f"Listagem do diretório {path} concluída")
        except PermissionError as e:
            logger.error(f"Erro de permissão ao listar diretório {path}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro ao listar diretório {path}: {str(e)}")
            raise

    def move_to_trash(self, path: Path) -> None:
        """
        Move o arquivo ou diretório para a lixeira do sistema.

        Args:
            path: Caminho do arquivo ou diretório a ser movido para a lixeira.

        Raises:
            FileNotFoundError: Se o arquivo ou diretório não existir.
            PermissionError: Se o arquivo ou diretório não puder ser movido por permissões.
        """
        path = normalize_path(path)

        if not path.exists():
            logger.error(f"Arquivo/diretório não encontrado para mover para a lixeira: {path}")
            raise FileNotFoundError(f"Arquivo/diretório não encontrado: {path}")

        # Verifica se a movimentação para a lixeira está habilitada na configuração
        trash_enabled = get_config("trash_enabled", True)

        try:
            if trash_enabled:
                logger.info(f"Movendo para a lixeira: {path}")
                send2trash(str(path))
            else:
                logger.warning(f"Removendo permanentemente (trash_enabled=False): {path}")
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
        except PermissionError as e:
            logger.error(f"Erro de permissão ao mover para a lixeira: {path} - {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro ao mover para a lixeira: {path} - {str(e)}")
            raise

    def copy_file(self, source: Path, destination: Path) -> None:
        """
        Copia um arquivo de origem para destino.

        Args:
            source: Caminho do arquivo de origem.
            destination: Caminho do arquivo de destino.

        Raises:
            FileNotFoundError: Se o arquivo de origem não existir.
            IsADirectoryError: Se o caminho de origem apontar para um diretório.
            PermissionError: Se o arquivo não puder ser copiado por permissões.
        """
        source = normalize_path(source)
        destination = normalize_path(destination)

        if not source.exists():
            logger.error(f"Arquivo de origem não encontrado para cópia: {source}")
            raise FileNotFoundError(f"Arquivo de origem não encontrado: {source}")

        if source.is_dir():
            logger.error(f"Caminho de origem é um diretório, não um arquivo: {source}")
            raise IsADirectoryError(f"Caminho de origem é um diretório: {source}")

        # Garante que o diretório de destino exista
        destination.parent.mkdir(parents=True, exist_ok=True)

        try:
            logger.info(f"Copiando arquivo de {source} para {destination}")
            shutil.copy2(source, destination)  # copy2 preserva metadados
        except PermissionError as e:
            logger.error(f"Erro de permissão ao copiar arquivo: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro ao copiar arquivo: {str(e)}")
            raise

    def create_directory(self, path: Path, exist_ok: bool = True) -> None:
        """
        Cria um diretório no caminho especificado.

        Args:
            path: Caminho do diretório a ser criado.
            exist_ok: Se True, não levanta erro se o diretório já existir.

        Raises:
            FileExistsError: Se o diretório já existir e exist_ok=False.
            PermissionError: Se o diretório não puder ser criado por permissões.
        """
        path = normalize_path(path)

        try:
            logger.debug(f"Criando diretório: {path} (exist_ok={exist_ok})")
            path.mkdir(parents=True, exist_ok=exist_ok)
        except FileExistsError:
            logger.error(f"Diretório já existe e exist_ok=False: {path}")
            raise
        except PermissionError as e:
            logger.error(f"Erro de permissão ao criar diretório {path}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro ao criar diretório {path}: {str(e)}")
            raise

    def path_exists(self, path: Path) -> bool:
        """
        Verifica se um caminho existe.

        Args:
            path: Caminho a ser verificado.

        Returns:
            True se o caminho existir, False caso contrário.
        """
        path = normalize_path(path)
        exists = path.exists()
        logger.debug(f"Verificando existência do caminho {path}: {exists}")
        return exists

    def get_creation_time(self, path: Path) -> Optional[float]:
        """
        Retorna o timestamp de criação do arquivo ou diretório.

        Args:
            path: Caminho do arquivo ou diretório.

        Returns:
            Timestamp de criação como float (segundos desde a época) ou None se não disponível.

        Raises:
            FileNotFoundError: Se o arquivo ou diretório não existir.
            PermissionError: Se o arquivo ou diretório não for acessível por permissões.
        """
        path = normalize_path(path)

        if not path.exists():
            logger.error(f"Arquivo/diretório não encontrado ao obter data de criação: {path}")
            raise FileNotFoundError(f"Arquivo/diretório não encontrado: {path}")

        try:
            # Em sistemas Windows, st_ctime é a data de criação
            # Em sistemas Unix, st_birthtime seria a data de criação, mas nem sempre está disponível
            # st_ctime em Unix é a data da última alteração de metadados
            stat_result = path.stat()

            if os.name == 'nt':  # Windows
                creation_time = stat_result.st_ctime
            else:
                # Em sistemas Unix, tentamos obter st_birthtime se disponível
                try:
                    creation_time = stat_result.st_birthtime  # Disponível em alguns sistemas Unix
                except AttributeError:
                    # Fallback para st_ctime se st_birthtime não estiver disponível
                    creation_time = stat_result.st_ctime

            logger.debug(f"Data de criação de {path}: {datetime.fromtimestamp(creation_time)}")
            return creation_time
        except PermissionError as e:
            logger.error(f"Erro de permissão ao obter data de criação de {path}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro ao obter data de criação de {path}: {str(e)}")
            return None

    def get_modification_time(self, path: Path) -> Optional[float]:
        """
        Retorna o timestamp de modificação do arquivo ou diretório.

        Args:
            path: Caminho do arquivo ou diretório.

        Returns:
            Timestamp de modificação como float (segundos desde a época) ou None se não disponível.

        Raises:
            FileNotFoundError: Se o arquivo ou diretório não existir.
            PermissionError: Se o arquivo ou diretório não for acessível por permissões.
        """
        path = normalize_path(path)

        if not path.exists():
            logger.error(f"Arquivo/diretório não encontrado ao obter data de modificação: {path}")
            raise FileNotFoundError(f"Arquivo/diretório não encontrado: {path}")

        try:
            modification_time = path.stat().st_mtime
            logger.debug(f"Data de modificação de {path}: {datetime.fromtimestamp(modification_time)}")
            return modification_time
        except PermissionError as e:
            logger.error(f"Erro de permissão ao obter data de modificação de {path}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro ao obter data de modificação de {path}: {str(e)}")
            return None
