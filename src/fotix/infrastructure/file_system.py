"""
Módulo de serviço do sistema de arquivos para o Fotix.

Este módulo fornece uma implementação concreta de IFileSystemService
para abstrair operações no sistema de arquivos, como leitura, escrita,
movimentação para lixeira e listagem de diretórios.
"""

import os
import shutil
from pathlib import Path
from typing import Iterable, Optional, List, Generator

from send2trash import send2trash

from fotix.infrastructure.interfaces import IFileSystemService
from fotix.infrastructure.logging_config import get_logger

# Configuração do logger
logger = get_logger(__name__)


class FileSystemService(IFileSystemService):
    """
    Implementação concreta do serviço de sistema de arquivos.
    
    Utiliza pathlib, shutil, os e send2trash para realizar operações
    no sistema de arquivos de forma segura e abstraída.
    """
    
    def get_file_size(self, path: Path) -> Optional[int]:
        """
        Retorna o tamanho do arquivo em bytes.
        
        Args:
            path: Caminho do arquivo.
            
        Returns:
            O tamanho do arquivo em bytes ou None se o arquivo não existir ou não for acessível.
        """
        try:
            if not path.is_file():
                logger.debug(f"Caminho {path} não é um arquivo")
                return None
            
            size = path.stat().st_size
            logger.debug(f"Tamanho do arquivo {path}: {size} bytes")
            return size
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.error(f"Erro ao obter tamanho do arquivo {path}: {e}")
            return None
    
    def stream_file_content(self, path: Path, chunk_size: int = 65536) -> Iterable[bytes]:
        """
        Retorna um iterador/gerador para ler o conteúdo do arquivo em blocos.
        
        Args:
            path: Caminho do arquivo.
            chunk_size: Tamanho de cada bloco em bytes.
            
        Returns:
            Um iterador que produz blocos de bytes do arquivo.
            
        Raises:
            FileNotFoundError: Se o arquivo não for encontrado.
            PermissionError: Se não houver permissão para acessar o arquivo.
            OSError: Para outros erros de IO.
        """
        logger.debug(f"Iniciando stream do arquivo {path} com chunk_size={chunk_size}")
        
        try:
            with open(path, 'rb') as file:
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
            
            logger.debug(f"Stream do arquivo {path} concluído")
        except (FileNotFoundError, PermissionError) as e:
            logger.error(f"Erro ao ler arquivo {path}: {e}")
            raise  # Re-levanta a exceção para ser tratada pela camada superior
        except OSError as e:
            logger.error(f"Erro de IO ao ler arquivo {path}: {e}")
            raise
    
    def list_directory_contents(
        self, path: Path, recursive: bool = True, file_extensions: Optional[List[str]] = None
    ) -> Iterable[Path]:
        """
        Retorna um iterador para os caminhos de arquivos dentro de um diretório.
        
        Args:
            path: Caminho do diretório.
            recursive: Se True, inclui arquivos em subdiretórios.
            file_extensions: Lista de extensões para filtrar os arquivos (ex: ['.jpg', '.png']).
                            Se None, todos os arquivos são incluídos.
            
        Returns:
            Um iterador que produz caminhos de arquivos (Path).
            
        Raises:
            FileNotFoundError: Se o diretório não for encontrado.
            PermissionError: Se não houver permissão para acessar o diretório.
            NotADirectoryError: Se o caminho não apontar para um diretório.
        """
        if not path.is_dir():
            logger.error(f"Caminho {path} não é um diretório")
            raise NotADirectoryError(f"O caminho {path} não é um diretório")
        
        extensions_info = "todas" if file_extensions is None else ", ".join(file_extensions)
        recursive_info = "recursivamente" if recursive else "apenas no nível raiz"
        logger.info(f"Listando arquivos em {path} {recursive_info} com extensões: {extensions_info}")
        
        try:
            if recursive:
                return self._walk_directory(path, file_extensions)
            else:
                return self._list_files_in_directory(path, file_extensions)
        except (FileNotFoundError, PermissionError) as e:
            logger.error(f"Erro ao listar conteúdo do diretório {path}: {e}")
            raise
    
    def _walk_directory(self, path: Path, file_extensions: Optional[List[str]] = None) -> Generator[Path, None, None]:
        """
        Percorre recursivamente um diretório, filtrando por extensões.
        
        Args:
            path: Caminho do diretório.
            file_extensions: Lista de extensões para filtrar os arquivos.
            
        Returns:
            Um gerador que produz caminhos de arquivos.
        """
        for item in path.rglob("*"):
            if item.is_file():
                if file_extensions is None or item.suffix.lower() in file_extensions:
                    yield item
    
    def _list_files_in_directory(self, path: Path, file_extensions: Optional[List[str]] = None) -> Generator[Path, None, None]:
        """
        Lista os arquivos em um diretório (sem recursão), filtrando por extensões.
        
        Args:
            path: Caminho do diretório.
            file_extensions: Lista de extensões para filtrar os arquivos.
            
        Returns:
            Um gerador que produz caminhos de arquivos.
        """
        for item in path.iterdir():
            if item.is_file():
                if file_extensions is None or item.suffix.lower() in file_extensions:
                    yield item
    
    def move_to_trash(self, path: Path) -> None:
        """
        Move o arquivo ou diretório para a lixeira do sistema.
        
        Args:
            path: Caminho do arquivo ou diretório.
            
        Raises:
            FileNotFoundError: Se o arquivo/diretório não for encontrado.
            PermissionError: Se não houver permissão para mover o arquivo/diretório.
            OSError: Para outros erros de IO.
        """
        if not path.exists():
            logger.error(f"Impossível mover para a lixeira: {path} não existe")
            raise FileNotFoundError(f"O caminho {path} não existe")
        
        try:
            logger.info(f"Movendo {path} para a lixeira")
            send2trash(str(path))
            logger.info(f"{path} movido para a lixeira com sucesso")
        except PermissionError as e:
            logger.error(f"Sem permissão para mover {path} para a lixeira: {e}")
            raise
        except OSError as e:
            logger.error(f"Erro ao mover {path} para a lixeira: {e}")
            raise
    
    def copy_file(self, source: Path, destination: Path) -> None:
        """
        Copia um arquivo de origem para destino.
        
        Args:
            source: Caminho do arquivo de origem.
            destination: Caminho do arquivo de destino.
            
        Raises:
            FileNotFoundError: Se o arquivo de origem não for encontrado.
            PermissionError: Se não houver permissão para copiar o arquivo.
            OSError: Para outros erros de IO.
        """
        if not source.exists():
            logger.error(f"Impossível copiar: arquivo de origem {source} não existe")
            raise FileNotFoundError(f"O arquivo de origem {source} não existe")
        
        if not source.is_file():
            logger.error(f"Impossível copiar: {source} não é um arquivo")
            raise IsADirectoryError(f"O caminho de origem {source} não é um arquivo")
        
        # Garantir que o diretório de destino exista
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            logger.info(f"Copiando {source} para {destination}")
            shutil.copy2(source, destination)  # copy2 preserva metadados
            logger.info(f"Arquivo copiado com sucesso de {source} para {destination}")
        except PermissionError as e:
            logger.error(f"Sem permissão para copiar {source} para {destination}: {e}")
            raise
        except OSError as e:
            logger.error(f"Erro ao copiar {source} para {destination}: {e}")
            raise
    
    def create_directory(self, path: Path, exist_ok: bool = True) -> None:
        """
        Cria um diretório.
        
        Args:
            path: Caminho do diretório a ser criado.
            exist_ok: Se True, não levanta exceção se o diretório já existir.
            
        Raises:
            FileExistsError: Se o diretório já existir e exist_ok for False.
            PermissionError: Se não houver permissão para criar o diretório.
            OSError: Para outros erros de IO.
        """
        try:
            logger.info(f"Criando diretório {path}")
            path.mkdir(parents=True, exist_ok=exist_ok)
            logger.info(f"Diretório {path} criado com sucesso")
        except FileExistsError:
            logger.error(f"Diretório {path} já existe e exist_ok=False")
            raise
        except PermissionError as e:
            logger.error(f"Sem permissão para criar diretório {path}: {e}")
            raise
        except OSError as e:
            logger.error(f"Erro ao criar diretório {path}: {e}")
            raise
    
    def path_exists(self, path: Path) -> bool:
        """
        Verifica se um caminho existe.
        
        Args:
            path: Caminho a ser verificado.
            
        Returns:
            True se o caminho existir, False caso contrário.
        """
        exists = path.exists()
        logger.debug(f"Verificando se {path} existe: {exists}")
        return exists
    
    def get_creation_time(self, path: Path) -> Optional[float]:
        """
        Retorna o timestamp de criação do arquivo.
        
        Args:
            path: Caminho do arquivo.
            
        Returns:
            Timestamp de criação como float (segundos desde a época) ou None se não disponível.
        """
        try:
            if not path.exists():
                logger.debug(f"Impossível obter data de criação: {path} não existe")
                return None
            
            # No Windows, st_ctime é a data de criação
            # No Unix, utiliza a melhor aproximação disponível (pode ser data de modificação dos metadados)
            ctime = path.stat().st_ctime
            logger.debug(f"Data de criação de {path}: {ctime}")
            return ctime
        except (PermissionError, OSError) as e:
            logger.error(f"Erro ao obter data de criação de {path}: {e}")
            return None
    
    def get_modification_time(self, path: Path) -> Optional[float]:
        """
        Retorna o timestamp de modificação do arquivo.
        
        Args:
            path: Caminho do arquivo.
            
        Returns:
            Timestamp de modificação como float (segundos desde a época) ou None se não disponível.
        """
        try:
            if not path.exists():
                logger.debug(f"Impossível obter data de modificação: {path} não existe")
                return None
            
            mtime = path.stat().st_mtime
            logger.debug(f"Data de modificação de {path}: {mtime}")
            return mtime
        except (PermissionError, OSError) as e:
            logger.error(f"Erro ao obter data de modificação de {path}: {e}")
            return None 