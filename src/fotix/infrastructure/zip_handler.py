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
            logger.debug(f"[ZipHandlerService] Iniciando streaming do arquivo ZIP: {zip_path}")

            # Função para ler o arquivo ZIP em blocos
            def zip_chunks():
                with open(zip_path, 'rb') as f:
                    while True:
                        chunk = f.read(65536)  # 64KB chunks
                        if not chunk:
                            break
                        yield chunk

            # Processar o arquivo ZIP usando stream_unzip
            processed_any_entry = False
            # Lista para armazenar temporariamente as entradas processadas antes de fazer o yield
            collected_entries = []

            for file_name_bytes, file_size, unzipped_chunks_fn in stream_unzip(zip_chunks()):
                processed_any_entry = True
                # Converter o nome do arquivo de bytes para string
                file_name = file_name_bytes.decode('utf-8', errors='replace')
                logger.debug(f"[ZipHandlerService] Entrada no ZIP: {file_name}, Tamanho: {file_size}")

                # CRUCIAL: Consumir os chunks da entrada atual IMEDIATAMENTE
                # e calcular o tamanho real a partir dos chunks.
                current_file_chunks = []
                calculated_size = 0
                try:
                    for chunk in unzipped_chunks_fn:
                        current_file_chunks.append(chunk)
                        calculated_size += len(chunk)
                except Exception as e:
                    logger.error(f"[ZipHandlerService] Erro ao consumir chunks para {file_name} no ZIP {zip_path}: {repr(e)}", exc_info=True)
                    # Pular esta entrada do ZIP se houver erro ao ler seus chunks
                    continue 
                
                # Determinar o tamanho a ser reportado
                reported_size = 0
                if file_size is None:
                    logger.debug(f"[ZipHandlerService] Tamanho original de stream-unzip para '{file_name}' era None. Usando tamanho calculado: {calculated_size}")
                    reported_size = calculated_size
                elif file_size == 0 and calculated_size > 0 and not file_name.endswith('/'): # Provavelmente um arquivo, não diretório, mas stream-unzip disse 0
                    logger.warning(f"[ZipHandlerService] Tamanho de stream-unzip para '{file_name}' era 0 mas calculado foi {calculated_size}. Usando calculado.")
                    reported_size = calculated_size
                elif file_size != calculated_size and not file_name.endswith('/'): # Não é diretório, mas tamanhos divergem
                    logger.warning(f"[ZipHandlerService] Tamanho de stream-unzip ({file_size}) para '{file_name}' difere do calculado ({calculated_size}). Usando calculado como mais confiável.")
                    reported_size = calculated_size
                else: # Tamanhos conferem, ou é um diretório (file_size 0 é ok), ou file_size não era None e confere
                    reported_size = file_size

                # Verificar se o arquivo deve ser incluído com base na extensão
                if should_include_file(file_name):
                    logger.debug(f"[ZipHandlerService] INCLUINDO arquivo do ZIP: {file_name}")

                    # Criar uma função que retorna o iterador de conteúdo a partir dos chunks já lidos
                    # É importante que cada content_fn tenha sua própria cópia dos chunks
                    # ou uma referência aos chunks corretos.
                    def create_closure_content_fn(chunks_for_file):
                        def content_provider():
                            for chunk in chunks_for_file:
                                yield chunk
                        return content_provider

                    # Adicionar à lista para fazer yield depois que o loop stream_unzip terminar
                    collected_entries.append(
                        (file_name, reported_size, create_closure_content_fn(current_file_chunks))
                    )
                else:
                    # Se o arquivo não deve ser incluído, os current_file_chunks já foram lidos e podem ser descartados.
                    logger.debug(f"[ZipHandlerService] IGNORANDO arquivo no ZIP (extensão não correspondente): {file_name}")
            
            if not processed_any_entry:
                logger.warning(f"[ZipHandlerService] Nenhum arquivo encontrado dentro do ZIP: {zip_path}. O ZIP pode estar vazio ou corrompido.")

            # Agora, fazer o yield das entradas coletadas DEPOIS que o loop stream_unzip foi concluído
            for entry in collected_entries:
                yield entry

        except NotStreamUnzippable as e:
            logger.error(f"[ZipHandlerService] O arquivo ZIP não pode ser processado em streaming: {zip_path}. Erro: {str(e)}, Repr: {repr(e)}", exc_info=True)
            raise
        except UnzipError as e:
            logger.error(f"[ZipHandlerService] Erro ao processar o arquivo ZIP: {zip_path}. Erro: {str(e)}, Repr: {repr(e)}", exc_info=True)
            raise ValueError(f"Erro ao processar o arquivo ZIP: {str(e)}")
        except PermissionError as e:
            logger.error(f"[ZipHandlerService] Sem permissão para ler o arquivo ZIP: {zip_path}. Erro: {str(e)}, Repr: {repr(e)}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"[ZipHandlerService] Erro inesperado ao processar o arquivo ZIP {zip_path}: {str(e)}, Repr: {repr(e)}", exc_info=True)
            raise

    def extract_all_to_directory(self, zip_path: Path, target_directory: Path) -> List[Path]:
        """
        Extrai todo o conteúdo de um arquivo ZIP para um diretório de destino.

        Args:
            zip_path: Caminho para o arquivo ZIP.
            target_directory: Caminho para o diretório onde o conteúdo será extraído.
        
        Returns:
            List[Path]: Lista dos caminhos completos para os arquivos e diretórios extraídos.

        Raises:
            FileNotFoundError: Se o arquivo ZIP não existir.
            ValueError: Se o arquivo não for um ZIP válido ou se o diretório de destino não puder ser criado.
            Exception: Outras exceções relacionadas a IO podem ser levantadas.
        """
        if not zip_path.exists() or not zip_path.is_file():
            raise FileNotFoundError(f"Arquivo ZIP não encontrado ou não é um arquivo: {zip_path}")

        if not target_directory.exists():
            try:
                target_directory.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"Não foi possível criar o diretório de destino {target_directory}: {e}")
                raise ValueError(f"Não foi possível criar o diretório de destino {target_directory}: {e}")
        elif not target_directory.is_dir():
            raise ValueError(f"O caminho de destino especificado não é um diretório: {target_directory}")

        logger.info(f"Extraindo todo o conteúdo de {zip_path} para {target_directory}")
        extracted_paths: List[Path] = []

        try:
            # Usar stream_zip_entries para obter os nomes dos arquivos e os chunks de conteúdo
            # O file_extensions=None garante que tudo seja processado
            for internal_name, _, content_provider_fn in self.stream_zip_entries(zip_path, file_extensions=None):
                # Construir o caminho completo de destino
                # Lidar com nomes de arquivo que podem conter barras (subdiretórios no ZIP)
                # Assegurar que o caminho seja relativo ao target_directory e seguro
                # os.path.normpath para normalizar (e.g. remover ../)
                # No entanto, Path já faz um bom trabalho com isso ao juntar.
                
                # Sanitizar internal_name para evitar problemas de path traversal se necessário,
                # mas Path() geralmente lida bem com caminhos relativos.
                # Para maior segurança, pode-se verificar se internal_name começa com / ou ..
                # No contexto de stream_unzip, internal_name é geralmente seguro.

                # Converter barras do ZIP (geralmente /) para o separador do OS
                normalized_internal_name = internal_name.replace("/", os.sep).replace("\\", os.sep)
                # Remover possível separador no início se houver, para Path não tratar como absoluto
                if normalized_internal_name.startswith(os.sep):
                    normalized_internal_name = normalized_internal_name[len(os.sep):]

                destination_path = target_directory / normalized_internal_name
                extracted_paths.append(destination_path)

                if internal_name.endswith('/'): # É um diretório dentro do ZIP
                    destination_path.mkdir(parents=True, exist_ok=True)
                    logger.debug(f"Diretório criado/verificado em {destination_path} (de {internal_name} no ZIP)")
                else: # É um arquivo dentro do ZIP
                    # Garantir que o diretório pai do arquivo exista
                    destination_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    logger.debug(f"Extraindo {internal_name} para {destination_path}")
                    with open(destination_path, 'wb') as outfile:
                        for chunk in content_provider_fn():
                            outfile.write(chunk)
            
            logger.info(f"Extração de {zip_path} concluída. {len(extracted_paths)} entradas processadas.")
            return extracted_paths
        
        except Exception as e:
            logger.error(f"Erro durante a extração de {zip_path} para {target_directory}: {repr(e)}", exc_info=True)
            # Limpar arquivos parcialmente extraídos em caso de erro?
            # Por agora, apenas relançamos a exceção.
            raise
