from enum import Enum, unique
from dataclasses import dataclass



@unique
class Finalidade(Enum):
    COMERCIALIZACAO = ("comercializacao", "Comercialização")
    INDUSTRIALIZACAO = ("industrializacao", "Industrialização")
    USO_CONSUMO = ("uso_consumo", "Uso e Consumo")
    IMOBILIZADO = ("imobilizado", "Imobilizado")
    
    def __str__(self):
        return self.value[0]

    def __repr__(self):
        return self.value[0] 
      
    def __eq__(self, other):
        if isinstance(other, Finalidade):
            return self.value[0] == other.value[0]
        if isinstance(other, str):
            return self.value[0] == other
        return False
    
    @property
    def descricao(self):
        return self.value[1]
    
    @property
    def codigo(self):
        return self.value[0]
    
    @classmethod
    def from_value(cls, valor):
        for elem in cls:    
            if elem.value[0] == valor:
                return elem
        raise ValueError(f"{cls.__name__}: invalid value {valor}")
    
    @staticmethod
    def list(index = 0):
        return [elem.value[index] for elem in Finalidade]
 