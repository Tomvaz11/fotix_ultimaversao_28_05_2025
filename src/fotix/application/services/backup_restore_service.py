"""
Serviço de gerenciamento de backups e restauração do Fotix.

Este módulo implementa o BackupRestoreService, responsável por gerenciar
a listagem e restauração de backups, utilizando os serviços de backup
e sistema de arquivos da infraestrutura.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any

from fotix.infrastructure.interfaces import IBackupService, IFileSystemService
from fotix.infrastructure.logging_config import get_logger
from fotix.utils.helpers import measure_time

# Obter logger para este módulo
logger = get_logger(__name__)


class BackupRestoreService:
    """
    Serviço para gerenciar a listagem e restauração de backups.
    
    Esta classe fornece métodos para listar backups disponíveis,
    obter detalhes de um backup específico, restaurar backups para
    seus locais originais ou para um diretório específico, e excluir
    backups.
    """
    
    def __init__(
        self,
        backup_service: IBackupService,
        file_system_service: IFileSystemService
    ):
        """
        Inicializa o serviço de backup e restauração.
        
        Args:
            backup_service: Serviço para operações de backup.
            file_system_service: Serviço para operações no sistema de arquivos.
        """
        self.backup_service = backup_service
        self.file_system_service = file_system_service
        logger.debug("BackupRestoreService inicializado")
    
    @measure_time
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        Lista todos os backups disponíveis.
        
        Returns:
            List[Dict[str, Any]]: Lista de dicionários contendo informações sobre
                                 cada backup (id, data, número de arquivos, tamanho total).
        
        Raises:
            IOError: Se ocorrer um erro ao acessar os metadados dos backups.
        """
        logger.info("Listando backups disponíveis")
        try:
            backups = self.backup_service.list_backups()
            logger.debug(f"Encontrados {len(backups)} backups")
            return backups
        except Exception as e:
            logger.error(f"Erro ao listar backups: {str(e)}")
            raise IOError(f"Erro ao listar backups: {str(e)}")
    
    @measure_time
    def get_backup_details(self, backup_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes de um backup específico.
        
        Args:
            backup_id: ID do backup.
            
        Returns:
            Dict[str, Any]: Dicionário contendo informações detalhadas sobre o backup,
                           incluindo lista de arquivos.
        
        Raises:
            ValueError: Se o backup_id for inválido ou não existir.
            IOError: Se ocorrer um erro ao acessar os metadados do backup.
        """
        logger.info(f"Obtendo detalhes do backup {backup_id}")
        
        # Verificar se o backup existe na lista de backups
        try:
            backups = self.backup_service.list_backups()
            backup_info = next((b for b in backups if b["id"] == backup_id), None)
            
            if not backup_info:
                logger.error(f"Backup não encontrado: {backup_id}")
                raise ValueError(f"Backup não encontrado: {backup_id}")
            
            # Obter detalhes adicionais do backup (como lista de arquivos)
            # Nota: Isso depende da implementação específica do BackupService
            # Aqui estamos assumindo que os detalhes completos já estão incluídos
            # na resposta de list_backups()
            
            logger.debug(f"Detalhes do backup {backup_id} obtidos com sucesso")
            return backup_info
            
        except ValueError:
            # Repassar exceções de valor (backup não encontrado)
            raise
        except Exception as e:
            logger.error(f"Erro ao obter detalhes do backup {backup_id}: {str(e)}")
            raise IOError(f"Erro ao obter detalhes do backup: {str(e)}")
    
    @measure_time
    def restore_backup(
        self,
        backup_id: str,
        target_directory: Optional[Path] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Restaura um backup para seus locais originais ou para um diretório específico.
        
        Args:
            backup_id: ID do backup a ser restaurado.
            target_directory: Diretório alvo para restauração. Se None, os arquivos
                             são restaurados em seus locais originais.
            progress_callback: Função opcional para reportar progresso da restauração.
                              Deve aceitar um valor float entre 0 e 1.
            
        Returns:
            Dict[str, Any]: Dicionário contendo informações sobre a restauração,
                           incluindo status e mensagem.
        
        Raises:
            ValueError: Se o backup_id for inválido ou não existir.
            IOError: Se ocorrer um erro durante a restauração.
        """
        logger.info(f"Iniciando restauração do backup {backup_id}")
        
        if target_directory:
            logger.info(f"Diretório alvo para restauração: {target_directory}")
            
            # Verificar se o diretório alvo existe
            if not self.file_system_service.path_exists(target_directory):
                try:
                    logger.debug(f"Criando diretório alvo: {target_directory}")
                    self.file_system_service.create_directory(target_directory)
                except Exception as e:
                    logger.error(f"Erro ao criar diretório alvo: {str(e)}")
                    raise IOError(f"Erro ao criar diretório alvo: {str(e)}")
        
        try:
            # Restaurar o backup
            self.backup_service.restore_backup(backup_id, target_directory)
            
            # Obter detalhes do backup para incluir no resultado
            backup_info = self.get_backup_details(backup_id)
            
            result = {
                "status": "success",
                "message": f"Backup {backup_id} restaurado com sucesso",
                "backup_info": backup_info,
                "target_directory": str(target_directory) if target_directory else "locais originais"
            }
            
            logger.info(f"Backup {backup_id} restaurado com sucesso")
            return result
            
        except ValueError as e:
            # Repassar exceções de valor (backup não encontrado)
            logger.error(f"Backup não encontrado: {backup_id}")
            raise
        except Exception as e:
            logger.error(f"Erro ao restaurar backup {backup_id}: {str(e)}")
            raise IOError(f"Erro ao restaurar backup: {str(e)}")
    
    @measure_time
    def delete_backup(self, backup_id: str) -> Dict[str, Any]:
        """
        Remove um backup específico.
        
        Args:
            backup_id: ID do backup a ser removido.
            
        Returns:
            Dict[str, Any]: Dicionário contendo informações sobre a remoção,
                           incluindo status e mensagem.
        
        Raises:
            ValueError: Se o backup_id for inválido ou não existir.
            IOError: Se ocorrer um erro durante a remoção.
        """
        logger.info(f"Removendo backup {backup_id}")
        
        try:
            # Obter detalhes do backup antes de removê-lo (para incluir no resultado)
            backup_info = self.get_backup_details(backup_id)
            
            # Remover o backup
            self.backup_service.delete_backup(backup_id)
            
            result = {
                "status": "success",
                "message": f"Backup {backup_id} removido com sucesso",
                "backup_info": backup_info
            }
            
            logger.info(f"Backup {backup_id} removido com sucesso")
            return result
            
        except ValueError:
            # Repassar exceções de valor (backup não encontrado)
            logger.error(f"Backup não encontrado: {backup_id}")
            raise
        except Exception as e:
            logger.error(f"Erro ao remover backup {backup_id}: {str(e)}")
            raise IOError(f"Erro ao remover backup: {str(e)}")
