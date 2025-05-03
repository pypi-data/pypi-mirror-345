from enum import Enum, unique
from dataclasses import dataclass


@unique
class PerfilContribuinte(Enum):
    COMERCIO_VAREJISTA = ("comercio_varejista", "Comércio Varejista")
    COMERCIO_ATACADISTA = ("comercio_atacadista", "Comércio Atacadista")
    IMPORTADOR = ("importador", "Importador")
    FABRICANTE = ("fabricante", "Fabricante")
    PRODUTOR_RURAL = ("produtor_rural", "Produtor Rural")
    
    def __str__(self):
        return self.value[0]

    def __repr__(self):
        return self.value[0] 
      
    def __eq__(self, other):
        if isinstance(other, PerfilContribuinte):
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
        return [elem[index] for elem in PerfilContribuinte]

