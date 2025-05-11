"""
Implementação do serviço de manipulação de arquivos ZIP para o Fotix.

Este módulo implementa a interface IZipHandlerService, fornecendo métodos
para acessar o conteúdo de arquivos ZIP de forma eficiente (streaming),
sem extrair todo o conteúdo para o disco.
"""

import os
from pathlib import Path
from typing import Iterable, Optional, Tuple, Callable, List

from stream_unzip import stream_unzip, UnzipError, NotStreamUnzippable

from fotix.infrastructure.interfaces import IZipHandlerService
from fotix.infrastructure.logging_config import get_logger

# Obter logger para este módulo
logger = get_logger(__name__)


class ZipHandlerService(IZipHandlerService):
    """
    Implementação do serviço de manipulação de arquivos ZIP usando stream-unzip.

    Esta classe implementa a interface IZipHandlerService, fornecendo métodos
    para acessar o conteúdo de arquivos ZIP de forma eficiente (streaming),
    sem extrair todo o conteúdo para o disco.
    """

    def stream_zip_entries(self, zip_path: Path,
                          file_extensions: Optional[List[str]] = None) -> Iterable[Tuple[str, int, Callable[[], Iterable[bytes]]]]:
        """
        Retorna um iterador/gerador para os arquivos dentro de um ZIP.

        Args:
            zip_path: Caminho para o arquivo ZIP.
            file_extensions: Lista opcional de extensões de arquivo para filtrar.
                            Se None, todos os arquivos são incluídos.
                            Exemplo: ['.jpg', '.png']

        Returns:
            Iterable[Tuple[str, int, Callable[[], Iterable[bytes]]]]: Iterador/gerador onde cada item é uma tupla contendo:
                - nome do arquivo dentro do zip (str)
                - tamanho do arquivo em bytes (int)
                - uma função lazy que retorna um iterador/gerador para o conteúdo do arquivo em blocos (Callable[[], Iterable[bytes]])

        Raises:
            FileNotFoundError: Se o arquivo ZIP não existir.
            PermissionError: Se não houver permissão para ler o arquivo ZIP.
            ValueError: Se o arquivo não for um ZIP válido.
            NotStreamUnzippable: Se o arquivo ZIP não puder ser processado em streaming.
            Exception: Outras exceções relacionadas a IO ou formato podem ser levantadas.

        Note:
            Esta implementação é eficiente para arquivos ZIP grandes, pois não extrai
            todo o conteúdo para o disco ou memória de uma vez. O conteúdo de cada
            arquivo é acessado apenas quando a função lazy é chamada e iterada.

            A função lazy retornada deve ser iterada até o final para cada arquivo
            antes de passar para o próximo, ou uma exceção pode ser levantada.
        """
        # Verificar se o arquivo existe
        if not zip_path.exists():
            logger.error(f"Arquivo ZIP não encontrado: {zip_path}")
            raise FileNotFoundError(f"Arquivo ZIP não encontrado: {zip_path}")

        # Verificar se é um arquivo (não um diretório)
        if not zip_path.is_file():
            logger.error(f"O caminho não é um arquivo: {zip_path}")
            raise ValueError(f"O caminho não é um arquivo: {zip_path}")

        # Normalizar extensões para comparação (converter para minúsculas)
        normalized_extensions = None
        if file_extensions:
            normalized_extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in file_extensions]

        # Função para verificar se um arquivo deve ser incluído com base na extensão
        def should_include_file(file_name: str) -> bool:
            if not normalized_extensions:
                return True
            # Extrair a extensão do nome do arquivo
            _, ext = os.path.splitext(file_name)
            return ext.lower() in normalized_extensions

        try:
            logger.debug(f"Iniciando streaming do arquivo ZIP: {zip_path}")

            # Função para ler o arquivo ZIP em blocos
            def zip_chunks():
                with open(zip_path, 'rb') as f:
                    while True:
                        chunk = f.read(65536)  # 64KB chunks
                        if not chunk:
                            break
                        yield chunk

            # Processar o arquivo ZIP usando stream_unzip
            for file_name_bytes, file_size, unzipped_chunks_fn in stream_unzip(zip_chunks()):
                # Converter o nome do arquivo de bytes para string
                file_name = file_name_bytes.decode('utf-8', errors='replace')

                # Verificar se o arquivo deve ser incluído com base na extensão
                if should_include_file(file_name):
                    logger.debug(f"Encontrado arquivo no ZIP: {file_name}, tamanho: {file_size or 'desconhecido'}")

                    # Criar uma função que retorna o iterador de conteúdo
                    # Precisamos criar uma cópia do gerador para cada arquivo
                    # já que o gerador original só pode ser consumido uma vez
                    def content_fn():
                        # Consumir o gerador completamente
                        chunks = list(unzipped_chunks_fn)
                        for chunk in chunks:
                            yield chunk

                    yield file_name, file_size or 0, content_fn
                else:
                    # Se o arquivo não deve ser incluído, ainda precisamos iterar sobre seu conteúdo
                    # para evitar UnfinishedIterationError
                    logger.debug(f"Ignorando arquivo no ZIP (extensão não correspondente): {file_name}")
                    # Consumir o gerador completamente
                    for _ in unzipped_chunks_fn:
                        pass

        except NotStreamUnzippable as e:
            logger.error(f"O arquivo ZIP não pode ser processado em streaming: {zip_path}. Erro: {str(e)}")
            raise
        except UnzipError as e:
            logger.error(f"Erro ao processar o arquivo ZIP: {zip_path}. Erro: {str(e)}")
            raise ValueError(f"Erro ao processar o arquivo ZIP: {str(e)}")
        except PermissionError as e:
            logger.error(f"Sem permissão para ler o arquivo ZIP: {zip_path}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao processar o arquivo ZIP {zip_path}: {str(e)}")
            raise
