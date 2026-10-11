import asyncio
import logging

from abstencao.db.session import SessionLocal
from abstencao.services.etl_service import executar_etl
from abstencao.services.modelo_service import executar_treino

logger = logging.getLogger(__name__)


def _rodar_etl() -> list[dict]:
    with SessionLocal() as db:
        cargas = executar_etl(db)
        return [{"fonte": c.fonte, "status": c.status, "linhas": c.linhas} for c in cargas]


def _rodar_treino() -> dict:
    with SessionLocal() as db:
        return executar_treino(db)


async def tarefa_etl(ctx: dict) -> list[dict]:
    logger.info("Job %s: ETL iniciado", ctx["job_id"])
    return await asyncio.to_thread(_rodar_etl)


async def tarefa_treino(ctx: dict) -> dict:
    logger.info("Job %s: treino iniciado", ctx["job_id"])
    return await asyncio.to_thread(_rodar_treino)
