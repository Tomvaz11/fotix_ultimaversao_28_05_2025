"""
Implementação do serviço de sistema de arquivos para o Fotix.

Este módulo implementa a interface IFileSystemService, fornecendo métodos
para operações no sistema de arquivos como leitura, escrita, movimentação
para lixeira e listagem de diretórios.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional, List, Union

import send2trash

from fotix.infrastructure.logging_config import get_logger

# Obter logger para este módulo
logger = get_logger(__name__)


class FileSystemService:
    """
    Implementação da interface IFileSystemService.
    
    Esta classe fornece métodos para operações comuns no sistema de arquivos,
    como leitura, escrita, movimentação para lixeira e listagem de diretórios.
    Implementa tratamento de erros robusto e logging de operações.
    """
    
    def get_file_size(self, path: Path) -> Optional[int]:
        """
        Retorna o tamanho do arquivo em bytes.
        
        Args:
            path: Caminho para o arquivo.
            
        Returns:
            int: Tamanho do arquivo em bytes, ou None se o arquivo não existir
                 ou não for acessível.
        """
        try:
            # Verificar se é um arquivo (não um diretório)
            if not path.is_file():
                logger.debug(f"Caminho não é um arquivo: {path}")
                return None
            
            # Obter o tamanho do arquivo
            size = path.stat().st_size
            logger.debug(f"Tamanho do arquivo {path}: {size} bytes")
            return size
        except FileNotFoundError:
            logger.debug(f"Arquivo não encontrado: {path}")
            return None
        except PermissionError:
            logger.warning(f"Sem permissão para acessar o arquivo: {path}")
            return None
        except Exception as e:
            logger.error(f"Erro ao obter tamanho do arquivo {path}: {str(e)}")
            return None
    
    def stream_file_content(self, path: Path, chunk_size: int = 65536) -> Iterable[bytes]:
        """
        Retorna um iterador/gerador para ler o conteúdo do arquivo em blocos.
        
        Args:
            path: Caminho para o arquivo.
            chunk_size: Tamanho de cada bloco em bytes. Padrão é 64KB.
            
        Returns:
            Iterable[bytes]: Iterador/gerador que produz blocos do conteúdo do arquivo.
            
        Raises:
            FileNotFoundError: Se o arquivo não existir.
            PermissionError: Se não houver permissão para ler o arquivo.
            IsADirectoryError: Se o caminho apontar para um diretório.
            Exception: Outras exceções relacionadas a IO podem ser levantadas.
        """
        logger.debug(f"Iniciando streaming do arquivo: {path}")
        
        try:
            with open(path, 'rb') as file:
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
            
            logger.debug(f"Streaming do arquivo {path} concluído com sucesso")
        except FileNotFoundError:
            logger.error(f"Arquivo não encontrado: {path}")
            raise
        except PermissionError:
            logger.error(f"Sem permissão para ler o arquivo: {path}")
            raise
        except IsADirectoryError:
            logger.error(f"O caminho é um diretório, não um arquivo: {path}")
            raise
        except Exception as e:
            logger.error(f"Erro ao ler o arquivo {path}: {str(e)}")
            raise
    
    def list_directory_contents(self, path: Path, recursive: bool = True, 
                               file_extensions: Optional[List[str]] = None) -> Iterable[Path]:
        """
        Lista os conteúdos de um diretório, opcionalmente de forma recursiva.
        
        Args:
            path: Caminho para o diretório.
            recursive: Se True, lista também os conteúdos dos subdiretórios.
            file_extensions: Lista opcional de extensões de arquivo para filtrar.
                            Se None, todos os arquivos são incluídos.
                            Exemplo: ['.jpg', '.png']
            
        Returns:
            Iterable[Path]: Iterador/gerador que produz os caminhos dos arquivos
                           encontrados.
            
        Raises:
            FileNotFoundError: Se o diretório não existir.
            NotADirectoryError: Se o caminho não apontar para um diretório.
            PermissionError: Se não houver permissão para acessar o diretório.
        """
        logger.debug(f"Listando conteúdo do diretório: {path} (recursivo={recursive})")
        
        try:
            # Verificar se é um diretório
            if not path.is_dir():
                logger.error(f"O caminho não é um diretório: {path}")
                raise NotADirectoryError(f"O caminho não é um diretório: {path}")
            
            # Função para verificar se um arquivo deve ser incluído com base na extensão
            def should_include_file(file_path: Path) -> bool:
                if not file_extensions:
                    return True
                return file_path.suffix.lower() in file_extensions
            
            # Listar conteúdo do diretório
            if recursive:
                for item in path.rglob('*'):
                    if item.is_file() and should_include_file(item):
                        yield item
            else:
                for item in path.iterdir():
                    if item.is_file() and should_include_file(item):
                        yield item
            
            logger.debug(f"Listagem do diretório {path} concluída com sucesso")
        except FileNotFoundError:
            logger.error(f"Diretório não encontrado: {path}")
            raise
        except PermissionError:
            logger.error(f"Sem permissão para acessar o diretório: {path}")
            raise
        except Exception as e:
            logger.error(f"Erro ao listar o diretório {path}: {str(e)}")
            raise
    
    def move_to_trash(self, path: Path) -> None:
        """
        Move um arquivo ou diretório para a lixeira do sistema.
        
        Args:
            path: Caminho para o arquivo ou diretório a ser movido para a lixeira.
            
        Raises:
            FileNotFoundError: Se o caminho não existir.
            PermissionError: Se não houver permissão para mover o arquivo/diretório.
            OSError: Para outros erros relacionados ao sistema operacional.
        """
        logger.info(f"Movendo para a lixeira: {path}")
        
        try:
            # Verificar se o caminho existe
            if not path.exists():
                logger.error(f"Caminho não encontrado: {path}")
                raise FileNotFoundError(f"Caminho não encontrado: {path}")
            
            # Mover para a lixeira usando send2trash
            send2trash.send2trash(str(path))
            
            logger.info(f"Movido para a lixeira com sucesso: {path}")
        except FileNotFoundError:
            logger.error(f"Caminho não encontrado: {path}")
            raise
        except PermissionError:
            logger.error(f"Sem permissão para mover para a lixeira: {path}")
            raise
        except Exception as e:
            logger.error(f"Erro ao mover para a lixeira {path}: {str(e)}")
            raise
    
    def copy_file(self, source: Path, destination: Path) -> None:
        """
        Copia um arquivo de origem para destino.
        
        Args:
            source: Caminho para o arquivo de origem.
            destination: Caminho para o arquivo de destino.
            
        Raises:
            FileNotFoundError: Se o arquivo de origem não existir.
            IsADirectoryError: Se source for um diretório.
            PermissionError: Se não houver permissão para ler a origem ou escrever no destino.
            OSError: Para outros erros relacionados ao sistema operacional.
        """
        logger.info(f"Copiando arquivo de {source} para {destination}")
        
        try:
            # Verificar se a origem é um arquivo
            if not source.is_file():
                if not source.exists():
                    logger.error(f"Arquivo de origem não encontrado: {source}")
                    raise FileNotFoundError(f"Arquivo de origem não encontrado: {source}")
                else:
                    logger.error(f"A origem não é um arquivo: {source}")
                    raise IsADirectoryError(f"A origem não é um arquivo: {source}")
            
            # Criar diretório de destino se não existir
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Copiar o arquivo preservando metadados
            shutil.copy2(source, destination)
            
            logger.info(f"Arquivo copiado com sucesso de {source} para {destination}")
        except FileNotFoundError:
            logger.error(f"Arquivo de origem não encontrado: {source}")
            raise
        except PermissionError:
            logger.error(f"Sem permissão para copiar de {source} para {destination}")
            raise
        except Exception as e:
            logger.error(f"Erro ao copiar arquivo de {source} para {destination}: {str(e)}")
            raise
    
    def create_directory(self, path: Path, exist_ok: bool = True) -> None:
        """
        Cria um diretório e todos os diretórios pai necessários.
        
        Args:
            path: Caminho para o diretório a ser criado.
            exist_ok: Se True, não levanta erro se o diretório já existir.
            
        Raises:
            FileExistsError: Se o diretório já existir e exist_ok for False.
            PermissionError: Se não houver permissão para criar o diretório.
            FileNotFoundError: Se um diretório pai não puder ser criado.
        """
        logger.info(f"Criando diretório: {path}")
        
        try:
            path.mkdir(parents=True, exist_ok=exist_ok)
            logger.info(f"Diretório criado com sucesso: {path}")
        except FileExistsError:
            logger.warning(f"Diretório já existe: {path}")
            raise
        except PermissionError:
            logger.error(f"Sem permissão para criar o diretório: {path}")
            raise
        except Exception as e:
            logger.error(f"Erro ao criar o diretório {path}: {str(e)}")
            raise
    
    def path_exists(self, path: Path) -> bool:
        """
        Verifica se um caminho existe no sistema de arquivos.
        
        Args:
            path: Caminho a ser verificado.
            
        Returns:
            bool: True se o caminho existir, False caso contrário.
        """
        exists = path.exists()
        logger.debug(f"Verificando existência do caminho {path}: {exists}")
        return exists
    
    def get_creation_time(self, path: Path) -> Optional[float]:
        """
        Retorna o timestamp de criação do arquivo ou diretório.
        
        Args:
            path: Caminho para o arquivo ou diretório.
            
        Returns:
            float: Timestamp de criação (segundos desde a época), ou None se
                  o arquivo não existir ou a informação não estiver disponível.
        """
        try:
            if not path.exists():
                logger.debug(f"Caminho não encontrado: {path}")
                return None
            
            # Obter o timestamp de criação
            # Em sistemas Windows, st_ctime é o timestamp de criação
            # Em sistemas Unix, st_ctime é o timestamp de alteração de metadados
            # Usamos st_ctime como melhor aproximação disponível
            creation_time = path.stat().st_ctime
            logger.debug(f"Timestamp de criação para {path}: {creation_time}")
            return creation_time
        except Exception as e:
            logger.error(f"Erro ao obter timestamp de criação para {path}: {str(e)}")
            return None
    
    def get_modification_time(self, path: Path) -> Optional[float]:
        """
        Retorna o timestamp de última modificação do arquivo ou diretório.
        
        Args:
            path: Caminho para o arquivo ou diretório.
            
        Returns:
            float: Timestamp de modificação (segundos desde a época), ou None se
                  o arquivo não existir ou a informação não estiver disponível.
        """
        try:
            if not path.exists():
                logger.debug(f"Caminho não encontrado: {path}")
                return None
            
            # Obter o timestamp de modificação
            modification_time = path.stat().st_mtime
            logger.debug(f"Timestamp de modificação para {path}: {modification_time}")
            return modification_time
        except Exception as e:
            logger.error(f"Erro ao obter timestamp de modificação para {path}: {str(e)}")
            return None
