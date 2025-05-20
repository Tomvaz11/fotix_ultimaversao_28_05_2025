"""
Serviço de gerenciamento de duplicatas do Fotix.

Este módulo implementa o DuplicateManagementService, responsável por gerenciar
a seleção do arquivo a ser mantido (usando SelectionStrategy), a remoção segura
(usando FileSystemService) e o backup (usando BackupService).
"""

from pathlib import Path
from typing import List, Optional, Callable, Dict, Any, Tuple
import tempfile
import shutil
import os

from fotix.core.interfaces import ISelectionStrategy
from fotix.core.models import DuplicateSet, FileInfo
from fotix.infrastructure.interfaces import IFileSystemService, IBackupService, IZipHandlerService
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
        backup_service: IBackupService,
        zip_handler_service: IZipHandlerService
    ):
        """
        Inicializa o serviço de gerenciamento de duplicatas.
        
        Args:
            selection_strategy: Estratégia para selecionar qual arquivo manter.
            file_system_service: Serviço para operações no sistema de arquivos.
            backup_service: Serviço para backup de arquivos.
            zip_handler_service: Serviço para manipulação de arquivos ZIP.
        """
        self.selection_strategy = selection_strategy
        self.file_system_service = file_system_service
        self.backup_service = backup_service
        self.zip_handler_service = zip_handler_service
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
            
            actual_removed_files_info: List[FileInfo] = [] # Declarada aqui
            skipped_zip_files_info: List[FileInfo] = [] # Declarada aqui

            # --- Início da nova lógica para lidar com duplicatas internas de ZIP ---
            is_internal_zip_scenario = False
            if file_to_keep.in_zip:
                # Verificar se algum dos files_to_remove está no MESMO zip que o file_to_keep
                for f_remove in files_to_remove:
                    if f_remove.in_zip and f_remove.zip_path == file_to_keep.zip_path:
                        is_internal_zip_scenario = True
                        break
            
            if is_internal_zip_scenario:
                logger.info(f"Cenário de duplicatas internas no ZIP detectado para: {file_to_keep.zip_path}")
                result['processed_as_extracted_folder'] = True
                
                original_zip_path = file_to_keep.zip_path
                # Assegurar que original_zip_path é um Path; FileInfo.zip_path já deve ser Path
                if not isinstance(original_zip_path, Path):
                    original_zip_path = Path(str(original_zip_path)) # Conversão por segurança

                output_folder_name = f"{original_zip_path.stem}_conteudo_filtrado"
                output_folder_path = original_zip_path.parent / output_folder_name
                result['output_folder_path'] = str(output_folder_path)
                
                # Função auxiliar para extrair o nome interno real de um FileInfo de ZIP
                def extract_actual_internal_name(file_info_path_obj: Path) -> str:
                    """
                    Extrai o nome interno real de um arquivo dentro do ZIP.
                    
                    Args:
                        file_info_path_obj: Path object contendo o caminho completo do arquivo no formato
                                          'caminho_do_zip:caminho_interno_no_zip'
                    
                    Returns:
                        str: O caminho interno do arquivo no ZIP (sem o caminho do arquivo ZIP)
                    """
                    s = str(file_info_path_obj)
                    # Primeiro, encontrar onde termina o caminho do ZIP
                    zip_path_str = str(original_zip_path)
                    if s.startswith(zip_path_str):
                        # Pular o caminho do ZIP e o caractere ':' para obter apenas o caminho interno
                        internal_path = s[len(zip_path_str) + 1:]
                        # Normalizar separadores de caminho para '/'
                        return internal_path.replace('\\', '/')
                    return s.replace('\\', '/') # Fallback, normalizar separadores de qualquer forma

                # Garantir que estamos usando as STRINGS dos NOMES INTERNOS REAIS nos conjuntos.
                # FileInfo.path para ZIPs é um Path object: "zip_path_str:internal_path_str"
                
                actual_internal_name_to_keep = extract_actual_internal_name(file_to_keep.path)
                zip_internal_names_to_keep = {actual_internal_name_to_keep}
                
                zip_internal_names_to_remove_from_this_zip = set()
                for f_remove in files_to_remove:
                    if f_remove.in_zip and f_remove.zip_path == original_zip_path:
                        actual_internal_name_to_remove = extract_actual_internal_name(f_remove.path)
                        zip_internal_names_to_remove_from_this_zip.add(actual_internal_name_to_remove)

                logger.debug(f"[ZIP Interno] file_to_keep.path: {file_to_keep.path} (Tipo: {type(file_to_keep.path)})")
                logger.debug(f"[ZIP Interno] Nome interno REAL extraído para MANTER: '{actual_internal_name_to_keep}'")
                logger.debug(f"[ZIP Interno] Nomes internos REAIS a MANTER (conjunto de STRINGS): {zip_internal_names_to_keep}")
                logger.debug(f"[ZIP Interno] Nomes internos REAIS a REMOVER deste ZIP (conjunto de STRINGS): {zip_internal_names_to_remove_from_this_zip}")

                try:
                    with tempfile.TemporaryDirectory(prefix="fotix_zip_extract_") as temp_dir_str:
                        temp_dir_path = Path(temp_dir_str)
                        logger.info(f"Extraindo {original_zip_path} para diretório temporário {temp_dir_path}")
                        
                        # Extrair tudo do ZIP para o diretório temporário
                        # O zip_handler_service.extract_all_to_directory retorna List[Path] dos arquivos extraídos
                        extracted_file_paths = self.zip_handler_service.extract_all_to_directory(
                            zip_path=original_zip_path,
                            target_directory=temp_dir_path
                        )
                        logger.info(f"{len(extracted_file_paths)} arquivos/pastas extraídos de {original_zip_path}")
                        
                        # Criar o diretório de saída final se não existir
                        if not output_folder_path.exists():
                            output_folder_path.mkdir(parents=True, exist_ok=True)
                            logger.info(f"Diretório de saída criado: {output_folder_path}")
                        elif not output_folder_path.is_dir():
                            raise OSError(f"Um arquivo já existe no caminho do diretório de saída: {output_folder_path}")
                        
                        copied_count = 0
                        # Iterar sobre os arquivos extraídos e copiar os que devem ser mantidos
                        for extracted_file_full_path in extracted_file_paths:
                            # Obter o nome do arquivo relativo ao diretório temporário (que corresponde ao nome interno no ZIP)
                            # Precisamos normalizar os separadores de caminho para a comparação
                            # Path.relative_to() cuida disso.
                            try:
                                relative_path_in_temp = extracted_file_full_path.relative_to(temp_dir_path)
                                # O nome interno no ZIP pode ter separadores diferentes do OS.
                                # Normalizar para '/' como é esperado em FileInfo.path para arquivos ZIP.
                                internal_name_from_extraction = str(relative_path_in_temp).replace(os.sep, '/')
                                logger.debug(f"[ZIP Interno] Processando extraído: '{internal_name_from_extraction}' (original: '{extracted_file_full_path}')")
                            except ValueError as ve:
                                logger.warning(f"[ZIP Interno] Não foi possível obter o caminho relativo para {extracted_file_full_path} em {temp_dir_path}: {ve}. Pulando este arquivo.")
                                continue

                            copy_this_file = False
                            if internal_name_from_extraction in zip_internal_names_to_keep:
                                logger.info(f"[ZIP Interno] MARCADO PARA COPIAR (é o arquivo a manter): {internal_name_from_extraction}")
                                copy_this_file = True
                            elif internal_name_from_extraction in zip_internal_names_to_remove_from_this_zip:
                                logger.info(f"[ZIP Interno] IGNORADO (é uma duplicata a ser removida do ZIP): {internal_name_from_extraction}")
                                # copy_this_file permanece False, e vamos pular a cópia
                                continue # Pula para o próximo arquivo na extração
                            else:
                                logger.info(f"[ZIP Interno] MARCADO PARA COPIAR (outro arquivo do ZIP original): {internal_name_from_extraction}")
                                copy_this_file = True
                            
                            if copy_this_file:
                                destination_file_path = output_folder_path / relative_path_in_temp # Usa relative_path_in_temp para manter estrutura de subpastas
                                
                                if extracted_file_full_path.is_file():
                                    destination_file_path.parent.mkdir(parents=True, exist_ok=True)
                                    shutil.copy2(extracted_file_full_path, destination_file_path)
                                    copied_count += 1
                                    logger.debug(f"[ZIP Interno] COPIADO: '{extracted_file_full_path}' para '{destination_file_path}'")
                                elif extracted_file_full_path.is_dir():
                                    if not destination_file_path.exists(): # Cria o diretório no destino se não existir
                                        destination_file_path.mkdir(parents=True, exist_ok=True)
                                        logger.debug(f"[ZIP Interno] DIRETÓRIO CRIADO/VERIFICADO NO DESTINO: '{destination_file_path}'")
                            # else: o arquivo foi marcado para não ser copiado (era um 'file_to_remove')

                        logger.info(f"{copied_count} arquivos copiados para {output_folder_path}")
                        result['message'] = f"Duplicatas dentro de {original_zip_path.name} processadas. Conteúdo filtrado salvo em {output_folder_name}. O ZIP original não foi modificado."
                        result['kept_file'] = file_to_keep # O FileInfo original
                        result['removed_files'] = [f for f in files_to_remove if f.in_zip and f.zip_path == original_zip_path]
                        result['backup_id'] = "original_zip_not_modified"
                        # Skipped zip files count não se aplica aqui da mesma forma, pois foram "processados"
                        result['skipped_zip_files_count'] = 0 
                        # Limpar os arquivos removidos que foram tratados por esta lógica
                        actual_removed_files_info = [] # Resetar, pois a "remoção" foi não copiar
                        skipped_zip_files_info = [f for f in files_to_remove if not (f.in_zip and f.zip_path == original_zip_path)]
                        # (continua para o resto dos arquivos do duplicate_set que não estão neste ZIP)

                except Exception as e_zip_proc:
                    error_msg = f"Erro ao processar duplicatas internas do ZIP {original_zip_path}: {str(e_zip_proc)}"
                    logger.error(error_msg, exc_info=True)
                    result['error'] = error_msg
                    # Se houve erro, não podemos garantir o estado, então retornamos
                    # Mantém o file_to_keep original e os files_to_remove para que o usuário veja
                    result['kept_file'] = file_to_keep 
                    result['removed_files'] = files_to_remove
                    return result

                # Se o cenário de ZIP interno foi tratado, os files_to_remove que estavam DENTRO desse ZIP
                # já foram "removidos" (não copiados). Precisamos filtrar files_to_remove para que a lógica
                # subsequente não tente processá-los novamente.
                files_to_remove_original_count = len(files_to_remove)
                files_to_remove = [f for f in files_to_remove if not (f.in_zip and f.zip_path == original_zip_path)]
                logger.info(f"{files_to_remove_original_count - len(files_to_remove)} arquivos do ZIP {original_zip_path.name} foram tratados pela lógica de extração.")
            
            # --- Fim da nova lógica para lidar com duplicatas internas de ZIP ---

            files_for_backup: List[FileInfo] = []

            # Fazer backup dos arquivos a serem removidos (se solicitado)
            if create_backup and files_to_remove:
                # Identificar arquivos que não estão em ZIP para backup
                for f_info in files_to_remove:
                    if not f_info.in_zip:
                        files_for_backup.append(f_info)
                
                if files_for_backup:
                    backup_id = self._backup_files(files_for_backup) # _backup_files já lida com in_zip, mas aqui garantimos
                    result['backup_id'] = backup_id
                else:
                    logger.info("Nenhum arquivo (não-ZIP) para fazer backup.")
                    result['backup_id'] = "no_backup_for_zip_files"
            
            # Remover os arquivos duplicados (mover para a lixeira)
            for file_info in files_to_remove:
                if file_info.in_zip:
                    logger.info(f"Arquivo {file_info.path} está dentro de um ZIP e não será removido.")
                    skipped_zip_files_info.append(file_info)
                else:
                    try:
                        # _remove_file já tem a checagem in_zip, mas chamamos aqui para arquivos não-ZIP
                        self._remove_file(file_info) 
                        actual_removed_files_info.append(file_info)
                    except Exception as e:
                        # Se _remove_file falhar, o arquivo não foi removido
                        logger.error(f"Falha ao remover o arquivo {file_info.path}: {str(e)}")
                        # Adicionar ao erro geral ou tratar de forma específica?
                        # Por enquanto, não adicionamos a actual_removed_files_info
                        # e deixamos o erro geral da exceção ser pego abaixo se necessário.
                        # Se uma exceção for pega aqui, ela será registrada e o processamento continua para outros arquivos.
                        # Se quisermos parar tudo, podemos relançar a exceção.
                        if result['error'] is None:
                            result['error'] = f"Falha ao remover {file_info.path}. "
                        else:
                            result['error'] += f"Falha ao remover {file_info.path}. "
            
            result['kept_file'] = file_to_keep
            result['removed_files'] = actual_removed_files_info # Apenas os que foram realmente movidos/tentados
            # Adicionar informação sobre arquivos ignorados ao resultado para a UI
            if 'skipped_zip_files_count' not in result:
                result['skipped_zip_files_count'] = len(skipped_zip_files_info)
            
            log_message = f"Processamento concluído. "
            if result.get('processed_as_extracted_folder'):
                log_message += f"ZIP Interno: {result.get('message', '')} "
            else:
                log_message += f"Mantido: {file_to_keep.path}. "
                log_message += f"Removidos (do sistema de arquivos): {len(actual_removed_files_info)}. "
                if skipped_zip_files_info:
                    log_message += f"Ignorados (dentro de ZIP): {len(skipped_zip_files_info)}. "
            
            if result.get('backup_id') and result['backup_id'] not in ["no_backup_needed", "no_backup_for_zip_files", "original_zip_not_modified"]:
                log_message += f"Backup ID: {result['backup_id']}."
            elif result.get('backup_id') == "no_backup_for_zip_files":
                log_message += "Nenhum backup realizado para arquivos em ZIP (não internos)."
            elif result.get('backup_id') == "original_zip_not_modified":
                log_message += "O arquivo ZIP original não foi modificado."
            
            logger.info(log_message)
            
            # Se houve erros parciais na remoção, garantir que sejam refletidos
            if result['error'] and not result['error'].startswith("Erro ao processar conjunto de duplicatas:"):
                 result['error'] = "Erros parciais durante a remoção: " + result['error']

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
