from pydantic import BaseModel, Field


class PrevisaoEntrada(BaseModel):
    sg_uf: str = Field(min_length=2, max_length=2, examples=["AP"])
    abstencao_anterior: float = Field(ge=0, le=1, examples=[0.22])
    aptos: int = Field(gt=0, examples=[20000])
    populacao: int = Field(gt=0, examples=[25000])
    pib_per_capita: float = Field(gt=0, examples=[25000.0])
    pct_16_17: float = Field(ge=0, le=1, examples=[0.015])
    pct_70_mais: float = Field(ge=0, le=1, examples=[0.10])
    pct_analfabeto: float = Field(ge=0, le=1, examples=[0.05])
    pct_superior: float = Field(ge=0, le=1, examples=[0.08])
    pct_feminino: float = Field(ge=0, le=1, examples=[0.51])
    pct_biometria: float = Field(ge=0, le=1, examples=[0.90])
    pct_vab_agro: float = Field(ge=0, le=1, examples=[0.20])
    pct_vab_adm_publica: float = Field(ge=0, le=1, examples=[0.40])


class PrevisaoSaida(BaseModel):
    taxa_abstencao_prevista: float
    versao_modelo: str
