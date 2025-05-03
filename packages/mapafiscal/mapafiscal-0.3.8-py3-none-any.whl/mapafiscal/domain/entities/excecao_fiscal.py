from dataclasses import dataclass

 
@dataclass
class ExcecaoFiscal:
    tributo: str
    uf: str
    ncm: str    
    aliquota: float
    cst: str
    fcp: float = 0.0    
    reducao_base_calculo: float = 0.0
    descricao: str = ""
    fundamento_legal: str = ""
    versao: str = ''
    id: int = None
    
    def __str__(self):
        return f"Tributo: {self.tributo}, Aliquota: {self.aliquota}, Fundamento Legal: {self.fundamento_legal}"