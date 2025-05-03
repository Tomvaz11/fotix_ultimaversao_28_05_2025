"""
Testes unitários para o módulo decision_logic.

Este módulo contém testes para verificar o comportamento da função decide_file_to_keep
em diferentes cenários, incluindo casos de sucesso, erro e borda.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from fotix.core.decision_logic import decide_file_to_keep
from fotix.domain import FileMetadata, DuplicateGroup


class TestDecisionLogic:
    """Testes para a função decide_file_to_keep."""

    def setup_method(self):
        """Configuração executada antes de cada teste."""
        # Cria mocks para FileMetadata com diferentes atributos
        self.create_test_files()

    def create_test_files(self):
        """Cria arquivos de teste com diferentes características."""
        # Arquivo com alta resolução, data recente e nome longo
        self.file1 = Mock(spec=FileMetadata)
        self.file1.path = Path("/path/to/file_with_long_name.jpg")
        self.file1.size = 1000
        self.file1.creation_time = 1600000000.0
        self.file1.resolution = (1920, 1080)
        self.file1.modification_time = 1678886400.0

        # Arquivo com alta resolução, data mais recente e nome longo
        self.file2 = Mock(spec=FileMetadata)
        self.file2.path = Path("/path/to/another_long_name.jpg")
        self.file2.size = 1000
        self.file2.creation_time = 1600001000.0
        self.file2.resolution = (1920, 1080)
        self.file2.modification_time = 1678886500.0

        # Arquivo com baixa resolução, data mais recente e nome curto
        self.file3 = Mock(spec=FileMetadata)
        self.file3.path = Path("/path/to/short.jpg")
        self.file3.size = 1000
        self.file3.creation_time = 1600002000.0
        self.file3.resolution = (800, 600)
        self.file3.modification_time = 1678886600.0

        # Arquivo sem resolução, com data antiga e nome médio
        self.file4 = Mock(spec=FileMetadata)
        self.file4.path = Path("/path/to/medium.jpg")
        self.file4.size = 1000
        self.file4.creation_time = 1600003000.0
        self.file4.resolution = None
        self.file4.modification_time = 1678886300.0

        # Arquivo com alta resolução, sem data de modificação e nome curto
        self.file5 = Mock(spec=FileMetadata)
        self.file5.path = Path("/path/to/short2.jpg")
        self.file5.size = 1000
        self.file5.creation_time = 1600004000.0
        self.file5.resolution = (1920, 1080)
        self.file5.modification_time = None

    def test_invalid_group(self):
        """Testa o comportamento com um grupo inválido."""
        # Caso: grupo None
        with pytest.raises(ValueError, match="DuplicateGroup inválido ou lista de arquivos vazia"):
            decide_file_to_keep(None)

        # Caso: grupo com files None
        group = Mock(spec=DuplicateGroup)
        group.files = None
        with pytest.raises(ValueError, match="DuplicateGroup inválido ou lista de arquivos vazia"):
            decide_file_to_keep(group)

    def test_insufficient_files(self):
        """Testa o comportamento com menos de dois arquivos."""
        # Caso: grupo com lista vazia
        group = Mock(spec=DuplicateGroup)
        group.files = []
        with pytest.raises(ValueError, match="Não é possível decidir entre menos de dois arquivos"):
            decide_file_to_keep(group)

        # Caso: grupo com apenas um arquivo
        group = Mock(spec=DuplicateGroup)
        group.files = [self.file1]
        with pytest.raises(ValueError, match="Não é possível decidir entre menos de dois arquivos"):
            decide_file_to_keep(group)

    def test_resolution_criterion(self):
        """Testa a seleção baseada no critério de resolução."""
        # Caso: um arquivo com resolução maior que os outros
        group = Mock(spec=DuplicateGroup)
        group.files = [self.file3, self.file1, self.file4]  # file1 tem a maior resolução
        
        result = decide_file_to_keep(group)
        assert result == self.file1

    def test_modification_date_criterion(self):
        """Testa a seleção baseada no critério de data de modificação."""
        # Caso: empate na resolução, desempate pela data
        group = Mock(spec=DuplicateGroup)
        group.files = [self.file1, self.file2]  # Ambos têm a mesma resolução, file2 tem data mais recente
        
        result = decide_file_to_keep(group)
        assert result == self.file2

    def test_name_length_criterion(self):
        """Testa a seleção baseada no critério de comprimento do nome."""
        # Criando arquivos com mesma resolução e data, mas nomes diferentes
        file_a = Mock(spec=FileMetadata)
        file_a.path = Path("/path/to/long_name_file.jpg")
        file_a.resolution = (1920, 1080)
        file_a.modification_time = 1678886500.0

        file_b = Mock(spec=FileMetadata)
        file_b.path = Path("/path/to/short.jpg")
        file_b.resolution = (1920, 1080)
        file_b.modification_time = 1678886500.0

        group = Mock(spec=DuplicateGroup)
        group.files = [file_a, file_b]  # Mesmo resolução e data, file_b tem nome mais curto
        
        result = decide_file_to_keep(group)
        assert result == file_b

    def test_final_tiebreaker(self):
        """Testa o desempate final quando todos os critérios empatam."""
        # Criando arquivos idênticos em todos os critérios
        file_a = Mock(spec=FileMetadata)
        file_a.path = Path("/path/to/same.jpg")
        file_a.resolution = (1920, 1080)
        file_a.modification_time = 1678886500.0

        file_b = Mock(spec=FileMetadata)
        file_b.path = Path("/path/to/same2.jpg")  # Mesmo comprimento que file_a
        file_b.resolution = (1920, 1080)
        file_b.modification_time = 1678886500.0

        group = Mock(spec=DuplicateGroup)
        group.files = [file_a, file_b]  # Empate em todos os critérios
        
        result = decide_file_to_keep(group)
        assert result == file_a  # Deve escolher o primeiro arquivo

    def test_missing_resolution(self):
        """Testa o comportamento com arquivos sem resolução."""
        # Arquivo com resolução vs arquivo sem resolução
        group = Mock(spec=DuplicateGroup)
        group.files = [self.file4, self.file3]  # file4 não tem resolução, file3 tem
        
        result = decide_file_to_keep(group)
        assert result == self.file3

    def test_missing_modification_time(self):
        """Testa o comportamento com arquivos sem data de modificação."""
        # Arquivo com data vs arquivo sem data
        group = Mock(spec=DuplicateGroup)
        group.files = [self.file5, self.file1]  # file5 não tem data, file1 tem
        
        result = decide_file_to_keep(group)
        assert result == self.file1

    def test_all_criteria_combined(self):
        """Testa um cenário completo com todos os critérios em ação."""
        # Cenário completo com vários arquivos
        group = Mock(spec=DuplicateGroup)
        group.files = [self.file1, self.file2, self.file3, self.file4, self.file5]
        
        result = decide_file_to_keep(group)
        assert result == self.file2  # Maior resolução e data mais recente
