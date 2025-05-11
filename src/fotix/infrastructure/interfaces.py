"""
Interfaces para os serviços da camada de infraestrutura do Fotix.

Este módulo define os contratos (interfaces) para os serviços da camada de infraestrutura,
como acesso ao sistema de arquivos, manipulação de ZIPs, concorrência e backup.
Estas interfaces permitem que as camadas superiores (core e aplicação) dependam
de abstrações em vez de implementações concretas, facilitando testes e manutenção.
"""

from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Optional, Protocol, TypeVar, Tuple, List
from concurrent.futures import Future

# Importação com aspas simples para evitar importação circular
# FileInfo será usado apenas para anotação de tipo
from fotix.core.models import FileInfo

# Tipo genérico para resultados de operações paralelas
T = TypeVar('T')
R = TypeVar('R')


class IConcurrencyService(Protocol):
    """
    Interface para abstrair a execução de tarefas concorrentes/paralelas.

    Esta interface define métodos para executar tarefas em paralelo e em background,
    utilizando threads ou processos. Implementações concretas devem gerenciar o pool
    de workers e lidar com os detalhes específicos da biblioteca de concorrência.
    """

    def run_parallel(self, tasks: Iterable[Callable[[], T]]) -> Iterable[T]:
        """
        Executa uma coleção de funções (tasks) em paralelo e retorna os resultados.

        Args:
            tasks: Coleção de funções sem argumentos que retornam um resultado.
                  Cada função deve ser independente e thread-safe.

        Returns:
            Iterable[T]: Os resultados das funções, na mesma ordem das tasks fornecidas.

        Note:
            Esta implementação gerencia internamente o pool de workers e o número
            máximo de threads/processos concorrentes, com base nas configurações
            e recursos do sistema.
        """
        ...

    def submit_background_task(self, task: Callable[..., R], *args, **kwargs) -> Future[R]:
        """
        Submete uma tarefa para execução em background e retorna um objeto Future.

        Args:
            task: Função a ser executada em background.
            *args: Argumentos posicionais para a função.
            **kwargs: Argumentos nomeados para a função.

        Returns:
            Future[R]: Objeto Future que representa a execução da tarefa.
                      Pode ser usado para verificar o status, obter o resultado
                      ou cancelar a execução.

        Note:
            O objeto Future retornado é da biblioteca concurrent.futures.
            Para obter o resultado, use future.result(), que bloqueará até
            a tarefa ser concluída. Para verificar se a tarefa foi concluída
            sem bloquear, use future.done().
        """
        ...


