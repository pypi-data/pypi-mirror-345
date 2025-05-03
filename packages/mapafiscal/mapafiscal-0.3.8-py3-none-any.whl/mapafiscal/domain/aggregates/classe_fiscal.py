from dataclasses import dataclass
from mapafiscal.domain.entities import ICMS, IPI, PIS_COFINS
from typing import Optional
   
   
@dataclass
class ClasseFiscal:
    codigo: str
    ncm: str
    origem: int 
    descricao: str 
    cest: str
    segmento: str 
    ipi: Optional[IPI] = None    
    icms: Optional[ICMS] = None
    pis: Optional[PIS_COFINS] = None      
    cofins: Optional[PIS_COFINS] = None 
    fabricante_equiparado: bool = False
    regime_especial: bool = False
         
    def __str__(self):
        return f"Código: {self.codigo}, " \
               f"NCM: {self.ncm}, " \
               f"Origem: {self.origem}, " \
               f"Descricao: {self.descricao}, " \
               f"CEST: {self.cest}"