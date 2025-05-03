from enum import Enum, unique
from dataclasses import dataclass


@unique
class CST_ICMS(Enum):
    CST_00 = ("00", "Tributada integralmente")
    CST_10 = ("10", "Tributada e com cobrança do ICMS por substituição tributária")
    CST_20 = ("20", "Com redução de base de cálculo")
    CST_30 = ("30", "Isenta ou não tributada e com cobrança do ICMS por substituição tributária")
    CST_40 = ("40", "Isenta")
    CST_41 = ("41", "Nao Tributada")
    CST_50 = ("50", "Suspensão")
    CST_51 = ("51", "Diferimento")
    CST_60 = ("60", "ICMS cobrado anteriormente por substituição tributária")
    CST_70 = ("70", "Com redução de base de cálculo e cobrança do ICMS por substituição tributária")
    CST_90 = ("90", "Outros")
    
    @classmethod
    def from_value(cls, valor):
        for elem in cls:
            if elem.value[0] == valor:
                return elem
        raise ValueError(f"{cls.__name__}: invalid value {valor}")    
    
    @staticmethod
    def list(index = 0):
        return [elem.value[index] for elem in CST_ICMS]
    
    def __str__(self):
        return self.value[0]

    def __repr__(self):
        return self.value[0] 
    
    def __eq__(self, other):
        if isinstance(other, CST_ICMS):
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
