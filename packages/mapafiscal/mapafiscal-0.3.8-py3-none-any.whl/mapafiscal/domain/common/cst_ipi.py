from enum import Enum, unique
from dataclasses import dataclass

     
@unique
class CST_IPI(Enum):
    CST_00 = ("00", "Entrada com Recuperação de Crédito")   
    CST_01 = ("01", "Entrada Tributada com Aliquota Zero")
    CST_02 = ("02", "Entrada Isenta")
    CST_03 = ("03", "Entrada Nao Tributada")
    CST_04 = ("04", "Entrada Imune")
    CST_05 = ("05", "Entrada com Suspensão")
    CST_49 = ("49", "Outras entradas")
    CST_50 = ("50", "Saida Tributada")
    CST_51 = ("51", "Saida Tributada com Aliquota Zero")
    CST_52 = ("52", "Saida Isenta")
    CST_53 = ("53", "Saida Nao Tributada")
    CST_54 = ("54", "Saida Imune")
    CST_55 = ("55", "Saida com Suspensão")
    CST_99 = ("99", "Outras saidas")
    
    @classmethod
    def from_value(cls, valor):
        for elem in cls:
            if elem.value[0] == valor:
                return elem
        raise ValueError(f"{cls.__name__}: invalid value {valor}")
    
    @staticmethod
    def list(index = 0):
        return [elem.value[index] for elem in CST_IPI]

    def __str__(self):
        return self.value[0]
    
    def __repr__(self):
        return self.value[0] 
    
    def __eq__(self, other):
        if isinstance(other, CST_IPI):
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
