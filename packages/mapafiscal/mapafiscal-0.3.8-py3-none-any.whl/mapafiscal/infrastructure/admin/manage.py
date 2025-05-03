import json
from importlib import import_module
from mapafiscal.interfaces.repository import Repository
import shutil
from importlib.resources import files
from tqdm import tqdm
from typing import List
import os
from datetime import date


def copy_resource_file(package_path, nome_arquivo, destino):
    """
    Copia um arquivo de recurso para uma pasta local.
    
    Args:
        package_path (str): Caminho do pacote (ex.: 'mapafiscal.resources.tabelas').
        nome_arquivo (str): Nome do arquivo JSON a ser copiado.
        destino (str): Caminho local para onde o arquivo será copiado.
        
    Raises:
        FileNotFoundError: Se o arquivo não for encontrado no pacote.
        Exception: Para outros erros gerais.
    """
    try:
        # Caminho completo do arquivo no pacote
        caminho_origem = files(package_path) / nome_arquivo

        # Copiar o arquivo para o destino
        shutil.copy(caminho_origem, destino)
        print(f"Arquivo '{nome_arquivo}' copiado para '{destino}'.")
    except FileNotFoundError:
        print(f"O arquivo '{nome_arquivo}' não foi encontrado em '{package_path}'.")
        raise
    except Exception as e:
        print(f"Erro ao copiar o arquivo: {e}")
        raise

def find_files(path: str, filter: str, ext: str = ".json") -> List[str]:
    """
    Busca arquivos em um diretório que contenham uma palavra específica no nome e tenham a extensão especificada.

    Args:
        diretorio (str): Caminho do diretório para buscar os arquivos.
        palavra (str): Palavra que deve estar presente no nome do arquivo.
        extensao (str): Extensão dos arquivos a serem filtrados (default é ".json").

    Returns:
        List[str]: Lista de caminhos completos dos arquivos encontrados.
    """
    arquivos_encontrados = []
    
    # Itera sobre os arquivos no diretório
    for arquivo in os.listdir(path):
        if filter in arquivo and arquivo.endswith(ext):
            arquivos_encontrados.append(os.path.join(path, arquivo))
    
    return arquivos_encontrados

def repository_import_from_file(repository: Repository, filename: str, encoding="utf-8"):

    def get_table_item_clazz(classe_item: str):
        clazz_module = classe_item.rsplit('.', 1) [0] 
        clazz_name = classe_item.rsplit('.', 1) [1] 
        # Importar o módulo 
        module_instance = import_module(clazz_module) 
        # Obter a classe do módulo 
        return getattr(module_instance, clazz_name)

    try:     
        try:   
            with open(filename, 'r', encoding=encoding) as f:
                dados = json.load(f)
        except json.JSONDecodeError:
            print(f"Erro ao carregar o arquivo JSON: {filename}")
        except FileNotFoundError:
            print(f"Arquivo {filename} não encontrado.")

        tabela = dados.get("tabela", {})
        if not tabela:
            raise ValueError(f"Nenhuma tabela encontrada no arquivo {filename}.")

        tabela_nome = tabela.get("nome")
        tabela_versao = tabela.get("versao", "")
        classe_item = tabela.get("classe_item", None)
        if classe_item is None:
            raise ValueError(f"Elemento 'classe_item' não encontrado na tabela {tabela_nome}.")
        
        itens = tabela.get("itens", [])
        if not itens:
            raise ValueError(f"Nenhum dado encontrado na tabela {tabela_nome}")

        for item in tqdm(itens, desc=f"Importando dados da tabela {tabela_nome}"):
            item['versao'] = tabela_versao
            clazz_type = get_table_item_clazz(classe_item)
            obj = clazz_type(**item)  
            repository.add(obj, clazz_type)
            
        repository.commit()

    except Exception as e:
         print(f"Erro inesperado: {e}")

def repository_start(repository: Repository, encoding="utf-8"):
    
    # Caminho completo do arquivo no pacote
    resources_path = files('mapafiscal.resources.tabelas').joinpath(".")
    for arquivo in find_files(path=resources_path, filter="tabela", ext=".json"):
        repository_import_from_file(filename=arquivo, 
                         repository=repository,
                         encoding=encoding) 
   
    

    



