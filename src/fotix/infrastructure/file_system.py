"""
Implementação do serviço de sistema de arquivos.
"""
import logging
import os
import shutil
from pathlib import Path
from typing import Any, Iterable

import send2trash # type: ignore

from fotix.infrastructure.interfaces import IFileSystemService

logger = logging.getLogger(__name__)


class FileSystemService(IFileSystemService):
    """
    Implementação concreta de IFileSystemService usando pathlib, shutil, send2trash.
    """

    def get_file_size(self, path: Path) -> int | None:
        """Retorna o tamanho do arquivo em bytes ou None se não existir/acessível."""
        try:
            if path.is_file():
                return path.stat().st_size
            return None
        except FileNotFoundError:
            logger.debug(f"Arquivo não encontrado ao obter tamanho: {path}")
            return None
        except PermissionError:
            logger.warning(f"Permissão negada ao obter tamanho do arquivo: {path}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao obter tamanho do arquivo {path}: {e}", exc_info=True)
            return None

    def stream_file_content(
        self, path: Path, chunk_size: int = 65536
    ) -> Iterable[bytes]:
        """
        Retorna um iterador/gerador para ler o conteúdo do arquivo em blocos.
        Lança exceções apropriadas (ex: FileNotFoundError, PermissionError).
        """
        if not path.is_file():
            logger.error(f"Tentativa de stream de um não-arquivo ou arquivo inexistente: {path}")
            raise FileNotFoundError(f"O caminho especificado não é um arquivo: {path}")
        try:
            with open(path, "rb") as f:
                while chunk := f.read(chunk_size):
                    yield chunk
        except FileNotFoundError:
            logger.error(f"Arquivo não encontrado durante o streaming: {path}")
            raise
        except PermissionError:
            logger.error(f"Permissão negada durante o streaming do arquivo: {path}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado durante o streaming do arquivo {path}: {e}", exc_info=True)
            raise

    def list_directory_contents(
        self,
        path: Path,
        recursive: bool = True,
        file_extensions: list[str] | None = None,
    ) -> Iterable[Path]:
        """
        Retorna um iterador para os caminhos de arquivos dentro de um diretório.
        Filtra por extensões se fornecido (ex: ['.jpg', '.png']).
        """
        if not path.is_dir():
            logger.warning(f"Tentativa de listar conteúdo de um não-diretório: {path}")
            return iter([])  # Retorna um iterador vazio

        try:
            pattern = "*"
            iterator = path.rglob(pattern) if recursive else path.glob(pattern)

            for item_path in iterator:
                if item_path.is_file():
                    if file_extensions:
                        # Normaliza as extensões para minúsculas e com ponto
                        normalized_extensions = [
                            ext.lower() if ext.startswith(".") else f".{ext.lower()}"
                            for ext in file_extensions
                        ]
                        if item_path.suffix.lower() in normalized_extensions:
                            yield item_path
                    else:
                        yield item_path
        except PermissionError:
            logger.warning(f"Permissão negada ao listar o diretório: {path}")
            # Retorna um iterador vazio em caso de erro de permissão para não interromper fluxos
            return iter([])
        except Exception as e:
            logger.error(f"Erro inesperado ao listar o diretório {path}: {e}", exc_info=True)
            return iter([])


    def move_to_trash(self, path: Path) -> None:
        """
        Move o arquivo/diretório para a lixeira do sistema.
        Lança exceção FileNotFoundError se o caminho não existir,
        ou outras exceções em caso de falha na operação.
        """
        if not self.path_exists(path):
            logger.error(f"Tentativa de mover para lixeira um caminho inexistente: {path}")
            raise FileNotFoundError(f"Caminho não encontrado: {path}")
        try:
            send2trash.send2trash(str(path))
            logger.info(f"Movido para a lixeira: {path}")
        except Exception as e: # send2trash pode levantar várias exceções não específicas
            logger.error(f"Falha ao mover para a lixeira {path}: {e}", exc_info=True)
            raise # Re-levanta a exceção para o chamador tratar

    def copy_file(self, source: Path, destination: Path) -> None:
        """Copia um arquivo. Preserva metadados. Lança exceções em caso de erro."""
        if not source.is_file():
            logger.error(f"Tentativa de copiar um não-arquivo ou arquivo de origem inexistente: {source}")
            raise FileNotFoundError(f"Arquivo de origem não encontrado ou não é um arquivo: {source}")
        try:
            # Garante que o diretório de destino exista
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination) # copy2 preserva metadados
            logger.info(f"Arquivo copiado de {source} para {destination}")
        except Exception as e:
            logger.error(f"Falha ao copiar arquivo de {source} para {destination}: {e}", exc_info=True)
            raise

    def create_directory(self, path: Path, exist_ok: bool = True) -> None:
        """Cria um diretório."""
        try:
            path.mkdir(parents=True, exist_ok=exist_ok)
            logger.info(f"Diretório criado (ou já existente com exist_ok=True): {path}")
        except FileExistsError:
            logger.warning(f"Tentativa de criar diretório que já existe (exist_ok=False): {path}")
            raise
        except Exception as e:
            logger.error(f"Falha ao criar diretório {path}: {e}", exc_info=True)
            raise

    def path_exists(self, path: Path) -> bool:
        """Verifica se um caminho existe."""
        try:
            return path.exists()
        except Exception as e: # Path.exists() pode raramente falhar em casos extremos (ex: links quebrados longos)
            logger.warning(f"Erro ao verificar existência do caminho {path}: {e}", exc_info=True)
            return False

    def get_creation_time(self, path: Path) -> float | None:
        """Retorna o timestamp de criação (Unix epoch) ou None."""
        try:
            if self.path_exists(path):
                # Em Windows, st_ctime é o tempo de criação. Em Unix, pode ser tempo de mudança de metadados.
                # os.path.getctime() é mais portável para "tempo de criação" em Windows.
                return path.stat().st_ctime
            return None
        except FileNotFoundError:
            logger.debug(f"Arquivo não encontrado ao obter tempo de criação: {path}")
            return None
        except PermissionError:
            logger.warning(f"Permissão negada ao obter tempo de criação para: {path}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao obter tempo de criação para {path}: {e}", exc_info=True)
            return None


    def get_modification_time(self, path: Path) -> float | None:
        """Retorna o timestamp de modificação (Unix epoch) ou None."""
        try:
            if self.path_exists(path):
                return path.stat().st_mtime
            return None
        except FileNotFoundError:
            logger.debug(f"Arquivo não encontrado ao obter tempo de modificação: {path}")
            return None
        except PermissionError:
            logger.warning(f"Permissão negada ao obter tempo de modificação para: {path}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao obter tempo de modificação para {path}: {e}", exc_info=True)
            return None

    def delete_file(self, path: Path) -> None:
        """Exclui um arquivo permanentemente."""
        if not path.is_file():
            logger.error(f"Tentativa de deletar um não-arquivo ou arquivo inexistente: {path}")
            raise FileNotFoundError(f"Caminho não é um arquivo ou não encontrado: {path}")
        try:
            path.unlink()
            logger.info(f"Arquivo deletado permanentemente: {path}")
        except Exception as e:
            logger.error(f"Falha ao deletar arquivo permanentemente {path}: {e}", exc_info=True)
            raise

    def delete_directory(self, path: Path, recursive: bool = False) -> None:
        """Exclui um diretório permanentemente."""
        if not path.is_dir():
            logger.error(f"Tentativa de deletar um não-diretório ou diretório inexistente: {path}")
            raise NotADirectoryError(f"Caminho não é um diretório ou não encontrado: {path}")
        try:
            if recursive:
                shutil.rmtree(path)
                logger.info(f"Diretório deletado recursivamente: {path}")
            else:
                path.rmdir() # Falhará se o diretório não estiver vazio
                logger.info(f"Diretório vazio deletado: {path}")
        except Exception as e:
            logger.error(f"Falha ao deletar diretório {path} (recursivo={recursive}): {e}", exc_info=True)
            raise

    def get_file_info(self, path: Path) -> dict[str, Any] | None:
        """Retorna um dicionário com informações do arquivo/diretório ou None."""
        if not self.path_exists(path):
            logger.debug(f"Caminho não encontrado ao obter informações: {path}")
            return None
        try:
            stat_info = path.stat()
            is_dir = path.is_dir()
            return {
                "name": path.name,
                "path": str(path.resolve()), # Usar resolve() para obter caminho absoluto canônico
                "size": stat_info.st_size if not is_dir else None, # Tamanho só para arquivos
                "creation_time": stat_info.st_ctime,
                "modification_time": stat_info.st_mtime,
                "is_dir": is_dir,
            }
        except Exception as e:
            logger.error(f"Erro inesperado ao obter informações de {path}: {e}", exc_info=True)
            return None 