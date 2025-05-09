"""
Implementação do serviço de sistema de arquivos.

Este módulo implementa a interface IFileSystemService, fornecendo operações
de sistema de arquivos como leitura, escrita, movimentação para lixeira e
listagem de diretórios.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Iterable, Optional, List, Iterator
import send2trash

from fotix.infrastructure.interfaces import IFileSystemService

# Configuração do logger para este módulo
logger = logging.getLogger(__name__)

class FileSystemService(IFileSystemService):
    """
    Implementação da interface IFileSystemService para operações no sistema de arquivos.
    
    Esta classe implementa operações como leitura, escrita, movimentação para lixeira
    e listagem de diretórios, usando as bibliotecas padrão do Python e send2trash.
    """
    
    def get_file_size(self, path: Path) -> Optional[int]:
        """
        Retorna o tamanho do arquivo em bytes.
        
        Args:
            path: Caminho do arquivo.
            
        Returns:
            Tamanho do arquivo em bytes ou None se o arquivo não existir/for inacessível.
        """
        try:
            if not path.is_file():
                logger.debug(f"Caminho não é um arquivo ou não existe: {path}")
                return None
            size = path.stat().st_size
            logger.debug(f"Tamanho do arquivo {path}: {size} bytes")
            return size
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.error(f"Erro ao obter tamanho do arquivo {path}: {str(e)}")
            return None
    
    def stream_file_content(self, path: Path, chunk_size: int = 65536) -> Iterable[bytes]:
        """
        Retorna um iterador/gerador para ler o conteúdo do arquivo em blocos.
        
        Args:
            path: Caminho do arquivo.
            chunk_size: Tamanho de cada bloco de leitura em bytes.
            
        Returns:
            Iterador/gerador que produz blocos de bytes do arquivo.
            
        Raises:
            FileNotFoundError: Se o arquivo não existir.
            PermissionError: Se não houver permissão para ler o arquivo.
            IOError: Para outros erros de IO.
        """
        logger.debug(f"Iniciando stream do arquivo: {path} (chunk_size={chunk_size})")
        try:
            with open(path, 'rb') as file:
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
            logger.debug(f"Stream do arquivo {path} concluído com sucesso")
        except (FileNotFoundError, PermissionError) as e:
            logger.error(f"Erro ao ler arquivo {path}: {str(e)}")
            raise  # Re-lança a exceção original para que o chamador possa tratá-la
        except IOError as e:
            logger.error(f"Erro de IO ao ler arquivo {path}: {str(e)}")
            raise
    
    def list_directory_contents(self, path: Path, recursive: bool = True,
                              file_extensions: Optional[List[str]] = None) -> Iterable[Path]:
        """
        Lista os arquivos (e diretórios) em um diretório, com filtros opcionais.
        
        Args:
            path: Caminho do diretório.
            recursive: Se True, inclui arquivos em subdiretórios recursivamente.
            file_extensions: Lista opcional de extensões de arquivo para filtrar
                           (ex: ['.jpg', '.png']). Se None, inclui todos os arquivos.
                           
        Returns:
            Iterador/gerador que produz caminhos de arquivos/diretórios.
            
        Raises:
            FileNotFoundError: Se o diretório não existir.
            PermissionError: Se não houver permissão para acessar o diretório.
            NotADirectoryError: Se o caminho não for um diretório.
        """
        if not path.exists():
            logger.error(f"Diretório não existe: {path}")
            raise FileNotFoundError(f"Diretório não existe: {path}")
        
        if not path.is_dir():
            logger.error(f"Caminho não é um diretório: {path}")
            raise NotADirectoryError(f"Caminho não é um diretório: {path}")
        
        logger.debug(f"Listando conteúdo do diretório: {path} (recursive={recursive}, " 
                     f"extensions={file_extensions if file_extensions else 'todas'})")
        
        try:
            # Função para verificar se um arquivo corresponde às extensões desejadas
            def matches_extension(file_path: Path) -> bool:
                if file_extensions is None:
                    return True
                return file_path.suffix.lower() in [ext.lower() for ext in file_extensions]
            
            # Listagem recursiva usando Path.glob ou Path.rglob
            if recursive:
                pattern = "**/*"  # Padrão para todos os arquivos em todos os subdiretórios
                generator = path.glob(pattern)
            else:
                pattern = "*"  # Padrão para apenas arquivos no diretório atual
                generator = path.glob(pattern)
            
            # Filtra pelo tipo de arquivo se necessário e aplica filtro de extensão
            for item in generator:
                if item.is_file() and matches_extension(item):
                    logger.debug(f"Arquivo encontrado: {item}")
                    yield item
                elif item.is_dir() and item != path:  # Evita incluir o próprio diretório
                    logger.debug(f"Diretório encontrado: {item}")
                    yield item
            
            logger.debug(f"Listagem do diretório {path} concluída com sucesso")
            
        except PermissionError as e:
            logger.error(f"Erro de permissão ao listar diretório {path}: {str(e)}")
            raise
        except OSError as e:
            logger.error(f"Erro ao listar diretório {path}: {str(e)}")
            raise
    
    def move_to_trash(self, path: Path) -> None:
        """
        Move o arquivo ou diretório para a lixeira do sistema.
        
        Args:
            path: Caminho do arquivo ou diretório a ser movido para a lixeira.
            
        Raises:
            FileNotFoundError: Se o arquivo/diretório não existir.
            PermissionError: Se não houver permissão para movê-lo.
            OSError: Para outros erros do sistema operacional durante a operação.
        """
        if not path.exists():
            logger.error(f"Arquivo/diretório não existe: {path}")
            raise FileNotFoundError(f"Arquivo/diretório não existe: {path}")
        
        logger.info(f"Movendo para a lixeira: {path}")
        try:
            send2trash.send2trash(str(path))
            logger.info(f"Arquivo/diretório movido para a lixeira com sucesso: {path}")
        except PermissionError as e:
            logger.error(f"Erro de permissão ao mover para a lixeira: {path}, {str(e)}")
            raise
        except OSError as e:
            logger.error(f"Erro ao mover para a lixeira: {path}, {str(e)}")
            raise
    
    def copy_file(self, source: Path, destination: Path) -> None:
        """
        Copia um arquivo de origem para o destino.
        
        Args:
            source: Caminho do arquivo de origem.
            destination: Caminho de destino para o arquivo.
            
        Raises:
            FileNotFoundError: Se o arquivo de origem não existir.
            PermissionError: Se não houver permissão para ler a origem ou escrever no destino.
            IsADirectoryError: Se a origem for um diretório e não um arquivo.
            OSError: Para outros erros do sistema operacional durante a operação.
        """
        if not source.exists():
            logger.error(f"Arquivo de origem não existe: {source}")
            raise FileNotFoundError(f"Arquivo de origem não existe: {source}")
        
        if source.is_dir():
            logger.error(f"Origem é um diretório, não um arquivo: {source}")
            raise IsADirectoryError(f"Origem é um diretório, não um arquivo: {source}")
        
        # Certifica-se de que o diretório de destino existe
        destination_dir = destination.parent
        if not destination_dir.exists():
            logger.debug(f"Criando diretório de destino: {destination_dir}")
            destination_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Copiando arquivo de {source} para {destination}")
        try:
            shutil.copy2(source, destination)  # copy2 preserva metadados como timestamps
            logger.info(f"Arquivo copiado com sucesso de {source} para {destination}")
        except PermissionError as e:
            logger.error(f"Erro de permissão ao copiar arquivo: {str(e)}")
            raise
        except OSError as e:
            logger.error(f"Erro ao copiar arquivo: {str(e)}")
            raise
    
    def create_directory(self, path: Path, exist_ok: bool = True) -> None:
        """
        Cria um diretório.
        
        Args:
            path: Caminho do diretório a ser criado.
            exist_ok: Se True, não gera erro se o diretório já existir.
            
        Raises:
            FileExistsError: Se o diretório já existir e exist_ok for False.
            PermissionError: Se não houver permissão para criar o diretório.
            OSError: Para outros erros do sistema operacional durante a operação.
        """
        logger.info(f"Criando diretório: {path} (exist_ok={exist_ok})")
        try:
            path.mkdir(parents=True, exist_ok=exist_ok)
            logger.info(f"Diretório criado (ou já existente): {path}")
        except FileExistsError as e:
            logger.error(f"Diretório já existe e exist_ok é False: {path}")
            raise
        except PermissionError as e:
            logger.error(f"Erro de permissão ao criar diretório {path}: {str(e)}")
            raise
        except OSError as e:
            logger.error(f"Erro ao criar diretório {path}: {str(e)}")
            raise
    
    def path_exists(self, path: Path) -> bool:
        """
        Verifica se um caminho (arquivo ou diretório) existe.
        
        Args:
            path: Caminho a ser verificado.
            
        Returns:
            True se o caminho existir, False caso contrário.
        """
        exists = path.exists()
        logger.debug(f"Verificando existência do caminho {path}: {'existe' if exists else 'não existe'}")
        return exists
    
    def get_creation_time(self, path: Path) -> Optional[float]:
        """
        Retorna o timestamp de criação do arquivo ou diretório.
        
        Args:
            path: Caminho do arquivo ou diretório.
            
        Returns:
            Timestamp de criação como float (segundos desde epoch) ou
            None se o arquivo não existir ou a informação não estiver disponível.
        """
        try:
            if not path.exists():
                logger.debug(f"Caminho não existe: {path}")
                return None
            
            # O atributo ctime em Windows é criação, mas em Unix pode ser a última modificação de metadados
            # Para maior portabilidade, verificamos os atributos de stat disponíveis em cada sistema
            stat_result = path.stat()
            
            # Em Windows, st_ctime é o tempo de criação
            # Em Unix/Linux, podemos tentar obter st_birthtime (disponível em alguns sistemas)
            # Se não estiver disponível, usamos st_ctime como melhor aproximação
            if hasattr(stat_result, 'st_birthtime'):  # macOS e alguns BSDs
                creation_time = stat_result.st_birthtime
            else:  # Windows ou Linux sem st_birthtime
                creation_time = stat_result.st_ctime
                
            logger.debug(f"Timestamp de criação para {path}: {creation_time}")
            return creation_time
            
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.error(f"Erro ao obter timestamp de criação para {path}: {str(e)}")
            return None
    
    def get_modification_time(self, path: Path) -> Optional[float]:
        """
        Retorna o timestamp de modificação do arquivo ou diretório.
        
        Args:
            path: Caminho do arquivo ou diretório.
            
        Returns:
            Timestamp de modificação como float (segundos desde epoch) ou
            None se o arquivo não existir ou a informação não estiver disponível.
        """
        try:
            if not path.exists():
                logger.debug(f"Caminho não existe: {path}")
                return None
            
            modification_time = path.stat().st_mtime
            logger.debug(f"Timestamp de modificação para {path}: {modification_time}")
            return modification_time
            
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.error(f"Erro ao obter timestamp de modificação para {path}: {str(e)}")
            return None 