"""
Módulo que implementa a lógica de identificação de arquivos duplicados.

Este módulo contém a classe DuplicateFinder, responsável por encontrar grupos
de arquivos duplicados a partir de um iterador de metadados de arquivos.
"""

import logging
from collections import defaultdict
from typing import Dict, Iterator, List, Callable

from fotix.domain import FileMetadata, DuplicateGroup


class DuplicateFinder:
    """
    Classe responsável por encontrar grupos de arquivos duplicados.
    
    Esta classe implementa a lógica para identificar arquivos duplicados
    baseando-se no tamanho e no hash do conteúdo dos arquivos.
    """
    
    def find_duplicates(
        self, 
        file_iterator: Iterator[FileMetadata], 
        hash_function: Callable[[FileMetadata], str]
    ) -> List[DuplicateGroup]:
        """
        Encontra grupos de arquivos duplicados a partir de um iterador de metadados.
        
        O processo de identificação de duplicatas ocorre em duas etapas:
        1. Agrupamento inicial por tamanho (arquivos com tamanhos diferentes não podem ser duplicatas)
        2. Para cada grupo de arquivos com o mesmo tamanho, cálculo do hash e agrupamento por hash
        
        Args:
            file_iterator: Um iterador que produz objetos FileMetadata
            hash_function: Uma função que recebe um FileMetadata e retorna o hash BLAKE3 do arquivo
                           correspondente, ou levanta uma exceção em caso de erro
        
        Returns:
            Uma lista de DuplicateGroup, onde cada grupo contém dois ou mais arquivos duplicados
            (mesmo tamanho e mesmo hash). A lista será vazia se nenhuma duplicata for encontrada.
        
        Raises:
            Não levanta exceções diretamente, mas a hash_function pode levantar exceções
            relacionadas a I/O (ex: OSError, PermissionError) que são capturadas internamente.
        """
        # Passo 1: Agrupamento inicial por tamanho
        files_by_size: Dict[int, List[FileMetadata]] = defaultdict(list)
        
        for file_meta in file_iterator:
            files_by_size[file_meta.size].append(file_meta)
        
        # Passo 2: Identificação e hashing de potenciais duplicatas
        result_groups: List[DuplicateGroup] = []
        
        for potential_duplicates in files_by_size.values():
            # Pré-filtragem: pula grupos com menos de 2 arquivos (não podem ser duplicatas)
            if len(potential_duplicates) < 2:
                continue
            
            # Agrupamento por hash dentro do grupo de tamanho
            hashes_in_group: Dict[str, List[FileMetadata]] = defaultdict(list)
            
            for file_meta in potential_duplicates:
                try:
                    # Cálculo do hash com tratamento de erro
                    hash_value = hash_function(file_meta)
                    hashes_in_group[hash_value].append(file_meta)
                except Exception as e:
                    # Loga um aviso e continua para o próximo arquivo
                    logging.warning(
                        f"Falha ao calcular hash para o arquivo {file_meta.path}: {str(e)}"
                    )
                    continue
            
            # Formação de grupos de duplicatas reais
            for hash_value, actual_duplicates in hashes_in_group.items():
                # Filtragem final: ignora grupos com menos de 2 arquivos
                if len(actual_duplicates) < 2:
                    continue
                
                # Cria um grupo de duplicatas
                duplicate_group = DuplicateGroup(
                    files=actual_duplicates,
                    hash_value=hash_value,
                    file_to_keep=None  # Será definido posteriormente por outro componente
                )
                
                result_groups.append(duplicate_group)
        
        return result_groups
