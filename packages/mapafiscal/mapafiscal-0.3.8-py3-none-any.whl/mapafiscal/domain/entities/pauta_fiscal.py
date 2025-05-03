from dataclasses import dataclass


@dataclass
class PautaFiscal:
    uf_origem: str
    uf_destino: str
    ncm: str
    cest: str
    descricao_cest: str
    segmento: str
    mva_original: float
    fundamento_legal: str
    versao: str = ''
    id: int = None
    
    def __str__(self):
        return f"UF Origem: {self.uf_origem}, "\
            f"UF Destino: {self.uf_destino}, "\
            f"NCM: {self.ncm}, "\
            f"CEST: {self.cest}, "\
            f"Segmento: {self.segmento}, "\
            f"MVA original: {self.mva_original}, "\
            f"Fundamento Legal: {self.fundamento_legal}"
            