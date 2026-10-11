from arq import create_pool
from arq.connections import ArqRedis, RedisSettings
from arq.jobs import Job

from abstencao.core.config import settings

TAREFA_ETL = "tarefa_etl"
TAREFA_TREINO = "tarefa_treino"


async def _conectar() -> ArqRedis:
    return await create_pool(RedisSettings.from_dsn(settings.redis_url))


async def enfileirar(tarefa: str) -> str:
    redis = await _conectar()
    try:
        job = await redis.enqueue_job(tarefa)
        return job.job_id
    finally:
        await redis.aclose()


async def consultar_job(job_id: str) -> tuple[str, object | None]:
    redis = await _conectar()
    try:
        job = Job(job_id, redis)
        status = await job.status()
        info = await job.result_info()
        if info is None:
            return status.value, None
        return status.value, info.result if info.success else f"erro: {info.result}"
    finally:
        await redis.aclose()
