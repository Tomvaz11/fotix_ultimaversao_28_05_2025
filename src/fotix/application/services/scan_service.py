"""
Serviço de varredura de diretórios e arquivos do Fotix.

Este módulo implementa o ScanService, responsável por orquestrar o processo
de varredura de diretórios e arquivos ZIP, utilizando os serviços de concorrência,
sistema de arquivos, manipulador de ZIP e o buscador de duplicatas do core.
"""

from pathlib import Path
from typing import List, Optional, Callable, Set, Dict, Tuple

from fotix.core.interfaces import IDuplicateFinderService
from fotix.core.models import DuplicateSet, FileInfo
from fotix.infrastructure.interfaces import (
    IConcurrencyService,
    IFileSystemService,
    IZipHandlerService
)
from fotix.infrastructure.logging_config import get_logger
from fotix.utils.helpers import measure_time

# Obter logger para este módulo
logger = get_logger(__name__)


class ScanService:
    """
    Serviço de varredura de diretórios e arquivos.
    
    Esta classe orquestra o processo de varredura de diretórios e arquivos ZIP,
    utilizando os serviços de concorrência, sistema de arquivos, manipulador de
    ZIP e o buscador de duplicatas do core.
    """
    
    def __init__(
        self,
        duplicate_finder_service: IDuplicateFinderService,
        file_system_service: IFileSystemService,
        zip_handler_service: IZipHandlerService,
        concurrency_service: IConcurrencyService
    ):
        """
        Inicializa o serviço de varredura.
        
        Args:
            duplicate_finder_service: Serviço para detecção de duplicatas.
            file_system_service: Serviço para operações no sistema de arquivos.
            zip_handler_service: Serviço para manipulação de arquivos ZIP.
            concurrency_service: Serviço para execução de tarefas em paralelo.
        """
        self.duplicate_finder_service = duplicate_finder_service
        self.file_system_service = file_system_service
        self.zip_handler_service = zip_handler_service
        self.concurrency_service = concurrency_service
        logger.debug("ScanService inicializado")
    
    @measure_time
    def scan_directories(
        self,
        directories: List[Path],
        include_zips: bool = True,
        file_extensions: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> List[DuplicateSet]:
        """
        Varre os diretórios especificados em busca de arquivos duplicados.
        
        Args:
            directories: Lista de diretórios a serem analisados.
            include_zips: Se True, também analisa o conteúdo de arquivos ZIP encontrados.
            file_extensions: Lista opcional de extensões de arquivo para filtrar.
                           Se None, todos os arquivos são incluídos.
            progress_callback: Função opcional para reportar o progresso (0.0 a 1.0).
        
        Returns:
            List[DuplicateSet]: Lista de conjuntos de arquivos duplicados encontrados.
        
        Raises:
            ValueError: Se algum dos diretórios não existir ou não for um diretório.
        """
        logger.info(f"Iniciando varredura de {len(directories)} diretórios (include_zips={include_zips})")
        
        # Validar diretórios
        self._validate_directories(directories)
        
        # Filtrar diretórios para remover subdiretórios já incluídos
        filtered_directories = self._filter_nested_directories(directories)
        if len(filtered_directories) < len(directories):
            logger.info(f"Removidos {len(directories) - len(filtered_directories)} diretórios aninhados")
        
        # Preparar caminhos para varredura
        scan_paths = self._prepare_scan_paths(filtered_directories, file_extensions)
        
        # Delegar a detecção de duplicatas para o serviço especializado
        duplicate_sets = self.duplicate_finder_service.find_duplicates(
            scan_paths=scan_paths,
            include_zips=include_zips,
            progress_callback=progress_callback
        )
        
        logger.info(f"Varredura concluída. Encontrados {len(duplicate_sets)} conjuntos de duplicatas")
        return duplicate_sets
    
    def _validate_directories(self, directories: List[Path]) -> None:
        """
        Valida se os diretórios especificados existem e são realmente diretórios.
        
        Args:
            directories: Lista de diretórios a serem validados.
            
        Raises:
            ValueError: Se algum dos diretórios não existir ou não for um diretório.
        """
        invalid_dirs = []
        
        for directory in directories:
            if not self.file_system_service.path_exists(directory):
                invalid_dirs.append(f"'{directory}' não existe")
            elif not directory.is_dir():
                invalid_dirs.append(f"'{directory}' não é um diretório")
        
        if invalid_dirs:
            error_msg = f"Diretórios inválidos: {', '.join(invalid_dirs)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def _filter_nested_directories(self, directories: List[Path]) -> List[Path]:
        """
        Filtra diretórios para remover subdiretórios já incluídos em outros diretórios da lista.
        
        Args:
            directories: Lista de diretórios a serem filtrados.
            
        Returns:
            List[Path]: Lista de diretórios filtrada, sem subdiretórios redundantes.
        """
        # Ordenar diretórios por comprimento do caminho (do mais curto para o mais longo)
        sorted_dirs = sorted(directories, key=lambda p: len(str(p)))
        filtered_dirs = []
        
        for current_dir in sorted_dirs:
            # Verificar se o diretório atual é subdiretório de algum já incluído
            is_subdirectory = False
            for parent_dir in filtered_dirs:
                try:
                    # Verificar se current_dir é subdiretório de parent_dir
                    current_dir.relative_to(parent_dir)
                    is_subdirectory = True
                    logger.debug(f"Diretório '{current_dir}' é subdiretório de '{parent_dir}', ignorando")
                    break
                except ValueError:
                    # Não é subdiretório, continuar verificação
                    pass
            
            if not is_subdirectory:
                filtered_dirs.append(current_dir)
        
        return filtered_dirs
    
    def _prepare_scan_paths(self, directories: List[Path], file_extensions: Optional[List[str]] = None) -> List[Path]:
        """
        Prepara os caminhos para varredura, expandindo diretórios conforme necessário.
        
        Args:
            directories: Lista de diretórios a serem preparados.
            file_extensions: Lista opcional de extensões de arquivo para filtrar.
            
        Returns:
            List[Path]: Lista de caminhos para varredura.
        """
        # Por enquanto, apenas retorna os diretórios como estão
        # Em versões futuras, pode implementar lógica adicional de preparação
        return directories
