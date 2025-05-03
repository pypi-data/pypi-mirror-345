from enum import Enum, unique
from dataclasses import dataclass

    
@unique    
class NaturezaOperacao(Enum):
    
    # SAIDAS
    VENDA_PRODUCAO = ("venda_producao", "venda", "saida", "Venda de produção")
    VENDA_PRODUCAO_ORDEM = ("venda_producao_ordem", "venda", "saida", "Venda de produção por ordem")
    VENDA_MERCADORIA = ("venda_mercadoria", "venda", "saida", "Venda de mercadoria")
    VENDA_MERCADORIA_ORDEM = ("venda_mercadoria_ordem", "venda", "saida", "Venda de mercadoria por ordem")
    BONIFICACAO_SAIDA = ("bonificacao_saida", "remessa", "saida", "Bonificação")
    AMOSTRA_GRATIS_SAIDA = ("amostra_gratis_saida", "remessa", "saida", "Amostra gratis")
    REMESSA_INDUSTRIALIZACAO_SAIDA = ("remessa_industrializacao_saida", "remessa", "saida", "Remessa para industrialização")
    REMESSA_POR_CONTA_ORDEM_SAIDA = ("remessa_por_conta_ordem_saida", "remessa", "saida", "Remsessa por conta de ordem")
    EXPORTACAO = ("exportacao", "venda", "saida", "Exportação")
    TRANSFERENCIA_PRODUCAO_SAIDA = ("transferencia_producao_saida", "remessa", "saida", "Transferência de produção")
    TRANSFERENCIA_MERCADORIA_SAIDA = ("transferencia_mercadoria_saida", "remessa", "saida", "Transferência de mercadoria")
    INDUSTRIALIZACAO_SAIDA = ("industrializacao_saida", "venda", "saida", "Mão de obra")
    RETORNO_INDUSTRIALIZACAO_SAIDA = ("retorno_industrializacao_saida", "retorno", "saida", "Retorno de industrialização")
    RETORNO_MATERIAL_NAO_INDUSTRIALIZADO_SAIDA = ("retorno_material_nao_industrializado_saida", "retorno", "saida", "Retorno de material não industrializado")    
    REMESSA_CONSERTO_SAIDA = ("remessa_conserto_saida", "remessa", "saida", "Remessa para conserto")        
    RETORNO_CONSERTO_SAIDA = ("retorno_conserto_saida", "retorno", "saida", "Retorno de conserto")
    OUTRAS_SAIDAS = ("outras_saidas", "remessa", "saidas", "Outras saidas")
    DEVOLUCAO_COMPRA = ("devolucao_compra", "devolucao", "saida", "Devolução de compra")   
    REMESSA_VASILHAME_SAIDA = ("remessa_vasilhame_saida", "remessa", "saida", "Remessa de vasilhame")
    RETORNO_VASILHAME_SAIDA = ("retorno_vasilhame_saida", "retorno", "saida", "Retorno de vasilhame")
    RETORNO_ATIVO_SAIDA = ("retorno_ativo_saida", "retorno", "saida", "Retorno de ativo")
    REMESSA_ATIVO_SAIDA = ("remessa_ativo_saida", "remessa", "saida", "Remessa de ativo")
    
    # ENTRADAS
    IMPORTACAO = ("importacao", "compra", "entrada", "Importação")    
    COMPRA_INDUSTRIALIZACAO = ("compra_industrializacao", "compra", "entrada", "Compra para industrialização")
    COMPRA_MERCADORIA = ("compra_mercadoria", "compra", "entrada", "Compra de mercadoria")
    BONIFICACAO_ENTRADA = ("bonificacao_entrada", "remessa", "entrada", "Bonificação")  
    TRANSFERENCIA_PRODUCAO_ENTRADA = ("transferencia_producao_entrada", "remessa", "entrada", "Transferência de produção")
    TRANSFERENCIA_MERCADORIA_ENTRADA = ("transferencia_mercadoria_entrada", "remessa", "entrada", "Transferência de mercadoria")    
    INDUSTRIALIZACAO_ENTRADA = ("industrializacao_entrada", "compra", "entrada", "Mão de obra/servicos")
    RETORNO_CONSERTO_ENTRADA = ("retorno_conserto_entrada", "retorno", "entrada", "Retorno de conserto")    
    REMESSA_CONSERTO_ENTRADA = ("remessa_conserto_entrada", "remessa", "entrada", "Remessa para conserto")
    OUTRAS_ENTRADAS = ("outras_entradas", "outras", "entradas", "Outras entradas")
    REMESSA_VASILHAME_ENTRADA = ("remessa_vasilhame_entrada", "remessa", "entrada", "Remessa de vasilhame")
    RETORNO_VASILHAME_ENTRADA = ("retorno_vasilhame_entrada", "retorno", "entrada", "Retorno de vasilhame")    
    RETORNO_ATIVO_ENTRADA = ("retorno_ativo_entrada", "retorno", "entrada", "Retorno de ativo")
    REMESSA_ATIVO_ENTRADA = ("remessa_ativo_entrada", "remessa", "entrada", "Remessa de ativo")   
    
    @classmethod
    def from_value(cls, valor):
        for elem in cls:
            if elem.value[0] == valor:
                return elem
        raise ValueError(f"{cls.__name__}: invalid value {valor}")

    @staticmethod
    def list(index = 0):
        return [elem.value[index] for elem in NaturezaOperacao]

    @property
    def tipo_operacao(self):
        return self.value[2]
    
    @property
    def descricao(self):
        return self.value[3]
    
    @property
    def grupo(self):        
        return self.value[1]
    
    @property
    def codigo(self):        
        return self.value[0]
       
    def __str__(self):
        return self.value[0]

    def __repr__(self):
        return self.value[0] 
      
    def __eq__(self, other):
        if isinstance(other, NaturezaOperacao):
            return self.value[0] == other.value[0]
        if isinstance(other, str):
            return self.value[0] == other
        return False
