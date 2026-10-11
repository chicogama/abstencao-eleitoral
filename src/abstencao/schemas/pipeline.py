from typing import Any

from pydantic import BaseModel


class JobEnfileirado(BaseModel):
    job_id: str
    tarefa: str


class JobStatus(BaseModel):
    job_id: str
    status: str
    resultado: Any | None = None
