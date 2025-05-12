# Testes de Integração para a UI do Fotix

Este diretório contém testes de integração para verificar a comunicação e o fluxo de dados entre a Camada de Apresentação (UI) e a Camada de Aplicação do Fotix.

## Objetivo

Os testes de integração da UI têm como objetivo garantir que:

1. As ações do usuário na UI disparem corretamente os serviços de aplicação
2. Os resultados/atualizações dos serviços sejam refletidos na UI
3. Os dados do core sejam corretamente formatados e exibidos nos componentes da UI
4. O fluxo completo de trabalho funcione corretamente, desde a UI até os serviços de aplicação

## Cenários Testados

### 1. Scan a partir da UI

Simula a seleção de um diretório na UI e o início de um scan. Verifica se o `ScanService` na camada de aplicação é invocado com os parâmetros corretos e se a UI exibe informações de progresso e, eventualmente, os resultados (lista de duplicatas).

### 2. Seleção e Remoção de Duplicata via UI

A partir de uma lista de duplicatas exibida na UI, simula a seleção de um arquivo para manter e a confirmação para remover os outros. Verifica se o `DuplicateManagementService` é chamado, se o backup ocorre e se o arquivo é movido para a lixeira, com a UI atualizando seu estado.

### 3. Restauração de Backup via UI

Simula a navegação pela lista de backups na UI, a seleção de um backup e o acionamento da restauração. Verifica se o `BackupRestoreService` é invocado e se a UI reflete o sucesso ou falha da operação.

### 4. Exibição de Dados do Core na UI

Certifica-se de que os `FileInfo` e `DuplicateSet` (de `fotix.core.models`) são corretamente formatados e exibidos nos componentes apropriados da UI.

## Estrutura dos Testes

Os testes de integração da UI utilizam mocks para simular os serviços da camada de aplicação, permitindo verificar se a UI interage corretamente com esses serviços sem depender de implementações reais.

### Fixtures

- `app`: Cria uma instância da aplicação Qt
- `service_mocks`: Cria mocks para os serviços utilizados pela UI
- `main_window`: Cria uma instância da janela principal com serviços mockados
- `sample_duplicate_sets`: Cria conjuntos de duplicatas de exemplo para testes

## Como Executar os Testes

Para executar os testes de integração da UI, use o seguinte comando:

```bash
pytest tests/integration/fotix/ui -v
```

Para executar um teste específico:

```bash
pytest tests/integration/fotix/ui/test_ui_application_integration.py::TestUiApplicationIntegration::test_scan_from_ui -v
```

## Notas Importantes

1. Estes testes dependem do PySide6, que deve estar instalado no ambiente de desenvolvimento.
2. Os testes utilizam mocks para simular os serviços da camada de aplicação, não testando a integração real com esses serviços.
3. Para testes de integração completos, que incluem a UI e os serviços reais, seria necessário utilizar ferramentas de automação de UI como o `pytest-qt`.
