"""
Testes unitários para o FileSystemService.
"""
import os
import shutil
import stat
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, mock_open, patch

import pytest
import send2trash # type: ignore

from fotix.infrastructure.file_system import FileSystemService


@pytest.fixture
def fs_service() -> FileSystemService:
    """Retorna uma instância de FileSystemService para os testes."""
    return FileSystemService()


class TestFileSystemService:
    """Agrupa os testes para FileSystemService."""

    # Testes para get_file_size
    def test_get_file_size_existing_file(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa get_file_size para um arquivo existente."""
        file = tmp_path / "test_file.txt"
        file.write_bytes(b"12345")
        assert fs_service.get_file_size(file) == 5

    def test_get_file_size_non_existent_file(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa get_file_size para um arquivo inexistente."""
        non_existent_file = tmp_path / "non_existent.txt"
        assert fs_service.get_file_size(non_existent_file) is None

    def test_get_file_size_directory(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa get_file_size para um diretório (deve retornar None)."""
        directory = tmp_path / "test_dir"
        directory.mkdir()
        assert fs_service.get_file_size(directory) is None

    @patch("pathlib.Path.stat")
    def test_get_file_size_permission_error(self, mock_stat: MagicMock, fs_service: FileSystemService):
        """Testa get_file_size lidando com PermissionError."""
        mock_path = MagicMock(spec=Path)
        mock_path.is_file.return_value = True
        mock_path.stat.side_effect = PermissionError
        assert fs_service.get_file_size(mock_path) is None

    # Testes para stream_file_content
    def test_stream_file_content_existing_file(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa stream_file_content para um arquivo existente."""
        file_content = b"abcdefghijklmnopqrstuvwxyz"
        file = tmp_path / "stream_me.txt"
        file.write_bytes(file_content)

        streamed_content = b"".join(list(fs_service.stream_file_content(file, chunk_size=5)))
        assert streamed_content == file_content

    def test_stream_file_content_non_existent_file(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa stream_file_content para um arquivo inexistente."""
        non_existent_file = tmp_path / "non_existent_stream.txt"
        with pytest.raises(FileNotFoundError):
            # Consumir o gerador para acionar a exceção
            list(fs_service.stream_file_content(non_existent_file))

    def test_stream_file_content_directory(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa stream_file_content para um diretório (deve levantar FileNotFoundError)."""
        directory = tmp_path / "stream_dir"
        directory.mkdir()
        with pytest.raises(FileNotFoundError):
            list(fs_service.stream_file_content(directory))

    @patch("builtins.open", new_callable=mock_open)
    def test_stream_file_content_permission_error(
        self, mock_open_file: MagicMock, fs_service: FileSystemService
    ):
        """Testa stream_file_content lidando com PermissionError."""
        mock_path = MagicMock(spec=Path)
        mock_path.is_file.return_value = True
        mock_open_file.side_effect = PermissionError
        with pytest.raises(PermissionError):
            list(fs_service.stream_file_content(mock_path))

    # Testes para list_directory_contents
    def test_list_directory_contents_empty(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa listar um diretório vazio."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        assert list(fs_service.list_directory_contents(empty_dir)) == []

    def test_list_directory_contents_flat(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa listar um diretório com arquivos (não recursivo)."""
        test_dir = tmp_path / "flat_dir"
        test_dir.mkdir()
        file_a = test_dir / "a.txt"
        file_a.touch()
        file_b = test_dir / "b.log"
        file_b.touch()
        sub_dir = test_dir / "sub"
        sub_dir.mkdir()
        (sub_dir / "c.txt").touch()

        # Não recursivo
        contents = list(fs_service.list_directory_contents(test_dir, recursive=False))
        assert len(contents) == 2
        assert file_a in contents
        assert file_b in contents

    def test_list_directory_contents_recursive(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa listar um diretório com arquivos e subdiretórios (recursivo)."""
        test_dir = tmp_path / "recursive_dir"
        test_dir.mkdir()
        file_a = test_dir / "a.txt"
        file_a.touch()
        sub_dir = test_dir / "sub"
        sub_dir.mkdir()
        file_b_in_sub = sub_dir / "b.txt"
        file_b_in_sub.touch()

        contents = sorted(list(fs_service.list_directory_contents(test_dir, recursive=True)))
        assert len(contents) == 2
        assert file_a in contents
        assert file_b_in_sub in contents

    def test_list_directory_contents_with_extensions(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa listar com filtro de extensões."""
        test_dir = tmp_path / "ext_dir"
        test_dir.mkdir()
        (test_dir / "file.txt").touch()
        (test_dir / "image.JPG").touch()
        (test_dir / "archive.zip").touch()
        (test_dir / "document.pdf").touch()

        txt_files = list(fs_service.list_directory_contents(test_dir, file_extensions=[".txt", "pdf"])) # testa com e sem ponto
        assert len(txt_files) == 2
        assert test_dir / "file.txt" in txt_files
        assert test_dir / "document.pdf" in txt_files

        jpg_files = list(fs_service.list_directory_contents(test_dir, file_extensions=[".jpg"]))
        assert len(jpg_files) == 1
        assert test_dir / "image.JPG" in jpg_files # Deve ser case-insensitive

    def test_list_directory_contents_non_existent_dir(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa listar um diretório inexistente."""
        non_existent_dir = tmp_path / "i_dont_exist"
        assert list(fs_service.list_directory_contents(non_existent_dir)) == []

    @patch("pathlib.Path.rglob")
    def test_list_directory_contents_permission_error(
        self, mock_rglob: MagicMock, fs_service: FileSystemService
    ):
        """Testa list_directory_contents lidando com PermissionError."""
        mock_path = MagicMock(spec=Path)
        mock_path.is_dir.return_value = True
        mock_rglob.side_effect = PermissionError
        # Deve retornar iterador vazio e logar, não levantar exceção
        assert list(fs_service.list_directory_contents(mock_path)) == []
        # (Verificação de log seria ideal aqui com caplog)

    # Testes para move_to_trash
    @patch("send2trash.send2trash")
    def test_move_to_trash_success(self, mock_send2trash: MagicMock, fs_service: FileSystemService):
        """Testa mover para lixeira com sucesso."""
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = True
        fs_service.move_to_trash(mock_path)
        mock_send2trash.assert_called_once_with(str(mock_path))

    def test_move_to_trash_non_existent(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa mover para lixeira um arquivo inexistente."""
        non_existent = tmp_path / "no_trash_me.txt"
        with pytest.raises(FileNotFoundError):
            fs_service.move_to_trash(non_existent)

    @patch("send2trash.send2trash")
    def test_move_to_trash_failure_exception(self, mock_send2trash: MagicMock, fs_service: FileSystemService):
        """Testa falha ao mover para lixeira (exceção de send2trash)."""
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = True
        mock_send2trash.side_effect = OSError("Falha ao mover")
        with pytest.raises(OSError):
            fs_service.move_to_trash(mock_path)

    # Testes para copy_file
    def test_copy_file_success(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa copiar arquivo com sucesso."""
        source = tmp_path / "source.txt"
        source.write_text("copiado")
        destination = tmp_path / "dest" / "copied.txt"

        fs_service.copy_file(source, destination)
        assert destination.exists()
        assert destination.read_text() == "copiado"

    def test_copy_file_source_not_exists(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa copiar arquivo onde a origem não existe."""
        source = tmp_path / "non_existent_source.txt"
        destination = tmp_path / "dest.txt"
        with pytest.raises(FileNotFoundError):
            fs_service.copy_file(source, destination)

    def test_copy_file_source_is_dir(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa copiar arquivo onde a origem é um diretório."""
        source_dir = tmp_path / "source_dir"
        source_dir.mkdir()
        destination = tmp_path / "dest.txt"
        with pytest.raises(FileNotFoundError): # A implementação checa is_file()
            fs_service.copy_file(source_dir, destination)

    @patch("shutil.copy2")
    def test_copy_file_shutil_exception(self, mock_copy2: MagicMock, fs_service: FileSystemService):
        """Testa copy_file lidando com exceção do shutil.copy2."""
        mock_source_path = MagicMock(spec=Path)
        mock_source_path.is_file.return_value = True
        mock_dest_path = MagicMock(spec=Path)
        mock_dest_path.parent.mkdir = MagicMock() # Mockar mkdir do parent
        mock_copy2.side_effect = shutil.Error("Erro de cópia")

        with pytest.raises(shutil.Error):
            fs_service.copy_file(mock_source_path, mock_dest_path)
        mock_dest_path.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    # Testes para create_directory
    def test_create_directory_success_new(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa criar um novo diretório."""
        new_dir = tmp_path / "new_created_dir"
        fs_service.create_directory(new_dir)
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_create_directory_success_existing_ok(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa criar um diretório que já existe com exist_ok=True."""
        existing_dir = tmp_path / "already_exists"
        existing_dir.mkdir()
        fs_service.create_directory(existing_dir, exist_ok=True)
        assert existing_dir.is_dir()

    def test_create_directory_fails_existing_not_ok(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa criar um diretório que já existe com exist_ok=False."""
        existing_dir = tmp_path / "already_exists_fail"
        existing_dir.mkdir()
        with pytest.raises(FileExistsError):
            fs_service.create_directory(existing_dir, exist_ok=False)

    # Testes para path_exists
    def test_path_exists_true_file(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa path_exists para arquivo existente."""
        file = tmp_path / "exists.txt"
        file.touch()
        assert fs_service.path_exists(file) is True

    def test_path_exists_true_dir(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa path_exists para diretório existente."""
        dir_path = tmp_path / "dir_exists"
        dir_path.mkdir()
        assert fs_service.path_exists(dir_path) is True

    def test_path_exists_false(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa path_exists para caminho inexistente."""
        non_existent = tmp_path / "i_am_not_here"
        assert fs_service.path_exists(non_existent) is False

    # Testes para get_creation_time e get_modification_time
    def test_get_times_existing_file(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa get_creation_time e get_modification_time para arquivo existente."""
        file = tmp_path / "timed_file.txt"
        file.write_text("content")
        file_stat = file.stat()

        assert fs_service.get_creation_time(file) == pytest.approx(file_stat.st_ctime)
        assert fs_service.get_modification_time(file) == pytest.approx(file_stat.st_mtime)

    def test_get_times_non_existent(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa get_creation_time e get_modification_time para arquivo inexistente."""
        non_existent = tmp_path / "no_time_for_me.txt"
        assert fs_service.get_creation_time(non_existent) is None
        assert fs_service.get_modification_time(non_existent) is None

    # Testes para delete_file
    def test_delete_file_success(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa deletar um arquivo com sucesso."""
        file_to_delete = tmp_path / "delete_me.txt"
        file_to_delete.touch()
        assert file_to_delete.exists()
        fs_service.delete_file(file_to_delete)
        assert not file_to_delete.exists()

    def test_delete_file_non_existent(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa deletar um arquivo inexistente."""
        non_existent = tmp_path / "cant_delete_non_existent.txt"
        with pytest.raises(FileNotFoundError):
            fs_service.delete_file(non_existent)

    def test_delete_file_is_directory(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa deletar um caminho que é um diretório usando delete_file."""
        dir_path = tmp_path / "dir_not_file_for_delete"
        dir_path.mkdir()
        with pytest.raises(FileNotFoundError): # A implementação verifica is_file()
            fs_service.delete_file(dir_path)

    # Testes para delete_directory
    def test_delete_directory_empty_success(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa deletar um diretório vazio com sucesso."""
        empty_dir = tmp_path / "empty_dir_to_delete"
        empty_dir.mkdir()
        assert empty_dir.exists()
        fs_service.delete_directory(empty_dir)
        assert not empty_dir.exists()

    def test_delete_directory_recursive_success(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa deletar um diretório não vazio recursivamente com sucesso."""
        parent_dir = tmp_path / "parent_dir_to_delete"
        parent_dir.mkdir()
        (parent_dir / "file.txt").touch()
        sub_dir = parent_dir / "sub"
        sub_dir.mkdir()
        (sub_dir / "another.txt").touch()

        assert parent_dir.exists()
        fs_service.delete_directory(parent_dir, recursive=True)
        assert not parent_dir.exists()

    def test_delete_directory_not_empty_not_recursive(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa falha ao deletar diretório não vazio sem recursive=True."""
        non_empty_dir = tmp_path / "non_empty_dir_fail"
        non_empty_dir.mkdir()
        (non_empty_dir / "some_file.txt").touch()
        with pytest.raises(OSError): # rmdir() raises OSError if not empty
            fs_service.delete_directory(non_empty_dir, recursive=False)
        assert non_empty_dir.exists() # Deve continuar existindo

    def test_delete_directory_non_existent(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa deletar um diretório inexistente."""
        non_existent_dir = tmp_path / "no_dir_here_to_delete"
        with pytest.raises(NotADirectoryError):
            fs_service.delete_directory(non_existent_dir)

    def test_delete_directory_is_file(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa deletar um caminho que é um arquivo usando delete_directory."""
        file_path = tmp_path / "file_not_dir_for_delete"
        file_path.touch()
        with pytest.raises(NotADirectoryError):
            fs_service.delete_directory(file_path)

    # Testes para get_file_info
    def test_get_file_info_file(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa get_file_info para um arquivo."""
        file = tmp_path / "info_file.txt"
        file.write_text("info")
        file_stat = file.stat()

        info = fs_service.get_file_info(file)
        assert info is not None
        assert info["name"] == "info_file.txt"
        assert Path(info["path"]) == file.resolve()
        assert info["size"] == 4
        assert info["creation_time"] == pytest.approx(file_stat.st_ctime)
        assert info["modification_time"] == pytest.approx(file_stat.st_mtime)
        assert info["is_dir"] is False

    def test_get_file_info_directory(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa get_file_info para um diretório."""
        dir_path = tmp_path / "info_dir"
        dir_path.mkdir()
        dir_stat = dir_path.stat()

        info = fs_service.get_file_info(dir_path)
        assert info is not None
        assert info["name"] == "info_dir"
        assert Path(info["path"]) == dir_path.resolve()
        assert info["size"] is None # Tamanho é None para diretórios
        assert info["creation_time"] == pytest.approx(dir_stat.st_ctime)
        assert info["modification_time"] == pytest.approx(dir_stat.st_mtime)
        assert info["is_dir"] is True

    def test_get_file_info_non_existent(self, fs_service: FileSystemService, tmp_path: Path):
        """Testa get_file_info para um caminho inexistente."""
        non_existent = tmp_path / "no_info_here.dat"
        assert fs_service.get_file_info(non_existent) is None

    @patch("pathlib.Path.stat")
    def test_get_file_info_stat_exception(self, mock_stat: MagicMock, fs_service: FileSystemService):
        """Testa get_file_info quando path.stat() levanta uma exceção."""
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = True
        mock_path.is_dir.return_value = False # Simula ser um arquivo
        mock_path.stat.side_effect = OSError("Erro ao acessar stat")
        # path.name e path.resolve() ainda podem ser chamados no mock_path
        mock_path.name = "error_file.txt"
        mock_path.resolve.return_value = Path("/fake/path/error_file.txt")

        assert fs_service.get_file_info(mock_path) is None
        # (Verificar log seria bom aqui) 