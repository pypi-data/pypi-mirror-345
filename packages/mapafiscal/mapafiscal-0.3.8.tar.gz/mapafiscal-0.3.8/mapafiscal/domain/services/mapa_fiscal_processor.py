from mapafiscal.domain.services.contexto_fiscal import ContextoFiscal
from mapafiscal.domain.entities import PautaFiscal, ICMS, IPI, PIS_COFINS
from mapafiscal.domain.common import Finalidade, TipoCliente, NaturezaOperacao, RegimeEspecial
from mapafiscal.domain.common import TipoIncidencia, CST_ICMS, CST_IPI, CST_PIS_COFINS
from mapafiscal.domain.aggregates import ClasseFiscal, OperacaoFiscal, CenarioFiscal, ClasseST
from typing import Optional


class MapaFiscalProcessor():
    
    """
    Motor de regras fiscais para construção de mapa fiscal a partir de um contexto fiscal.
    """

    def __init__(self, contexto: ContextoFiscal):
        """
        Inicializa o processador com os dados do contexto fiscal.

        Args:
            dados (ContextoFiscalData): Fonte de dados para processamento.
        """
        self._contexto = contexto
    
    @property
    def contexto(self):
        return self._contexto
    
    def calculate_icms(self, ncm: str, uf: str, origem: int, regime_especial: RegimeEspecial = None) -> ICMS:     
        """
        Calcula a incidência de ICMS para um NCM e UF.

        Args:
            ncm (str): NCM do produto.
            uf (str): Unidade Federativa.
            regime_especial (RegimeEspecial): Tratamento tributário especial para a UF.

        Returns:
            ICMS: Configuração calculada do ICMS.
        """
        icms = self._contexto.find_aliquota(tributo="ICMS", uf=uf, ncm=ncm)
        cst = CST_ICMS.CST_00
        aliquota = icms.aliquota
        reducao_base_calculo = 0.0
        fcp = icms.fcp
        fundamento_legal = ''
        
        excecao = self._contexto.find_excecao_fiscal(ncm=ncm, uf=uf, tributo="ICMS")
        if excecao:
            cst = CST_ICMS.from_value(excecao.cst)
            aliquota = excecao.aliquota
            reducao_base_calculo = excecao.reducao_base_calculo
            fcp=excecao.fcp
            fundamento_legal = excecao.fundamento_legal
        
        # Regras de negócio para tratamento tributário especial    
        if regime_especial != None:
            if uf == regime_especial.uf:
                pass
            
            match(regime_especial):
                case RegimeEspecial.FABRICANTE_SETORIAL_MG:
                    if aliquota > 12.0 and origem in [0, 4, 5, 6, 7]:
                        aliquota = 12.0
                        reducao_base_calculo = 0.0
                        fundamento_legal = self.__concat_text(fundamento_legal, "ICMS de 12% conf. ePTA nº XXXX")
                case RegimeEspecial.CD_EXCLUSIVO_FABRICACAO_MG:
                    if aliquota > 12.0 and origem in [0, 4, 5, 6, 7]:
                        aliquota = 12.0
                        reducao_base_calculo = 0.0                
                        fundamento_legal = self.__concat_text(fundamento_legal, "ICMS de 12% conf. ePTA nº XXXX")
                case RegimeEspecial.CD_EXCLUSIVO_FABRICACAO_MG:
                    if aliquota > 12.0 and origem in [0, 4, 5, 6, 7]:
                        aliquota = 12.0
                        reducao_base_calculo = 0.0                
                        fundamento_legal = self.__concat_text(fundamento_legal, "ICMS de 12% conf. ePTA nº XXXX")

        return ICMS(
            cst=cst,
            aliquota=aliquota,
            reducao_base_calculo=reducao_base_calculo,
            fcp=fcp,
            fundamento_legal=fundamento_legal
        )  
            
        

    def calculate_aliquota_icms(self, ncm: str, origem: int, uf_destino: str, regime_especial: RegimeEspecial = None) -> float:
        """
        Obtém a aliquota para uma operação de ICMS.
        
        A aliquota depende do NCM, origem e UF de destino e origem.
        """
        if uf_destino == self._contexto.uf_origem:
            aliquota_icms = self.calculate_icms(ncm=ncm, uf=uf_destino, origem=origem , regime_especial=regime_especial).aliquota
            return aliquota_icms
                        
        if origem in [0, 4, 5, 6, 7]:
            if uf_destino in ['SP', 'MG', 'RJ', 'SC', 'PR', 'RS']:
                return 12.0
            else:
                return 7.0                
        else:
            return 4.00    

    def calculate_pis(self, ncm: str) -> PIS_COFINS:
        """
        Calcula a incidência de PIS para um NCM.

        Args:
            ncm (str): NCM do produto.

        Returns:
            PIS_COFINS: Configuração calculada do PIS.
        """
        excecao = self._contexto.find_excecao_fiscal(ncm=ncm, tributo="PIS")
        if excecao:
            return PIS_COFINS(
                cst=CST_PIS_COFINS.from_value(excecao.cst),
                aliquota=excecao.aliquota,
                fundamento_legal=excecao.fundamento_legal
            )
        else:
            aliquota = self._contexto.find_aliquota(tributo="PIS", ncm=ncm)
            return PIS_COFINS(
                cst=CST_PIS_COFINS.CST_01,
                aliquota=aliquota.aliquota,
                fundamento_legal=""
            )
    
    def calculate_cofins(self, ncm: str) -> PIS_COFINS:
        """
        Calcula a incidência da COFINS para um NCM.

        Args:
            ncm (str): NCM do produto.

        Returns:
            PIS_COFINS: Configuração calculada do COFINS.
        """
        excecao = self._contexto.find_excecao_fiscal(ncm=ncm, tributo="COFINS")
        if excecao:
            return PIS_COFINS(
                cst=CST_PIS_COFINS.from_value(excecao.cst),
                aliquota=excecao.aliquota,
                fundamento_legal=excecao.fundamento_legal
            )
        else:
            aliquota = self._contexto.find_aliquota(tributo="COFINS", ncm=ncm)
            return PIS_COFINS(
                cst=CST_PIS_COFINS.CST_01,
                aliquota=aliquota.aliquota,
                fundamento_legal=""
            )
    
    def calculate_ipi(self, ncm: str, fabricante: bool = True) -> IPI: 
        """
        Calcula a incidência do IPI para um NCM.

        Args:
            ncm (str): NCM do produto.

        Returns:
            IPI: Configuração calculada do IPI.
        """       
        excecao = self._contexto.find_excecao_fiscal(ncm=ncm, tributo="IPI")
        if excecao:
            return IPI(
                cst=CST_IPI.from_value(excecao.cst),
                descricao_tipi=excecao.descricao,
                aliquota=excecao.aliquota,
                fundamento_legal=excecao.fundamento_legal
            )    
        else:
            aliquota = self._contexto.find_aliquota(tributo="IPI", ncm=ncm)
            if fabricante:                
                return IPI(
                    cst=CST_IPI.CST_51 if aliquota.aliquota == 0.0 else CST_IPI.CST_50, 
                    aliquota=aliquota.aliquota, 
                    descricao_tipi=aliquota.descricao,
                    fundamento_legal=""
                )
            else:
                return IPI(
                    cst=CST_IPI.CST_99, 
                    aliquota=0.0, 
                    descricao_tipi=aliquota.descricao,
                    fundamento_legal=""
                )
    
    
    def process_classe_fiscal(self, 
                              codigo: str,
                              ncm: str, 
                              descricao: str,
                              origem: int,
                              cest: str = '', 
                              segmento: str = '',
                              fabricante: bool = False,
                              regime_especial: bool = False) -> ClasseFiscal:

        return ClasseFiscal(
            codigo=codigo,
            ncm=ncm,
            origem=origem,
            descricao=descricao,
            cest=cest,
            segmento=segmento,
            icms=self.calculate_icms(ncm=ncm, uf=self._contexto.uf_origem, origem=origem),
            pis=self.calculate_pis(ncm),
            cofins=self.calculate_cofins(ncm),
            ipi=self.calculate_ipi(ncm=ncm, fabricante=fabricante),
            fabricante_equiparado=fabricante,
            regime_especial=regime_especial
        )
    
    def process_classe_st(self, classe_fiscal: ClasseFiscal, 
                          pauta_fiscal: PautaFiscal) -> ClasseST:
        
        uf_destino = pauta_fiscal.uf_destino
        mva_original = pauta_fiscal.mva_original   
        mva_ajustada_4 = mva_original
        mva_ajustada_12 = mva_original
        icms_destino = self.calculate_icms(ncm=classe_fiscal.ncm, uf=uf_destino, origem=classe_fiscal.origem)

        if icms_destino.aliquota > 0.04:    
            mva_ajustada_4 = round((((1 + mva_original / 100.0) * (0.96) / (1 - icms_destino.aliquota / 100.0)) - 1) * 100.0, 4)                
        
        if icms_destino.aliquota > 0.12:    
            mva_ajustada_12 = round((((1 + mva_original / 100.0) * (0.88) / (1 - icms_destino.aliquota / 100.0)) - 1) * 100.0, 4)                
                                        
        return ClasseST(ncm=classe_fiscal.ncm,
                        cest=classe_fiscal.cest, 
                        descricao_cest=pauta_fiscal.descricao_cest, 
                        segmento=classe_fiscal.segmento, 
                        uf_origem=self._contexto.uf_origem,
                        uf_destino=uf_destino,                       
                        mva_original=mva_original, 
                        mva_ajustada_4=mva_ajustada_4, 
                        mva_ajustada_12=mva_ajustada_12, 
                        fundamento_legal=pauta_fiscal.fundamento_legal)
            
                                                             
    def process_cenario_fiscal(self,
                               grupo: str, 
                               natureza_operacao: NaturezaOperacao, 
                               uf: str,                    
                               tipo_cliente: TipoCliente, 
                               finalidade: Finalidade,
                               classe_fiscal: ClasseFiscal,
                               classe_st: Optional[ClasseST],
                               regime_especial: bool = False) -> CenarioFiscal:
            
        # CST padrão
        cst_icms = CST_ICMS.CST_90
        cst_pis_cofins =  CST_PIS_COFINS.CST_99
        cst_ipi = CST_IPI.CST_99
    
        # Buscar cenario incidencia de acordo com os parâmetros selecionados
        incidencia = self._contexto.find_cenario_incidencia(natureza_operacao=natureza_operacao,
                                                            tipo_cliente=tipo_cliente, 
                                                            finalidade=finalidade) 
        if incidencia == None:
            raise MapaFiscalProcessorException(f'Nao foi possivel identificar um cenario para o NCM {classe_fiscal.ncm}' \
                                            f'na natureza de operacao {natureza_operacao}, ' \
                                            f'tipo de cliente {tipo_cliente} e finalidade {finalidade}')
        
        match (incidencia.incidencia_icms):
            case TipoIncidencia.TRIBUTADO:
                cst_icms = self.calculate_icms(ncm=classe_fiscal.ncm, uf=uf, origem=classe_fiscal.origem).cst    
            case TipoIncidencia.NAO_TRIBUTADO: 
                cst_icms = CST_ICMS.CST_41
            case TipoIncidencia.ISENTO:
                cst_icms = CST_ICMS.CST_40
            case TipoIncidencia.DIFERIDO:
                cst_icms = CST_ICMS.CST_51
            case TipoIncidencia.SUSPENSO:
                cst_icms = CST_ICMS.CST_50
            case TipoIncidencia.RETIDO:
                cst_icms = CST_ICMS.CST_60
            
        if incidencia.incidencia_icms_st == TipoIncidencia.TRIBUTADO and classe_st != None:        
            
            if classe_st.uf_destino != uf or classe_st.ncm != classe_fiscal.ncm or classe_st.cest != classe_fiscal.cest:
                raise MapaFiscalProcessorException(f'Classe ST: {classe_st} incompativel com a classe fiscal: {classe_fiscal}')
            
            # Se incidir ICMS ST substituir CST ICMS se necessário        
            match(classe_fiscal.icms.cst):
                case CST_ICMS.CST_20:
                    cst_icms = CST_ICMS.CST_70
                case CST_ICMS.CST_40:
                    cst_icms = CST_ICMS.CST_30  
                case _:
                    cst_icms = CST_ICMS.CST_10
                    
        match(incidencia.incidencia_ipi):
            case TipoIncidencia.TRIBUTADO:
                if classe_fiscal.fabricante_equiparado:
                    cst_ipi = self.calculate_ipi(ncm=classe_fiscal.ncm).cst
            case TipoIncidencia.NAO_TRIBUTADO:
                cst_ipi = CST_IPI.CST_53
            case TipoIncidencia.ISENTO:
                cst_ipi = CST_IPI.CST_52
            case TipoIncidencia.SUSPENSO:
                cst_ipi = CST_IPI.CST_55
        
        match(incidencia.incidencia_pis_cofins):          
            case TipoIncidencia.TRIBUTADO:
                cst_pis_cofins = self.calculate_pis(ncm=classe_fiscal.ncm).cst
            case TipoIncidencia.NAO_TRIBUTADO:
                cst_pis_cofins = CST_PIS_COFINS.CST_08
            case TipoIncidencia.ISENTO:
                cst_pis_cofins = CST_PIS_COFINS.CST_07
            case TipoIncidencia.SUSPENSO:
                cst_pis_cofins = CST_PIS_COFINS.CST_09
     
        incide_icms = cst_icms in [CST_ICMS.CST_00,
                                    CST_ICMS.CST_10,
                                    CST_ICMS.CST_20,
                                    CST_ICMS.CST_70]
        
        incide_icms_st = cst_icms in [CST_ICMS.CST_10,
                                       CST_ICMS.CST_30,
                                       CST_ICMS.CST_60,
                                       CST_ICMS.CST_70]
        
        incide_difal = incide_icms and finalidade in [Finalidade.USO_CONSUMO, Finalidade.IMOBILIZADO] and \
            tipo_cliente in [TipoCliente.CONSTRUCAO_CIVIL, TipoCliente.PRESTADOR_SERVICO, TipoCliente.CONSUMIDOR_FINAL, TipoCliente.PJ_NAO_CONTRIBUINTE]
        
        incide_ipi = cst_ipi in [CST_IPI.CST_50, CST_IPI.CST_51] 
               
        incide_pis_cofins = cst_pis_cofins in [CST_PIS_COFINS.CST_01,
                                               CST_PIS_COFINS.CST_02,
                                               CST_PIS_COFINS.CST_03,
                                               CST_PIS_COFINS.CST_04,
                                               CST_PIS_COFINS.CST_05,
                                               CST_PIS_COFINS.CST_06]
     
        return CenarioFiscal(grupo=grupo, 
                                 classe_fiscal=classe_fiscal, 
                                 uf_origem=self._contexto.uf_origem, 
                                 uf_destino=uf, 
                                 natureza_operacao=natureza_operacao, 
                                 cfop_interno=incidencia.cfop_interno if incide_icms_st==False else incidencia.cfop_interno_st, 
                                 cfop_interno_devolucao=incidencia.cfop_interno_devolucao if incide_icms_st==False else incidencia.cfop_interno_devolucao_st, 
                                 cfop_interestadual=incidencia.cfop_interestadual if incide_icms_st==False else incidencia.cfop_interestadual_st, 
                                 cfop_interestadual_devolucao=incidencia.cfop_interestadual_devolucao if incide_icms_st==False else incidencia.cfop_interestadual_devolucao_st, 
                                 finalidade=finalidade, 
                                 tipo_cliente=tipo_cliente,                                  
                                 incide_icms=incide_icms, 
                                 incide_icms_st=incide_icms_st, 
                                 incide_difal=incide_difal, 
                                 cst_icms=cst_icms,                                  
                                 incide_ipi=incide_ipi, 
                                 cst_ipi=cst_ipi,
                                 incide_pis_cofins=incide_pis_cofins, 
                                 cst_pis_cofins=cst_pis_cofins,                                 
                                 fundamento_legal=incidencia.fundamento_legal,
                                 codigo_cenario=incidencia.codigo,
                                 regime_especial=regime_especial,
                                 classe_st=classe_st)
                
            
    
    def process_operacao_fiscal(self, cenario: CenarioFiscal) -> OperacaoFiscal:        
        
        cfop_saida = ""
        cfop_entrada = ""
        fundamento_legal = cenario.fundamento_legal
        aliq_icms_operacao = 0.0
        reducao_bc_icms = 0.0
        mva_st = 0.0
        difal_icms = False
        difal_icms_st = False
        regime_especial = self._contexto.regime_especial != None and cenario.regime_especial and cenario.classe_fiscal.regime_especial

        icms_uf_destino = self.calculate_icms(
            ncm=cenario.classe_fiscal.ncm, 
            uf=cenario.uf_destino,
            origem=cenario.classe_fiscal.origem
        )              
       
        # Processar a incidência de ICMS
        if cenario.incide_icms:  
            
            # Processar a incidência de ICMS para operações internas 
            if cenario.uf_origem == cenario.uf_destino: 
                icms_origem = self.calculate_icms(ncm=cenario.classe_fiscal.ncm, 
                                                  uf=cenario.uf_origem, 
                                                  origem=cenario.classe_fiscal.origem, 
                                                  regime_especial=self._contexto.regime_especial if regime_especial else None)
                aliq_icms_operacao = icms_origem.aliquota     
                reducao_bc_icms = icms_origem.reducao_base_calculo  
                cfop_saida = cenario.cfop_interno
                cfop_entrada = cenario.cfop_interno_devolucao
                fundamento_legal = self.__concat_text(fundamento_legal, icms_origem.fundamento_legal)
            
            # Processar a incidência de ICMS para operações interestaduais
            else:                   
                aliq_icms_operacao = self.calculate_aliquota_icms(ncm=cenario.classe_fiscal.ncm, 
                                                                  origem=cenario.classe_fiscal.origem, 
                                                                  uf_destino=cenario.uf_destino)
                cfop_saida = cenario.cfop_interestadual
                cfop_entrada = cenario.cfop_interestadual_devolucao   
        
        # Processar a incidência de ICMS-ST
        if cenario.incide_icms_st:               
            if cenario.classe_st is None:
                raise MapaFiscalProcessorException(f"Classe ST para NCM {cenario.classe_fiscal.ncm} e UF Destino {cenario.uf_destino} desconhecida.")
            
            fundamento_legal = self.__concat_text(fundamento_legal, cenario.classe_st.fundamento_legal)
            if aliq_icms_operacao == 12.0:            
                mva_st = cenario.classe_st.mva_ajustada_12
            elif aliq_icms_operacao == 4.0:
                mva_st = cenario.classe_st.mva_ajustada_4
            else:
                mva_st = cenario.classe_st.mva_original            
               
        # Processar a incidência de DIFAL 
        if cenario.incide_difal:            
            difal_icms = icms_uf_destino.aliquota - aliq_icms_operacao if cenario.incide_icms else 0.0
            difal_icms_st = icms_uf_destino.aliquota - aliq_icms_operacao if cenario.incide_icms_st else 0.0
        
        return OperacaoFiscal(
            cenario=cenario,
            cfop_saida=cfop_saida,
            cfop_entrada=cfop_entrada,
            aliq_icms_operacao=aliq_icms_operacao,
            reducao_bc_icms=reducao_bc_icms,
            reducao_bc_icms_st=0.0,            
            aliq_fcp_uf_destino=icms_uf_destino.fcp if cenario.incide_icms else 0.0,
            aliq_icms_uf_destino=icms_uf_destino.aliquota if cenario.incide_icms else 0.0,
            mva_st=mva_st,
            difal_icms=difal_icms,
            difal_icms_st=difal_icms_st,
            aliq_ipi=cenario.classe_fiscal.ipi.aliquota if cenario.incide_ipi else 0.0,            
            aliq_pis=cenario.classe_fiscal.pis.aliquota if cenario.incide_pis_cofins else 0.0,
            aliq_cofins=cenario.classe_fiscal.cofins.aliquota if cenario.incide_pis_cofins else 0.0,
            fundamento_legal=fundamento_legal
        )

    
    def __concat_text(self, current_text: str, new_text: str) -> str:
        if current_text == '':
            return new_text
        else:
            if new_text != '' and new_text not in current_text:
                return current_text + ', ' + new_text
            else:
                return current_text

            
class MapaFiscalProcessorException(Exception):
    pass