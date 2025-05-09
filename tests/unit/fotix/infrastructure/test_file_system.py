"""
Testes unitários para o módulo file_system.

Este módulo contém testes unitários para o FileSystemService que implementa
a interface IFileSystemService, verificando todas as operações de sistema de arquivos.
"""

import os
import time
import shutil
import tempfile
from pathlib import Path
from unittest import mock
import pytest

from fotix.infrastructure.file_system import FileSystemService
from fotix.infrastructure.interfaces import IFileSystemService


class TestFileSystemService:
    """Testes para o serviço FileSystemService."""

    @pytest.fixture
    def fs_service(self):
        """Fixture que fornece uma instância do FileSystemService."""
        return FileSystemService()

    @pytest.fixture
    def temp_dir(self):
        """Fixture que cria um diretório temporário para os testes."""
        # Cria um diretório temporário que será automaticamente removido após os testes
        temp_dir_path = Path(tempfile.mkdtemp())
        yield temp_dir_path
        # Cleanup: remove o diretório temporário e seu conteúdo após os testes
        if temp_dir_path.exists():
            shutil.rmtree(temp_dir_path)

    @pytest.fixture
    def temp_file(self, temp_dir):
        """Fixture que cria um arquivo temporário para os testes."""
        # Cria um arquivo de teste dentro do diretório temporário
        file_path = temp_dir / "test_file.txt"
        with open(file_path, "w") as f:
            f.write("Conteúdo de teste para o arquivo")
        return file_path

    @pytest.fixture
    def nested_dir_structure(self, temp_dir):
        """Fixture que cria uma estrutura de diretórios aninhados com diversos arquivos para testes."""
        # Cria uma estrutura com subdiretórios e arquivos
        subdirs = ["subdir1", "subdir2", "subdir1/nested"]
        files = {
            "file1.txt": "Conteúdo do arquivo 1",
            "file2.jpg": "Conteúdo do arquivo 2",
            "subdir1/file3.png": "Conteúdo do arquivo 3",
            "subdir2/file4.txt": "Conteúdo do arquivo 4",
            "subdir1/nested/file5.jpg": "Conteúdo do arquivo 5"
        }

        # Cria os subdiretórios
        for subdir in subdirs:
            (temp_dir / subdir).mkdir(parents=True, exist_ok=True)

        # Cria os arquivos com seus conteúdos
        for file_path, content in files.items():
            full_path = temp_dir / file_path
            with open(full_path, "w") as f:
                f.write(content)

        return temp_dir

    def test_protocol_compliance(self, fs_service):
        """Testa se FileSystemService implementa corretamente a interface IFileSystemService."""
        assert isinstance(fs_service, IFileSystemService)

    def test_get_file_size_existing_file(self, fs_service, temp_file):
        """Testa obter o tamanho de um arquivo existente."""
        size = fs_service.get_file_size(temp_file)
        assert size is not None
        assert size > 0
        # Obter o tamanho real do arquivo diretamente
        real_size = temp_file.stat().st_size
        assert size == real_size

    def test_get_file_size_nonexistent_file(self, fs_service, temp_dir):
        """Testa obter o tamanho de um arquivo inexistente."""
        nonexistent_file = temp_dir / "nonexistent.txt"
        size = fs_service.get_file_size(nonexistent_file)
        assert size is None

    def test_get_file_size_directory(self, fs_service, temp_dir):
        """Testa obter o tamanho de um diretório (deve retornar None)."""
        size = fs_service.get_file_size(temp_dir)
        assert size is None

    def test_stream_file_content(self, fs_service, temp_file):
        """Testa a leitura de conteúdo de arquivo em chunks."""
        content = b""
        for chunk in fs_service.stream_file_content(temp_file, chunk_size=5):
            assert isinstance(chunk, bytes)
            content += chunk

        # Ler o conteúdo diretamente para comparação
        with open(temp_file, "rb") as f:
            expected_content = f.read()
        
        assert content == expected_content

    def test_stream_file_content_nonexistent_file(self, fs_service, temp_dir):
        """Testa a exceção ao tentar ler um arquivo inexistente."""
        nonexistent_file = temp_dir / "nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            # Tenta ler um arquivo que não existe, deve lançar FileNotFoundError
            list(fs_service.stream_file_content(nonexistent_file))

    def test_list_directory_contents_recursive(self, fs_service, nested_dir_structure):
        """Testa a listagem recursiva de diretórios."""
        files = list(fs_service.list_directory_contents(nested_dir_structure, recursive=True))
        
        # Verifica se todos os arquivos e diretórios foram encontrados
        expected_count = 8  # 5 arquivos + 3 diretórios
        assert len(files) == expected_count

        # Verifica alguns arquivos específicos
        file_paths = [str(f.relative_to(nested_dir_structure)) for f in files if f.is_file()]
        assert "file1.txt" in file_paths
        
        # Usar Path para lidar com diferentes separadores de caminhos em diferentes SOs
        subdir1_file3 = str(Path("subdir1") / "file3.png")
        assert subdir1_file3 in file_paths
        
        subdir1_nested_file5 = str(Path("subdir1") / "nested" / "file5.jpg")
        assert subdir1_nested_file5 in file_paths

    def test_list_directory_contents_non_recursive(self, fs_service, nested_dir_structure):
        """Testa a listagem não recursiva de diretórios."""
        files = list(fs_service.list_directory_contents(nested_dir_structure, recursive=False))
        
        # Verifica se apenas os arquivos e diretórios no nível superior foram encontrados
        expected_count = 4  # 2 arquivos (file1.txt, file2.jpg) + 2 diretórios (subdir1, subdir2)
        assert len(files) == expected_count

        # Verifica alguns arquivos específicos
        file_paths = [str(f.relative_to(nested_dir_structure)) for f in files if f.is_file()]
        assert "file1.txt" in file_paths
        assert "file2.jpg" in file_paths
        assert "subdir1/file3.png" not in file_paths  # Este arquivo está em um subdiretório

    def test_list_directory_contents_with_extension_filter(self, fs_service, nested_dir_structure):
        """Testa a listagem com filtro de extensão."""
        # Listar apenas arquivos .jpg
        files = list(fs_service.list_directory_contents(
            nested_dir_structure, 
            recursive=True,
            file_extensions=['.jpg']
        ))
        
        # Filtra para obter apenas os arquivos (não diretórios) e seus caminhos relativos
        file_paths = [str(f.relative_to(nested_dir_structure)) for f in files if f.is_file()]
        
        # Verifica se apenas os arquivos .jpg foram listados
        assert len(file_paths) == 2
        assert "file2.jpg" in file_paths
        
        # Usar Path para lidar com diferentes separadores de caminhos em diferentes SOs
        subdir1_nested_file5 = str(Path("subdir1") / "nested" / "file5.jpg")
        assert subdir1_nested_file5 in file_paths
        
        assert "file1.txt" not in file_paths
        
        # Usar Path para lidar com diferentes separadores de caminhos
        subdir1_file3 = str(Path("subdir1") / "file3.png")
        assert subdir1_file3 not in file_paths

    def test_list_directory_contents_nonexistent_dir(self, fs_service, temp_dir):
        """Testa a exceção ao listar um diretório inexistente."""
        nonexistent_dir = temp_dir / "nonexistent_dir"
        with pytest.raises(FileNotFoundError):
            list(fs_service.list_directory_contents(nonexistent_dir))

    def test_list_directory_contents_file_as_dir(self, fs_service, temp_file):
        """Testa a exceção ao tentar listar um arquivo como se fosse um diretório."""
        with pytest.raises(NotADirectoryError):
            list(fs_service.list_directory_contents(temp_file))

    @mock.patch('fotix.infrastructure.file_system.send2trash.send2trash')
    def test_move_to_trash(self, mock_send2trash, fs_service, temp_file):
        """Testa a movimentação de arquivo para a lixeira, usando um mock para send2trash."""
        fs_service.move_to_trash(temp_file)
        mock_send2trash.assert_called_once_with(str(temp_file))

    def test_move_to_trash_nonexistent_file(self, fs_service, temp_dir):
        """Testa a exceção ao tentar mover um arquivo inexistente para a lixeira."""
        nonexistent_file = temp_dir / "nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            fs_service.move_to_trash(nonexistent_file)

    def test_copy_file(self, fs_service, temp_file, temp_dir):
        """Testa a cópia de arquivo."""
        destination = temp_dir / "copied_file.txt"
        fs_service.copy_file(temp_file, destination)
        
        # Verifica se o arquivo foi copiado corretamente
        assert destination.exists()
        with open(destination, "r") as f:
            content = f.read()
        assert content == "Conteúdo de teste para o arquivo"

    def test_copy_file_create_parent_dirs(self, fs_service, temp_file, temp_dir):
        """Testa a cópia de arquivo com criação automática de diretórios pais."""
        destination = temp_dir / "new_subdir" / "copied_file.txt"
        fs_service.copy_file(temp_file, destination)
        
        # Verifica se o diretório pai foi criado e o arquivo foi copiado
        assert destination.exists()
        with open(destination, "r") as f:
            content = f.read()
        assert content == "Conteúdo de teste para o arquivo"

    def test_copy_file_nonexistent_source(self, fs_service, temp_dir):
        """Testa a exceção ao copiar de um arquivo inexistente."""
        source = temp_dir / "nonexistent.txt"
        destination = temp_dir / "destination.txt"
        with pytest.raises(FileNotFoundError):
            fs_service.copy_file(source, destination)

    def test_copy_file_directory_as_source(self, fs_service, temp_dir):
        """Testa a exceção ao tentar copiar um diretório como se fosse um arquivo."""
        destination = temp_dir / "copied_dir"
        with pytest.raises(IsADirectoryError):
            fs_service.copy_file(temp_dir, destination)

    def test_create_directory(self, fs_service, temp_dir):
        """Testa a criação de diretório."""
        new_dir = temp_dir / "new_dir"
        fs_service.create_directory(new_dir)
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_create_directory_with_parents(self, fs_service, temp_dir):
        """Testa a criação de diretório com diretórios pais."""
        new_dir = temp_dir / "parent" / "child" / "grandchild"
        fs_service.create_directory(new_dir)
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_create_directory_already_exists(self, fs_service, temp_dir):
        """Testa a criação de diretório que já existe com exist_ok=True."""
        # Primeiro cria o diretório
        new_dir = temp_dir / "existing_dir"
        new_dir.mkdir()
        
        # Tenta criar novamente com exist_ok=True, não deve gerar erro
        fs_service.create_directory(new_dir, exist_ok=True)
        assert new_dir.exists()

    def test_create_directory_already_exists_error(self, fs_service, temp_dir):
        """Testa a exceção ao criar diretório que já existe com exist_ok=False."""
        # Primeiro cria o diretório
        new_dir = temp_dir / "existing_dir"
        new_dir.mkdir()
        
        # Tenta criar novamente com exist_ok=False, deve gerar FileExistsError
        with pytest.raises(FileExistsError):
            fs_service.create_directory(new_dir, exist_ok=False)

    def test_path_exists_file(self, fs_service, temp_file):
        """Testa verificação de existência de arquivo."""
        assert fs_service.path_exists(temp_file) is True

    def test_path_exists_dir(self, fs_service, temp_dir):
        """Testa verificação de existência de diretório."""
        assert fs_service.path_exists(temp_dir) is True

    def test_path_exists_nonexistent(self, fs_service, temp_dir):
        """Testa verificação de existência de caminho inexistente."""
        nonexistent_path = temp_dir / "nonexistent"
        assert fs_service.path_exists(nonexistent_path) is False

    def test_get_creation_time(self, fs_service, temp_file):
        """Testa obtenção do timestamp de criação."""
        creation_time = fs_service.get_creation_time(temp_file)
        assert creation_time is not None
        assert isinstance(creation_time, float)
        # O timestamp de criação deve ser recente (nos últimos 10 segundos)
        assert time.time() - creation_time < 10

    def test_get_creation_time_nonexistent(self, fs_service, temp_dir):
        """Testa obtenção do timestamp de criação para arquivo inexistente."""
        nonexistent_path = temp_dir / "nonexistent"
        assert fs_service.get_creation_time(nonexistent_path) is None

    def test_get_modification_time(self, fs_service, temp_file):
        """Testa obtenção do timestamp de modificação."""
        modification_time = fs_service.get_modification_time(temp_file)
        assert modification_time is not None
        assert isinstance(modification_time, float)
        # O timestamp de modificação deve ser recente (nos últimos 10 segundos)
        assert time.time() - modification_time < 10

    def test_get_modification_time_after_update(self, fs_service, temp_file):
        """Testa se o timestamp de modificação é atualizado após modificar o arquivo."""
        initial_time = fs_service.get_modification_time(temp_file)
        
        # Espera um pouco para garantir que o timestamp será diferente
        time.sleep(0.1)
        
        # Modifica o arquivo
        with open(temp_file, "a") as f:
            f.write("\nConteúdo adicional")
        
        # Obtém o novo timestamp
        new_time = fs_service.get_modification_time(temp_file)
        
        assert new_time > initial_time

    def test_get_modification_time_nonexistent(self, fs_service, temp_dir):
        """Testa obtenção do timestamp de modificação para arquivo inexistente."""
        nonexistent_path = temp_dir / "nonexistent"
        assert fs_service.get_modification_time(nonexistent_path) is None 