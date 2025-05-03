import json
from pathlib import Path
from typing import Type, TypeVar, List, Optional, Dict
from mapafiscal.interfaces.repository import Repository
from mapafiscal.domain.entities import Aliquota, PautaFiscal, CenarioIncidencia, ExcecaoFiscal

T = TypeVar('T')

DEFAULT_CLAZZ_MAP = {
    Aliquota: "aliquotas.json",
    PautaFiscal: "pautas_fiscais.json",
    CenarioIncidencia: "cenarios_incidencias.json",
    ExcecaoFiscal: "excecoes_fiscais.json",
}

class JSONRepository(Repository[T]):

    def __init__(self, db_path: str, clazz_map: Dict[Type[T], str] = DEFAULT_CLAZZ_MAP, encoding: str = 'utf-8'):
        self.clazz_map = clazz_map
        self.encoding = encoding
        self.files = {clazz.__name__: Path(f"{db_path}/{arquivo}") for clazz, arquivo in clazz_map.items()}
        self.data = {clazz.__name__: self._load_data(clazz) for clazz in clazz_map.keys()}     
        self.dirty = {clazz.__name__: False for clazz in clazz_map.keys()}   

    def _load_data(self, clazz: Type[T]) -> List[T]:
        arquivo = self.files[clazz.__name__]
        if not arquivo.exists():
            return []
        with open(arquivo, 'r', encoding=self.encoding) as f:
            try:
                dados = json.load(f)
                return [clazz(**item) for item in dados]
            except json.JSONDecodeError:
                print(f"Erro ao carregar o arquivo JSON: {arquivo}")
                return []

    def _save(self, clazz: Type[T]) -> None:      
        arquivo = self.files[clazz.__name__]
        with open(arquivo, 'w', encoding=self.encoding) as f:
            json.dump(self.data[clazz.__name__], fp=f, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)
            
    def _next_id(self, clazz: Type[T]) -> int:
        """
        Gera o próximo ID sequencial para a entidade especificada.

        Args:
            clazz (Type[T]): A classe da entidade.

        Returns:
            int: O próximo ID único.
        """
        if clazz.__name__ in self.data:
            max_id = max((item.id for item in self.data[clazz.__name__]), default=0)
            return max_id + 1
        else:
            raise KeyError(f"Classe {clazz.__name__} não encontrada")

    def add(self, obj: T, clazz: Type[T]) -> None:
        if clazz.__name__ in self.data:
            if not hasattr(obj, 'id') or obj.id is None:  # Gera ID se não estiver definido
                obj.id = self._next_id(clazz)
            self.data[clazz.__name__].append(obj)
            self.dirty[clazz.__name__] = True
        else:
            raise KeyError(f"Classe {clazz.__name__} não encontrada")

    def get(self, id: int, clazz: Type[T]) -> Optional[T]:
        if clazz.__name__ in self.data:
            return next((item for item in self.data[clazz.__name__] if item.id == id), None)
        else:
            raise KeyError(f"Classe {clazz.__name__} não encontrada")

    def update(self, obj: T, clazz: Type[T]) -> None:
        if clazz.__name__ in self.data:            
            for i, item in enumerate(self.data[clazz.__name__]):
                if item.id == obj.id:
                    self.data[clazz.__name__][i] = obj
                    break
            self.dirty[clazz.__name__] = True
        else:
            raise KeyError(f"Classe {clazz.__name__} não encontrada")

    def remove(self, id: int, clazz: Type[T]) -> None:
        if clazz.__name__ in self.data:
            self.data[clazz.__name__] = [item for item in self.data[clazz.__name__] if item.id != id]
            self.dirty[clazz.__name__] = True
        else:
            raise KeyError(f"Classe {clazz.__name__} não encontrada")

    def list_all(self, clazz: Type[T]) -> List[T]:
        if clazz.__name__ in self.data:           
            return self.data[clazz.__name__]
        else:
            raise KeyError(f"Classe {clazz.__name__} não encontrada")

    def commit(self):
        for clazz in self.clazz_map.keys():  
            if self.dirty[clazz.__name__]: 
                self._save(clazz)  
                self.dirty[clazz.__name__] = False