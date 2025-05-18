"""
Implementação do serviço de detecção de duplicatas para o Fotix.

Este módulo implementa a interface IDuplicateFinderService, fornecendo a lógica
central para identificar arquivos duplicados com base em seu conteúdo (hash).
Utiliza o algoritmo BLAKE3 para hashing eficiente e inclui otimizações como
pré-filtragem por tamanho.
"""

import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Callable, Iterable

import blake3

from fotix.core.interfaces import IDuplicateFinderService
from fotix.core.models import DuplicateSet, FileInfo
from fotix.infrastructure.interfaces import IFileSystemService, IZipHandlerService
from fotix.infrastructure.logging_config import get_logger
from fotix.utils.helpers import measure_time

# Obter logger para este módulo
logger = get_logger(__name__)

# Tamanho do bloco para leitura de arquivos (64KB)
CHUNK_SIZE = 65536

# Tamanho mínimo para considerar arquivos como potenciais duplicatas (1KB)
# Arquivos muito pequenos podem ter colisões de hash mais frequentes
MIN_FILE_SIZE = 1024


class DuplicateFinderService(IDuplicateFinderService):
    """
    Implementação do serviço de detecção de duplicatas.

    Esta classe implementa a interface IDuplicateFinderService, fornecendo
    métodos para identificar arquivos duplicados com base em seu conteúdo.
    Utiliza o algoritmo BLAKE3 para hashing eficiente e inclui otimizações
    como pré-filtragem por tamanho.
    """

    def __init__(self, file_system_service: IFileSystemService,
                zip_handler_service: Optional[IZipHandlerService] = None):
        """
        Inicializa o serviço de detecção de duplicatas.

        Args:
            file_system_service: Serviço para operações no sistema de arquivos.
            zip_handler_service: Serviço opcional para manipulação de arquivos ZIP.
                                Necessário apenas se include_zips=True for usado.
        """
        self.file_system_service = file_system_service
        self.zip_handler_service = zip_handler_service
        logger.debug("DuplicateFinderService inicializado")

    @measure_time
    def find_duplicates(self, scan_paths: List[Path], include_zips: bool,
                       progress_callback: Optional[Callable[[float], None]] = None) -> List[DuplicateSet]:
        """
        Analisa os caminhos fornecidos e retorna uma lista de conjuntos de arquivos duplicados.

        Args:
            scan_paths: Lista de caminhos (diretórios e/ou arquivos) a serem analisados.
            include_zips: Se True, também analisa o conteúdo de arquivos ZIP encontrados.
            progress_callback: Função opcional para reportar o progresso (0.0 a 1.0).

        Returns:
            List[DuplicateSet]: Lista de conjuntos de arquivos duplicados encontrados.

        Raises:
            ValueError: Se include_zips=True mas zip_handler_service não foi fornecido.
        """
        if include_zips and self.zip_handler_service is None:
            raise ValueError("zip_handler_service é necessário quando include_zips=True")

        logger.info(f"Iniciando busca por duplicatas em {len(scan_paths)} caminhos (include_zips={include_zips})")

        # Etapa 1: Coletar informações de todos os arquivos
        all_files: List[FileInfo] = []
        total_paths = len(scan_paths)

        for i, path in enumerate(scan_paths):
            if progress_callback:
                # Reportar progresso da fase de coleta (0% a 50%)
                progress_callback(0.5 * i / total_paths)

            if path.is_dir():
                # Processar diretório
                files = self._process_directory(path, include_zips)
                all_files.extend(files)
            elif path.is_file():
                # Processar arquivo individual
                if include_zips and path.suffix.lower() == '.zip' and self.zip_handler_service:
                    # Processar arquivo ZIP
                    zip_files = self._process_zip(path)
                    all_files.extend(zip_files)
                else:
                    # Processar arquivo normal
                    size = self.file_system_service.get_file_size(path)
                    if size and size >= MIN_FILE_SIZE:
                        file_info = FileInfo(
                            path=path,
                            size=size,
                            hash=None,  # Hash será calculado posteriormente se necessário
                            creation_time=self.file_system_service.get_creation_time(path),
                            modification_time=self.file_system_service.get_modification_time(path),
                            in_zip=False
                        )
                        all_files.append(file_info)

        logger.info(f"Coletados {len(all_files)} arquivos para análise")

        # Etapa 2: Agrupar arquivos por tamanho (pré-filtragem)
        size_groups = self._group_files_by_size(all_files)

        # Etapa 3: Para cada grupo de mesmo tamanho, calcular hashes e agrupar por hash
        duplicate_sets: List[DuplicateSet] = []
        total_size_groups = len(size_groups)
        processed_groups = 0

        for size, files in size_groups.items():
            if len(files) > 1:  # Apenas grupos com mais de um arquivo podem ter duplicatas
                # Calcular hash para cada arquivo no grupo
                for file_info in files:
                    if file_info.hash is None:  # Se o hash ainda não foi calculado
                        try:
                            file_info.hash = self._calculate_file_hash(file_info)
                        except Exception as e:
                            logger.warning(f"Erro ao calcular hash para {file_info.path}: {str(e)}")
                            # Manter o hash como None, este arquivo será ignorado na etapa seguinte

                # Agrupar por hash
                hash_groups = self._group_files_by_hash(files)

                # Criar DuplicateSet para cada grupo com mesmo hash
                for hash_value, hash_files in hash_groups.items():
                    if len(hash_files) > 1:  # Apenas grupos com mais de um arquivo são duplicatas
                        duplicate_set = DuplicateSet(files=hash_files, hash=hash_value)
                        duplicate_sets.append(duplicate_set)

            processed_groups += 1
            if progress_callback:
                # Reportar progresso da fase de análise (50% a 100%)
                progress_callback(0.5 + 0.5 * processed_groups / total_size_groups)

        # Ordenar os conjuntos de duplicatas por tamanho (do maior para o menor)
        # Isso é útil para a UI, mostrando primeiro as duplicatas que ocupam mais espaço
        duplicate_sets.sort(key=lambda ds: ds.size, reverse=True)

        logger.info(f"Encontrados {len(duplicate_sets)} conjuntos de duplicatas")
        return duplicate_sets

    def _process_directory(self, directory: Path, include_zips: bool) -> List[FileInfo]:
        """
        Processa um diretório, coletando informações sobre seus arquivos.

        Args:
            directory: Caminho para o diretório a ser processado.
            include_zips: Se True, também processa arquivos ZIP encontrados.

        Returns:
            List[FileInfo]: Lista de informações sobre os arquivos encontrados.
        """
        logger.debug(f"Processando diretório: {directory}")
        files: List[FileInfo] = []

        try:
            # Listar todos os arquivos no diretório (recursivamente)
            file_paths = list(self.file_system_service.list_directory_contents(directory))

            for file_path in file_paths:
                # Verificar se é um arquivo ZIP
                if include_zips and file_path.suffix.lower() == '.zip' and self.zip_handler_service:
                    # Processar arquivo ZIP
                    zip_files = self._process_zip(file_path)
                    files.extend(zip_files)

                # Processar arquivo normal
                size = self.file_system_service.get_file_size(file_path)
                if size and size >= MIN_FILE_SIZE:
                    file_info = FileInfo(
                        path=file_path,
                        size=size,
                        hash=None,  # Hash será calculado posteriormente se necessário
                        creation_time=self.file_system_service.get_creation_time(file_path),
                        modification_time=self.file_system_service.get_modification_time(file_path),
                        in_zip=False
                    )
                    files.append(file_info)

        except Exception as e:
            logger.error(f"Erro ao processar diretório {directory}: {str(e)}")

        logger.debug(f"Encontrados {len(files)} arquivos no diretório {directory}")
        return files

    def _process_zip(self, zip_path: Path) -> List[FileInfo]:
        """
        Processa um arquivo ZIP, coletando informações sobre seus arquivos internos.

        Args:
            zip_path: Caminho para o arquivo ZIP a ser processado.

        Returns:
            List[FileInfo]: Lista de informações sobre os arquivos encontrados no ZIP.
        """
        if self.zip_handler_service is None:
            logger.warning(f"Tentativa de processar ZIP sem zip_handler_service: {zip_path}")
            return []

        logger.debug(f"Processando arquivo ZIP: {zip_path}")
        files: List[FileInfo] = []

        try:
            # Obter timestamp de modificação do arquivo ZIP
            zip_modification_time = self.file_system_service.get_modification_time(zip_path)

            # Iterar sobre os arquivos no ZIP
            for file_name, file_size, content_fn in self.zip_handler_service.stream_zip_entries(zip_path):
                # Ignorar arquivos muito pequenos
                if file_size >= MIN_FILE_SIZE:
                    # Criar um caminho virtual para o arquivo dentro do ZIP
                    # Formato: zip_path:internal_path
                    virtual_path = Path(f"{zip_path}:{file_name}")

                    file_info = FileInfo(
                        path=virtual_path,
                        size=file_size,
                        hash=None,  # Hash será calculado posteriormente
                        # Usar o timestamp do ZIP como aproximação
                        creation_time=zip_modification_time,
                        modification_time=zip_modification_time,
                        in_zip=True,
                        zip_path=zip_path,
                        internal_path=file_name,
                        content_provider=content_fn
                    )
                    files.append(file_info)

        except Exception as e:
            logger.error(f"Erro ao processar arquivo ZIP {zip_path}: {str(e)}")

        logger.debug(f"Encontrados {len(files)} arquivos no ZIP {zip_path}")
        return files

    def _calculate_file_hash(self, file_info: FileInfo) -> str:
        """
        Calcula o hash BLAKE3 de um arquivo.

        Args:
            file_info: Informações sobre o arquivo.

        Returns:
            str: Hash do arquivo em formato hexadecimal.

        Raises:
            FileNotFoundError: Se o arquivo não existir.
            PermissionError: Se não houver permissão para ler o arquivo.
            Exception: Outras exceções relacionadas a IO podem ser levantadas.
        """
        logger.debug(f"Calculando hash para: {file_info.path}")

        # Criar um novo hasher BLAKE3
        hasher = blake3.blake3()

        try:
            if file_info.in_zip:
                # Arquivo dentro de um ZIP
                if not hasattr(file_info, 'content_provider') or file_info.content_provider is None:
                    raise ValueError(f"Arquivo ZIP sem content_provider: {file_info.path}")

                # Usar o content_provider para obter o conteúdo do arquivo
                for chunk in file_info.content_provider():
                    hasher.update(chunk)
            else:
                # Arquivo normal no sistema de arquivos
                for chunk in self.file_system_service.stream_file_content(file_info.path, CHUNK_SIZE):
                    hasher.update(chunk)

            # Obter o hash em formato hexadecimal
            hash_hex = hasher.hexdigest()
            logger.debug(f"Hash calculado para {file_info.path}: {hash_hex}")
            return hash_hex

        except Exception as e:
            logger.error(f"Erro ao calcular hash para {file_info.path}: {str(e)}")
            raise

    def _group_files_by_size(self, files: List[FileInfo]) -> Dict[int, List[FileInfo]]:
        """
        Agrupa arquivos por tamanho.

        Args:
            files: Lista de informações sobre arquivos.

        Returns:
            Dict[int, List[FileInfo]]: Dicionário onde a chave é o tamanho em bytes
                                      e o valor é uma lista de arquivos com esse tamanho.
        """
        size_groups = defaultdict(list)

        for file_info in files:
            size_groups[file_info.size].append(file_info)

        logger.debug(f"Arquivos agrupados em {len(size_groups)} grupos por tamanho")
        return size_groups

    def _group_files_by_hash(self, files: List[FileInfo]) -> Dict[str, List[FileInfo]]:
        """
        Agrupa arquivos por hash.

        Args:
            files: Lista de informações sobre arquivos.

        Returns:
            Dict[str, List[FileInfo]]: Dicionário onde a chave é o hash
                                      e o valor é uma lista de arquivos com esse hash.
        """
        hash_groups = defaultdict(list)

        for file_info in files:
            if file_info.hash:  # Ignorar arquivos sem hash (erro ao calcular)
                hash_groups[file_info.hash].append(file_info)

        logger.debug(f"Arquivos agrupados em {len(hash_groups)} grupos por hash")
        return hash_groups
