from pydantic import BaseModel


class MunicipioOut(BaseModel):
    cd_ibge: int
    nome: str
    sg_uf: str
    regiao: str
    aptos: int
    taxa_abstencao: float
    abstencao_anterior: float | None
    taxa_prevista: float | None
