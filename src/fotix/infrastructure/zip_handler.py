"""
Implementação do serviço de manipulação de arquivos ZIP para o Fotix.

Este módulo implementa a interface IZipHandlerService definida em fotix.infrastructure.interfaces,
fornecendo funcionalidades para ler o conteúdo de arquivos dentro de arquivos ZIP de forma eficiente
(streaming), sem a necessidade de extração completa para o disco.
"""

import os
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Tuple

from stream_unzip import stream_unzip

from fotix.infrastructure.interfaces import IZipHandlerService
from fotix.infrastructure.logging_config import get_logger
from fotix.utils.helpers import filter_by_extensions

# Obter logger para este módulo
logger = get_logger(__name__)


class ZipHandlerService(IZipHandlerService):
    """
    Implementação concreta do serviço de manipulação de arquivos ZIP.

    Esta classe implementa a interface IZipHandlerService usando a biblioteca
    stream-unzip para ler o conteúdo de arquivos dentro de arquivos ZIP de forma
    eficiente (streaming), sem a necessidade de extração completa para o disco.
    """

    def stream_zip_entries(
        self,
        zip_path: Path,
        file_extensions: Optional[List[str]] = None
    ) -> Iterable[Tuple[str, Optional[int], Callable[[], Iterable[bytes]]]]:
        """
        Retorna um iterador/gerador para os arquivos dentro de um ZIP.

        Args:
            zip_path: Caminho para o arquivo ZIP.
            file_extensions: Lista opcional de extensões de arquivo para filtrar (ex: ['.jpg', '.png']).
                            Se None, não aplica filtro de extensão.

        Returns:
            Iterable[Tuple[str, Optional[int], Callable[[], Iterable[bytes]]]]:
                Iterador/gerador que produz tuplas contendo:
                - Nome do arquivo dentro do ZIP
                - Tamanho do arquivo em bytes (pode ser None se não disponível)
                - Uma função lazy que retorna um iterador/gerador para o conteúdo do arquivo em blocos

        Raises:
            FileNotFoundError: Se o arquivo ZIP não existir.
            PermissionError: Se não houver permissão para ler o arquivo ZIP.
            zipfile.BadZipFile: Se o arquivo não for um ZIP válido ou estiver corrompido.
            IOError: Para outros erros de IO.
        """
        logger.debug(f"Iniciando stream de arquivos do ZIP: {zip_path}")

        if not zip_path.exists():
            logger.error(f"Arquivo ZIP não encontrado: {zip_path}")
            raise FileNotFoundError(f"Arquivo ZIP não encontrado: {zip_path}")

        if not os.access(zip_path, os.R_OK):
            logger.error(f"Sem permissão para ler o arquivo ZIP: {zip_path}")
            raise PermissionError(f"Sem permissão para ler o arquivo ZIP: {zip_path}")

        try:
            # Função para ler o arquivo ZIP em blocos
            def zip_chunks():
                with open(zip_path, 'rb') as f:
                    chunk_size = 65536  # 64KB
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk

            # Usar stream_unzip para processar o arquivo ZIP
            for file_name, file_size, unzipped_chunks in stream_unzip(zip_chunks()):
                # Converter o nome do arquivo para string se for bytes
                if isinstance(file_name, bytes):
                    file_name = file_name.decode('utf-8', errors='replace')

                # Pular diretórios vazios (terminam com '/')
                if file_name.endswith('/'):
                    # Consumir o iterador para evitar UnfinishedIterationError
                    if hasattr(unzipped_chunks, '__iter__'):
                        for _ in unzipped_chunks:
                            pass
                    elif callable(unzipped_chunks):
                        for _ in unzipped_chunks():
                            pass
                    continue

                # Verificar se o arquivo passa pelo filtro de extensões
                if not filter_by_extensions(file_name, file_extensions):
                    # Consumir o iterador para evitar UnfinishedIterationError
                    if hasattr(unzipped_chunks, '__iter__'):
                        for _ in unzipped_chunks:
                            pass
                    elif callable(unzipped_chunks):
                        for _ in unzipped_chunks():
                            pass
                    continue

                logger.debug(f"Encontrado arquivo no ZIP: {file_name}, tamanho: {file_size}")

                # Criar uma função que retorna o iterador de chunks
                # Isso permite que o chamador decida quando consumir o conteúdo
                if hasattr(unzipped_chunks, '__iter__'):
                    # Se já for um iterador, criar uma cópia
                    chunks = list(unzipped_chunks)
                    def get_content(chunks=chunks):
                        return iter(chunks)
                elif callable(unzipped_chunks):
                    # Se for uma função, retornar a função
                    get_content = unzipped_chunks
                else:
                    # Caso inesperado, criar um iterador vazio
                    def get_content():
                        return iter([])

                yield file_name, file_size, get_content

        except Exception as e:
            logger.error(f"Erro ao processar o arquivo ZIP {zip_path}: {str(e)}")
            raise
