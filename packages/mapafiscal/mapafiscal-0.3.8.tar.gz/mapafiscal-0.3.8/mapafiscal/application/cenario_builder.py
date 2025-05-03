import json
from mapafiscal.domain.services import MapaFiscalBuilder, ContextoFiscal
from mapafiscal.domain.common import NaturezaOperacao, TipoCliente, Finalidade
from mapafiscal.interfaces.repository import Repository
from mapafiscal.domain.aggregates import MapaFiscal
from mapafiscal.domain.common import RegimeTributacao, PerfilContribuinte, RegimeEspecial

class CenarioBuilder:
    """Classe para construção do mapa fiscal a partir de um arquivo de configuração."""

    def __init__(self, repositorio: Repository):
        self.repositorio = repositorio

    def build_from_file(self, cenario_file: str) -> MapaFiscal:
        
        with open(cenario_file, encoding="utf-8") as file:            
                config = json.load(file)
                
                cliente= config["cliente"]
                produtos = config.get("produtos", [])
                cenarios = config.get("cenarios", [])
                uf_origem = config["uf_origem"]
                regime_especial = RegimeEspecial.from_value(config["regime_especial"]) if config.get("regime_especial") else None
                regime_tributacao = RegimeTributacao.from_value(config["regime_tributacao"])                
                perfil_contribuinte = PerfilContribuinte.from_value(config["perfil_contribuinte"])
        
        contexto = ContextoFiscal(uf_origem=uf_origem,
                                regime_tributacao=regime_tributacao,
                                perfil_contribuinte=perfil_contribuinte,
                                repositorio=self.repositorio,
                                regime_especial=regime_especial)
        
        # Construindo mapa fiscal
        mapa_builder = MapaFiscalBuilder(cliente=cliente, contexto=contexto)
        
        for produto in produtos:    
            classe_fiscal = mapa_builder.build_classe_fiscal(codigo=produto.get("codigo"), 
                                                            ncm=produto.get("ncm"), 
                                                            descricao=produto.get("descricao", ""), 
                                                            origem=produto.get("origem", 0),
                                                            cest=produto.get("cest", ""),
                                                            segmento=produto.get("segmento", ""),
                                                            fabricante_equiparado=produto.get("fabricante", False),
                                                            regime_especial=produto.get("regime_especial", False))
            # Construindo classes ST       
            mapa_builder.build_classes_st(classe_fiscal=classe_fiscal)
            
            for cenario in cenarios:   
                
                mapa_builder.build_cenarios(grupo=cenario.get("grupo", "padrao"),
                                            natureza_operacao=NaturezaOperacao.from_value(cenario["natureza_operacao"]),
                                            tipo_cliente=TipoCliente.from_value(cenario["tipo_cliente"]),
                                            finalidade=Finalidade.from_value(cenario["finalidade"]),
                                            classe_fiscal=classe_fiscal,
                                            regime_especial=cenario.get("regime_especial", False),
                                            uf_list=cenario.get("uf_list"))
                
            mapa_builder.build_operacoes(grupo=cenario.get("grupo", "padrao"), classe_fiscal=classe_fiscal)     
                    
        return mapa_builder.build(f"Mapa Fiscal - {cliente}")    

