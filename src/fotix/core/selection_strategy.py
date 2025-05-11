"""
Estratégias de seleção de arquivos duplicados para o Fotix.

Este módulo implementa a interface ISelectionStrategy, fornecendo diferentes
estratégias para selecionar automaticamente qual arquivo manter de um conjunto
de duplicatas, com base em critérios como data, resolução ou nome.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Dict, Any, Type, Callable

from fotix.core.interfaces import ISelectionStrategy
from fotix.core.models import DuplicateSet, FileInfo
from fotix.infrastructure.interfaces import IFileSystemService
from fotix.infrastructure.logging_config import get_logger
from fotix.utils.helpers import measure_time
from fotix.utils.image_utils import (
    get_image_resolution,
    get_image_resolution_from_bytes,
    is_image_file,
    calculate_image_quality
)

# Obter logger para este módulo
logger = get_logger(__name__)


class BaseSelectionStrategy(ISelectionStrategy, ABC):
    """
    Classe base abstrata para estratégias de seleção de arquivos duplicados.

    Implementa a interface ISelectionStrategy e define métodos comuns
    para todas as estratégias concretas.
    """

    def __init__(self, file_system_service: Optional[IFileSystemService] = None):
        """
        Inicializa a estratégia de seleção.

        Args:
            file_system_service: Serviço opcional para acessar o sistema de arquivos.
                                Necessário para algumas estratégias que precisam
                                acessar o conteúdo dos arquivos.
        """
        self.file_system_service = file_system_service

    @measure_time
    def select_file_to_keep(self, duplicate_set: DuplicateSet) -> FileInfo:
        """
        Recebe um conjunto de arquivos duplicados e retorna o arquivo que deve ser mantido.

        Args:
            duplicate_set: Conjunto de arquivos duplicados.

        Returns:
            FileInfo: O arquivo que deve ser mantido com base nos critérios da estratégia.

        Raises:
            ValueError: Se o conjunto de duplicatas estiver vazio.
        """
        if not duplicate_set.files:
            raise ValueError("O conjunto de duplicatas está vazio")

        if len(duplicate_set.files) == 1:
            # Se só há um arquivo, retorná-lo diretamente
            logger.debug(f"Apenas um arquivo no conjunto, retornando: {duplicate_set.files[0].path}")
            return duplicate_set.files[0]

        # Delegar para a implementação específica da estratégia
        selected_file = self._select_file(duplicate_set)
        logger.info(f"Arquivo selecionado para manter: {selected_file.path}")

        return selected_file

    @abstractmethod
    def _select_file(self, duplicate_set: DuplicateSet) -> FileInfo:
        """
        Método abstrato que deve ser implementado pelas subclasses.

        Args:
            duplicate_set: Conjunto de arquivos duplicados.

        Returns:
            FileInfo: O arquivo selecionado para ser mantido.
        """
        pass

    @property
    def name(self) -> str:
        """
        Retorna o nome da estratégia.

        Returns:
            str: Nome da estratégia.
        """
        return self.__class__.__name__


class CreationDateStrategy(BaseSelectionStrategy):
    """
    Estratégia que seleciona o arquivo mais antigo com base na data de criação.

    Esta estratégia é útil quando se deseja manter o arquivo original e
    descartar cópias posteriores.
    """

    def _select_file(self, duplicate_set: DuplicateSet) -> FileInfo:
        """
        Seleciona o arquivo com a data de criação mais antiga.

        Args:
            duplicate_set: Conjunto de arquivos duplicados.

        Returns:
            FileInfo: O arquivo mais antigo do conjunto.
        """
        # Filtrar arquivos que têm data de criação definida
        files_with_creation_time = [f for f in duplicate_set.files if f.creation_time is not None]

        if not files_with_creation_time:
            logger.warning("Nenhum arquivo com data de criação definida, usando o primeiro arquivo")
            return duplicate_set.files[0]

        # Ordenar por data de criação (mais antigo primeiro)
        oldest_file = min(files_with_creation_time, key=lambda f: f.creation_time)
        logger.debug(f"Arquivo mais antigo: {oldest_file.path} ({oldest_file.creation_datetime})")

        return oldest_file


class ModificationDateStrategy(BaseSelectionStrategy):
    """
    Estratégia que seleciona o arquivo mais recente com base na data de modificação.

    Esta estratégia é útil quando se deseja manter a versão mais recente de um arquivo.
    """

    def _select_file(self, duplicate_set: DuplicateSet) -> FileInfo:
        """
        Seleciona o arquivo com a data de modificação mais recente.

        Args:
            duplicate_set: Conjunto de arquivos duplicados.

        Returns:
            FileInfo: O arquivo mais recente do conjunto.
        """
        # Filtrar arquivos que têm data de modificação definida
        files_with_modification_time = [f for f in duplicate_set.files if f.modification_time is not None]

        if not files_with_modification_time:
            logger.warning("Nenhum arquivo com data de modificação definida, usando o primeiro arquivo")
            return duplicate_set.files[0]

        # Ordenar por data de modificação (mais recente primeiro)
        newest_file = max(files_with_modification_time, key=lambda f: f.modification_time)
        logger.debug(f"Arquivo mais recente: {newest_file.path} ({newest_file.modification_datetime})")

        return newest_file


class HighestResolutionStrategy(BaseSelectionStrategy):
    """
    Estratégia que seleciona a imagem com a maior resolução.

    Esta estratégia é útil para arquivos de imagem, onde a resolução
    é um indicador de qualidade. Para arquivos que não são imagens,
    usa uma estratégia de fallback.
    """

    def __init__(self, file_system_service: Optional[IFileSystemService] = None,
                fallback_strategy: Optional[BaseSelectionStrategy] = None):
        """
        Inicializa a estratégia de seleção por resolução.

        Args:
            file_system_service: Serviço para acessar o sistema de arquivos.
                                Necessário para ler o conteúdo das imagens.
            fallback_strategy: Estratégia alternativa para arquivos que não são imagens.
                              Se None, usa o primeiro arquivo do conjunto.
        """
        super().__init__(file_system_service)
        self.fallback_strategy = fallback_strategy

    def _select_file(self, duplicate_set: DuplicateSet) -> FileInfo:
        """
        Seleciona a imagem com a maior resolução.

        Args:
            duplicate_set: Conjunto de arquivos duplicados.

        Returns:
            FileInfo: A imagem com a maior resolução ou o resultado da estratégia de fallback.
        """
        # Verificar se os arquivos são imagens
        image_files = [f for f in duplicate_set.files if is_image_file(f.path)]

        if not image_files:
            logger.debug("Nenhum arquivo de imagem encontrado no conjunto")
            if self.fallback_strategy:
                logger.debug(f"Usando estratégia de fallback: {self.fallback_strategy.name}")
                return self.fallback_strategy._select_file(duplicate_set)
            return duplicate_set.files[0]

        # Calcular a resolução para cada imagem
        image_qualities = []

        for file_info in image_files:
            resolution = None

            if file_info.in_zip and file_info.content_provider:
                # Imagem dentro de um ZIP
                resolution = get_image_resolution_from_bytes(file_info.content_provider)
            elif self.file_system_service and not file_info.in_zip:
                # Imagem normal no sistema de arquivos
                resolution = get_image_resolution(file_info.path)

            if resolution:
                quality = calculate_image_quality(resolution)
                image_qualities.append((file_info, quality))
                logger.debug(f"Qualidade da imagem {file_info.path}: {quality} ({resolution})")

        if not image_qualities:
            logger.warning("Não foi possível determinar a resolução de nenhuma imagem")
            if self.fallback_strategy:
                logger.debug(f"Usando estratégia de fallback: {self.fallback_strategy.name}")
                return self.fallback_strategy._select_file(duplicate_set)
            return image_files[0]

        # Selecionar a imagem com a maior qualidade
        best_image = max(image_qualities, key=lambda x: x[1])[0]
        logger.debug(f"Imagem com maior resolução: {best_image.path}")

        return best_image


class ShortestNameStrategy(BaseSelectionStrategy):
    """
    Estratégia que seleciona o arquivo com o nome mais curto.

    Esta estratégia é útil quando os arquivos originais tendem a ter
    nomes mais curtos, enquanto as cópias têm sufixos adicionais.
    """

    def _select_file(self, duplicate_set: DuplicateSet) -> FileInfo:
        """
        Seleciona o arquivo com o nome mais curto.

        Args:
            duplicate_set: Conjunto de arquivos duplicados.

        Returns:
            FileInfo: O arquivo com o nome mais curto.
        """
        # Ordenar por comprimento do nome do arquivo (mais curto primeiro)
        shortest_name_file = min(duplicate_set.files, key=lambda f: len(f.filename))
        logger.debug(f"Arquivo com nome mais curto: {shortest_name_file.path}")

        return shortest_name_file


class CompositeStrategy(BaseSelectionStrategy):
    """
    Estratégia que combina várias estratégias em ordem de prioridade.

    Esta estratégia tenta aplicar cada estratégia na ordem especificada,
    até que uma delas retorne um resultado único. Se várias estratégias
    retornarem o mesmo resultado, a próxima estratégia é aplicada aos
    arquivos restantes.
    """

    def __init__(self, strategies: List[BaseSelectionStrategy]):
        """
        Inicializa a estratégia composta.

        Args:
            strategies: Lista de estratégias a serem aplicadas em ordem.

        Raises:
            ValueError: Se a lista de estratégias estiver vazia.
        """
        super().__init__()
        if not strategies:
            raise ValueError("A lista de estratégias não pode estar vazia")
        self.strategies = strategies

    def _select_file(self, duplicate_set: DuplicateSet) -> FileInfo:
        """
        Aplica várias estratégias em sequência para selecionar um arquivo.

        Args:
            duplicate_set: Conjunto de arquivos duplicados.

        Returns:
            FileInfo: O arquivo selecionado após aplicar todas as estratégias.
        """
        remaining_files = duplicate_set.files.copy()

        for strategy in self.strategies:
            if len(remaining_files) == 1:
                return remaining_files[0]

            # Criar um conjunto temporário com os arquivos restantes
            temp_set = DuplicateSet(files=remaining_files, hash=duplicate_set.hash)

            # Aplicar a estratégia atual
            selected = strategy._select_file(temp_set)
            logger.debug(f"Estratégia {strategy.name} selecionou: {selected.path}")

            # Se ainda houver mais de um arquivo, continuar com a próxima estratégia
            if len(remaining_files) > 1:
                remaining_files = [selected]

        # Retornar o único arquivo restante após aplicar todas as estratégias
        return remaining_files[0]


def create_strategy(strategy_type: str, file_system_service: Optional[IFileSystemService] = None) -> ISelectionStrategy:
    """
    Cria uma estratégia de seleção com base no tipo especificado.

    Args:
        strategy_type: Tipo de estratégia a ser criada.
                      Valores válidos: 'creation_date', 'modification_date',
                      'highest_resolution', 'shortest_name', 'composite'.
        file_system_service: Serviço para acessar o sistema de arquivos.
                            Necessário para algumas estratégias.

    Returns:
        ISelectionStrategy: A estratégia de seleção criada.

    Raises:
        ValueError: Se o tipo de estratégia for desconhecido.
    """
    if strategy_type == 'creation_date':
        return CreationDateStrategy(file_system_service)
    elif strategy_type == 'modification_date':
        return ModificationDateStrategy(file_system_service)
    elif strategy_type == 'highest_resolution':
        # Usar ModificationDateStrategy como fallback para arquivos que não são imagens
        fallback = ModificationDateStrategy(file_system_service)
        return HighestResolutionStrategy(file_system_service, fallback)
    elif strategy_type == 'shortest_name':
        return ShortestNameStrategy(file_system_service)
    elif strategy_type == 'composite':
        # Estratégia composta padrão: resolução > data de modificação > nome mais curto
        strategies = [
            HighestResolutionStrategy(file_system_service),
            ModificationDateStrategy(file_system_service),
            ShortestNameStrategy(file_system_service)
        ]
        return CompositeStrategy(strategies)
    else:
        raise ValueError(f"Tipo de estratégia desconhecido: {strategy_type}")
