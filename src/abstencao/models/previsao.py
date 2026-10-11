from datetime import datetime

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from abstencao.db.base import Base


class Previsao(Base):
    __tablename__ = "previsao"

    cd_ibge: Mapped[int] = mapped_column(ForeignKey("municipio.cd_ibge"), primary_key=True)
    versao_modelo: Mapped[str] = mapped_column(String(40), primary_key=True)
    taxa_prevista: Mapped[float]
    criado_em: Mapped[datetime] = mapped_column(server_default=func.now())
