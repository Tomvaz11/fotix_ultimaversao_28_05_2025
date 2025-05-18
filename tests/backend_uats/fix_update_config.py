"""
Script para corrigir o uso da função update_config nos testes UAT.

Este script modifica os testes UAT para usar a função update_config corretamente,
passando chave e valor separadamente em vez de um dicionário.
"""

import re
import os
from pathlib import Path


def fix_update_config_calls(file_path):
    """
    Corrige as chamadas para update_config no arquivo especificado.
    
    Args:
        file_path: Caminho para o arquivo a ser corrigido.
    """
    print(f"Corrigindo chamadas para update_config em {file_path}")
    
    # Ler o conteúdo do arquivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Padrão para encontrar chamadas como update_config({"key": value})
    pattern = r'update_config\(\{(["\'])(\w+)\1\s*:\s*([^}]+)\}\)'
    
    # Substituir por update_config("key", value)
    fixed_content = re.sub(pattern, r'update_config(\1\2\1, \3)', content)
    
    # Padrão para encontrar chamadas como update_config(original_config)
    # onde original_config é um dicionário
    pattern_dict = r'update_config\((\w+_config)\)'
    
    # Substituir por código que atualiza cada chave individualmente
    def replace_dict_call(match):
        dict_var = match.group(1)
        return f"# Atualizar cada chave individualmente\n    for key, value in {dict_var}.items():\n        update_config(key, value)"
    
    fixed_content = re.sub(pattern_dict, replace_dict_call, fixed_content)
    
    # Escrever o conteúdo corrigido de volta para o arquivo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"Arquivo {file_path} corrigido com sucesso!")


if __name__ == "__main__":
    # Caminho para o arquivo de testes UAT
    test_file = Path(__file__).parent / "test_backend_uats_fotix.py"
    
    # Verificar se o arquivo existe
    if not test_file.exists():
        print(f"Arquivo {test_file} não encontrado!")
        exit(1)
    
    # Corrigir o arquivo
    fix_update_config_calls(test_file)
