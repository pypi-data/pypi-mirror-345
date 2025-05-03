from enum import Enum, unique
from dataclasses import dataclass


@unique
class UF(Enum):
    SP = ("SP", "São Paulo")
    MG = ("MG", "Minas Gerais")
    RJ = ("RJ", "Rio de Janeiro")
    ES = ("ES", "Espírito Santo")
    PR = ("PR", "Paraná")
    RS = ("RS", "Rio Grande do Sul")
    SC = ("SC", "Santa Catarina")
    MS = ("MS", "Mato Grosso do Sul")
    MT = ("MT", "Mato Grosso")
    GO = ("GO", "Goiás")
    DF = ("DF", "Distrito Federal")
    AC = ("AC", "Acre")
    AL = ("AL", "Alagoas")
    AM = ("AM", "Amazonas")
    AP = ("AP", "Amapá")
    BA = ("BA", "Bahia")
    CE = ("CE", "Ceará")
    MA = ("MA", "Maranhão")
    PB = ("PB", "Pará")
    PE = ("PE", "Pernambuco")
    PI = ("PI", "Piauí")
    RN = ("RN", "Rio Grande do Norte")
    SE = ("SE", "Sergipe")
    TO = ("TO", "Tocantins")
    RR = ("RR", "Roraima")
    RO = ("RO", "Rondônia")
    PA = ("PA", "Pará")
    
    @classmethod
    def from_value(cls, valor):
        for elem in cls:
            if elem.value[0] == valor:
                return elem
        raise ValueError(f"{cls.__name__}: invalid value {valor}")

    @staticmethod
    def list(index = 0):        
        return [elem.value[index] for elem in UF]        

    @property
    def descricao(self):
        return self.value[1]
    
    @property
    def sigla(self):
        return self.value[0]
    
    def __eq__(self, other):
        if isinstance(other, UF):
            return self.value[0] == other.value[0]
        if isinstance(other, str):
            return self.value[0] == other
        return False
    
    def __str__(self):
        return self.value[0]

    def __repr__(self):
        return self.value[0] 
  