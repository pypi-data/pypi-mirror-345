from dataclasses import dataclass
from mapafiscal.domain.common import RegimeTributacao, RegimeEspecial
from typing import List
from .classe_fiscal import ClasseFiscal
from .classe_st import ClasseST
from .cenario_fiscal import CenarioFiscal
from .operacao_fiscal import OperacaoFiscal


@dataclass           
class MapaFiscal:
    '''
    Mapa Fiscal Tributário - Mapa contendo cenarios e operacoes fiscais para um determinado conjunto de classes fiscais
    '''
    def __init__(self, nome: str, uf_origem: str, tributacao: RegimeTributacao, regime_especial: RegimeEspecial = None):
        self._nome: str = nome
        self._uf_origem: str = uf_origem
        self._regime_tributacao: RegimeTributacao = tributacao
        self._regime_especial: RegimeEspecial = regime_especial
        self._classes_fiscais: List[ClasseFiscal] = [] 
        self._classes_st: List[ClasseST] = []
        self._operacoes: List[OperacaoFiscal] = []
        self._cenarios: List[CenarioFiscal] = []
    
    @property
    def nome(self):        
        return self._nome
    
    @nome.setter
    def nome(self, value):        
        self._nome = value   
  
    @property
    def uf_origem(self):        
        return self._uf_origem
        
    @property
    def regime_tributario(self):        
        return self._regime_tributacao

    @property
    def regime_especial(self):        
        return self._regime_especial

    @property
    def cenarios(self):        
        return self._cenarios
        
    @property
    def operacoes(self):        
        return self._operacoes   
     
    @property
    def classes_st(self):           
        return self._classes_st
        
    @property
    def classes_fiscais(self):        
        return self._classes_fiscais
        
    def get_classe_fiscal(self, codigo: str) -> ClasseFiscal:
        for classe in self._classes_fiscais:
            if classe.codigo == codigo:
                return classe
        return None
    
    def get_cenarios(self, grupo: str, classe_fiscal: ClasseFiscal) -> List[CenarioFiscal]:
        return [cenario for cenario in self._cenarios if cenario is not None and cenario.grupo == grupo and cenario.classe_fiscal == classe_fiscal]
    
    def get_operacoes(self, grupo: str) -> List[OperacaoFiscal]:
        return [operacao for operacao in self._operacoes if operacao is not None and operacao.cenario == grupo]
    
    def get_classe_st(self, ncm: str, uf_destino: str) -> ClasseST:
        for classe in self._classes_st:
            if classe.ncm == ncm and classe.uf_destino == uf_destino:
                return classe
        return None
        
    def __str__(self):        
        return f"Mapa Fiscal: {self._nome}, " \
               f"UF Origem: {self._uf_origem}, " \
               f"Regime Tributação: {self._regime_tributacao}"