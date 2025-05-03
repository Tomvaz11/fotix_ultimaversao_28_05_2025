"""
Módulo que implementa a lógica de decisão para selecionar arquivos a serem mantidos.

Este módulo contém funções para decidir qual arquivo deve ser mantido dentro
de um grupo de duplicatas, com base em critérios hierárquicos como resolução,
data de modificação e nome do arquivo.
"""

from typing import List, Optional, Tuple

from fotix.domain import FileMetadata, DuplicateGroup


def decide_file_to_keep(group: DuplicateGroup) -> FileMetadata:
    """
    Seleciona um arquivo para ser mantido dentro de um grupo de duplicatas.
    
    A seleção segue uma hierarquia de critérios:
    1. Maior resolução (área em pixels)
    2. Data de modificação mais recente
    3. Nome de arquivo mais curto
    
    Se houver empate em todos os critérios, o primeiro arquivo entre os empatados
    finais será selecionado.
    
    Args:
        group: Um grupo de duplicatas contendo arquivos idênticos (mesmo hash)
        
    Returns:
        O arquivo selecionado para ser mantido
        
    Raises:
        ValueError: Se o grupo for inválido ou contiver menos de dois arquivos
    """
    # Validação inicial
    if group is None or group.files is None:
        raise ValueError("DuplicateGroup inválido ou lista de arquivos vazia.")
    
    if len(group.files) < 2:
        raise ValueError("Não é possível decidir entre menos de dois arquivos.")
    
    # Aplicação dos critérios hierárquicos
    # 1. Critério de resolução
    files_by_resolution = _filter_by_resolution(group.files)
    if len(files_by_resolution) == 1:
        return files_by_resolution[0]
    
    # 2. Critério de data de modificação
    files_by_date = _filter_by_modification_date(files_by_resolution)
    if len(files_by_date) == 1:
        return files_by_date[0]
    
    # 3. Critério de nome mais curto
    files_by_name_length = _filter_by_name_length(files_by_date)
    
    # Retorna o primeiro arquivo entre os empatados finais
    return files_by_name_length[0]


def _filter_by_resolution(files: List[FileMetadata]) -> List[FileMetadata]:
    """
    Filtra os arquivos pelo critério de maior resolução.
    
    Args:
        files: Lista de arquivos a serem filtrados
        
    Returns:
        Lista contendo apenas os arquivos com a maior resolução
    """
    # Calcula a área de resolução para cada arquivo
    # Arquivos sem resolução recebem área 0 (menor prioridade)
    files_with_area = []
    max_area = 0
    
    for file in files:
        # Assume que FileMetadata tem um atributo ou método para acessar a resolução
        # Se não tiver, considera como None (sem resolução)
        resolution = getattr(file, 'resolution', None)
        
        area = 0
        if resolution is not None and isinstance(resolution, tuple) and len(resolution) >= 2:
            width, height = resolution
            if isinstance(width, int) and isinstance(height, int):
                area = width * height
        
        files_with_area.append((file, area))
        max_area = max(max_area, area)
    
    # Filtra apenas os arquivos com a maior área
    return [file for file, area in files_with_area if area == max_area]


def _filter_by_modification_date(files: List[FileMetadata]) -> List[FileMetadata]:
    """
    Filtra os arquivos pelo critério de data de modificação mais recente.
    
    Args:
        files: Lista de arquivos a serem filtrados
        
    Returns:
        Lista contendo apenas os arquivos com a data de modificação mais recente
    """
    # Obtém a data de modificação para cada arquivo
    # Arquivos sem data recebem 0 (menor prioridade)
    files_with_date = []
    max_date = 0.0
    
    for file in files:
        # Assume que FileMetadata tem um atributo ou método para acessar a data de modificação
        # Se não tiver, considera como 0 (data mais antiga possível)
        modification_time = getattr(file, 'modification_time', 0.0)
        
        if not isinstance(modification_time, (int, float)):
            modification_time = 0.0
        
        files_with_date.append((file, modification_time))
        max_date = max(max_date, modification_time)
    
    # Filtra apenas os arquivos com a data mais recente
    return [file for file, date in files_with_date if date == max_date]


def _filter_by_name_length(files: List[FileMetadata]) -> List[FileMetadata]:
    """
    Filtra os arquivos pelo critério de nome mais curto.
    
    Args:
        files: Lista de arquivos a serem filtrados
        
    Returns:
        Lista contendo apenas os arquivos com o nome mais curto
    """
    # Calcula o comprimento do nome para cada arquivo
    files_with_name_length = []
    min_length = float('inf')
    
    for file in files:
        name_length = len(file.path.name)
        files_with_name_length.append((file, name_length))
        min_length = min(min_length, name_length)
    
    # Filtra apenas os arquivos com o nome mais curto
    return [file for file, length in files_with_name_length if length == min_length]
