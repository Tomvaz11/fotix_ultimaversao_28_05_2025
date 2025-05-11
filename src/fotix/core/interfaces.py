"""
Interfaces para os serviços da camada de domínio (core) do Fotix.

Este módulo define os contratos (interfaces) para os serviços da camada de domínio,
como detecção de duplicatas e estratégias de seleção. Estas interfaces permitem que
as camadas superiores (aplicação) dependam de abstrações em vez de implementações
concretas, facilitando testes e manutenção.
"""

from pathlib import Path
from typing import Callable, List, Optional, Protocol

from fotix.core.models import DuplicateSet, FileInfo


class IDuplicateFinderService(Protocol):
    """
    Interface para o serviço de detecção de duplicatas.
    
    Esta interface define como encontrar conjuntos de arquivos duplicados
    em diretórios e arquivos ZIP. Implementações concretas devem lidar com
    os detalhes específicos de hashing e comparação de arquivos.
    """
    
    def find_duplicates(self, scan_paths: List[Path], include_zips: bool, 
                       progress_callback: Optional[Callable[[float], None]] = None) -> List[DuplicateSet]:
        """
        Analisa os caminhos fornecidos e retorna uma lista de conjuntos de arquivos duplicados.
        
        Args:
            scan_paths: Lista de caminhos (diretórios e/ou arquivos) a serem analisados.
            include_zips: Se True, também analisa o conteúdo de arquivos ZIP encontrados.
            progress_callback: Função opcional para reportar o progresso (0.0 a 1.0).
                              Útil para atualizar uma barra de progresso na UI.
        
        Returns:
            List[DuplicateSet]: Lista de conjuntos de arquivos duplicados encontrados.
                               Cada conjunto contém arquivos com o mesmo conteúdo (hash).
        
        Note:
            Esta operação pode ser demorada para grandes quantidades de arquivos.
            O callback de progresso permite que a UI se mantenha responsiva e
            informe o usuário sobre o andamento do processo.
        """
        ...


class ISelectionStrategy(Protocol):
    """
    Interface para estratégias de seleção de arquivos duplicados.
    
    Esta interface define como selecionar qual arquivo manter de um conjunto
    de duplicatas. Diferentes implementações podem usar critérios distintos,
    como data de criação, resolução de imagem ou nome do arquivo.
    """
    
    def select_file_to_keep(self, duplicate_set: DuplicateSet) -> FileInfo:
        """
        Recebe um conjunto de arquivos duplicados e retorna o arquivo que deve ser mantido.
        
        Args:
            duplicate_set: Conjunto de arquivos duplicados.
        
        Returns:
            FileInfo: O arquivo que deve ser mantido com base nos critérios da estratégia.
        
        Note:
            Esta função não modifica o sistema de arquivos, apenas seleciona
            qual arquivo deve ser mantido. A remoção efetiva dos outros arquivos
            é responsabilidade de outro componente.
        """
        ...
