from datetime import datetime

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from abstencao.db.base import Base


class CargaEtl(Base):
    __tablename__ = "carga_etl"

    id: Mapped[int] = mapped_column(primary_key=True)
    fonte: Mapped[str] = mapped_column(String(60))
    inicio: Mapped[datetime] = mapped_column(server_default=func.now())
    fim: Mapped[datetime | None]
    linhas: Mapped[int | None]
    status: Mapped[str] = mapped_column(String(20), default="em_andamento")
    mensagem: Mapped[str | None] = mapped_column(String(500))
