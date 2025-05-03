from dataclasses import dataclass
from mapafiscal.domain.common import NaturezaOperacao, Finalidade, TipoCliente
from mapafiscal.domain.common import CST_ICMS, CST_IPI, CST_PIS_COFINS
from .classe_fiscal import ClasseFiscal
from .cenario_fiscal import CenarioFiscal
 
        
@dataclass
class OperacaoFiscal:
    cenario: CenarioFiscal       
    cfop_saida: str
    cfop_entrada: str
    aliq_icms_operacao: float
    reducao_bc_icms: float
    aliq_fcp_uf_destino: float
    aliq_icms_uf_destino: float
    reducao_bc_icms_st: float
    mva_st: float
    difal_icms: float
    difal_icms_st: float    
    aliq_ipi: float
    aliq_pis: float
    aliq_cofins: float
    fundamento_legal: str 

    def __str__(self):        
        return f"Operação: {self.cenario}, " \
               f"Natureza Operacao: {self.cenario.natureza_operacao}, " \
               f"Tipo Cliente: {self.cenario.tipo_cliente}, " \
               f"Finalidade: {self.cenario.finalidade}" \
               f"CFOP: {self.cfop_saida}, " \
               f"NCM: {self.cenario.classe_fiscal.ncm}, " \
               f"UF Origem: {self.cenario.uf_origem}, " \
               f"UF Destino: {self.cenario.uf_destino}, " 

 