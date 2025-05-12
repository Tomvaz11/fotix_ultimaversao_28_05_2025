"""
Serviço de gerenciamento de duplicatas do Fotix.

Este módulo implementa o DuplicateManagementService, responsável por gerenciar
a seleção do arquivo a ser mantido (usando SelectionStrategy), a remoção segura
(usando FileSystemService) e o backup (usando BackupService).
"""

from pathlib import Path
from typing import List, Optional, Callable, Dict, Any, Tuple

from fotix.core.interfaces import ISelectionStrategy
from fotix.core.models import DuplicateSet, FileInfo
from fotix.infrastructure.interfaces import IFileSystemService, IBackupService
from fotix.infrastructure.logging_config import get_logger
from fotix.utils.helpers import measure_time

# Obter logger para este módulo
logger = get_logger(__name__)


class DuplicateManagementService:
    """
    Serviço de gerenciamento de duplicatas.
    
    Esta classe gerencia a seleção do arquivo a ser mantido (usando SelectionStrategy),
    a remoção segura dos arquivos duplicados (usando FileSystemService) e o backup
    (usando BackupService).
    """
    
    def __init__(
        self,
        selection_strategy: ISelectionStrategy,
        file_system_service: IFileSystemService,
        backup_service: IBackupService
    ):
        """
        Inicializa o serviço de gerenciamento de duplicatas.
        
        Args:
            selection_strategy: Estratégia para selecionar qual arquivo manter.
            file_system_service: Serviço para operações no sistema de arquivos.
            backup_service: Serviço para backup de arquivos.
        """
        self.selection_strategy = selection_strategy
        self.file_system_service = file_system_service
        self.backup_service = backup_service
        logger.debug("DuplicateManagementService inicializado")
    
    @measure_time
    def process_duplicate_set(
        self,
        duplicate_set: DuplicateSet,
        create_backup: bool = True,
        custom_selection: Optional[FileInfo] = None
    ) -> Dict[str, Any]:
        """
        Processa um conjunto de duplicatas, selecionando o arquivo a manter,
        fazendo backup dos outros e movendo-os para a lixeira.
        
        Args:
            duplicate_set: Conjunto de arquivos duplicados a ser processado.
            create_backup: Se True, cria backup dos arquivos antes de removê-los.
            custom_selection: Se fornecido, usa este arquivo como o arquivo a manter
                             em vez de aplicar a estratégia de seleção.
        
        Returns:
            Dict[str, Any]: Dicionário com informações sobre o processamento:
                - 'kept_file': FileInfo do arquivo mantido
                - 'removed_files': Lista de FileInfo dos arquivos removidos
                - 'backup_id': ID do backup criado (ou None se não criado)
                - 'error': Mensagem de erro (se ocorrer)
        
        Raises:
            ValueError: Se o conjunto de duplicatas estiver vazio.
        """
        if not duplicate_set.files:
            error_msg = "O conjunto de duplicatas está vazio"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Processando conjunto de duplicatas com hash {duplicate_set.hash}, "
                   f"{len(duplicate_set.files)} arquivos")
        
        result = {
            'kept_file': None,
            'removed_files': [],
            'backup_id': None,
            'error': None
        }
        
        try:
            # Selecionar o arquivo a manter
            if custom_selection:
                # Verificar se o arquivo selecionado está no conjunto
                if custom_selection not in duplicate_set.files:
                    raise ValueError("O arquivo selecionado não está no conjunto de duplicatas")
                file_to_keep = custom_selection
                logger.info(f"Usando seleção personalizada: {file_to_keep.path}")
            else:
                # Usar a estratégia de seleção
                file_to_keep = self.selection_strategy.select_file_to_keep(duplicate_set)
                logger.info(f"Arquivo selecionado pela estratégia: {file_to_keep.path}")
            
            # Identificar arquivos a serem removidos
            files_to_remove = [f for f in duplicate_set.files if f != file_to_keep]
            
            # Fazer backup dos arquivos a serem removidos (se solicitado)
            if create_backup and files_to_remove:
                backup_id = self._backup_files(files_to_remove)
                result['backup_id'] = backup_id
            
            # Remover os arquivos duplicados (mover para a lixeira)
            for file_info in files_to_remove:
                self._remove_file(file_info)
                result['removed_files'].append(file_info)
            
            # Atualizar resultado
            result['kept_file'] = file_to_keep
            
            logger.info(f"Processamento concluído. Mantido: {file_to_keep.path}, "
                       f"Removidos: {len(files_to_remove)} arquivos")
            
            return result
            
        except Exception as e:
            error_msg = f"Erro ao processar conjunto de duplicatas: {str(e)}"
            logger.error(error_msg)
            result['error'] = error_msg
            return result
    
    def _backup_files(self, files: List[FileInfo]) -> str:
        """
        Cria backup dos arquivos especificados.
        
        Args:
            files: Lista de arquivos a serem incluídos no backup.
            
        Returns:
            str: ID do backup criado.
            
        Raises:
            Exception: Se ocorrer um erro durante o backup.
        """
        logger.info(f"Criando backup de {len(files)} arquivos")
        
        # Preparar lista de tuplas (caminho, FileInfo) para o serviço de backup
        files_to_backup = [(file_info.path, file_info) for file_info in files 
                          if not file_info.in_zip]  # Ignorar arquivos dentro de ZIPs
        
        if not files_to_backup:
            logger.warning("Nenhum arquivo válido para backup")
            return "no_backup_needed"
        
        try:
            # Criar o backup usando o serviço de backup
            backup_id = self.backup_service.create_backup(files_to_backup)
            logger.info(f"Backup criado com sucesso. ID: {backup_id}")
            return backup_id
        except Exception as e:
            logger.error(f"Erro ao criar backup: {str(e)}")
            raise
    
    def _remove_file(self, file_info: FileInfo) -> None:
        """
        Remove um arquivo (move para a lixeira).
        
        Args:
            file_info: Informações sobre o arquivo a ser removido.
            
        Raises:
            Exception: Se ocorrer um erro durante a remoção.
        """
        if file_info.in_zip:
            logger.info(f"Arquivo dentro de ZIP, não pode ser removido diretamente: {file_info.path}")
            return
        
        logger.info(f"Removendo arquivo: {file_info.path}")
        
        try:
            # Mover o arquivo para a lixeira usando o serviço de sistema de arquivos
            self.file_system_service.move_to_trash(file_info.path)
            logger.info(f"Arquivo movido para a lixeira com sucesso: {file_info.path}")
        except Exception as e:
            logger.error(f"Erro ao remover arquivo {file_info.path}: {str(e)}")
            raise