class IFileSystemService(Protocol):
    """
    Interface para abstrair operações no sistema de arquivos.

    Esta interface define métodos para operações comuns no sistema de arquivos,
    como leitura, escrita, movimentação para lixeira e listagem de diretórios.
    Implementações concretas devem lidar com os detalhes específicos do sistema
    operacional e tratar erros apropriadamente.
    """

    def get_file_size(self, path: Path) -> Optional[int]:
        """
        Retorna o tamanho do arquivo em bytes.

        Args:
            path: Caminho para o arquivo.

        Returns:
            int: Tamanho do arquivo em bytes, ou None se o arquivo não existir
                 ou não for acessível.

        Note:
            Esta operação não segue links simbólicos. Para obter o tamanho do
            arquivo apontado por um link simbólico, resolva o link antes de
            chamar este método.
        """
        ...

    def stream_file_content(self, path: Path, chunk_size: int = 65536) -> Iterable[bytes]:
        """
        Retorna um iterador/gerador para ler o conteúdo do arquivo em blocos.

        Args:
            path: Caminho para o arquivo.
            chunk_size: Tamanho de cada bloco em bytes. Padrão é 64KB.

        Returns:
            Iterable[bytes]: Iterador/gerador que produz blocos do conteúdo do arquivo.

        Raises:
            FileNotFoundError: Se o arquivo não existir.
            PermissionError: Se não houver permissão para ler o arquivo.
            IsADirectoryError: Se o caminho apontar para um diretório.
            Exception: Outras exceções relacionadas a IO podem ser levantadas.

        Note:
            Esta implementação é eficiente para arquivos grandes, pois não carrega
            todo o conteúdo na memória de uma vez.
        """
        ...

    def list_directory_contents(self, path: Path, recursive: bool = True,
                               file_extensions: Optional[list[str]] = None) -> Iterable[Path]:
        """
        Lista os conteúdos de um diretório, opcionalmente de forma recursiva.

        Args:
            path: Caminho para o diretório.
            recursive: Se True, lista também os conteúdos dos subdiretórios.
            file_extensions: Lista opcional de extensões de arquivo para filtrar.
                            Se None, todos os arquivos são incluídos.
                            Exemplo: ['.jpg', '.png']

        Returns:
            Iterable[Path]: Iterador/gerador que produz os caminhos dos arquivos
                           (e opcionalmente diretórios) encontrados.

        Raises:
            FileNotFoundError: Se o diretório não existir.
            NotADirectoryError: Se o caminho não apontar para um diretório.
            PermissionError: Se não houver permissão para acessar o diretório.

        Note:
            Esta implementação é eficiente para diretórios grandes, pois usa
            iteração em vez de construir uma lista completa na memória.
        """
        ...

    def move_to_trash(self, path: Path) -> None:
        """
        Move um arquivo ou diretório para a lixeira do sistema.

        Args:
            path: Caminho para o arquivo ou diretório a ser movido para a lixeira.

        Raises:
            FileNotFoundError: Se o caminho não existir.
            PermissionError: Se não houver permissão para mover o arquivo/diretório.
            OSError: Para outros erros relacionados ao sistema operacional.

        Note:
            Esta operação é mais segura que a exclusão direta, pois permite
            recuperação posterior. Usa a biblioteca send2trash internamente.
        """
        ...

    def copy_file(self, source: Path, destination: Path) -> None:
        """
        Copia um arquivo de origem para destino.

        Args:
            source: Caminho para o arquivo de origem.
            destination: Caminho para o arquivo de destino.

        Raises:
            FileNotFoundError: Se o arquivo de origem não existir.
            IsADirectoryError: Se source for um diretório.
            PermissionError: Se não houver permissão para ler a origem ou escrever no destino.
            OSError: Para outros erros relacionados ao sistema operacional.

        Note:
            Se o arquivo de destino já existir, ele será sobrescrito.
            Os metadados do arquivo (permissões, timestamps) são preservados.
        """
        ...

    def create_directory(self, path: Path, exist_ok: bool = True) -> None:
        """
        Cria um diretório e todos os diretórios pai necessários.

        Args:
            path: Caminho para o diretório a ser criado.
            exist_ok: Se True, não levanta erro se o diretório já existir.

        Raises:
            FileExistsError: Se o diretório já existir e exist_ok for False.
            PermissionError: Se não houver permissão para criar o diretório.
            FileNotFoundError: Se um diretório pai não puder ser criado.

        Note:
            Esta operação é equivalente a `mkdir -p` no Unix.
        """
        ...

    def path_exists(self, path: Path) -> bool:
        """
        Verifica se um caminho existe no sistema de arquivos.

        Args:
            path: Caminho a ser verificado.

        Returns:
            bool: True se o caminho existir, False caso contrário.

        Note:
            Esta operação segue links simbólicos. Para verificar se o caminho
            apontado por um link simbólico existe, use este método diretamente.
            Para verificar se o próprio link simbólico existe (independentemente
            de para onde ele aponta), use este método no caminho do link.
        """
        ...

    def get_creation_time(self, path: Path) -> Optional[float]:
        """
        Retorna o timestamp de criação do arquivo ou diretório.

        Args:
            path: Caminho para o arquivo ou diretório.

        Returns:
            float: Timestamp de criação (segundos desde a época), ou None se
                  o arquivo não existir ou a informação não estiver disponível.

        Note:
            Em alguns sistemas de arquivos, esta informação pode não estar
            disponível ou pode ser o timestamp de modificação.
        """
        ...

    def get_modification_time(self, path: Path) -> Optional[float]:
        """
        Retorna o timestamp de última modificação do arquivo ou diretório.

        Args:
            path: Caminho para o arquivo ou diretório.

        Returns:
            float: Timestamp de modificação (segundos desde a época), ou None se
                  o arquivo não existir ou a informação não estiver disponível.
        """
        ...


