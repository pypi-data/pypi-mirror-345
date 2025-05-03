from enum import Enum, unique
from dataclasses import dataclass

    
@unique
class CST_PIS_COFINS(Enum):
    CST_01 = ("01", "Tributada integralmente")
    CST_02 = ("02", "Operação Tributável com Alíquota Diferenciada")
    CST_03 = ("03", "Operação Tributável com Alíquota por Unidade de Medida de Produto")
    CST_04 = ("04", "Operação Tributável Monofásica – Revenda a Alíquota Zero")
    CST_05 = ("05", "Operação Tributável por Substituição Tributária")
    CST_06 = ("06", "Operação Tributável a Alíquota Zero") 
    CST_07 = ("07", "Operação Isenta da Contribuição")
    CST_08 = ("08", "Operação sem incidência da Contribuição")
    CST_09 = ("09", "Operação com suspensão da Contribuição")
    CST_49 = ("49", "Outras Operações de Saída")
    CST_98 = ("98", "Outras Operações de Entrada")
    CST_99 = ("99", "Outras Operações")
    
    @classmethod
    def from_value(cls, valor):
        for elem in cls:
            if elem.value[0] == valor:
                return elem
        raise ValueError(f"{cls.__name__}: invalid value {valor}")

    @staticmethod
    def list(index = 0):
        return [elem.value[index] for elem in CST_PIS_COFINS]
    
    def __str__(self):
        return self.value[0]  
    
    def __repr__(self):
        return self.value[0] 
    
    def __eq__(self, other):
        if isinstance(other, CST_PIS_COFINS):
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
