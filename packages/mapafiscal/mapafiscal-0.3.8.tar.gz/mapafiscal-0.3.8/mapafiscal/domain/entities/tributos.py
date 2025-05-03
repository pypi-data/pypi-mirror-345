from mapafiscal.domain.common import CST_ICMS, CST_IPI, CST_PIS_COFINS


class ICMS:
    cst: CST_ICMS
    aliquota: float
    reducao_base_calculo: float
    fcp: float
    fundamento_legal: str    

    def __init__(self, cst: CST_ICMS, aliquota: float, reducao_base_calculo: float, fcp: float, fundamento_legal: str):
        self.cst = cst
        self.aliquota = aliquota 
        self.reducao_base_calculo = reducao_base_calculo
        self.fcp = fcp
        self.fundamento_legal = fundamento_legal
    
    def __str__(self):
        return f"{self.cst}:{self.aliquota}"

    def __eq__(self, value):
        if isinstance(value, ICMS):
            return self.cst == value.cst and self.aliquota == value.aliquota and self.reducao_base_calculo == value.reducao_base_calculo and self.fcp == value.fcp        
        return False


class IPI:
    cst: CST_IPI
    aliquota: float
    descricao_tipi: str
    fundamento_legal: str

    def __init__(self, cst: CST_IPI, aliquota: float, descricao_tipi: str, fundamento_legal: str):
        self.cst = cst
        self.aliquota = aliquota
        self.descricao_tipi = descricao_tipi
        self.fundamento_legal = fundamento_legal

    def __str__(self):
        return f"{self.cst}:{self.aliquota}"
    
    def __eq__(self, value):
        if isinstance(value, IPI):
            return self.cst == value.cst and self.aliquota == value.aliquota and self.descricao_tipi == value.descricao_tipi
        return False


class PIS_COFINS:
    cst: CST_PIS_COFINS
    aliquota: float
    fundamento_legal: str 

    def __init__(self, cst: CST_PIS_COFINS, aliquota: float, fundamento_legal: str):
        self.cst = cst
        self.aliquota = aliquota
        self.fundamento_legal = fundamento_legal
    
    def __str__(self):
        return f"{self.cst}:{self.aliquota}"
    
    def __eq__(self, value):
        if isinstance(value, PIS_COFINS):
            return self.cst == value.cst and self.aliquota == value.aliquota
        return False