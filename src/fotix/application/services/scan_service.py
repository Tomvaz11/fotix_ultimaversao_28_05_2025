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
        paths_to_scan: List[Path],
        include_zips: bool = True,
        file_extensions: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> List[DuplicateSet]:
        """
        Varre os caminhos especificados (diretórios e/ou arquivos ZIP) em busca de arquivos duplicados.
        
        Args:
            paths_to_scan: Lista de caminhos (diretórios ou arquivos ZIP individuais) a serem analisados.
            include_zips: Se True, também analisa o conteúdo de arquivos ZIP encontrados (sejam eles
                          arquivos ZIP individuais na lista paths_to_scan ou dentro dos diretórios).
            file_extensions: Lista opcional de extensões de arquivo para filtrar.
                           Se None, todos os arquivos são incluídos.
            progress_callback: Função opcional para reportar o progresso (0.0 a 1.0).
        
        Returns:
            List[DuplicateSet]: Lista de conjuntos de arquivos duplicados encontrados.
        
        Raises:
            ValueError: Se algum dos caminhos que deveriam ser diretórios não existir ou não for um diretório,
                        ou se um arquivo que não é ZIP for passado diretamente.
        """
        logger.info(f"Iniciando varredura de {len(paths_to_scan)} caminhos (include_zips={include_zips})")
        logger.debug(f"[ScanService] Caminhos recebidos para scan: {paths_to_scan}")
        
        actual_directories: List[Path] = []
        individual_zip_files: List[Path] = []
        invalid_paths: List[str] = []

        for path in paths_to_scan:
            if not self.file_system_service.path_exists(path):
                invalid_paths.append(f"'{path}' não existe")
                continue

            if path.is_dir():
                actual_directories.append(path)
                logger.debug(f"[ScanService] Caminho classificado como DIRETÓRIO: {path}")
            elif path.is_file():
                logger.debug(f"[ScanService] Caminho classificado como ARQUIVO: {path}, Sufixo: {path.suffix.lower()}")
                if include_zips and path.suffix.lower() == '.zip':
                    individual_zip_files.append(path)
                    logger.debug(f"[ScanService] Arquivo classificado como ZIP INDIVIDUAL: {path}")
                else:
                    # É um arquivo, mas não é ZIP ou include_zips é False
                    invalid_paths.append(f"'{path}' é um arquivo mas não é um ZIP processável ou include_zips é falso.")
                    logger.warning(f"[ScanService] Arquivo IGNORADO (não é ZIP ou include_zips=False): {path}")
            else:
                # Nem diretório, nem arquivo (ex: link simbólico quebrado, etc.)
                invalid_paths.append(f"'{path}' não é um diretório nem um arquivo válido.")
                logger.warning(f"[ScanService] Caminho INVÁLIDO (nem dir, nem arq): {path}")

        if invalid_paths:
            error_msg = f"Caminhos inválidos fornecidos: {', '.join(invalid_paths)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        # Validar e filtrar apenas os diretórios reais
        # O método _validate_and_filter_directories será criado a seguir
        # Ele combinará _validate_directories e _filter_nested_directories
        # e só deve operar em caminhos que são confirmadamente diretórios.
        
        # Validar e filtrar os diretórios reais
        validated_and_filtered_directories = self._validate_and_filter_directories(actual_directories)
        
        # Preparar caminhos para varredura (combina diretórios validados e arquivos ZIP individuais)
        # O método _prepare_scan_paths será modificado para aceitar ambos
        scan_paths = self._prepare_scan_paths(
            valid_directories=validated_and_filtered_directories, 
            zip_files=individual_zip_files,
            file_extensions=file_extensions # file_extensions não é usado por _prepare_scan_paths atualmente
        )
        logger.debug(f"[ScanService] Caminhos preparados para DuplicateFinderService: {scan_paths}")
        
        if not scan_paths:
            logger.info("Nenhum caminho válido para varredura após filtragem e validação.")
            return []

        # Delegar a detecção de duplicatas para o serviço especializado
        duplicate_sets = self.duplicate_finder_service.find_duplicates(
            scan_paths=scan_paths,
            include_zips=include_zips,
            progress_callback=progress_callback
        )
        
        logger.info(f"Varredura concluída. Encontrados {len(duplicate_sets)} conjuntos de duplicatas")
        return duplicate_sets
    
    def _validate_and_filter_directories(self, directories_to_check: List[Path]) -> List[Path]:
        """
        Valida se os caminhos fornecidos são diretórios existentes e os filtra para remover aninhamentos.
        
        Args:
            directories_to_check: Lista de caminhos que se espera serem diretórios.
            
        Returns:
            List[Path]: Lista de diretórios validados e filtrados.
            
        Raises:
            ValueError: Se algum dos caminhos não existir ou não for um diretório.
        """
        if not directories_to_check:
            return []

        validated_dirs = []
        invalid_paths_messages = []
        for directory in directories_to_check:
            # A verificação de existência já foi feita em scan_directories, 
            # mas é bom manter aqui por segurança se o método for chamado de outro lugar.
            if not self.file_system_service.path_exists(directory):
                invalid_paths_messages.append(f"\'{directory}\' não existe")
            elif not directory.is_dir():
                invalid_paths_messages.append(f"\'{directory}\' não é um diretório")
            else:
                validated_dirs.append(directory)
        
        if invalid_paths_messages:
            error_msg = f"Diretórios inválidos fornecidos para validação interna: {', '.join(invalid_paths_messages)}"
            logger.error(error_msg)
            # Esta exceção idealmente não deveria ser alcançada se a lógica em scan_directories estiver correta.
            raise ValueError(error_msg)

        # Filtrar diretórios para remover subdiretórios já incluídos (lógica do antigo _filter_nested_directories)
        if not validated_dirs:
            return []

        # Ordenar diretórios por comprimento do caminho (do mais curto para o mais longo)
        sorted_dirs = sorted(validated_dirs, key=lambda p: len(str(p)))
        filtered_dirs = []
        
        for current_dir in sorted_dirs:
            is_subdirectory = False
            for parent_dir in filtered_dirs:
                try:
                    current_dir.relative_to(parent_dir)
                    is_subdirectory = True
                    logger.debug(f"Diretório '{current_dir}' é subdiretório de '{parent_dir}', ignorando")
                    break
                except ValueError:
                    pass  # Não é subdiretório
            
            if not is_subdirectory:
                filtered_dirs.append(current_dir)
        
        if len(filtered_dirs) < len(validated_dirs):
            logger.info(f"Removidos {len(validated_dirs) - len(filtered_dirs)} diretórios aninhados durante a validação e filtragem.")
            
        return filtered_dirs
    
    def _prepare_scan_paths(
        self, 
        valid_directories: List[Path], 
        zip_files: List[Path],
        file_extensions: Optional[List[str]] = None # Mantido para consistência, mas não usado aqui
    ) -> List[Path]:
        """
        Prepara os caminhos para varredura, combinando diretórios validados e arquivos ZIP individuais.
        
        Args:
            valid_directories: Lista de diretórios validados e filtrados.
            zip_files: Lista de arquivos ZIP individuais a serem incluídos diretamente.
            file_extensions: Lista opcional de extensões de arquivo para filtrar (não usado atualmente aqui).
            
        Returns:
            List[Path]: Lista combinada de caminhos para varredura.
        """
        # Combina os diretórios válidos com os arquivos ZIP individuais
        scan_paths = list(valid_directories)  # Cria uma cópia para não modificar a original se for a mesma referência
        scan_paths.extend(zip_files)
        
        if not scan_paths:
            logger.info("Nenhum caminho preparado para varredura.")
        else:
            logger.debug(f"Caminhos preparados para varredura: {scan_paths}")
            
        return scan_paths
