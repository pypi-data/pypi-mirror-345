from dataclasses import dataclass


@dataclass
class Aliquota:        
    tributo: str 
    aliquota: float   
    uf: str = '' 
    fcp: float = 0.0
    ncm: str = ''
    descricao: str = ''
    ex: str = ''
    versao: str = ''
    id: int = None

    def __str__(self):
        return f"Tributo: {self.tributo}, Aliquota: {self.aliquota}"
 