"""
Implementação do serviço de sistema de arquivos para o Fotix.

Este módulo implementa a interface IFileSystemService definida em fotix.infrastructure.interfaces,
fornecendo funcionalidades concretas para interagir com o sistema de arquivos local.
"""

import os
import shutil
from pathlib import Path
from typing import Iterable, List, Optional

import send2trash

from fotix.infrastructure.interfaces import IFileSystemService
from fotix.infrastructure.logging_config import get_logger

# Obter logger para este módulo
logger = get_logger(__name__)


class FileSystemService(IFileSystemService):
    """
    Implementação concreta do serviço de sistema de arquivos.
    
    Esta classe implementa a interface IFileSystemService usando as bibliotecas
    pathlib, shutil, os e send2trash para operações no sistema de arquivos.
    """
    
    def get_file_size(self, path: Path) -> Optional[int]:
        """
        Retorna o tamanho do arquivo em bytes.
        
        Args:
            path: Caminho para o arquivo.
            
        Returns:
            int: Tamanho do arquivo em bytes, ou None se o arquivo não existir ou não for acessível.
        """
        try:
            return path.stat().st_size
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.debug(f"Não foi possível obter o tamanho do arquivo {path}: {str(e)}")
            return None
    
    def stream_file_content(self, path: Path, chunk_size: int = 65536) -> Iterable[bytes]:
        """
        Retorna um iterador/gerador para ler o conteúdo do arquivo em blocos.
        
        Args:
            path: Caminho para o arquivo.
            chunk_size: Tamanho de cada bloco em bytes. O padrão é 65536 (64KB).
            
        Returns:
            Iterable[bytes]: Iterador/gerador que produz blocos do conteúdo do arquivo.
            
        Raises:
            FileNotFoundError: Se o arquivo não existir.
            PermissionError: Se não houver permissão para ler o arquivo.
            IOError: Para outros erros de IO.
        """
        try:
            with open(path, 'rb') as file:
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        except (FileNotFoundError, PermissionError) as e:
            logger.error(f"Erro ao ler o arquivo {path}: {str(e)}")
            raise
        except IOError as e:
            logger.error(f"Erro de IO ao ler o arquivo {path}: {str(e)}")
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
            path: Caminho para o diretório.
            recursive: Se True, lista também os arquivos em subdiretórios. O padrão é True.
            file_extensions: Lista opcional de extensões de arquivo para filtrar (ex: ['.jpg', '.png']).
                            Se None, não aplica filtro de extensão.
            
        Returns:
            Iterable[Path]: Iterador/gerador que produz caminhos de arquivos.
            
        Raises:
            FileNotFoundError: Se o diretório não existir.
            NotADirectoryError: Se o caminho não for um diretório.
            PermissionError: Se não houver permissão para acessar o diretório.
        """
        if not path.exists():
            logger.error(f"Diretório não encontrado: {path}")
            raise FileNotFoundError(f"Diretório não encontrado: {path}")
        
        if not path.is_dir():
            logger.error(f"O caminho não é um diretório: {path}")
            raise NotADirectoryError(f"O caminho não é um diretório: {path}")
        
        try:
            # Normalizar extensões para minúsculas se fornecidas
            normalized_extensions = None
            if file_extensions:
                normalized_extensions = [ext.lower() for ext in file_extensions]
            
            # Escolher o método de listagem com base no parâmetro recursive
            if recursive:
                walker = path.rglob('*')
            else:
                walker = path.glob('*')
            
            # Filtrar apenas arquivos (não diretórios) e aplicar filtro de extensão se necessário
            for item in walker:
                if item.is_file():
                    if normalized_extensions is None or item.suffix.lower() in normalized_extensions:
                        yield item
        except PermissionError as e:
            logger.error(f"Erro de permissão ao acessar o diretório {path}: {str(e)}")
            raise
        except OSError as e:
            logger.error(f"Erro ao listar o conteúdo do diretório {path}: {str(e)}")
            raise
    
    def move_to_trash(self, path: Path) -> None:
        """
        Move o arquivo ou diretório para a lixeira do sistema.
        
        Args:
            path: Caminho para o arquivo ou diretório.
            
        Raises:
            FileNotFoundError: Se o arquivo ou diretório não existir.
            PermissionError: Se não houver permissão para mover o arquivo ou diretório.
            OSError: Para outros erros do sistema operacional.
        """
        if not path.exists():
            logger.error(f"Arquivo ou diretório não encontrado: {path}")
            raise FileNotFoundError(f"Arquivo ou diretório não encontrado: {path}")
        
        try:
            logger.info(f"Movendo para a lixeira: {path}")
            send2trash.send2trash(str(path))
        except PermissionError as e:
            logger.error(f"Erro de permissão ao mover para a lixeira: {path}: {str(e)}")
            raise
        except OSError as e:
            logger.error(f"Erro ao mover para a lixeira: {path}: {str(e)}")
            raise
    
    def copy_file(self, source: Path, destination: Path) -> None:
        """
        Copia um arquivo de origem para destino.
        
        Args:
            source: Caminho para o arquivo de origem.
            destination: Caminho para o arquivo de destino.
            
        Raises:
            FileNotFoundError: Se o arquivo de origem não existir.
            PermissionError: Se não houver permissão para ler o arquivo de origem ou escrever no destino.
            IsADirectoryError: Se o destino for um diretório.
            IOError: Para outros erros de IO.
        """
        if not source.exists():
            logger.error(f"Arquivo de origem não encontrado: {source}")
            raise FileNotFoundError(f"Arquivo de origem não encontrado: {source}")
        
        if not source.is_file():
            logger.error(f"A origem não é um arquivo: {source}")
            raise IsADirectoryError(f"A origem não é um arquivo: {source}")
        
        # Criar o diretório de destino se não existir
        destination_dir = destination.parent
        if not destination_dir.exists():
            try:
                destination_dir.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as e:
                logger.error(f"Erro ao criar diretório de destino {destination_dir}: {str(e)}")
                raise
        
        try:
            logger.debug(f"Copiando arquivo de {source} para {destination}")
            shutil.copy2(source, destination)
        except PermissionError as e:
            logger.error(f"Erro de permissão ao copiar arquivo: {str(e)}")
            raise
        except IsADirectoryError as e:
            logger.error(f"O destino é um diretório: {destination}: {str(e)}")
            raise
        except IOError as e:
            logger.error(f"Erro de IO ao copiar arquivo: {str(e)}")
            raise
    
    def create_directory(self, path: Path, exist_ok: bool = True) -> None:
        """
        Cria um diretório.
        
        Args:
            path: Caminho para o diretório a ser criado.
            exist_ok: Se True, não lança erro se o diretório já existir. O padrão é True.
            
        Raises:
            FileExistsError: Se o diretório já existir e exist_ok for False.
            PermissionError: Se não houver permissão para criar o diretório.
            FileNotFoundError: Se o diretório pai não existir.
        """
        try:
            logger.debug(f"Criando diretório: {path}")
            path.mkdir(parents=True, exist_ok=exist_ok)
        except FileExistsError as e:
            logger.error(f"Diretório já existe: {path}")
            raise
        except PermissionError as e:
            logger.error(f"Erro de permissão ao criar diretório {path}: {str(e)}")
            raise
        except FileNotFoundError as e:
            logger.error(f"Diretório pai não encontrado para {path}: {str(e)}")
            raise
    
    def path_exists(self, path: Path) -> bool:
        """
        Verifica se um caminho existe.
        
        Args:
            path: Caminho para verificar.
            
        Returns:
            bool: True se o caminho existir, False caso contrário.
        """
        return path.exists()
    
    def get_creation_time(self, path: Path) -> Optional[float]:
        """
        Retorna o timestamp de criação do arquivo ou diretório.
        
        Args:
            path: Caminho para o arquivo ou diretório.
            
        Returns:
            float: Timestamp de criação (segundos desde a época), ou None se não for possível obter.
        """
        try:
            # Em sistemas Windows, st_ctime é o tempo de criação
            # Em sistemas Unix, st_ctime é o tempo de mudança de status, não de criação
            # Usamos st_birthtime em sistemas que o suportam (como macOS)
            stat_result = path.stat()
            
            # Tentar obter st_birthtime (disponível em alguns sistemas como macOS)
            try:
                return getattr(stat_result, 'st_birthtime', None)
            except AttributeError:
                # Se st_birthtime não estiver disponível, usar st_ctime como fallback
                return stat_result.st_ctime
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.debug(f"Não foi possível obter o timestamp de criação para {path}: {str(e)}")
            return None
    
    def get_modification_time(self, path: Path) -> Optional[float]:
        """
        Retorna o timestamp de modificação do arquivo ou diretório.
        
        Args:
            path: Caminho para o arquivo ou diretório.
            
        Returns:
            float: Timestamp de modificação (segundos desde a época), ou None se não for possível obter.
        """
        try:
            return path.stat().st_mtime
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.debug(f"Não foi possível obter o timestamp de modificação para {path}: {str(e)}")
            return None
