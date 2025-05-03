from typing import List, Optional
from mapafiscal.domain.entities import Aliquota, ExcecaoFiscal, PautaFiscal, CenarioIncidencia
from mapafiscal.interfaces.repository import Repository
from mapafiscal.domain.common import RegimeTributacao, PerfilContribuinte, NaturezaOperacao
from mapafiscal.domain.common import TipoCliente, Finalidade, RegimeEspecial


class ContextoFiscalException(Exception):
    """Exceções específicas para o Contexto Fiscal."""
    pass


class ContextoFiscal():
    """
    Classe de contexto de dados tributários e fiscais, acessando-os via repositório.
    """

    def __init__(self, 
                 uf_origem: str, 
                 regime_tributacao: RegimeTributacao, 
                 perfil_contribuinte: PerfilContribuinte, 
                 repositorio: Repository,
                 regime_especial: RegimeEspecial = None):
        
        
        self._uf_origem = uf_origem
        self._regime_tributacao = regime_tributacao
        self._perfil_contribuinte = perfil_contribuinte
        self._repositorio = repositorio  # Repositório responsável pelo acesso aos dados
        self._regime_especial = regime_especial

    
    @property
    def uf_origem(self): 
        return self._uf_origem
    
    @property
    def regime_tributacao(self) -> RegimeTributacao: 
        return self._regime_tributacao
    
    @property
    def perfil_contribuinte(self) -> PerfilContribuinte: 
        return self._perfil_contribuinte

    @property
    def repositorio(self) -> Repository: 
        return self._repositorio
    
    @property
    def regime_especial(self) -> RegimeEspecial: 
        return self._regime_especial
   
    def list_all_aliquotas(self) -> List[Aliquota]:
        return self._repositorio.list_all(Aliquota)

    def list_all_excecoes(self) -> List[ExcecaoFiscal]:
        return self._repositorio.list_all(ExcecaoFiscal)

    def list_all_pautas(self) -> List[PautaFiscal]:
        return self._repositorio.list_all(PautaFiscal)

    def list_all_cenarios(self) -> List[CenarioIncidencia]:
        return self._repositorio.list_all(CenarioIncidencia)

    def list_aliquota_by_tributo(self, tributo: str):
        return [aliquota for aliquota in self.list_all_aliquotas() if aliquota.tributo == tributo]
    
    def list_excecoes_by_tributo(self, tributo: str):
        return [excecao for excecao in self.list_all_excecoes() if excecao.tributo == tributo]
    
    def list_pauta_by_cest(self, cest: str):
        return [pauta for pauta in self.list_all_pautas() if pauta.cest == cest and pauta.uf_origem == self._uf_origem]
    
    def list_cenario_by_natureza(self, natureza_operacao: NaturezaOperacao):
        return [operacao for operacao in self.list_all_cenarios() if operacao.natureza_operacao == natureza_operacao.codigo]

    def find_excecao_fiscal(self, ncm: str, tributo: str, uf: str = '') -> ExcecaoFiscal:
        excecoes = self.list_excecoes_by_tributo(tributo=tributo)
        if uf == '':
            for excecao in excecoes:
                if ncm == excecao.ncm:
                    return excecao
        else:    
            for excecao in excecoes:
                if uf.upper() == excecao.uf and ncm == excecao.ncm:
                    return excecao
        return None

    def find_cenario_incidencia(self, 
                                natureza_operacao: NaturezaOperacao, 
                                tipo_cliente: TipoCliente,
                                finalidade: Finalidade) -> CenarioIncidencia:        
        for cenario in self.list_all_cenarios():
            if cenario.natureza_operacao == natureza_operacao and \
               cenario.finalidade == finalidade and \
               cenario.perfil_contribuinte == self.perfil_contribuinte and \
               cenario.tipo_cliente == tipo_cliente:
                return cenario
        
        raise ContextoFiscalException(
            f"Configuração não encontrada para {self.perfil_contribuinte}: "
            f"natureza_operacao={natureza_operacao}, tipo_cliente={tipo_cliente}, finalidade={finalidade}"
        )
    
    def find_pauta_fiscal(self, cest: str, uf_destino: str) -> PautaFiscal:     
        if not cest:
            raise ContextoFiscalException("CEST deve ser informado")
        if not uf_destino:
            raise ContextoFiscalException("UF destino deve ser informado")
        
        for pauta in self.list_pauta_by_cest(cest=cest):
            if pauta.uf_destino == uf_destino and pauta.uf_origem == self._uf_origem:
                return pauta
        return None

    def find_aliquota(self, tributo: str, uf: str = "", ncm: str = "") -> Aliquota:
        """
        Obtém a aliquota para um determinado tributo de acordo com o NCM ou UF.
        
        Args:
            tributo (str): Tributo
            uf (str): UF
            ncm (str): NCM
        
        Returns:
            Aliquota
        """
        
        match(tributo):
            case "ICMS":
                if uf == "":
                    raise ContextoFiscalException("UF deve ser informada")
                
                for aliquota_icms in self.list_aliquota_by_tributo(tributo="ICMS"):
                    if aliquota_icms.uf == uf:                                                                          
                        return aliquota_icms
            
            case "IPI":
                if ncm == "":
                    raise ContextoFiscalException("NCM deve ser informado")
                
                for aliquota in self.list_aliquota_by_tributo(tributo=tributo):
                    if aliquota.ncm == ncm:
                        return aliquota
                
            case "PIS" | "COFINS":
            
                if ncm == "": 
                    raise ContextoFiscalException("NCM deve ser informado")

                # Busca aliquota pelo NCM
                for aliquota in self.list_aliquota_by_tributo(tributo=tributo):
                    if aliquota.ncm == ncm:
                        return aliquota

                # Retorna aliquota padrão
                if self.regime_tributacao == RegimeTributacao.LUCRO_REAL:            
                    return Aliquota(tributo=tributo, 
                                    ncm=ncm, 
                                    uf=uf,
                                    aliquota=1.65 if tributo == "PIS" else 7.6, 
                                    fcp=0.0, 
                                    descricao="",
                                    ex="",
                                    versao="")

                elif self.regime_tributacao == RegimeTributacao.LUCRO_PRESUMIDO:            
                    return Aliquota(tributo=tributo, 
                                    ncm=ncm, 
                                    uf=uf,
                                    aliquota=0.65 if tributo == "PIS" else 3.0, 
                                    fcp=0.0, 
                                    descricao="",
                                    ex="",
                                    versao="")
                    
                elif self.regime_tributacao == RegimeTributacao.SIMPLES_NACIONAL:            
                    return Aliquota(tributo=tributo, 
                                    ncm=ncm, 
                                    uf=uf,
                                    aliquota=0.0, 
                                    fcp=0.0, 
                                    descricao="",
                                    ex="",
                                    versao="")
            
            case _:
                # Busca a aliquota para o tributo informado, caso ela exista, retorna a primeira ocorrencia encontrada
                aliquotas = self.list_aliquota_by_tributo(tributo=tributo)
                if len(aliquotas) > 0:
                    return aliquotas[0] 
        
        # Caso nenhuma aliquota seja encontrada, retorna a aliquota zero
        return Aliquota(tributo=tributo, 
                        ncm=ncm, 
                        uf=uf,
                        aliquota=0.0,
                        fcp=0.0,                                             
                        descricao="",
                        versao="")