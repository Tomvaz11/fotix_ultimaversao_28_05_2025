"""
Implementação do serviço de backup para o Fotix.

Este módulo implementa a interface IBackupService, fornecendo métodos
para criar, listar, restaurar e excluir backups de arquivos.
"""

import json
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple, Any

from fotix.config import get_backup_dir
from fotix.core.models import FileInfo
from fotix.infrastructure.logging_config import get_logger

# Obter logger para este módulo
logger = get_logger(__name__)


class BackupService:
    """
    Implementação da interface IBackupService.
    
    Esta classe fornece métodos para gerenciar backups de arquivos,
    incluindo criação, listagem, restauração e exclusão. Utiliza um
    sistema de armazenamento baseado em arquivos, com metadados em JSON.
    """
    
    def __init__(self, file_system_service=None):
        """
        Inicializa o serviço de backup.
        
        Args:
            file_system_service: Instância de IFileSystemService para operações de arquivo.
                                Se None, as operações serão realizadas diretamente.
        """
        self.file_system_service = file_system_service
        self.backup_dir = get_backup_dir()
        self.metadata_dir = self.backup_dir / "metadata"
        self.files_dir = self.backup_dir / "files"
        
        # Garantir que os diretórios existam
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.files_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Serviço de backup inicializado. Diretório de backup: {self.backup_dir}")
    
    def create_backup(self, files_to_backup: Iterable[Tuple[Path, FileInfo]]) -> str:
        """
        Cria um backup dos arquivos fornecidos.
        
        Args:
            files_to_backup: Coleção de tuplas contendo o caminho do arquivo e seu FileInfo.
                            O FileInfo contém metadados importantes como hash, tamanho, etc.
            
        Returns:
            str: ID único para o backup realizado.
            
        Raises:
            FileNotFoundError: Se algum dos arquivos não existir.
            PermissionError: Se não houver permissão para ler os arquivos ou escrever no destino.
            IOError: Para outros erros relacionados a IO.
        """
        # Gerar ID único para o backup
        backup_id = str(uuid.uuid4())
        backup_date = datetime.now().isoformat()
        
        # Criar diretório para este backup
        backup_files_dir = self.files_dir / backup_id
        backup_files_dir.mkdir(parents=True, exist_ok=True)
        
        # Metadados do backup
        metadata = {
            "id": backup_id,
            "date": backup_date,
            "files": []
        }
        
        file_count = 0
        total_size = 0
        
        logger.info(f"Iniciando backup {backup_id}")
        
        # Copiar cada arquivo para o diretório de backup
        for file_path, file_info in files_to_backup:
            try:
                # Verificar se o arquivo existe
                if not file_path.exists():
                    logger.warning(f"Arquivo não encontrado, pulando: {file_path}")
                    continue
                
                # Criar nome de arquivo único no backup (usando hash se disponível)
                if file_info.hash:
                    backup_filename = f"{file_info.hash}{file_path.suffix}"
                else:
                    # Se não tiver hash, usar um UUID
                    backup_filename = f"{uuid.uuid4()}{file_path.suffix}"
                
                backup_file_path = backup_files_dir / backup_filename
                
                # Copiar o arquivo
                if self.file_system_service:
                    self.file_system_service.copy_file(file_path, backup_file_path)
                else:
                    shutil.copy2(file_path, backup_file_path)
                
                # Adicionar metadados do arquivo
                file_metadata = {
                    "original_path": str(file_path),
                    "backup_filename": backup_filename,
                    "size": file_info.size,
                    "hash": file_info.hash,
                    "creation_time": file_info.creation_time,
                    "modification_time": file_info.modification_time
                }
                
                metadata["files"].append(file_metadata)
                file_count += 1
                total_size += file_info.size
                
                logger.debug(f"Arquivo copiado para backup: {file_path} -> {backup_file_path}")
                
            except (FileNotFoundError, PermissionError) as e:
                logger.error(f"Erro ao fazer backup do arquivo {file_path}: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Erro inesperado ao fazer backup do arquivo {file_path}: {str(e)}")
                raise IOError(f"Erro ao fazer backup: {str(e)}")
        
        # Adicionar estatísticas ao metadata
        metadata["file_count"] = file_count
        metadata["total_size"] = total_size
        
        # Salvar metadados
        metadata_path = self.metadata_dir / f"{backup_id}.json"
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Backup {backup_id} concluído com sucesso. {file_count} arquivos, {total_size} bytes.")
            return backup_id
            
        except Exception as e:
            logger.error(f"Erro ao salvar metadados do backup {backup_id}: {str(e)}")
            # Tentar limpar o diretório de backup em caso de erro
            try:
                shutil.rmtree(backup_files_dir)
            except Exception:
                pass
            raise IOError(f"Erro ao salvar metadados do backup: {str(e)}")
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        Retorna uma lista de informações sobre os backups disponíveis.
        
        Returns:
            List[Dict[str, Any]]: Lista de dicionários, cada um contendo informações
                                 sobre um backup.
        """
        backups = []
        
        try:
            # Listar todos os arquivos de metadados
            for metadata_file in self.metadata_dir.glob("*.json"):
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    # Extrair informações relevantes
                    backup_info = {
                        "id": metadata.get("id"),
                        "date": metadata.get("date"),
                        "file_count": metadata.get("file_count", 0),
                        "total_size": metadata.get("total_size", 0)
                    }
                    
                    backups.append(backup_info)
                    
                except Exception as e:
                    logger.warning(f"Erro ao ler metadados do backup {metadata_file}: {str(e)}")
            
            # Ordenar por data (mais recente primeiro)
            backups.sort(key=lambda x: x.get("date", ""), reverse=True)
            
            logger.info(f"Listados {len(backups)} backups.")
            return backups
            
        except Exception as e:
            logger.error(f"Erro ao listar backups: {str(e)}")
            return []
    
    def restore_backup(self, backup_id: str, target_directory: Optional[Path] = None) -> None:
        """
        Restaura os arquivos de um backup específico.
        
        Args:
            backup_id: ID do backup a ser restaurado.
            target_directory: Diretório alvo para restauração. Se None, os arquivos
                             são restaurados em seus locais originais.
            
        Raises:
            ValueError: Se o backup_id for inválido ou não existir.
            FileExistsError: Se algum arquivo de destino já existir e não puder ser sobrescrito.
            PermissionError: Se não houver permissão para escrever nos destinos.
            IOError: Para outros erros relacionados a IO.
        """
        # Verificar se o backup existe
        metadata_path = self.metadata_dir / f"{backup_id}.json"
        if not metadata_path.exists():
            logger.error(f"Backup não encontrado: {backup_id}")
            raise ValueError(f"Backup não encontrado: {backup_id}")
        
        # Carregar metadados
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        except Exception as e:
            logger.error(f"Erro ao ler metadados do backup {backup_id}: {str(e)}")
            raise IOError(f"Erro ao ler metadados do backup: {str(e)}")
        
        backup_files_dir = self.files_dir / backup_id
        if not backup_files_dir.exists():
            logger.error(f"Diretório de arquivos do backup não encontrado: {backup_files_dir}")
            raise ValueError(f"Diretório de arquivos do backup não encontrado")
        
        logger.info(f"Iniciando restauração do backup {backup_id}")
        
        # Restaurar cada arquivo
        for file_metadata in metadata.get("files", []):
            try:
                original_path = Path(file_metadata.get("original_path", ""))
                backup_filename = file_metadata.get("backup_filename")
                
                if not backup_filename:
                    logger.warning("Metadados de arquivo incompletos, pulando")
                    continue
                
                backup_file_path = backup_files_dir / backup_filename
                
                # Determinar o destino da restauração
                if target_directory:
                    # Restaurar apenas com o nome do arquivo (sem estrutura de diretórios)
                    dest_path = target_directory / original_path.name
                else:
                    # Restaurar no local original
                    dest_path = original_path
                
                # Garantir que o diretório de destino exista
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copiar o arquivo
                if self.file_system_service:
                    self.file_system_service.copy_file(backup_file_path, dest_path)
                else:
                    shutil.copy2(backup_file_path, dest_path)
                
                logger.debug(f"Arquivo restaurado: {backup_file_path} -> {dest_path}")
                
            except FileExistsError as e:
                logger.error(f"Arquivo já existe: {dest_path}")
                raise
            except (FileNotFoundError, PermissionError) as e:
                logger.error(f"Erro ao restaurar arquivo: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Erro inesperado ao restaurar arquivo: {str(e)}")
                raise IOError(f"Erro ao restaurar backup: {str(e)}")
        
        logger.info(f"Restauração do backup {backup_id} concluída com sucesso.")
    
    def delete_backup(self, backup_id: str) -> None:
        """
        Remove um backup específico.
        
        Args:
            backup_id: ID do backup a ser removido.
            
        Raises:
            ValueError: Se o backup_id for inválido ou não existir.
            PermissionError: Se não houver permissão para excluir os arquivos.
            IOError: Para outros erros relacionados a IO.
        """
        # Verificar se o backup existe
        metadata_path = self.metadata_dir / f"{backup_id}.json"
        if not metadata_path.exists():
            logger.error(f"Backup não encontrado: {backup_id}")
            raise ValueError(f"Backup não encontrado: {backup_id}")
        
        backup_files_dir = self.files_dir / backup_id
        
        logger.info(f"Removendo backup {backup_id}")
        
        # Remover diretório de arquivos
        try:
            if backup_files_dir.exists():
                shutil.rmtree(backup_files_dir)
                logger.debug(f"Diretório de arquivos removido: {backup_files_dir}")
        except Exception as e:
            logger.error(f"Erro ao remover diretório de arquivos do backup {backup_id}: {str(e)}")
            raise IOError(f"Erro ao remover arquivos do backup: {str(e)}")
        
        # Remover arquivo de metadados
        try:
            metadata_path.unlink()
            logger.debug(f"Arquivo de metadados removido: {metadata_path}")
        except Exception as e:
            logger.error(f"Erro ao remover metadados do backup {backup_id}: {str(e)}")
            raise IOError(f"Erro ao remover metadados do backup: {str(e)}")
        
        logger.info(f"Backup {backup_id} removido com sucesso.")
