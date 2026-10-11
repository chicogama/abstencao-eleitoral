from fastapi import APIRouter, HTTPException

from abstencao.schemas.previsao import PrevisaoEntrada, PrevisaoSaida
from abstencao.services import modelo_service

router = APIRouter(tags=["previsão"])


@router.post("/prever", response_model=PrevisaoSaida)
def prever(entrada: PrevisaoEntrada) -> PrevisaoSaida:
    if not modelo_service.caminho_modelo().exists():
        raise HTTPException(status_code=503, detail="Modelo ainda não treinado: rode POST /pipeline/treino")
    taxa = modelo_service.prever(entrada.model_dump())
    return PrevisaoSaida(taxa_abstencao_prevista=round(taxa, 4), versao_modelo=modelo_service.VERSAO_MODELO)
