from dataclasses import dataclass
 
 
@dataclass    
class ClasseST:
    ncm: str
    cest: str  
    descricao_cest: str
    segmento: str
    uf_origem: str
    uf_destino: str
    mva_original: float
    mva_ajustada_4: float
    mva_ajustada_12: float
    fundamento_legal: str
    
    def __str__(self):
        return f"NCM: {self.ncm}, " \
               f"CEST: {self.cest}, " \
               f"Origem: {self.uf_origem}, " \
               f"Destino: {self.uf_destino}, " \
               f"MVA original: {self.mva_original}"