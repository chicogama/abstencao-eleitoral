import logging

from arq.connections import RedisSettings

from abstencao.core.config import settings
from abstencao.worker.tasks import tarefa_etl, tarefa_treino

_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(message)s"))
logging.getLogger("abstencao").addHandler(_handler)
logging.getLogger("abstencao").setLevel(logging.INFO)


class WorkerSettings:
    functions = [tarefa_etl, tarefa_treino]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    max_jobs = 1
    job_timeout = 1800
