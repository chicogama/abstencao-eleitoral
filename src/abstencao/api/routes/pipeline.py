from fastapi import APIRouter, HTTPException

from abstencao.schemas.pipeline import JobEnfileirado, JobStatus
from abstencao.services import processing_service

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/etl", response_model=JobEnfileirado, status_code=202)
async def enfileirar_etl() -> JobEnfileirado:
    job_id = await processing_service.enfileirar(processing_service.TAREFA_ETL)
    return JobEnfileirado(job_id=job_id, tarefa=processing_service.TAREFA_ETL)


@router.post("/treino", response_model=JobEnfileirado, status_code=202)
async def enfileirar_treino() -> JobEnfileirado:
    job_id = await processing_service.enfileirar(processing_service.TAREFA_TREINO)
    return JobEnfileirado(job_id=job_id, tarefa=processing_service.TAREFA_TREINO)


@router.get("/jobs/{job_id}", response_model=JobStatus)
async def consultar_job(job_id: str) -> JobStatus:
    status, resultado = await processing_service.consultar_job(job_id)
    if status == "not_found":
        raise HTTPException(status_code=404, detail="Job não encontrado")
    return JobStatus(job_id=job_id, status=status, resultado=resultado)
