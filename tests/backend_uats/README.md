# Testes de Backend Automatizados para Cenários UAT do Fotix

Este diretório contém testes automatizados que validam os cenários de teste de aceitação do usuário (UAT) do Fotix, interagindo diretamente com os serviços da camada de aplicação e infraestrutura, sem usar a interface gráfica do usuário.

## Objetivo

O objetivo destes testes é validar os fluxos funcionais descritos nos cenários UAT, mas através de chamadas diretas aos serviços de backend, em vez de interações com a UI. Isso permite:

1. Testar a lógica de negócio independentemente da interface gráfica
2. Executar testes de forma automatizada e rápida
3. Validar a funcionalidade em ambientes de integração contínua
4. Detectar regressões em funcionalidades críticas

## Cenários Implementados

1. **UAT_FOTIX_001**: Scan de Diretório com Duplicatas Simples, Seleção Manual, Backup e Remoção para Lixeira
2. **UAT_FOTIX_002**: Scan Incluindo Arquivos ZIP, Seleção Automática (Ex: Mais Recente), Backup e Remoção
3. **UAT_FOTIX_003**: Listagem de Backups Existentes e Restauração para Local Original
4. **UAT_FOTIX_004**: Restauração de Backup para um Local Personalizado
5. **UAT_FOTIX_005**: Exclusão de um Backup Existente
6. **UAT_FOTIX_006**: Tentativa de Scan de Diretório Inválido ou Inacessível
7. **UAT_FOTIX_007**: Scan de Diretório Sem Duplicatas
8. **UAT_FOTIX_008**: Scan com Filtro de Extensões de Arquivo
9. **UAT_FOTIX_009**: Processamento de Duplicatas onde um Arquivo está Solto e Outro em um ZIP
10. **UAT_FOTIX_010**: Teste de Estratégia de Seleção: Manter Arquivo com Nome Mais Curto
11. **UAT_FOTIX_011**: Configuração do Caminho de Backup e Verificação de Uso
12. **UAT_FOTIX_012**: Indicação de Progresso Durante Scan Demorado

## Execução dos Testes

Para executar todos os testes de backend UAT:

```bash
pytest tests/backend_uats
```

Para executar um cenário específico:

```bash
pytest tests/backend_uats/test_backend_uats_fotix.py::test_uat_fotix_001_scan_with_simple_duplicates_manual_selection
```

## Estrutura dos Testes

Cada teste segue uma estrutura consistente:

1. **Arrange**: Configuração do ambiente de teste (criação de arquivos, diretórios, etc.)
2. **Act**: Execução das operações a serem testadas (scan, processamento, restauração, etc.)
3. **Assert**: Verificação dos resultados esperados

Os testes utilizam fixtures do pytest para criar instâncias dos serviços necessários e configurar o ambiente de teste de forma isolada para cada teste.

## Mocking

Para evitar efeitos colaterais indesejados (como mover arquivos reais para a lixeira do sistema), alguns métodos são mockados durante os testes:

```python
# Exemplo de mock para evitar mover arquivos para a lixeira
with mock.patch.object(fs_service, 'move_to_trash'):
    # Código que chama move_to_trash internamente
    result = duplicate_management_service.process_duplicate_set(...)
```

## Notas Importantes

- Os testes criam arquivos temporários que são automaticamente limpos após a execução
- A configuração do sistema é restaurada ao estado original após cada teste
- Os testes são independentes e podem ser executados em qualquer ordem
