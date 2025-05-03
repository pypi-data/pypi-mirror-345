from dataclasses import dataclass, field
from mapafiscal.domain.common import Finalidade, NaturezaOperacao, TipoCliente, TipoIncidencia, PerfilContribuinte


@dataclass
class CenarioIncidencia:
    codigo: str
    natureza_operacao: NaturezaOperacao
    perfil_contribuinte: PerfilContribuinte
    finalidade: Finalidade
    tipo_cliente: TipoCliente    
    cfop_interno: str    
    cfop_interno_devolucao: str
    cfop_interestadual: str
    cfop_interestadual_devolucao: str    
    cfop_interno_st: str = ""
    cfop_interno_devolucao_st: str = ""
    cfop_interestadual_st: str = ""
    cfop_interestadual_devolucao_st: str = ""
    incidencia_icms: TipoIncidencia = field(default_factory=lambda: TipoIncidencia.NAO_TRIBUTADO)
    incidencia_icms_st: TipoIncidencia = field(default_factory=lambda: TipoIncidencia.NAO_TRIBUTADO)
    incidencia_ipi: TipoIncidencia = field(default_factory=lambda: TipoIncidencia.NAO_TRIBUTADO)
    incidencia_pis_cofins: TipoIncidencia = field(default_factory=lambda: TipoIncidencia.NAO_TRIBUTADO)
    fundamento_legal: str = ""
    versao: str = ''
    id: int = None        
    
    def __str__(self):
        return f"Código: {self.codigo}, "\
            f"Natureza Operação: {self.natureza_operacao}, "\
            f"Finalidade: {self.finalidade}, "\
            f"Tipo Cliente: {self.tipo_cliente}"