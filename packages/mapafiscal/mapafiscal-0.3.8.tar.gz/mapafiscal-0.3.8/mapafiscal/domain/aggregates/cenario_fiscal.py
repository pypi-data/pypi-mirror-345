from dataclasses import dataclass
from mapafiscal.domain.common import NaturezaOperacao, Finalidade, TipoCliente
from mapafiscal.domain.common import CST_ICMS, CST_IPI, CST_PIS_COFINS
from .classe_fiscal import ClasseFiscal
from .classe_st import ClasseST
from typing import Optional
 
@dataclass
class CenarioFiscal:
    grupo: str
    classe_fiscal: ClasseFiscal    
    uf_origem: str
    uf_destino: str
    natureza_operacao: NaturezaOperacao    
    cfop_interno: str
    cfop_interno_devolucao: str
    cfop_interestadual: str
    cfop_interestadual_devolucao: str
    finalidade: Finalidade
    tipo_cliente: TipoCliente     
    incide_icms: bool
    incide_icms_st: bool
    incide_difal: bool
    cst_icms: CST_ICMS
    incide_ipi: bool
    cst_ipi: CST_IPI    
    incide_pis_cofins: bool
    cst_pis_cofins: CST_PIS_COFINS
    fundamento_legal: str
    codigo_cenario: str  
    regime_especial: bool  
    classe_st: Optional[ClasseST]  
        
    def __str__(self):
        return f"Grupo: {self.grupo}, " \
               f"NCM: {self.classe_fiscal.ncm}, " \
               f"Natureza Operacao: {self.natureza_operacao}, " \
               f"UF Origem: {self.uf_origem}, " \
               f"UF Destino: {self.uf_destino}"