class IZipHandlerService(Protocol):
    """
    Interface para abstrair a leitura de arquivos dentro de arquivos ZIP.

    Esta interface define métodos para acessar o conteúdo de arquivos ZIP
    de forma eficiente (streaming), sem extrair todo o conteúdo para o disco.
    Implementações concretas devem lidar com os detalhes específicos da
    biblioteca de descompressão utilizada.
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
        ...


class IBackupService(Protocol):
    """
    Interface para abstrair as operações de backup e restauração.

    Esta interface define métodos para criar, listar, restaurar e excluir backups
    de arquivos. Implementações concretas devem lidar com os detalhes específicos
    de armazenamento e gerenciamento de metadados dos backups.
    """

    def create_backup(self, files_to_backup: Iterable[Tuple[Path, FileInfo]]) -> str:
        """
        Cria um backup dos arquivos fornecidos.

        Args:
            files_to_backup: Coleção de tuplas contendo o caminho do arquivo e seu FileInfo.
                            O FileInfo contém metadados importantes como hash, tamanho, etc.

        Returns:
            str: ID único para o backup realizado.

        Raises:
            FileNotFoundError: Se algum dos arquivos não existir.
            PermissionError: Se não houver permissão para ler os arquivos ou escrever no destino.
            IOError: Para outros erros relacionados a IO.

        Note:
            Esta operação copia os arquivos para uma área segura (configurada via fotix.config)
            e armazena metadados sobre o backup (data, arquivos, hashes, caminhos originais).
            O ID retornado pode ser usado posteriormente para restaurar ou excluir o backup.
        """
        ...

    def list_backups(self) -> List[Dict[str, Any]]:
        """
        Retorna uma lista de informações sobre os backups disponíveis.

        Returns:
            List[Dict[str, Any]]: Lista de dicionários, cada um contendo informações
                                 sobre um backup, como:
                                 - 'id': ID único do backup (str)
                                 - 'date': Data/hora do backup (datetime)
                                 - 'file_count': Número de arquivos no backup (int)
                                 - 'total_size': Tamanho total em bytes (int)
                                 - 'description': Descrição opcional (str)

        Note:
            Esta operação não acessa os arquivos de backup em si, apenas os metadados.
        """
        ...

    def restore_backup(self, backup_id: str, target_directory: Optional[Path] = None) -> None:
        """
        Restaura os arquivos de um backup específico.

        Args:
            backup_id: ID do backup a ser restaurado.
            target_directory: Diretório alvo para restauração. Se None, os arquivos
                             são restaurados em seus locais originais.

        Raises:
            ValueError: Se o backup_id for inválido ou não existir.
            FileExistsError: Se algum arquivo de destino já existir e não puder ser sobrescrito.
            PermissionError: Se não houver permissão para escrever nos destinos.
            IOError: Para outros erros relacionados a IO.

        Note:
            Se target_directory for fornecido, todos os arquivos são restaurados
            nesse diretório, preservando apenas os nomes dos arquivos (não a estrutura
            de diretórios original). Se for None, a estrutura original é recriada.
        """
        ...

    def delete_backup(self, backup_id: str) -> None:
        """
        Remove um backup específico.

        Args:
            backup_id: ID do backup a ser removido.

        Raises:
            ValueError: Se o backup_id for inválido ou não existir.
            PermissionError: Se não houver permissão para excluir os arquivos.
            IOError: Para outros erros relacionados a IO.

        Note:
            Esta operação remove tanto os arquivos de backup quanto os metadados associados.
            Após a exclusão, o backup não poderá mais ser restaurado.
        """
        ...
