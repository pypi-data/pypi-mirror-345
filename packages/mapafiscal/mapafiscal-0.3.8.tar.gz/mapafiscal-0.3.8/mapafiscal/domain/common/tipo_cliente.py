from enum import Enum, unique
from dataclasses import dataclass

    
@unique
class TipoCliente(Enum):
    PJ_CONTRIBUINTE = ("pj_contribuinte", "PJ Contribuinte", "pj_contribuinte")
    PJ_NAO_CONTRIBUINTE = ("pj_nao_contribuinte", "PJ Não Contribuinte", "pj_nao_contribuinte")
    CONSUMIDOR_FINAL = ("consumidor_final", "Consumidor Final", "nao_contribuinte")
    DISTRIBUIDOR = ("distribuidor", "Distribuidor", "pj_contribuinte")
    COMERCIO_ATACADISTA = ("comercio_atacadista", "Comércio Atacadista", "pj_contribuinte")
    COMERCIO_VAREJISTA = ("comercio_varejista", "Comércio Varejista", "pj_contribuinte")
    DEPOSITO_FECHADO = ("deposito_fechado", "Depósito Fechado", "pj_contribuinte")
    ARMAZEM_GERAL = ("armazem_geral", "Armazem Geral", "pj_contribuinte")
    INDUSTRIA = ("industria", "Indústria", "pj_contribuinte")
    IMPORTADOR = ("importador", "Importador", "pj_contribuinte")
    GOVERNO = ("governo", "Governo", "nao_contribuinte")    
    TRANSPORTADORA = ("transportadora", "Transportadora", "pj_contribuinte")
    PRESTADOR_SERVICO = ("prestador_servico", "Prestador de Serviços", "pj_nao_contribuinte")
    CONSTRUCAO_CIVIL = ("construcao_civil", "Construção Civil", "pj_nao_contribuinte")    
    PRODUTOR_RURAL = ("produtor_rural", "Produtor Rural", "pj_contribuinte")
    
    def __str__(self):
        return self.value[0]

    def __repr__(self):
        return self.value[0] 

    @property
    def codigo(self):
        return self.value[0]
    
    @property
    def descricao(self):
        return self.value[1]
    
    @property
    def classificacao(self):
        return self.value[2]
    
    def __eq__(self, other):
        if isinstance(other, TipoCliente):
            return self.value[0] == other.value[0]
        if isinstance(other, str):
            return self.value[0] == other
        return False
    
    @classmethod
    def from_value(cls, valor):
        for elem in cls:    
            if elem.value[0] == valor:
                return elem
        raise ValueError(f"{cls.__name__}: invalid value {valor}")
    
    @staticmethod
    def list(index = 0):
        return [elem.value[index] for elem in TipoCliente]
