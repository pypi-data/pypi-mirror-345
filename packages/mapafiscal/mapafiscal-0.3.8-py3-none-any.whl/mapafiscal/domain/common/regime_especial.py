from enum import Enum, unique

    
@unique
class RegimeEspecial(Enum):
    CD_EXCLUSIVO_FABRICACAO_MG = ('cd_exclusivo_fabricacao', 'CD Exclusivo de Fabricação', 'MG')
    FABRICANTE_SETORIAL_MG = ('fabricante_setorial', 'Fabricante Setorial', 'MG')
    ECOMMERCE_NAO_VINCULADO_MG = ('ecommerce_nao_vinculado', 'Ecommerce não vinculado', 'MG')
    ECOMMERCE_VINCULADO_MG = ('ecommerce_vinculado', 'Ecommerce vinculado', 'MG')
    CORREDOR_IMPORTACAO_MG = ('corredor_importacao', 'Corredor de importação', 'MG')
    
    def __str__(self):
        return self.value[0]

    def __repr__(self):
        return self.value[0] 
      
    def __eq__(self, other):
        if isinstance(other, RegimeEspecial):
            return self.value[0] == other.value[0]
        return False
    
    @property
    def descricao(self):
        return self.value[1]
    
    @property
    def codigo(self):
        return self.value[0]
    
    @property
    def uf(self):
        return self.value[2]
    
    @classmethod
    def from_value(cls, valor):
        for elem in cls:    
            if elem.value[0] == valor:
                return elem
        raise ValueError(f"{cls.__name__}: invalid value {valor}") 

    @staticmethod
    def list(index = 0):
        return [elem.value[index] for elem in RegimeEspecial]
