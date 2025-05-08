"""
Testes unitários para o módulo file_system.py.

Este módulo testa a implementação do FileSystemService, verificando
se todas as operações de arquivos e diretórios funcionam como esperado.
"""

import os
import tempfile
import shutil
import logging
from pathlib import Path
from unittest import mock
import pytest

from fotix.infrastructure.file_system import FileSystemService
from fotix.infrastructure.interfaces import IFileSystemService


class TestFileSystemService:
    """Testes para a classe FileSystemService."""
    
    @pytest.fixture
    def fs_service(self):
        """Fixture que retorna uma instância do FileSystemService."""
        # Desativa o logging durante os testes para evitar poluição na saída
        with mock.patch('fotix.infrastructure.file_system.logger'):
            return FileSystemService()
    
    @pytest.fixture
    def temp_dir(self):
        """Fixture que cria um diretório temporário para os testes."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        # Limpeza: remove o diretório temporário após o teste
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def temp_file(self, temp_dir):
        """Fixture que cria um arquivo temporário para os testes."""
        temp_file = temp_dir / "test_file.txt"
        with open(temp_file, "w") as f:
            f.write("Test content")
        yield temp_file
        # A limpeza do arquivo é feita pelo fixture temp_dir
    
    @pytest.fixture
    def temp_subdir(self, temp_dir):
        """Fixture que cria um subdiretório temporário para os testes."""
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        yield subdir
        # A limpeza do subdiretório é feita pelo fixture temp_dir
    
    def test_initialization(self, fs_service):
        """Testa se a classe é inicializada corretamente."""
        assert isinstance(fs_service, IFileSystemService)
        assert isinstance(fs_service, FileSystemService)
    
    def test_get_file_size_existent_file(self, fs_service, temp_file):
        """Testa se get_file_size retorna o tamanho correto para um arquivo existente."""
        size = fs_service.get_file_size(temp_file)
        assert size == len("Test content")
    
    def test_get_file_size_nonexistent_file(self, fs_service, temp_dir):
        """Testa se get_file_size retorna None para um arquivo inexistente."""
        nonexistent_file = temp_dir / "nonexistent.txt"
        size = fs_service.get_file_size(nonexistent_file)
        assert size is None
    
    def test_get_file_size_directory(self, fs_service, temp_dir):
        """Testa se get_file_size retorna None para um diretório."""
        size = fs_service.get_file_size(temp_dir)
        assert size is None
    
    def test_stream_file_content(self, fs_service, temp_file):
        """Testa se stream_file_content retorna o conteúdo correto."""
        content = b"".join(fs_service.stream_file_content(temp_file))
        assert content == b"Test content"
    
    def test_stream_file_content_nonexistent_file(self, fs_service, temp_dir):
        """Testa se stream_file_content levanta exceção para arquivo inexistente."""
        nonexistent_file = temp_dir / "nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            list(fs_service.stream_file_content(nonexistent_file))
    
    def test_stream_file_content_with_custom_chunk_size(self, fs_service, temp_dir):
        """Testa se stream_file_content funciona com um tamanho de chunk personalizado."""
        # Cria um arquivo maior para testar chunks
        test_file = temp_dir / "chunked_file.txt"
        content = "A" * 1000  # 1000 caracteres
        with open(test_file, "w") as f:
            f.write(content)
        
        # Lê com chunk de 100 bytes
        chunks = list(fs_service.stream_file_content(test_file, chunk_size=100))
        assert len(chunks) > 1  # Deve haver múltiplos chunks
        reconstructed = b"".join(chunks)
        assert reconstructed == content.encode()
    
    def test_list_directory_contents_recursive(self, fs_service, temp_dir, temp_subdir):
        """Testa listagem recursiva de diretório."""
        # Cria alguns arquivos para testar
        (temp_dir / "file1.txt").write_text("file1")
        (temp_dir / "file2.jpg").write_text("file2")
        (temp_subdir / "file3.txt").write_text("file3")
        (temp_subdir / "file4.png").write_text("file4")
        
        # Lista todos os arquivos
        files = list(fs_service.list_directory_contents(temp_dir))
        assert len(files) == 4
        
        # Verifica se os arquivos esperados estão na lista
        filenames = [f.name for f in files]
        assert "file1.txt" in filenames
        assert "file2.jpg" in filenames
        assert "file3.txt" in filenames
        assert "file4.png" in filenames
    
    def test_list_directory_contents_non_recursive(self, fs_service, temp_dir, temp_subdir):
        """Testa listagem não-recursiva de diretório."""
        # Cria alguns arquivos para testar
        (temp_dir / "file1.txt").write_text("file1")
        (temp_dir / "file2.jpg").write_text("file2")
        (temp_subdir / "file3.txt").write_text("file3")
        
        # Lista apenas o diretório raiz
        files = list(fs_service.list_directory_contents(temp_dir, recursive=False))
        assert len(files) == 2
        
        # Verifica se apenas os arquivos do diretório raiz estão na lista
        filenames = [f.name for f in files]
        assert "file1.txt" in filenames
        assert "file2.jpg" in filenames
        assert "file3.txt" not in filenames
    
    def test_list_directory_contents_with_extensions(self, fs_service, temp_dir, temp_subdir):
        """Testa listagem de diretório com filtro de extensões."""
        # Cria alguns arquivos para testar
        (temp_dir / "file1.txt").write_text("file1")
        (temp_dir / "file2.jpg").write_text("file2")
        (temp_subdir / "file3.txt").write_text("file3")
        (temp_subdir / "file4.png").write_text("file4")
        
        # Lista apenas arquivos .txt
        files = list(fs_service.list_directory_contents(temp_dir, file_extensions=[".txt"]))
        assert len(files) == 2
        
        # Verifica se apenas os arquivos .txt estão na lista
        filenames = [f.name for f in files]
        assert "file1.txt" in filenames
        assert "file3.txt" in filenames
        assert "file2.jpg" not in filenames
        assert "file4.png" not in filenames
    
    def test_list_directory_contents_nonexistent_directory(self, fs_service, temp_dir):
        """Testa se list_directory_contents levanta exceção para diretório inexistente."""
        nonexistent_dir = temp_dir / "nonexistent"
        with pytest.raises(FileNotFoundError):
            list(fs_service.list_directory_contents(nonexistent_dir))
    
    def test_list_directory_contents_not_a_directory(self, fs_service, temp_file):
        """Testa se list_directory_contents levanta exceção para não-diretório."""
        with pytest.raises(NotADirectoryError):
            list(fs_service.list_directory_contents(temp_file))
    
    def test_move_to_trash(self, fs_service, temp_file):
        """
        Testa a movimentação de arquivo para a lixeira.
        
        Observação: Este teste utiliza mock para evitar a remoção real do arquivo.
        """
        with mock.patch('fotix.infrastructure.file_system.send2trash') as mock_send2trash:
            fs_service.move_to_trash(temp_file)
            mock_send2trash.assert_called_once_with(str(temp_file))
    
    def test_move_to_trash_nonexistent_file(self, fs_service, temp_dir):
        """Testa se move_to_trash levanta exceção para arquivo inexistente."""
        nonexistent_file = temp_dir / "nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            fs_service.move_to_trash(nonexistent_file)
    
    def test_copy_file(self, fs_service, temp_file, temp_dir):
        """Testa a cópia de um arquivo."""
        dest = temp_dir / "copied_file.txt"
        fs_service.copy_file(temp_file, dest)
        
        # Verifica se o arquivo de destino existe e tem o mesmo conteúdo
        assert dest.exists()
        assert dest.read_text() == "Test content"
    
    def test_copy_file_nonexistent_source(self, fs_service, temp_dir):
        """Testa se copy_file levanta exceção para arquivo de origem inexistente."""
        nonexistent_file = temp_dir / "nonexistent.txt"
        dest = temp_dir / "copied_file.txt"
        with pytest.raises(FileNotFoundError):
            fs_service.copy_file(nonexistent_file, dest)
    
    def test_copy_file_source_is_directory(self, fs_service, temp_dir):
        """Testa se copy_file levanta exceção quando a origem é um diretório."""
        dest = temp_dir / "copied_dir"
        with pytest.raises(IsADirectoryError):
            fs_service.copy_file(temp_dir, dest)
    
    def test_create_directory(self, fs_service, temp_dir):
        """Testa a criação de um diretório."""
        new_dir = temp_dir / "new_directory"
        fs_service.create_directory(new_dir)
        assert new_dir.is_dir()
    
    def test_create_directory_nested(self, fs_service, temp_dir):
        """Testa a criação de um diretório aninhado."""
        nested_dir = temp_dir / "nested" / "directory" / "structure"
        fs_service.create_directory(nested_dir)
        assert nested_dir.is_dir()
    
    def test_create_directory_already_exists(self, fs_service, temp_dir):
        """Testa a criação de um diretório que já existe com exist_ok=True."""
        fs_service.create_directory(temp_dir)  # Não deve levantar exceção
        assert temp_dir.is_dir()
    
    def test_create_directory_already_exists_error(self, fs_service, temp_dir):
        """Testa se create_directory levanta exceção quando o diretório já existe e exist_ok=False."""
        with pytest.raises(FileExistsError):
            fs_service.create_directory(temp_dir, exist_ok=False)
    
    def test_path_exists(self, fs_service, temp_file, temp_dir):
        """Testa a verificação de existência de caminho."""
        assert fs_service.path_exists(temp_file) is True
        assert fs_service.path_exists(temp_dir) is True
        
        nonexistent = temp_dir / "nonexistent.txt"
        assert fs_service.path_exists(nonexistent) is False
    
    def test_get_creation_time(self, fs_service, temp_file):
        """Testa a obtenção do timestamp de criação."""
        creation_time = fs_service.get_creation_time(temp_file)
        assert isinstance(creation_time, float)
        assert creation_time > 0
    
    def test_get_creation_time_nonexistent_file(self, fs_service, temp_dir):
        """Testa se get_creation_time retorna None para arquivo inexistente."""
        nonexistent_file = temp_dir / "nonexistent.txt"
        assert fs_service.get_creation_time(nonexistent_file) is None
    
    def test_get_modification_time(self, fs_service, temp_file):
        """Testa a obtenção do timestamp de modificação."""
        mod_time = fs_service.get_modification_time(temp_file)
        assert isinstance(mod_time, float)
        assert mod_time > 0
        
        # Modifica o arquivo e verifica se o timestamp muda
        original_time = mod_time
        # Espera um pouco para garantir timestamp diferente
        import time
        time.sleep(0.1)
        
        with open(temp_file, "a") as f:
            f.write(" updated")
        
        new_mod_time = fs_service.get_modification_time(temp_file)
        assert new_mod_time > original_time
    
    def test_get_modification_time_nonexistent_file(self, fs_service, temp_dir):
        """Testa se get_modification_time retorna None para arquivo inexistente."""
        nonexistent_file = temp_dir / "nonexistent.txt"
        assert fs_service.get_modification_time(nonexistent_file) is None
    
    # Testes para os métodos privados
    def test_walk_directory(self, fs_service, temp_dir, temp_subdir):
        """Testa o método privado _walk_directory."""
        # Cria alguns arquivos para testar
        (temp_dir / "file1.txt").write_text("file1")
        (temp_subdir / "file2.jpg").write_text("file2")
        
        # Lista todos os arquivos
        files = list(fs_service._walk_directory(temp_dir))
        assert len(files) == 2
        
        # Lista apenas arquivos .txt
        files = list(fs_service._walk_directory(temp_dir, file_extensions=[".txt"]))
        assert len(files) == 1
        assert files[0].name == "file1.txt"
    
    def test_list_files_in_directory(self, fs_service, temp_dir, temp_subdir):
        """Testa o método privado _list_files_in_directory."""
        # Cria alguns arquivos para testar
        (temp_dir / "file1.txt").write_text("file1")
        (temp_dir / "file2.jpg").write_text("file2")
        (temp_subdir / "file3.txt").write_text("file3")  # Não deve ser listado
        
        # Lista todos os arquivos no diretório raiz
        files = list(fs_service._list_files_in_directory(temp_dir))
        assert len(files) == 2
        
        # Lista apenas arquivos .txt no diretório raiz
        files = list(fs_service._list_files_in_directory(temp_dir, file_extensions=[".txt"]))
        assert len(files) == 1
        assert files[0].name == "file1.txt" 